from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta

from apps.market.mongo_client import get_db


RANGE_TO_DAYS = {"7d": 7, "30d": 30, "90d": 90}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _to_datetime(raw) -> datetime | None:
    """Safely convert a raw date value (datetime or ISO string) to a tz-aware datetime."""
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw if raw.tzinfo else raw.replace(tzinfo=UTC)
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _to_iso(raw) -> str:
    """Convert a raw date value to an ISO string."""
    dt = _to_datetime(raw)
    return dt.isoformat() if dt else ""


def _order_date(order: dict):
    """Return the date field of an order — supports both 'date' and 'created_at' keys."""
    return order.get("date") or order.get("created_at")


# ── Data loader ────────────────────────────────────────────────────────────────

def _load_documents() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    database = get_db()
    if database is None:
        return [], [], [], []

    products   = list(database["products"].find({}, {"_id": 0}))
    orders     = list(database["orders"].find({}, {"_id": 0}))
    users      = list(database["users"].find({}, {"_id": 0}))
    admin_logs = list(database["admin_logs"].find({}, {"_id": 0}))
    return products, orders, users, admin_logs


# ── Filtering ──────────────────────────────────────────────────────────────────

def _recent_orders(orders: list[dict], day_count: int) -> list[dict]:
    cutoff = datetime.now(UTC) - timedelta(days=day_count)
    recent = []
    for order in orders:
        raw = _order_date(order)
        dt  = _to_datetime(raw)
        # If no date at all, still include it so the dashboard isn't empty
        if dt is None or dt >= cutoff:
            recent.append(order)
    return recent


# ── Alerts ─────────────────────────────────────────────────────────────────────

def build_alerts(products: list[dict],
                 low_stock: list[dict] | None = None,
                 perishables: list[dict] | None = None) -> list[dict]:
    if low_stock is None:
        low_stock = [
            p for p in products
            if p.get("stock_quantity", 0) <= p.get("reorder_threshold", 0)
            and p.get("stock_quantity") is not None       # only flag real stock data
        ]
    if perishables is None:
        perishables = [
            p for p in products
            if p.get("perishable") and p.get("freshness_days", 99) <= 3
        ]

    alerts = []
    for product in low_stock[:4]:
        name      = product.get("name", "Unknown product")
        stock     = product.get("stock_quantity", 0)
        threshold = product.get("reorder_threshold", 0)
        alerts.append({
            "type": "low_stock",
            "headline": f"{name} is below reorder level",
            "detail": f"{stock} units left against threshold {threshold}.",
            "severity": "high",
        })
    for product in perishables[:3]:
        name = product.get("name", "Unknown product")
        days = product.get("freshness_days", 0)
        alerts.append({
            "type": "perishable",
            "headline": f"{name} needs freshness attention",
            "detail": f"Freshness window is {days} day(s).",
            "severity": "medium",
        })
    return alerts


# ── Dashboard payload ──────────────────────────────────────────────────────────

