"""
Seed MongoDB with realistic PulsePrice Grocery dashboard data.
Run: python -m database.seed_dashboard
"""
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "pulseprice_admin")

IST = timezone(timedelta(hours=5, minutes=30))
NOW = datetime.now(IST)


def get_db():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000)
    client.admin.command("ping")
    print("[OK] Connected to MongoDB Atlas!")
    return client[DB_NAME]


# ──────────────────────────────────────────────
# 1. PRODUCTS  (Grocery only)
# ──────────────────────────────────────────────
def seed_products(db):
    coll = db["products"]
    coll.drop()
    products = [
        {"sku": "GRO_0101", "name": "Organic Whole Milk 1 gal",    "category": "Dairy",           "base_price": 5.49, "current_price": 5.99, "cost": 3.20, "margin_pct": 47, "stock": 340, "status": "active"},
        {"sku": "GRO_0202", "name": "Sourdough Bread Loaf",        "category": "Bakery",          "base_price": 6.99, "current_price": 7.49, "cost": 3.50, "margin_pct": 53, "stock": 85,  "status": "active"},
        {"sku": "GRO_0303", "name": "Hass Avocados (bag of 6)",    "category": "Produce",         "base_price": 5.99, "current_price": 6.99, "cost": 3.60, "margin_pct": 48, "stock": 120, "status": "active"},
        {"sku": "GRO_0404", "name": "Free-Range Eggs (dozen)",     "category": "Dairy",           "base_price": 6.49, "current_price": 6.99, "cost": 3.80, "margin_pct": 46, "stock": 210, "status": "active"},
        {"sku": "GRO_0505", "name": "Atlantic Salmon Fillet 1 lb", "category": "Meat & Seafood",  "base_price": 12.99,"current_price": 14.49,"cost": 8.50, "margin_pct": 41, "stock": 45,  "status": "active"},
        {"sku": "GRO_0606", "name": "Oat Milk Vanilla 64 oz",      "category": "Beverages",       "base_price": 4.99, "current_price": 4.49, "cost": 2.40, "margin_pct": 47, "stock": 280, "status": "active"},
        {"sku": "GRO_0707", "name": "Jasmine Rice 5 lb bag",       "category": "Staples",         "base_price": 8.49, "current_price": 8.99, "cost": 4.80, "margin_pct": 47, "stock": 190, "status": "active"},
        {"sku": "GRO_0808", "name": "Greek Yogurt Tub 32 oz",      "category": "Dairy",           "base_price": 6.99, "current_price": 6.99, "cost": 3.90, "margin_pct": 44, "stock": 0,   "status": "out_of_stock"},
        {"sku": "GRO_0909", "name": "Baby Spinach 10 oz",          "category": "Produce",         "base_price": 4.29, "current_price": 3.79, "cost": 2.10, "margin_pct": 45, "stock": 95,  "status": "active"},
        {"sku": "GRO_1010", "name": "Artisan Granola 16 oz",       "category": "Snacks",          "base_price": 7.99, "current_price": 8.49, "cost": 4.20, "margin_pct": 50, "stock": 165, "status": "active"},
        {"sku": "GRO_1111", "name": "Frozen Veggie Mix 1 lb",      "category": "Frozen",          "base_price": 3.99, "current_price": 3.49, "cost": 1.80, "margin_pct": 48, "stock": 310, "status": "active"},
        {"sku": "GRO_1212", "name": "Cheddar Cheese Block 8 oz",   "category": "Dairy",           "base_price": 4.99, "current_price": 5.29, "cost": 2.70, "margin_pct": 49, "stock": 0,   "status": "paused"},
    ]
    for p in products:
        p["created_at"] = NOW - timedelta(days=random.randint(10, 90))
        p["updated_at"] = NOW
    coll.insert_many(products)
    print(f"   [+] Inserted {len(products)} grocery products")
    return products


# ──────────────────────────────────────────────
# 2. KPI METRICS
# ──────────────────────────────────────────────
def seed_kpi(db):
    coll = db["kpi_metrics"]
    coll.drop()
    doc = {
        "date": NOW.strftime("%Y-%m-%d"),
        "total_revenue_today": 18420,
        "revenue_change_pct": 9.7,
        "active_sessions": 1243,
        "sessions_change_pct": 6.4,
        "prices_updated": 8740,
        "avg_order_value": 42.30,
        "aov_change_pct": -1.8,
        "updated_at": NOW,
    }
    coll.insert_one(doc)
    print("   [+] Inserted KPI metrics")


