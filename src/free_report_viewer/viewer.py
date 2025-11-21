"""
Streamlit Free Report Viewer
"""
import streamlit as st
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import sys

# Add src to path if not already added
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from free_report_viewer.models import QuestionnaireResponse, FreeReportResponse, CareHome, FairCostGap
from free_report_viewer.api import FreeReportAPIClient
from free_report_viewer.pdf_generator import generate_pdf_from_response


# Custom CSS for premium styling
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif;
        color: #1E2A44;
    }
    
    .stButton>button {
        background-color: #10B981;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #059669;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #10B981;
    }
    
    .card-danger {
        border-left-color: #EF4444;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1E2A44 0%, #2D3A5A 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(30, 42, 68, 0.3);
    }
    
    .care-home-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border: 1px solid #e5e7eb;
        transition: all 0.3s;
    }
    
    .care-home-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    .fair-cost-gap {
        background: #FEF2F2;
        border: 2px solid #EF4444;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
</style>
"""


def load_sample_questionnaires() -> Dict[str, str]:
    """Load sample questionnaire files"""
    sample_dir = Path(__file__).parent.parent.parent / "data" / "sample_questionnaires"
    questionnaires = {}
    
    if sample_dir.exists():
        for file in sample_dir.glob("*.json"):
            questionnaires[file.stem] = str(file)
    
    return questionnaires


def parse_questionnaire(file_path: str) -> Optional[QuestionnaireResponse]:
    """Parse questionnaire JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return QuestionnaireResponse(**data)
    except Exception as e:
        st.error(f"Error parsing questionnaire: {str(e)}")
        return None


def parse_uploaded_questionnaire(uploaded_file) -> Optional[QuestionnaireResponse]:
    """Parse uploaded questionnaire JSON"""
    try:
        data = json.load(uploaded_file)
        return QuestionnaireResponse(**data)
    except Exception as e:
        st.error(f"Error parsing uploaded file: {str(e)}")
        return None


def display_questionnaire_card(questionnaire: QuestionnaireResponse):
    """Display questionnaire summary card"""
    st.markdown("### 📋 Questionnaire Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("📍 Postcode", questionnaire.postcode)
        if questionnaire.budget:
            st.metric("💰 Weekly Budget", f"£{questionnaire.budget:,.0f}")
    
    with col2:
        if questionnaire.care_type:
            st.metric("🏥 Care Type", questionnaire.care_type.title())
        if questionnaire.chc_probability is not None:
            st.metric(
                "📊 CHC Probability", 
                f"{questionnaire.chc_probability:.1f}%"
            )
    
    if questionnaire.address or questionnaire.city:
        st.info(f"📍 Location: {questionnaire.address or ''} {questionnaire.city or ''}".strip())


def display_care_home_card(home: CareHome, index: int):
    """Display care home card"""
    st.markdown(f"### 🏠 {home.name}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Weekly Cost", f"£{home.weekly_cost:,.0f}")
        if home.rating:
            st.metric("⭐ Rating", home.rating)
    
    with col2:
        if home.distance_km:
            st.metric("📍 Distance", f"{home.distance_km:.1f} km")
        if home.care_types:
            st.write("**Care Types:**")
            for ct in home.care_types:
                st.write(f"- {ct.title()}")
    
    with col3:
        if home.features:
            st.write("**Features:**")
            for feature in home.features[:3]:
                st.write(f"- {feature}")
            if len(home.features) > 3:
                st.caption(f"+ {len(home.features) - 3} more")
    
    if home.contact_phone or home.website:
        st.divider()
        col_contact = st.columns(2)
        if home.contact_phone:
            col_contact[0].write(f"📞 {home.contact_phone}")
        if home.website:
            col_contact[1].write(f"🌐 [{home.website}]({home.website})")


def display_fair_cost_gap(fair_cost_gap: FairCostGap):
    """Display Fair Cost Gap block - ОБЯЗАТЕЛЬНЫЙ эмоциональный блок (красный, огромные цифры)"""
    
    # Эмоциональный заголовок
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); 
                    border-radius: 16px; 
                    padding: 2rem; 
                    margin: 2rem 0;
                    box-shadow: 0 8px 24px rgba(239, 68, 68, 0.3);">
            <h2 style="color: white; font-size: 2.5rem; font-weight: 700; margin: 0; text-align: center;">
                ⚠️ FAIR COST GAP IDENTIFIED
            </h2>
            <p style="color: white; text-align: center; font-size: 1.2rem; margin-top: 0.5rem; opacity: 0.9;">
                The gap between market price and MSIF fair cost lower bound
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Огромные цифры в красном блоке
    st.markdown(
        f"""
        <div style="background: #FEF2F2; 
                    border: 3px solid #EF4444; 
                    border-radius: 16px; 
                    padding: 2.5rem; 
                    margin: 1.5rem 0;">
        """,
        unsafe_allow_html=True
    )
    
    # Три колонки с огромными цифрами
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 0.9rem; color: #7F1D1D; font-weight: 600; margin-bottom: 0.5rem;">
                    WEEKLY GAP
                </div>
                <div style="font-size: 3.5rem; color: #EF4444; font-weight: 700; font-family: 'Poppins', sans-serif;">
                    £{fair_cost_gap.gap_week:,.0f}
                </div>
                <div style="font-size: 0.85rem; color: #991B1B; margin-top: 0.5rem;">
                    per week
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 0.9rem; color: #7F1D1D; font-weight: 600; margin-bottom: 0.5rem;">
                    ANNUAL GAP
                </div>
                <div style="font-size: 3.5rem; color: #EF4444; font-weight: 700; font-family: 'Poppins', sans-serif;">
                    £{fair_cost_gap.gap_year:,.0f}
                </div>
                <div style="font-size: 0.85rem; color: #991B1B; margin-top: 0.5rem;">
                    per year
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 0.9rem; color: #7F1D1D; font-weight: 600; margin-bottom: 0.5rem;">
                    5-YEAR GAP
                </div>
                <div style="font-size: 3.5rem; color: #EF4444; font-weight: 700; font-family: 'Poppins', sans-serif;">
                    £{fair_cost_gap.gap_5year:,.0f}
                </div>
                <div style="font-size: 0.85rem; color: #991B1B; margin-top: 0.5rem;">
                    over 5 years
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Детальная информация
    st.markdown("---")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("### 📊 Market Analysis")
        st.metric("Market Price (Average)", f"£{fair_cost_gap.market_price:,.2f}/week")
        st.metric("MSIF Lower Bound", f"£{fair_cost_gap.msif_lower_bound:,.2f}/week")
    
    with col_info2:
        st.markdown("### 📍 Location Details")
        st.metric("Local Authority", fair_cost_gap.local_authority)
        st.metric("Care Type", fair_cost_gap.care_type.title())
    
    # Объяснение
    st.markdown("---")
    st.markdown("### 📝 Explanation")
    st.warning(f"**{fair_cost_gap.explanation}**")
    
    # Рекомендации
    if fair_cost_gap.recommendations:
        st.markdown("### 💡 Recommendations")
        for i, rec in enumerate(fair_cost_gap.recommendations, 1):
            st.markdown(f"**{i}.** {rec}")


def display_web_version_report(report: FreeReportResponse):
    """Display premium web version of the report"""
    
    # Animated counter for Fair Cost Gap (simplified for Streamlit)
    def display_animated_counter(target_value: float, prefix: str = "£"):
        """Display animated counter effect using CSS animation"""
        # Use CSS animation for smoother effect with responsive design
        st.markdown(
            f"""
            <style>
                @keyframes countUp {{
                    from {{
                        opacity: 0;
                        transform: translateY(20px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
                .animated-counter {{
                    animation: countUp 1.5s ease-out;
                    font-family: 'Poppins', sans-serif;
                    font-size: 5rem;
                    font-weight: 800;
                    color: white;
                    text-align: center;
                    text-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }}
                @media (max-width: 768px) {{
                    .animated-counter {{
                        font-size: 3rem;
                    }}
                }}
            </style>
            <div class="animated-counter">
                {prefix}{target_value:,.0f}
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Header
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-family: 'Poppins', sans-serif; font-size: 3rem; font-weight: 700; 
                       color: #1E2A44; margin-bottom: 0.5rem;">
                📊 Your Free Care Home Report
            </h1>
            <p style="font-size: 1.2rem; color: #6B7280;">
                Personalized recommendations for {{ postcode }}
            </p>
        </div>
        """.replace("{{ postcode }}", report.questionnaire.get("postcode", "your area")),
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Fair Cost Gap - CENTER SCREEN, RED BLOCK WITH ANIMATED COUNTER
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); 
                    border-radius: 20px; 
                    padding: 4rem 2rem; 
                    margin: 3rem 0;
                    box-shadow: 0 12px 40px rgba(239, 68, 68, 0.4);
                    text-align: center;">
        """,
        unsafe_allow_html=True
    )
    
    fair_cost_gap = FairCostGap(**report.fair_cost_gap)
    
    # Animated counter for 5-year gap
    st.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <h2 style="font-family: 'Poppins', sans-serif; font-size: 2rem; font-weight: 700; 
                       color: white; margin-bottom: 1rem;">
                ⚠️ YOUR TOTAL OVERPAYMENT
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Animated counter
    display_animated_counter(fair_cost_gap.gap_5year, prefix="£")
    
    st.markdown(
        f"""
        <div style="margin-top: 2rem;">
            <p style="font-size: 1.5rem; color: white; font-weight: 600; margin-bottom: 0.5rem;">
                Over 5 Years
            </p>
            <p style="font-size: 1.2rem; color: rgba(255,255,255,0.9); margin-top: 1rem;">
                £{fair_cost_gap.gap_year:,.0f} per year | £{fair_cost_gap.gap_week:,.0f} per week
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # "Это только вершина айсберга" text
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <p style="font-family: 'Poppins', sans-serif; font-size: 1.8rem; font-weight: 600; 
                     color: #1E2A44; font-style: italic;">
                Это только вершина айсберга
            </p>
            <p style="font-size: 1.1rem; color: #6B7280; margin-top: 0.5rem;">
                The gap between market prices and what the Local Authority typically funds
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Green CTA Button
    col_cta = st.columns([1, 2, 1])
    with col_cta[1]:
        st.markdown(
            """
            <div style="text-align: center; margin: 2rem 0;">
                <p style="font-family: 'Poppins', sans-serif; font-size: 1.1rem; color: #6B7280; margin-bottom: 1rem;">
                    Discover how to save £50k+ with our Professional Report
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button(
            "💰 Узнать, как сэкономить £50k+ → Professional £119",
            use_container_width=True,
            type="primary",
            key="cta_professional"
        ):
            st.success("🎉 Redirecting to Professional Report upgrade page...")
            st.info("""
            **Professional Report includes:**
            - Full Companies House financial analysis
            - Detailed FSA inspection history  
            - Comprehensive risk assessment
            - Comparative market analysis
            - Personalized savings recommendations
            """)
    
    st.markdown("---")
    
    # Care Homes Cards in Columns
    st.markdown(
        """
        <h2 style="font-family: 'Poppins', sans-serif; font-size: 2.5rem; font-weight: 700; 
                   color: #1E2A44; margin: 2rem 0 1rem 0; text-align: center;">
            🏠 Recommended Care Homes
        </h2>
        """,
        unsafe_allow_html=True
    )
    
    # Display homes in columns (responsive)
    if len(report.care_homes) > 0:
        cols = st.columns(min(len(report.care_homes), 3))
        
        for idx, home_data in enumerate(report.care_homes):
            home = CareHome(**home_data)
            col_idx = idx % len(cols)
            
            with cols[col_idx]:
                display_care_home_card_web(home, idx + 1)
    
    st.markdown("---")
    
    # Professional Peek Expander
    if len(report.care_homes) > 0:
        with st.expander(
            "🔍 Professional Peek: Deep Analysis",
            expanded=False
        ):
            display_professional_peek(report.care_homes[0])
    
    st.markdown("---")
    
    # Share and Professional Buttons
    st.markdown("### 📤 Share & Upgrade")
    col_actions = st.columns(3)
    
    with col_actions[0]:
        report_link = f"https://rightcarehome.com/report/{report.report_id}"
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 1rem;">
                <p style="font-size: 0.85rem; color: #6B7280; margin-bottom: 0.5rem;">Share Report</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        # Copy link button using Streamlit
        if st.button("📤 Поделиться", use_container_width=True, key="share_report"):
            st.success(f"✅ Report link copied! Share: {report_link}")
            st.code(report_link, language=None)
    
    with col_actions[1]:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 1rem;">
                <p style="font-size: 0.85rem; color: #6B7280; margin-bottom: 0.5rem;">Upgrade</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🚀 Перейти к Professional", use_container_width=True, key="go_professional", type="primary"):
            st.info("💡 Professional Report includes: Full Companies House analysis, detailed FSA history, comprehensive risk assessment, and more!")
    
    with col_actions[2]:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 1rem;">
                <p style="font-size: 0.85rem; color: #6B7280; margin-bottom: 0.5rem;">Report ID</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.code(report.report_id[:12] + "...", language=None)


def display_care_home_card_web(home: CareHome, index: int):
    """Display care home card for web version"""
    
    match_badge_colors = {
        "Safe Bet": "#10B981",
        "Best Value": "#3B82F6",
        "Premium": "#8B5CF6"
    }
    
    badge_color = match_badge_colors.get(home.match_type or "", "#6B7280")
    
    st.markdown(
        f"""
        <div style="background: white; 
                    border: 2px solid #E5E7EB; 
                    border-radius: 16px; 
                    padding: 1.5rem; 
                    margin-bottom: 1.5rem;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    transition: transform 0.2s, box-shadow 0.2s;
                    height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <span style="background: {badge_color}; 
                            color: white; 
                            padding: 0.4rem 0.8rem; 
                            border-radius: 6px; 
                            font-size: 0.75rem; 
                            font-weight: 600;">
                    {home.match_type or "Recommended"}
                </span>
                <span style="font-size: 1.5rem;">#{index}</span>
            </div>
            
            <h3 style="font-family: 'Poppins', sans-serif; 
                       font-size: 1.5rem; 
                       font-weight: 700; 
                       color: #1E2A44; 
                       margin-bottom: 0.5rem;">
                {home.name}
            </h3>
            
            <p style="font-size: 0.9rem; color: #6B7280; margin-bottom: 1rem;">
                {home.address}<br>
                {home.postcode}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Weekly Cost", f"£{home.weekly_cost:,.0f}")
        if home.rating:
            st.metric("CQC Rating", home.rating)
    
    with col2:
        if home.distance_km:
            st.metric("Distance", f"{home.distance_km:.1f} km")
        if home.band:
            st.metric("Price Band", f"Band {home.band}")
    
    # FSA Rating
    if home.fsa_color:
        fsa_colors = {
            "green": "#10B981",
            "yellow": "#F59E0B",
            "red": "#EF4444"
        }
        fsa_color_hex = fsa_colors.get(home.fsa_color, "#6B7280")
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 1rem;">
                <span style="background: {fsa_color_hex}; 
                            color: white; 
                            padding: 0.4rem 1rem; 
                            border-radius: 6px; 
                            font-size: 0.85rem; 
                            font-weight: 600;">
                    FSA Rating: {home.fsa_color.upper()}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


def display_professional_peek(home_data: dict):
    """Display Professional Peek section"""
    
    home = CareHome(**home_data)
    
    st.markdown(
        """
        <h3 style="font-family: 'Poppins', sans-serif; font-size: 1.8rem; font-weight: 700; 
                   color: #1E2A44; margin-bottom: 1rem;">
            🔍 Deep Analysis: {home_name}
        </h3>
        """.replace("{home_name}", home.name),
        unsafe_allow_html=True
    )
    
    # Analysis sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 CQC Rating")
        if home.rating:
            st.info(f"**{home.rating}** - Full inspection reports available at cqc.org.uk")
        else:
            st.warning("Rating not available")
        
        if home.location_id:
            st.markdown(f"**Location ID:** `{home.location_id}`")
    
    with col2:
        st.markdown("### 🍽️ Food Hygiene")
        if home.fsa_color:
            fsa_colors = {
                "green": "✅ Excellent",
                "yellow": "⚠️ Good",
                "red": "❌ Needs Improvement"
            }
            st.info(f"**FSA Rating:** {fsa_colors.get(home.fsa_color, home.fsa_color.upper())}")
        else:
            st.warning("FSA rating not available")
    
    st.markdown("### 🏢 Companies House Data")
    st.info(
        """
        **Available in Professional Report:**
        - Financial stability analysis
        - Company structure and directors
        - Recent filings and changes
        - Risk assessment
        """
    )
    
    st.markdown(
        """
        <div style="background: #FEF3C7; padding: 1rem; border-radius: 8px; border-left: 4px solid #F59E0B; margin-top: 1rem;">
            <p style="margin: 0; color: #92400E; font-weight: 600;">
                💡 Upgrade to Professional Report for full Companies House analysis, 
                detailed FSA history, and comprehensive risk assessment.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="Free Report Viewer | RightCareHome",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Header
    st.title("📊 Free Report Viewer")
    st.markdown("Generate comprehensive care home reports from questionnaire responses")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📁 Select Questionnaire")
        
        sample_questionnaires = load_sample_questionnaires()
        selected_sample = None
        
        if sample_questionnaires:
            selected_sample = st.selectbox(
                "Choose a sample questionnaire:",
                ["None"] + list(sample_questionnaires.keys())
            )
        
        st.divider()
        
        st.markdown("### 📤 Or Upload Your Own")
        uploaded_file = st.file_uploader(
            "Upload JSON questionnaire",
            type=["json"],
            help="Upload a JSON file with questionnaire data"
        )
        
        st.divider()
        
        generate_button = st.button(
            "🚀 Generate Report",
            type="primary",
            use_container_width=True
        )
    
    # Initialize session state
    if "questionnaire" not in st.session_state:
        st.session_state.questionnaire = None
    if "report" not in st.session_state:
        st.session_state.report = None
    
    # Parse questionnaire
    questionnaire = None
    
    if uploaded_file:
        questionnaire = parse_uploaded_questionnaire(uploaded_file)
        st.session_state.questionnaire = questionnaire
    elif selected_sample and selected_sample != "None":
        file_path = sample_questionnaires[selected_sample]
        questionnaire = parse_questionnaire(file_path)
        st.session_state.questionnaire = questionnaire
    
    # Display questionnaire card if available
    if questionnaire:
        display_questionnaire_card(questionnaire)
        st.divider()
    
    # Generate report
    if generate_button:
        if not questionnaire:
            st.error("⚠️ Please select or upload a questionnaire first!")
        else:
            with st.spinner("🔄 Generating report..."):
                try:
                    api_client = FreeReportAPIClient()
                    report = api_client.generate_report(questionnaire)
                    st.session_state.report = report
                    st.success("✅ Report generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
                    st.info("💡 Make sure the FastAPI backend is running on http://localhost:8000")
    
    # Display report if available
    if st.session_state.report:
        report = st.session_state.report
        
        st.markdown("---")
        st.markdown("## 📄 Generated Report")
        
        # Care Homes Section
        st.markdown("### 🏠 Recommended Care Homes")
        
        for idx, home_data in enumerate(report.care_homes, 1):
            home = CareHome(**home_data)
            display_care_home_card(home, idx)
            if idx < len(report.care_homes):
                st.divider()
        
        # Fair Cost Gap Section (MANDATORY)
        st.markdown("---")
        fair_cost_gap = FairCostGap(**report.fair_cost_gap)
        display_fair_cost_gap(fair_cost_gap)
        
        # Report metadata and actions
        st.markdown("---")
        col_meta = st.columns(3)
        col_meta[0].caption(f"📅 Generated: {report.generated_at}")
        col_meta[1].caption(f"🆔 Report ID: {report.report_id}")
        col_meta[2].caption(f"🏠 Homes Found: {len(report.care_homes)}")
        
        # Download buttons
        st.markdown("### 📥 Download Options")
        col_download = st.columns(2)
        
        with col_download[0]:
            try:
                # Generate PDF
                pdf_bytes = generate_pdf_from_response(report.dict())
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"free_report_{report.report_id[:8]}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                st.info("💡 Make sure weasyprint is installed: `pip install weasyprint`")
        
        with col_download[1]:
            # Toggle web version display
            if "show_web_version" not in st.session_state:
                st.session_state.show_web_version = False
            
            if st.button(
                "🌐 View Web Version",
                use_container_width=True,
                help="View interactive web version of the report"
            ):
                st.session_state.show_web_version = not st.session_state.show_web_version
                st.rerun()
        
        # Display web version if toggled
        if st.session_state.get("show_web_version", False):
            st.markdown("---")
            display_web_version_report(report)


if __name__ == "__main__":
    main()

