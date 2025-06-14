import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from .models import LoginRequest, LoginResponse

class AuthService:
    """
    Simple authentication service for single user (arumugam/pappu)
    """
    
    def __init__(self):
        self.secret_key = os.environ.get('AUTH_SECRET', 'default-secret-key')
        self.username = os.environ.get('AUTH_USERNAME')
        self.password = os.environ.get('AUTH_PASSWORD')
        self.algorithm = 'HS256'
        self.token_expire_hours = 24
    
    def validate_user(self, username: str, password: str) -> bool:
        """Validate username and password"""
        return username == self.username and password == self.password
    
    def generate_token(self, username: str) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expire_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return username if valid"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username = payload.get('username')
            if username == self.username:
                return username
            return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def login(self, login_request: LoginRequest) -> LoginResponse:
        """Process login request"""
        if self.validate_user(login_request.username, login_request.password):
            token = self.generate_token(login_request.username)
            return LoginResponse(success=True, token=token)
        else:
            return LoginResponse(success=False, error="Invalid credentials")
    
    def get_authorization_header(self, request) -> Optional[str]:
        """Extract authorization header from request"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        return None
    
    def authenticate_request(self, request) -> Optional[str]:
        """Authenticate request and return username if valid"""
        token = self.get_authorization_header(request)
        if token:
            return self.verify_token(token)
        return None

# Initialize auth service
auth_service = AuthService()

def require_auth(func):
    """Decorator to require authentication for API endpoints"""
    def wrapper(request, *args, **kwargs):
        username = auth_service.authenticate_request(request)
        if not username:
            return {
                'success': False,
                'error': 'Authentication required'
            }, 401
        
        # Add username to request for use in handler
        request.username = username
        return func(request, *args, **kwargs)
    
    return wrapper