# ──────────────────────────────────────────────
# 3. REVENUE DAILY (for chart)
# ──────────────────────────────────────────────
def seed_revenue(db):
    coll = db["revenue_daily"]
    coll.drop()
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    values = [4200, 6800, 8100, 9400, 12600, 15100, 18420]
    docs = []
    for i, (day, val) in enumerate(zip(days, values)):
        docs.append({
            "day": day,
            "date": (NOW - timedelta(days=6 - i)).strftime("%Y-%m-%d"),
            "revenue": val,
        })
    coll.insert_many(docs)
    print(f"   [+] Inserted {len(docs)} revenue days")


# ──────────────────────────────────────────────
# 4. PRICE CHANGES  (Grocery)
# ──────────────────────────────────────────────
def seed_price_changes(db):
    coll = db["price_changes"]
    coll.drop()
    changes = [
        {"product": "Hass Avocados (bag of 6)",    "category": "Produce",        "old_price": 5.99, "new_price": 6.99, "reason": "High Demand",        "status": "increased",  "minutes_ago": 2},
        {"product": "Oat Milk Vanilla 64 oz",      "category": "Beverages",      "old_price": 4.99, "new_price": 4.49, "reason": "Flash Sale",         "status": "decreased",  "minutes_ago": 5},
        {"product": "Greek Yogurt Tub 32 oz",      "category": "Dairy",          "old_price": 6.99, "new_price": 6.99, "reason": "Stable",             "status": "stable",     "minutes_ago": 8},
        {"product": "Atlantic Salmon Fillet 1 lb", "category": "Meat & Seafood", "old_price": 12.99,"new_price": 14.49,"reason": "Limited Stock",      "status": "increased",  "minutes_ago": 14},
        {"product": "Frozen Veggie Mix 1 lb",      "category": "Frozen",         "old_price": 3.99, "new_price": 3.49, "reason": "Personalized Offer", "status": "decreased",  "minutes_ago": 20},
        {"product": "Organic Whole Milk 1 gal",    "category": "Dairy",          "old_price": 5.49, "new_price": 5.99, "reason": "Supplier Cost Rise", "status": "increased",  "minutes_ago": 28},
    ]
    for c in changes:
        c["timestamp"] = NOW - timedelta(minutes=c["minutes_ago"])
    coll.insert_many(changes)
    print(f"   [+] Inserted {len(changes)} price changes")


# ──────────────────────────────────────────────
# 5. PRICE ADJUSTMENT REASONS (donut)
# ──────────────────────────────────────────────
def seed_adjustment_reasons(db):
    coll = db["adjustment_reasons"]
    coll.drop()
    coll.insert_many([
        {"reason": "Seasonal Demand",    "percentage": 35, "count": 3059},
        {"reason": "Supplier Cost Rise", "percentage": 27, "count": 2360},
        {"reason": "Perishable Markdown", "percentage": 22, "count": 1923},
        {"reason": "Promo / Flash Sale", "percentage": 16, "count": 1398},
    ])
    print("   [+] Inserted adjustment reasons")


# ──────────────────────────────────────────────
# 6. USER SEGMENTS
# ──────────────────────────────────────────────
def seed_user_segments(db):
    coll = db["user_segments"]
    coll.drop()
    segments = [
        {"name": "Premium Shoppers",  "count": 2810, "wtp_avg": 0.84, "avg_aov": 68, "conversion": 7.9, "color": "gold",    "progress": 32},
        {"name": "Budget Buyers",     "count": 7640, "wtp_avg": 0.35, "avg_aov": 24, "conversion": 3.4, "color": "violet",  "progress": 55},
        {"name": "Weekly Regulars",   "count": 8120, "wtp_avg": 0.61, "avg_aov": 47, "conversion": 5.8, "color": "emerald", "progress": 58},
        {"name": "New / Unknown",     "count": 2900, "wtp_avg": None, "avg_aov": None,"conversion": None,"color": "warning", "progress": 21},
    ]
    coll.insert_many(segments)
    print(f"   [+] Inserted {len(segments)} user segments")


