from django.urls import path

from apps.admin_api.views import (
    AdminLogsView,
    AdminDashboardSummaryView,
    AdminLoginView,
    AlertsView,
    CategoryPerformanceView,
    InventoryOverviewView,
    OperationsSummaryView,
    OrderOverviewView,
    SalesTrendView,
    UserInsightsView,
)


urlpatterns = [
    path("admin/auth/login", AdminLoginView.as_view(), name="admin-login"),
    path("admin/dashboard/summary", AdminDashboardSummaryView.as_view(), name="admin-dashboard-summary"),
    path("admin/dashboard/sales-trends", SalesTrendView.as_view(), name="admin-sales-trends"),
    path("admin/dashboard/inventory-overview", InventoryOverviewView.as_view(), name="admin-inventory-overview"),
    path("admin/dashboard/order-overview", OrderOverviewView.as_view(), name="admin-order-overview"),
    path("admin/dashboard/category-performance", CategoryPerformanceView.as_view(), name="admin-category-performance"),
    path("admin/dashboard/alerts", AlertsView.as_view(), name="admin-alerts"),
    path("admin/operations/summary", OperationsSummaryView.as_view(), name="admin-operations-summary"),
    path("admin/users/insights", UserInsightsView.as_view(), name="admin-users-insights"),
    path("admin/admin-logs", AdminLogsView.as_view(), name="admin-logs"),
]
