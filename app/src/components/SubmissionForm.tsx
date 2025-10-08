'use client';

import { useState, useEffect } from 'react';
import { SubmissionData, FormState } from '@/types';
import { formFields, getFieldsByStep, totalSteps } from '@/lib/formConfig';
import FormCard from './FormCard';
import FormField from './FormField';
import SuccessScreen from './SuccessScreen';

export default function SubmissionForm() {
  const [formState, setFormState] = useState<FormState>({
    data: {
      trips: 0,
      stops: 0
    },
    errors: {},
    isSubmitting: false,
    currentStep: 0
  });

  const [showSuccess, setShowSuccess] = useState(false);

  const currentFields = getFieldsByStep(formState.currentStep);
  const isLastStep = formState.currentStep === totalSteps - 1;
  const isFirstStep = formState.currentStep === 0;

  const updateField = (fieldId: string, value: any) => {
    setFormState(prev => ({
      ...prev,
      data: {
        ...prev.data,
        [fieldId]: value
      },
      errors: {
        ...prev.errors,
        [fieldId]: ''
      }
    }));
  };

  const validateCurrentStep = () => {
    const errors: Record<string, string> = {};
    
    currentFields.forEach(field => {
      const value = formState.data[field.id as keyof SubmissionData];
      
      if (field.required && (value === null || value === undefined || value === '')) {
        errors[field.id] = `${field.label} is required`;
      }
      
      if (field.type === 'number' && value !== null && value !== undefined) {
        const numValue = Number(value);
        if (field.min !== undefined && numValue < field.min) {
          errors[field.id] = `${field.label} must be at least ${field.min}`;
        }
        if (field.max !== undefined && numValue > field.max) {
          errors[field.id] = `${field.label} must be no more than ${field.max}`;
        }
      }

      // Validate stops don't exceed trips
      if (field.id === 'stops' && formState.data.trips && value !== null && value !== undefined) {
        if (Number(value) > formState.data.trips) {
          errors[field.id] = 'Stops cannot exceed total trips';
        }
      }
    });

    setFormState(prev => ({ ...prev, errors }));
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (validateCurrentStep()) {
      setFormState(prev => ({
        ...prev,
        currentStep: Math.min(prev.currentStep + 1, totalSteps - 1)
      }));
    }
  };

  const handlePrevious = () => {
    setFormState(prev => ({
      ...prev,
      currentStep: Math.max(prev.currentStep - 1, 0)
    }));
  };

  const handleSubmit = async () => {
    if (!validateCurrentStep()) return;

    setFormState(prev => ({ ...prev, isSubmitting: true }));
    
    try {
      const response = await fetch('/api/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formState.data),
      });

      if (response.ok) {
        setShowSuccess(true);
      } else {
        throw new Error('Submission failed');
      }
    } catch (error) {
      alert('There was an error submitting your data. Please try again.');
    } finally {
      setFormState(prev => ({ ...prev, isSubmitting: false }));
    }
  };

  const handleReset = () => {
    setShowSuccess(false);
    setFormState({
      data: { trips: 0, stops: 0 },
      errors: {},
      isSubmitting: false,
      currentStep: 0
    });
  };

  if (showSuccess) {
    return <SuccessScreen onReset={handleReset} />;
  }

  const progress = ((formState.currentStep + 1) / totalSteps) * 100;

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <FormCard className="p-8 mb-6 text-center">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            StopOdds
          </h1>
          <p className="text-gray-600 mb-6">
            Help us understand fare inspection patterns on Melbourne public transport
          </p>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div 
              className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-500">
            Step {formState.currentStep + 1} of {totalSteps}
          </p>
        </FormCard>

        {/* Form */}
        <FormCard className="p-8">
          <div className="space-y-6">
            {currentFields.map((field) => (
              <FormField
                key={field.id}
                {...field}
                value={formState.data[field.id as keyof SubmissionData]}
                onChange={(value) => updateField(field.id, value)}
                error={formState.errors[field.id]}
              />
            ))}
          </div>

          {/* Navigation */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={handlePrevious}
              disabled={isFirstStep}
              className={`
                px-6 py-3 rounded-xl font-semibold transition-all duration-200 button-press
                ${isFirstStep
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }
              `}
            >
              Previous
            </button>

            {isLastStep ? (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={formState.isSubmitting}
                className={`
                  px-8 py-3 rounded-xl font-semibold transition-all duration-200 button-press
                  ${formState.isSubmitting
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700'
                  }
                  text-white shadow-lg
                `}
              >
                {formState.isSubmitting ? 'Submitting...' : 'Submit Data'}
              </button>
            ) : (
              <button
                type="button"
                onClick={handleNext}
                className="px-8 py-3 rounded-xl font-semibold bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transition-all duration-200 button-press shadow-lg"
              >
                Next
              </button>
            )}
          </div>
        </FormCard>

        {/* Privacy Notice */}
        <FormCard className="p-6 mt-6 text-center">
          <p className="text-sm text-gray-600">
            🔒 Your data is anonymous and helps improve public transport equity. 
            <br />
            Read our <a href="/privacy" className="text-blue-600 hover:underline">privacy policy</a> for details.
          </p>
        </FormCard>
      </div>
    </div>
  );
}