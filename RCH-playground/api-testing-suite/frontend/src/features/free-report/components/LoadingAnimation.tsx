import { useState, useEffect } from 'react';
import { Sparkles, TrendingUp, Shield, Award } from 'lucide-react';

interface LoadingAnimationProps {
  progress: number; // 0-100
}

export default function LoadingAnimation({ progress }: LoadingAnimationProps) {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { icon: Sparkles, text: 'Analyzing your data...', color: 'text-[#10B981]' },
    { icon: TrendingUp, text: 'Calculating Fair Cost Gap...', color: 'text-[#EF4444]' },
    { icon: Shield, text: 'Finding the best care homes...', color: 'text-blue-600' },
    { icon: Award, text: 'Creating personal recommendations...', color: 'text-purple-600' },
  ];

  useEffect(() => {
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % steps.length);
    }, 2000);
    return () => clearInterval(stepInterval);
  }, []);

  const Icon = steps[currentStep].icon;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1E2A44] via-[#2D3E5F] to-[#1E2A44] flex items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center">
        {/* Animated Logo/Icon */}
        <div className="mb-8 relative">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 border-4 border-[#10B981]/30 rounded-full animate-ping"></div>
          </div>
          <div className="relative flex items-center justify-center">
            <div className="w-24 h-24 bg-gradient-to-br from-[#10B981] to-[#059669] rounded-2xl flex items-center justify-center shadow-2xl transform rotate-3 hover:rotate-6 transition-transform duration-300">
              <Award className="w-12 h-12 text-white" />
            </div>
          </div>
        </div>

        {/* Main Title */}
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 animate-fade-in">
          Generating Your Report
        </h1>
        <p className="text-xl text-gray-300 mb-8">
          This will only take a few seconds...
        </p>

        {/* Current Step */}
        <div className="mb-8 flex items-center justify-center">
          <div className={`${steps[currentStep].color} flex items-center space-x-3 bg-white/10 backdrop-blur-sm rounded-full px-6 py-3`}>
            <Icon className="w-5 h-5 animate-spin-slow" />
            <span className="text-white font-medium">{steps[currentStep].text}</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden backdrop-blur-sm">
            <div
              className="h-full bg-gradient-to-r from-[#10B981] to-[#059669] rounded-full transition-all duration-300 ease-out shadow-lg"
              style={{ width: `${progress}%` }}
            >
              <div className="h-full bg-white/20 animate-shimmer"></div>
            </div>
          </div>
          <p className="text-white/80 text-sm mt-2">{Math.round(progress)}%</p>
        </div>

        {/* All Steps Indicator */}
        <div className="flex justify-center space-x-4 mt-8">
          {steps.map((step, idx) => {
            const StepIcon = step.icon;
            const isActive = idx === currentStep;
            const isCompleted = idx < currentStep;

            return (
              <div
                key={idx}
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isActive
                    ? 'bg-[#10B981] scale-110 shadow-lg'
                    : isCompleted
                    ? 'bg-[#10B981]/50'
                    : 'bg-white/10'
                }`}
              >
                <StepIcon
                  className={`w-5 h-5 ${
                    isActive || isCompleted ? 'text-white' : 'text-white/50'
                  }`}
                />
              </div>
            );
          })}
        </div>

        {/* Fun Fact */}
        <div className="mt-12 bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <p className="text-white/90 text-sm">
            💡 <strong>Did you know?</strong> The average overpayment for care is{' '}
            <span className="text-[#10B981] font-bold">£44,928 per year</span>. We'll help you find ways to save!
          </p>
        </div>
      </div>
    </div>
  );
}

