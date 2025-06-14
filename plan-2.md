# PipeCenter Backend Migration Plan (Plan 2)

## Project Overview
Migration of PipeCenter React Native app from local AsyncStorage to a **Python backend hosted on Vercel** with **Vercel Blob Storage** for data persistence and **proper PDF generation** capabilities.

**Current Status**: React Native 0.74.5 app with local storage (Phase 6 complete)
**Target**: Full-stack app with Python API backend and enhanced PDF generation

---

## Migration Objectives

### Core Goals
- [x] **Backend Infrastructure**: Python API hosted on Vercel
- [x] **Data Storage**: Migrate from AsyncStorage to Vercel Blob Storage (.json files)
- [x] **Authentication**: Simple username/password auth (arumugam/pappu)
- [x] **PDF Generation**: Professional PDF export with proper table formatting
- [x] **Company Details**: Add missing company information to PDFs
- [x] **Date Enhancement**: Add current date to quotations
- [x] **API Integration**: Update React Native app to use REST APIs

### Enhanced Features
- Professional PDF generation with company branding
- Centralized data storage accessible from multiple devices
- Backup and data persistence beyond device storage
- Better quotation formatting and export capabilities

---

## Phase 1: Backend Architecture & Setup ⏳

### 1.1 Project Structure
```
backend/
├── api/                    # Vercel serverless functions
│   ├── auth/
│   │   └── login.py       # POST /api/auth/login
│   ├── configurations/
│   │   ├── index.py       # GET /api/configurations
│   │   ├── create.py      # POST /api/configurations
│   │   └── [id].py        # DELETE /api/configurations/[id]
│   ├── quotations/
│   │   ├── index.py       # GET /api/quotations
│   │   ├── create.py      # POST /api/quotations
│   │   ├── [id].py        # PUT/DELETE /api/quotations/[id]
│   │   └── pdf/[id].py    # GET /api/quotations/pdf/[id]
│   └── health.py          # GET /api/health
├── lib/
│   ├── auth.py            # Authentication utilities
│   ├── storage.py         # Vercel Blob Storage utilities
│   ├── pdf_generator.py   # PDF generation with ReportLab
│   └── models.py          # Data models and validation
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
└── README.md             # Backend documentation
```

### 1.2 Technology Stack
- **Runtime**: Python 3.9+ (Vercel supported)
- **Framework**: FastAPI/Flask (lightweight REST API)
- **Storage**: Vercel Blob Storage (JSON files)
- **PDF**: ReportLab (professional PDF generation)
- **Authentication**: JWT tokens with simple user validation
- **Validation**: Pydantic for data models

### 1.3 Vercel Configuration
```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.9"
    }
  },
  "env": {
    "BLOB_READ_WRITE_TOKEN": "@blob-token",
    "AUTH_SECRET": "@auth-secret"
  }
}
```

---

## Phase 2: Data Models & Storage ⏳

### 2.1 Enhanced Data Models
```python
# lib/models.py
from pydantic import BaseModel, validator
from typing import List
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
    date: str  # NEW: Current date in DD/MM/YYYY format
    
    @validator('date', pre=True, always=True)
    def set_date(cls, v):
        return datetime.now().strftime("%d/%m/%Y")
```

### 2.2 Blob Storage Structure
```
vercel-blob-storage/
├── configurations.json    # All configurations
├── quotations.json       # All quotations
└── pdfs/                # Generated PDF files
    ├── quotation_[id].pdf
    └── ...
```

### 2.3 Storage Service
```python
# lib/storage.py
import json
from vercel_blob import put, get, delete
import os

class BlobStorageService:
    @staticmethod
    async def get_configurations():
        try:
            response = await get('configurations.json')
            return json.loads(response)
        except:
            return []
    
    @staticmethod
    async def save_configurations(configurations):
        data = json.dumps(configurations, indent=2)
        await put('configurations.json', data)
    
    # Similar methods for quotations...
```

---

## Phase 3: API Endpoints ⏳

### 3.1 Authentication API
```python
# api/auth/login.py
from lib.auth import validate_user, generate_token

def handler(request):
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if validate_user(username, password):  # arumugam/pappu
            token = generate_token(username)
            return {'success': True, 'token': token}
        else:
            return {'success': False, 'error': 'Invalid credentials'}, 401
```

