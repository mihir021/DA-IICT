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
