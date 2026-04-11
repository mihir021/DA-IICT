from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def home(request):
    return render(request, "landingPage.html") 

def aiGroceryPlanner(request):
    return render(request, "AIGroceryPlanner.html") 

def myOrder(request):
    return render(request, "myOrder.html")


def login(request):
    return render(request, "login.html")