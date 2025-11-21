# PDF Generation Setup Guide

## Overview

Backend PDF generation has been implemented using WeasyPrint and Jinja2 templates. PDFs are automatically generated when reports are created and can be uploaded to AWS S3 for storage and distribution.

## Features

✅ **WeasyPrint Integration** - Server-side PDF generation  
✅ **Jinja2 Templates** - HTML templates for PDF rendering  
✅ **S3 Storage** - Automatic upload to AWS S3  
✅ **Presigned URLs** - Secure, time-limited download links  
✅ **Error Handling** - Graceful fallback if PDF generation fails  

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

This will install:
- `weasyprint==60.1` - PDF generation
- `jinja2==3.1.2` - Template engine
- `boto3==1.34.0` - AWS S3 client
- `pillow==10.1.0` - Image processing (required by WeasyPrint)

2. **System dependencies (for WeasyPrint):**

On macOS:
```bash
brew install cairo pango gdk-pixbuf libffi
```

On Ubuntu/Debian:
```bash
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

On CentOS/RHEL:
```bash
sudo yum install cairo pango gdk-pixbuf2 libffi
```

## Configuration

### AWS S3 Setup

1. **Create S3 bucket:**
   - Go to AWS Console → S3
   - Create bucket: `rightcarehome-reports`
   - Set region (e.g., `us-east-1`)
   - Configure CORS if needed for direct access

2. **Create IAM user:**
   - Go to AWS Console → IAM
   - Create user with programmatic access
   - Attach policy: `AmazonS3FullAccess` (or custom policy for specific bucket)
   - Save Access Key ID and Secret Access Key

3. **Set environment variables:**
```bash
export AWS_S3_BUCKET=rightcarehome-reports
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

Or create `.env` file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Alternative: Use Default AWS Credentials

If you don't set environment variables, the service will try to use:
- IAM role (if running on EC2)
- `~/.aws/credentials` file
- Environment variables from AWS CLI

## Usage

### Automatic PDF Generation

PDFs are automatically generated when creating a free report:

```python
POST /api/free-report
{
  "postcode": "SW1A 1AA",
  "budget": 1200.0,
  "care_type": "residential"
}
```

Response includes `pdf_url` if S3 is configured:
```json
{
  "report_id": "abc123...",
  "care_homes": [...],
  "fair_cost_gap": {...},
  "pdf_url": "https://s3.amazonaws.com/...?signature=..."
}
```

### Manual PDF Generation

Generate PDF directly:

```python
POST /api/free-report/pdf
{
  "report_id": "abc123...",
  "care_homes": [...],
  "fair_cost_gap": {...}
}
```

Returns PDF file as download.

### Retrieve PDF by ID

```python
GET /api/free-report/pdf/{report_id}
```

Returns redirect to S3 URL or presigned URL.

## File Structure

```
api-testing-suite/backend/
├── services/
│   ├── pdf_generator.py      # PDF generation service
│   └── s3_service.py         # S3 upload service
├── templates/
│   └── pdf/
│       ├── free_report.html   # Main PDF template
│       └── styles.css         # PDF styles
└── main.py                    # API endpoints
```

## Template Customization

Edit `templates/pdf/free_report.html` to customize PDF layout.

Template variables:
- `report_id` - Unique report identifier
- `generated_date` - Report generation date
- `generated_time` - Report generation time
- `postcode` - User postcode
- `care_type` - Care type (residential/nursing/dementia)
- `budget` - User budget
- `care_homes` - List of recommended homes
- `fair_cost_gap` - Fair cost gap data

## Troubleshooting

### PDF Generation Fails

1. **Check WeasyPrint installation:**
```bash
python -c "import weasyprint; print('OK')"
```

2. **Check system dependencies:**
```bash
# On macOS
brew list | grep cairo

# On Linux
dpkg -l | grep cairo
```

3. **Check logs:**
   - Look for error messages in console output
   - PDF generation errors are logged but don't fail the request

### S3 Upload Fails

1. **Check credentials:**
```bash
aws s3 ls s3://rightcarehome-reports/
```

2. **Check bucket permissions:**
   - Ensure IAM user has `PutObject` permission
   - Check bucket CORS configuration

3. **Check network:**
   - Ensure server can reach AWS S3
   - Check firewall/proxy settings

### PDF Looks Wrong

1. **Check template:**
   - Verify HTML template syntax
   - Check CSS styles

2. **Check fonts:**
   - WeasyPrint uses system fonts
   - Google Fonts (Inter) may not render correctly
   - Consider using web-safe fonts

## Performance

- **PDF Generation:** ~2-5 seconds per report
- **S3 Upload:** ~1-2 seconds per report
- **Total:** ~3-7 seconds added to report generation

PDF generation is non-blocking - if it fails, the API still returns the report data.

## Security

- **Presigned URLs:** Expire after 30 days
- **Bucket Policy:** Configure bucket to allow only authenticated uploads
- **CORS:** Configure CORS for web access if needed

## Cost Estimation

- **S3 Storage:** ~£0.023 per GB/month
- **S3 Requests:** ~£0.0004 per 1,000 PUT requests
- **Data Transfer:** ~£0.09 per GB out

For 1,000 reports/month:
- Storage: ~500 MB = £0.01/month
- Requests: 1,000 PUTs = £0.0004/month
- **Total: ~£0.01/month**

## Next Steps

1. ✅ PDF generation implemented
2. ✅ S3 upload implemented
3. ⏳ Email integration (send PDF link)
4. ⏳ PDF optimization (file size reduction)
5. ⏳ Watermarking (optional)