### 3.2 Configurations API
```python
# api/configurations/index.py - GET
# api/configurations/create.py - POST  
# api/configurations/[id].py - DELETE

# Example GET endpoint
def handler(request):
    if request.method == 'GET':
        configs = await BlobStorageService.get_configurations()
        return {'success': True, 'data': configs}
```

### 3.3 Quotations API
```python
# api/quotations/index.py - GET (with 30-day filtering)
# api/quotations/create.py - POST
# api/quotations/[id].py - PUT/DELETE

# Enhanced with date field
def handler(request):
    if request.method == 'POST':
        quotation_data = request.json
        quotation = Quotation(**quotation_data)  # Auto-adds current date
        # Save to blob storage...
```

### 3.4 PDF Generation API
```python
# api/quotations/pdf/[id].py
from lib.pdf_generator import QuotationPDFGenerator

def handler(request, id):
    if request.method == 'GET':
        quotation = await get_quotation_by_id(id)
        pdf_bytes = QuotationPDFGenerator.generate(quotation)
        
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=quotation_{id}.pdf'}
        )
```

---

## Phase 4: Professional PDF Generation ⏳

### 4.1 Company Information
```python
COMPANY_INFO = {
    'name': 'Pipe Center',
    'address': '51, MARIYAPPA STREET, KATTOOR,\nCOIMBATORE, PIN - 641 009',
    'contact': '+91 9894858006 / +91 9894154439'
}
```

### 4.2 PDF Template Structure
```python
# lib/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class QuotationPDFGenerator:
    @staticmethod
    def generate(quotation: Quotation) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Company Header
        elements.append(company_header())
        
        # Quotation Details
        elements.append(quotation_details(quotation))
        
        # Items Table
        elements.append(items_table(quotation.items))
        
        # Summary Table
        elements.append(summary_table(quotation))
        
        # Footer
        elements.append(footer())
        
        doc.build(elements)
        return buffer.getvalue()
    
    @staticmethod
    def company_header():
        styles = getSampleStyleSheet()
        company_style = ParagraphStyle(
            'CompanyHeader',
            parent=styles['Heading1'],
            fontSize=20,
            alignment=1,  # Center
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        return [
            Paragraph("PIPE CENTER", company_style),
            Paragraph("51, MARIYAPPA STREET, KATTOOR,<br/>COIMBATORE, PIN - 641 009", styles['Normal']),
            Paragraph("Contact: +91 9894858006 / +91 9894154439", styles['Normal']),
            Spacer(1, 20)
        ]
    
    @staticmethod
    def items_table(items):
        data = [['S.No', 'Item Name', 'Rate (₹)', 'Quantity', 'Unit', 'Amount (₹)']]
        
        for item in items:
            data.append([
                str(item.sno),
                item.itemName,
                f"₹{item.rate:.2f}",
                str(item.quantity),
                item.unit,
                f"₹{item.amount:.2f}"
            ])
        
        table = Table(data, colWidths=[40, 150, 80, 60, 60, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
```

---

## Phase 5: React Native Frontend Updates ⏳

### 5.1 API Service Layer
```typescript
// src/services/apiService.ts
class ApiService {
  private baseURL = 'https://your-vercel-app.vercel.app/api';
  private token: string | null = null;

  async login(username: string, password: string) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    if (data.success) {
      this.token = data.token;
      await AsyncStorage.setItem('auth_token', data.token);
    }
    return data;
  }

  async getConfigurations(): Promise<Configuration[]> {
    const response = await this.authenticatedFetch('/configurations');
    const data = await response.json();
    return data.success ? data.data : [];
  }

  async createConfiguration(config: Configuration): Promise<boolean> {
    const response = await this.authenticatedFetch('/configurations/create', {
      method: 'POST',
      body: JSON.stringify(config)
    });
    const data = await response.json();
    return data.success;
  }

  private async authenticatedFetch(endpoint: string, options: RequestInit = {}) {
    return fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
        ...options.headers
      }
    });
  }
}
```