def build_dashboard_payload(range_key: str) -> dict:
    products, orders, users, admin_logs = _load_documents()
    recent_orders = _recent_orders(orders, RANGE_TO_DAYS[range_key])

    active_statuses    = {"pending", "packed", "out_for_delivery", "confirmed", "processing"}
    category_revenue   = defaultdict(float)
    sales_series       = defaultdict(lambda: {"revenue": 0.0, "orders": 0})
    order_status_counter = Counter()

    for order in recent_orders:
        raw_dt  = _to_datetime(_order_date(order))
        day_key = raw_dt.strftime("%d %b") if raw_dt else "Today"

        amount = float(order.get("total_amount", 0))
        sales_series[day_key]["revenue"] += amount
        sales_series[day_key]["orders"]  += 1

        # Normalise status to lowercase for counting
        status = (order.get("status") or "pending").lower()
        order_status_counter[status] += 1

        items = order.get("items") or []
        per_item = amount / max(len(items), 1)
        for item in items:
            cat = (item.get("category") or item.get("name") or "other").split()[0].lower()
            category_revenue[cat] += per_item

    # Product-level stats (defensive — products may lack stock fields)
    low_stock   = [p for p in products
                   if p.get("stock_quantity") is not None
                   and p.get("stock_quantity", 0) <= p.get("reorder_threshold", 0)]
    perishables = [p for p in products
                   if p.get("perishable") and p.get("freshness_days", 99) <= 3]

    total_revenue = sum(
        float(o.get("total_amount", 0))
        for o in recent_orders
        if (o.get("status") or "").lower() != "cancelled"
    )
    top_categories = sorted(category_revenue.items(), key=lambda x: x[1], reverse=True)[:5]

    # Build a complete status map — include ALL statuses with 0 so charts always show them
    ALL_STATUSES = ["pending", "confirmed", "packed", "delivered", "cancelled"]
    full_status: dict[str, int] = {s: 0 for s in ALL_STATUSES}
    for s, count in order_status_counter.items():
        key = s.lower()
        full_status[key] = full_status.get(key, 0) + count

    # New users today
    from datetime import date as _date
    today_str = _date.today().isoformat()
    new_users_today = sum(
        1 for u in users
        if str(_to_iso(u.get("created_at") or u.get("date_joined") or "")).startswith(today_str)
    )

    return {
        "filters":  {"range": range_key, "available_ranges": list(RANGE_TO_DAYS.keys())},
        "kpis": {
            "today_revenue":        round(total_revenue, 2),
            "active_orders":        sum(order_status_counter[s] for s in active_statuses),
            "low_stock_skus":       len(low_stock),
            "perishable_attention": len(perishables),
            "total_orders":         len(recent_orders),
            "total_products":       len(products),
            "total_users":          len(users),
            "new_users_today":      new_users_today,
        },
        "charts": {
            "sales_trends": [
                {"label": label, **values}
                for label, values in sorted(sales_series.items())
            ],
            "inventory_mix": [
                {"label": "Healthy stock",    "value": max(len(products) - len(low_stock), 0)},
                {"label": "Low stock",        "value": len(low_stock)},
                {"label": "Perishable watch", "value": len(perishables)},
            ],
            "category_performance": [
                {"label": label.title(), "revenue": round(value, 2)}
                for label, value in top_categories
            ],
            "inventory_depth_3d": [
                {
                    "label":     p.get("name", ""),
                    "stock":     p.get("stock_quantity", 0),
                    "threshold": p.get("reorder_threshold", 0),
                    "category":  p.get("category", "other"),
                }
                for p in products[:6]
            ],
            "order_status": [
                {"label": status.replace("_", " ").title(), "value": count}
                for status, count in full_status.items()
            ],
        },
        "alerts": build_alerts(products, low_stock, perishables),
        "sections": {
            "catalog":   {"product_count": len(products),
                          "top_category": top_categories[0][0].title() if top_categories else "—"},
            "inventory": {"at_risk_products": len(low_stock), "perishable_watch": len(perishables)},
            "orders":    {"status_breakdown": dict(order_status_counter), "total": len(recent_orders)},
            "users":     {"total": len(users)},
            "admin":     {"recent_actions": len(admin_logs)},
        },
        "updated_at": datetime.now(UTC).isoformat(),
    }


# ── Operations payload ─────────────────────────────────────────────────────────

def build_operations_payload(range_key: str) -> dict:
    products, orders, _, _ = _load_documents()
    recent_orders   = _recent_orders(orders, RANGE_TO_DAYS[range_key])
    highest_velocity = sorted(products, key=lambda p: p.get("velocity_score", 0), reverse=True)[:5]
    inventory_watch  = sorted(
        products,
        key=lambda p: p.get("stock_quantity", 0) - p.get("reorder_threshold", 0)
    )[:6]
    return {
        "filters":        {"range": range_key},
        "inventory_watch": inventory_watch,
        "top_movers":      highest_velocity,
        "order_lane":      sorted(
            recent_orders,
            key=lambda o: _to_iso(_order_date(o)),
            reverse=True
        )[:8],
        "updated_at": datetime.now(UTC).isoformat(),
    }


# ── User insights payload ──────────────────────────────────────────────────────

def build_user_insights_payload() -> dict:
    _, orders, users, _ = _load_documents()
    non_cancelled = [o for o in orders if (o.get("status") or "").lower() != "cancelled"]
    total_revenue = sum(o.get("total_amount", 0) for o in non_cancelled)
    avg_basket    = round(total_revenue / max(len(non_cancelled), 1), 2)
    repeat_users  = [u for u in users if u.get("order_frequency", 0) >= 8]
    high_intent   = sorted(users, key=lambda u: u.get("intent_score", 0), reverse=True)[:6]
    scatter = [
        {
            "label":   u.get("name", "User"),
            "x":       u.get("order_frequency", 0),
            "y":       u.get("average_basket_value", 0),
            "z":       u.get("lifetime_value", 0),
            "segment": u.get("segment", "general"),
        }
        for u in users
    ]
    return {
        "kpis": {
            "average_basket_value": avg_basket,
            "repeat_customer_rate": round((len(repeat_users) / max(len(users), 1)) * 100, 1),
            "high_intent_users":    len([u for u in users if u.get("intent_score", 0) >= 80]),
        },
        "scatter_matrix_3d": scatter,
        "top_customers":     high_intent,
        "segment_mix":       dict(Counter(u.get("segment", "general") for u in users)),
        "updated_at":        datetime.now(UTC).isoformat(),
    }


# ── Admin logs payload ─────────────────────────────────────────────────────────

def build_admin_logs_payload() -> dict:
    _, _, _, admin_logs = _load_documents()
    return {
        "entries":    sorted(admin_logs, key=lambda x: x.get("timestamp", ""), reverse=True),
        "updated_at": datetime.now(UTC).isoformat(),
    }
