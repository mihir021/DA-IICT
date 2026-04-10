"""
Seed MongoDB with realistic PulsePrice dashboard data.
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
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("✅ Connected to MongoDB Atlas!")
    return client[DB_NAME]


# ──────────────────────────────────────────────
# 1. PRODUCTS
# ──────────────────────────────────────────────
def seed_products(db):
    coll = db["products"]
    coll.drop()
    products = [
        {"sku": "SKU_0442", "name": "Pulse Max Headphones", "category": "Electronics", "base_price": 129, "current_price": 139, "cost": 92, "margin_pct": 34, "stock": 114, "status": "active"},
        {"sku": "SKU_1892", "name": "CoreRun Jacket", "category": "Clothing", "base_price": 110, "current_price": 98, "cost": 77, "margin_pct": 21, "stock": 34, "status": "active"},
        {"sku": "SKU_0028", "name": "TrailFlex Bottle", "category": "Sports", "base_price": 24, "current_price": 22, "cost": 18, "margin_pct": 18, "stock": 88, "status": "active"},
        {"sku": "SKU_0877", "name": "ZenDesk Lamp", "category": "Home", "base_price": 52, "current_price": 59, "cost": 43, "margin_pct": 27, "stock": 19, "status": "active"},
        {"sku": "SKU_0904", "name": "Nova Skin Serum", "category": "Beauty", "base_price": 38, "current_price": 38, "cost": 31, "margin_pct": 12, "stock": 8, "status": "paused"},
        {"sku": "SKU_1430", "name": "Prime Knit Tee", "category": "Clothing", "base_price": 35, "current_price": 35, "cost": 24, "margin_pct": 31, "stock": 203, "status": "active"},
        {"sku": "SKU_2110", "name": "Atlas Smartwatch", "category": "Electronics", "base_price": 199, "current_price": 214, "cost": 141, "margin_pct": 34, "stock": 27, "status": "active"},
        {"sku": "SKU_3018", "name": "HomeAura Diffuser", "category": "Home", "base_price": 48, "current_price": 48, "cost": 42, "margin_pct": 13, "stock": 0, "status": "out_of_stock"},
        {"sku": "SKU_4001", "name": "AeroFit Sneakers", "category": "Sports", "base_price": 84, "current_price": 76, "cost": 55, "margin_pct": 28, "stock": 62, "status": "active"},
        {"sku": "SKU_4555", "name": "GlowRing LED", "category": "Electronics", "base_price": 29, "current_price": 32, "cost": 20, "margin_pct": 38, "stock": 310, "status": "active"},
    ]
    for p in products:
        p["created_at"] = NOW - timedelta(days=random.randint(10, 90))
        p["updated_at"] = NOW
    coll.insert_many(products)
    print(f"   📦 Inserted {len(products)} products")
    return products


# ──────────────────────────────────────────────
# 2. KPI METRICS
# ──────────────────────────────────────────────
def seed_kpi(db):
    coll = db["kpi_metrics"]
    coll.drop()
    doc = {
        "date": NOW.strftime("%Y-%m-%d"),
        "total_revenue_today": 48320,
        "revenue_change_pct": 12.4,
        "active_sessions": 1847,
        "sessions_change_pct": 8.1,
        "prices_updated": 23540,
        "avg_order_value": 67.40,
        "aov_change_pct": -3.2,
        "updated_at": NOW,
    }
    coll.insert_one(doc)
    print("   📊 Inserted KPI metrics")


# ──────────────────────────────────────────────
# 3. REVENUE DAILY (for chart)
# ──────────────────────────────────────────────
def seed_revenue(db):
    coll = db["revenue_daily"]
    coll.drop()
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    values = [8200, 14800, 22100, 28400, 35600, 42100, 48320]
    docs = []
    for i, (day, val) in enumerate(zip(days, values)):
        docs.append({
            "day": day,
            "date": (NOW - timedelta(days=6 - i)).strftime("%Y-%m-%d"),
            "revenue": val,
        })
    coll.insert_many(docs)
    print(f"   📈 Inserted {len(docs)} revenue days")


# ──────────────────────────────────────────────
# 4. PRICE CHANGES
# ──────────────────────────────────────────────
def seed_price_changes(db):
    coll = db["price_changes"]
    coll.drop()
    changes = [
        {"product": "Pulse Max Headphones", "category": "Electronics", "old_price": 129, "new_price": 139, "reason": "High Demand", "status": "increased", "minutes_ago": 2},
        {"product": "AeroFit Sneakers", "category": "Sports", "old_price": 84, "new_price": 76, "reason": "Flash Sale", "status": "decreased", "minutes_ago": 4},
        {"product": "Nova Skin Serum", "category": "Beauty", "old_price": 38, "new_price": 38, "reason": "Stable", "status": "stable", "minutes_ago": 7},
        {"product": "ZenDesk Lamp", "category": "Home", "old_price": 52, "new_price": 59, "reason": "Limited Stock", "status": "increased", "minutes_ago": 12},
        {"product": "CoreRun Jacket", "category": "Clothing", "old_price": 110, "new_price": 98, "reason": "Personalized Offer", "status": "decreased", "minutes_ago": 18},
        {"product": "Atlas Smartwatch", "category": "Electronics", "old_price": 199, "new_price": 214, "reason": "High Demand", "status": "increased", "minutes_ago": 26},
    ]
    for c in changes:
        c["timestamp"] = NOW - timedelta(minutes=c["minutes_ago"])
    coll.insert_many(changes)
    print(f"   💰 Inserted {len(changes)} price changes")


# ──────────────────────────────────────────────
# 5. PRICE ADJUSTMENT REASONS (donut)
# ──────────────────────────────────────────────
def seed_adjustment_reasons(db):
    coll = db["adjustment_reasons"]
    coll.drop()
    coll.insert_many([
        {"reason": "High Demand", "percentage": 42, "count": 9887},
        {"reason": "Limited Stock", "percentage": 28, "count": 6591},
        {"reason": "Personalized", "percentage": 18, "count": 4237},
        {"reason": "Flash Sale", "percentage": 12, "count": 2825},
    ])
    print("   🍩 Inserted adjustment reasons")


# ──────────────────────────────────────────────
# 6. USER SEGMENTS
# ──────────────────────────────────────────────
def seed_user_segments(db):
    coll = db["user_segments"]
    coll.drop()
    segments = [
        {"name": "High Spenders", "count": 3214, "wtp_avg": 0.84, "avg_aov": 124, "conversion": 8.2, "color": "gold", "progress": 36},
        {"name": "Bargain Hunters", "count": 8902, "wtp_avg": 0.31, "avg_aov": 34, "conversion": 3.1, "color": "violet", "progress": 52},
        {"name": "Regular Shoppers", "count": 9441, "wtp_avg": 0.57, "avg_aov": 67, "conversion": 5.4, "color": "emerald", "progress": 61},
        {"name": "New / Unknown", "count": 3314, "wtp_avg": None, "avg_aov": None, "conversion": None, "color": "warning", "progress": 24},
    ]
    coll.insert_many(segments)
    print(f"   👥 Inserted {len(segments)} user segments")


# ──────────────────────────────────────────────
# 7. USER SESSIONS
# ──────────────────────────────────────────────
def seed_user_sessions(db):
    coll = db["user_sessions"]
    coll.drop()
    sessions = [
        {"user_id": "usr_***44", "segment": "High Spenders", "engagement": 0.91, "categories": "Electronics, Home", "wtp_score": 0.88, "last_active": "18:41"},
        {"user_id": "usr_***12", "segment": "Bargain Hunters", "engagement": 0.52, "categories": "Sports, Clothing", "wtp_score": 0.29, "last_active": "18:39"},
        {"user_id": "usr_***98", "segment": "Regular Shoppers", "engagement": 0.76, "categories": "Beauty, Home", "wtp_score": 0.58, "last_active": "18:37"},
        {"user_id": "usr_***37", "segment": "New / Unknown", "engagement": 0.33, "categories": "Books", "wtp_score": None, "last_active": "18:35"},
        {"user_id": "usr_***20", "segment": "Regular Shoppers", "engagement": 0.71, "categories": "Electronics, Sports", "wtp_score": 0.62, "last_active": "18:33"},
        {"user_id": "usr_***73", "segment": "Bargain Hunters", "engagement": 0.48, "categories": "Clothing, Beauty", "wtp_score": 0.27, "last_active": "18:31"},
    ]
    coll.insert_many(sessions)
    print(f"   🔗 Inserted {len(sessions)} user sessions")


# ──────────────────────────────────────────────
# 8. A/B EXPERIMENTS
# ──────────────────────────────────────────────
def seed_ab_experiments(db):
    coll = db["ab_experiments"]
    coll.drop()
    experiments = [
        {
            "experiment_id": "exp_price_021", "type": "Pricing Strategy",
            "variant_a": {"name": "Rule Baseline", "conversion": 4.8, "aov": 64.12, "revenue_session": 3.08, "sample": 18240},
            "variant_b": {"name": "Elastic Guardrail V2", "conversion": 5.6, "aov": 68.90, "revenue_session": 3.86, "sample": 18011},
            "split": "50 / 50", "status": "running", "start_date": "2026-04-02", "days_running": 8,
            "confidence": 95, "winner": "B",
        },
        {
            "experiment_id": "exp_rec_008", "type": "Rec Model",
            "variant_a": {"name": "Hybrid CF", "conversion": 3.2, "aov": 52.40, "revenue_session": 1.68, "sample": 9200},
            "variant_b": {"name": "Session Boosted", "conversion": 3.8, "aov": 55.10, "revenue_session": 2.09, "sample": 9100},
            "split": "60 / 40", "status": "paused", "start_date": "2026-03-28", "days_running": 13,
            "confidence": 78, "winner": None,
        },
    ]
    coll.insert_many(experiments)
    print(f"   🧪 Inserted {len(experiments)} A/B experiments")


# ──────────────────────────────────────────────
# 9. AB EVENT LOG
# ──────────────────────────────────────────────
def seed_ab_events(db):
    coll = db["ab_event_log"]
    coll.drop()
    events = [
        {"timestamp": "18:41:11", "user_id": "usr_2847", "variant": "B", "event": "impression", "product": "Atlas Smartwatch", "revenue": None},
        {"timestamp": "18:41:18", "user_id": "usr_1103", "variant": "B", "event": "click", "product": "Pulse Max Headphones", "revenue": None},
        {"timestamp": "18:41:32", "user_id": "usr_6241", "variant": "A", "event": "purchase", "product": "CoreRun Jacket", "revenue": 98},
        {"timestamp": "18:41:48", "user_id": "usr_9011", "variant": "B", "event": "purchase", "product": "Nova Skin Serum", "revenue": 38},
        {"timestamp": "18:42:04", "user_id": "usr_3380", "variant": "A", "event": "impression", "product": "ZenDesk Lamp", "revenue": None},
        {"timestamp": "18:42:17", "user_id": "usr_6612", "variant": "B", "event": "click", "product": "TrailFlex Bottle", "revenue": None},
        {"timestamp": "18:42:39", "user_id": "usr_4502", "variant": "B", "event": "purchase", "product": "Prime Knit Tee", "revenue": 35},
        {"timestamp": "18:42:52", "user_id": "usr_1408", "variant": "A", "event": "purchase", "product": "HomeAura Diffuser", "revenue": 48},
    ]
    coll.insert_many(events)
    print(f"   📝 Inserted {len(events)} A/B events")


# ──────────────────────────────────────────────
# 10. PIPELINE STATUS
# ──────────────────────────────────────────────
def seed_pipeline(db):
    coll = db["pipeline_status"]
    coll.drop()
    services = [
        {"name": "Kafka", "label": "Stream Broker", "status": "healthy", "metrics": {"messages_sec": 4820, "topics": 2, "consumer_lag": "12ms", "partitions": 6}},
        {"name": "Apache Flink", "label": "Stream Processing", "status": "healthy", "metrics": {"jobs_running": 2, "throughput": "3,104 events / sec", "checkpointing": "Enabled", "uptime": "14h 32m"}},
        {"name": "MongoDB Atlas", "label": "Primary Store", "status": "healthy", "metrics": {"connections": 48, "avg_query": "8ms", "storage_used": "2.4 GB", "collections": 7}},
    ]
    coll.insert_many(services)
    print(f"   🔧 Inserted {len(services)} pipeline services")


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
    print(f"   📊 Inserted {len(docs)} throughput points")


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
            {"name": "Price Floor Compliance", "result": "PASSED", "status": "healthy", "detail": "All 5,000 products are priced above cost x 1.10. Zero violations."},
            {"name": "Reason String Coverage", "result": "PARTIAL", "status": "review", "detail": "97.4% of price responses include a reason string. 62 responses missing reason field."},
        ],
        "disparity": [
            {"segment": "High Spenders", "avg_price": 96},
            {"segment": "Regular Shoppers", "avg_price": 67},
            {"segment": "Bargain Hunters", "avg_price": 39},
            {"segment": "New Users", "avg_price": 44},
        ],
        "features_used": ["demand_velocity", "inventory_ratio", "competitor_price", "user_wtp_score", "hour_of_day"],
        "features_blocked": ["user_age", "user_gender", "user_location"],
    }
    coll.insert_one(doc)
    print("   ⚖️  Inserted fairness audit")


# ──────────────────────────────────────────────
# 13. RECOMMENDATION STATS
# ──────────────────────────────────────────────
def seed_recommendations(db):
    coll = db["recommendation_stats"]
    coll.drop()
    doc = {
        "date": NOW.strftime("%Y-%m-%d"),
        "ctr": 34.2,
        "avg_recs_per_session": 8.4,
        "cold_start_rate": 12.1,
        "model_accuracy": 81.7,
        "top_categories": [
            {"name": "Electronics", "count": 4920},
            {"name": "Clothing", "count": 4110},
            {"name": "Sports", "count": 3660},
            {"name": "Home", "count": 2980},
            {"name": "Beauty", "count": 2340},
            {"name": "Books", "count": 1420},
        ],
        "session_model": [
            {"user_id": "usr_***44", "session": "08m 12s", "viewed": 17, "shown": 10, "clicked": 4, "converted": True},
            {"user_id": "usr_***12", "session": "05m 45s", "viewed": 11, "shown": 8, "clicked": 2, "converted": True},
            {"user_id": "usr_***98", "session": "10m 04s", "viewed": 26, "shown": 12, "clicked": 6, "converted": True},
            {"user_id": "usr_***37", "session": "03m 11s", "viewed": 7, "shown": 6, "clicked": 1, "converted": True},
            {"user_id": "usr_***20", "session": "09m 28s", "viewed": 19, "shown": 10, "clicked": 5, "converted": True},
        ],
        "cold_start_signals": {
            "enabled": ["Device Type", "Time of Day", "Referral Source"],
            "disabled": ["Geo Region"],
        },
    }
    coll.insert_one(doc)
    print("   🎯 Inserted recommendation stats")


# ──────────────────────────────────────────────
# 14. PRICING ENGINE
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
            "min_price": "cost × 1.10",
            "max_discount": "30%",
            "compliance": "No protected attributes used",
        },
        "demand_signals": {
            "avg_velocity": "142 views/min",
            "inventory_ratio": 0.64,
            "competitor_delta": "-2.3%",
        },
        "top_movers": [
            {"rank": 1, "product": "Atlas Smartwatch", "category": "Electronics", "changes": 31, "current": 214, "margin": "34%"},
            {"rank": 2, "product": "Pulse Max Headphones", "category": "Electronics", "changes": 28, "current": 139, "margin": "29%"},
            {"rank": 3, "product": "CoreRun Jacket", "category": "Clothing", "changes": 25, "current": 98, "margin": "21%"},
            {"rank": 4, "product": "ZenDesk Lamp", "category": "Home", "changes": 22, "current": 59, "margin": "27%"},
            {"rank": 5, "product": "Nova Skin Serum", "category": "Beauty", "changes": 20, "current": 38, "margin": "18%"},
        ],
        "price_distribution": [
            {"range": "$0–$25", "pct": 21},
            {"range": "$25–$50", "pct": 34},
            {"range": "$50–$100", "pct": 26},
            {"range": "$100–$250", "pct": 15},
            {"range": "$250+", "pct": 4},
        ],
    }
    coll.insert_one(doc)
    print("   ⚙️  Inserted pricing engine data")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    print("\n🔌 Connecting to MongoDB Atlas...")
    db = get_db()
    print(f"📂 Database: {DB_NAME}\n")

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

    colls = db.list_collection_names()
    print(f"\n✅ Done! {len(colls)} collections created: {', '.join(sorted(colls))}")


if __name__ == "__main__":
    main()
