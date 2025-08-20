import { FormField } from '@/types';

export const formFields: FormField[] = [
  {
    id: 'trips',
    label: 'Total trips in last 30 days',
    type: 'number',
    required: true,
    min: 1,
    max: 200,
    description: 'How many times did you use public transport in Melbourne in the last 30 days?'
  },
  {
    id: 'stops',
    label: 'Times stopped by fare inspectors',
    type: 'number',
    required: true,
    min: 0,
    description: 'How many times were you checked by fare inspectors in the last 30 days?'
  },
  {
    id: 'age_bracket',
    label: 'Age bracket',
    type: 'select',
    options: [
      { value: '18-24', label: '18-24 years' },
      { value: '25-34', label: '25-34 years' },
      { value: '35-44', label: '35-44 years' },
      { value: '45+', label: '45+ years' }
    ],
    description: 'Your age group (optional)'
  },
  {
    id: 'gender',
    label: 'Gender',
    type: 'select',
    options: [
      { value: 'Male', label: 'Male' },
      { value: 'Female', label: 'Female' },
      { value: 'Nonbinary', label: 'Non-binary' },
      { value: 'PreferNot', label: 'Prefer not to say' }
    ],
    description: 'Your gender identity (optional)'
  },
  {
    id: 'ethnicity',
    label: 'Ethnicity',
    type: 'select',
    options: [
      { value: 'Anglo Australian', label: 'Anglo Australian' },
      { value: 'Indigenous', label: 'Indigenous Australian' },
      { value: 'South Asian', label: 'South Asian' },
      { value: 'East Asian', label: 'East Asian' },
      { value: 'Southeast Asian', label: 'Southeast Asian' },
      { value: 'Middle Eastern', label: 'Middle Eastern' },
      { value: 'African', label: 'African' },
      { value: 'European', label: 'European' },
      { value: 'Latin American', label: 'Latin American' },
      { value: 'Other', label: 'Other' },
      { value: 'PreferNot', label: 'Prefer not to say' }
    ],
    description: 'Your ethnic background (optional)'
  },
  {
    id: 'skin_tone',
    label: 'Skin tone',
    type: 'select',
    options: [
      { value: 'Light', label: 'Light' },
      { value: 'Medium', label: 'Medium' },
      { value: 'Dark', label: 'Dark' },
      { value: 'PreferNot', label: 'Prefer not to say' }
    ],
    description: 'Your skin tone (optional)'
  },
  {
    id: 'height_bracket',
    label: 'Height',
    type: 'select',
    options: [
      { value: '<160', label: 'Under 160cm' },
      { value: '160-175', label: '160-175cm' },
      { value: '175-190', label: '175-190cm' },
      { value: '>190', label: 'Over 190cm' },
      { value: 'PreferNot', label: 'Prefer not to say' }
    ],
    description: 'Your height range (optional)'
  },
  {
    id: 'visible_disability',
    label: 'Visible disability',
    type: 'boolean',
    description: 'Do you have a visible disability? (optional)'
  },
  {
    id: 'concession',
    label: 'Concession or MYKI Money',
    type: 'boolean',
    description: 'Do you use a concession card or MYKI Money? (optional)'
  }
];

export const getFieldsByStep = (step: number) => {
  const stepsConfig = [
    ['trips', 'stops'], // Step 1: Essential data
    ['age_bracket', 'gender'], // Step 2: Basic demographics
    ['ethnicity', 'skin_tone'], // Step 3: Appearance
    ['height_bracket', 'visible_disability', 'concession'] // Step 4: Other traits
  ];
  
  return formFields.filter(field => stepsConfig[step]?.includes(field.id));
};

export const totalSteps = 4;