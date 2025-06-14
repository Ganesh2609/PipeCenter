from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import asyncio
from urllib.parse import urlparse

# Add lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lib'))

from auth import auth_service
from storage import storage_service
from pdf_generator import QuotationPDFGenerator
from models import ApiResponse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Generate and return PDF for a quotation"""
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
            
            # Get quotation by ID
            quotation = asyncio.run(storage_service.get_quotation_by_id(quotation_id))
            
            if not quotation:
                self._send_error(404, f"Quotation with ID '{quotation_id}' not found")
                return
            
            # Generate PDF
            pdf_bytes = QuotationPDFGenerator.generate(quotation)
            
            # Send PDF response
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', f'attachment; filename="quotation_{quotation_id}.pdf"')
            self.send_header('Content-Length', str(len(pdf_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Expose-Headers', 'Content-Disposition')
            self.end_headers()
            
            self.wfile.write(pdf_bytes)
            
        except Exception as e:
            print(f"PDF generation error: {e}")
            self._send_error(500, f"Failed to generate PDF: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Expose-Headers', 'Content-Disposition')
        self.end_headers()
    
    def _extract_id_from_path(self):
        """Extract ID from URL path"""
        try:
            # Get the path from the request
            path = self.path
            # Remove query parameters
            path = urlparse(path).path
            # Extract ID from path like /api/quotations/pdf/12345
            parts = path.strip('/').split('/')
            if len(parts) >= 4:
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