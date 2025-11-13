import flet as ft
from typing import Optional, Callable, Any, Dict
from datetime import datetime, timedelta
import jwt
from .config import Config
from .api_client import api_client

class AuthService:
    """
    Authentication service to handle user sessions and token management.
    This can be used by both web and mobile apps.
    """
    def __init__(self, page: ft.Page = None):
        self.page = page
        self._on_login = None
        self._on_logout = None
        self._user_data = None

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        if not api_client.token:
            return False
            
        try:
            # Check if token is expired
            payload = jwt.decode(
                api_client.token, 
                options={"verify_signature": False}
            )
            exp = payload.get('exp')
            if exp and datetime.utcnow() > datetime.utcfromtimestamp(exp):
                return False
            return True
        except jwt.PyJWTError:
            return False

    @property
    def user_data(self) -> Optional[Dict]:
        """Get user data from token"""
        if not self.is_authenticated:
            return None
            
        if not self._user_data:
            try:
                self._user_data = jwt.decode(
                    api_client.token, 
                    options={"verify_signature": False}
                )
            except jwt.PyJWTError:
                return None
                
        return self._user_data

    async def login(self, username: str, password: str) -> bool:
        """
        Authenticate user with username and password
        Returns True if successful, False otherwise
        """
        try:
            await api_client.login(username, password)
            if self._on_login:
                await self._on_login()
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    async def logout(self) -> bool:
        """Logout the current user"""
        try:
            await api_client.logout()
            self._user_data = None
            if self._on_logout:
                await self._on_logout()
            return True
        except Exception as e:
            print(f"Logout failed: {str(e)}")
            return False

    def set_on_login_callback(self, callback: Callable[[], Any]):
        """Set callback to be called after successful login"""
        self._on_login = callback

    def set_on_logout_callback(self, callback: Callable[[], Any]):
        """Set callback to be called after logout"""
        self._on_logout = callback

    def get_auth_header(self) -> Dict[str, str]:
        """Get authentication header for API requests"""
        if not self.is_authenticated or not api_client.token:
            return {}
        return {"Authorization": f"Bearer {api_client.token}"}

# Singleton instance
auth_service = AuthService()
