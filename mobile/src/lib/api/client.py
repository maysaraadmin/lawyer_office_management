import os
import json
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class APIClient:
    """
    API client for communicating with the Lawyer Office backend
    """
    
    def __init__(self, base_url: str = None, token: str = None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000/api")
        self.token = token
        self.client = httpx.AsyncClient()
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors
            error_detail = {"status_code": e.response.status_code}
            try:
                error_detail.update(e.response.json())
            except:
                error_detail["detail"] = e.response.text
            return {"status": "error", "message": str(e), "error": error_detail}
        except Exception as e:
            # Handle other errors
            return {"status": "error", "message": str(e)}
    
    # Authentication methods
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and get an access token
        """
        data = {"email": email, "password": password}
        response = await self._request("POST", "auth/token/", data=data)
        if "access" in response:
            self.token = response["access"]
            self.headers["Authorization"] = f"Bearer {self.token}"
        return response
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token
        """
        data = {"refresh": refresh_token}
        response = await self._request("POST", "auth/token/refresh/", data=data)
        if "access" in response:
            self.token = response["access"]
            self.headers["Authorization"] = f"Bearer {self.token}"
        return response
    
    # User methods
    async def get_current_user(self) -> Dict[str, Any]:
        """
        Get the current authenticated user's profile
        """
        return await self._request("GET", "auth/me/")
    
    # Case methods
    async def get_cases(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get a list of cases
        """
        return await self._request("GET", "cases/", params=params)
    
    async def get_case(self, case_id: str) -> Dict[str, Any]:
        """
        Get a single case by ID
        """
        return await self._request("GET", f"cases/{case_id}/")
    
    # Appointment methods
    async def get_appointments(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get a list of appointments
        """
        return await self._request("GET", "appointments/", params=params)
    
    async def create_appointment(self, data: Dict) -> Dict[str, Any]:
        """
        Create a new appointment
        """
        return await self._request("POST", "appointments/", data=data)
    
    # Document methods
    async def upload_document(self, file_path: str, case_id: str) -> Dict[str, Any]:
        """
        Upload a document for a case
        """
        url = f"{self.base_url.rstrip('/')}/documents/"
        
        try:
            with open(file_path, "rb") as f:
                files = {
                    "file": (os.path.basename(file_path), f, "application/octet-stream"),
                    "case": (None, case_id),
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        files=files,
                        headers={"Authorization": self.headers.get("Authorization")},
                    )
                    response.raise_for_status()
                    return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # Close the client
    async def close(self):
        """
        Close the HTTP client
        """
        await self.client.aclose()
