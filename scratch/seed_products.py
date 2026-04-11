import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGO_DB_NAME", "pulseprice_admin")

client = MongoClient(uri)
db = client[db_name]

products = [
    {"name": "Organic Red Apples", "price": 180, "category": "Fruits", "weight": "1kg"},
    {"name": "Whole Wheat Atta", "price": 340, "category": "Kitchen Staples", "weight": "5kg"},
    {"name": "Farm Fresh Milk", "price": 65, "category": "Dairy & Eggs", "weight": "1L"},
    {"name": "Cherry Tomatoes", "price": 45, "category": "Vegetables", "weight": "250g"},
    {"name": "Desi Ghee", "price": 580, "category": "Dairy & Eggs", "weight": "500ml"}
]

if db.products.count_documents({}) == 0:
    db.products.insert_many(products)
    print("Seeded products successfully!")
else:
    print("Products already exist.")
