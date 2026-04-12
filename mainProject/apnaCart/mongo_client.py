"""
mongo_client.py - MongoDB client with safe in-memory fallback for local dev.

If MongoDB URI is missing/invalid/unreachable, the app switches to an
in-memory store so signup/login/cart flows still work for demo/testing.
"""

from __future__ import annotations

import copy
import re
import threading
from dataclasses import dataclass

from bson import ObjectId
from django.conf import settings
from pymongo import MongoClient, TEXT

_client = None
_fallback_db = None
_init_lock = threading.Lock()
_using_fallback = False


def _is_placeholder(uri: str) -> bool:
    if not uri:
        return True
    bad_tokens = ("<username>", "<password>", "<cluster>")
    return any(token in uri for token in bad_tokens)


def _match(doc: dict, query: dict) -> bool:
    if not query:
        return True
    for key, val in query.items():
        if key == "$or":
            if not any(_match(doc, sub) for sub in val):
                return False
            continue
        actual = doc.get(key)
        if isinstance(val, dict):
            if "$gt" in val:
                if not (actual is not None and actual > val["$gt"]):
                    return False
            elif "$text" in val:
                needle = str(val["$text"].get("$search", "")).lower()
                hay = " ".join(
                    [
                        str(doc.get("name", "")),
                        str(doc.get("category", "")),
                        str(doc.get("keywords", "")),
                    ]
                ).lower()
                if needle not in hay:
                    return False
            else:
                if actual != val:
                    return False
        elif hasattr(val, "search"):
            if not val.search(str(actual or "")):
                return False
        else:
            if actual != val:
                return False
    return True


class InMemoryCursor:
    def __init__(self, docs: list[dict]):
        self._docs = docs

    def sort(self, key, direction=1):
        reverse = direction == -1
        self._docs.sort(key=lambda d: d.get(key), reverse=reverse)
        return self

    def limit(self, n: int):
        self._docs = self._docs[:n]
        return self

    def __iter__(self):
        return iter(self._docs)


@dataclass
class InsertResult:
    inserted_id: ObjectId


class InMemoryCollection:
    def __init__(self):
        self.docs: list[dict] = []

    def index_information(self):
        return {}

    def create_index(self, *args, **kwargs):
        return None

    def find(self, query=None, projection=None):
        query = query or {}
        rows = [copy.deepcopy(d) for d in self.docs if _match(d, query)]
        if projection and projection.get("_id") == 0:
            for row in rows:
                row.pop("_id", None)
        return InMemoryCursor(rows)

    def find_one(self, query=None, projection=None):
        for d in self.find(query, projection):
            return d
        return None

    def insert_one(self, doc: dict):
        row = copy.deepcopy(doc)
        row.setdefault("_id", ObjectId())
        self.docs.append(row)
        return InsertResult(inserted_id=row["_id"])

    def update_one(self, query: dict, update: dict):
        for i, d in enumerate(self.docs):
            if _match(d, query):
                row = self.docs[i]
                if "$set" in update:
                    row.update(update["$set"])
                if "$inc" in update:
                    for k, v in update["$inc"].items():
                        row[k] = row.get(k, 0) + v
                return

    def delete_one(self, query: dict):
        for i, d in enumerate(self.docs):
            if _match(d, query):
                self.docs.pop(i)
                return

    def delete_many(self, query: dict):
        self.docs = [d for d in self.docs if not _match(d, query)]

    def count_documents(self, query: dict):
        return sum(1 for d in self.docs if _match(d, query))


class InMemoryDB:
    def __init__(self):
        self._cols: dict[str, InMemoryCollection] = {}
        self._seed()

    def __getitem__(self, name: str):
        if name not in self._cols:
            self._cols[name] = InMemoryCollection()
        return self._cols[name]

    def _seed(self):
        products = self["products"]
        seeded = [
            {
                "name": "Amul Full Cream Milk",
                "category": "Dairy",
                "price": 68,
                "discount": 6,
                "weight": "1L",
                "image_url": "",
                "keywords": "milk dairy amul",
                "is_best_seller": True,
            },
            {
                "name": "Fresh Banana",
                "category": "Fruits",
                "price": 50,
                "discount": 10,
                "weight": "1 Dozen",
                "image_url": "",
                "keywords": "banana fruit",
                "is_best_seller": True,
            },
            {
                "name": "Toor Dal",
                "category": "Pulses",
                "price": 145,
                "discount": 0,
                "weight": "1kg",
                "image_url": "",
                "keywords": "dal pulses",
                "is_best_seller": False,
            },
            {
                "name": "Aashirvaad Atta",
                "category": "Flour",
                "price": 280,
                "discount": 8,
                "weight": "5kg",
                "image_url": "",
                "keywords": "flour atta wheat",
                "is_best_seller": True,
            },
            {
                "name": "Tomato",
                "category": "Vegetables",
                "price": 40,
                "discount": 0,
                "weight": "1kg",
                "image_url": "",
                "keywords": "tomato vegetable",
                "is_best_seller": False,
            },
        ]
        for p in seeded:
            products.insert_one(p)


def _get_client():
    global _client, _fallback_db, _using_fallback
    with _init_lock:
        if _client is not None:
            return _client
        uri = getattr(settings, "MONGODB_URI", "") or ""
        if _is_placeholder(uri):
            _using_fallback = True
            _fallback_db = InMemoryDB()
            return None
        try:
            client = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=10000,
            )
            client.admin.command("ping")
            _client = client
            _using_fallback = False
            return _client
        except Exception:
            _using_fallback = True
            _fallback_db = InMemoryDB()
            return None


def get_db():
    client = _get_client()
    if client is None:
        return _fallback_db
    return client[settings.MONGODB_DB_NAME]


def using_fallback() -> bool:
    _get_client()
    return _using_fallback


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


def ensure_product_indexes():
    col = get_products_collection()
    existing = col.index_information()
    if "text_search" not in existing:
        try:
            col.create_index(
                [("name", TEXT), ("keywords", TEXT), ("category", TEXT)],
                name="text_search",
            )
        except Exception:
            pass


def search_products(query_text: str, limit: int = 20) -> list:
    col = get_products_collection()
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

    pattern = re.compile(re.escape(query_text), re.IGNORECASE)
    return list(
        col.find({"$or": [{"name": pattern}, {"keywords": pattern}, {"category": pattern}]}).limit(limit)
    )


def search_product_by_name(name: str):
    col = get_products_collection()
    pattern = re.compile(f"^{re.escape(name)}$", re.IGNORECASE)
    product = col.find_one({"name": pattern})
    if product:
        return product
    pattern = re.compile(re.escape(name), re.IGNORECASE)
    return col.find_one({"$or": [{"name": pattern}, {"keywords": pattern}]})
