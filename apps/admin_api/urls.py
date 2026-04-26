from django.urls import path
from django.views.generic import TemplateView

from apps.admin_api.views import (
    AdminLogsView,
    AdminDashboardSummaryView,
    AdminLoginView,
    AlertsView,
    CategoryPerformanceView,
    ContactMessagesView,
    GlobalSearchView,
    InventoryOverviewView,
    OperationsSummaryView,
    OrderOverviewView,
    OrdersListView,
    ProductsListView,
    SalesTrendView,
    UserInsightsView,
    UsersListView,
    AddProductView,
    RestockProductView,
)


urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────
    path("admin/auth/login", AdminLoginView.as_view(), name="admin-login"),

    # ── HTML Portal (single page) ─────────────────────────────────
    path("admin/portal/", TemplateView.as_view(template_name="pages/admin.html"), name="admin-portal"),

    # ── Dashboard / Analytics APIs ────────────────────────────────
    path("admin/dashboard/summary", AdminDashboardSummaryView.as_view(), name="admin-dashboard-summary"),
    path("admin/dashboard/sales-trends", SalesTrendView.as_view(), name="admin-sales-trends"),
    path("admin/dashboard/inventory-overview", InventoryOverviewView.as_view(), name="admin-inventory-overview"),
    path("admin/dashboard/order-overview", OrderOverviewView.as_view(), name="admin-order-overview"),
    path("admin/dashboard/category-performance", CategoryPerformanceView.as_view(), name="admin-category-performance"),
    path("admin/dashboard/alerts", AlertsView.as_view(), name="admin-alerts"),
    path("admin/operations/summary", OperationsSummaryView.as_view(), name="admin-operations-summary"),

    # ── User & Log APIs ───────────────────────────────────────────
    path("admin/users/insights", UserInsightsView.as_view(), name="admin-users-insights"),
    path("admin/admin-logs", AdminLogsView.as_view(), name="admin-logs"),

    # ── NEW: Full data list endpoints ─────────────────────────────
    path("admin/products/list", ProductsListView.as_view(), name="admin-products-list"),
    path("admin/orders/list", OrdersListView.as_view(), name="admin-orders-list"),
    path("admin/users/list", UsersListView.as_view(), name="admin-users-list"),
    path("admin/contact-messages", ContactMessagesView.as_view(), name="admin-contact-messages"),
    path("admin/search", GlobalSearchView.as_view(), name="admin-global-search"),

    # ── Product management ────────────────────────────────────────
    path("admin/products/add", AddProductView.as_view(), name="admin-add-product"),
    path("admin/products/<str:product_id>/restock", RestockProductView.as_view(), name="admin-restock-product"),
]
