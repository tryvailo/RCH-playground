import { useState, useRef } from 'react';
import { Upload, FileText, X, AlertCircle } from 'lucide-react';
import type { ProfessionalQuestionnaireResponse } from '../types';

interface QuestionLoaderProps {
  onLoad: (questionnaire: ProfessionalQuestionnaireResponse) => void;
  selectedFile?: string;
  onFileSelect: (filename: string) => void;
}

const PROFESSIONAL_SAMPLE_FILES = [
  {
    filename: 'professional_questionnaire_1_dementia.json',
    label: '1. Dementia Care Profile',
    description: 'Rule 2: Деменция → Medical +7% (19% → 26%)',
    scenario: 'Сценарий: Специализированный уход при деменции. Приоритет: медицинские возможности и обученный персонал.'
  },
  {
    filename: 'professional_questionnaire_2_diabetes_mobility.json',
    label: '2. Diabetes & Mobility + Fall Risk',
    description: 'Rule 1: Высокий риск падений → Safety +9% (16% → 25%)',
    scenario: 'Сценарий: Критический приоритет безопасности. Fall Risk останавливает все остальные правила. Приоритет: программы предотвращения падений.'
  },
  {
    filename: 'professional_questionnaire_3_cardiac_nursing.json',
    label: '3. Cardiac Nursing',
    description: 'Rule 4: Сестринский уход → Medical +3%, Staff +3%',
    scenario: 'Сценарий: Требуется сестринский уход. Приоритет: квалифицированные медсестры и медицинские протоколы.'
  },
  {
    filename: 'professional_questionnaire_4_healthy_residential.json',
    label: '4. Healthy Residential + Low Budget',
    description: 'Rule 5: Низкий бюджет → Financial +6% (13% → 19%)',
    scenario: 'Сценарий: Ограниченный бюджет. Приоритет: финансовая стабильность дома (избежание закрытия).'
  },
  {
    filename: 'professional_questionnaire_5_high_fall_risk.json',
    label: '5. High Fall Risk',
    description: 'Rule 1: Высокий риск падений → Safety +9% (приоритет)',
    scenario: 'Сценарий: Высокий риск падений (критический). Приоритет: безопасность и CQC Safe рейтинг.'
  },
  {
    filename: 'professional_questionnaire_6_complex_multiple.json',
    label: '6. Complex Multiple Conditions',
    description: 'Rule 1: Fall Risk (приоритет) перекрывает Multiple Conditions',
    scenario: 'Сценарий: Множественные условия + Fall Risk. Fall Risk имеет высший приоритет и останавливает другие правила.'
  },
];

export default function QuestionLoader({ onLoad, selectedFile, onFileSelect }: QuestionLoaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadQuestionnaire = async (file: File | string) => {
    try {
      setError(null);
      let jsonData: ProfessionalQuestionnaireResponse;

      if (typeof file === 'string') {
        // Load from public folder
        const response = await fetch(`/sample_questionnaires/${file}`);
        if (!response.ok) {
          throw new Error(`Failed to load ${file}`);
        }
        jsonData = await response.json();
        onFileSelect(file);
      } else {
        // Load from file input
        const text = await file.text();
        jsonData = JSON.parse(text);
        onFileSelect(file.name);
      }

      // Validate required sections
      if (!jsonData.section_1_contact_emergency?.q1_names) {
        throw new Error('Section 1 (Contact & Emergency) is required');
      }
      if (!jsonData.section_2_location_budget?.q5_preferred_city) {
        throw new Error('Section 2 (Location & Budget) is required');
      }
      if (!jsonData.section_3_medical_needs?.q8_care_types) {
        throw new Error('Section 3 (Medical Needs) is required');
      }
      if (!jsonData.section_4_safety_special_needs?.q13_fall_history) {
        throw new Error('Section 4 (Safety & Special Needs) is required');
      }
      if (!jsonData.section_5_timeline?.q17_placement_timeline) {
        throw new Error('Section 5 (Timeline) is required');
      }

      onLoad(jsonData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load questionnaire';
      setError(errorMessage);
      console.error('Error loading questionnaire:', err);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      loadQuestionnaire(file);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files[0];
    if (file && file.type === 'application/json') {
      loadQuestionnaire(file);
    } else {
      setError('Please drop a JSON file');
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Load Professional Questionnaire</h3>
        
        {/* Info Banner */}
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-start">
          <AlertCircle className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-blue-800 font-medium">17 Questions • 5 Sections</p>
            <p className="text-xs text-blue-700 mt-1">
              Professional questionnaire includes detailed medical needs, safety requirements, and financial planning
            </p>
          </div>
        </div>

        {/* Sample Files */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sample Professional Questionnaires:
          </label>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {PROFESSIONAL_SAMPLE_FILES.map((file) => (
              <button
                key={file.filename}
                onClick={() => loadQuestionnaire(file.filename)}
                className={`w-full text-left px-4 py-3 rounded-md border transition-colors ${
                  selectedFile === file.filename
                    ? 'bg-[#1E2A44] text-white border-[#1E2A44]'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start">
                  <FileText className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium">{file.label}</div>
                    <div className="text-xs opacity-75 mt-0.5">{file.description}</div>
                    <div className="text-xs opacity-70 mt-1 italic">{file.scenario}</div>
                    <div className="text-xs opacity-60 mt-1">{file.filename}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Divider */}
        <div className="relative my-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">or</span>
          </div>
        </div>

        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload Your Own JSON:
          </label>
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
              isDragging
                ? 'border-[#10B981] bg-[#10B981]/5'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={handleFileSelect}
              className="hidden"
            />
            <Upload className={`w-8 h-8 mx-auto mb-2 ${isDragging ? 'text-[#10B981]' : 'text-gray-400'}`} />
            <p className="text-sm text-gray-600">
              {isDragging ? 'Drop JSON file here' : 'Click to upload or drag and drop'}
            </p>
            <p className="text-xs text-gray-500 mt-1">JSON files only • Must include all 5 sections</p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md flex items-start">
            <X className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

