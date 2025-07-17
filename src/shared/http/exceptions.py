class HTTPClientError(Exception):
    """Base exception for HTTP client errors"""
    pass


class ExternalServiceError(HTTPClientError):
    """Raised when external service returns 5XX or network error"""
    pass


class TimeoutError(ExternalServiceError):
    """Raised when request times out"""
    pass


class NetworkError(ExternalServiceError):
    """Raised when network error occurs"""
    pass


class ServerError(ExternalServiceError):
    """Raised when server returns 5XX error"""
    pass 