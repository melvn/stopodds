'use client';

import { useState } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Box,
  Button,
  Alert,
  Link,
  Paper,
} from '@mui/material';
import { ArrowBack, ArrowForward, CheckCircle } from '@mui/icons-material';
import { SubmissionData, FormState } from '@/types';
import { formFields, getFieldsByStep, totalSteps } from '@/lib/formConfig';
import MaterialFormField from './MaterialFormField';
import MaterialSuccessScreen from './MaterialSuccessScreen';
import Logo from './Logo';

const stepLabels = [
  'Trip Information',
  'Basic Demographics', 
  'Appearance',
  'Additional Information'
];

export default function MaterialSubmissionForm() {
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
  const [personalEstimate, setPersonalEstimate] = useState<any>(null);

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
        // Get personal estimate after successful submission
        const traits = new URLSearchParams();
        Object.entries(formState.data).forEach(([key, value]) => {
          if (value !== null && value !== undefined && key !== 'trips' && key !== 'stops') {
            traits.append(key, value.toString());
          }
        });
        
        try {
          const predictionResponse = await fetch(`/api/predict?${traits.toString()}`);
          if (predictionResponse.ok) {
            const prediction = await predictionResponse.json();
            setPersonalEstimate(prediction);
          }
        } catch (err) {
          console.log('Could not fetch personal estimate:', err);
        }
        
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
    setPersonalEstimate(null);
    setFormState({
      data: { trips: 0, stops: 0 },
      errors: {},
      isSubmitting: false,
      currentStep: 0
    });
  };

  if (showSuccess) {
    return <MaterialSuccessScreen onReset={handleReset} personalEstimate={personalEstimate} />;
  }

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="sm">
        {/* Header */}
        <Paper elevation={1} sx={{ p: 4, mb: 3, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <Logo size="large" showText={true} />
          </Box>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            Help us understand fare inspection patterns on Melbourne public transport
          </Typography>
          
          {/* Stepper */}
          <Box sx={{ mt: 3 }}>
            <Stepper activeStep={formState.currentStep} alternativeLabel>
              {stepLabels.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </Box>
        </Paper>

        {/* Form */}
        <Card elevation={2}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h6" gutterBottom>
              {stepLabels[formState.currentStep]}
            </Typography>
            
            <Box>
              {currentFields.map((field) => (
                <MaterialFormField
                  key={field.id}
                  {...field}
                  value={formState.data[field.id as keyof SubmissionData]}
                  onChange={(value) => updateField(field.id, value)}
                  error={formState.errors[field.id]}
                />
              ))}
            </Box>

            {/* Navigation */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4, pt: 2 }}>
              <Button
                onClick={handlePrevious}
                disabled={isFirstStep}
                startIcon={<ArrowBack />}
                variant="outlined"
                color="secondary"
              >
                Previous
              </Button>

              {isLastStep ? (
                <Button
                  onClick={handleSubmit}
                  disabled={formState.isSubmitting}
                  endIcon={<CheckCircle />}
                  variant="contained"
                  color="primary"
                >
                  {formState.isSubmitting ? 'Submitting...' : 'Submit Data'}
                </Button>
              ) : (
                <Button
                  onClick={handleNext}
                  endIcon={<ArrowForward />}
                  variant="contained"
                  color="primary"
                >
                  Next
                </Button>
              )}
            </Box>
          </CardContent>
        </Card>

        {/* Privacy Notice */}
        <Box sx={{ mt: 3 }}>
          <Alert severity="info">
            🔒 Your data is anonymous and helps improve public transport equity.{' '}
            <Link href="/privacy" underline="hover">
              Read our privacy policy
            </Link>{' '}
            for details.
          </Alert>
        </Box>
      </Container>
    </Box>
  );
}