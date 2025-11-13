"""
Authentication and authorization utilities for the Lawyer Office Management system.
Handles JWT token management, user sessions, and permission checks.
"""
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

import jwt
from ..services.api_client import api_client

# Configure logging
logger = logging.getLogger(__name__)

class AuthError(Exception):
    """Base exception for authentication-related errors"""
    
    def __init__(self, message: str, details: Any = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class AuthService:
    """Authentication service for handling JWT tokens with enhanced security"""
    
    def __init__(self, api_client):
        """Initialize the authentication service
        
        Args:
            api_client: Instance of APIClient for making API requests
        """
        if not api_client:
            raise ValueError("API client is required")
            
        self.api_client = api_client
        self.token_file = self._get_token_file_path()
        self._load_tokens()
    
    def _get_token_file_path(self) -> Path:
        """Get the path to the token file in the user's home directory"""
        # Create .lawyer_office directory in user's home if it doesn't exist
        home = Path.home()
        token_dir = home / ".lawyer_office"
        token_dir.mkdir(mode=0o700, exist_ok=True)
        
        # Set appropriate permissions (read/write for owner only)
        try:
            token_dir.chmod(0o700)
        except Exception as e:
            logger.warning(f"Failed to set permissions on token directory: {e}")
        
        return token_dir / "auth_tokens.json"
    
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
                    # Use create_task to avoid blocking
                    import asyncio
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
            payload = jwt.decode(token, options={"verify_signature": False})
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
        return bool(self.api_client.access_token)
    
    async def login(self, email: str, password: str) -> Tuple[bool, str]:
        """Login with email and password
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not email or not password:
            return False, "Email and password are required"
            
        # Basic email validation
        if '@' not in email or '.' not in email:
            return False, "Please enter a valid email address"
            
        try:
            # Make the login request
            response = await self.api_client.post('auth/token/', {
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
            
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'status_code') and e.status_code == 401:
                error_msg = "Invalid email or password"
            logger.error(f"Login failed: {error_msg}")
            return False, error_msg
    
    async def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token
        
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
            
            response = await self.api_client.post('auth/token/refresh/', {
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
            
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'status_code') and e.status_code == 401:  # Unauthorized
                logger.warning("Refresh token is invalid or expired")
                self._clear_tokens()
            else:
                logger.error(f"Error refreshing token: {error_msg}")
            return False
    
    def logout(self):
        """Logout the current user"""
        self._clear_tokens()
        logger.info("User logged out")
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user information from JWT token"""
        if not self.api_client.access_token:
            return None
            
        try:
            # Decode token without verification
            payload = jwt.decode(
                self.api_client.access_token,
                options={"verify_signature": False}
            )
            return {
                'id': payload.get('user_id'),
                'email': payload.get('email'),
                'first_name': payload.get('first_name'),
                'last_name': payload.get('last_name'),
                'is_staff': payload.get('is_staff', False),
                'is_superuser': payload.get('is_superuser', False),
            }
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None
    
    def has_permission(self, permission: str) -> bool:
        """Check if current user has the specified permission"""
        # In a real app, this would check the user's permissions
        # For now, just check if user is authenticated
        return self.is_authenticated()

# Create a singleton instance
auth_service = AuthService(api_client)
