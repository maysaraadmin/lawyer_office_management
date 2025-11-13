from typing import Dict, Optional, Any
import json
import logging
from datetime import datetime, timedelta

from .api_client import api_client

logger = logging.getLogger(__name__)

class AuthService:
    """
    Service for handling authentication state and user sessions
    """
    
    def __init__(self, api_client):
        self.api_client = api_client
        self._user = None
        self._on_login_callbacks = []
        self._on_logout_callbacks = []
    
    @property
    def is_authenticated(self) -> bool:
        """Check if the user is currently authenticated"""
        return self.api_client.is_authenticated
    
    @property
    def user(self) -> Optional[Dict[str, Any]]:
        """Get the current user's data"""
        return self._user
    
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated"""
        return self.api_client.is_authenticated
    
    def on_login(self, callback):
        """Register a callback to be called when a user logs in"""
        self._on_login_callbacks.append(callback)
        return lambda: self._on_login_callbacks.remove(callback)
    
    def on_logout(self, callback):
        """Register a callback to be called when a user logs out"""
        self._on_logout_callbacks.append(callback)
        return lambda: self._on_logout_callbacks.remove(callback)
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Attempt to log in a user with the provided credentials
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Dict containing the result of the login attempt
        """
        try:
            result = await self.api_client.login(email, password)
            
            if result.get("status") == "success":
                self._user = result.get("user", {})
                
                # Call login callbacks
                for callback in self._on_login_callbacks:
                    try:
                        callback(self._user)
                    except Exception as e:
                        logger.error(f"Error in login callback: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {
                "status": "error",
                "message": f"Login failed: {str(e)}"
            }
    
    async def logout(self) -> Dict[str, Any]:
        """
        Log out the current user
        """
        try:
            # Call the API to invalidate the token
            await self.api_client.logout()
            
            # Clear local user data
            user = self._user
            self._user = None
            
            # Call logout callbacks
            for callback in self._on_logout_callbacks:
                try:
                    callback(user)
                except Exception as e:
                    logger.error(f"Error in logout callback: {e}")
            
            return {
                "status": "success",
                "message": "Logged out successfully"
            }
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return {
                "status": "error",
                "message": f"Logout failed: {str(e)}"
            }
    
    async def refresh_user_data(self) -> bool:
        """
        Refresh the current user's data from the server
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_authenticated:
            return False
            
        try:
            result = await self.api_client.get_current_user()
            if result.get("status") == "success":
                self._user = result.get("data", {})
                return True
        except Exception as e:
            logger.error(f"Failed to refresh user data: {str(e)}")
            
        return False
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if the current user has a specific permission
        
        Args:
            permission: The permission to check (e.g., 'cases.view_case')
            
        Returns:
            bool: True if the user has the permission, False otherwise
        """
        if not self._user:
            return False
            
        # Check direct permissions
        permissions = self._user.get("permissions", [])
        if permission in permissions:
            return True
            
        # Check role-based permissions
        user_roles = self._user.get("roles", [])
        for role in user_roles:
            role_permissions = role.get("permissions", [])
            if permission in role_permissions:
                return True
                
        return False
    
    def has_role(self, role_name: str) -> bool:
        """
        Check if the current user has a specific role
        
        Args:
            role_name: The name of the role to check
            
        Returns:
            bool: True if the user has the role, False otherwise
        """
        if not self._user:
            return False
            
        user_roles = self._user.get("roles", [])
        return any(role.get("name") == role_name for role in user_roles)

# Singleton instance
auth_service = AuthService(api_client)
