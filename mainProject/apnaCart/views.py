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

def product_page(request, product_id):
    return render(request, "product.html", {"product_id": product_id})


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
#  PRODUCTS API (with Dynamic Pricing)
# ===================================================================

from .dynamic_pricing import calculate_dynamic_price


def _get_session_data(request):
    """Extract session pricing data from the request."""
    # Session data stored in Django session
    if not hasattr(request, 'session'):
        return {"category_views": {}, "total_views": 0, "cart_count": 0}
    return {
        "category_views": request.session.get("dp_category_views", {}),
        "total_views": request.session.get("dp_total_views", 0),
        "cart_count": request.session.get("dp_cart_count", 0),
    }


def _track_product_view(request, category):
    """Track a product view in the session for dynamic pricing."""
    if not hasattr(request, 'session'):
        return
    views = request.session.get("dp_category_views", {})
    views[category] = views.get(category, 0) + 1
    request.session["dp_category_views"] = views
    request.session["dp_total_views"] = request.session.get("dp_total_views", 0) + 1
    request.session.modified = True


def _apply_dynamic_pricing(products, session_data):
    """Apply dynamic pricing to a list of product dicts."""
    for p in products:
        dp = calculate_dynamic_price(
            base_price=p.get("price", 0),
            existing_discount_pct=p.get("discount", 0),
            category=p.get("category", "Other"),
            is_best_seller=p.get("is_best_seller", False),
            session_data=session_data,
        )
        p["dynamic_price"] = dp["final_price"]
        p["effective_discount"] = dp["effective_discount"]
        p["savings"] = dp["savings"]
        p["dynamic_adjustment"] = dp["dynamic_adjustment"]
        p["pricing_factors"] = dp["factors"]
    return products


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
        query["$or"] = [{"name": pattern}, {"keywords": pattern}, {"category": pattern}]
    if category and category != "All":
        query["category"] = category

    products = list(col.find(query).limit(50))
    serialised = _json_serialise(products)

    # Apply dynamic pricing
    session_data = _get_session_data(request)
    serialised = _apply_dynamic_pricing(serialised, session_data)

    return JsonResponse(serialised, safe=False)


@csrf_exempt
def api_best_sellers(request):
    col = mongo_client.get_products_collection()
    products = list(col.find({"is_best_seller": True}).limit(12))
    serialised = _json_serialise(products)
    session_data = _get_session_data(request)
    serialised = _apply_dynamic_pricing(serialised, session_data)
    return JsonResponse(serialised, safe=False)


@csrf_exempt
def api_offers(request):
    col = mongo_client.get_products_collection()
    products = list(col.find({"discount": {"$gt": 0}}).limit(12))
    serialised = _json_serialise(products)
    session_data = _get_session_data(request)
    serialised = _apply_dynamic_pricing(serialised, session_data)
    return JsonResponse(serialised, safe=False)


