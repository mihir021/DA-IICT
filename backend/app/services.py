import bcrypt
import jwt
import datetime
import os
import plotly.express as px
import pandas as pd
from .database import get_db, USERS, EXPENSES, ORDERS
from bson import ObjectId
from rest_framework.exceptions import ValidationError, AuthenticationFailed

JWT_SECRET = os.getenv("DJANGO_SECRET_KEY", "your-secret-key")

def signup_user(data: dict) -> dict:
    db = get_db()
    if db is None:
        raise ValidationError({"error": "Database connection failed."})
    if db[USERS].find_one({"email": data["email"]}):
        raise ValidationError({"error": "Email already registered."})
    
    hashed_pw = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user_doc = {
        "name": data["name"],
        "email": data["email"],
        "password": hashed_pw,
        "location": data.get("location", ""),
        "profile_image": "",
        "created_at": datetime.datetime.utcnow(),
    }
    result = db[USERS].insert_one(user_doc)
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}

def login_user(data: dict) -> dict:
    db = get_db()
    if db is None:
        raise AuthenticationFailed("Database connection failed.")
    user = db[USERS].find_one({"email": data["email"]})
    if not user:
        raise AuthenticationFailed("Incorrect email or password.")
    
    stored_pw = user["password"]
    incoming_pw = data["password"].encode('utf-8')
    
    # Support both bcrypt and legacy SHA-256 passwords
    password_ok = False
    if stored_pw.startswith("$2"):
        # It's a bcrypt hash
        password_ok = bcrypt.checkpw(incoming_pw, stored_pw.encode('utf-8'))
    else:
        # Legacy: plain SHA-256 hash — migrate to bcrypt on successful login
        import hashlib
        legacy_hash = hashlib.sha256(incoming_pw).hexdigest()
        if legacy_hash == stored_pw:
            password_ok = True
            # Migrate to bcrypt
            new_hash = bcrypt.hashpw(incoming_pw, bcrypt.gensalt()).decode('utf-8')
            db[USERS].update_one({"_id": user["_id"]}, {"$set": {"password": new_hash}})
    
    if not password_ok:
        raise AuthenticationFailed("Incorrect email or password.")
    
    token = jwt.encode({
        "user_id": str(user["_id"]), 
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, JWT_SECRET, algorithm="HS256")
    
    token_str = token.decode('utf-8') if isinstance(token, bytes) else token
    return {"token": token_str, "name": user["name"], "email": user["email"]}

def get_profile(user_id: str) -> dict:
    db = get_db()
    if db is None:
        return None
    user = db[USERS].find_one({"_id": ObjectId(user_id)})
    if not user:
        return None
    
    # Calculate total expenses
    expenses = list(db[EXPENSES].find({"user_id": user_id}))
    total_expenses = sum(exp.get("amount", 0) for exp in expenses)
    
    return {
        "name": user["name"],
        "email": user["email"],
        "location": user.get("location", "Not provided"),
        "profile_image": user.get("profile_image", ""),
        "total_expenses": total_expenses
    }

def update_profile(user_id: str, data: dict) -> dict:
    db = get_db()
    if db is None:
        return None
    update_data = {
        "name": data.get("name"),
        "email": data.get("email"),
        "location": data.get("location", ""),
    }
    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    db[USERS].update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    return get_profile(user_id)

def get_user_expenses(user_id: str) -> list:
    db = get_db()
    if db is None:
        return []
    expenses_cursor = list(db[EXPENSES].find({"user_id": user_id}))
    output = []
    for exp in expenses_cursor:
        exp["id"] = str(exp.get("_id", "unknown"))
        if "_id" in exp: del exp["_id"]
        if "user_id" in exp: del exp["user_id"]
        if "date" in exp and isinstance(exp["date"], datetime.datetime):
            exp["date"] = exp["date"].isoformat()
        output.append(exp)
    return output

def add_user_expense(user_id: str, data: dict) -> dict:
    db = get_db()
    if db is None:
        raise ValidationError({"error": "Database connection failed."})
    expense = {
        "user_id": user_id,
        "title": data["title"],
        "amount": float(data["amount"]),
        "category": data["category"],
        "date": datetime.datetime.utcnow()
    }
    result = db[EXPENSES].insert_one(expense)
    expense["id"] = str(result.inserted_id)
    del expense["_id"]
    del expense["user_id"]
    expense["date"] = expense["date"].isoformat()
    return expense

def get_user_orders(user_id: str) -> list:
    db = get_db()
    if db is None:
        return []
    orders_cursor = list(db[ORDERS].find({"user_id": user_id}))
    output = []
    for order in orders_cursor:
        order["id"] = str(order.get("_id", "unknown"))
        if "_id" in order: del order["_id"]
        if "user_id" in order: del order["user_id"]
        output.append(order)
    return output

def generate_monthly_expense_graph(user_id: str):
    db = get_db()
    if db is None:
        return None
    expenses = list(db[EXPENSES].find({"user_id": user_id}))
    if not expenses:
        return None
    
    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%b %Y')
    
    monthly_data = df.groupby('month')['amount'].sum().reset_index()
    
    fig = px.bar(monthly_data, x='month', y='amount', title="Monthly Expenses",
                 labels={'amount': 'Total Amount', 'month': 'Month'})
    return fig.to_json()

def generate_category_expense_graph(user_id: str):
    db = get_db()
    if db is None:
        return None
    expenses = list(db[EXPENSES].find({"user_id": user_id}))
    if not expenses:
        return None
    
    df = pd.DataFrame(expenses)
    category_data = df.groupby('category')['amount'].sum().reset_index()
    
    fig = px.pie(category_data, names='category', values='amount', title="Expenses by Category")
    return fig.to_json()

def get_all_products(search_query="", category="All"):
    db = get_db()
    if db is None:
        return []
    query = {}
    if search_query:
        query["name"] = {"$regex": search_query, "$options": "i"}
    if category != "All":
        query["category"] = category
    
    products = list(db[PRODUCTS].find(query))
    for p in products: 
        p["id"] = str(p["_id"])
        del p["_id"]
    return products

def get_special_products(type_name):
    db = get_db()
    if db is None:
        return []
    # In a real app, we might filter by a flag. For now, we'll return some based on query.
    if type_name == "best_sellers":
        products = list(db[PRODUCTS].find().limit(4))
    else:
        products = list(db[PRODUCTS].find().skip(4).limit(4))
        
    for p in products: 
        p["id"] = str(p["_id"])
        del p["_id"]
    return products
