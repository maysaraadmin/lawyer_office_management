import json
import logging
from typing import Any, Dict, Optional, Union
import httpx
from datetime import datetime, timedelta
from jose import jwt, JWTError
from pathlib import Path
import os

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIClient:
    """HTTP client for making requests to the Django REST API"""
    
    def __init__(self):
        self.base_url = Config.API_BASE_URL.rstrip('/') + '/'
        self.timeout = Config.API_TIMEOUT
        self.access_token = None
        self.refresh_token = None
        self.client = httpx.AsyncClient()
    
    async def _get_headers(self, headers: Optional[Dict] = None) -> Dict:
        """Get headers with authorization if available"""
        if headers is None:
            headers = {}
        
        headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        return headers
    
    async def _handle_response(self, response: httpx.Response):
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
            raise Exception(error_detail.get('detail', 'An error occurred'))
    
    async def request(self, method: str, endpoint: str, **kwargs):
        """Make an HTTP request to the API with enhanced error handling"""
        if not endpoint:
            raise ValueError("Endpoint cannot be empty")
            
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        headers = await self._get_headers(kwargs.pop('headers', {}))
        
        # Add request logging
        logger.debug(f"Making {method.upper()} request to {url}")
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            return await self._handle_response(response)
            
        except httpx.RequestError as e:
            error_msg = f"Network error while making {method.upper()} request to {url}: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError("Unable to connect to the server. Please check your internet connection.")
            
        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}", exc_info=True)
            raise Exception("Unable to connect to the server. Please check your internet connection.")
    
    async def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Any:
        """Make a GET request"""
        return await self.request('GET', endpoint, params=params, **kwargs)
    
    async def post(self, endpoint: str, data: Any = None, **kwargs) -> Any:
        """Make a POST request"""
        if data is not None and not isinstance(data, (str, bytes)):
            data = json.dumps(data, default=self._json_serializer)
        return await self.request('POST', endpoint, content=data, **kwargs)
    
    async def put(self, endpoint: str, data: Any = None, **kwargs) -> Any:
        """Make a PUT request"""
        if data is not None and not isinstance(data, (str, bytes)):
            data = json.dumps(data, default=self._json_serializer)
        return await self.request('PUT', endpoint, content=data, **kwargs)
    
    async def patch(self, endpoint: str, data: Any = None, **kwargs) -> Any:
        """Make a PATCH request"""
        if data is not None and not isinstance(data, (str, bytes)):
            data = json.dumps(data, default=self._json_serializer)
        return await self.request('PATCH', endpoint, content=data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Any:
        """Make a DELETE request"""
        return await self.request('DELETE', endpoint, **kwargs)
    
    def _json_serializer(self, obj):
        """JSON serializer for objects not serializable by default"""
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class AuthService:
    """Authentication service for handling JWT tokens with enhanced security"""
    
    def __init__(self, api_client: APIClient):
        if not api_client:
            raise ValueError("API client is required")
            
        self.api_client = api_client
        self.token_file = Path.home() / '.lawyer_office_auth.json'  # Store in user's home directory
        self._load_tokens()
    
    def _load_tokens(self):
        """Securely load tokens from file if they exist"""
        if not self.token_file.exists():
            return
            
        try:
            # Read with restricted permissions
            self.token_file.chmod(0o600)  # Only owner can read/write
            with open(self.token_file, 'r') as f:
                tokens = json.load(f)
                
                # Validate token format
                if not all(key in tokens for key in ['access_token', 'refresh_token']):
                    logger.warning("Invalid token format in auth file")
                    self._clear_tokens()
                    return
                    
                # Set tokens
                self.api_client.access_token = tokens.get('access_token')
                self.api_client.refresh_token = tokens.get('refresh_token')
                
                # Verify tokens are not expired
                if self._is_token_expired(self.api_client.access_token):
                    logger.info("Access token expired, attempting refresh...")
                    asyncio.create_task(self.refresh_access_token())
                    
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in auth file: {e}")
            self._clear_tokens()
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
            self._clear_tokens()
    
    def _save_tokens(self):
        """Securely save tokens to file"""
        if not self.api_client.access_token or not self.api_client.refresh_token:
            self._clear_tokens()
            return
            
        try:
            # Create parent directory if it doesn't exist
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write with restricted permissions
            with open(self.token_file, 'w') as f:
                json.dump({
                    'access_token': self.api_client.access_token,
                    'refresh_token': self.api_client.refresh_token,
                    'timestamp': datetime.utcnow().isoformat()
                }, f)
                
            # Set file permissions to read/write for owner only
            self.token_file.chmod(0o600)
            
        except Exception as e:
            logger.error(f"Error saving tokens: {e}")
            # Don't raise to prevent login failure just because of token saving
    
    def _clear_tokens(self):
        """Securely clear tokens from memory and storage"""
        # Overwrite tokens in memory before deletion
        if self.api_client.access_token:
            self.api_client.access_token = None
        if self.api_client.refresh_token:
            self.api_client.refresh_token = None
            
        # Securely delete the token file if it exists
        if self.token_file.exists():
            try:
                # Overwrite file with random data before deletion
                with open(self.token_file, 'wb') as f:
                    f.write(os.urandom(1024))
                self.token_file.unlink()
            except Exception as e:
                logger.error(f"Error securely removing token file: {e}")
    
    def _is_token_expired(self, token: str) -> bool:
        """Check if a JWT token is expired"""
        if not token:
            return True
            
        try:
            # Decode without verification to check expiration
            payload = jwt.get_unverified_claims(token)
            exp = payload.get('exp')
            if not exp:
                return True
                
            # Check if token is expired (with 30 second leeway)
            return datetime.utcnow().timestamp() > (exp - 30)
            
        except Exception as e:
            logger.warning(f"Error checking token expiration: {e}")
            return True
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.api_client.access_token is not None
    
    async def login(self, email: str, password: str) -> tuple[bool, str]:
        """
        Login with email and password
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not email or not password:
            return False, "Email and password are required"
            
        # Basic email validation
        if '@' not in email or '.' not in email:
            return False, "Please enter a valid email address"
            
        try:
            # Add rate limiting check here if needed
            
            # Make the login request
            response = await self.api_client.post('users/token/', {
                'email': email.strip().lower(),
                'password': password
            })
            
            # Validate response
            if not response or 'access' not in response or 'refresh' not in response:
                return False, "Invalid response from server"
            
            # Update tokens
            self.api_client.access_token = response['access']
            self.api_client.refresh_token = response['refresh']
            
            # Save tokens securely
            self._save_tokens()
            
            logger.info(f"User {email} logged in successfully")
            return True, "Login successful"
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return False, "Invalid email or password"
            return False, f"Authentication failed: {e.response.text}"
            
        except httpx.RequestError as e:
            logger.error(f"Network error during login: {str(e)}")
            return False, "Unable to connect to the server. Please check your internet connection."
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return False, f"An unexpected error occurred: {str(e)}"
    
    async def refresh_access_token(self) -> bool:
        """
        Refresh access token using refresh token
        
        Returns:
            bool: True if token was refreshed successfully, False otherwise
        """
        if not self.api_client.refresh_token:
            logger.debug("No refresh token available")
            return False
            
        # Check if refresh token is expired
        if self._is_token_expired(self.api_client.refresh_token):
            logger.warning("Refresh token has expired")
            self._clear_tokens()
            return False
            
        try:
            logger.debug("Attempting to refresh access token")
            
            response = await self.api_client.post('users/token/refresh/', {
                'refresh': self.api_client.refresh_token
            })
            
            if not response or 'access' not in response:
                logger.error("Invalid response when refreshing token")
                self._clear_tokens()
                return False
                
            # Update access token
            self.api_client.access_token = response['access']
            
            # Update refresh token if a new one was provided
            if 'refresh' in response:
                self.api_client.refresh_token = response['refresh']
                
            # Save the new tokens
            self._save_tokens()
            
            logger.debug("Successfully refreshed access token")
            return True
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:  # Unauthorized
                logger.warning("Refresh token is invalid or expired")
                self._clear_tokens()
            else:
                logger.error(f"Error refreshing token: {e.response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error refreshing token: {str(e)}", exc_info=True)
            return False
    
    def logout(self):
        """Logout the current user"""
        self._clear_tokens()
    
    async def register(self, user_data: Dict) -> bool:
        """Register a new user"""
        try:
            response = await self.api_client.post('users/register/', user_data)
            return True
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            raise


# Global API client and auth service instances
api_client = APIClient()
auth_service = AuthService(api_client)
