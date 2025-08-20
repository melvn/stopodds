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
      <Box
        sx={{
          position: 'relative',
          width: width + 20,
          height: height + 20,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'scale(1.05)',
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `
              radial-gradient(
                ellipse at center,
                transparent 35%,
                rgba(248, 250, 252, 0.3) 50%,
                rgba(248, 250, 252, 0.7) 70%,
                rgba(248, 250, 252, 0.9) 85%,
                rgba(248, 250, 252, 1) 100%
              )
            `,
            borderRadius: '50%',
            pointerEvents: 'none',
          }
        }}
      >
        <Image
          src="/logo1.png"
          alt="StopOdds Logo"
          width={width}
          height={height}
          style={{
            objectFit: 'contain',
            position: 'relative',
            zIndex: 1,
            filter: 'drop-shadow(0 2px 8px rgba(30, 58, 138, 0.15))',
            transition: 'filter 0.3s ease'
          }}
        />
      </Box>
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