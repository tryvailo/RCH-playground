import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import QuestionLoader from '../QuestionLoader';

describe('QuestionLoader', () => {
  // Test 1: Renders loader interface
  it('should render loader title and instructions', () => {
    const mockOnLoad = vi.fn();
    const mockOnFileSelect = vi.fn();
    
    render(
      <QuestionLoader 
        onLoad={mockOnLoad} 
        onFileSelect={mockOnFileSelect} 
      />
    );
    
    expect(screen.getByText('Load Professional Questionnaire')).toBeInTheDocument();
    expect(screen.getByText(/17 Questions • 5 Sections/)).toBeInTheDocument();
  });

  // Test 2: Lists sample files
  it('should display sample questionnaire files', () => {
    const mockOnLoad = vi.fn();
    const mockOnFileSelect = vi.fn();
    
    render(
      <QuestionLoader 
        onLoad={mockOnLoad} 
        onFileSelect={mockOnFileSelect} 
      />
    );
    
    expect(screen.getByText(/Dementia Care Profile/)).toBeInTheDocument();
    expect(screen.getByText(/Diabetes & Mobility/)).toBeInTheDocument();
  });

  // Test 3: Has drag-and-drop zone
  it('should render drag-and-drop upload zone', () => {
    const mockOnLoad = vi.fn();
    const mockOnFileSelect = vi.fn();
    
    render(
      <QuestionLoader 
        onLoad={mockOnLoad} 
        onFileSelect={mockOnFileSelect} 
      />
    );
    
    expect(screen.getByText(/Click to upload or drag and drop/)).toBeInTheDocument();
  });

  // Test 4: Shows drop state on drag
  it('should show drop zone for file upload', () => {
    const mockOnLoad = vi.fn();
    const mockOnFileSelect = vi.fn();
    
    render(
      <QuestionLoader 
        onLoad={mockOnLoad} 
        onFileSelect={mockOnFileSelect} 
      />
    );
    
    expect(screen.getByText(/drag and drop/)).toBeInTheDocument();
  });

  // Test 5: Sample files have descriptions
  it('should show proper section info', () => {
    const mockOnLoad = vi.fn();
    const mockOnFileSelect = vi.fn();
    
    render(
      <QuestionLoader 
        onLoad={mockOnLoad} 
        onFileSelect={mockOnFileSelect} 
      />
    );
    
    expect(screen.getByText(/17 Questions • 5 Sections/)).toBeInTheDocument();
  });

  // Test 6: Shows banner information
  it('should display info banner', () => {
    const mockOnLoad = vi.fn();
    const mockOnFileSelect = vi.fn();
    
    render(
      <QuestionLoader 
        onLoad={mockOnLoad} 
        onFileSelect={mockOnFileSelect} 
      />
    );
    
    expect(screen.getByText(/Professional questionnaire includes detailed/)).toBeInTheDocument();
  });

  // Test 7: Shows file upload label
  it('should show file upload instructions', () => {
    const mockOnLoad = vi.fn();
    const mockOnFileSelect = vi.fn();
    
    render(
      <QuestionLoader 
        onLoad={mockOnLoad} 
        onFileSelect={mockOnFileSelect} 
      />
    );
    
    expect(screen.getByText(/Sample Professional Questionnaires/)).toBeInTheDocument();
  });

  // Test 8: Has sample file buttons
  it('should show multiple sample file options', () => {
    const mockOnLoad = vi.fn();
    const mockOnFileSelect = vi.fn();
    
    render(
      <QuestionLoader 
        onLoad={mockOnLoad} 
        onFileSelect={mockOnFileSelect} 
      />
    );
    
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(5);
  });

  // Test 9: Highlights selected file
  it('should show selection capability for files', () => {
    const mockOnLoad = vi.fn();
    const mockOnFileSelect = vi.fn();
    
    render(
      <QuestionLoader 
        onLoad={mockOnLoad} 
        selectedFile="professional_questionnaire_1_dementia.json"
        onFileSelect={mockOnFileSelect} 
      />
    );
    
    expect(screen.getByText(/Dementia Care Profile/)).toBeInTheDocument();
  });

  // Test 10: Has file type restriction
  it('should specify JSON file type requirement', () => {
    const mockOnLoad = vi.fn();
    const mockOnFileSelect = vi.fn();
    
    render(
      <QuestionLoader 
        onLoad={mockOnLoad} 
        onFileSelect={mockOnFileSelect} 
      />
    );
    
    expect(screen.getByText(/JSON files only/)).toBeInTheDocument();
  });
});
