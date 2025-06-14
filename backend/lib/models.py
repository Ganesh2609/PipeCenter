from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime

class Configuration(BaseModel):
    id: str
    name: str
    firstDiscount: float
    secondDiscount: float
    margin: float
    createdAt: int
    
    @validator('firstDiscount', 'secondDiscount', 'margin')
    def validate_percentages(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Percentage must be between 0 and 100')
        return v

class QuotationItem(BaseModel):
    sno: int
    itemName: str
    rate: float
    quantity: float
    unit: str
    amount: float
    
    @validator('rate', 'quantity', 'amount')
    def validate_positive_numbers(cls, v):
        if v < 0:
            raise ValueError('Value must be positive')
        return v

class Quotation(BaseModel):
    id: str
    buyerName: str
    buyerAddress: str
    items: List[QuotationItem]
    subtotal: float
    gst: float
    transportCharges: float
    total: float
    createdAt: int
    date: Optional[str] = None
    
    @validator('date', pre=True, always=True)
    def set_date(cls, v):
        if v is None:
            return datetime.now().strftime("%d/%m/%Y")
        return v
    
    @validator('subtotal', 'gst', 'transportCharges', 'total')
    def validate_positive_amounts(cls, v):
        if v < 0:
            raise ValueError('Amount must be positive')
        return v

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    error: Optional[str] = None

class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
    error: Optional[str] = None