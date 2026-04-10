from datetime import UTC, datetime, timedelta
import os

import django
from django.contrib.auth.hashers import make_password

from database.collections import ADMIN_LOGS, ADMIN_USERS, ORDERS, PRODUCTS, USERS
from database.connection import get_database
from database.seed_data import build_admin_logs, build_orders, build_products, build_users


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pulseprice.settings")
django.setup()

def seed() -> None:
    database = get_database()
    if database is None:
        raise RuntimeError("MongoDB connection is not available. Set MONGO_URI in your .env file.")

    products = build_products()
    users = build_users()
    orders = build_orders(products, users)

    if database[PRODUCTS].count_documents({}) == 0:
        database[PRODUCTS].insert_many(products)

    if database[USERS].count_documents({}) == 0:
        database[USERS].insert_many(users)

    if database[ORDERS].count_documents({}) == 0:
        database[ORDERS].insert_many(orders)

    if database[ADMIN_LOGS].count_documents({}) == 0:
        database[ADMIN_LOGS].insert_many(build_admin_logs())

    bootstrap_email = os.getenv("ADMIN_BOOTSTRAP_EMAIL")
    bootstrap_password = os.getenv("ADMIN_BOOTSTRAP_PASSWORD")
    bootstrap_name = os.getenv("ADMIN_BOOTSTRAP_NAME", "Store Manager")
    if bootstrap_email and bootstrap_password and database[ADMIN_USERS].count_documents({}) == 0:
        database[ADMIN_USERS].insert_one(
            {
                "name": bootstrap_name,
                "email": bootstrap_email,
                "password_hash": make_password(bootstrap_password),
                "is_staff": True,
                "role": "operations_admin",
            }
        )


if __name__ == "__main__":
    seed()
