from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    def get(self, request) -> Response:
        return Response({"status": "ok", "service": "grocery-admin-api"}, status=status.HTTP_200_OK)