@csrf_exempt
def api_product_detail(request, product_id):
    """GET /api/auth/products/<product_id>/ — return a single product with dynamic pricing."""
    try:
        col = mongo_client.get_products_collection()
        product = col.find_one({"_id": ObjectId(product_id)})
        if not product:
            return JsonResponse({"error": "Product not found"}, status=404)

        serialised = _json_serialise(product)

        # Track this view for dynamic pricing
        _track_product_view(request, product.get("category", "Other"))

        # Apply dynamic pricing
        session_data = _get_session_data(request)
        dp = calculate_dynamic_price(
            base_price=serialised.get("price", 0),
            existing_discount_pct=serialised.get("discount", 0),
            category=serialised.get("category", "Other"),
            is_best_seller=serialised.get("is_best_seller", False),
            session_data=session_data,
        )
        serialised["dynamic_price"] = dp["final_price"]
        serialised["effective_discount"] = dp["effective_discount"]
        serialised["savings"] = dp["savings"]
        serialised["dynamic_adjustment"] = dp["dynamic_adjustment"]
        serialised["pricing_factors"] = dp["factors"]

        return JsonResponse(serialised)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def api_product_suggestions(request, product_id):
    """GET /api/auth/products/<product_id>/suggestions/ — return related products."""
    try:
        col = mongo_client.get_products_collection()
        product = col.find_one({"_id": ObjectId(product_id)})
        if not product:
            return JsonResponse({"error": "Product not found"}, status=404)

        # Find products in the same category, excluding the current product
        suggestions = list(
            col.find({
                "category": product.get("category", ""),
                "_id": {"$ne": ObjectId(product_id)},
            }).limit(8)
        )

        # If not enough suggestions, pad with best sellers from other categories
        if len(suggestions) < 4:
            extra = list(
                col.find({
                    "_id": {"$ne": ObjectId(product_id)},
                    "is_best_seller": True,
                }).limit(8 - len(suggestions))
            )
            existing_ids = {str(s["_id"]) for s in suggestions}
            for e in extra:
                if str(e["_id"]) not in existing_ids:
                    suggestions.append(e)

        serialised = _json_serialise(suggestions)
        session_data = _get_session_data(request)
        serialised = _apply_dynamic_pricing(serialised, session_data)
        return JsonResponse(serialised, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def api_track_session(request):
    """POST /api/session/track/ — Track user session activity for dynamic pricing."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        action = data.get("action", "")

        if action == "view_product":
            category = data.get("category", "Other")
            _track_product_view(request, category)

        elif action == "cart_update":
            request.session["dp_cart_count"] = data.get("cart_count", 0)
            request.session.modified = True

        elif action == "reset":
            request.session["dp_category_views"] = {}
            request.session["dp_total_views"] = 0
            request.session["dp_cart_count"] = 0
            request.session.modified = True

        return JsonResponse({
            "status": "ok",
            "session": _get_session_data(request),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


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

    from .ai_planner import generate_plan

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

        # Format month labels for readability (e.g. "Apr 2026")
        month_labels = []
        for m in sorted_months:
            try:
                dt = datetime.strptime(m, "%Y-%m")
                month_labels.append(dt.strftime("%b %Y"))
            except Exception:
                month_labels.append(m)

        data = {
            "data": [{
                "x": month_labels,
                "y": [monthly[m] for m in sorted_months],
                "type": "scatter",
                "mode": "lines+markers",
                "fill": "tozeroy",
                "fillcolor": "rgba(0,96,54,0.08)",
                "line": {"color": "#006036", "width": 3, "shape": "spline"},
                "marker": {"color": "#006036", "size": 8, "symbol": "circle"},
                "name": "Expenses",
                "hovertemplate": "%{x}<br>₹%{y:,.0f}<extra></extra>",
            }],
            "layout": {
                "autosize": True,
                "margin": {"l": 55, "r": 15, "t": 15, "b": 50},
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "xaxis": {
                    "title": {"text": "Month", "font": {"size": 12, "color": "#71717a"}},
                    "gridcolor": "rgba(0,0,0,0.04)",
                    "tickangle": -30,
                    "tickfont": {"size": 11, "color": "#52525b"},
                },
                "yaxis": {
                    "title": {"text": "₹ Amount", "font": {"size": 12, "color": "#71717a"}},
                    "gridcolor": "rgba(0,0,0,0.04)",
                    "tickfont": {"size": 11, "color": "#52525b"},
                    "tickprefix": "₹",
                },
                "hovermode": "x unified",
            },
        }
        return JsonResponse(data)

    elif graph_type == "category":
        # Keyword-based classification into grocery categories
        CATEGORY_KEYWORDS = {
            "Dairy Products": ["milk", "curd", "paneer", "cheese", "butter", "yogurt", "cream", "ghee", "dahi", "lassi", "buttermilk", "whey"],
            "Fruits": ["apple", "banana", "mango", "grape", "orange", "papaya", "watermelon", "pomegranate", "guava", "kiwi", "pineapple", "strawberry", "lemon", "lime", "coconut", "fig", "cherry", "fruit"],
            "Vegetables": ["potato", "tomato", "onion", "carrot", "cabbage", "spinach", "brinjal", "capsicum", "peas", "beans", "cauliflower", "broccoli", "ginger", "garlic", "chilli", "pepper", "corn", "vegetable", "sabzi", "bhindi", "palak", "gobi", "methi", "cucumber", "radish"],
            "Pulses & Lentils": ["dal", "daal", "dhal", "lentil", "chana", "rajma", "moong", "toor", "masoor", "urad", "pulse", "legume", "bean", "chickpea", "soybean"],
            "Flour & Grains": ["flour", "atta", "maida", "sooji", "suji", "rava", "besan", "rice", "wheat", "bajra", "jowar", "ragi", "oats", "grain", "cereal", "bread", "roti", "chapati"],
            "Oil & Ghee": ["oil", "ghee", "mustard oil", "olive oil", "sunflower", "refined", "coconut oil", "sesame oil", "groundnut oil"],
            "Pantry & Spices": ["salt", "sugar", "spice", "masala", "turmeric", "haldi", "cumin", "jeera", "coriander", "dhaniya", "chilli powder", "garam masala", "sauce", "ketchup", "vinegar", "pickle", "jam", "honey", "noodle", "pasta", "maggi", "biscuit", "papad", "pickle"],
            "Beverages": ["tea", "coffee", "chai", "juice", "water", "soda", "drink", "cola", "shake", "smoothie"],
            "Snacks": ["chips", "namkeen", "bhujia", "cookie", "cake", "chocolate", "sweet", "halwa", "ladoo", "snack", "popcorn", "crackers"],
            "Meat & Eggs": ["chicken", "mutton", "fish", "egg", "prawn", "shrimp", "meat", "pork", "lamb"],
        }

        cats = {}
        for d in docs:
            title = d.get("title", "").lower().strip()
            original_category = d.get("category", "Other")
            matched_cat = None

            # Try to match by title keywords first
            for cat_name, keywords in CATEGORY_KEYWORDS.items():
                for kw in keywords:
                    if kw in title:
                        matched_cat = cat_name
                        break
                if matched_cat:
                    break

            # Fallback to the original category, or "Other"
            if not matched_cat:
                matched_cat = original_category if original_category else "Other"

            cats[matched_cat] = cats.get(matched_cat, 0) + d.get("amount", 0)

        # Sort by value descending for a cleaner pie chart
        sorted_cats = sorted(cats.items(), key=lambda x: x[1], reverse=True)
        labels = [c[0] for c in sorted_cats]
        values = [c[1] for c in sorted_cats]

        # Vibrant color palette for grocery categories
        category_colors = {
            "Dairy Products": "#60a5fa",
            "Fruits": "#f97316",
            "Vegetables": "#22c55e",
            "Pulses & Lentils": "#eab308",
            "Flour & Grains": "#a78bfa",
            "Oil & Ghee": "#f59e0b",
            "Pantry & Spices": "#ef4444",
            "Beverages": "#06b6d4",
            "Snacks": "#ec4899",
            "Meat & Eggs": "#b45309",
            "Grocery": "#006036",
            "Dining": "#8b5cf6",
            "Travel": "#14b8a6",
            "Bills": "#64748b",
            "Other": "#a1a1aa",
        }
        colors = [category_colors.get(l, "#71717a") for l in labels]

        data = {
            "data": [{
                "labels": labels,
                "values": values,
                "type": "pie",
                "hole": 0.45,
                "textinfo": "label+percent",
                "textposition": "inside",
                "insidetextorientation": "radial",
                "marker": {
                    "colors": colors,
                    "line": {"color": "#ffffff", "width": 2},
                },
                "hovertemplate": "%{label}<br>₹%{value:,.0f} (%{percent})<extra></extra>",
                "textfont": {"size": 11, "color": "#ffffff"},
            }],
            "layout": {
                "autosize": True,
                "margin": {"l": 50, "r": 50, "t": 15, "b": 60},
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "showlegend": True,
                "legend": {
                    "orientation": "h",
                    "y": -0.2,
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 10, "color": "#52525b"},
                },
            },
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


# ===================================================================
#  ML MODEL API
# ===================================================================

@csrf_exempt
def api_ml_model_info(request):
    """GET /api/ml/model-info/ — return ML model metadata and metrics."""
    try:
        from .ml_pricing_model import get_model_metadata
        meta = get_model_metadata()
        if not meta:
            return JsonResponse({"error": "No trained model found"}, status=404)

        # Convert feature importances to a serialisable format
        result = {
            "model_type": "GradientBoostingRegressor",
            "library": "scikit-learn",
            "mae": meta.get("mae"),
            "r2_score": meta.get("r2_score"),
            "n_samples": meta.get("n_samples"),
            "n_train": meta.get("n_train"),
            "n_test": meta.get("n_test"),
            "trained_at": meta.get("trained_at"),
            "feature_importances": [
                {"feature": f, "importance": round(imp, 4)}
                for f, imp in meta.get("feature_importances", [])
            ],
        }
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def api_ml_retrain(request):
    """POST /api/ml/retrain/ — retrain the ML pricing model."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        from .ml_pricing_model import train_model
        metrics = train_model(n_samples=5000)
        return JsonResponse({
            "success": True,
            "mae": metrics["mae"],
            "r2_score": metrics["r2_score"],
            "message": f"Model retrained on {metrics['n_samples']} samples. "
                       f"MAE: {metrics['mae']}, R²: {metrics['r2_score']}",
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