# ──────────────────────────────────────────────
# 7. USER SESSIONS  (Grocery categories)
# ──────────────────────────────────────────────
def seed_user_sessions(db):
    coll = db["user_sessions"]
    coll.drop()
    sessions = [
        {"user_id": "usr_***44", "segment": "Premium Shoppers",  "engagement": 0.91, "categories": "Dairy, Produce",         "wtp_score": 0.88, "last_active": "18:41"},
        {"user_id": "usr_***12", "segment": "Budget Buyers",     "engagement": 0.52, "categories": "Staples, Frozen",        "wtp_score": 0.29, "last_active": "18:39"},
        {"user_id": "usr_***98", "segment": "Weekly Regulars",   "engagement": 0.76, "categories": "Bakery, Beverages",      "wtp_score": 0.58, "last_active": "18:37"},
        {"user_id": "usr_***37", "segment": "New / Unknown",     "engagement": 0.33, "categories": "Snacks",                 "wtp_score": None, "last_active": "18:35"},
        {"user_id": "usr_***20", "segment": "Weekly Regulars",   "engagement": 0.71, "categories": "Produce, Meat & Seafood","wtp_score": 0.62, "last_active": "18:33"},
        {"user_id": "usr_***73", "segment": "Budget Buyers",     "engagement": 0.48, "categories": "Dairy, Staples",         "wtp_score": 0.27, "last_active": "18:31"},
    ]
    coll.insert_many(sessions)
    print(f"   [+] Inserted {len(sessions)} user sessions")


# ──────────────────────────────────────────────
# 8. A/B EXPERIMENTS  (Grocery context)
# ──────────────────────────────────────────────
def seed_ab_experiments(db):
    coll = db["ab_experiments"]
    coll.drop()
    experiments = [
        {
            "experiment_id": "exp_price_021", "type": "Produce Pricing",
            "variant_a": {"name": "Fixed Markup", "conversion": 4.8, "aov": 38.12, "revenue_session": 1.83, "sample": 18240},
            "variant_b": {"name": "Dynamic Demand V2", "conversion": 5.6, "aov": 44.90, "revenue_session": 2.51, "sample": 18011},
            "split": "50 / 50", "status": "running", "start_date": "2026-04-02", "days_running": 8,
            "confidence": 95, "winner": "B",
        },
        {
            "experiment_id": "exp_rec_008", "type": "Basket Builder",
            "variant_a": {"name": "Aisle Affinity", "conversion": 3.2, "aov": 32.40, "revenue_session": 1.04, "sample": 9200},
            "variant_b": {"name": "Meal-Kit Bundler", "conversion": 3.8, "aov": 41.10, "revenue_session": 1.56, "sample": 9100},
            "split": "60 / 40", "status": "paused", "start_date": "2026-03-28", "days_running": 13,
            "confidence": 78, "winner": None,
        },
    ]
    coll.insert_many(experiments)
    print(f"   [+] Inserted {len(experiments)} A/B experiments")


# ──────────────────────────────────────────────
# 9. AB EVENT LOG  (Grocery products)
# ──────────────────────────────────────────────
def seed_ab_events(db):
    coll = db["ab_event_log"]
    coll.drop()
    events = [
        {"timestamp": "18:41:11", "user_id": "usr_2847", "variant": "B", "event": "impression", "product": "Hass Avocados (bag of 6)",    "revenue": None},
        {"timestamp": "18:41:18", "user_id": "usr_1103", "variant": "B", "event": "click",      "product": "Organic Whole Milk 1 gal",    "revenue": None},
        {"timestamp": "18:41:32", "user_id": "usr_6241", "variant": "A", "event": "purchase",   "product": "Sourdough Bread Loaf",         "revenue": 7.49},
        {"timestamp": "18:41:48", "user_id": "usr_9011", "variant": "B", "event": "purchase",   "product": "Baby Spinach 10 oz",           "revenue": 3.79},
        {"timestamp": "18:42:04", "user_id": "usr_3380", "variant": "A", "event": "impression", "product": "Atlantic Salmon Fillet 1 lb",  "revenue": None},
        {"timestamp": "18:42:17", "user_id": "usr_6612", "variant": "B", "event": "click",      "product": "Artisan Granola 16 oz",        "revenue": None},
        {"timestamp": "18:42:39", "user_id": "usr_4502", "variant": "B", "event": "purchase",   "product": "Jasmine Rice 5 lb bag",        "revenue": 8.99},
        {"timestamp": "18:42:52", "user_id": "usr_1408", "variant": "A", "event": "purchase",   "product": "Frozen Veggie Mix 1 lb",       "revenue": 3.49},
    ]
    coll.insert_many(events)
    print(f"   [+] Inserted {len(events)} A/B events")


