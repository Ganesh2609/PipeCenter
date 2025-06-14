import json
import os
import requests
from typing import List, Dict, Any, Optional
from .models import Configuration, Quotation

class BlobStorageService:
    """
    Vercel Blob Storage service for managing configurations and quotations
    """
    
    def __init__(self):
        self.token = os.environ.get('BLOB_READ_WRITE_TOKEN')
        if not self.token:
            raise ValueError("BLOB_READ_WRITE_TOKEN environment variable is required")
        
        self.base_url = "https://blob.vercel-storage.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def put_blob(self, filename: str, data: str) -> bool:
        """Upload data to Vercel Blob Storage"""
        try:
            url = f"{self.base_url}/put"
            files = {"file": (filename, data, "application/json")}
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.post(url, files=files, headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"Error uploading to blob storage: {e}")
            return False
    
    async def get_blob(self, filename: str) -> Optional[str]:
        """Download data from Vercel Blob Storage"""
        try:
            url = f"{self.base_url}/get/{filename}"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                return None
            else:
                print(f"Error getting blob: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading from blob storage: {e}")
            return None
    
    async def delete_blob(self, filename: str) -> bool:
        """Delete file from Vercel Blob Storage"""
        try:
            url = f"{self.base_url}/delete/{filename}"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.delete(url, headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting from blob storage: {e}")
            return False

    # Configuration methods
    async def get_configurations(self) -> List[Configuration]:
        """Get all configurations from blob storage"""
        try:
            data = await self.get_blob("configurations.json")
            if not data:
                return []
            
            configs_data = json.loads(data)
            if not isinstance(configs_data, list):
                print("Invalid configurations data format, returning empty list")
                return []
            
            # Validate and filter configurations
            valid_configs = []
            for config_data in configs_data:
                try:
                    config = Configuration(**config_data)
                    valid_configs.append(config)
                except Exception as e:
                    print(f"Invalid configuration data: {e}")
                    continue
            
            return valid_configs
        except Exception as e:
            print(f"Error loading configurations: {e}")
            return []
    
    async def save_configurations(self, configurations: List[Configuration]) -> bool:
        """Save configurations to blob storage"""
        try:
            # Convert to dict format for JSON serialization
            configs_data = [config.dict() for config in configurations]
            data = json.dumps(configs_data, indent=2)
            return await self.put_blob("configurations.json", data)
        except Exception as e:
            print(f"Error saving configurations: {e}")
            return False
    
    # Quotation methods
    async def get_quotations(self) -> List[Quotation]:
        """Get all quotations from blob storage with 30-day cleanup"""
        try:
            data = await self.get_blob("quotations.json")
            if not data:
                return []
            
            quotations_data = json.loads(data)
            if not isinstance(quotations_data, list):
                print("Invalid quotations data format, returning empty list")
                return []
            
            # Auto-cleanup old quotations (30 days)
            import time
            thirty_days_ago = int(time.time() * 1000) - (30 * 24 * 60 * 60 * 1000)
            
            valid_quotations = []
            cleanup_needed = False
            
            for quotation_data in quotations_data:
                try:
                    if quotation_data.get('createdAt', 0) > thirty_days_ago:
                        quotation = Quotation(**quotation_data)
                        valid_quotations.append(quotation)
                    else:
                        cleanup_needed = True
                except Exception as e:
                    print(f"Invalid quotation data: {e}")
                    cleanup_needed = True
                    continue
            
            # Save cleaned data if cleanup was needed
            if cleanup_needed:
                await self.save_quotations(valid_quotations)
            
            return valid_quotations
        except Exception as e:
            print(f"Error loading quotations: {e}")
            return []
    
    async def save_quotations(self, quotations: List[Quotation]) -> bool:
        """Save quotations to blob storage"""
        try:
            # Convert to dict format for JSON serialization
            quotations_data = [quotation.dict() for quotation in quotations]
            data = json.dumps(quotations_data, indent=2)
            return await self.put_blob("quotations.json", data)
        except Exception as e:
            print(f"Error saving quotations: {e}")
            return False
    
    async def get_quotation_by_id(self, quotation_id: str) -> Optional[Quotation]:
        """Get a specific quotation by ID"""
        quotations = await self.get_quotations()
        for quotation in quotations:
            if quotation.id == quotation_id:
                return quotation
        return None

# Initialize storage service
storage_service = BlobStorageService()