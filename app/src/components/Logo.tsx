import Image from 'next/image';
import { Box, Typography } from '@mui/material';

interface LogoProps {
  size?: 'small' | 'medium' | 'large';
  showText?: boolean;
  variant?: 'light' | 'dark';
}

const sizeMap = {
  small: { width: 32, height: 32, textSize: 'h6' as const },
  medium: { width: 48, height: 48, textSize: 'h5' as const },
  large: { width: 64, height: 64, textSize: 'h4' as const },
};

export default function Logo({ 
  size = 'medium', 
  showText = true, 
  variant = 'dark' 
}: LogoProps) {
  const { width, height, textSize } = sizeMap[size];
  
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: showText ? 2 : 0 
      }}
    >
      <Image
        src="/logo1.png"
        alt="StopOdds Logo"
        width={width}
        height={height}
        style={{
          borderRadius: '8px',
          objectFit: 'contain'
        }}
      />
      {showText && (
        <Typography 
          variant={textSize} 
          component="span" 
          sx={{ 
            fontWeight: 700,
            color: variant === 'light' ? 'white' : 'text.primary',
            letterSpacing: '-0.02em'
          }}
        >
          StopOdds
        </Typography>
      )}
    </Box>
  );
}