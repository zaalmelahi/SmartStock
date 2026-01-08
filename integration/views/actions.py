from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from ..models import Application
from ..providers import WPPConnectProvider

class ApplicationActionView(LoginRequiredMixin, View):
    """Base view for application actions with feedback"""
    action_name = ""
    provider_method = ""
    
    def post(self, request, pk):
        application = get_object_or_404(Application, pk=pk)
        
        if application.whatsapp_provider_type == 'wppconnect':
            provider = WPPConnectProvider(application)
            if hasattr(provider, self.provider_method):
                method = getattr(provider, self.provider_method)
                method(request)
            else:
                messages.error(request, f"Method '{self.provider_method}' not implemented for WPPConnect.")
        else:
            # Placeholder for other providers or if no provider logic exists
            messages.info(request, f"Action '{self.action_name}' triggered for {application.name} (Provider: {application.get_whatsapp_provider_type_display()}).")
            
        return redirect('application-detail', pk=pk)

class ApplicationStartSessionView(ApplicationActionView):
    action_name = "Start Session"
    provider_method = "start_session"

class ApplicationGenerateTokenView(ApplicationActionView):
    action_name = "Generate Token"
    provider_method = "generate_token"

class ApplicationGetQRCodeView(ApplicationActionView):
    action_name = "Get QR Code"
    provider_method = "get_qrcode"

class ApplicationCheckStatusView(ApplicationActionView):
    action_name = "Check Status"
    provider_method = "check_status"

class ApplicationGetPhoneNumberView(ApplicationActionView):
    action_name = "Get Phone Number"
    provider_method = "get_phone_number"

class ApplicationCloseSessionView(ApplicationActionView):
    action_name = "Close Session"
    provider_method = "close_session"

class ApplicationRestartSessionView(ApplicationActionView):
    action_name = "Restart Session"
    provider_method = "start_session"  # Restart usually starts it if it was closed

class ApplicationCheckConnectionView(ApplicationActionView):
    action_name = "Check Connection"
    provider_method = "check_connection_session"

class ApplicationSyncContactsView(ApplicationActionView):
    action_name = "Sync Contacts"
    provider_method = "sync_contacts"

class ApplicationSyncMessagesView(ApplicationActionView):
    action_name = "Sync Messages"
    provider_method = "sync_messages"
