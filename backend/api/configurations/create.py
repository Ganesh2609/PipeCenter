from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import asyncio
import time

# Add lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))

from auth import auth_service
from storage import storage_service
from models import Configuration, ApiResponse

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Create a new configuration"""
        try:
            # Authenticate request
            username = auth_service.authenticate_request(self)
            if not username:
                self._send_error(401, "Authentication required")
                return
            
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            data = json.loads(post_data.decode('utf-8'))
            
            # Generate ID and timestamp if not provided
            if 'id' not in data:
                data['id'] = str(int(time.time() * 1000))
            if 'createdAt' not in data:
                data['createdAt'] = int(time.time() * 1000)
            
            # Validate configuration data
            new_config = Configuration(**data)
            
            # Get existing configurations
            configurations = asyncio.run(storage_service.get_configurations())
            
            # Check for duplicate names
            for config in configurations:
                if config.name.lower() == new_config.name.lower():
                    self._send_error(400, f"Configuration with name '{new_config.name}' already exists")
                    return
            
            # Add new configuration
            configurations.append(new_config)
            
            # Save to storage
            success = asyncio.run(storage_service.save_configurations(configurations))
            
            if success:
                response = ApiResponse(
                    success=True,
                    data={'configuration': new_config.dict()},
                    message="Configuration created successfully"
                )
                
                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_json = json.dumps(response.dict())
                self.wfile.write(response_json.encode())
            else:
                self._send_error(500, "Failed to save configuration")
            
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON format")
        except ValueError as e:
            self._send_error(400, f"Validation error: {str(e)}")
        except Exception as e:
            print(f"Create configuration error: {e}")
            self._send_error(500, "Failed to create configuration")
    
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
        
        error_response = ApiResponse(
            success=False,
            error=message
        )
        
        response_json = json.dumps(error_response.dict())
        self.wfile.write(response_json.encode())

# Run async function
async def main():
    pass

if __name__ == "__main__":
    asyncio.run(main())