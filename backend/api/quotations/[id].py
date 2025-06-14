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
from models import Quotation, ApiResponse

class handler(BaseHTTPRequestHandler):
    def do_PUT(self):
        """Update a quotation by ID"""
        try:
            # Authenticate request
            username = auth_service.authenticate_request(self)
            if not username:
                self._send_error(401, "Authentication required")
                return
            
            # Extract quotation ID from URL
            quotation_id = self._extract_id_from_path()
            if not quotation_id:
                self._send_error(400, "Quotation ID is required")
                return
            
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            data = json.loads(post_data.decode('utf-8'))
            
            # Ensure ID matches URL
            data['id'] = quotation_id
            
            # Validate updated quotation data
            updated_quotation = Quotation(**data)
            
            # Get existing quotations
            quotations = asyncio.run(storage_service.get_quotations())
            
            # Find and update quotation
            found = False
            for i, quotation in enumerate(quotations):
                if quotation.id == quotation_id:
                    quotations[i] = updated_quotation
                    found = True
                    break
            
            if not found:
                self._send_error(404, f"Quotation with ID '{quotation_id}' not found")
                return
            
            # Save updated quotations
            success = asyncio.run(storage_service.save_quotations(quotations))
            
            if success:
                response = ApiResponse(
                    success=True,
                    data={'quotation': updated_quotation.dict()},
                    message=f"Quotation '{quotation_id}' updated successfully"
                )
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_json = json.dumps(response.dict())
                self.wfile.write(response_json.encode())
            else:
                self._send_error(500, "Failed to save updated quotation")
            
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON format")
        except ValueError as e:
            self._send_error(400, f"Validation error: {str(e)}")
        except Exception as e:
            print(f"Update quotation error: {e}")
            self._send_error(500, "Failed to update quotation")
    
    def do_DELETE(self):
        """Delete a quotation by ID"""
        try:
            # Authenticate request
            username = auth_service.authenticate_request(self)
            if not username:
                self._send_error(401, "Authentication required")
                return
            
            # Extract quotation ID from URL
            quotation_id = self._extract_id_from_path()
            if not quotation_id:
                self._send_error(400, "Quotation ID is required")
                return
            
            # Get existing quotations
            quotations = asyncio.run(storage_service.get_quotations())
            
            # Find and remove quotation
            original_count = len(quotations)
            quotations = [quotation for quotation in quotations if quotation.id != quotation_id]
            
            if len(quotations) == original_count:
                self._send_error(404, f"Quotation with ID '{quotation_id}' not found")
                return
            
            # Save updated quotations
            success = asyncio.run(storage_service.save_quotations(quotations))
            
            if success:
                response = ApiResponse(
                    success=True,
                    message=f"Quotation '{quotation_id}' deleted successfully"
                )
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_json = json.dumps(response.dict())
                self.wfile.write(response_json.encode())
            else:
                self._send_error(500, "Failed to save quotations after deletion")
            
        except Exception as e:
            print(f"Delete quotation error: {e}")
            self._send_error(500, "Failed to delete quotation")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def _extract_id_from_path(self):
        """Extract ID from URL path"""
        try:
            # Get the path from the request
            path = self.path
            # Remove query parameters
            path = urlparse(path).path
            # Extract ID from path like /api/quotations/12345
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