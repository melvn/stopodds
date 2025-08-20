'use client';

import { useState, useEffect } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Paper,
  Grid,
  Chip,
  IconButton,
  Link,
} from '@mui/material';
import {
  CheckCircle,
  PlayArrow,
  Celebration,
  Speed,
  TrendingUp,
  Analytics,
  Refresh,
  Science,
} from '@mui/icons-material';
import { SubmissionData, FormState } from '@/types';
import { formFields } from '@/lib/formConfig';
import Logo from './Logo';
import MaterialSuccessScreen from './MaterialSuccessScreen';

// Reorder questions for better flow
const gamifiedQuestions = [
  formFields.find(f => f.id === 'trips')!,
  formFields.find(f => f.id === 'stops')!,
  formFields.find(f => f.id === 'age_bracket')!,
  formFields.find(f => f.id === 'gender')!,
  formFields.find(f => f.id === 'ethnicity')!,
  formFields.find(f => f.id === 'skin_tone')!,
  formFields.find(f => f.id === 'height_bracket')!,
  formFields.find(f => f.id === 'concession')!,
  formFields.find(f => f.id === 'visible_disability')!,
];

interface AnimatedButtonProps {
  option: any;
  isSelected: boolean;
  onClick: () => void;
  delay: number;
  questionKey: string; // Add key to reset state on question change
}

function AnimatedButton({ option, isSelected, onClick, delay, questionKey }: AnimatedButtonProps) {
  const [clicked, setClicked] = useState(false);

  // Reset clicked state when question changes
  useEffect(() => {
    setClicked(false);
  }, [questionKey]);

  const handleClick = () => {
    setClicked(true);
    setTimeout(() => {
      onClick();
    }, 200); // Brief delay for animation
  };

  return (
    <Card
        sx={{
          cursor: 'pointer',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          transform: clicked ? 'scale(0.95)' : isSelected ? 'scale(1.05)' : 'scale(1)',
          background: isSelected 
            ? 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)'
            : clicked
            ? 'linear-gradient(135deg, #059669 0%, #10b981 100%)'
            : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
          color: isSelected || clicked ? 'white' : 'text.primary',
          border: '2px solid',
          borderColor: isSelected 
            ? '#1e3a8a' 
            : clicked 
            ? '#059669'
            : 'rgba(30, 58, 138, 0.1)',
          boxShadow: isSelected 
            ? '0 8px 25px rgba(30, 58, 138, 0.3)' 
            : clicked
            ? '0 8px 25px rgba(5, 150, 105, 0.3)'
            : '0 2px 8px rgba(0,0,0,0.1)',
          '&:hover': {
            transform: clicked ? 'scale(0.95)' : 'scale(1.02)',
            boxShadow: '0 6px 20px rgba(30, 58, 138, 0.2)',
          },
          minHeight: 80,
          position: 'relative',
          overflow: 'hidden',
        }}
        onClick={handleClick}
      >
        {(isSelected || clicked) && (
          <Box
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              animation: clicked ? 'bounce 0.5s ease' : 'pulse 2s infinite',
              '@keyframes bounce': {
                '0%, 20%, 50%, 80%, 100%': { transform: 'translateY(0)' },
                '40%': { transform: 'translateY(-10px)' },
                '60%': { transform: 'translateY(-5px)' },
              },
              '@keyframes pulse': {
                '0%': { transform: 'scale(1)' },
                '50%': { transform: 'scale(1.1)' },
                '100%': { transform: 'scale(1)' },
              },
            }}
          >
            <CheckCircle sx={{ fontSize: 24 }} />
          </Box>
        )}
        
        <CardContent sx={{ textAlign: 'center', py: 2 }}>
          <Typography 
            variant="h6" 
            component="div"
            sx={{ 
              fontWeight: 600,
              fontSize: { xs: '0.9rem', sm: '1.1rem' }
            }}
          >
            {typeof option === 'object' ? option.label : option}
          </Typography>
          {typeof option === 'object' && option.description && (
            <Typography 
              variant="caption" 
              sx={{ 
                opacity: 0.8,
                fontSize: '0.75rem',
                mt: 0.5,
                display: 'block'
              }}
            >
              {option.description}
            </Typography>
          )}
        </CardContent>
      </Card>
  );
}

