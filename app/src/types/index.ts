export interface SubmissionData {
  age_bracket?: string;
  gender?: string;
  ethnicity?: string;
  skin_tone?: string;
  height_bracket?: string;
  visible_disability?: boolean | null;
  concession?: boolean | null;
  trips: number;
  stops: number;
}

export interface FormField {
  id: string;
  label: string;
  type: 'select' | 'number' | 'boolean';
  options?: { value: string; label: string }[];
  required?: boolean;
  min?: number;
  max?: number;
  description?: string;
}

export interface FormState {
  data: SubmissionData;
  errors: Record<string, string>;
  isSubmitting: boolean;
  currentStep: number;
}