from datetime import UTC, datetime, timedelta


def build_products() -> list[dict]:
    return [
        {"sku": "FRU-101", "name": "Bananas", "category": "fruits", "price": 32, "stock_quantity": 18, "reorder_threshold": 22, "perishable": True, "freshness_days": 2, "margin_pct": 18, "velocity_score": 84},
        {"sku": "VEG-202", "name": "Spinach", "category": "vegetables", "price": 25, "stock_quantity": 9, "reorder_threshold": 15, "perishable": True, "freshness_days": 1, "margin_pct": 16, "velocity_score": 76},
        {"sku": "DAI-303", "name": "Greek Yogurt", "category": "dairy", "price": 58, "stock_quantity": 42, "reorder_threshold": 20, "perishable": True, "freshness_days": 5, "margin_pct": 22, "velocity_score": 61},
        {"sku": "BEV-404", "name": "Orange Juice", "category": "beverages", "price": 89, "stock_quantity": 27, "reorder_threshold": 12, "perishable": True, "freshness_days": 4, "margin_pct": 28, "velocity_score": 57},
        {"sku": "SNA-505", "name": "Granola Bars", "category": "snacks", "price": 120, "stock_quantity": 64, "reorder_threshold": 18, "perishable": False, "freshness_days": 45, "margin_pct": 35, "velocity_score": 48},
        {"sku": "BAK-606", "name": "Multigrain Bread", "category": "bakery", "price": 48, "stock_quantity": 13, "reorder_threshold": 16, "perishable": True, "freshness_days": 2, "margin_pct": 19, "velocity_score": 81},
        {"sku": "HOU-707", "name": "Dish Wash Gel", "category": "household", "price": 149, "stock_quantity": 33, "reorder_threshold": 10, "perishable": False, "freshness_days": 180, "margin_pct": 31, "velocity_score": 37},
        {"sku": "FRZ-808", "name": "Frozen Peas", "category": "frozen", "price": 96, "stock_quantity": 25, "reorder_threshold": 14, "perishable": True, "freshness_days": 60, "margin_pct": 26, "velocity_score": 52},
    ]


def build_users() -> list[dict]:
    return [
        {"user_id": "USR-1001", "name": "Aarav Shah", "segment": "family_bulk", "city": "Ahmedabad", "average_basket_value": 842, "order_frequency": 12, "lifetime_value": 14500, "last_seen_days": 1, "intent_score": 92},
        {"user_id": "USR-1002", "name": "Diya Patel", "segment": "healthy_regular", "city": "Vadodara", "average_basket_value": 534, "order_frequency": 9, "lifetime_value": 9300, "last_seen_days": 2, "intent_score": 81},
        {"user_id": "USR-1003", "name": "Ishaan Mehta", "segment": "quick_topups", "city": "Surat", "average_basket_value": 316, "order_frequency": 18, "lifetime_value": 7720, "last_seen_days": 0, "intent_score": 88},
        {"user_id": "USR-1004", "name": "Mira Joshi", "segment": "premium_fresh", "city": "Rajkot", "average_basket_value": 1180, "order_frequency": 6, "lifetime_value": 12420, "last_seen_days": 3, "intent_score": 75},
        {"user_id": "USR-1005", "name": "Kabir Desai", "segment": "dormant_returning", "city": "Ahmedabad", "average_basket_value": 690, "order_frequency": 4, "lifetime_value": 4280, "last_seen_days": 17, "intent_score": 43},
        {"user_id": "USR-1006", "name": "Anaya Trivedi", "segment": "snacking_focused", "city": "Bhavnagar", "average_basket_value": 412, "order_frequency": 11, "lifetime_value": 6890, "last_seen_days": 1, "intent_score": 78},
    ]


def build_orders(products: list[dict], users: list[dict]) -> list[dict]:
    now = datetime.now(UTC)
    sku_map = {product["category"]: product["sku"] for product in products}
    orders = []
    templates = [
        ("pending", 540, ["fruits", "vegetables"], 1),
        ("packed", 920, ["dairy", "bakery"], 2),
        ("out_for_delivery", 1370, ["beverages", "snacks"], 3),
        ("delivered", 760, ["household", "fruits"], 4),
        ("delivered", 1140, ["frozen", "dairy"], 5),
        ("cancelled", 0, ["vegetables"], 6),
        ("delivered", 480, ["bakery", "fruits"], 8),
        ("packed", 1330, ["household", "beverages"], 9),
        ("pending", 690, ["snacks", "fruits"], 10),
        ("out_for_delivery", 870, ["vegetables", "dairy"], 12),
        ("delivered", 1010, ["frozen", "snacks"], 14),
        ("delivered", 1450, ["bakery", "household"], 18),
    ]
    for index, (status, total, categories, hours_ago) in enumerate(templates, start=1):
        orders.append(
            {
                "order_id": f"ORD-{1000 + index}",
                "user_id": users[index % len(users)]["user_id"],
                "status": status,
                "total_amount": total,
                "created_at": (now - timedelta(hours=hours_ago)).isoformat(),
                "items": [{"sku": sku_map[category], "quantity": (index % 4) + 1, "category": category} for category in categories],
            }
        )
    return orders


def build_admin_logs() -> list[dict]:
    now = datetime.now(UTC)
    actions = [
        ("Store Manager", "Adjusted reorder threshold for Spinach", "inventory"),
        ("Store Manager", "Reviewed customer cohort drift", "insights"),
        ("Store Manager", "Approved promo on Orange Juice", "catalog"),
        ("Store Manager", "Resolved low-stock alert for Bread", "alerts"),
        ("Store Manager", "Exported daily revenue snapshot", "analytics"),
    ]
    return [
        {"actor": actor, "action": action, "module": module, "timestamp": (now - timedelta(minutes=index * 37)).isoformat()}
        for index, (actor, action, module) in enumerate(actions, start=1)
    ]
