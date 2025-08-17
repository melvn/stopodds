'use client';

import { ReactNode } from 'react';

interface FormCardProps {
  children: ReactNode;
  className?: string;
  animate?: boolean;
}

export default function FormCard({ children, className = '', animate = true }: FormCardProps) {
  return (
    <div 
      className={`
        bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20
        ${animate ? 'card-hover slide-in' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
}