"""
Synthetic clickstream producer for local Kafka.

Run:
  python data-pipeline/producers/clickstream_producer.py --rate 8
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from kafka import KafkaProducer

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_CLICKSTREAM_TOPIC", "user-events")

PRODUCTS = [
    ("Organic Whole Milk", "Dairy"),
    ("Sourdough Bread", "Bakery"),
    ("Hass Avocados", "Produce"),
    ("Greek Yogurt", "Dairy"),
    ("Jasmine Rice", "Staples"),
    ("Baby Spinach", "Produce"),
]
EVENT_TYPES = ["view", "search", "add_to_cart", "purchase"]


def build_event() -> dict:
    product, category = random.choice(PRODUCTS)
    event_type = random.choices(EVENT_TYPES, weights=[50, 20, 20, 10], k=1)[0]
    price = round(random.uniform(2.0, 15.0), 2)
    return {
        "event_type": event_type,
        "user_id": f"user_{random.randint(1000, 9999)}",
        "session_id": f"session_{random.randint(10000, 99999)}",
        "product_name": product,
        "category": category,
        "price": price,
        "quantity": random.randint(1, 3) if event_type in {"add_to_cart", "purchase"} else 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=6.0, help="Events per second")
    parser.add_argument("--count", type=int, default=0, help="Total events (0 = infinite)")
    args = parser.parse_args()

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=50,
        acks=1,
    )

    sent = 0
    delay = 1.0 / max(args.rate, 0.2)
    print(f"[clickstream] sending to {TOPIC} via {BOOTSTRAP} at {args.rate:.2f} eps")
    try:
        while True:
            event = build_event()
            producer.send(TOPIC, event)
            sent += 1
            if sent % 50 == 0:
                producer.flush()
                print(f"[clickstream] sent {sent} events")
            if args.count and sent >= args.count:
                break
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\n[clickstream] stopped by user")
    finally:
        producer.flush()
        producer.close()
        print(f"[clickstream] total sent: {sent}")


if __name__ == "__main__":
    main()
