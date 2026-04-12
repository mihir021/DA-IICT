#!/usr/bin/env bash
set -euo pipefail

BROKER="${BROKER:-localhost:9092}"
CLICKSTREAM_TOPIC="${KAFKA_CLICKSTREAM_TOPIC:-user-events}"
COMP_TOPIC="${KAFKA_COMPETITOR_TOPIC:-competitor-prices}"

echo "Creating topics on broker ${BROKER}..."

kafka-topics.sh --bootstrap-server "${BROKER}" --create --if-not-exists --topic "${CLICKSTREAM_TOPIC}" --partitions 3 --replication-factor 1
kafka-topics.sh --bootstrap-server "${BROKER}" --create --if-not-exists --topic "${COMP_TOPIC}" --partitions 3 --replication-factor 1

echo "Existing topics:"
kafka-topics.sh --bootstrap-server "${BROKER}" --list
