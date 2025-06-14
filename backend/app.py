from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import asyncio
from urllib.parse import urlparse, parse_qs

# Add lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from auth import auth_service
from storage import storage_service
from pdf_generator import QuotationPDFGenerator
from models import Configuration, Quotation, LoginRequest, ApiResponse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = urlparse(self.path).path
            
            if path == '/api/health':
                self._handle_health()
            elif path == '/api/configurations':
                self._handle_get_configurations()
            elif path == '/api/quotations':
                self._handle_get_quotations()
            elif path.startswith('/api/quotations/pdf/'):
                quotation_id = path.split('/')[-1]
                self._handle_pdf_generation(quotation_id)
            else:
                self._send_error(404, "Endpoint not found")
                
        except Exception as e:
            print(f"GET error: {e}")
            self._send_error(500, "Internal server error")
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            path = urlparse(self.path).path
            
            if path == '/api/auth/login':
                self._handle_login()
            elif path == '/api/configurations/create':
                self._handle_create_configuration()
            elif path == '/api/quotations/create':
                self._handle_create_quotation()
            else:
                self._send_error(404, "Endpoint not found")
                
        except Exception as e:
            print(f"POST error: {e}")
            self._send_error(500, "Internal server error")
    
    def do_PUT(self):
        """Handle PUT requests"""
        try:
            path = urlparse(self.path).path
            
            if path.startswith('/api/quotations/'):
                quotation_id = path.split('/')[-1]
                self._handle_update_quotation(quotation_id)
            else:
                self._send_error(404, "Endpoint not found")
                
        except Exception as e:
            print(f"PUT error: {e}")
            self._send_error(500, "Internal server error")
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        try:
            path = urlparse(self.path).path
            
            if path.startswith('/api/configurations/'):
                config_id = path.split('/')[-1]
                self._handle_delete_configuration(config_id)
            elif path.startswith('/api/quotations/'):
                quotation_id = path.split('/')[-1]
                self._handle_delete_quotation(quotation_id)
            else:
                self._send_error(404, "Endpoint not found")
                
        except Exception as e:
            print(f"DELETE error: {e}")
            self._send_error(500, "Internal server error")
    
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
    
    # Authentication
    def _handle_login(self):
        """Handle login requests"""
        try:
            data = self._get_request_body()
            login_request = LoginRequest(**data)
            response = auth_service.login(login_request)
            
            status_code = 200 if response.success else 401
            self._send_json_response(status_code, response.dict())
            
        except Exception as e:
            self._send_error(400, f"Login failed: {str(e)}")
    
    # Configurations
    def _handle_get_configurations(self):
        """Get all configurations"""
        if not self._authenticate():
            return
        
        try:
            configurations = asyncio.run(storage_service.get_configurations())
            configs_data = [config.dict() for config in configurations]
            
            response = ApiResponse(
                success=True,
                data={'configurations': configs_data},
                message=f"Retrieved {len(configs_data)} configurations"
            )
            
            self._send_json_response(200, response.dict())
            
        except Exception as e:
            self._send_error(500, "Failed to retrieve configurations")
    
    def _handle_create_configuration(self):
        """Create a new configuration"""
        if not self._authenticate():
            return
        
        try:
            import time
            data = self._get_request_body()
            
            if 'id' not in data:
                data['id'] = str(int(time.time() * 1000))
            if 'createdAt' not in data:
                data['createdAt'] = int(time.time() * 1000)
            
            new_config = Configuration(**data)
            configurations = asyncio.run(storage_service.get_configurations())
            
            # Check for duplicate names
            for config in configurations:
                if config.name.lower() == new_config.name.lower():
                    self._send_error(400, f"Configuration with name '{new_config.name}' already exists")
                    return
            
            configurations.append(new_config)
            success = asyncio.run(storage_service.save_configurations(configurations))
            
            if success:
                response = ApiResponse(
                    success=True,
                    data={'configuration': new_config.dict()},
                    message="Configuration created successfully"
                )
                self._send_json_response(201, response.dict())
            else:
                self._send_error(500, "Failed to save configuration")
                
        except Exception as e:
            self._send_error(400, f"Failed to create configuration: {str(e)}")
    
    def _handle_delete_configuration(self, config_id):
        """Delete a configuration"""
        if not self._authenticate():
            return
        
        try:
            configurations = asyncio.run(storage_service.get_configurations())
            original_count = len(configurations)
            configurations = [config for config in configurations if config.id != config_id]
            
            if len(configurations) == original_count:
                self._send_error(404, f"Configuration with ID '{config_id}' not found")
                return
            
            success = asyncio.run(storage_service.save_configurations(configurations))
            
            if success:
                response = ApiResponse(
                    success=True,
                    message=f"Configuration '{config_id}' deleted successfully"
                )
                self._send_json_response(200, response.dict())
            else:
                self._send_error(500, "Failed to save configurations after deletion")
                
        except Exception as e:
            self._send_error(500, "Failed to delete configuration")
    
    # Quotations
    def _handle_get_quotations(self):
        """Get all quotations"""
        if not self._authenticate():
            return
        
        try:
            quotations = asyncio.run(storage_service.get_quotations())
            quotations_data = [quotation.dict() for quotation in quotations]
            quotations_data.sort(key=lambda x: x['createdAt'], reverse=True)
            
            response = ApiResponse(
                success=True,
                data={'quotations': quotations_data},
                message=f"Retrieved {len(quotations_data)} quotations"
            )
            
            self._send_json_response(200, response.dict())
            
        except Exception as e:
            self._send_error(500, "Failed to retrieve quotations")
    
    def _handle_create_quotation(self):
        """Create a new quotation"""
        if not self._authenticate():
            return
        
        try:
            import time
            data = self._get_request_body()
            
            if 'id' not in data:
                data['id'] = str(int(time.time() * 1000))
            if 'createdAt' not in data:
                data['createdAt'] = int(time.time() * 1000)
            
            new_quotation = Quotation(**data)
            quotations = asyncio.run(storage_service.get_quotations())
            quotations.append(new_quotation)
            
            success = asyncio.run(storage_service.save_quotations(quotations))
            
            if success:
                response = ApiResponse(
                    success=True,
                    data={'quotation': new_quotation.dict()},
                    message="Quotation created successfully"
                )
                self._send_json_response(201, response.dict())
            else:
                self._send_error(500, "Failed to save quotation")
                
        except Exception as e:
            self._send_error(400, f"Failed to create quotation: {str(e)}")
    
    def _handle_update_quotation(self, quotation_id):
        """Update a quotation"""
        if not self._authenticate():
            return
        
        try:
            data = self._get_request_body()
            data['id'] = quotation_id
            
            updated_quotation = Quotation(**data)
            quotations = asyncio.run(storage_service.get_quotations())
            
            found = False
            for i, quotation in enumerate(quotations):
                if quotation.id == quotation_id:
                    quotations[i] = updated_quotation
                    found = True
                    break
            
            if not found:
                self._send_error(404, f"Quotation with ID '{quotation_id}' not found")
                return
            
            success = asyncio.run(storage_service.save_quotations(quotations))
            
            if success:
                response = ApiResponse(
                    success=True,
                    data={'quotation': updated_quotation.dict()},
                    message=f"Quotation '{quotation_id}' updated successfully"
                )
                self._send_json_response(200, response.dict())
            else:
                self._send_error(500, "Failed to save updated quotation")
                
        except Exception as e:
            self._send_error(400, f"Failed to update quotation: {str(e)}")
    
    def _handle_delete_quotation(self, quotation_id):
        """Delete a quotation"""
        if not self._authenticate():
            return
        
        try:
            quotations = asyncio.run(storage_service.get_quotations())
            original_count = len(quotations)
            quotations = [quotation for quotation in quotations if quotation.id != quotation_id]
            
            if len(quotations) == original_count:
                self._send_error(404, f"Quotation with ID '{quotation_id}' not found")
                return
            
            success = asyncio.run(storage_service.save_quotations(quotations))
            
            if success:
                response = ApiResponse(
                    success=True,
                    message=f"Quotation '{quotation_id}' deleted successfully"
                )
                self._send_json_response(200, response.dict())
            else:
                self._send_error(500, "Failed to save quotations after deletion")
                
        except Exception as e:
            self._send_error(500, "Failed to delete quotation")
    
    # PDF Generation
    def _handle_pdf_generation(self, quotation_id):
        """Generate PDF for quotation"""
        if not self._authenticate():
            return
        
        try:
            quotation = asyncio.run(storage_service.get_quotation_by_id(quotation_id))
            
            if not quotation:
                self._send_error(404, f"Quotation with ID '{quotation_id}' not found")
                return
            
            pdf_bytes = QuotationPDFGenerator.generate(quotation)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', f'attachment; filename="quotation_{quotation_id}.pdf"')
            self.send_header('Content-Length', str(len(pdf_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Expose-Headers', 'Content-Disposition')
            self.end_headers()
            
            self.wfile.write(pdf_bytes)
            
        except Exception as e:
            self._send_error(500, f"Failed to generate PDF: {str(e)}")
    
    # Helper methods
    def _authenticate(self):
        """Authenticate request"""
        username = auth_service.authenticate_request(self)
        if not username:
            self._send_error(401, "Authentication required")
            return False
        return True
    
    def _get_request_body(self):
        """Get and parse request body"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        
        post_data = self.rfile.read(content_length)
        return json.loads(post_data.decode('utf-8'))
    
    def _send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(data)
        self.wfile.write(response_json.encode())
    
    def _send_error(self, status_code, message):
        """Send error response"""
        error_response = ApiResponse(success=False, error=message)
        self._send_json_response(status_code, error_response.dict())