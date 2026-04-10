from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta

from database.collections import ADMIN_LOGS, ORDERS, PRODUCTS, USERS
from database.connection import get_database
from database.seed_data import build_admin_logs, build_orders, build_products, build_users


RANGE_TO_DAYS = {"7d": 7, "30d": 30, "90d": 90}


def _sample_products() -> list[dict]:
    return build_products()


def _sample_orders() -> list[dict]:
    return build_orders(_sample_products(), _sample_users())


def _sample_users() -> list[dict]:
    return build_users()


def _sample_admin_logs() -> list[dict]:
    return build_admin_logs()


def _load_documents() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    database = get_database()
    if database is None:
        return _sample_products(), _sample_orders(), _sample_users(), _sample_admin_logs()

    products = list(database[PRODUCTS].find({}, {"_id": 0})) or _sample_products()
    orders = list(database[ORDERS].find({}, {"_id": 0})) or _sample_orders()
    users = list(database[USERS].find({}, {"_id": 0})) or _sample_users()
    admin_logs = list(database[ADMIN_LOGS].find({}, {"_id": 0})) or _sample_admin_logs()
    return products, orders, users, admin_logs


def _recent_orders(orders: list[dict], day_count: int) -> list[dict]:
    cutoff = datetime.now(UTC) - timedelta(days=day_count)
    recent = []
    for order in orders:
        created_at = datetime.fromisoformat(order["created_at"].replace("Z", "+00:00"))
        if created_at >= cutoff:
            recent.append(order)
    return recent


def build_alerts(products: list[dict], low_stock: list[dict] | None = None, perishables: list[dict] | None = None) -> list[dict]:
    low_stock = low_stock if low_stock is not None else [product for product in products if product.get("stock_quantity", 0) <= product.get("reorder_threshold", 0)]
    perishables = perishables if perishables is not None else [product for product in products if product.get("perishable") and product.get("freshness_days", 99) <= 3]
    alerts = []
    for product in low_stock[:4]:
        alerts.append({"type": "low_stock", "headline": f"{product['name']} is below reorder level", "detail": f"{product['stock_quantity']} units left against threshold {product['reorder_threshold']}.", "severity": "high"})
    for product in perishables[:3]:
        alerts.append({"type": "perishable", "headline": f"{product['name']} needs freshness attention", "detail": f"Freshness window is {product['freshness_days']} day(s).", "severity": "medium"})
    return alerts


def build_dashboard_payload(range_key: str) -> dict:
    products, orders, users, admin_logs = _load_documents()
    recent_orders = _recent_orders(orders, RANGE_TO_DAYS[range_key])
    active_statuses = {"pending", "packed", "out_for_delivery"}
    category_revenue = defaultdict(float)
    sales_series = defaultdict(lambda: {"revenue": 0.0, "orders": 0})
    order_status_counter = Counter()

    for order in recent_orders:
        created_at = datetime.fromisoformat(order["created_at"].replace("Z", "+00:00"))
        day_key = created_at.strftime("%d %b")
        sales_series[day_key]["revenue"] += float(order.get("total_amount", 0))
        sales_series[day_key]["orders"] += 1
        order_status_counter[order.get("status", "pending")] += 1
        for item in order.get("items", []):
            category_revenue[item.get("category", "other")] += float(order.get("total_amount", 0)) / max(len(order.get("items", [])), 1)

    low_stock = [product for product in products if product.get("stock_quantity", 0) <= product.get("reorder_threshold", 0)]
    perishables = [product for product in products if product.get("perishable") and product.get("freshness_days", 99) <= 3]
    total_revenue = sum(float(order.get("total_amount", 0)) for order in recent_orders if order.get("status") != "cancelled")
    top_categories = sorted(category_revenue.items(), key=lambda item: item[1], reverse=True)[:5]

    return {
        "filters": {"range": range_key, "available_ranges": list(RANGE_TO_DAYS.keys())},
        "kpis": {"today_revenue": round(total_revenue, 2), "active_orders": sum(order_status_counter[status] for status in active_statuses), "low_stock_skus": len(low_stock), "perishable_attention": len(perishables)},
        "charts": {
            "sales_trends": [{"label": label, **values} for label, values in sorted(sales_series.items())],
            "inventory_mix": [{"label": "Healthy stock", "value": max(len(products) - len(low_stock), 0)}, {"label": "Low stock", "value": len(low_stock)}, {"label": "Perishable watch", "value": len(perishables)}],
            "category_performance": [{"label": label.title(), "revenue": round(value, 2)} for label, value in top_categories],
            "inventory_depth_3d": [{"label": product["name"], "stock": product.get("stock_quantity", 0), "threshold": product.get("reorder_threshold", 0), "category": product.get("category", "other")} for product in products[:6]],
        },
        "alerts": build_alerts(products, low_stock, perishables),
        "sections": {
            "catalog": {"product_count": len(products), "top_category": top_categories[0][0].title() if top_categories else "Fruits"},
            "inventory": {"at_risk_products": len(low_stock), "perishable_watch": len(perishables)},
            "orders": {"status_breakdown": dict(order_status_counter)},
            "users": {"active_high_intent": len([user for user in users if user.get("intent_score", 0) >= 75]), "loyal_segments": len({user.get("segment") for user in users})},
            "admin": {"recent_actions": len(admin_logs)},
        },
        "updated_at": datetime.now(UTC).isoformat(),
    }


def build_operations_payload(range_key: str) -> dict:
    products, orders, _, _ = _load_documents()
    recent_orders = _recent_orders(orders, RANGE_TO_DAYS[range_key])
    highest_velocity = sorted(products, key=lambda item: item.get("velocity_score", 0), reverse=True)[:5]
    inventory_watch = sorted(products, key=lambda item: item.get("stock_quantity", 0) - item.get("reorder_threshold", 0))[:6]
    return {
        "filters": {"range": range_key},
        "inventory_watch": inventory_watch,
        "top_movers": highest_velocity,
        "order_lane": sorted(recent_orders, key=lambda item: item["created_at"], reverse=True)[:8],
        "updated_at": datetime.now(UTC).isoformat(),
    }


def build_user_insights_payload() -> dict:
    _, orders, users, _ = _load_documents()
    total_revenue = sum(order.get("total_amount", 0) for order in orders if order.get("status") != "cancelled")
    avg_basket = round(total_revenue / max(len([order for order in orders if order.get("status") != "cancelled"]), 1), 2)
    repeat_users = [user for user in users if user.get("order_frequency", 0) >= 8]
    high_intent = sorted(users, key=lambda item: item.get("intent_score", 0), reverse=True)[:6]
    scatter = [
        {"label": user["name"], "x": user.get("order_frequency", 0), "y": user.get("average_basket_value", 0), "z": user.get("lifetime_value", 0), "segment": user.get("segment", "general")}
        for user in users
    ]
    return {
        "kpis": {
            "average_basket_value": avg_basket,
            "repeat_customer_rate": round((len(repeat_users) / max(len(users), 1)) * 100, 1),
            "high_intent_users": len([user for user in users if user.get("intent_score", 0) >= 80]),
        },
        "scatter_matrix_3d": scatter,
        "top_customers": high_intent,
        "segment_mix": dict(Counter(user.get("segment", "general") for user in users)),
        "updated_at": datetime.now(UTC).isoformat(),
    }


def build_admin_logs_payload() -> dict:
    _, _, _, admin_logs = _load_documents()
    return {
        "entries": sorted(admin_logs, key=lambda item: item.get("timestamp", ""), reverse=True),
        "updated_at": datetime.now(UTC).isoformat(),
    }
