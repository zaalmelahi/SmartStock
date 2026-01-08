from django.contrib.sessions.models import Session
from django.conf import settings
from django.contrib.auth import logout
from django.utils import timezone

class ConcurrentSessionMiddleware:
    """
    Middleware to prevent multiple concurrent sessions for the same user.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_session_key = request.session.session_key
            
            # Find all active sessions for this user
            sessions = Session.objects.filter(expire_date__gte=timezone.now())
            
            for session in sessions:
                data = session.get_decoded()
                if str(data.get('_auth_user_id')) == str(request.user.id):
                    if session.session_key != current_session_key:
                        session.delete()
        
        response = self.get_response(request)
        return response

class SessionSecurityMiddleware:
    """
    Middleware to enforce additional session security measures.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure session is tied to IP address (optional but recommended for hijacking prevention)
        if request.user.is_authenticated:
            user_ip = request.META.get('REMOTE_ADDR')
            if 'user_ip' not in request.session:
                request.session['user_ip'] = user_ip
            elif request.session['user_ip'] != user_ip:
                logout(request)
                # You might want to add a message here
        
        response = self.get_response(request)
        return response
