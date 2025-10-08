'use client';

import { useState } from 'react';

interface Option {
  value: string;
  label: string;
}

interface FormFieldProps {
  id: string;
  label: string;
  type: 'select' | 'number' | 'boolean';
  value: any;
  onChange: (value: any) => void;
  options?: Option[];
  required?: boolean;
  min?: number;
  max?: number;
  description?: string;
  error?: string;
}

export default function FormField({
  id,
  label,
  type,
  value,
  onChange,
  options = [],
  required = false,
  min,
  max,
  description,
  error
}: FormFieldProps) {
  const [isFocused, setIsFocused] = useState(false);

  const baseInputClass = `
    w-full px-4 py-3 rounded-xl border-2 transition-all duration-200
    font-medium text-gray-800 placeholder-gray-400
    ${error 
      ? 'border-red-300 bg-red-50 focus:border-red-500 focus:ring-4 focus:ring-red-500/20' 
      : isFocused
        ? 'border-blue-500 bg-blue-50 focus:ring-4 focus:ring-blue-500/20'
        : 'border-gray-200 bg-gray-50 hover:border-gray-300 focus:border-blue-500'
    }
    focus:outline-none focus:bg-white
  `;

  const renderInput = () => {
    switch (type) {
      case 'select':
        return (
          <select
            id={id}
            value={value || ''}
            onChange={(e) => onChange(e.target.value || null)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            className={baseInputClass}
            required={required}
          >
            <option value="">Select an option</option>
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'number':
        return (
          <input
            type="number"
            id={id}
            value={value || ''}
            onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            className={baseInputClass}
            min={min}
            max={max}
            required={required}
            placeholder={`Enter ${label.toLowerCase()}`}
          />
        );

      case 'boolean':
        return (
          <div className="grid grid-cols-3 gap-3">
            {[
              { value: true, label: 'Yes' },
              { value: false, label: 'No' },
              { value: null, label: 'Prefer not to say' }
            ].map((option) => (
              <button
                key={String(option.value)}
                type="button"
                onClick={() => onChange(option.value)}
                className={`
                  px-4 py-3 rounded-xl font-medium transition-all duration-200 button-press
                  ${value === option.value
                    ? 'bg-blue-500 text-white shadow-lg scale-105'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border-2 border-transparent hover:border-gray-300'
                  }
                `}
              >
                {option.label}
              </button>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-2">
      <label htmlFor={id} className="block text-sm font-semibold text-gray-800">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {description && (
        <p className="text-sm text-gray-600">{description}</p>
      )}
      
      <div className="scale-in">
        {renderInput()}
      </div>
      
      {error && (
        <p className="text-sm text-red-600 font-medium fade-in">{error}</p>
      )}
    </div>
  );
}