# ──────────────────────────────────────────────
# 10. PIPELINE STATUS
# ──────────────────────────────────────────────
def seed_pipeline(db):
    coll = db["pipeline_status"]
    coll.drop()
    services = [
        {"name": "Kafka", "label": "Stream Broker", "status": "healthy", "metrics": {"messages_sec": 4820, "topics": 2, "consumer_lag": "12ms", "partitions": 6}},
        {"name": "Apache Flink", "label": "Stream Processing", "status": "healthy", "metrics": {"jobs_running": 2, "throughput": "3,104 events / sec", "checkpointing": "Enabled", "uptime": "14h 32m"}},
        {"name": "MongoDB Atlas", "label": "Primary Store", "status": "healthy", "metrics": {"connections": 48, "avg_query": "8ms", "storage_used": "2.4 GB", "collections": 14}},
    ]
    coll.insert_many(services)
    print(f"   [+] Inserted {len(services)} pipeline services")


# ──────────────────────────────────────────────
# 11. THROUGHPUT (chart data)
# ──────────────────────────────────────────────
def seed_throughput(db):
    coll = db["throughput_history"]
    coll.drop()
    labels = ["-55m", "-50m", "-45m", "-40m", "-35m", "-30m", "-25m", "-20m", "-15m", "-10m", "-5m", "now"]
    values = [2100, 2800, 2500, 3200, 3700, 3100, 3300, 3900, 3500, 3800, 4100, 4820]
    docs = [{"label": l, "value": v, "timestamp": NOW - timedelta(minutes=55 - i * 5)} for i, (l, v) in enumerate(zip(labels, values))]
    coll.insert_many(docs)
    print(f"   [+] Inserted {len(docs)} throughput points")


# ──────────────────────────────────────────────
# 12. FAIRNESS AUDIT
# ──────────────────────────────────────────────
def seed_fairness(db):
    coll = db["fairness_audit"]
    coll.drop()
    doc = {
        "date": NOW.strftime("%Y-%m-%d"),
        "checks": [
            {"name": "Protected Attribute Check", "result": "PASSED", "status": "healthy", "detail": "No race, gender, age, or religion attributes detected in model inputs."},
            {"name": "Price Floor Compliance", "result": "PASSED", "status": "healthy", "detail": "All 5,000 grocery items are priced above cost x 1.10. Zero violations."},
            {"name": "Reason String Coverage", "result": "PARTIAL", "status": "review", "detail": "97.4% of price responses include a reason string. 62 responses missing reason field."},
        ],
        "disparity": [
            {"segment": "Premium Shoppers", "avg_price": 9.80},
            {"segment": "Weekly Regulars",  "avg_price": 6.70},
            {"segment": "Budget Buyers",    "avg_price": 4.20},
            {"segment": "New Customers",    "avg_price": 5.10},
        ],
        "features_used": ["demand_velocity", "inventory_ratio", "competitor_price", "basket_affinity", "hour_of_day"],
        "features_blocked": ["user_age", "user_gender", "user_zipcode"],
    }
    coll.insert_one(doc)
    print("   [+] Inserted fairness audit")


