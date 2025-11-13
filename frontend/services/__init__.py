"""
Services package for the Lawyer Office Management frontend.
"""
from .api_client import api_client, auth_service
from .storage import Storage

# Re-export the Storage class
def get_storage():
    return Storage

__all__ = ['api_client', 'auth_service', 'Storage', 'get_storage']
