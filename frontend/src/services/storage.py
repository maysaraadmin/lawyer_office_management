"""
Simple storage service for persisting data using browser's localStorage or in-memory storage.
"""
import json
from typing import Any, Optional, Dict

class Storage:
    """Simple key-value storage with JSON serialization"""
    
    def __init__(self, prefix: str = "lawyer_office_"):
        self.prefix = prefix
        self._storage: Dict[str, str] = {}
        self._load_from_local_storage()
    
    def _get_key(self, key: str) -> str:
        """Get namespaced key"""
        return f"{self.prefix}{key}"
    
    def _load_from_local_storage(self):
        """Load data from browser's localStorage if available"""
        try:
            # This will work in browser environment
            from js import localStorage
            self._storage = {}
            for i in range(localStorage.length):
                key = localStorage.key(i)
                if key.startswith(self.prefix):
                    self._storage[key] = localStorage.getItem(key)
        except Exception:
            # Fallback to in-memory storage
            self._storage = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from storage"""
        full_key = self._get_key(key)
        try:
            # Try browser localStorage first
            from js import localStorage
            value = localStorage.getItem(full_key)
            if value is not None:
                return json.loads(value)
        except Exception:
            # Fallback to in-memory storage
            if full_key in self._storage:
                return json.loads(self._storage[full_key])
        return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in storage"""
        full_key = self._get_key(key)
        try:
            # Try browser localStorage first
            from js import localStorage
            localStorage.setItem(full_key, json.dumps(value))
        except Exception:
            # Fallback to in-memory storage
            self._storage[full_key] = json.dumps(value)
    
    def remove(self, key: str) -> None:
        """Remove a key from storage"""
        full_key = self._get_key(key)
        try:
            # Try browser localStorage first
            from js import localStorage
            localStorage.removeItem(full_key)
        except Exception:
            # Fallback to in-memory storage
            if full_key in self._storage:
                del self._storage[full_key]
    
    def clear(self) -> None:
        """Clear all storage"""
        try:
            # Try browser localStorage first
            from js import localStorage
            keys_to_remove = []
            for i in range(localStorage.length):
                key = localStorage.key(i)
                if key.startswith(self.prefix):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                localStorage.removeItem(key)
        except Exception:
            # Fallback to in-memory storage
            self._storage.clear()
