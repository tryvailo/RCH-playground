"""
PDF Generator for Free Report
Uses WeasyPrint + Jinja2 for PDF generation
"""
from pathlib import Path
from typing import Dict, Any
import jinja2
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import io


def generate_free_report_pdf(data: Dict[str, Any]) -> bytes:
    """
    Generate PDF report from data dictionary
    
    Args:
        data: Dictionary containing report data (FreeReportResponse dict)
        
    Returns:
        PDF bytes
    """
    # Get template directory
    template_dir = Path(__file__).parent / "templates"
    template_path = template_dir / "free_report.html"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    # Load template
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Create Jinja2 environment
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )
    
    # Add custom filters for number formatting
    def format_number(value, decimals=0):
        """Format number with specified decimals"""
        if value is None:
            return "0"
        try:
            num = float(value)
            if decimals == 0:
                return f"{int(num):,}"
            return f"{num:,.{decimals}f}"
        except (ValueError, TypeError):
            return "0"
    
    env.filters['format_number'] = format_number
    
    # Render template
    template = env.from_string(template_content)
    html_content = template.render(**data)
    
    # Generate PDF with WeasyPrint
    font_config = FontConfiguration()
    
    # Additional CSS for PDF optimization
    pdf_css = CSS(string="""
        @page {
            size: A4;
            margin: 0;
        }
        
        body {
            font-family: 'Inter', 'Arial', sans-serif;
        }
        
        .page {
            page-break-after: always;
        }
        
        .page:last-child {
            page-break-after: auto;
        }
        
        .care-home-card {
            page-break-inside: avoid;
        }
        
        .checklist-item {
            page-break-inside: avoid;
        }
    """)
    
    # Generate PDF
    html = HTML(string=html_content, base_url=str(template_dir))
    pdf_bytes = html.write_pdf(
        stylesheets=[pdf_css],
        font_config=font_config
    )
    
    return pdf_bytes


def generate_pdf_from_response(response: Dict[str, Any]) -> bytes:
    """
    Generate PDF from FreeReportResponse dictionary
    
    Args:
        response: FreeReportResponse dict from API
        
    Returns:
        PDF bytes
    """
    # Ensure data structure is correct
    data = {
        "questionnaire": response.get("questionnaire", {}),
        "care_homes": response.get("care_homes", []),
        "fair_cost_gap": response.get("fair_cost_gap", {}),
        "generated_at": response.get("generated_at", ""),
        "report_id": response.get("report_id", "")
    }
    
    return generate_free_report_pdf(data)

