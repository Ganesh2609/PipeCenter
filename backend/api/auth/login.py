from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))

from auth import auth_service
from models import LoginRequest, LoginResponse

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle login requests"""
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            data = json.loads(post_data.decode('utf-8'))
            
            # Validate request
            login_request = LoginRequest(**data)
            
            # Process login
            response = auth_service.login(login_request)
            
            # Send response
            status_code = 200 if response.success else 401
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_json = json.dumps(response.dict())
            self.wfile.write(response_json.encode())
            
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON format")
        except Exception as e:
            print(f"Login error: {e}")
            self._send_error(500, "Login failed")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def _send_error(self, status_code: int, message: str):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            'success': False,
            'error': message
        }
        
        response_json = json.dumps(error_response)
        self.wfile.write(response_json.encode())