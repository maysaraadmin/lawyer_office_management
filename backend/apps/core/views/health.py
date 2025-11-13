from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class HealthCheckView(APIView):
    """
    A simple health check endpoint that returns the status of the API.
    """
    permission_classes = []  # No authentication required
    
    def get(self, request, *args, **kwargs):
        return Response(
            {
                'status': 'healthy',
                'service': 'lawyer-office-management-api',
                'version': '1.0.0'
            },
            status=status.HTTP_200_OK
        )
