'use client';

import { useEffect, useState } from 'react';
import FormCard from './FormCard';

interface SuccessScreenProps {
  onReset: () => void;
}

export default function SuccessScreen({ onReset }: SuccessScreenProps) {
  const [showConfetti, setShowConfetti] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setShowConfetti(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl relative">
        {/* Confetti Effect */}
        {showConfetti && (
          <div className="absolute inset-0 pointer-events-none">
            {[...Array(20)].map((_, i) => (
              <div
                key={i}
                className="absolute w-2 h-2 bg-gradient-to-r from-blue-400 to-purple-600 rounded-full animate-bounce"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 2}s`,
                  animationDuration: `${1 + Math.random()}s`
                }}
              />
            ))}
          </div>
        )}

        {/* Success Card */}
        <FormCard className="p-12 text-center">
          <div className="mb-8">
            <div className="w-20 h-20 bg-gradient-to-r from-green-400 to-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            <h1 className="text-4xl font-bold text-gray-800 mb-4">
              Thank You! 🎉
            </h1>
            
            <p className="text-xl text-gray-600 mb-6">
              Your data has been successfully submitted to StopOdds
            </p>
          </div>

          <div className="bg-blue-50 rounded-xl p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">
              What happens next?
            </h2>
            <ul className="text-left text-gray-600 space-y-2">
              <li className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                Your anonymous data joins our growing dataset
              </li>
              <li className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                We'll analyze patterns to calculate stop rates by demographic group
              </li>
              <li className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                Results will be published transparently with confidence intervals
              </li>
              <li className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                All methodology and code will be made publicly available
              </li>
            </ul>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <a
              href="/results"
              className="px-6 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 transition-all duration-200 button-press"
            >
              View Results
            </a>
            <a
              href="/methodology"
              className="px-6 py-4 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-all duration-200 button-press"
            >
              Our Methodology
            </a>
          </div>

          <button
            onClick={onReset}
            className="text-blue-600 hover:text-blue-800 font-medium transition-colors duration-200"
          >
            Submit another response
          </button>
        </FormCard>

        {/* Privacy Reminder */}
        <FormCard className="p-6 mt-6 text-center">
          <div className="flex items-center justify-center mb-3">
            <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <h3 className="font-semibold text-gray-800">Privacy Protected</h3>
          </div>
          <p className="text-sm text-gray-600">
            Your submission contains no personally identifiable information and cannot be traced back to you. 
            Groups with fewer than 50 respondents will be suppressed from public results to ensure privacy.
          </p>
        </FormCard>
      </div>
    </div>
  );
}