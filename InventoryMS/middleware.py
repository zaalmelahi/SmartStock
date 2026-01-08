import re
from django.http.request import RawPostDataException
import logging
import time
import json
import traceback
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.db import connection
from .utils.exceptions import ProjectBaseException

# Loggers
sqli_logger = logging.getLogger('security.sqli')
error_logger = logging.getLogger('error.handler')
access_logger = logging.getLogger('access.log')
perf_logger = logging.getLogger('performance.log')

class SQLInjectionProtectionMiddleware:
    # ... (existing code)
    SQL_PATTERNS = [
        r"(?i)UNION\s+SELECT",
        r"(?i)OR\s+.+?=.+",
        r"(?i)AND\s+.+?=.+",
        r"--",
        r"/\*.*?\*/",
        r"#",
        r";",
        r"(?i)DROP\s+TABLE",
        r"(?i)INSERT\s+INTO",
        r"(?i)UPDATE\s+.+?\s+SET",
        r"(?i)DELETE\s+FROM",
        r"(?i)SLEEP\(",
        r"(?i)BENCHMARK\(",
    ]

    def __init__(self, get_response):
        self.get_response = get_response
        self.compiled_patterns = [re.compile(p) for p in self.SQL_PATTERNS]

    def __call__(self, request):
        if self._is_malicious(request.GET):
            return self._record_and_block(request, "GET")
        if self._is_malicious(request.POST):
            return self._record_and_block(request, "POST")
        try:
            if request.body:
                try:
                    body_str = request.body.decode('utf-8', errors='ignore')
                    if self._is_malicious_string(body_str):
                         return self._record_and_block(request, "BODY")
                except:
                    pass
        except RawPostDataException:
            pass
        except Exception:
            pass
        return self.get_response(request)

    def _is_malicious(self, data_dict):
        for key, value in data_dict.items():
            if self._is_malicious_string(str(value)):
                return True
        return False

    def _is_malicious_string(self, value):
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                return True
        return False

    def _record_and_block(self, request, method):
        ip = self._get_client_ip(request)
        sqli_logger.warning(
            f"SQL Injection attempt detected! "
            f"IP: {ip} | Method: {method} | Path: {request.path}"
        )
        return HttpResponseForbidden("Malicious request blocked by security policy.")

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class GlobalExceptionHandlerMiddleware:
    """
    Middleware to catch all exceptions and return consistent JSON responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:
            return self.process_exception(request, exc)

    def process_exception(self, request, exc):
        # Determine status code and message
        if isinstance(exc, ProjectBaseException):
            status = exc.status_code
            message = exc.message
            payload = exc.payload
        else:
            status = 500
            message = "Internal Server Error"
            payload = None

        # Log the error
        self._log_error(request, exc, status)

        # In production, hide detailed error info for non-project exceptions
        if not settings.DEBUG and status == 500:
            message = "An unexpected error occurred. Please contact support."

        response_data = {
            "success": False,
            "error": {
                "message": message,
                "code": exc.__class__.__name__,
                "status": status,
                "payload": payload
            }
        }

        # Include traceback in debug mode
        if settings.DEBUG:
            response_data["error"]["traceback"] = traceback.format_exc()

        return JsonResponse(response_data, status=status)

    def _log_error(self, request, exc, status):
        user = request.user if request.user.is_authenticated else "Anonymous"
        ip = self._get_client_ip(request)
        
        log_msg = (
            f"Exception occurred: {exc.__class__.__name__} | "
            f"Status: {status} | User: {user} | IP: {ip} | "
            f"Path: {request.path} | Method: {request.method}\n"
            f"{traceback.format_exc()}"
        )
        
        if status >= 500:
            error_logger.error(log_msg)
        else:
            error_logger.warning(log_msg)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class RequestResponseLoggingMiddleware:
    """
    Middleware to log details of every request and response.
    """
    SENSITIVE_KEYS = {'password', 'token', 'secret', 'key', 'auth'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Log details
        self._log_access(request, response, duration)
        
        return response

    def _log_access(self, request, response, duration):
        user = request.user if request.user.is_authenticated else "Anonymous"
        ip = self._get_client_ip(request)
        
        # Scrub sensitive data from POST params
        params = self._scrub_dict(request.POST.dict()) if request.method == "POST" else {}
        
        log_data = {
            "timestamp": timezone.now().isoformat(),
            "ip": ip,
            "user": str(user),
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration": f"{duration:.3f}s",
            "params": params
        }
        
        access_logger.info(json.dumps(log_data))

    def _scrub_dict(self, data):
        scrubbed = data.copy()
        for key in scrubbed:
            if any(s in key.lower() for s in self.SENSITIVE_KEYS):
                scrubbed[key] = "********"
        return scrubbed

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class PerformanceLoggingMiddleware:
    """
    Middleware to log slow requests and slow database queries.
    """
    SLOW_REQUEST_THRESHOLD = 1.0  # seconds
    SLOW_QUERY_THRESHOLD = 0.5    # seconds

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Check for slow request
        if duration > self.SLOW_REQUEST_THRESHOLD:
            self._log_performance(request, "Slow Request", duration)
            
        # Check for slow queries
        for query in connection.queries:
            query_time = float(query.get('time', 0))
            if query_time > self.SLOW_QUERY_THRESHOLD:
                self._log_performance(request, "Slow Query", query_time, query.get('sql'))
                
        return response

    def _log_performance(self, request, type, duration, extra=None):
        log_msg = (
            f"PERFORMANCE ALERT: {type} | duration: {duration:.3f}s | "
            f"Path: {request.path} | Method: {request.method}"
        )
        if extra:
            log_msg += f" | Details: {extra}"
            
        perf_logger.warning(log_msg)
