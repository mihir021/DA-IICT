from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path("aiGroceryPlanner",views.aiGroceryPlanner),
    path('myOrder',views.myOrder)
]