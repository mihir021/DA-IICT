from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.admin_api.auth import authenticate_request
from apps.admin_api.serializers import AdminLoginSerializer, DashboardQuerySerializer
from apps.admin_api.services import get_admin_logs, get_dashboard_data, get_operations_data, get_user_insights, login_admin


class AdminProtectedAPIView(APIView):
    def get_admin(self, request) -> dict | None:
        return authenticate_request(request)

    def handle_unauthorized(self) -> Response:
        return Response({"detail": "Admin authentication required."}, status=status.HTTP_401_UNAUTHORIZED)


class AdminLoginView(APIView):
    def post(self, request) -> Response:
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = login_admin(**serializer.validated_data)
        if payload is None:
            return Response({"detail": "Invalid admin credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(payload, status=status.HTTP_200_OK)


class AdminDashboardSummaryView(AdminProtectedAPIView):
    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(get_dashboard_data(serializer.validated_data["range"]), status=status.HTTP_200_OK)


class AdminChartView(AdminProtectedAPIView):
    chart_name = ""

    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payload = get_dashboard_data(serializer.validated_data["range"])
        return Response({"filters": payload["filters"], "data": payload["charts"][self.chart_name], "updated_at": payload["updated_at"]}, status=status.HTTP_200_OK)


class SalesTrendView(AdminChartView):
    chart_name = "sales_trends"


class InventoryOverviewView(AdminChartView):
    chart_name = "inventory_mix"


class CategoryPerformanceView(AdminChartView):
    chart_name = "category_performance"


class OrderOverviewView(AdminProtectedAPIView):
    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payload = get_dashboard_data(serializer.validated_data["range"])
        return Response({"filters": payload["filters"], "data": payload["sections"]["orders"], "updated_at": payload["updated_at"]}, status=status.HTTP_200_OK)


class AlertsView(AdminProtectedAPIView):
    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payload = get_dashboard_data(serializer.validated_data["range"])
        return Response({"filters": payload["filters"], "data": payload["alerts"], "updated_at": payload["updated_at"]}, status=status.HTTP_200_OK)


class OperationsSummaryView(AdminProtectedAPIView):
    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payload = get_operations_data(serializer.validated_data["range"])
        return Response(payload, status=status.HTTP_200_OK)


class UserInsightsView(AdminProtectedAPIView):
    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        return Response(get_user_insights(), status=status.HTTP_200_OK)


class AdminLogsView(AdminProtectedAPIView):
    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        return Response(get_admin_logs(), status=status.HTTP_200_OK)


# ─── NEW ENDPOINTS ────────────────────────────────────────────────────────────

class ProductsListView(AdminProtectedAPIView):
    """Return all products from MongoDB for admin product management."""
    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        from apps.market.mongo_client import get_db
        db = get_db()
        if db is None:
            return Response([], status=status.HTTP_200_OK)
        products = list(db["products"].find({}).limit(300))
        result = []
        for p in products:
            p["_id"] = str(p["_id"])
            if p.get("images") and not p.get("image_url"):
                p["image_url"] = p["images"][0]
            result.append(p)
        return Response(result, status=status.HTTP_200_OK)


class OrdersListView(AdminProtectedAPIView):
    """Return all orders from MongoDB sorted newest-first."""
    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        from apps.market.mongo_client import get_db
        db = get_db()
        if db is None:
            return Response([], status=status.HTTP_200_OK)
        orders = list(db["orders"].find({}).sort("created_at", -1).limit(300))
        result = []
        for o in orders:
            o["_id"] = str(o["_id"])
            if "created_at" in o and hasattr(o["created_at"], "isoformat"):
                o["created_at"] = o["created_at"].isoformat()
            result.append(o)
        return Response(result, status=status.HTTP_200_OK)


class UsersListView(AdminProtectedAPIView):
    """Return all registered users (passwords and tokens excluded)."""
    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        from apps.market.mongo_client import get_db
        db = get_db()
        if db is None:
            return Response([], status=status.HTTP_200_OK)
        users = list(db["users"].find({}, {"password": 0, "token": 0}).sort("created_at", -1).limit(300))
        result = []
        for u in users:
            u["_id"] = str(u["_id"])
            if "created_at" in u and hasattr(u["created_at"], "isoformat"):
                u["created_at"] = u["created_at"].isoformat()
            result.append(u)
        return Response(result, status=status.HTTP_200_OK)


class ContactMessagesView(AdminProtectedAPIView):
    """Return all contact form submissions."""
    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        from apps.market.mongo_client import get_db
        db = get_db()
        if db is None:
            return Response([], status=status.HTTP_200_OK)
        messages = list(db["contact_messages"].find({}).sort("created_at", -1).limit(200))
        result = []
        for m in messages:
            m["_id"] = str(m["_id"])
            if "created_at" in m and hasattr(m["created_at"], "isoformat"):
                m["created_at"] = m["created_at"].isoformat()
            result.append(m)
        return Response(result, status=status.HTTP_200_OK)


class GlobalSearchView(AdminProtectedAPIView):
    """Search across products, orders, and users simultaneously."""
    def get(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        q = request.query_params.get("q", "").strip()
        if len(q) < 2:
            return Response({"products": [], "orders": [], "users": []}, status=status.HTTP_200_OK)
        from apps.market.mongo_client import get_db
        import re
        db = get_db()
        if db is None:
            return Response({"products": [], "orders": [], "users": []}, status=status.HTTP_200_OK)
        pat = {"$regex": re.escape(q), "$options": "i"}
        products = list(db["products"].find(
            {"$or": [{"name": pat}, {"category": pat}]},
            {"_id": 1, "name": 1, "category": 1, "price": 1, "stock_quantity": 1}
        ).limit(6))
        orders = list(db["orders"].find(
            {"$or": [{"user_name": pat}, {"user_email": pat}, {"status": pat}]},
            {"_id": 1, "user_name": 1, "user_email": 1, "status": 1, "total_amount": 1}
        ).limit(6))
        users = list(db["users"].find(
            {"$or": [{"name": pat}, {"email": pat}]},
            {"_id": 1, "name": 1, "email": 1}
        ).limit(6))
        for x in [*products, *orders, *users]:
            x["_id"] = str(x["_id"])
        return Response({"products": products, "orders": orders, "users": users}, status=status.HTTP_200_OK)


class AddProductView(AdminProtectedAPIView):
    """Create a new product document in MongoDB."""
    def post(self, request) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        from apps.market.mongo_client import get_db
        from datetime import datetime, UTC
        db = get_db()
        if db is None:
            return Response({"error": "Database unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        data = request.data
        name = (data.get("name") or "").strip()
        if not name:
            return Response({"error": "Product name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            price = float(data.get("price", 0))
            stock = int(data.get("stock", 0))
            discount = int(data.get("discount_pct", 0))
        except (ValueError, TypeError):
            return Response({"error": "Invalid numeric fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Build slug
        import re
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

        doc = {
            "name": name,
            "category": (data.get("category") or "Other").strip(),
            "price": price,
            "stock_quantity": stock,
            "discount": discount,
            "unit": (data.get("unit") or "").strip(),
            "weight": (data.get("unit") or "").strip(),
            "description": (data.get("description") or "").strip(),
            "is_best_seller": bool(data.get("is_best_seller", False)),
            "is_active": bool(data.get("is_active", True)),
            "slug": slug,
            "keywords": name.lower(),
            "image_url": "",
            "images": [],
            "created_at": datetime.now(UTC),
        }

        result = db["products"].insert_one(doc)
        return Response({
            "success": True,
            "product_id": str(result.inserted_id),
            "message": f'"{name}" added successfully.',
        }, status=status.HTTP_201_CREATED)


class RestockProductView(AdminProtectedAPIView):
    """Increment stock_quantity of an existing product."""
    def post(self, request, product_id: str) -> Response:
        if self.get_admin(request) is None:
            return self.handle_unauthorized()
        from apps.market.mongo_client import get_db
        from bson import ObjectId
        db = get_db()
        if db is None:
            return Response({"error": "Database unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            qty = int(request.data.get("quantity", 0))
        except (ValueError, TypeError):
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

        if qty <= 0:
            return Response({"error": "Quantity must be positive"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            oid = ObjectId(product_id)
        except Exception:
            return Response({"error": "Invalid product ID"}, status=status.HTTP_400_BAD_REQUEST)

        product = db["products"].find_one({"_id": oid})
        if not product:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        current = product.get("stock_quantity", 0) or 0
        new_stock = current + qty
        db["products"].update_one({"_id": oid}, {"$set": {"stock_quantity": new_stock}})

        return Response({
            "success": True,
            "new_stock": new_stock,
            "message": f"Stock updated to {new_stock} units.",
        }, status=status.HTTP_200_OK)
