# PipeCenter Backend API

A Python-based backend API for the PipeCenter React Native application, hosted on Vercel with Blob Storage for data persistence.

## Overview

This backend provides REST APIs for:
- User authentication (username: arumugam, password: pappu)
- Configuration management (pricing configurations)
- Quotation management with 30-day auto-cleanup
- Professional PDF generation with company branding

## Technology Stack

- **Runtime**: Python 3.9
- **Framework**: Vercel Serverless Functions
- **Storage**: Vercel Blob Storage (JSON files)
- **PDF Generation**: ReportLab
- **Authentication**: JWT tokens

## Project Structure

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
└── README.md             # This file
```

## Environment Variables

Required environment variables in Vercel:

```
BLOB_READ_WRITE_TOKEN=<your-vercel-blob-token>
AUTH_SECRET=<random-secret-for-jwt>
AUTH_USERNAME=arumugam
AUTH_PASSWORD=pappu
```

## API Endpoints

### Health Check
- `GET /api/health` - Health check with environment status

### Authentication
- `POST /api/auth/login` - Login with username/password

### Configurations
- `GET /api/configurations` - Get all configurations
- `POST /api/configurations/create` - Create new configuration
- `DELETE /api/configurations/[id]` - Delete configuration

### Quotations
- `GET /api/quotations` - Get all quotations (30-day filtered)
- `POST /api/quotations/create` - Create new quotation
- `PUT /api/quotations/[id]` - Update quotation
- `DELETE /api/quotations/[id]` - Delete quotation
- `GET /api/quotations/pdf/[id]` - Generate and download PDF

## Data Models

### Configuration
```json
{
  "id": "string",
  "name": "string",
  "firstDiscount": "number (0-100)",
  "secondDiscount": "number (0-100)",
  "margin": "number (0-100)",
  "createdAt": "number (timestamp)"
}
```

### Quotation
```json
{
  "id": "string",
  "buyerName": "string",
  "buyerAddress": "string",
  "items": [
    {
      "sno": "number",
      "itemName": "string",
      "rate": "number",
      "quantity": "number",
      "unit": "string",
      "amount": "number"
    }
  ],
  "subtotal": "number",
  "gst": "number",
  "transportCharges": "number",
  "total": "number",
  "createdAt": "number (timestamp)",
  "date": "string (DD/MM/YYYY)"
}
```

## Features

### Authentication
- Simple JWT-based authentication
- Single user support (arumugam/pappu)
- 24-hour token expiration

### Data Storage
- JSON files in Vercel Blob Storage
- Automatic 30-day cleanup for quotations
- Data validation with Pydantic models

### PDF Generation
- Professional PDF formatting with ReportLab
- Company branding and contact information
- Itemized table with proper formatting
- Summary section with totals

### Company Information
- **Name**: Pipe Center
- **Address**: 51, MARIYAPPA STREET, KATTOOR, COIMBATORE, PIN - 641 009
- **Contact**: +91 9894858006 / +91 9894154439

## Deployment

### Prerequisites
1. Vercel account
2. Vercel CLI installed
3. Blob Storage token from Vercel

### Steps
1. Clone repository
2. Navigate to backend directory
3. Set environment variables in Vercel dashboard
4. Deploy with Vercel CLI:
   ```bash
   vercel --prod
   ```

### Environment Setup
```bash
# Set environment variables
vercel env add BLOB_READ_WRITE_TOKEN
vercel env add AUTH_SECRET
```

## Development

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run local development server
vercel dev
```

### Testing Endpoints
```bash
# Health check
curl https://your-app.vercel.app/api/health

# Login
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "arumugam", "password": "pappu"}'
```

## Security Considerations

- JWT tokens for authentication
- Environment variables for sensitive data
- Input validation with Pydantic
- CORS headers configured
- Error handling without sensitive data exposure

## Performance

- Serverless functions with cold start optimization
- Efficient JSON storage and retrieval
- PDF generation optimized for mobile consumption
- 30-day automatic data cleanup

## Monitoring

- Health check endpoint for monitoring
- Error logging for debugging
- Environment status validation

## Support

For issues or questions:
1. Check Vercel function logs
2. Verify environment variables
3. Test API endpoints individually
4. Review error messages in responses

## License

Private project for PipeCenter business application.