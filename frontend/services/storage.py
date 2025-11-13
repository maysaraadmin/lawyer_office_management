"""
Simple storage utility for client-side storage using browser's localStorage.
"""

class Storage:
    @staticmethod
    def get(key, default=None):
        """Get a value from storage"""
        try:
            from browser import window
            value = window.localStorage.getItem(key)
            return value if value is not None else default
        except:
            # Fallback for testing or non-browser environments
            return default

    @staticmethod
    def set(key, value):
        """Set a value in storage"""
        try:
            from browser import window
            if value is None:
                window.localStorage.removeItem(key)
            else:
                window.localStorage.setItem(key, str(value))
        except:
            # Fallback for testing or non-browser environments
            pass

    @staticmethod
    def remove(key):
        """Remove a value from storage"""
        try:
            from browser import window
            window.localStorage.removeItem(key)
        except:
            # Fallback for testing or non-browser environments
            pass

# For testing in non-browser environment
if __name__ == "__main__":
    import sys
    if "_js" not in sys.modules:
        from unittest.mock import MagicMock
        import sys
        sys.modules["js"] = MagicMock()
        sys.modules["js.window"] = MagicMock()
        sys.modules["js.window.localStorage"] = {}
    
    # Test the storage
    set("test_key", "test_value")
    assert get("test_key") == "test_value"
    remove("test_key")
    assert get("test_key") is None
    print("Storage tests passed!")
