import { useState, useRef } from 'react';
import { Upload, X } from 'lucide-react';

interface JsonFileDropzoneProps {
  onFileLoaded: (fileContent: string, filename: string) => void;
  onError?: (error: string) => void;
  helperText?: string;
  noteText?: string;
  accept?: string;
  className?: string;
}

export function JsonFileDropzone({
  onFileLoaded,
  onError,
  helperText = 'Click to upload or drag and drop',
  noteText = 'JSON files only',
  accept = '.json',
  className = '',
}: JsonFileDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleError = (message: string) => {
    setError(message);
    onError?.(message);
  };

  const loadFromFile = async (file: File) => {
    try {
      setError(null);
      const text = await file.text();
      onFileLoaded(text, file.name);
    } catch {
      handleError('Failed to read file');
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) loadFromFile(file);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files[0];
    if (file && (file.type === 'application/json' || file.name.endsWith('.json'))) {
      loadFromFile(file);
    } else {
      handleError('Please drop a JSON file');
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <div
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
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
          accept={accept}
          onChange={handleFileSelect}
          className="hidden"
        />
        <Upload
          className={`w-8 h-8 mx-auto mb-2 ${isDragging ? 'text-[#10B981]' : 'text-gray-400'}`}
        />
        <p className="text-sm text-gray-600">
          {isDragging ? 'Drop file here' : helperText}
        </p>
        <p className="text-xs text-gray-500 mt-1">{noteText}</p>
      </div>

      {error && (
        <div className="p-2 bg-red-50 border border-red-200 rounded-md flex items-start">
          <X className="w-4 h-4 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-red-800">{error}</p>
        </div>
      )}
    </div>
  );
}

export default JsonFileDropzone;
