"""
PulsePrice Admin API server.

Primary mode: MongoDB-backed data.
Fallback mode: built-in demo data if MongoDB is unavailable or not configured.
Run: python api/server.py
"""

from __future__ import annotations

import json
import os
import threading
import time
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path

from bson import json_util
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
try:
    from kafka import KafkaConsumer, TopicPartition
    from kafka.errors import KafkaError
except Exception:  # noqa: BLE001
    KafkaConsumer = None
    TopicPartition = None
    KafkaError = Exception

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("MONGO_DB_NAME", "grocery_admin")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_CLICKSTREAM_TOPIC = os.getenv("KAFKA_CLICKSTREAM_TOPIC", "user-events")
KAFKA_COMPETITOR_TOPIC = os.getenv("KAFKA_COMPETITOR_TOPIC", "competitor-prices")


def to_json(value):
    return json.loads(json_util.dumps(value))


DEMO_DATA = {
    "kpi": {
        "total_revenue_today": 1158937558,
        "revenue_change_pct": 5.2,
        "active_sessions": 1987694,
        "sessions_change_pct": 2.1,
        "prices_updated": 5368,
        "avg_order_value": 945.82,
        "aov_change_pct": 1.4,
    },
    "revenue": [
        {"day": "Mon", "revenue": 165562508},
        {"day": "Tue", "revenue": 162419651},
        {"day": "Wed", "revenue": 168105360},
        {"day": "Thu", "revenue": 164891722},
        {"day": "Fri", "revenue": 170234819},
        {"day": "Sat", "revenue": 172891247},
        {"day": "Sun", "revenue": 154832251},
    ],
    "price_changes": [
        {"product": "Electronics — SKU003847", "category": "Electronics", "old_price": 890.50, "new_price": 1029.00, "reason": "High Demand", "minutes_ago": 5, "status": "increased"},
        {"product": "Home & Kitchen — SKU001294", "category": "Home & Kitchen", "old_price": 348.00, "new_price": 320.00, "reason": "Clearance Sale", "minutes_ago": 12, "status": "decreased"},
        {"product": "Clothing — SKU003102", "category": "Clothing", "old_price": 89.00, "new_price": 95.00, "reason": "High Demand", "minutes_ago": 18, "status": "increased"},
    ],
    "adjustment_reasons": [
        {"reason": "Organic Search", "percentage": 22, "count": 2244000},
        {"reason": "Direct", "percentage": 20, "count": 2040000},
        {"reason": "Social Media", "percentage": 18, "count": 1836000},
        {"reason": "Paid Ads", "percentage": 16, "count": 1632000},
        {"reason": "Email", "percentage": 10, "count": 1020000},
        {"reason": "Affiliate", "percentage": 8, "count": 816000},
        {"reason": "Push Notification", "percentage": 6, "count": 612000},
    ],
    "pricing_engine": {
        "model_type": "Regression + Guardrails",
        "last_trained": "From dataset",
        "accuracy": 87.3,
        "guardrails": {"min_price": "$4.11", "max_discount": "30%", "compliance": "No protected attributes used"},
        "demand_signals": {"avg_velocity": "5.1 events/session", "inventory_ratio": 0.04, "competitor_delta": "N/A"},
        "top_movers": [
            {"rank": 1, "product": "Electronics — SKU003847", "category": "Electronics", "changes": 31, "current": 1029.00, "margin": "45%"},
            {"rank": 2, "product": "Home & Kitchen — SKU001294", "category": "Home & Kitchen", "changes": 28, "current": 348.00, "margin": "45%"},
            {"rank": 3, "product": "Beauty & Health — SKU002156", "category": "Beauty & Health", "changes": 22, "current": 165.00, "margin": "45%"},
        ],
        "price_distribution": [
            {"range": "$0-$50", "pct": 5},
            {"range": "$50-$100", "pct": 8},
            {"range": "$100-$250", "pct": 15},
            {"range": "$250-$500", "pct": 22},
            {"range": "$500-$1000", "pct": 28},
            {"range": "$1000+", "pct": 22},
        ],
    },
    "products": [
        {"sku": "SKU003847", "name": "Electronics — SKU003847", "category": "Electronics", "base_price": 945.82, "current_price": 945.82, "cost": 520.20, "margin_pct": 45, "stock": 2340, "status": "active", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=200&h=200&fit=crop&q=80"},
        {"sku": "SKU001294", "name": "Home & Kitchen — SKU001294", "category": "Home & Kitchen", "base_price": 320.00, "current_price": 348.00, "cost": 176.00, "margin_pct": 45, "stock": 1780, "status": "active", "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=200&h=200&fit=crop&q=80"},
        {"sku": "SKU002156", "name": "Beauty & Health — SKU002156", "category": "Beauty & Health", "base_price": 185.00, "current_price": 165.00, "cost": 101.75, "margin_pct": 45, "stock": 1450, "status": "active", "image": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=200&h=200&fit=crop&q=80"},
        {"sku": "SKU003102", "name": "Clothing — SKU003102", "category": "Clothing", "base_price": 89.00, "current_price": 95.00, "cost": 48.95, "margin_pct": 45, "stock": 890, "status": "active", "image": "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=200&h=200&fit=crop&q=80"},
    ],
    "recommendations": {
        "ctr": 63.5,
        "avg_recs_per_session": 6.2,
        "cold_start_rate": 18.0,
        "model_accuracy": 79.4,
        "session_model": [
            {"user_id": "U00121959", "session": "14m 47s", "viewed": 17, "shown": 10, "clicked": 4, "converted": True},
            {"user_id": "U00146868", "session": "16m 06s", "viewed": 11, "shown": 8, "clicked": 2, "converted": True},
        ],
        "top_categories": [
            {"name": "Electronics", "count": 4920},
            {"name": "Home & Kitchen", "count": 4110},
            {"name": "Beauty & Health", "count": 3660},
            {"name": "Clothing", "count": 2980},
            {"name": "Books & Media", "count": 2340},
        ],
        "cold_start_signals": {
            "enabled": ["device_type", "hour_of_day", "referral_source"],
            "disabled": ["user_zipcode"],
        },
    },
    "user_segments": [
        {"name": "High Value", "count": 1457143, "wtp_avg": 0.04, "avg_aov": 952.30, "conversion": 3.9, "progress": 100, "color": "gold"},
        {"name": "Loyal", "count": 1457143, "wtp_avg": 0.04, "avg_aov": 940.10, "conversion": 3.8, "progress": 100, "color": "emerald"},
        {"name": "Deal Seeker", "count": 1457143, "wtp_avg": 0.04, "avg_aov": 935.50, "conversion": 3.7, "progress": 100, "color": "violet"},
        {"name": "Casual Browser", "count": 1457143, "wtp_avg": 0.03, "avg_aov": 948.20, "conversion": 3.4, "progress": 95, "color": "warning"},
    ],
    "user_sessions": [
        {"user_id": "U00121959", "segment": "High Value", "engagement": 0.91, "categories": "Electronics", "wtp_score": 0.88, "last_active": "2024-04-08T06:42"},
        {"user_id": "U00146868", "segment": "At Risk", "engagement": 0.66, "categories": "Home & Kitchen", "wtp_score": 0.59, "last_active": "2024-02-13T05:53"},
    ],
    "ab_experiments": [
        {
            "experiment_id": "exp_clickstream_01",
            "type": "Dynamic Pricing A/B",
            "variant_a": {"name": "Control", "conversion": 3.91, "aov": 945.82, "revenue_session": 7.38, "sample": 3400000},
            "variant_b": {"name": "Treatment B", "conversion": 3.91, "aov": 946.10, "revenue_session": 7.40, "sample": 3400000},
            "split": "50 / 50",
            "status": "completed",
            "start_date": "2024-01-01",
            "days_running": 365,
            "confidence": 95,
            "winner": "B",
        }
    ],
    "ab_events": [
        {"timestamp": "2024-04-08T06:42:57", "user_id": "U00121959", "variant": "Control", "event": "page_view", "product": "Electronics — SKU002065", "revenue": None},
        {"timestamp": "2024-02-13T05:53:15", "user_id": "U00146868", "variant": "Control", "event": "purchase", "product": "Home & Kitchen — SKU003513", "revenue": 107.02},
    ],
    "pipeline": [
        {"name": "Kafka", "label": "Stream Broker", "status": "healthy", "metrics": {"messages_sec": 10200000, "topics": 9, "consumer_lag": "0ms", "partitions": 5}},
        {"name": "Apache Flink", "label": "Stream Processing", "status": "healthy", "metrics": {"jobs_running": 9, "throughput": "10,200,000 events total", "checkpointing": "Enabled", "uptime": "Dataset span"}},
        {"name": "MongoDB Atlas", "label": "Primary Store", "status": "healthy", "metrics": {"connections": 500000, "avg_query": "1987694 sessions", "storage_used": "10,200,000 events", "collections": 15}},
    ],
    "throughput": [
        {"label": "00:00", "value": 380000},
        {"label": "06:00", "value": 420000},
        {"label": "12:00", "value": 460000},
        {"label": "18:00", "value": 440000},
        {"label": "23:00", "value": 390000},
    ],
    "fairness": {
        "checks": [
            {"name": "Segment Price Parity", "result": "PASSED", "status": "healthy", "detail": "Max segment price gap within tolerance across 7 segments."},
            {"name": "Device Price Parity", "result": "PASSED", "status": "healthy", "detail": "Prices across mobile, desktop, tablet are within tolerance."},
            {"name": "AB Group Fairness", "result": "PASSED", "status": "healthy", "detail": "All 3 AB groups have balanced sample sizes."},
        ],
        "disparity": [
            {"segment": "High Value", "avg_price": 952.30},
            {"segment": "Loyal", "avg_price": 940.10},
            {"segment": "Deal Seeker", "avg_price": 935.50},
            {"segment": "New User", "avg_price": 948.20},
        ],
        "features_used": ["event_type", "session_id", "user_id", "sku_id", "category", "price_seen_usd", "quantity", "timestamp", "user_segment", "ab_group"],
        "features_blocked": ["user_age", "user_gender", "user_zipcode"],
    },
    "user_counts": {"total_users": 500000, "active_today": 500000, "new_this_week": 89827},
}

# Real-time Kafka stream state (best effort).
STREAM_LOCK = threading.Lock()
STREAM_STATE = {
    "kafka_connected": False,
    "kafka_error": "Kafka monitor not started.",
    "messages_sec": 0,
    "topics": 0,
    "consumer_lag": 0,
    "event_type_counts": Counter(),
    "last_events": deque(maxlen=100),
    "throughput_points": deque(maxlen=12),
}
KAFKA_SAMPLE = {"ts": None, "total_offsets": 0}


def _decode_message(raw):
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", errors="ignore")
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:  # noqa: BLE001
            return {"raw": raw}
    if isinstance(raw, dict):
        return raw
    return {"raw": str(raw)}


def _probe_kafka_once() -> None:
    if KafkaConsumer is None or TopicPartition is None:
        with STREAM_LOCK:
            STREAM_STATE["kafka_connected"] = False
            STREAM_STATE["kafka_error"] = "kafka-python is not installed."
            STREAM_STATE["messages_sec"] = 0
            STREAM_STATE["topics"] = 0
        return

    consumer = None
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            request_timeout_ms=2500,
            api_version_auto_timeout_ms=2500,
            consumer_timeout_ms=1000,
            enable_auto_commit=False,
            group_id=None,
        )
        topics = consumer.topics()
        tracked_topics = [t for t in [KAFKA_CLICKSTREAM_TOPIC, KAFKA_COMPETITOR_TOPIC] if t in topics]

        partitions = []
        for topic in tracked_topics:
            for p in consumer.partitions_for_topic(topic) or set():
                partitions.append(TopicPartition(topic, p))

        total_offsets = 0
        if partitions:
            end_offsets = consumer.end_offsets(partitions)
            total_offsets = sum(end_offsets.values())

        now = time.time()
        prev_ts = KAFKA_SAMPLE["ts"]
        prev_total = KAFKA_SAMPLE["total_offsets"]
        eps = 0
        if prev_ts is not None and now > prev_ts and total_offsets >= prev_total:
            eps = int((total_offsets - prev_total) / (now - prev_ts))

        KAFKA_SAMPLE["ts"] = now
        KAFKA_SAMPLE["total_offsets"] = total_offsets

        with STREAM_LOCK:
            STREAM_STATE["kafka_connected"] = True
            STREAM_STATE["kafka_error"] = ""
            STREAM_STATE["messages_sec"] = eps
            STREAM_STATE["topics"] = len(tracked_topics)
            STREAM_STATE["consumer_lag"] = 0
            STREAM_STATE["throughput_points"].append(
                {"label": datetime.now(timezone.utc).strftime("%H:%M:%S"), "value": eps}
            )
    except Exception as exc:  # noqa: BLE001
        with STREAM_LOCK:
            STREAM_STATE["kafka_connected"] = False
            STREAM_STATE["kafka_error"] = str(exc)
            STREAM_STATE["messages_sec"] = 0
            STREAM_STATE["topics"] = 0
    finally:
        if consumer is not None:
            try:
                consumer.close()
            except Exception:  # noqa: BLE001
                pass


def _stream_pipeline_override():
    with STREAM_LOCK:
        connected = STREAM_STATE["kafka_connected"]
        eps = STREAM_STATE["messages_sec"]
        lag = STREAM_STATE["consumer_lag"]
        topics = STREAM_STATE["topics"]

    return {
        "name": "Kafka",
        "label": "Event Stream",
        "metrics": {
            "messages_sec": f"{eps:,}",
            "topics": topics,
            "consumer_lag": lag,
            "partitions": 3,
        },
        "status": "healthy" if connected else "degraded",
    }


client = None
db = None
mongo_error = None

if MONGO_URI and "<username>" not in MONGO_URI and "<password>" not in MONGO_URI and "<cluster>" not in MONGO_URI:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        client.admin.command("ping")
    except Exception as exc:  # noqa: BLE001
        mongo_error = str(exc)
        client = None
        db = None
else:
    mongo_error = "MONGO_URI is not configured."

def use_demo() -> bool:
    return db is None


def find_one(collection: str, fallback):
    if use_demo():
        return fallback
    doc = db[collection].find_one({}, {"_id": 0})
    return doc if doc else fallback


def find_many(collection: str, fallback, sort_field: str | None = None):
    if use_demo():
        return fallback
    cursor = db[collection].find({}, {"_id": 0})
    if sort_field:
        cursor = cursor.sort(sort_field, 1)
    docs = list(cursor)
    return docs if docs else fallback


@app.route("/")
def serve_frontend():
    return send_from_directory(str(BASE_DIR / "frontend"), "admin.html")


@app.route("/api/health")
def health():
    _probe_kafka_once()
    with STREAM_LOCK:
        kafka_connected = STREAM_STATE["kafka_connected"]
        kafka_error = STREAM_STATE["kafka_error"]
        kafka_eps = STREAM_STATE["messages_sec"]
    if use_demo():
        return jsonify(
            {
                "status": "ok",
                "mode": "demo",
                "db": DB_NAME,
                "collections": [],
                "note": f"Running demo data fallback: {mongo_error}",
                "kafka_connected": kafka_connected,
                "kafka_messages_sec": kafka_eps,
                "kafka_error": kafka_error,
            }
        )
    return jsonify(
        {
            "status": "ok",
            "mode": "mongo",
            "db": DB_NAME,
            "collections": db.list_collection_names(),
            "kafka_connected": kafka_connected,
            "kafka_messages_sec": kafka_eps,
            "kafka_error": kafka_error,
        }
    )


@app.route("/api/kpi")
def kpi():
    return jsonify(find_one("kpi_metrics", DEMO_DATA["kpi"]))


@app.route("/api/revenue")
def revenue():
    return jsonify(find_many("revenue_daily", DEMO_DATA["revenue"], sort_field="date"))


@app.route("/api/price-changes")
def price_changes():
    return jsonify(to_json(find_many("price_changes", DEMO_DATA["price_changes"], sort_field="minutes_ago")))


@app.route("/api/adjustment-reasons")
def adjustment_reasons():
    return jsonify(find_many("adjustment_reasons", DEMO_DATA["adjustment_reasons"]))


@app.route("/api/pricing-engine")
def pricing_engine():
    return jsonify(find_one("pricing_engine", DEMO_DATA["pricing_engine"]))


@app.route("/api/products")
def products():
    return jsonify(to_json(find_many("products", DEMO_DATA["products"])))


@app.route("/api/recommendations")
def recommendations():
    return jsonify(find_one("recommendation_stats", DEMO_DATA["recommendations"]))


@app.route("/api/user-segments")
def user_segments():
    return jsonify(find_many("user_segments", DEMO_DATA["user_segments"]))


@app.route("/api/user-sessions")
def user_sessions():
    return jsonify(find_many("user_sessions", DEMO_DATA["user_sessions"]))


@app.route("/api/ab-experiments")
def ab_experiments():
    return jsonify(to_json(find_many("ab_experiments", DEMO_DATA["ab_experiments"])))


@app.route("/api/ab-events")
def ab_events():
    return jsonify(find_many("ab_event_log", DEMO_DATA["ab_events"]))


@app.route("/api/pipeline")
def pipeline():
    _probe_kafka_once()
    data = find_many("pipeline_status", DEMO_DATA["pipeline"])
    kafka_row = _stream_pipeline_override()
    replaced = False
    for i, row in enumerate(data):
        if row.get("name") == "Kafka":
            data[i] = kafka_row
            replaced = True
            break
    if not replaced:
        data.insert(0, kafka_row)
    return jsonify(data)


@app.route("/api/throughput")
def throughput():
    _probe_kafka_once()
    with STREAM_LOCK:
        dynamic_points = list(STREAM_STATE["throughput_points"])
    if dynamic_points:
        return jsonify(dynamic_points)
    return jsonify(to_json(find_many("throughput_history", DEMO_DATA["throughput"], sort_field="timestamp")))


@app.route("/api/kafka/stream")
def kafka_stream():
    _probe_kafka_once()
    with STREAM_LOCK:
        return jsonify(
            {
                "connected": STREAM_STATE["kafka_connected"],
                "error": STREAM_STATE["kafka_error"],
                "messages_sec": STREAM_STATE["messages_sec"],
                "event_type_counts": dict(STREAM_STATE["event_type_counts"]),
                "recent_events": list(STREAM_STATE["last_events"]),
            }
        )


@app.route("/api/fairness")
def fairness():
    return jsonify(to_json(find_one("fairness_audit", DEMO_DATA["fairness"])))


@app.route("/api/user-counts")
def user_counts():
    if use_demo():
        return jsonify(DEMO_DATA["user_counts"])
    doc = db["user_counts"].find_one({}, {"_id": 0})
    if doc:
        return jsonify(doc)
    segments = list(db["user_segments"].find({}, {"_id": 0}))
    total = sum(s.get("count", 0) for s in segments)
    return jsonify({"total_users": total, "active_today": 0, "new_this_week": 0})


if __name__ == "__main__":
    print("[*] PulsePrice API starting on http://127.0.0.1:5000")
    if use_demo():
        print(f"[WARN] MongoDB unavailable. Demo mode enabled. Reason: {mongo_error}")
    else:
        print(f"[OK] MongoDB connected. Database: {DB_NAME}")
    app.run(debug=True, port=5000)
