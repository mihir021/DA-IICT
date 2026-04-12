#!/usr/bin/env python
"""
seed_products.py — Populate MongoDB with sample Indian grocery products.

Usage:
    cd mainProject
    python seed_products.py

This script is standalone (not a Django management command) but loads
Django settings so it can reuse MONGODB_URI / MONGODB_DB_NAME.
"""

import os
import sys
import django
from urllib.parse import quote_plus

# Bootstrap Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainProject.settings")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from apnaCart.mongo_client import get_products_collection, ensure_product_indexes


def _real_image_url(product_name: str, category: str) -> str:
    """Return a realistic grocery photo URL for a product."""
    query = f"{product_name} {category} grocery"
    return f"https://source.unsplash.com/900x900/?{quote_plus(query)}"

PRODUCTS = [
    # ── Pulses & Lentils ────────────────────────────────────
    {"name": "Chana Dal", "category": "Pulses", "price": 72, "discount": 5, "unit": "kg", "weight": "1kg", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081035.png", "keywords": ["chana", "dal", "lentil", "gram"]},
    {"name": "Toor Dal", "category": "Pulses", "price": 95, "discount": 0, "unit": "kg", "weight": "1kg", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081035.png", "keywords": ["toor", "arhar", "dal", "lentil"]},
    {"name": "Moong Dal", "category": "Pulses", "price": 110, "discount": 8, "unit": "kg", "weight": "1kg", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081035.png", "keywords": ["moong", "dal", "lentil", "green gram"]},
    {"name": "Urad Dal", "category": "Pulses", "price": 120, "discount": 0, "unit": "kg", "weight": "1kg", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081035.png", "keywords": ["urad", "dal", "black gram"]},
    {"name": "Masoor Dal", "category": "Pulses", "price": 85, "discount": 10, "unit": "kg", "weight": "1kg", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081035.png", "keywords": ["masoor", "dal", "red lentil"]},
    {"name": "Rajma", "category": "Pulses", "price": 140, "discount": 0, "unit": "kg", "weight": "1kg", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081035.png", "keywords": ["rajma", "kidney beans"]},
    {"name": "Kabuli Chana", "category": "Pulses", "price": 130, "discount": 5, "unit": "kg", "weight": "1kg", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081035.png", "keywords": ["kabuli", "chana", "chickpeas", "chole"]},

    # ── Flour & Grains ──────────────────────────────────────
    {"name": "Wheat Flour (Atta)", "category": "Flour", "price": 210, "discount": 5, "unit": "kg", "weight": "5kg", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081992.png", "keywords": ["atta", "wheat", "flour", "chapati"]},
    {"name": "All Purpose Flour (Maida)", "category": "Flour", "price": 45, "discount": 0, "unit": "kg", "weight": "1kg", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081992.png", "keywords": ["maida", "all purpose flour", "refined flour"]},
    {"name": "Besan (Gram Flour)", "category": "Flour", "price": 65, "discount": 0, "unit": "kg", "weight": "1kg", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081992.png", "keywords": ["besan", "gram flour", "chickpea flour"]},
    {"name": "Basmati Rice", "category": "Grains", "price": 320, "discount": 10, "unit": "kg", "weight": "5kg", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081996.png", "keywords": ["rice", "basmati", "chawal"]},
    {"name": "Sooji (Semolina)", "category": "Flour", "price": 40, "discount": 0, "unit": "kg", "weight": "500g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081992.png", "keywords": ["sooji", "semolina", "rava", "suji"]},

    # ── Spices ──────────────────────────────────────────────
    {"name": "Turmeric Powder (Haldi)", "category": "Spices", "price": 35, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["turmeric", "haldi"]},
    {"name": "Red Chilli Powder", "category": "Spices", "price": 45, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["red chilli", "lal mirch", "chili"]},
    {"name": "Cumin Seeds (Jeera)", "category": "Spices", "price": 55, "discount": 5, "unit": "pack", "weight": "100g", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["cumin", "jeera"]},
    {"name": "Coriander Powder (Dhania)", "category": "Spices", "price": 30, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["coriander", "dhania"]},
    {"name": "Garam Masala", "category": "Spices", "price": 60, "discount": 0, "unit": "pack", "weight": "50g", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["garam masala", "masala"]},
    {"name": "Mustard Seeds (Rai)", "category": "Spices", "price": 25, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["mustard", "rai", "sarson"]},
    {"name": "Salt", "category": "Pantry", "price": 22, "discount": 0, "unit": "kg", "weight": "1kg", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081951.png", "keywords": ["salt", "namak", "tata salt"]},
    {"name": "Black Pepper", "category": "Spices", "price": 80, "discount": 0, "unit": "pack", "weight": "50g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["black pepper", "kali mirch"]},
    {"name": "Asafoetida (Hing)", "category": "Spices", "price": 90, "discount": 10, "unit": "pack", "weight": "50g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["hing", "asafoetida"]},
    {"name": "Fennel Seeds (Saunf)", "category": "Spices", "price": 40, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["fennel", "saunf"]},
    {"name": "Dry Mango Powder (Amchur)", "category": "Spices", "price": 35, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["amchur", "dry mango", "amchoor"]},
    {"name": "Ajwain (Carom Seeds)", "category": "Spices", "price": 30, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["ajwain", "carom"]},

    # ── Oil & Ghee ──────────────────────────────────────────
    {"name": "Vegetable Oil", "category": "Oil", "price": 150, "discount": 5, "unit": "L", "weight": "1L", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081965.png", "keywords": ["vegetable oil", "refined oil", "cooking oil"]},
    {"name": "Mustard Oil", "category": "Oil", "price": 170, "discount": 0, "unit": "L", "weight": "1L", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081965.png", "keywords": ["mustard oil", "sarson ka tel"]},
    {"name": "Desi Ghee", "category": "Dairy", "price": 550, "discount": 8, "unit": "kg", "weight": "500ml", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081965.png", "keywords": ["ghee", "desi ghee", "clarified butter"]},

    # ── Dairy ───────────────────────────────────────────────
    {"name": "Full Cream Milk", "category": "Dairy", "price": 66, "discount": 0, "unit": "L", "weight": "1L", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081967.png", "keywords": ["milk", "full cream", "doodh"]},
    {"name": "Curd (Yogurt)", "category": "Dairy", "price": 40, "discount": 0, "unit": "pack", "weight": "400g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081967.png", "keywords": ["curd", "yogurt", "dahi"]},
    {"name": "Paneer", "category": "Dairy", "price": 90, "discount": 5, "unit": "pack", "weight": "200g", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081967.png", "keywords": ["paneer", "cottage cheese"]},
    {"name": "Butter", "category": "Dairy", "price": 55, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081967.png", "keywords": ["butter", "makhan"]},
    {"name": "Cream", "category": "Dairy", "price": 35, "discount": 0, "unit": "pack", "weight": "200ml", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081967.png", "keywords": ["cream", "fresh cream", "malai"]},

    # ── Vegetables ───────────────────────────────────────────
    {"name": "Onion", "category": "Vegetables", "price": 30, "discount": 0, "unit": "kg", "weight": "1kg", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/1135/1135549.png", "keywords": ["onion", "pyaaz", "pyaz"]},
    {"name": "Tomato", "category": "Vegetables", "price": 40, "discount": 0, "unit": "kg", "weight": "1kg", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/1135/1135549.png", "keywords": ["tomato", "tamatar"]},
    {"name": "Potato", "category": "Vegetables", "price": 25, "discount": 0, "unit": "kg", "weight": "1kg", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/1135/1135549.png", "keywords": ["potato", "aloo"]},
    {"name": "Green Chilli", "category": "Vegetables", "price": 15, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/1135/1135549.png", "keywords": ["green chilli", "hari mirch"]},
    {"name": "Ginger", "category": "Vegetables", "price": 20, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/1135/1135549.png", "keywords": ["ginger", "adrak"]},
    {"name": "Garlic", "category": "Vegetables", "price": 25, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/1135/1135549.png", "keywords": ["garlic", "lehsun", "lahsun"]},
    {"name": "Fresh Coriander Leaves", "category": "Vegetables", "price": 10, "discount": 0, "unit": "bunch", "weight": "1 bunch", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/1135/1135549.png", "keywords": ["coriander", "dhania", "cilantro", "fresh coriander"]},
    {"name": "Curry Leaves", "category": "Vegetables", "price": 8, "discount": 0, "unit": "bunch", "weight": "1 bunch", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/1135/1135549.png", "keywords": ["curry leaves", "kadi patta"]},
    {"name": "Lemon", "category": "Fruits", "price": 10, "discount": 0, "unit": "pcs", "weight": "1 pc", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/1135/1135549.png", "keywords": ["lemon", "nimbu"]},

    # ── Fruits ──────────────────────────────────────────────
    {"name": "Shimla Apple", "category": "Fruits", "price": 180, "discount": 10, "unit": "kg", "weight": "1kg", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/415/415682.png", "keywords": ["apple", "seb"]},
    {"name": "Banana", "category": "Fruits", "price": 40, "discount": 0, "unit": "dozen", "weight": "1 dozen", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/415/415682.png", "keywords": ["banana", "kela"]},

    # ── Pantry Staples ──────────────────────────────────────
    {"name": "Sugar", "category": "Pantry", "price": 45, "discount": 0, "unit": "kg", "weight": "1kg", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081951.png", "keywords": ["sugar", "cheeni", "shakkar"]},
    {"name": "Jaggery (Gur)", "category": "Pantry", "price": 60, "discount": 0, "unit": "kg", "weight": "500g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081951.png", "keywords": ["jaggery", "gur", "gud"]},
    {"name": "Tamarind (Imli)", "category": "Pantry", "price": 30, "discount": 0, "unit": "pack", "weight": "200g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081951.png", "keywords": ["tamarind", "imli"]},
    {"name": "Baking Soda", "category": "Pantry", "price": 15, "discount": 0, "unit": "pack", "weight": "50g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081951.png", "keywords": ["baking soda", "meetha soda"]},
    {"name": "Dry Red Chilli", "category": "Spices", "price": 50, "discount": 0, "unit": "pack", "weight": "100g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/2909/2909820.png", "keywords": ["dry red chilli", "sabut lal mirch"]},

    # ── Snacks & Beverages ──────────────────────────────────
    {"name": "Tea (Chai Patti)", "category": "Beverages", "price": 120, "discount": 10, "unit": "pack", "weight": "250g", "is_best_seller": True, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081948.png", "keywords": ["tea", "chai", "patti"]},
    {"name": "Papad", "category": "Snacks", "price": 40, "discount": 0, "unit": "pack", "weight": "200g", "is_best_seller": False, "image_url": "https://cdn-icons-png.flaticon.com/512/3081/3081948.png", "keywords": ["papad", "papadum"]},
]


def seed():
    col = get_products_collection()

    # Clear existing products (optional — comment out if you want to keep them)
    col.delete_many({})
    print(f"🗑️  Cleared existing products.")

    # Replace icon-like images with realistic grocery photos.
    for product in PRODUCTS:
        product["image_url"] = _real_image_url(product.get("name", "grocery"), product.get("category", "food"))

    # Insert
    result = col.insert_many(PRODUCTS)
    print(f"✅ Inserted {len(result.inserted_ids)} products into MongoDB.")

    # Create search index
    ensure_product_indexes()
    print("📇 Text search index ensured.")


if __name__ == "__main__":
    seed()
