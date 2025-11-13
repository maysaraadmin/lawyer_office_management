import os
import json
import httpx
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class APIClient:
    """
    API client for communicating with the Lawyer Office backend
    """
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv(
            "API_BASE_URL", 
            "http://localhost:8000/api"
        )
        self.client = httpx.AsyncClient()
        self._token = None
        self._refresh_token = None
        self._token_expiry = None
        self._auth_header = {}
    
    @property
    def token(self) -> Optional[str]:
        return self._token
    
    @token.setter
    def token(self, value: str):
        self._token = value
        if value:
            self._auth_header = {"Authorization": f"Bearer {value}"}
        else:
            self._auth_header = {}
    
    @property
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated and token is not expired"""
        if not self.token:
            return False
        
        if self._token_expiry and datetime.now() < self._token_expiry:
            return True
            
        return False
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        files: Optional[Dict] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Prepare headers
        request_headers = {}
        if require_auth and self.is_authenticated:
            request_headers.update(self._auth_header)
        
        if headers:
            request_headers.update(headers)
        
        # Prepare request data
        json_data = None
        if data and not files:
            json_data = data
            if 'Content-Type' not in request_headers:
                request_headers['Content-Type'] = 'application/json'
        
        try:
            # Make the request
            response = await self.client.request(
                method=method.upper(),
                url=url,
                json=json_data,
                data=data if files else None,
                files=files,
                params=params,
                headers=request_headers,
                timeout=30.0,
            )
            
            # Handle token refresh on 401
            if response.status_code == 401 and require_auth and self._refresh_token:
                refresh_success = await self.refresh_token()
                if refresh_success:
                    # Retry the request with the new token
                    return await self._request(
                        method, endpoint, data, params, headers, files, require_auth
                    )
            
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204:  # No Content
                return {"status": "success", "message": "Operation completed successfully"}
                
            # Parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "message": "Invalid JSON response",
                    "raw_response": response.text
                }
                
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors
            error_detail = {"status_code": e.response.status_code}
            try:
                error_detail.update(e.response.json())
            except:
                error_detail["detail"] = e.response.text
                
            logger.error(
                f"API request failed: {method} {url} - {e.response.status_code}",
                extra={"error": error_detail}
            )
            
            return {
                "status": "error",
                "message": f"HTTP {e.response.status_code}: {e.response.text}",
                "error": error_detail,
                "status_code": e.response.status_code
            }
            
        except Exception as e:
            # Handle other errors
            logger.exception(f"API request failed: {method} {url}")
            return {
                "status": "error",
                "message": str(e),
                "error": {"detail": str(e)}
            }
    
    # Authentication methods
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and get an access token
        """
        data = {"email": email, "password": password}
        response = await self._request(
            "POST", 
            "auth/token/", 
            data=data, 
            require_auth=False
        )
        
        if response.get("access"):
            self.token = response["access"]
            self._refresh_token = response.get("refresh")
            
            # Set token expiry (default to 5 minutes if not provided)
            expires_in = response.get("expires_in", 300)
            self._token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            # Store user data
            user_response = await self._request("GET", "auth/me/")
            if user_response.get("status") == "success":
                self._user = user_response.get("data", {})
            
            return {
                "status": "success",
                "message": "Login successful",
                "user": self._user,
                "tokens": {
                    "access": self.token,
                    "refresh": self._refresh_token,
                    "expires_in": expires_in
                }
            }
        
        return response
    
    async def refresh_token(self) -> bool:
        """
        Refresh the access token using the refresh token
        Returns True if successful, False otherwise
        """
        if not self._refresh_token:
            return False
            
        try:
            response = await self._request(
                "POST",
                "auth/token/refresh/",
                data={"refresh": self._refresh_token},
                require_auth=False
            )
            
            if response.get("access"):
                self.token = response["access"]
                
                # Update token expiry
                expires_in = response.get("expires_in", 300)
                self._token_expiry = datetime.now() + timedelta(seconds=expires_in)
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to refresh token: {str(e)}")
            
        return False
    
    async def logout(self):
        """
        Log out the current user
        """
        # Invalidate tokens on the server if needed
        if self._refresh_token:
            try:
                await self._request(
                    "POST",
                    "auth/token/blacklist/",
                    data={"refresh": self._refresh_token}
                )
            except Exception as e:
                logger.warning(f"Error during logout: {str(e)}")
        
        # Clear local authentication state
        self.token = None
        self._refresh_token = None
        self._token_expiry = None
        self._user = None
    
    # User methods
    async def get_current_user(self) -> Dict[str, Any]:
        """
        Get the current authenticated user's profile
        """
        return await self._request("GET", "auth/me/")
    
    # Case methods
    async def get_cases(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get a list of cases with optional filtering
        """
        return await self._request("GET", "cases/", params=params)
    
    async def get_case(self, case_id: str) -> Dict[str, Any]:
        """
        Get a single case by ID
        """
        return await self._request("GET", f"cases/{case_id}/")
    
    async def create_case(self, case_data: Dict) -> Dict[str, Any]:
        """
        Create a new case
        """
        return await self._request("POST", "cases/", data=case_data)
    
    # Appointment methods
    async def get_appointments(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get a list of appointments with optional filtering
        """
        return await self._request("GET", "appointments/", params=params)
    
    async def create_appointment(self, appointment_data: Dict) -> Dict[str, Any]:
        """
        Create a new appointment
        """
        return await self._request("POST", "appointments/", data=appointment_data)
    
    # Document methods
    async def upload_document(self, file_path: str, case_id: str) -> Dict[str, Any]:
        """
        Upload a document for a case
        """
        try:
            with open(file_path, "rb") as f:
                files = {
                    "file": (os.path.basename(file_path), f, "application/octet-stream"),
                    "case": (None, case_id),
                }
                
                return await self._request(
                    "POST",
                    "documents/upload/",
                    files=files,
                    headers={"Content-Type": "multipart/form-data"}
                )
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to upload file: {str(e)}"
            }
    
    async def close(self):
        """
        Close the HTTP client
        """
        await self.client.aclose()

# Singleton instance
api_client = APIClient()
