from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _
import logging

from .base import BaseWhatsAppView

logger = logging.getLogger(__name__)

class SendMessageView(BaseWhatsAppView):
    """
    View to handle sending WhatsApp messages.
    """
    def post(self, request):
        validation_error = self.validate_request_data(request, ["webhook_key", "phone", "message"])
        if validation_error:
            return validation_error
            
        webhook_key = request.data["webhook_key"]
        application = self.get_application(webhook_key)
        
        provider = self.create_provider(application.whatsapp_provider_type, application)
        if not provider:
            return Response(
                {"status": "error", "message": _("Provider not found or not supported.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        response = provider.send_whatsapp_message(
            phone=request.data.get("phone"),
            is_group=request.data.get("isGroup", False),
            is_newsletter=request.data.get("is_newsletter", False),
            message=request.data.get("message"),
        )
        
        if response.get("status") == "error":
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(response, status=status.HTTP_200_OK)

class SendFileView(BaseWhatsAppView):
    """
    View to handle sending files via WhatsApp.
    """
    def post(self, request):
        validation_error = self.validate_request_data(request, ["webhook_key", "phone", "filename", "base64"])
        if validation_error:
            return validation_error
            
        webhook_key = request.data["webhook_key"]
        application = self.get_application(webhook_key)
        
        provider = self.create_provider(application.whatsapp_provider_type, application)
        if not provider:
            return Response(
                {"status": "error", "message": _("Provider not found or not supported.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        response = provider.send_file(
            phone=request.data.get("phone"),
            is_group=request.data.get("isGroup", False),
            is_newsletter=request.data.get("is_newsletter", False),
            filename=request.data.get("filename"),
            caption=request.data.get("caption", ""),
            base64_data=request.data.get("base64"),
        )
        
        if response.get("status") == "error":
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(response, status=status.HTTP_200_OK)

class SendMenuSelectView(BaseWhatsAppView):
    """
    View to handle sending a menu selection message via WhatsApp.
    """
    def post(self, request):
        validation_error = self.validate_request_data(request, ["webhook_key", "phone", "sections"])
        if validation_error:
            return validation_error
            
        webhook_key = request.data["webhook_key"]
        application = self.get_application(webhook_key)
        
        provider = self.create_provider(application.whatsapp_provider_type, application)
        if not provider:
            return Response(
                {"status": "error", "message": _("Provider not found or not supported.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        try:
            response = provider.send_list_message(
                phone=request.data.get("phone"),
                is_group=request.data.get("isGroup", False),
                description=request.data.get("description", ""),
                sections=request.data.get("sections"),
                button_text=str(request.data.get("buttonText", _("Click here to show the list"))),
            )
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error sending menu: %s", str(e))
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
