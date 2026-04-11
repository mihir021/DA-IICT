import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# We look for MONGODB_URI first (standard for Atlas)
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "pulseprice_admin")

# Collection names
USERS = "users"
EXPENSES = "expenses"
ORDERS = "orders"
PRODUCTS = "products"

def get_db():
    if not MONGO_URI:
        print("CRITICAL ERROR: MONGODB_URI not found in environment")
        return None
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        
        # Ensure collections exist
        existing = db.list_collection_names()
        for col in [USERS, EXPENSES, ORDERS, PRODUCTS]:
            if col not in existing:
                db.create_collection(col)
        
        return db
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None
