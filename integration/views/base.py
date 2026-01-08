from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
import logging

from ..models import Application
from ..providers import WPPConnectProvider

logger = logging.getLogger(__name__)

class BaseWhatsAppView(APIView):
    """
    Base class for WhatsApp-related views to avoid code duplication.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_application(self, webhook_key):
        """
        Fetch the Application object or return a 404 response if not found.
        """
        app = get_object_or_404(Application, webhook_key=webhook_key)
        if not app.enabled:
            logger.warning("Application with webhook_key %s is disabled", webhook_key)
            raise PermissionDenied(_("Application is disabled."))
        return app

    def create_provider(self, whatsapp_provider_type, application):
        """
        Create and return the provider instance.
        """
        if whatsapp_provider_type == 'wppconnect':
            return WPPConnectProvider(application)
        # Placeholder for other providers
        return None

    def validate_request_data(self, request, required_fields):
        """
        Validate that all required fields are present in the request data.
        """
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None
