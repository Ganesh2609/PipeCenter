# PipeCenter API Documentation

Complete API reference for the PipeCenter backend hosted on Vercel.

**Base URL**: `https://your-app.vercel.app/api`

## Authentication

All endpoints except `/health` and `/auth/login` require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt-token>
```

---

## Endpoints

### Health Check

#### GET /health
Check API health and environment status.

**Request**: No parameters required
**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-14T10:30:00.000Z",
  "version": "1.0.0",
  "service": "PipeCenter Backend API",
  "environment": {
    "has_blob_token": true,
    "has_auth_secret": true,
    "python_version": "3.9.18"
  }
}
```

---

### Authentication

#### POST /auth/login
Authenticate user and receive JWT token.

**Request Body**:
```json
{
  "username": "arumugam",
  "password": "pappu"
}
```

**Response (Success)**:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

---

### Configurations

#### GET /configurations
Retrieve all pricing configurations.

**Authentication**: Required
**Parameters**: None

**Response**:
```json
{
  "success": true,
  "data": {
    "configurations": [
      {
        "id": "1702537200000",
        "name": "Standard Discount",
        "firstDiscount": 5.0,
        "secondDiscount": 2.5,
        "margin": 15.0,
        "createdAt": 1702537200000
      }
    ]
  },
  "message": "Retrieved 1 configurations"
}
```

#### POST /configurations/create
Create a new pricing configuration.

**Authentication**: Required

**Request Body**:
```json
{
  "name": "Premium Discount",
  "firstDiscount": 8.0,
  "secondDiscount": 3.0,
  "margin": 20.0
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "configuration": {
      "id": "1702537800000",
      "name": "Premium Discount",
      "firstDiscount": 8.0,
      "secondDiscount": 3.0,
      "margin": 20.0,
      "createdAt": 1702537800000
    }
  },
  "message": "Configuration created successfully"
}
```

#### DELETE /configurations/[id]
Delete a configuration by ID.

**Authentication**: Required
**URL Parameter**: `id` - Configuration ID

**Response**:
```json
{
  "success": true,
  "message": "Configuration '1702537800000' deleted successfully"
}
```

---

### Quotations

#### GET /quotations
Retrieve all quotations (automatically filters to last 30 days).

**Authentication**: Required
**Parameters**: None

**Response**:
```json
{
  "success": true,
  "data": {
    "quotations": [
      {
        "id": "1702538000000",
        "buyerName": "ABC Corp",
        "buyerAddress": "123 Business St, City",
        "items": [
          {
            "sno": 1,
            "itemName": "Steel Pipe",
            "rate": 100.0,
            "quantity": 10,
            "unit": "pieces",
            "amount": 1000.0
          }
        ],
        "subtotal": 1000.0,
        "gst": 180.0,
        "transportCharges": 50.0,
        "total": 1230.0,
        "createdAt": 1702538000000,
        "date": "14/12/2024"
      }
    ]
  },
  "message": "Retrieved 1 quotations"
}
```

#### POST /quotations/create
Create a new quotation.

**Authentication**: Required

**Request Body**:
```json
{
  "buyerName": "XYZ Industries",
  "buyerAddress": "456 Industrial Ave, City",
  "items": [
    {
      "sno": 1,
      "itemName": "Copper Pipe",
      "rate": 150.0,
      "quantity": 5,
      "unit": "meters",
      "amount": 750.0
    }
  ],
  "subtotal": 750.0,
  "gst": 135.0,
  "transportCharges": 25.0,
  "total": 910.0
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "quotation": {
      "id": "1702538300000",
      "buyerName": "XYZ Industries",
      "buyerAddress": "456 Industrial Ave, City",
      "items": [...],
      "subtotal": 750.0,
      "gst": 135.0,
      "transportCharges": 25.0,
      "total": 910.0,
      "createdAt": 1702538300000,
      "date": "14/12/2024"
    }
  },
  "message": "Quotation created successfully"
}
```

#### PUT /quotations/[id]
Update an existing quotation.

**Authentication**: Required
**URL Parameter**: `id` - Quotation ID

**Request Body**: Same as create, but with updated values

**Response**: Same as create response

#### DELETE /quotations/[id]
Delete a quotation by ID.

**Authentication**: Required
**URL Parameter**: `id` - Quotation ID

**Response**:
```json
{
  "success": true,
  "message": "Quotation '1702538300000' deleted successfully"
}
```

