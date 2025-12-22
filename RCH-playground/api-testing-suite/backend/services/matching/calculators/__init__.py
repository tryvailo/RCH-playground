"""
Category Calculators for Professional Report Matching

8 specialized calculators for 156-point matching algorithm:
1. Medical - Medical capabilities (30 points)
2. Safety - Safety & quality (25 points)
3. Location - Location & access (15 points)
4. Financial - Financial stability (20 points)
5. Staff - Staff quality (18 points)
6. CQC - CQC quality (16 points)
7. Social - Social & community (12 points)
8. Services - Services & amenities (10 points)

Total: 156 points
"""

from services.matching.calculators.medical_calculator import MedicalCalculator
from services.matching.calculators.safety_calculator import SafetyCalculator
from services.matching.calculators.location_calculator import LocationCalculator
from services.matching.calculators.financial_calculator import FinancialCalculator
from services.matching.calculators.staff_calculator import StaffCalculator
from services.matching.calculators.cqc_calculator import CQCCalculator
from services.matching.calculators.social_calculator import SocialCalculator
from services.matching.calculators.services_calculator import ServicesCalculator

__all__ = [
    'MedicalCalculator',
    'SafetyCalculator',
    'LocationCalculator',
    'FinancialCalculator',
    'StaffCalculator',
    'CQCCalculator',
    'SocialCalculator',
    'ServicesCalculator'
]

# Convenient registry for accessing all calculators
CALCULATORS = {
    'medical': MedicalCalculator(),
    'safety': SafetyCalculator(),
    'location': LocationCalculator(),
    'financial': FinancialCalculator(),
    'staff': StaffCalculator(),
    'cqc': CQCCalculator(),
    'social': SocialCalculator(),
    'services': ServicesCalculator()
}
