import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class APIClient:
    """Client for communicating with the Django backend API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/v1"):
        self.base_url = base_url.rstrip('/')
        self.access_token: Optional[str] = None
        
    def set_auth_token(self, token: str):
        """Set the authentication token for API requests"""
        self.access_token = token
        
    def clear_auth_token(self):
        """Clear the authentication token"""
        self.access_token = None
    
    async def _get_client(self):
        """Get a new async client for each request"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers=headers
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate with the backend and return access token"""
        client = None
        try:
            client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                headers={"Content-Type": "application/json"}
            )
            response = await client.post(
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
            logger.error(f"Login HTTP error: {str(e)}")
            raise Exception(f"Login failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected login error: {str(e)}")
            raise
        finally:
            if client:
                await client.aclose()
    
    async def get_appointments(self) -> List[Dict[str, Any]]:
        """Get all appointments for the current user"""
        client = None
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
            
            client = await self._get_client()
            response = await client.get("/appointments/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Get appointments error: {str(e)}")
            # Return empty list if API is not available
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting appointments: {str(e)}")
            return []
        finally:
            if client:
                await client.aclose()
    
    async def get_clients(self) -> List[Dict[str, Any]]:
        """Get all clients for the current user"""
        client = None
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
            
            client = await self._get_client()
            response = await client.get("/clients/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Get clients error: {str(e)}")
            # Return empty list if API is not available
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting clients: {str(e)}")
            return []
        finally:
            if client:
                await client.aclose()
    
    async def create_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new appointment"""
        client = None
        try:
            if not self.access_token:
                logger.error("No access token - not authenticated")
                raise Exception("Not authenticated")
            
            logger.info(f"Posting to /appointments/ with data: {appointment_data}")
            
            client = await self._get_client()
            response = await client.post("/appointments/", json=appointment_data)
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
        finally:
            if client:
                await client.aclose()
    
    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new client"""
        client = None
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
            
            client = await self._get_client()
            response = await client.post("/clients/", json=client_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Create client error: {str(e)}")
            raise Exception(f"Failed to create client: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating client: {str(e)}")
            raise
        finally:
            if client:
                await client.aclose()
    
    async def update_appointment(self, appointment_id: int, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing appointment"""
        client = None
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
            
            client = await self._get_client()
            response = await client.put(f"/appointments/{appointment_id}/", json=appointment_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Update appointment error: {str(e)}")
            raise Exception(f"Failed to update appointment: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating appointment: {str(e)}")
            raise
        finally:
            if client:
                await client.aclose()
    
    async def delete_appointment(self, appointment_id: int) -> bool:
        """Delete an appointment"""
        client = None
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
            
            client = await self._get_client()
            response = await client.delete(f"/appointments/{appointment_id}/")
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            logger.error(f"Delete appointment error: {str(e)}")
            raise Exception(f"Failed to delete appointment: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting appointment: {str(e)}")
            raise
        finally:
            if client:
                await client.aclose()
    
    async def get_appointment_stats(self) -> Dict[str, Any]:
        """Get appointment statistics"""
        client = None
        try:
            if not self.access_token:
                raise Exception("Not authenticated")
            
            client = await self._get_client()
            response = await client.get("/appointments/stats/")
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
        finally:
            if client:
                await client.aclose()
    
    async def aclose(self):
        """Close method for compatibility - no-op since we create clients per request"""
        pass

# Global API client instance
api_client = APIClient()
