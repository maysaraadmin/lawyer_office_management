import httpx
import asyncio
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.auth_token: Optional[str] = None
        self.timeout = 30.0
    
    def set_auth_token(self, token: Optional[str]):
        """Set authentication token"""
        self.auth_token = token
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        return headers
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and return auth data"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/auth/login/",
                json={"email": email, "password": password},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get user profile"""
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/auth/profile/",
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def update_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/api/auth/profile/",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/dashboard/stats/",
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def get_appointments(self, 
                              status: Optional[str] = None,
                              date_from: Optional[str] = None,
                              date_to: Optional[str] = None,
                              client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get appointments with optional filters"""
        headers = self._get_headers()
        params = {}
        
        if status and status != "All":
            params["status"] = status
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if client_id:
            params["client_id"] = client_id
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/appointments/",
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def create_appointment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new appointment"""
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/appointments/",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def update_appointment(self, appointment_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update appointment"""
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/api/appointments/{appointment_id}/",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_appointment(self, appointment_id: str) -> bool:
        """Delete appointment"""
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api/appointments/{appointment_id}/",
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
    
    async def get_clients(self, 
                         search: Optional[str] = None,
                         is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get clients with optional filters"""
        headers = self._get_headers()
        params = {}
        
        if search:
            params["search"] = search
        if is_active is not None:
            params["is_active"] = is_active
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clients/",
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def get_client(self, client_id: str) -> Dict[str, Any]:
        """Get specific client details"""
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/clients/{client_id}/",
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def create_client(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new client"""
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/clients/",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def update_client(self, client_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update client"""
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/api/clients/{client_id}/",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def get_cases(self, 
                       client_id: Optional[str] = None,
                       status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get legal cases with optional filters"""
        headers = self._get_headers()
        params = {}
        
        if client_id:
            params["client_id"] = client_id
        if status:
            params["status"] = status
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/cases/",
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def create_case(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new case"""
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/cases/",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def update_case(self, case_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update case"""
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/api/cases/{case_id}/",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

class MockAPIClient:
    """Mock API client for testing without backend"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.auth_token: Optional[str] = None
    
    def set_auth_token(self, token: Optional[str]):
        """Set authentication token"""
        self.auth_token = token
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Mock login"""
        await asyncio.sleep(1)  # Simulate network delay
        
        if email == "test@example.com" and password == "password":
            return {
                "access_token": "mock_token_12345",
                "refresh_token": "mock_refresh_token",
                "user": {
                    "id": 1,
                    "email": "test@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "user_type": "lawyer",
                    "user_type_display": "Lawyer",
                    "phone": "+1234567890",
                    "address": "123 Main St, City, State",
                    "date_joined": "2023-01-01T10:00:00Z",
                    "last_login": "2024-01-01T10:00:00Z"
                }
            }
        else:
            raise httpx.HTTPStatusError(
                "Invalid credentials",
                request=httpx.Request("POST", "http://localhost:8000/api/auth/login/"),
                response=httpx.Response(401)
            )
    
    async def get_profile(self) -> Dict[str, Any]:
        """Mock get profile"""
        await asyncio.sleep(0.5)
        return {
            "id": 1,
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "lawyer",
            "user_type_display": "Lawyer",
            "phone": "+1234567890",
            "address": "123 Main St, City, State",
            "date_joined": "2023-01-01T10:00:00Z",
            "last_login": "2024-01-01T10:00:00Z"
        }
    
    async def update_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock update profile"""
        await asyncio.sleep(0.5)
        profile = await self.get_profile()
        profile.update(data)
        return profile
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Mock dashboard stats"""
        await asyncio.sleep(0.5)
        return {
            "total_clients": 156,
            "active_cases": 42,
            "today_appointments": 8,
            "pending_tasks": 23,
            "recent_appointments": [
                {
                    "id": 1,
                    "title": "Client Consultation",
                    "client_name": "Alice Johnson",
                    "date": "2024-01-15",
                    "time": "10:00 AM",
                    "status": "scheduled"
                },
                {
                    "id": 2,
                    "title": "Case Review",
                    "client_name": "Bob Smith",
                    "date": "2024-01-15",
                    "time": "2:00 PM",
                    "status": "confirmed"
                }
            ],
            "upcoming_deadlines": [
                {
                    "id": 1,
                    "title": "File Motion",
                    "case_name": "Smith vs. Jones",
                    "due_date": "2024-01-20",
                    "priority": "high"
                }
            ]
        }
    
    async def get_appointments(self, **kwargs) -> List[Dict[str, Any]]:
        """Mock get appointments"""
        await asyncio.sleep(0.5)
        return [
            {
                "id": 1,
                "title": "Client Consultation",
                "client_name": "Alice Johnson",
                "date": "2024-01-15",
                "time": "10:00 AM",
                "status": "scheduled",
                "notes": "Initial consultation"
            },
            {
                "id": 2,
                "title": "Case Review",
                "client_name": "Bob Smith",
                "date": "2024-01-15",
                "time": "2:00 PM",
                "status": "confirmed",
                "notes": "Review case progress"
            },
            {
                "id": 3,
                "title": "Court Appearance",
                "client_name": "Carol Davis",
                "date": "2024-01-16",
                "time": "9:00 AM",
                "status": "scheduled",
                "notes": "Motion hearing"
            }
        ]
    
    async def get_clients(self, **kwargs) -> List[Dict[str, Any]]:
        """Mock get clients"""
        await asyncio.sleep(0.5)
        return [
            {
                "id": 1,
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "phone": "+1234567890",
                "is_active": True,
                "total_cases": 3,
                "active_cases": 1
            },
            {
                "id": 2,
                "name": "Bob Smith",
                "email": "bob@example.com",
                "phone": "+0987654321",
                "is_active": True,
                "total_cases": 2,
                "active_cases": 2
            },
            {
                "id": 3,
                "name": "Carol Davis",
                "email": "carol@example.com",
                "phone": "+1122334455",
                "is_active": False,
                "total_cases": 1,
                "active_cases": 0
            }
        ]
