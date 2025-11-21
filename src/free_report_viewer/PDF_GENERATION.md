# PDF Generation Guide

## Overview

The Free Report Viewer includes PDF generation functionality using **WeasyPrint** and **Jinja2** templates. The PDF report contains 8 pages with comprehensive care home information.

## Installation

Install required dependencies:

```bash
pip install weasyprint jinja2
```

**Note**: WeasyPrint requires system dependencies on some platforms:
- **macOS**: `brew install cairo pango gdk-pixbuf libffi`
- **Linux**: `apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0`
- **Windows**: Usually works out of the box with pip install

## Structure

### Template: `templates/free_report.html`

The HTML template contains 8 pages:

1. **Page 1: Header + Personal Summary**
   - Report header with logo
   - Personal summary card with postcode, budget, care type, CHC probability

2. **Pages 2-4: 3 Care Homes**
   - Each home on a separate page
   - Photo, name, match type badge
   - Weekly cost, CQC rating, distance
   - Price band and FSA rating
   - "Why This Home?" section with key benefits

3. **Page 5: Fair Cost Gap (FULL PAGE RED)**
   - Emotional red gradient background
   - Huge numbers: weekly gap, annual gap, 5-year gap
   - Market price vs MSIF lower bound comparison
   - Explanation text

4. **Page 6: Comparison Table**
   - 3×6 comparison table (3 homes × 6 features)
   - Weekly cost, CQC rating, distance, price band, FSA rating, match type
   - Key insights section

5. **Page 7: Checklist**
   - "What to Ask During Your Visit" checklist
   - 10 key questions with checkboxes
   - Styled as Notion-style cards

6. **Page 8: CTA + Professional Peek**
   - Call-to-action for Professional Report upgrade
   - Professional Peek section with FSA rating and Companies House snippet
   - Deep analysis teaser

## Usage

### In Streamlit Viewer

The PDF download button is automatically available after generating a report:

```python
from free_report_viewer.pdf_generator import generate_pdf_from_response

# Generate PDF from report response
pdf_bytes = generate_pdf_from_response(report.dict())

# Download button in Streamlit
st.download_button(
    label="📄 Download PDF Report",
    data=pdf_bytes,
    file_name="free_report.pdf",
    mime="application/pdf"
)
```

### Via API Endpoint

**POST** `/api/free-report/pdf`

Accepts the same request body as `/api/free-report` and returns PDF bytes:

```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/free-report/pdf",
    json=questionnaire_data
)

with open("report.pdf", "wb") as f:
    f.write(response.content)
```

### Direct Function Call

```python
from free_report_viewer.pdf_generator import generate_free_report_pdf

data = {
    "questionnaire": {...},
    "care_homes": [...],
    "fair_cost_gap": {...},
    "generated_at": "2024-01-01T00:00:00",
    "report_id": "uuid-here"
}

pdf_bytes = generate_free_report_pdf(data)

with open("report.pdf", "wb") as f:
    f.write(pdf_bytes)
```

## Design Features

### Colors
- **Primary Dark**: `#1E2A44` (dark blue)
- **Primary Green**: `#10B981` (accent green)
- **Error Red**: `#EF4444` (Fair Cost Gap)

### Fonts
- **Inter**: Body text, clean and modern
- **Poppins**: Headings, bold and impactful
- Loaded from Google Fonts CDN

### Styling
- Notion-style cards with shadows
- Rounded corners (12px border-radius)
- Premium gradients
- Responsive grid layouts
- Page break controls for PDF

## Customization

### Modify Template

Edit `templates/free_report.html` to customize:
- Colors and fonts
- Layout and spacing
- Content sections
- Styling

### Add Custom Filters

In `pdf_generator.py`, add custom Jinja2 filters:

```python
def custom_filter(value):
    # Your logic here
    return processed_value

env.filters['custom_filter'] = custom_filter
```

Then use in template:
```html
{{ value|custom_filter }}
```

## Troubleshooting

### WeasyPrint Installation Issues

**macOS**:
```bash
brew install cairo pango gdk-pixbuf libffi
pip install weasyprint
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
pip install weasyprint
```

### Font Loading Issues

If fonts don't load in PDF:
1. Check internet connection (Google Fonts CDN)
2. Use system fonts as fallback
3. Download fonts locally and reference them

### Image Loading Issues

If care home photos don't appear:
1. Ensure `photo_url` is absolute URL or accessible path
2. For local images, use `base_url` parameter in WeasyPrint HTML()
3. Check image format (JPEG, PNG supported)

### Page Break Issues

Adjust CSS in template:
```css
.page {
    page-break-after: always;
}

.care-home-card {
    page-break-inside: avoid;
}
```

## Performance

- **Generation Time**: ~2-5 seconds for 8-page PDF
- **File Size**: ~500KB - 2MB depending on images
- **Memory Usage**: ~50-100MB during generation

## Future Enhancements

- [ ] Caching generated PDFs
- [ ] Async PDF generation
- [ ] Custom branding per client
- [ ] Multi-language support
- [ ] Interactive PDF elements
- [ ] Watermarking for free reports