---

### PDF Generation

#### GET /quotations/pdf/[id]
Generate and download PDF for a quotation.

**Authentication**: Required
**URL Parameter**: `id` - Quotation ID

**Response**: PDF file download
- **Content-Type**: `application/pdf`
- **Content-Disposition**: `attachment; filename="quotation_[id].pdf"`

**Error Response** (if quotation not found):
```json
{
  "success": false,
  "error": "Quotation with ID '1702538300000' not found"
}
```

---

## Data Models

### Configuration
```typescript
{
  id: string;                    // Auto-generated timestamp
  name: string;                  // Configuration name (unique)
  firstDiscount: number;         // First discount percentage (0-100)
  secondDiscount: number;        // Second discount percentage (0-100)
  margin: number;                // Margin percentage (0-100)
  createdAt: number;             // Creation timestamp
}
```

### QuotationItem
```typescript
{
  sno: number;                   // Serial number
  itemName: string;              // Item description
  rate: number;                  // Rate per unit
  quantity: number;              // Quantity
  unit: string;                  // Unit of measurement
  amount: number;                // Total amount (rate × quantity)
}
```

### Quotation
```typescript
{
  id: string;                    // Auto-generated timestamp
  buyerName: string;             // Customer name
  buyerAddress: string;          // Customer address
  items: QuotationItem[];        // Array of items
  subtotal: number;              // Subtotal (before GST and transport)
  gst: number;                   // GST amount (18%)
  transportCharges: number;      // Transport charges
  total: number;                 // Final total
  createdAt: number;             // Creation timestamp
  date: string;                  // Date in DD/MM/YYYY format (auto-generated)
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message description"
}
```

### Common HTTP Status Codes

- **200**: Success
- **201**: Created successfully
- **400**: Bad request (validation error, invalid JSON)
- **401**: Unauthorized (authentication required/failed)
- **404**: Resource not found
- **500**: Internal server error

---

## Authentication Flow

1. **Login**: POST `/auth/login` with username/password
2. **Store Token**: Save returned JWT token
3. **Authenticate Requests**: Include token in Authorization header
4. **Token Expiry**: Tokens expire after 24 hours, re-login required

### Example Authentication Header
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFydW11Z2FtIiwiZXhwIjoxNzAyNjI0NDAwLCJpYXQiOjE3MDI1MzgwMDB9.signature
```

---

## CORS Support

All endpoints include CORS headers to support browser requests:

- **Access-Control-Allow-Origin**: `*`
- **Access-Control-Allow-Methods**: `GET, POST, PUT, DELETE, OPTIONS`
- **Access-Control-Allow-Headers**: `Content-Type, Authorization`

---

## Rate Limits

Vercel serverless functions have built-in rate limiting. For production use:
- **Invocations**: 100 per second per function
- **Duration**: 10 seconds maximum per request
- **Memory**: 1008 MB maximum

---

## Company Information in PDFs

Generated PDFs include:

- **Company Name**: Pipe Center
- **Address**: 51, MARIYAPPA STREET, KATTOOR, COIMBATORE, PIN - 641 009
- **Contact**: +91 9894858006 / +91 9894154439

---

## Environment Variables Required

Backend requires these environment variables in Vercel:

```
BLOB_READ_WRITE_TOKEN=<vercel-blob-storage-token>
AUTH_SECRET=<jwt-signing-secret>
AUTH_USERNAME=arumugam
AUTH_PASSWORD=pappu
```

---

## Testing the API

### Using curl

```bash
# Health check
curl https://your-app.vercel.app/api/health

# Login
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "arumugam", "password": "pappu"}'

# Get configurations (with token)
curl https://your-app.vercel.app/api/configurations \
  -H "Authorization: Bearer <your-token>"

# Download PDF
curl https://your-app.vercel.app/api/quotations/pdf/1702538000000 \
  -H "Authorization: Bearer <your-token>" \
  -o quotation.pdf
```

### Using Postman

1. Set base URL: `https://your-app.vercel.app/api`
2. Login to get token
3. Add Authorization header with Bearer token for protected endpoints
4. Test CRUD operations on configurations and quotations

---

## Deployment Notes

- Backend automatically deployed when pushed to Vercel
- Environment variables must be set in Vercel dashboard
- Blob storage token must have read/write permissions
- Function cold starts may take 1-2 seconds initially