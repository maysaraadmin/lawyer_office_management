import json
import httpx
from .config import Config
from typing import Optional, Dict, Any, Union

class APIClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or Config.API_BASE_URL
        self.client = httpx.AsyncClient()
        self.token = None
        self.refresh_token = None

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Prepare headers
        request_headers = Config.get_auth_headers(self.token)
        if headers:
            request_headers.update(headers)
        
        # Make the request
        try:
            if method.upper() == 'GET':
                response = await self.client.get(
                    url, params=params, headers=request_headers
                )
            elif method.upper() == 'POST':
                if files:
                    response = await self.client.post(
                        url, data=data, files=files, headers=request_headers
                    )
                else:
                    response = await self.client.post(
                        url, json=data, headers=request_headers
                    )
            elif method.upper() == 'PUT':
                response = await self.client.put(
                    url, json=data, headers=request_headers
                )
            elif method.upper() == 'DELETE':
                response = await self.client.delete(
                    url, headers=request_headers
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except httpx.HTTPStatusError as e:
            # Handle specific HTTP errors
            error_detail = e.response.json().get('detail', str(e))
            raise Exception(f"API Error: {error_detail}")
        except json.JSONDecodeError:
            raise Exception("Failed to decode JSON response")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate and get access token"""
        data = {
            'username': username,
            'password': password
        }
        response = await self._make_request('POST', Config.AUTH_LOGIN, data=data)
        self.token = response.get('access')
        self.refresh_token = response.get('refresh')
        return response

    async def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            return False
            
        data = {'refresh': self.refresh_token}
        try:
            response = await self._make_request(
                'POST', 
                Config.AUTH_REFRESH, 
                data=data
            )
            self.token = response.get('access')
            return True
        except Exception:
            return False

    async def logout(self) -> bool:
        """Logout and clear tokens"""
        try:
            await self._make_request('POST', Config.AUTH_LOGOUT)
            return True
        except Exception:
            return False
        finally:
            self.token = None
            self.refresh_token = None

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Singleton instance
api_client = APIClient()
