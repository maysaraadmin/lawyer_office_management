# This file makes the core directory a Python package

# Import middleware from the middleware package
from .middleware import RequestLoggingMiddleware

__all__ = ['RequestLoggingMiddleware']
