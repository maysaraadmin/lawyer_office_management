"""
API utility functions for making HTTP requests to the backend.
This module provides a clean interface for making API calls and handling responses.
"""
import json
import logging
from typing import Any, Dict, List, Optional, Union
import httpx
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base exception for API-related errors"""
    def __init__(self, message: str, status_code: int = None, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class APIClient:
    """HTTP client for making API requests with authentication and error handling"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize the API client
        
        Args:
            base_url: Base URL of the API (e.g., 'http://localhost:8000/api/')
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/') + '/'
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.access_token = None
        self.refresh_token = None
    
    async def _get_headers(self, headers: Optional[Dict] = None) -> Dict:
        """Get headers with authorization if available"""
        headers = headers or {}
        headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
            
        return headers
    
    async def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response and raise appropriate exceptions"""
        try:
            response.raise_for_status()
            try:
                return response.json() if response.content else {}
            except ValueError as json_err:
                logger.error(f"Failed to parse JSON response: {json_err}")
                return {'detail': 'Invalid JSON response from server'}
                
        except httpx.HTTPStatusError as e:
            error_detail = {'detail': str(e)}
            try:
                if e.response.content:
                    error_detail = e.response.json()
                    if isinstance(error_detail, str):
                        error_detail = {'detail': error_detail}
            except Exception as parse_err:
                logger.error(f"Failed to parse error response: {parse_err}")
                error_detail = {'detail': f'HTTP {e.response.status_code}: {e.response.text[:200]}'}
                
            # Log the error
            logger.error(f"API Error: {error_detail}")
            raise APIError(
                error_detail.get('detail', 'An error occurred'),
                status_code=e.response.status_code,
                details=error_detail
            )
    
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Any = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        files: Any = None,
        json_encoder=None
    ) -> Any:
        """Make an HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (e.g., 'cases/1/')
            data: Request body data
            params: Query parameters
            headers: Additional headers
            files: Files to upload (for multipart/form-data)
            json_encoder: Custom JSON encoder for request data
            
        Returns:
            Parsed JSON response or raises APIError
        """
        if not endpoint:
            raise ValueError("Endpoint cannot be empty")
            
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        headers = await self._get_headers(headers)
        
        # Prepare request data
        json_data = None
        if data is not None and files is None:
            if not isinstance(data, (str, bytes)):
                json_data = json.dumps(data, default=self._json_serializer, cls=json_encoder)
            else:
                json_data = data
        
        # Log the request
        logger.debug(f"Making {method.upper()} request to {url}")
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                json=json_data if json_data is not None else None,
                data=data if files is not None else None,
                files=files,
                timeout=self.timeout,
            )
            return await self._handle_response(response)
            
        except httpx.RequestError as e:
            error_msg = f"Network error while making {method.upper()} request to {url}: {str(e)}"
            logger.error(error_msg)
            raise APIError("Unable to connect to the server. Please check your internet connection.")
            
        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}", exc_info=True)
            raise APIError(f"An unexpected error occurred: {str(e)}")
    
    @staticmethod
    def _json_serializer(obj):
        """JSON serializer for objects not serializable by default"""
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    async def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Any:
        """Make a GET request"""
        return await self.request('GET', endpoint, params=params, **kwargs)
    
    async def post(self, endpoint: str, data: Any = None, **kwargs) -> Any:
        """Make a POST request"""
        return await self.request('POST', endpoint, data=data, **kwargs)
    
    async def put(self, endpoint: str, data: Any = None, **kwargs) -> Any:
        """Make a PUT request"""
        return await self.request('PUT', endpoint, data=data, **kwargs)
    
    async def patch(self, endpoint: str, data: Any = None, **kwargs) -> Any:
        """Make a PATCH request"""
        return await self.request('PATCH', endpoint, data=data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Any:
        """Make a DELETE request"""
        return await self.request('DELETE', endpoint, **kwargs)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Create a singleton instance
api_client = APIClient("http://localhost:8000/api/")
