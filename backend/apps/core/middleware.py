import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all incoming requests and responses.
    """
    
    def process_request(self, request):
        # Store the start time for the request
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # Calculate request processing time
        total_time = time.time() - request.start_time
        
        # Prepare log data
        log_data = {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'response_time': total_time,
            'user': str(request.user) if hasattr(request, 'user') else 'anonymous',
            'remote_addr': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'query_params': dict(request.GET),
        }
        
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
