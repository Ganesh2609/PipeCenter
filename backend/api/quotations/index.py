from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import asyncio

# Add lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))

from auth import auth_service
from storage import storage_service
from models import ApiResponse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get all quotations (with 30-day auto-cleanup)"""
        try:
            # Authenticate request
            username = auth_service.authenticate_request(self)
            if not username:
                self._send_error(401, "Authentication required")
                return
            
            # Get quotations (includes automatic 30-day cleanup)
            quotations = asyncio.run(storage_service.get_quotations())
            
            # Convert to dict format for JSON serialization
            quotations_data = [quotation.dict() for quotation in quotations]
            
            # Sort by createdAt (newest first)
            quotations_data.sort(key=lambda x: x['createdAt'], reverse=True)
            
            # Send response
            response = ApiResponse(
                success=True,
                data={'quotations': quotations_data},
                message=f"Retrieved {len(quotations_data)} quotations"
            )
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_json = json.dumps(response.dict())
            self.wfile.write(response_json.encode())
            
        except Exception as e:
            print(f"Get quotations error: {e}")
            self._send_error(500, "Failed to retrieve quotations")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
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