### 5.2 Updated Storage Service
```typescript
// src/services/storage.ts - Updated to use API
import { ApiService } from './apiService';

export class StorageService {
  private static api = new ApiService();

  static async getConfigurations(): Promise<Configuration[]> {
    try {
      return await this.api.getConfigurations();
    } catch (error) {
      console.error('Error loading configurations:', error);
      return [];
    }
  }

  static async saveConfigurations(configurations: Configuration[]): Promise<void> {
    // API handles individual creates/updates/deletes
    throw new Error('Use individual create/update/delete methods');
  }

  static async getQuotations(): Promise<Quotation[]> {
    try {
      return await this.api.getQuotations();
    } catch (error) {
      console.error('Error loading quotations:', error);
      return [];
    }
  }
}
```

### 5.3 Enhanced Quotation Model
```typescript
// src/types/index.ts - Add date field
export interface Quotation {
  id: string;
  buyerName: string;
  buyerAddress: string;
  items: QuotationItem[];
  subtotal: number;
  gst: number;
  transportCharges: number;
  total: number;
  createdAt: number;
  date: string; // NEW: DD/MM/YYYY format
}
```

### 5.4 PDF Export Integration
```typescript
// src/services/pdfService.ts - Updated for API
export class PDFService {
  private static api = new ApiService();

  static async generateAndSharePDF(quotationId: string): Promise<void> {
    try {
      const pdfBlob = await this.api.getPDFBlob(quotationId);
      
      // Save to device and share
      const fileUri = await this.savePDFToFile(pdfBlob, quotationId);
      await Share.open({
        url: fileUri,
        type: 'application/pdf',
        title: `Quotation ${quotationId}`
      });
    } catch (error) {
      console.error('PDF generation failed:', error);
      throw new Error('Failed to generate PDF');
    }
  }
}
```

---

## Phase 6: Authentication & Security ⏳

### 6.1 Login Screen
```typescript
// src/screens/Login.tsx - NEW
export const LoginScreen: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const result = await ApiService.login(username, password);
      if (result.success) {
        // Navigate to main app
        navigation.navigate('MainTabs');
      } else {
        Alert.alert('Login Failed', result.error);
      }
    } catch (error) {
      Alert.alert('Error', 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Pipe Center</Text>
      <Input
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
      />
      <Input
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button
        title={loading ? "Logging in..." : "Login"}
        onPress={handleLogin}
        disabled={loading}
      />
    </View>
  );
};
```

### 6.2 Navigation Updates
```typescript
// src/navigation/AppNavigator.tsx - Add auth flow
export const AppNavigator: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      setIsAuthenticated(!!token);
    } catch (error) {
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainTabNavigator /> : <LoginScreen />}
    </NavigationContainer>
  );
};
```

---

## Phase 7: Testing & Deployment ⏳

### 7.1 Backend Testing
- [ ] Unit tests for all API endpoints
- [ ] PDF generation testing
- [ ] Blob storage operations testing
- [ ] Authentication flow testing
- [ ] Error handling and edge cases

### 7.2 Frontend Testing
- [ ] API integration testing
- [ ] Authentication flow testing
- [ ] PDF download and sharing testing
- [ ] Offline handling (fallback behavior)
- [ ] Error boundary testing

### 7.3 Deployment Checklist
- [ ] Vercel environment variables configured
- [ ] Blob storage permissions set
- [ ] API endpoints deployed and accessible
- [ ] React Native app updated with production API URLs
- [ ] SSL certificate verification
- [ ] Performance testing on target devices

---

## Implementation Timeline

### Week 1: Backend Foundation
- [ ] **Days 1-2**: Set up Vercel project structure and configuration
- [ ] **Days 3-4**: Implement authentication and basic API endpoints
- [ ] **Days 5-7**: Set up Blob storage integration and data models

### Week 2: API Development
- [ ] **Days 1-3**: Complete all CRUD operations for configurations and quotations
- [ ] **Days 4-5**: Implement PDF generation with ReportLab
- [ ] **Days 6-7**: Testing and error handling

