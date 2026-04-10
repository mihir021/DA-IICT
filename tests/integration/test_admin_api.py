from unittest.mock import patch


@patch("apps.admin_api.views.login_admin")
def test_admin_login_endpoint_success(mock_login_admin, api_client):
    mock_login_admin.return_value = {
        "token": "signed-token",
        "admin": {"name": "Store Manager", "email": "admin@grocerypulse.local", "role": "operations_admin"},
    }

    response = api_client.post("/api/admin/auth/login", {"email": "admin@grocerypulse.local", "password": "ChangeMe123!"}, format="json")

    assert response.status_code == 200
    assert response.json()["token"] == "signed-token"


@patch("apps.admin_api.views.authenticate_request")
@patch("apps.admin_api.views.get_dashboard_data")
def test_dashboard_summary_requires_auth_and_returns_payload(mock_get_dashboard_data, mock_authenticate_request, api_client):
    mock_authenticate_request.return_value = {"email": "admin@grocerypulse.local", "is_staff": True}
    mock_get_dashboard_data.return_value = {
        "filters": {"range": "7d"},
        "kpis": {"today_revenue": 1000, "active_orders": 2, "low_stock_skus": 1, "perishable_attention": 1},
        "charts": {"sales_trends": [], "inventory_mix": [], "category_performance": [], "inventory_depth_3d": []},
        "alerts": [],
        "sections": {"orders": {"status_breakdown": {"pending": 1}}},
        "updated_at": "2026-01-01T00:00:00+00:00",
    }

    response = api_client.get("/api/admin/dashboard/summary?range=7d", HTTP_AUTHORIZATION="Bearer signed-token")

    assert response.status_code == 200
    assert "kpis" in response.json()


@patch("apps.admin_api.views.authenticate_request")
@patch("apps.admin_api.views.get_operations_data")
def test_operations_summary_endpoint_returns_payload(mock_get_operations_data, mock_authenticate_request, api_client):
    mock_authenticate_request.return_value = {"email": "admin@grocerypulse.local", "is_staff": True}
    mock_get_operations_data.return_value = {"inventory_watch": [], "top_movers": [], "order_lane": [], "updated_at": "2026-01-01T00:00:00+00:00"}

    response = api_client.get("/api/admin/operations/summary?range=7d", HTTP_AUTHORIZATION="Bearer signed-token")

    assert response.status_code == 200
    assert "top_movers" in response.json()


@patch("apps.admin_api.views.authenticate_request")
@patch("apps.admin_api.views.get_user_insights")
def test_user_insights_endpoint_returns_payload(mock_get_user_insights, mock_authenticate_request, api_client):
    mock_authenticate_request.return_value = {"email": "admin@grocerypulse.local", "is_staff": True}
    mock_get_user_insights.return_value = {"kpis": {"average_basket_value": 500, "repeat_customer_rate": 40, "high_intent_users": 3}, "scatter_matrix_3d": [], "top_customers": [], "segment_mix": {}}

    response = api_client.get("/api/admin/users/insights", HTTP_AUTHORIZATION="Bearer signed-token")

    assert response.status_code == 200
    assert "scatter_matrix_3d" in response.json()
