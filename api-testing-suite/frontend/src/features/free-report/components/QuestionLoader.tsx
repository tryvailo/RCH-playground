import { useState, useRef } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import type { QuestionnaireResponse } from '../types';

interface QuestionLoaderProps {
  onLoad: (questionnaire: QuestionnaireResponse) => void;
  selectedFile?: string;
  onFileSelect: (filename: string) => void;
}

const SAMPLE_FILES = [
  'questionnaire_1.json',
  'questionnaire_2.json',
  'questionnaire_3.json',
  'questionnaire_4.json',
  'questionnaire_5.json',
  'questionnaire_6.json',
];

export default function QuestionLoader({ onLoad, selectedFile, onFileSelect }: QuestionLoaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadQuestionnaire = async (file: File | string) => {
    try {
      setError(null);
      let jsonData: QuestionnaireResponse;

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

      // Validate required fields
      if (!jsonData.postcode) {
        throw new Error('Postcode is required');
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
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Load Questionnaire</h3>
        
        {/* Sample Files */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sample Questionnaires:
          </label>
          <div className="space-y-2">
            {SAMPLE_FILES.map((filename) => (
              <button
                key={filename}
                onClick={() => loadQuestionnaire(filename)}
                className={`w-full text-left px-4 py-2 rounded-md border transition-colors ${
                  selectedFile === filename
                    ? 'bg-[#1E2A44] text-white border-[#1E2A44]'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center">
                  <FileText className="w-4 h-4 mr-2" />
                  <span className="text-sm">{filename}</span>
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
            <p className="text-xs text-gray-500 mt-1">JSON files only</p>
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

