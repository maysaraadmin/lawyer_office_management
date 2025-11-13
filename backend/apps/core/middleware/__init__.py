# This file makes the middleware directory a Python package

from .request_logging import RequestLoggingMiddleware

__all__ = ['RequestLoggingMiddleware']
