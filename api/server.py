"""
PulsePrice Admin — Flask API Server
Connects to MongoDB Atlas and serves live data to the admin dashboard.
Run: python api/server.py
"""
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import json_util
import json

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "pulseprice_admin")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]


def to_json(cursor):
    """Convert MongoDB cursor/doc to JSON-serializable dict."""
    return json.loads(json_util.dumps(cursor))


# ──────────── HEALTH CHECK ────────────
@app.route("/api/health")
def health():
    try:
        client.admin.command("ping")
        return jsonify({"status": "ok", "db": DB_NAME, "collections": db.list_collection_names()})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ──────────── OVERVIEW ────────────
@app.route("/api/kpi")
def kpi():
    doc = db["kpi_metrics"].find_one({}, {"_id": 0})
    return jsonify(doc or {})


@app.route("/api/revenue")
def revenue():
    docs = list(db["revenue_daily"].find({}, {"_id": 0}).sort("date", 1))
    return jsonify(docs)


@app.route("/api/price-changes")
def price_changes():
    docs = list(db["price_changes"].find({}, {"_id": 0}).sort("minutes_ago", 1))
    return jsonify(to_json(docs))


@app.route("/api/adjustment-reasons")
def adjustment_reasons():
    docs = list(db["adjustment_reasons"].find({}, {"_id": 0}))
    return jsonify(docs)


# ──────────── PRICING ENGINE ────────────
@app.route("/api/pricing-engine")
def pricing_engine():
    doc = db["pricing_engine"].find_one({}, {"_id": 0})
    return jsonify(doc or {})


# ──────────── PRODUCTS ────────────
@app.route("/api/products")
def products():
    docs = list(db["products"].find({}, {"_id": 0}))
    return jsonify(to_json(docs))


# ──────────── RECOMMENDATIONS ────────────
@app.route("/api/recommendations")
def recommendations():
    doc = db["recommendation_stats"].find_one({}, {"_id": 0})
    return jsonify(doc or {})


# ──────────── USER SEGMENTS ────────────
@app.route("/api/user-segments")
def user_segments():
    docs = list(db["user_segments"].find({}, {"_id": 0}))
    return jsonify(docs)


@app.route("/api/user-sessions")
def user_sessions():
    docs = list(db["user_sessions"].find({}, {"_id": 0}))
    return jsonify(docs)


# ──────────── A/B EXPERIMENTS ────────────
@app.route("/api/ab-experiments")
def ab_experiments():
    docs = list(db["ab_experiments"].find({}, {"_id": 0}))
    return jsonify(to_json(docs))


@app.route("/api/ab-events")
def ab_events():
    docs = list(db["ab_event_log"].find({}, {"_id": 0}))
    return jsonify(docs)


# ──────────── PIPELINE ────────────
@app.route("/api/pipeline")
def pipeline():
    docs = list(db["pipeline_status"].find({}, {"_id": 0}))
    return jsonify(docs)


@app.route("/api/throughput")
def throughput():
    docs = list(db["throughput_history"].find({}, {"_id": 0}).sort("timestamp", 1))
    return jsonify(to_json(docs))


# ──────────── FAIRNESS ────────────
@app.route("/api/fairness")
def fairness():
    doc = db["fairness_audit"].find_one({}, {"_id": 0})
    return jsonify(to_json(doc or {}))


# ──────────── TOTAL USERS COUNT ────────────
@app.route("/api/user-counts")
def user_counts():
    segments = list(db["user_segments"].find({}, {"_id": 0}))
    total = sum(s.get("count", 0) for s in segments)
    return jsonify({
        "total_users": total,
        "active_today": 1847,
        "new_this_week": 312,
    })


if __name__ == "__main__":
    print("[*] PulsePrice API starting on http://localhost:5000")
    print(f"[*] Database: {DB_NAME}")
    try:
        client.admin.command("ping")
        print("[OK] MongoDB connected!")
    except Exception as e:
        print(f"[ERROR] MongoDB error: {e}")
    app.run(debug=True, port=5000)
