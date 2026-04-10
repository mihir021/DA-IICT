from apps.admin_api.dashboard import (
    build_admin_logs_payload,
    build_alerts,
    build_dashboard_payload,
    build_operations_payload,
    build_user_insights_payload,
)


def test_build_dashboard_payload_contains_expected_sections():
    payload = build_dashboard_payload("7d")

    assert "kpis" in payload
    assert "charts" in payload
    assert "alerts" in payload
    assert "orders" in payload["sections"]


def test_build_alerts_flags_low_stock_and_perishable_products():
    alerts = build_alerts(
        [
            {"name": "Spinach", "stock_quantity": 8, "reorder_threshold": 12, "perishable": True, "freshness_days": 1},
            {"name": "Granola", "stock_quantity": 50, "reorder_threshold": 10, "perishable": False, "freshness_days": 20},
        ]
    )

    assert any(alert["type"] == "low_stock" for alert in alerts)
    assert any(alert["type"] == "perishable" for alert in alerts)


def test_operations_payload_contains_operational_sections():
    payload = build_operations_payload("7d")

    assert "inventory_watch" in payload
    assert "top_movers" in payload
    assert "order_lane" in payload


def test_user_insights_payload_contains_scatter_data():
    payload = build_user_insights_payload()

    assert "scatter_matrix_3d" in payload
    assert "segment_mix" in payload
    assert payload["kpis"]["high_intent_users"] >= 0


def test_admin_logs_payload_contains_entries():
    payload = build_admin_logs_payload()

    assert "entries" in payload