### Week 3: Frontend Integration
- [ ] **Days 1-2**: Update React Native app with API service layer
- [ ] **Days 3-4**: Implement authentication flow and login screen
- [ ] **Days 5-7**: Update all screens to use API instead of AsyncStorage

### Week 4: Testing & Polish
- [ ] **Days 1-3**: Comprehensive testing and bug fixes
- [ ] **Days 4-5**: PDF generation testing and formatting improvements
- [ ] **Days 6-7**: Final deployment and documentation

---

## Required Environment Variables

### Vercel Environment Variables
```
BLOB_READ_WRITE_TOKEN=<your-vercel-blob-token>
AUTH_SECRET=<random-secret-for-jwt>
AUTH_USERNAME=arumugam
AUTH_PASSWORD=pappu
```

### React Native Environment Variables
```
API_BASE_URL=https://your-vercel-app.vercel.app/api
```

---

## Success Criteria

### Backend Requirements
- ✅ All API endpoints functional and accessible
- ✅ Authentication working with username/password
- ✅ Data persisting to Vercel Blob Storage as JSON files
- ✅ Professional PDF generation with company branding
- ✅ Proper error handling and validation

### Frontend Requirements
- ✅ Seamless migration from AsyncStorage to API calls
- ✅ Login screen and authentication flow
- ✅ All existing functionality preserved
- ✅ PDF export working with improved formatting
- ✅ Current date displayed in quotations

### Technical Requirements
- ✅ App works on Pixel 3a Android 12.0
- ✅ Fast API response times (<2 seconds)
- ✅ Professional PDF output
- ✅ Proper error handling for network issues
- ✅ Secure authentication implementation

---

## Post-Migration Benefits

1. **Centralized Data**: Access quotations and configurations from multiple devices
2. **Professional PDFs**: Proper table formatting with company branding
3. **Data Backup**: Automatic cloud storage prevents data loss
4. **Scalability**: Backend can handle multiple users if needed in future
5. **Enhanced Features**: Better date handling and company information
6. **Reliability**: Professional PDF generation with ReportLab

---

## Risk Mitigation

### Potential Issues
1. **Network Dependency**: App now requires internet connection
   - **Mitigation**: Implement offline caching and sync when online
   
2. **API Rate Limits**: Vercel serverless function limits
   - **Mitigation**: Optimize API calls and implement request batching
   
3. **PDF Generation Performance**: Large PDFs may be slow
   - **Mitigation**: Optimize PDF generation and add loading indicators

4. **Authentication Security**: Simple username/password
   - **Mitigation**: Use JWT tokens and implement session management

---

## Future Enhancements (Phase 8+)

1. **Multi-user Support**: Extend beyond single user
2. **Data Export/Import**: Backup and restore functionality
3. **Email Integration**: Send PDFs directly via email
4. **Advanced PDF Templates**: Multiple quotation formats
5. **Analytics Dashboard**: Usage statistics and reporting
6. **Mobile App Notifications**: For quotation updates

---

## Dependencies to Install

### Backend Dependencies
```
requirements.txt:
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-jose[cryptography]==3.3.0
reportlab==4.0.7
vercel-blob==0.1.0
python-multipart==0.0.6
```

### Frontend Dependencies (Additional)
```json
{
  "react-native-keychain": "^8.2.0",
  "react-native-share": "^10.0.2"
}
```

---

## Documentation Files to Create

1. **backend/README.md**: Backend setup and deployment guide
2. **backend/API_DOCUMENTATION.md**: Complete API reference
3. **MIGRATION_GUIDE.md**: Step-by-step migration instructions
4. **PDF_TEMPLATE_GUIDE.md**: PDF customization documentation

---

## Final Notes

This migration plan transforms PipeCenter from a local-only app to a full-stack application with professional PDF generation capabilities. The backend uses Vercel's serverless architecture for scalability and reliability, while maintaining the React Native frontend's user experience.

The implementation prioritizes:
- **Simplicity**: Single user authentication as requested
- **Reliability**: Professional PDF generation with proper formatting
- **Maintainability**: Clean separation between frontend and backend
- **Performance**: Optimized for low-end devices like Pixel 3a

**Ready for Implementation**: All phases are clearly defined with specific deliverables and success criteria.