export default function GamifiedForm() {
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

  const currentQuestion = gamifiedQuestions[formState.currentStep];
  const progress = ((formState.currentStep + 1) / gamifiedQuestions.length) * 100;
  const isComplete = formState.currentStep >= gamifiedQuestions.length;

  useEffect(() => {
    if (isComplete && !showSuccess) {
      handleSubmit();
    }
  }, [isComplete]);

  const handleAnswer = async (value: any) => {
    // Update form data and advance to next question immediately
    setFormState(prev => ({
      ...prev,
      data: {
        ...prev.data,
        [currentQuestion.id]: value
      },
      currentStep: prev.currentStep + 1
    }));
  };

  const handleSubmit = async () => {
    setFormState(prev => ({ ...prev, isSubmitting: true }));
    
    try {
      const response = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formState.data),
      });

      if (response.ok) {
        // Get personal estimate
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
      data: {
        trips: 0,
        stops: 0
      },
      errors: {},
      isSubmitting: false,
      currentStep: 0
    });
  };

  const handlePrevious = () => {
    if (formState.currentStep > 0) {
      setFormState(prev => ({
        ...prev,
        currentStep: prev.currentStep - 1
      }));
    }
  };

  if (showSuccess) {
    return <MaterialSuccessScreen onReset={handleReset} personalEstimate={personalEstimate} />;
  }

  if (isComplete) {
    return (
      <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
        <Container maxWidth="sm">
          <Card sx={{ textAlign: 'center', p: 6 }}>
            <Celebration sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" gutterBottom>
              Submitting...
            </Typography>
            <LinearProgress sx={{ mt: 3 }} />
          </Card>
        </Container>
      </Box>
    );
  }

  const getOptionsForQuestion = (question: any) => {
    if (question.type === 'number') {
      // Create quick select options for numbers
      if (question.id === 'trips') {
        return [
          { label: '1-5 trips', value: 3 },
          { label: '6-10 trips', value: 8 },
          { label: '11-20 trips', value: 15 },
          { label: '21-50 trips', value: 35 },
          { label: '50+ trips', value: 75 },
        ];
      } else if (question.id === 'stops') {
        const maxStops = Math.min(formState.data.trips || 10, 20);
        return Array.from({ length: maxStops + 1 }, (_, i) => ({
          label: i === 0 ? 'Never stopped' : `${i} time${i === 1 ? '' : 's'}`,
          value: i
        }));
      }
    }
    
    if (question.type === 'boolean') {
      // Create Yes/No options for boolean questions
      const options: Array<{ label: string; value: boolean | null }> = [
        { label: 'Yes', value: true },
        { label: 'No', value: false }
      ];
      
      // Add "Prefer not to answer" for optional questions
      if (!question.required) {
        options.push({ label: 'Prefer not to answer', value: null });
      }
      
      return options;
    }
    
    if (question.options) {
      const options = question.options.map((opt: any) => 
        typeof opt === 'string' ? { label: opt, value: opt } : opt
      );
      
      // Add "Prefer not to answer" for optional questions
      if (!question.required) {
        options.push({ label: 'Prefer not to answer', value: null });
      }
      
      return options;
    }
    
    return [];
  };

  const options = getOptionsForQuestion(currentQuestion);

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="md">
        {/* Header */}
        <Paper elevation={1} sx={{ p: 3, mb: 3, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <Logo size="medium" showText={true} />
          </Box>
          
          {/* Progress */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Question {formState.currentStep + 1} of {gamifiedQuestions.length}
              </Typography>
              <Chip 
                icon={<Speed />} 
                label={`${Math.round(progress)}%`} 
                size="small" 
                color="primary"
              />
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{ 
                height: 8, 
                borderRadius: 4,
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%)',
                }
              }}
            />
          </Box>
        </Paper>

        {/* Question */}
        <Card elevation={3} sx={{ mb: 3 }}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Typography 
                variant="h4" 
                component="h2" 
                gutterBottom
                sx={{ 
                  fontWeight: 700,
                  background: 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                {currentQuestion.label}
              </Typography>
              {currentQuestion.description && (
                <Typography variant="body1" color="text.secondary">
                  {currentQuestion.description}
                </Typography>
              )}
            </Box>

            {/* Answer Grid */}
            <Grid container spacing={2}>
              {options.map((option, index) => (
                <Grid 
                  item 
                  xs={currentQuestion.type === 'number' && currentQuestion.id === 'stops' ? 6 : 12} 
                  sm={currentQuestion.type === 'number' ? 6 : 6}
                  md={options.length > 4 ? 4 : 6}
                  key={index}
                >
                  <AnimatedButton
                    option={option}
                    isSelected={formState.data[currentQuestion.id as keyof SubmissionData] === option.value}
                    onClick={() => handleAnswer(option.value)}
                    delay={index}
                    questionKey={currentQuestion.id}
                  />
                </Grid>
              ))}
            </Grid>

            {/* Back Button */}
            {formState.currentStep > 0 && (
              <Box sx={{ mt: 4, textAlign: 'center' }}>
                <Button
                  onClick={handlePrevious}
                  variant="outlined"
                  startIcon={<Refresh />}
                  sx={{ minWidth: 120 }}
                >
                  Previous
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Info Links */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Link href="/privacy" underline="none">
            <Chip 
              icon={<Analytics />} 
              label="Anonymous" 
              variant="outlined" 
              clickable
              sx={{ '&:hover': { backgroundColor: 'primary.50' } }}
            />
          </Link>
          <Link href="/methodology" underline="none">
            <Chip 
              icon={<Science />} 
              label="Methodology" 
              variant="outlined" 
              clickable
              sx={{ '&:hover': { backgroundColor: 'primary.50' } }}
            />
          </Link>
        </Box>
      </Container>
    </Box>
  );
}