"""
mongo_client.py — Singleton MongoDB connection for BasketIQ / ApnaCart.

Uses pymongo to connect to MongoDB Atlas.  Every other module should
import helpers from here instead of creating its own MongoClient.
"""

import re
from pymongo import MongoClient, TEXT
from django.conf import settings

# ---------------------------------------------------------------------------
# Singleton client – created once, reused across the Django process.
# ---------------------------------------------------------------------------
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGODB_URI)
    return _client


def get_db():
    """Return the main application database."""
    return _get_client()[settings.MONGODB_DB_NAME]


# ---------------------------------------------------------------------------
# Collection accessors
# ---------------------------------------------------------------------------


def get_products_collection():
    return get_db()["products"]


def get_cart_collection():
    return get_db()["cart"]


def get_users_collection():
    return get_db()["users"]


def get_orders_collection():
    return get_db()["orders"]


def get_expenses_collection():
    return get_db()["expenses"]


# ---------------------------------------------------------------------------
# Product search helpers
# ---------------------------------------------------------------------------


def ensure_product_indexes():
    """Create text index on products if it doesn't already exist."""
    col = get_products_collection()
    existing = col.index_information()
    if "text_search" not in existing:
        try:
            col.create_index(
                [("name", TEXT), ("keywords", TEXT), ("category", TEXT)],
                name="text_search",
            )
        except Exception:
            pass  # index may already exist in a different form


def search_products(query_text: str, limit: int = 20) -> list:
    """
    Search products by name/keyword.  Tries MongoDB text search first;
    falls back to case-insensitive regex if text search returns nothing.
    """
    col = get_products_collection()

    # Attempt 1: full-text search
    try:
        results = list(
            col.find(
                {"$text": {"$search": query_text}},
                {"score": {"$meta": "textScore"}},
            )
            .sort([("score", {"$meta": "textScore"})])
            .limit(limit)
        )
        if results:
            return results
    except Exception:
        pass

    # Attempt 2: regex fallback
    pattern = re.compile(re.escape(query_text), re.IGNORECASE)
    results = list(
        col.find(
            {"$or": [{"name": pattern}, {"keywords": pattern}, {"category": pattern}]}
        ).limit(limit)
    )
    return results


def search_product_by_name(name: str):
    """Find the single best match for a product name."""
    col = get_products_collection()

    # Exact match first (case-insensitive)
    pattern = re.compile(f"^{re.escape(name)}$", re.IGNORECASE)
    product = col.find_one({"name": pattern})
    if product:
        return product

    # Partial match
    pattern = re.compile(re.escape(name), re.IGNORECASE)
    product = col.find_one(
        {"$or": [{"name": pattern}, {"keywords": pattern}]}
    )
    return product
