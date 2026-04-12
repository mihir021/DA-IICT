from django.urls import path
from . import views

urlpatterns = [
    # ── Page views ──────────────────────────────────────────────────
    path("", views.home, name="home"),
    path("aiGroceryPlanner/", views.aiGroceryPlanner, name="aiGroceryPlanner"),
    path("myOrder/", views.myOrder, name="myOrder"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("index/", views.index_page, name="index"),
    path("profile/", views.profile_page, name="profile"),
    path("cart/", views.cart_page, name="cart"),
    path("product/<str:product_id>/", views.product_page, name="product"),

    # ── Auth API ────────────────────────────────────────────────────
    path("api/auth/signup/", views.api_signup, name="api_signup"),
    path("api/auth/login/", views.api_login, name="api_login"),

    # ── Products API ────────────────────────────────────────────────
    path("api/auth/products/", views.api_products, name="api_products"),
    path("api/auth/products/best-sellers/", views.api_best_sellers, name="api_best_sellers"),
    path("api/auth/products/offers/", views.api_offers, name="api_offers"),
    path("api/auth/products/<str:product_id>/", views.api_product_detail, name="api_product_detail"),
    path("api/auth/products/<str:product_id>/suggestions/", views.api_product_suggestions, name="api_product_suggestions"),

    # ── AI Planner API ──────────────────────────────────────────────
    path("api/planner/generate/", views.api_planner_generate, name="api_planner_generate"),
    path("api/planner/add-to-cart/", views.api_planner_add_to_cart, name="api_planner_add_to_cart"),

    # ── Cart API ────────────────────────────────────────────────────
    path("api/cart/", views.api_cart, name="api_cart"),
    path("api/cart/update/", views.api_cart_update, name="api_cart_update"),
    path("api/cart/remove/", views.api_cart_remove, name="api_cart_remove"),
    path("api/cart/checkout/", views.api_cart_checkout, name="api_cart_checkout"),

    # ── Profile API ─────────────────────────────────────────────────
    path("api/profile/profile/", views.api_profile, name="api_profile"),

    # ── Expenses API ────────────────────────────────────────────────
    path("api/expenses/expenses/", views.api_expenses, name="api_expenses"),
    path("api/expenses/expense-graph/<str:graph_type>/", views.api_expense_graph, name="api_expense_graph"),

    # ── Orders API ──────────────────────────────────────────────────
    path("api/orders/orders/", views.api_orders, name="api_orders"),

    # ── Session Tracking (Dynamic Pricing) ──────────────────────────
    path("api/session/track/", views.api_track_session, name="api_track_session"),

    # ── ML Model API ────────────────────────────────────────────────
    path("api/ml/model-info/", views.api_ml_model_info, name="api_ml_model_info"),
    path("api/ml/retrain/", views.api_ml_retrain, name="api_ml_retrain"),
]