from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path("aiGroceryPlanner",views.aiGroceryPlanner, name="aiGroceryPlanner"),
    path('myOrder',views.myOrder, name="myOrder"),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),

]