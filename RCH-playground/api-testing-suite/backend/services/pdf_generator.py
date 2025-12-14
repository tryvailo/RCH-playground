"""
PDF Generator Service
Generates PDF reports using WeasyPrint and Jinja2 templates
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Service for generating PDF reports from HTML templates"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize PDF generator
        
        Args:
            templates_dir: Directory containing Jinja2 templates (defaults to templates/pdf)
        """
        # Determine templates directory
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # Default: api-testing-suite/backend/templates/pdf
            backend_dir = Path(__file__).parent.parent
            self.templates_dir = backend_dir / "templates" / "pdf"
        
        # Create templates directory if it doesn't exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Font configuration for better typography
        self.font_config = FontConfiguration()
        
        logger.info(f"PDF Generator initialized with templates dir: {self.templates_dir}")
    
    def generate_free_report_pdf(
        self,
        report_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF for free report
        
        Args:
            report_data: Report data dictionary (from /api/free-report response)
            output_path: Optional path to save PDF file (for debugging)
        
        Returns:
            PDF content as bytes
        """
        try:
            # Load HTML template
            template = self.jinja_env.get_template("free_report.html")
            
            # Prepare template context
            context = self._prepare_context(report_data)
            
            # Render HTML
            html_content = template.render(**context)
            
            # Generate PDF from HTML
            pdf_bytes = self._html_to_pdf(html_content)
            
            # Optionally save to file (for debugging)
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                logger.info(f"PDF saved to: {output_path}")
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise
    
    def _prepare_context(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare context data for template rendering
        
        Args:
            report_data: Raw report data from API
        
        Returns:
            Formatted context dictionary
        """
        # Extract data
        questionnaire = report_data.get("questionnaire", {})
        care_homes = report_data.get("care_homes", [])
        fair_cost_gap = report_data.get("fair_cost_gap", {})
        generated_at = report_data.get("generated_at", datetime.now().isoformat())
        report_id = report_data.get("report_id", "unknown")
        
        # Format generated date
        try:
            gen_date = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
            formatted_date = gen_date.strftime("%d %B %Y")
            formatted_time = gen_date.strftime("%H:%M")
        except:
            formatted_date = datetime.now().strftime("%d %B %Y")
            formatted_time = datetime.now().strftime("%H:%M")
        
        # Format care homes
        formatted_homes = []
        for home in care_homes:
            formatted_home = {
                "name": home.get("name", "Unknown"),
                "postcode": home.get("postcode", ""),
                "address": home.get("address", ""),
                "distance_km": round(home.get("distance_km", 0), 1),
                "distance_miles": round(home.get("distance_km", 0) * 0.621371, 1),
                "weekly_cost": home.get("weekly_cost", 0),
                "rating": home.get("rating", "Not rated"),
                "match_type": home.get("match_type", "Recommended"),
                "why_this_home": home.get("why_this_home", "Recommended based on quality, price, and location."),
                "fsa_rating": home.get("fsa_rating"),
                "fsa_color": home.get("fsa_color"),
                "fsa_rating_date": home.get("fsa_rating_date"),
                "contact_phone": home.get("contact_phone"),
                "website": home.get("website"),
                "features": home.get("features", []),
                "care_types": home.get("care_types", []),
            }
            formatted_homes.append(formatted_home)
        
        # Format Fair Cost Gap
        gap_week = fair_cost_gap.get("gap_week", 0)
        gap_year = fair_cost_gap.get("gap_year", 0)
        gap_5year = fair_cost_gap.get("gap_5year", 0)
        market_price = fair_cost_gap.get("market_price", 0)
        msif_lower = fair_cost_gap.get("msif_lower_bound", 0)
        
        formatted_gap = {
            "gap_week": round(gap_week, 2),
            "gap_year": round(gap_year, 2),
            "gap_5year": round(gap_5year, 2),
            "market_price": round(market_price, 2),
            "msif_lower_bound": round(msif_lower, 2),
            "local_authority": fair_cost_gap.get("local_authority", "Unknown"),
            "care_type": fair_cost_gap.get("care_type", "Unknown"),
            "explanation": fair_cost_gap.get("explanation", ""),
            "gap_text": fair_cost_gap.get("gap_text", ""),
            "recommendations": fair_cost_gap.get("recommendations", []),
        }
        
        # Calculate percentage above fair price
        if msif_lower > 0:
            gap_percent = round((gap_week / msif_lower) * 100, 1)
        else:
            gap_percent = 0
        
        formatted_gap["gap_percent"] = gap_percent
        
        return {
            "report_id": report_id,
            "generated_date": formatted_date,
            "generated_time": formatted_time,
            "postcode": questionnaire.get("postcode", ""),
            "care_type": questionnaire.get("care_type", "residential"),
            "budget": questionnaire.get("budget"),
            "care_homes": formatted_homes,
            "fair_cost_gap": formatted_gap,
            "total_homes": len(formatted_homes),
        }
    
    def _html_to_pdf(self, html_content: str) -> bytes:
        """
        Convert HTML to PDF using WeasyPrint
        
        Args:
            html_content: HTML content as string
        
        Returns:
            PDF content as bytes
        """
        try:
            # Load CSS
            css_path = self.templates_dir / "styles.css"
            css_content = None
            if css_path.exists():
                with open(css_path, 'r') as f:
                    css_content = CSS(string=f.read(), font_config=self.font_config)
            
            # Generate PDF
            html = HTML(string=html_content, base_url=str(self.templates_dir))
            
            if css_content:
                pdf_bytes = html.write_pdf(stylesheets=[css_content], font_config=self.font_config)
            else:
                pdf_bytes = html.write_pdf(font_config=self.font_config)
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error converting HTML to PDF: {e}")
            raise


def generate_pdf_from_response(report_data: Dict[str, Any]) -> bytes:
    """
    Convenience function to generate PDF from report data
    
    Args:
        report_data: Report data dictionary
    
    Returns:
        PDF content as bytes
    """
    generator = PDFGenerator()
    return generator.generate_free_report_pdf(report_data)

