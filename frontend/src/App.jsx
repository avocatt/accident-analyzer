import React, { useState } from 'react';
import Header from './components/Header';
import Disclaimer from './components/Disclaimer';
import UploadSection from './components/UploadSection';
import AnalysisResults from './components/AnalysisResults';
import LoadingSpinner from './components/LoadingSpinner';
import axios from 'axios';

const resolveApiBaseUrl = () => {
  if (import.meta.env.VITE_BACKEND_URL) {
    return import.meta.env.VITE_BACKEND_URL;
  }

  if (import.meta.env.DEV) {
    return 'http://localhost:8000';
  }

  if (typeof window !== 'undefined') {
    return window.location.origin;
  }

  return '';
};

const API_BASE_URL = resolveApiBaseUrl();

function App() {
  const [currentStep, setCurrentStep] = useState('upload'); // upload, analyzing, results
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (formData) => {
    setCurrentStep('analyzing');
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minute timeout
      });

      setAnalysisResult(response.data);
      setCurrentStep('results');
    } catch (err) {
      console.error('Analysis error:', err);
      setError(
        err.response?.data?.detail || 
        'An error occurred during analysis. Please try again.'
      );
      setCurrentStep('upload');
    }
  };

  const handleReset = () => {
    setCurrentStep('upload');
    setAnalysisResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-secondary">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <Disclaimer />
        
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-r-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}
        
        {currentStep === 'upload' && (
          <UploadSection onAnalyze={handleAnalyze} />
        )}
        
        {currentStep === 'analyzing' && (
          <LoadingSpinner />
        )}
        
        {currentStep === 'results' && analysisResult && (
          <AnalysisResults 
            result={analysisResult} 
            onReset={handleReset}
          />
        )}
      </main>
      
      <footer className="bg-primary text-white py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm">
            © 2024 LexIntake. AI-Powered Legal Document Analysis.
          </p>
          <p className="text-xs mt-2 text-gray-300">
            This tool provides automated summaries for attorney review and is not legal advice.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
