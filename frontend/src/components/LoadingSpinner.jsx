import React from 'react';
import { FaSpinner } from 'react-icons/fa';

const LoadingSpinner = () => {
  return (
    <div className="card text-center py-12">
      <FaSpinner className="text-6xl text-accent animate-spin mx-auto mb-6" />
      <h2 className="text-2xl font-heading mb-3">Analyzing Your Documents</h2>
      <p className="text-gray-600 mb-2">
        Our AI is carefully reviewing your accident report and photos...
      </p>
      <p className="text-sm text-gray-500">
        This typically takes 30-60 seconds
      </p>
      <div className="mt-8 max-w-md mx-auto">
        <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
          <div className="bg-accent h-full rounded-full animate-pulse" style={{ width: '60%' }}></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;