"""
views.py — All page views + JSON API endpoints for BasketIQ / ApnaCart.

Page views:  home, aiGroceryPlanner, myOrder, login, signup, index, profile, cart
API views:   planner, auth, products, cart, profile, expenses, orders
"""

import json
import secrets
from datetime import datetime

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password

from bson import ObjectId

from . import mongo_client
from .ai_planner import generate_plan, generate_recipe_from_approved_items


# ===================================================================
#  HELPER UTILITIES
# ===================================================================

def _json_serialise(doc):
    """Make a MongoDB document JSON-serialisable."""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [_json_serialise(d) for d in doc]
    if isinstance(doc, dict):
        out = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                out[k] = str(v)
            elif isinstance(v, datetime):
                out[k] = v.isoformat()
            elif isinstance(v, dict):
                out[k] = _json_serialise(v)
            elif isinstance(v, list):
                out[k] = _json_serialise(v)
            else:
                out[k] = v
        return out
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc


def _get_user_from_token(request):
    """Extract & validate Bearer token → return user doc or None."""
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    users = mongo_client.get_users_collection()
    user = users.find_one({"token": token})
    return user


# ===================================================================
#  PAGE VIEWS (render templates)
# ===================================================================

def home(request):
    return render(request, "landingPage.html")

def aiGroceryPlanner(request):
    return render(request, "AIGroceryPlanner.html")

def myOrder(request):
    return render(request, "myOrder.html")

def login_page(request):
    return render(request, "login.html")

def signup_page(request):
    return render(request, "signup.html")

def index_page(request):
    return render(request, "index.html")

def profile_page(request):
    return render(request, "profile.html")

def cart_page(request):
    return render(request, "cart.html")


# ===================================================================
#  AUTH API
# ===================================================================

