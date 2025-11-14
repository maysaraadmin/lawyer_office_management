import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class APIClient:
    """Client for communicating with the Django backend API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/v1"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
        self.access_token: Optional[str] = None
        
    def set_auth_token(self, token: str):
        """Set the authentication token for API requests"""
        self.access_token = token
        self.client.headers.update({"Authorization": f"Bearer {token}"})
        
    def clear_auth_token(self):
        """Clear the authentication token"""
        self.access_token = None
        if "Authorization" in self.client.headers:
            del self.client.headers["Authorization"]
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate with the backend and return access token"""
        try:
            response = self.client.post(
                "/auth/login/",
                json={"email": email, "password": password}
            )
            response.raise_for_status()
            data = response.json()
            
            # Set the token if login successful
            if "access" in data:
                self.set_auth_token(data["access"])
                
            return data
        except httpx.HTTPError as e:
            logger.error(f"Login error: {str(e)}")
            raise Exception(f"Login failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected login error: {str(e)}")
            raise
    
    async def get_current_user(self) -> Dict[str, Any]:
        """Get current user information"""
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
                
            response = self.client.get("/auth/user/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Get current user error: {str(e)}")
            raise Exception(f"Failed to get user data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting user: {str(e)}")
            raise
    
    async def get_appointments(self) -> List[Dict[str, Any]]:
        """Get all appointments for the current user"""
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
                
            response = self.client.get("/appointments/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Get appointments error: {str(e)}")
            # Return empty list if API is not available
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting appointments: {str(e)}")
            return []
    
    async def get_clients(self) -> List[Dict[str, Any]]:
        """Get all clients for the current user"""
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
                
            response = self.client.get("/clients/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Get clients error: {str(e)}")
            # Return empty list if API is not available
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting clients: {str(e)}")
            return []
    
    async def create_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new appointment"""
        try:
            if not self.access_token:
                logger.error("No access token - not authenticated")
                raise Exception("Not authenticated")
            
            logger.info(f"Posting to /appointments/ with data: {appointment_data}")
            logger.info(f"Authorization header: {self.client.headers.get('Authorization')}")
                
            response = self.client.post("/appointments/", json=appointment_data)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response text: {response.text}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Create appointment error: {str(e)}")
            raise Exception(f"Failed to create appointment: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating appointment: {str(e)}")
            raise
    
    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new client"""
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
                
            response = self.client.post("/clients/", json=client_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Create client error: {str(e)}")
            raise Exception(f"Failed to create client: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating client: {str(e)}")
            raise
    
    async def update_appointment(self, appointment_id: int, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing appointment"""
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
                
            response = self.client.put(f"/appointments/{appointment_id}/", json=appointment_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Update appointment error: {str(e)}")
            raise Exception(f"Failed to update appointment: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating appointment: {str(e)}")
            raise
    
    async def delete_appointment(self, appointment_id: int) -> bool:
        """Delete an appointment"""
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
                
            response = self.client.delete(f"/appointments/{appointment_id}/")
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            logger.error(f"Delete appointment error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting appointment: {str(e)}")
            return False
    
    async def get_appointment_stats(self) -> Dict[str, Any]:
        """Get appointment statistics"""
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
                
            response = self.client.get("/appointments/stats/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Get appointment stats error: {str(e)}")
            # Return default stats if API is not available
            return {
                "total": 0,
                "upcoming": 0,
                "completed": 0,
                "cancelled": 0
            }
        except Exception as e:
            logger.error(f"Unexpected error getting appointment stats: {str(e)}")
            return {
                "total": 0,
                "upcoming": 0,
                "completed": 0,
                "cancelled": 0
            }
    
    def close(self):
        """Close the HTTP client"""
        if self.client:
            self.client.close()

# Global API client instance
api_client = APIClient()
