import React from 'react';
import { FaBalanceScale } from 'react-icons/fa';

const Header = () => {
  return (
    <header className="bg-primary text-white shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FaBalanceScale className="text-3xl text-accent" />
            <div>
              <h1 className="text-2xl font-heading font-bold">LexIntake</h1>
              <p className="text-sm text-gray-300">AI-Powered Traffic Accident Analysis</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-300">Turkish Legal Market Solution</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;