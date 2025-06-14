from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import asyncio
from urllib.parse import urlparse

# Add lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))

from auth import auth_service
from storage import storage_service
from models import ApiResponse

class handler(BaseHTTPRequestHandler):
    def do_DELETE(self):
        """Delete a configuration by ID"""
        try:
            # Authenticate request
            username = auth_service.authenticate_request(self)
            if not username:
                self._send_error(401, "Authentication required")
                return
            
            # Extract configuration ID from URL
            config_id = self._extract_id_from_path()
            if not config_id:
                self._send_error(400, "Configuration ID is required")
                return
            
            # Get existing configurations
            configurations = asyncio.run(storage_service.get_configurations())
            
            # Find and remove configuration
            original_count = len(configurations)
            configurations = [config for config in configurations if config.id != config_id]
            
            if len(configurations) == original_count:
                self._send_error(404, f"Configuration with ID '{config_id}' not found")
                return
            
            # Save updated configurations
            success = asyncio.run(storage_service.save_configurations(configurations))
            
            if success:
                response = ApiResponse(
                    success=True,
                    message=f"Configuration '{config_id}' deleted successfully"
                )
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_json = json.dumps(response.dict())
                self.wfile.write(response_json.encode())
            else:
                self._send_error(500, "Failed to save configurations after deletion")
            
        except Exception as e:
            print(f"Delete configuration error: {e}")
            self._send_error(500, "Failed to delete configuration")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def _extract_id_from_path(self):
        """Extract ID from URL path"""
        try:
            # Get the path from the request
            path = self.path
            # Remove query parameters
            path = urlparse(path).path
            # Extract ID from path like /api/configurations/12345
            parts = path.strip('/').split('/')
            if len(parts) >= 3:
                return parts[-1]  # Last part should be the ID
            return None
        except Exception as e:
            print(f"Error extracting ID from path: {e}")
            return None
    
    def _send_error(self, status_code: int, message: str):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = ApiResponse(
            success=False,
            error=message
        )
        
        response_json = json.dumps(error_response.dict())
        self.wfile.write(response_json.encode())