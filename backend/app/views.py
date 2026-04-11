from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import SignupSerializer, LoginSerializer, ExpenseSerializer, ProfileUpdateSerializer
from .services import (
    signup_user, login_user, get_profile, update_profile, 
    get_user_expenses, add_user_expense, get_user_orders,
    generate_monthly_expense_graph, generate_category_expense_graph,
    get_all_products, get_special_products
)

class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            try:
                res = signup_user(serializer.validated_data)
                return Response(res, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                res = login_user(serializer.validated_data)
                return Response(res, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id
        profile = get_profile(user_id)
        if profile is None:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(profile, status=status.HTTP_200_OK)
    
    def put(self, request):
        user_id = request.user.id
        serializer = ProfileUpdateSerializer(data=request.data)
        if serializer.is_valid():
            profile = update_profile(user_id, serializer.validated_data)
            return Response(profile, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExpenseView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id
        expenses = get_user_expenses(user_id)
        return Response(expenses, status=status.HTTP_200_OK)
    
    def post(self, request):
        user_id = request.user.id
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            expense = add_user_expense(user_id, serializer.validated_data)
            return Response(expense, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id
        orders = get_user_orders(user_id)
        return Response(orders, status=status.HTTP_200_OK)

class MonthlyGraphView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id
        graph_json = generate_monthly_expense_graph(user_id)
        if not graph_json:
            return Response({"error": "No data for graph"}, status=status.HTTP_404_NOT_FOUND)
        return Response(graph_json, status=status.HTTP_200_OK)

class CategoryGraphView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id
        graph_json = generate_category_expense_graph(user_id)
        if not graph_json:
            return Response({"error": "No data for graph"}, status=status.HTTP_404_NOT_FOUND)
        return Response(graph_json, status=status.HTTP_200_OK)

class ProductListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        search = request.query_params.get("search", "")
        category = request.query_params.get("category", "All")
        products = get_all_products(search, category)
        return Response(products, status=200)

class BestSellerView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        products = get_special_products("best_sellers")
        return Response(products, status=200)

class OfferView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        products = get_special_products("offers")
        return Response(products, status=200)
