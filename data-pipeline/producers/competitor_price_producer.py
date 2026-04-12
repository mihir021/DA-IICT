"""
Synthetic competitor-price producer for local Kafka.

Run:
  python data-pipeline/producers/competitor_price_producer.py --rate 2
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
TOPIC = os.getenv("KAFKA_COMPETITOR_TOPIC", "competitor-prices")

PRODUCTS = [
    "Organic Whole Milk",
    "Sourdough Bread",
    "Hass Avocados",
    "Greek Yogurt",
    "Jasmine Rice",
    "Baby Spinach",
]
COMPETITORS = ["BigBasket", "Blinkit", "Zepto", "Instamart"]


def build_event() -> dict:
    base = random.uniform(2.0, 15.0)
    return {
        "product_name": random.choice(PRODUCTS),
        "competitor": random.choice(COMPETITORS),
        "competitor_price": round(base, 2),
        "in_stock": random.choice([True, True, True, False]),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=2.0, help="Events per second")
    parser.add_argument("--count", type=int, default=0, help="Total events (0 = infinite)")
    args = parser.parse_args()

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=100,
        acks=1,
    )

    sent = 0
    delay = 1.0 / max(args.rate, 0.2)
    print(f"[competitor] sending to {TOPIC} via {BOOTSTRAP} at {args.rate:.2f} eps")
    try:
        while True:
            event = build_event()
            producer.send(TOPIC, event)
            sent += 1
            if sent % 20 == 0:
                producer.flush()
                print(f"[competitor] sent {sent} events")
            if args.count and sent >= args.count:
                break
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\n[competitor] stopped by user")
    finally:
        producer.flush()
        producer.close()
        print(f"[competitor] total sent: {sent}")


if __name__ == "__main__":
    main()
