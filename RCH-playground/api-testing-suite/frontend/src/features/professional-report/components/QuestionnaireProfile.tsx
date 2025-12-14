/**
 * Questionnaire Profile Component
 * Displays the full professional questionnaire profile
 */
import { FileText } from 'lucide-react';
import type { ProfessionalQuestionnaireResponse } from '../types';

interface QuestionnaireProfileProps {
  questionnaire: ProfessionalQuestionnaireResponse;
}

export default function QuestionnaireProfile({ questionnaire }: QuestionnaireProfileProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <FileText className="w-6 h-6 mr-2 text-[#10B981]" />
        Client Profile
      </h2>
      
      {/* Full Questionnaire Display */}
      <div className="space-y-4">
        {/* Section 1: Contact & Emergency */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">
            Section 1: Contact & Emergency
          </h4>
          <div className="space-y-3 text-sm">
            <div>
              <span className="text-gray-500 font-medium">Names:</span>
              <div className="mt-1 font-medium text-gray-900">
                {questionnaire.section_1_contact_emergency.q1_names}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Email:</span>
              <div className="mt-1 font-medium text-gray-900 break-words">
                {questionnaire.section_1_contact_emergency.q2_email}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Phone:</span>
              <div className="mt-1 font-medium text-gray-900">
                {questionnaire.section_1_contact_emergency.q3_phone}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Emergency Contact:</span>
              <div className="mt-1 font-medium text-gray-900 break-words">
                {questionnaire.section_1_contact_emergency.q4_emergency_contact}
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: Location & Budget */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">
            Section 2: Location & Budget
          </h4>
          <div className="space-y-3 text-sm">
            <div>
              <span className="text-gray-500 font-medium">Preferred City:</span>
              <div className="mt-1 font-medium text-gray-900">
                {questionnaire.section_2_location_budget.q5_preferred_city}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Max Distance:</span>
              <div className="mt-1 font-medium text-gray-900">
                {questionnaire.section_2_location_budget.q6_max_distance === 'distance_not_important' 
                  ? 'Not Important' 
                  : questionnaire.section_2_location_budget.q6_max_distance.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Budget:</span>
              <div className="mt-1 font-medium text-gray-900">
                {questionnaire.section_2_location_budget.q7_budget.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            </div>
          </div>
        </div>

        {/* Section 3: Medical Needs */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">
            Section 3: Medical Needs
          </h4>
          <div className="space-y-3 text-sm">
            <div>
              <span className="text-gray-500 font-medium">Care Types:</span>
              <div className="mt-2 flex flex-wrap gap-2">
                {questionnaire.section_3_medical_needs.q8_care_types.map((type, idx) => (
                  <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-md text-sm font-medium">
                    {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Medical Conditions:</span>
              <div className="mt-2 flex flex-wrap gap-2">
                {questionnaire.section_3_medical_needs.q9_medical_conditions.map((condition, idx) => (
                  <span key={idx} className="px-3 py-1 bg-red-100 text-red-800 rounded-md text-sm font-medium">
                    {condition.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Mobility Level:</span>
              <div className="mt-1 font-medium text-gray-900">
                {questionnaire.section_3_medical_needs.q10_mobility_level.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Medication Management:</span>
              <div className="mt-1 font-medium text-gray-900">
                {questionnaire.section_3_medical_needs.q11_medication_management.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Age Range:</span>
              <div className="mt-1 font-medium text-gray-900">
                {questionnaire.section_3_medical_needs.q12_age_range.replace(/_/g, '-')}
              </div>
            </div>
          </div>
        </div>

        {/* Section 4: Safety & Special Needs */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">
            Section 4: Safety & Special Needs
          </h4>
          <div className="space-y-3 text-sm">
            <div>
              <span className="text-gray-500 font-medium">Fall History:</span>
              <div className="mt-1 font-medium text-gray-900">
                {questionnaire.section_4_safety_special_needs.q13_fall_history.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Allergies:</span>
              <div className="mt-2 flex flex-wrap gap-2">
                {questionnaire.section_4_safety_special_needs.q14_allergies.map((allergy, idx) => (
                  <span key={idx} className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-md text-sm font-medium">
                    {allergy.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Dietary Requirements:</span>
              <div className="mt-2 flex flex-wrap gap-2">
                {questionnaire.section_4_safety_special_needs.q15_dietary_requirements.map((diet, idx) => (
                  <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-md text-sm font-medium">
                    {diet.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <span className="text-gray-500 font-medium">Social Personality:</span>
              <div className="mt-1 font-medium text-gray-900">
                {questionnaire.section_4_safety_special_needs.q16_social_personality.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            </div>
          </div>
        </div>

        {/* Section 5: Timeline */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">
            Section 5: Timeline
          </h4>
          <div className="text-sm">
            <span className="text-gray-500 font-medium">Placement Timeline:</span>
            <div className="mt-1 font-medium text-gray-900">
              {questionnaire.section_5_timeline.q17_placement_timeline.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

