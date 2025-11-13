import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
    
    # Authentication
    AUTH_TOKEN_KEY = 'auth_token'
    REFRESH_TOKEN_KEY = 'refresh_token'
    
    # API Endpoints
    AUTH_LOGIN = '/auth/login/'
    AUTH_REFRESH = '/auth/refresh/'
    AUTH_LOGOUT = '/auth/logout/'
    
    # Common Headers
    @staticmethod
    def get_auth_headers(token=None):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers
