"""
Debug script to test professional report generation and find NoneType comparison errors
"""
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_professional_report():
    """Test professional report generation with sample questionnaire"""
    try:
        # Load sample questionnaire
        sample_file = Path(__file__).parent.parent / "data" / "sample_questionnaires" / "professional_questionnaire_1_dementia.json"
        with open(sample_file, 'r') as f:
            questionnaire = json.load(f)
        
        # Import main endpoint
        from main import generate_professional_report
        
        # Create request
        request = {"questionnaire": questionnaire}
        
        # Call endpoint
        result = await generate_professional_report(request)
        
        print("✅ Report generated successfully!")
        print(f"Report ID: {result.get('report_id')}")
        print(f"Status: {result.get('status')}")
        print(f"Care homes: {len(result.get('report', {}).get('careHomes', []))}")
        
        return True
    except Exception as e:
        import traceback
        print(f"❌ Error generating report: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_professional_report())
    sys.exit(0 if result else 1)

