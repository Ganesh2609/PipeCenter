from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import urlparse

# Add lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

try:
    from auth import auth_service
    from storage import storage_service
    from pdf_generator import QuotationPDFGenerator
    from models import Configuration, Quotation, LoginRequest, ApiResponse
except ImportError as e:
    print(f"Import error: {e}")
    # Create dummy classes to prevent crashes
    class DummyService:
        def get_configurations(self): return []
        def save_configurations(self, configs): return True
        def get_quotations(self): return []
        def save_quotations(self, quotes): return True
        def get_quotation_by_id(self, id): return None
    
    class DummyAuth:
        def authenticate_request(self, request): return "test"
        def login(self, request): return {"success": True, "token": "test"}
    
    storage_service = DummyService()
    auth_service = DummyAuth()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = urlparse(self.path).path
            print(f"GET request to: {path}")
            
            if path == '/api/health' or path == '/health':
                self._handle_health()
            elif path == '/api/configurations' or path == '/configurations':
                self._handle_get_configurations()
            elif path == '/api/quotations' or path == '/quotations':
                self._handle_get_quotations()
            elif '/pdf/' in path:
                # Extract quotation ID from path
                parts = path.split('/')
                quotation_id = parts[-1] if parts else None
                if quotation_id:
                    self._handle_pdf_generation(quotation_id)
                else:
                    self._send_error(400, "Invalid PDF request")
            else:
                self._send_error(404, f"Endpoint not found: {path}")
                
        except Exception as e:
            print(f"GET error: {e}")
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            path = urlparse(self.path).path
            print(f"POST request to: {path}")
            
            if '/login' in path:
                self._handle_login()
            elif '/configurations' in path and '/create' in path:
                self._handle_create_configuration()
            elif '/quotations' in path and '/create' in path:
                self._handle_create_quotation()
            else:
                self._send_error(404, f"Endpoint not found: {path}")
                
        except Exception as e:
            print(f"POST error: {e}")
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_PUT(self):
        """Handle PUT requests"""
        try:
            path = urlparse(self.path).path
            print(f"PUT request to: {path}")
            
            if '/quotations/' in path:
                parts = path.split('/')
                quotation_id = parts[-1] if parts else None
                if quotation_id:
                    self._handle_update_quotation(quotation_id)
                else:
                    self._send_error(400, "Invalid quotation ID")
            else:
                self._send_error(404, f"Endpoint not found: {path}")
                
        except Exception as e:
            print(f"PUT error: {e}")
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        try:
            path = urlparse(self.path).path
            print(f"DELETE request to: {path}")
            
            if '/configurations/' in path:
                parts = path.split('/')
                config_id = parts[-1] if parts else None
                if config_id:
                    self._handle_delete_configuration(config_id)
                else:
                    self._send_error(400, "Invalid configuration ID")
            elif '/quotations/' in path:
                parts = path.split('/')
                quotation_id = parts[-1] if parts else None
                if quotation_id:
                    self._handle_delete_quotation(quotation_id)
                else:
                    self._send_error(400, "Invalid quotation ID")
            else:
                self._send_error(404, f"Endpoint not found: {path}")
                
        except Exception as e:
            print(f"DELETE error: {e}")
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Expose-Headers', 'Content-Disposition')
        self.end_headers()
    
    # Health check
    def _handle_health(self):
        """Health check endpoint"""
        try:
            from datetime import datetime
            
            has_blob_token = bool(os.environ.get('BLOB_READ_WRITE_TOKEN'))
            has_auth_secret = bool(os.environ.get('AUTH_SECRET'))
            
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'service': 'PipeCenter Backend API',
                'environment': {
                    'has_blob_token': has_blob_token,
                    'has_auth_secret': has_auth_secret,
                    'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                }
            }
            
            self._send_json_response(200, health_data)
        except Exception as e:
            print(f"Health check error: {e}")
            self._send_error(500, f"Health check failed: {str(e)}")
    
    # Authentication
    def _handle_login(self):
        """Handle login requests"""
        try:
            data = self._get_request_body()
            
            # Basic validation
            username = data.get('username', '')
            password = data.get('password', '')
            
            if not username or not password:
                self._send_error(400, "Username and password required")
                return
            
            # Check credentials
            if username == os.environ.get('AUTH_USERNAME', 'arumugam') and \
               password == os.environ.get('AUTH_PASSWORD', 'pappu'):
                response = {
                    'success': True,
                    'token': 'dummy-jwt-token-for-testing'
                }
                self._send_json_response(200, response)
            else:
                response = {
                    'success': False,
                    'error': 'Invalid credentials'
                }
                self._send_json_response(401, response)
            
        except Exception as e:
            print(f"Login error: {e}")
            self._send_error(400, f"Login failed: {str(e)}")
    
    # Configurations
    def _handle_get_configurations(self):
        """Get all configurations"""
        try:
            configurations = storage_service.get_configurations()
            configs_data = [config.dict() if hasattr(config, 'dict') else config for config in configurations]
            
            response = {
                'success': True,
                'data': {'configurations': configs_data},
                'message': f"Retrieved {len(configs_data)} configurations"
            }
            
            self._send_json_response(200, response)
            
        except Exception as e:
            print(f"Get configurations error: {e}")
            self._send_error(500, f"Failed to retrieve configurations: {str(e)}")
    
    def _handle_create_configuration(self):
        """Create a new configuration"""
        try:
            import time
            data = self._get_request_body()
            
            # Add required fields
            if 'id' not in data:
                data['id'] = str(int(time.time() * 1000))
            if 'createdAt' not in data:
                data['createdAt'] = int(time.time() * 1000)
            
            # Basic validation
            required_fields = ['name', 'firstDiscount', 'secondDiscount', 'margin']
            for field in required_fields:
                if field not in data:
                    self._send_error(400, f"Missing required field: {field}")
                    return
            
            configurations = storage_service.get_configurations()
            
            # Check for duplicate names
            for config in configurations:
                config_name = config.name if hasattr(config, 'name') else config.get('name', '')
                if config_name.lower() == data['name'].lower():
                    self._send_error(400, f"Configuration with name '{data['name']}' already exists")
                    return
            
            # Add new configuration
            configurations.append(data)
            success = storage_service.save_configurations(configurations)
            
            if success:
                response = {
                    'success': True,
                    'data': {'configuration': data},
                    'message': "Configuration created successfully"
                }
                self._send_json_response(201, response)
            else:
                self._send_error(500, "Failed to save configuration")
                
        except Exception as e:
            print(f"Create configuration error: {e}")
            self._send_error(400, f"Failed to create configuration: {str(e)}")
    
    def _handle_delete_configuration(self, config_id):
        """Delete a configuration"""
        try:
            configurations = storage_service.get_configurations()
            original_count = len(configurations)
            
            # Filter out the configuration to delete
            configurations = [
                config for config in configurations 
                if (config.id if hasattr(config, 'id') else config.get('id')) != config_id
            ]
            
            if len(configurations) == original_count:
                self._send_error(404, f"Configuration with ID '{config_id}' not found")
                return
            
            success = storage_service.save_configurations(configurations)
            
            if success:
                response = {
                    'success': True,
                    'message': f"Configuration '{config_id}' deleted successfully"
                }
                self._send_json_response(200, response)
            else:
                self._send_error(500, "Failed to save configurations after deletion")
                
        except Exception as e:
            print(f"Delete configuration error: {e}")
            self._send_error(500, f"Failed to delete configuration: {str(e)}")
    
    # Quotations
    def _handle_get_quotations(self):
        """Get all quotations"""
        try:
            quotations = storage_service.get_quotations()
            quotations_data = [quotation.dict() if hasattr(quotation, 'dict') else quotation for quotation in quotations]
            quotations_data.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
            
            response = {
                'success': True,
                'data': {'quotations': quotations_data},
                'message': f"Retrieved {len(quotations_data)} quotations"
            }
            
            self._send_json_response(200, response)
            
        except Exception as e:
            print(f"Get quotations error: {e}")
            self._send_error(500, f"Failed to retrieve quotations: {str(e)}")
    
    def _handle_create_quotation(self):
        """Create a new quotation"""
        try:
            import time
            from datetime import datetime
            
            data = self._get_request_body()
            
            # Add required fields
            if 'id' not in data:
                data['id'] = str(int(time.time() * 1000))
            if 'createdAt' not in data:
                data['createdAt'] = int(time.time() * 1000)
            if 'date' not in data:
                data['date'] = datetime.now().strftime("%d/%m/%Y")
            
            quotations = storage_service.get_quotations()
            quotations.append(data)
            
            success = storage_service.save_quotations(quotations)
            
            if success:
                response = {
                    'success': True,
                    'data': {'quotation': data},
                    'message': "Quotation created successfully"
                }
                self._send_json_response(201, response)
            else:
                self._send_error(500, "Failed to save quotation")
                
        except Exception as e:
            print(f"Create quotation error: {e}")
            self._send_error(400, f"Failed to create quotation: {str(e)}")
    
    def _handle_update_quotation(self, quotation_id):
        """Update a quotation"""
        try:
            data = self._get_request_body()
            data['id'] = quotation_id
            
            quotations = storage_service.get_quotations()
            
            found = False
            for i, quotation in enumerate(quotations):
                q_id = quotation.id if hasattr(quotation, 'id') else quotation.get('id')
                if q_id == quotation_id:
                    quotations[i] = data
                    found = True
                    break
            
            if not found:
                self._send_error(404, f"Quotation with ID '{quotation_id}' not found")
                return
            
            success = storage_service.save_quotations(quotations)
            
            if success:
                response = {
                    'success': True,
                    'data': {'quotation': data},
                    'message': f"Quotation '{quotation_id}' updated successfully"
                }
                self._send_json_response(200, response)
            else:
                self._send_error(500, "Failed to save updated quotation")
                
        except Exception as e:
            print(f"Update quotation error: {e}")
            self._send_error(400, f"Failed to update quotation: {str(e)}")
    
    def _handle_delete_quotation(self, quotation_id):
        """Delete a quotation"""
        try:
            quotations = storage_service.get_quotations()
            original_count = len(quotations)
            
            quotations = [
                quotation for quotation in quotations 
                if (quotation.id if hasattr(quotation, 'id') else quotation.get('id')) != quotation_id
            ]
            
            if len(quotations) == original_count:
                self._send_error(404, f"Quotation with ID '{quotation_id}' not found")
                return
            
            success = storage_service.save_quotations(quotations)
            
            if success:
                response = {
                    'success': True,
                    'message': f"Quotation '{quotation_id}' deleted successfully"
                }
                self._send_json_response(200, response)
            else:
                self._send_error(500, "Failed to save quotations after deletion")
                
        except Exception as e:
            print(f"Delete quotation error: {e}")
            self._send_error(500, f"Failed to delete quotation: {str(e)}")
    
    # PDF Generation
    def _handle_pdf_generation(self, quotation_id):
        """Generate PDF for quotation"""
        try:
            quotation = storage_service.get_quotation_by_id(quotation_id)
            
            if not quotation:
                self._send_error(404, f"Quotation with ID '{quotation_id}' not found")
                return
            
            # For now, return a simple text response instead of PDF
            # PDF generation can be implemented later once basic functionality works
            response_text = f"PDF for quotation {quotation_id} would be generated here"
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(response_text.encode())
            
        except Exception as e:
            print(f"PDF generation error: {e}")
            self._send_error(500, f"Failed to generate PDF: {str(e)}")
    
    # Helper methods
    def _get_request_body(self):
        """Get and parse request body"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return {}
            
            post_data = self.rfile.read(content_length)
            return json.loads(post_data.decode('utf-8'))
        except Exception as e:
            print(f"Error parsing request body: {e}")
            return {}
    
    def _send_json_response(self, status_code, data):
        """Send JSON response"""
        try:
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_json = json.dumps(data)
            self.wfile.write(response_json.encode())
        except Exception as e:
            print(f"Error sending JSON response: {e}")
    
    def _send_error(self, status_code, message):
        """Send error response"""
        try:
            error_response = {
                'success': False,
                'error': message
            }
            self._send_json_response(status_code, error_response)
        except Exception as e:
            print(f"Error sending error response: {e}")