# ──────────────────────────────────────────────
# 13. RECOMMENDATION STATS (Grocery categories)
# ──────────────────────────────────────────────
def seed_recommendations(db):
    coll = db["recommendation_stats"]
    coll.drop()
    doc = {
        "date": NOW.strftime("%Y-%m-%d"),
        "ctr": 28.6,
        "avg_recs_per_session": 6.2,
        "cold_start_rate": 14.3,
        "model_accuracy": 79.4,
        "top_categories": [
            {"name": "Dairy",          "count": 4920},
            {"name": "Produce",        "count": 4110},
            {"name": "Bakery",         "count": 3660},
            {"name": "Staples",        "count": 2980},
            {"name": "Meat & Seafood", "count": 2340},
        ],
        "session_model": [
            {"user_id": "usr_***44", "session": "08m 12s", "viewed": 17, "shown": 10, "clicked": 4, "converted": True},
            {"user_id": "usr_***12", "session": "05m 45s", "viewed": 11, "shown": 8,  "clicked": 2, "converted": True},
            {"user_id": "usr_***98", "session": "10m 04s", "viewed": 26, "shown": 12, "clicked": 6, "converted": True},
            {"user_id": "usr_***37", "session": "03m 11s", "viewed": 7,  "shown": 6,  "clicked": 1, "converted": False},
            {"user_id": "usr_***20", "session": "09m 28s", "viewed": 19, "shown": 10, "clicked": 5, "converted": True},
        ],
        "cold_start_signals": {
            "enabled": ["Device Type", "Time of Day", "Referral Source"],
            "disabled": ["Geo Region"],
        },
    }
    coll.insert_one(doc)
    print("   [+] Inserted recommendation stats")


# ──────────────────────────────────────────────
# 14. PRICING ENGINE (Grocery top movers)
# ──────────────────────────────────────────────
def seed_pricing_engine(db):
    coll = db["pricing_engine"]
    coll.drop()
    doc = {
        "model_status": "active",
        "model_type": "Regression + Guardrails",
        "last_trained": "2h ago",
        "accuracy": 87.3,
        "guardrails": {
            "min_price": "cost x 1.10",
            "max_discount": "30%",
            "compliance": "No protected attributes used",
        },
        "demand_signals": {
            "avg_velocity": "142 views/min",
            "inventory_ratio": 0.64,
            "competitor_delta": "-2.3%",
        },
        "top_movers": [
            {"rank": 1, "product": "Hass Avocados (bag of 6)",    "category": "Produce",        "changes": 31, "current": 6.99, "margin": "48%"},
            {"rank": 2, "product": "Atlantic Salmon Fillet 1 lb", "category": "Meat & Seafood", "changes": 28, "current": 14.49,"margin": "41%"},
            {"rank": 3, "product": "Organic Whole Milk 1 gal",    "category": "Dairy",          "changes": 25, "current": 5.99, "margin": "47%"},
            {"rank": 4, "product": "Sourdough Bread Loaf",        "category": "Bakery",         "changes": 22, "current": 7.49, "margin": "53%"},
            {"rank": 5, "product": "Artisan Granola 16 oz",       "category": "Snacks",         "changes": 20, "current": 8.49, "margin": "50%"},
        ],
        "price_distribution": [
            {"range": "$0-$3",  "pct": 18},
            {"range": "$3-$6",  "pct": 34},
            {"range": "$6-$10", "pct": 28},
            {"range": "$10-$15","pct": 14},
            {"range": "$15+",   "pct": 6},
        ],
    }
    coll.insert_one(doc)
    print("   [+] Inserted pricing engine data")


# ──────────────────────────────────────────────
# 15. USER COUNTS (dedicated collection)
# ──────────────────────────────────────────────
def seed_user_counts(db):
    coll = db["user_counts"]
    coll.drop()
    coll.insert_one({
        "date": NOW.strftime("%Y-%m-%d"),
        "total_users": 21470,
        "active_today": 1243,
        "new_this_week": 287,
    })
    print("   [+] Inserted user counts")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    print("\n[*] Connecting to MongoDB Atlas...")
    db = get_db()
    print(f"[*] Database: {DB_NAME}\n")

    seed_products(db)
    seed_kpi(db)
    seed_revenue(db)
    seed_price_changes(db)
    seed_adjustment_reasons(db)
    seed_user_segments(db)
    seed_user_sessions(db)
    seed_ab_experiments(db)
    seed_ab_events(db)
    seed_pipeline(db)
    seed_throughput(db)
    seed_fairness(db)
    seed_recommendations(db)
    seed_pricing_engine(db)
    seed_user_counts(db)

    colls = db.list_collection_names()
    print(f"\n[OK] Done! {len(colls)} collections created: {', '.join(sorted(colls))}")


if __name__ == "__main__":
    main()
