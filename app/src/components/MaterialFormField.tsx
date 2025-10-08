'use client';

import {
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Typography,
  Box,
  Select,
  MenuItem,
  InputLabel,
  FormHelperText,
} from '@mui/material';

interface Option {
  value: string;
  label: string;
}

interface MaterialFormFieldProps {
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

export default function MaterialFormField({
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
}: MaterialFormFieldProps) {
  const renderInput = () => {
    switch (type) {
      case 'select':
        return (
          <FormControl fullWidth margin="normal" error={!!error}>
            <InputLabel id={`${id}-label`}>{label}</InputLabel>
            <Select
              labelId={`${id}-label`}
              id={id}
              value={value || ''}
              label={label}
              onChange={(e) => onChange(e.target.value || null)}
            >
              {options.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
            {description && (
              <FormHelperText>{description}</FormHelperText>
            )}
            {error && (
              <FormHelperText error>{error}</FormHelperText>
            )}
          </FormControl>
        );

      case 'number':
        return (
          <TextField
            id={id}
            label={label}
            type="number"
            value={value || ''}
            onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
            variant="outlined"
            fullWidth
            margin="normal"
            required={required}
            inputProps={{ min, max }}
            helperText={error || description}
            error={!!error}
          />
        );

      case 'boolean':
        return (
          <Box sx={{ mt: 2, mb: 1 }}>
            <FormControl component="fieldset" error={!!error}>
              <FormLabel component="legend">
                <Typography variant="body1" sx={{ mb: 1 }}>
                  {label}
                </Typography>
              </FormLabel>
              <RadioGroup
                row
                value={value === null || value === undefined ? 'prefer-not' : value.toString()}
                onChange={(e) => {
                  const val = e.target.value;
                  if (val === 'prefer-not') {
                    onChange(null);
                  } else {
                    onChange(val === 'true');
                  }
                }}
              >
                <FormControlLabel
                  value="true"
                  control={<Radio />}
                  label="Yes"
                />
                <FormControlLabel
                  value="false"
                  control={<Radio />}
                  label="No"
                />
                <FormControlLabel
                  value="prefer-not"
                  control={<Radio />}
                  label="Prefer not to say"
                />
              </RadioGroup>
              {description && (
                <FormHelperText>{description}</FormHelperText>
              )}
              {error && (
                <FormHelperText error>{error}</FormHelperText>
              )}
            </FormControl>
          </Box>
        );

      default:
        return null;
    }
  };

  return renderInput();
}