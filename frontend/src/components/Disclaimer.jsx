import React from 'react';
import { FaExclamationTriangle } from 'react-icons/fa';

const Disclaimer = () => {
  return (
    <div className="disclaimer-box mb-8">
      <div className="flex items-start space-x-3">
        <FaExclamationTriangle className="text-yellow-600 text-xl mt-1 flex-shrink-0" />
        <div>
          <h3 className="font-heading font-bold text-lg mb-2">Important Legal Notice</h3>
          <p className="text-sm text-gray-700">
            This tool provides an automated summary for attorney review and is <strong>not legal advice</strong>. 
            Using this service does not create an attorney-client relationship. The analysis is generated 
            by AI and should be reviewed by a qualified legal professional before any action is taken.
          </p>
          <p className="text-sm text-gray-700 mt-2">
            Bu araç, avukat incelemesi için otomatik bir özet sağlar ve <strong>hukuki tavsiye değildir</strong>. 
            Bu hizmeti kullanmak avukat-müvekkil ilişkisi oluşturmaz.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Disclaimer;