@csrf_exempt
def api_signup(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    location = data.get("location", "Not provided")

    if not name or not email or not password:
        return JsonResponse({"error": "Name, email and password are required."}, status=400)

    users = mongo_client.get_users_collection()

    if users.find_one({"email": email}):
        return JsonResponse({"error": "Email already registered."}, status=400)

    # Hash password using Django's secure hasher (PBKDF2)
    hashed_pw = make_password(password)

    # Generate auth token immediately (auto-login)
    token = secrets.token_hex(32)

    user_doc = {
        "name": name,
        "email": email,
        "password": hashed_pw,
        "location": location,
        "profile_image": "",
        "token": token,
        "created_at": datetime.utcnow(),
    }
    result = users.insert_one(user_doc)

    return JsonResponse({
        "user_id": str(result.inserted_id),
        "token": token,
        "name": name,
        "email": email,
        "message": "Account created successfully! Welcome to BasketIQ!",
    })


@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    users = mongo_client.get_users_collection()
    user = users.find_one({"email": email})

    if not user:
        return JsonResponse({"error": "Invalid email or password."}, status=401)

    # Check password (supports Django's PBKDF2 hash)
    stored_pw = user.get("password", "")
    if not check_password(password, stored_pw):
        return JsonResponse({"error": "Invalid email or password."}, status=401)

    # Generate a new token
    token = secrets.token_hex(32)
    users.update_one({"_id": user["_id"]}, {"$set": {"token": token}})

    return JsonResponse({
        "token": token,
        "name": user.get("name", ""),
        "email": user.get("email", ""),
    })


# ===================================================================
#  PRODUCTS API
# ===================================================================

@csrf_exempt
def api_products(request):
    """GET /api/auth/products/?search=...&category=..."""
    import re as _re

    search = request.GET.get("search", "")
    category = request.GET.get("category", "All")

    col = mongo_client.get_products_collection()

    query = {}
    if search:
        pattern = _re.compile(_re.escape(search), _re.IGNORECASE)
        query["$or"] = [{"name": pattern}, {"keywords": pattern}]
    if category and category != "All":
        query["category"] = category

    products = list(col.find(query).limit(50))
    return JsonResponse(_json_serialise(products), safe=False)


@csrf_exempt
def api_best_sellers(request):
    col = mongo_client.get_products_collection()
    products = list(col.find({"is_best_seller": True}).limit(12))
    return JsonResponse(_json_serialise(products), safe=False)


@csrf_exempt
def api_offers(request):
    col = mongo_client.get_products_collection()
    products = list(col.find({"discount": {"$gt": 0}}).limit(12))
    return JsonResponse(_json_serialise(products), safe=False)


# ===================================================================
#  AI PLANNER API
# ===================================================================

@csrf_exempt
def api_planner_generate(request):
    """POST /api/planner/generate/  body: {"query": "Daal Pakwaan for 4"}"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    query = data.get("query", "").strip()

    if not query:
        return JsonResponse({"error": "Please describe what you want to cook."}, status=400)

    result = generate_plan(query)

    if "error" in result:
        return JsonResponse(result, status=500)

    return JsonResponse(_json_serialise(result))


@csrf_exempt
def api_planner_add_to_cart(request):
    """POST /api/planner/add-to-cart/  body: {"items": [...], "token": "..."}"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    items = data.get("items", [])
    token = data.get("token", "")

    if not items:
        return JsonResponse({"error": "No items provided."}, status=400)

    # Find user
    user_id = "guest"
    if token:
        user = mongo_client.get_users_collection().find_one({"token": token})
        if user:
            user_id = str(user["_id"])

    cart = mongo_client.get_cart_collection()

    for item in items:
        # Check if product already in cart — if so, increase quantity
        existing = cart.find_one({
            "user_id": user_id,
            "product_id": item.get("product_id"),
        })
        if existing:
            cart.update_one(
                {"_id": existing["_id"]},
                {"$inc": {"quantity": item.get("quantity", 1)}},
            )
        else:
            cart_item = {
                "user_id": user_id,
                "product_id": item.get("product_id"),
                "product_name": item.get("product_name", ""),
                "quantity": item.get("quantity", 1),
                "price": item.get("price", 0),
                "image_url": item.get("image_url", ""),
                "added_at": datetime.utcnow(),
            }
            cart.insert_one(cart_item)

    cart_count = cart.count_documents({"user_id": user_id})

    return JsonResponse({"success": True, "cart_count": cart_count})


@csrf_exempt
def api_planner_recipe(request):
    """POST /api/planner/recipe/ body: {dish, servings, items:[approved planner items]}"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    dish = data.get("dish", "My Dish").strip() or "My Dish"
    servings = int(data.get("servings", 1) or 1)
    items = data.get("items", [])

    if not items:
        return JsonResponse({"error": "Please select at least one approved item."}, status=400)

    recipe = generate_recipe_from_approved_items(dish=dish, servings=servings, approved_items=items)
    if "error" in recipe:
        return JsonResponse(recipe, status=500)
    return JsonResponse(_json_serialise(recipe))


# ===================================================================
#  CART API
# ===================================================================

@csrf_exempt
def api_cart(request):
    """GET /api/cart/ — return user's cart items."""
    user = _get_user_from_token(request)
    user_id = str(user["_id"]) if user else "guest"

    cart = mongo_client.get_cart_collection()
    items = list(cart.find({"user_id": user_id}).sort("added_at", -1))
    return JsonResponse(_json_serialise(items), safe=False)


@csrf_exempt
def api_cart_update(request):
    """POST /api/cart/update/ — update quantity of a cart item."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user = _get_user_from_token(request)
    user_id = str(user["_id"]) if user else "guest"
    data = json.loads(request.body)
    item_id = data.get("item_id")
    quantity = int(data.get("quantity", 1))

    cart = mongo_client.get_cart_collection()

    if quantity <= 0:
        cart.delete_one({"_id": ObjectId(item_id), "user_id": user_id})
    else:
        cart.update_one(
            {"_id": ObjectId(item_id), "user_id": user_id},
            {"$set": {"quantity": quantity}},
        )

    items = list(cart.find({"user_id": user_id}))
    return JsonResponse({"success": True, "cart_count": len(items)})


@csrf_exempt
def api_cart_remove(request):
    """POST /api/cart/remove/ — remove an item from cart."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user = _get_user_from_token(request)
    user_id = str(user["_id"]) if user else "guest"
    data = json.loads(request.body)
    item_id = data.get("item_id")

    cart = mongo_client.get_cart_collection()
    cart.delete_one({"_id": ObjectId(item_id), "user_id": user_id})

    items = list(cart.find({"user_id": user_id}))
    return JsonResponse({"success": True, "cart_count": len(items)})


@csrf_exempt
def api_cart_checkout(request):
    """POST /api/cart/checkout/ — create an order from the current cart."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user = _get_user_from_token(request)
    if not user:
        return JsonResponse({"error": "Please login first."}, status=401)

    user_id = str(user["_id"])
    cart = mongo_client.get_cart_collection()
    items = list(cart.find({"user_id": user_id}))

    if not items:
        return JsonResponse({"error": "Your cart is empty."}, status=400)

    # Build order
    order_items = []
    total = 0
    for it in items:
        qty = it.get("quantity", 1)
        price = it.get("price", 0)
        line_total = qty * price
        total += line_total
        order_items.append({
            "product_id": it.get("product_id"),
            "name": it.get("product_name", ""),
            "quantity": qty,
            "price": price,
            "line_total": line_total,
            "image_url": it.get("image_url", ""),
        })

    import random
    order_id = f"BK-{random.randint(10000,99999)}"

    order_doc = {
        "user_id": user_id,
        "order_id": order_id,
        "items": order_items,
        "total_amount": round(total, 2),
        "status": "Confirmed",
        "date": datetime.utcnow(),
    }
    mongo_client.get_orders_collection().insert_one(order_doc)

    # Clear the cart
    cart.delete_many({"user_id": user_id})

    return JsonResponse({
        "success": True,
        "order_id": order_id,
        "total_amount": round(total, 2),
        "item_count": len(order_items),
    })


# ===================================================================
#  PROFILE API
# ===================================================================

@csrf_exempt
def api_profile(request):
    user = _get_user_from_token(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if request.method == "GET":
        expenses = mongo_client.get_expenses_collection()
        total = sum(
            e.get("amount", 0)
            for e in expenses.find({"user_id": str(user["_id"])})
        )
        profile = {
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "location": user.get("location", "Not provided"),
            "profile_image": user.get("profile_image", ""),
            "total_expenses": total,
        }
        return JsonResponse(profile)

    elif request.method == "PUT":
        data = json.loads(request.body)
        update_fields = {}
        for field in ("name", "email", "location", "profile_image"):
            if field in data:
                update_fields[field] = data[field]

        users = mongo_client.get_users_collection()
        users.update_one({"_id": user["_id"]}, {"$set": update_fields})
        updated = users.find_one({"_id": user["_id"]})
        return JsonResponse({
            "name": updated.get("name", ""),
            "email": updated.get("email", ""),
            "location": updated.get("location", ""),
            "profile_image": updated.get("profile_image", ""),
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


# ===================================================================
#  EXPENSES API
# ===================================================================

@csrf_exempt
def api_expenses(request):
    user = _get_user_from_token(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user_id = str(user["_id"])
    expenses = mongo_client.get_expenses_collection()

    if request.method == "GET":
        docs = list(expenses.find({"user_id": user_id}).sort("date", -1).limit(100))
        return JsonResponse(_json_serialise(docs), safe=False)

    elif request.method == "POST":
        data = json.loads(request.body)
        doc = {
            "user_id": user_id,
            "title": data.get("title", ""),
            "amount": float(data.get("amount", 0)),
            "category": data.get("category", "Other"),
            "date": datetime.utcnow(),
        }
        result = expenses.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return JsonResponse(_json_serialise(doc))

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def api_expense_graph(request, graph_type):
    user = _get_user_from_token(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user_id = str(user["_id"])
    expenses_col = mongo_client.get_expenses_collection()
    docs = list(expenses_col.find({"user_id": user_id}))

    if not docs:
        return JsonResponse({"error": "No data"}, status=404)

    if graph_type == "monthly":
        monthly = {}
        for d in docs:
            month_key = d.get("date", datetime.utcnow()).strftime("%Y-%m")
            monthly[month_key] = monthly.get(month_key, 0) + d.get("amount", 0)
        sorted_months = sorted(monthly.keys())
        data = {
            "data": [{"x": sorted_months, "y": [monthly[m] for m in sorted_months], "type": "bar", "marker": {"color": "#006036"}}],
            "layout": {"title": "Monthly Expenses", "autosize": True, "margin": {"l": 40, "r": 20, "t": 40, "b": 40}, "paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)"},
        }
        return JsonResponse(data)

    elif graph_type == "category":
        cats = {}
        for d in docs:
            cat = d.get("category", "Other")
            cats[cat] = cats.get(cat, 0) + d.get("amount", 0)
        data = {
            "data": [{"labels": list(cats.keys()), "values": list(cats.values()), "type": "pie", "marker": {"colors": ["#006036", "#1b7a4a", "#80d9a0", "#feae2c", "#835500"]}}],
            "layout": {"title": "Category Breakdown", "autosize": True, "margin": {"l": 20, "r": 20, "t": 40, "b": 20}, "paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)"},
        }
        return JsonResponse(data)

    return JsonResponse({"error": "Unknown graph type"}, status=400)


# ===================================================================
#  ORDERS API
# ===================================================================

@csrf_exempt
def api_orders(request):
    user = _get_user_from_token(request)
    if not user:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user_id = str(user["_id"])
    orders_col = mongo_client.get_orders_collection()
    docs = list(orders_col.find({"user_id": user_id}).sort("date", -1).limit(50))
    return JsonResponse(_json_serialise(docs), safe=False)