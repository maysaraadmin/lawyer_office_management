import json
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests and responses.
    """
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        # Log request
        request.start_time = time.time()
        
        # Skip logging for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return self.get_response(request)
            
        # Log request details
        request_body = {}
        if request.body:
            try:
                request_body = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                request_body = {'raw_body': str(request.body)}
        
        log_data = {
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'headers': dict(request.headers),
            'body': request_body,
            'user': str(request.user) if hasattr(request, 'user') else None,
            'ip': self._get_client_ip(request),
        }
        
        logger.info("Request received", extra={'request': log_data})
        
        # Process the request and get the response
        response = self.get_response(request)
        
        # Calculate response time
        response_time = time.time() - request.start_time
        
        # Log response details
        response_body = {}
        if hasattr(response, 'data'):
            response_body = response.data
        
        log_data.update({
            'status_code': response.status_code,
            'response': response_body,
            'response_time_seconds': round(response_time, 4),
        })
        
        # Log at different levels based on status code
        if 400 <= response.status_code < 500:
            logger.warning(
                "Client error response", 
                extra={'response': log_data}
            )
        elif response.status_code >= 500:
            logger.error(
                "Server error response", 
                extra={'response': log_data}
            )
        else:
            logger.info(
                "Response sent", 
                extra={'response': log_data}
            )
        
        return response
    
    def _get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
