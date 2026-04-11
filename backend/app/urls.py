from django.urls import path
from .views import (
    SignupView, LoginView, ProfileView, ExpenseView, 
    OrderView, MonthlyGraphView, CategoryGraphView,
    ProductListView, BestSellerView, OfferView
)

urlpatterns = [
    # Auth APIs - simplified as requested
    path('signup/', SignupView.as_view(), name='api-signup'),
    path('login/', LoginView.as_view(), name='api-login'),
    
    # User Profile & Stats
    path('profile/', ProfileView.as_view(), name='api-profile'),
    path('expenses/', ExpenseView.as_view(), name='api-expenses'),
    path('expense-graph/monthly/', MonthlyGraphView.as_view(), name='monthly-graph'),
    path('expense-graph/category/', CategoryGraphView.as_view(), name='category-graph'),
    
    # Orders & Inventory
    path('orders/', OrderView.as_view(), name='api-orders'),
    path('products/', ProductListView.as_view(), name='api-products'),
    path('best-sellers/', BestSellerView.as_view(), name='best-sellers'),
    path('offers/', OfferView.as_view(), name='offers'),
]
