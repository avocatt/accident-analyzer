import React, { useState } from 'react';
import parse from 'html-react-parser';
import { 
  FaDownload, FaRedo, FaCheckCircle, FaExclamationTriangle, 
  FaCar, FaMapMarkerAlt, FaClock, FaBalanceScale, FaFileAlt
} from 'react-icons/fa';

const AnalysisResults = ({ result, onReset }) => {
  const [activeTab, setActiveTab] = useState('summary');
  
  const downloadBriefing = (format) => {
    if (format === 'html') {
      const blob = new Blob([result.briefing_html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `lexintake_briefing_${result.session_id}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } else if (format === 'pdf') {
      // In a real implementation, this would fetch the PDF from the backend
      alert('PDF download will be implemented with backend integration');
    }
  };

  const renderTabContent = () => {
    switch(activeTab) {
      case 'summary':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center">
                <FaFileAlt className="mr-2 text-accent" />
                Case Summary
              </h3>
              <p className="text-gray-700">{result.analysis.case_summary}</p>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center">
                <FaMapMarkerAlt className="mr-2 text-accent" />
                Accident Details
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <FaClock className="text-utility" />
                  <span className="font-medium">Date & Time:</span>
                  <span>{result.analysis.accident_details.date} - {result.analysis.accident_details.time}</span>
                </div>
                <div className="flex items-start space-x-2">
                  <FaMapMarkerAlt className="text-utility mt-1" />
                  <span className="font-medium">Location:</span>
                  <span className="flex-1">{result.analysis.accident_details.location}</span>
                </div>
              </div>
            </div>

            <div className="bg-green-50 border-l-4 border-accent p-4 rounded-r-lg">
              <h3 className="text-lg font-semibold mb-3 flex items-center">
                <FaBalanceScale className="mr-2 text-accent" />
                Preliminary Fault Assessment
              </h3>
              {result.analysis.fault_assessment.preliminary_fault_party && (
                <p className="mb-2">
                  <strong>Likely At-Fault Party:</strong> {result.analysis.fault_assessment.preliminary_fault_party}
                </p>
              )}
              {result.analysis.fault_assessment.party_a_fault_percentage !== null && (
                <div className="mt-3">
                  <p className="text-sm font-medium mb-2">Estimated Fault Distribution:</p>
                  <div className="flex space-x-4">
                    <div className="flex-1">
                      <div className="bg-white rounded-lg p-3">
                        <p className="text-sm text-gray-600">Party A</p>
                        <p className="text-2xl font-bold text-primary">
                          {result.analysis.fault_assessment.party_a_fault_percentage}%
                        </p>
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="bg-white rounded-lg p-3">
                        <p className="text-sm text-gray-600">Party B</p>
                        <p className="text-2xl font-bold text-primary">
                          {result.analysis.fault_assessment.party_b_fault_percentage}%
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        );

      case 'parties':
        return (
          <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-blue-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <FaCar className="mr-2 text-primary" />
                  Party A (Sürücü A)
                </h3>
                <div className="space-y-2">
                  <div>
                    <span className="font-medium text-gray-600">Name:</span>
                    <p className="text-lg">{result.analysis.party_a.name}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Vehicle Plate:</span>
                    <p className="text-lg">{result.analysis.party_a.vehicle_plate}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Vehicle Type:</span>
                    <p>{result.analysis.party_a.vehicle_type}</p>
                  </div>
                  {result.analysis.party_a.insurance_company && (
                    <div>
                      <span className="font-medium text-gray-600">Insurance:</span>
                      <p>{result.analysis.party_a.insurance_company}</p>
                    </div>
                  )}
                </div>
              </div>

              <div className="bg-orange-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <FaCar className="mr-2 text-orange-600" />
                  Party B (Sürücü B)
                </h3>
                <div className="space-y-2">
                  <div>
                    <span className="font-medium text-gray-600">Name:</span>
                    <p className="text-lg">{result.analysis.party_b.name}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Vehicle Plate:</span>
                    <p className="text-lg">{result.analysis.party_b.vehicle_plate}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Vehicle Type:</span>
                    <p>{result.analysis.party_b.vehicle_type}</p>
                  </div>
                  {result.analysis.party_b.insurance_company && (
                    <div>
                      <span className="font-medium text-gray-600">Insurance:</span>
                      <p>{result.analysis.party_b.insurance_company}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        );

      case 'details':
        return (
          <div className="space-y-6">
            {result.analysis.form_checkboxes && (
              <div>
                <h3 className="text-lg font-semibold mb-3">Form Analysis</h3>
                
                {result.analysis.form_checkboxes.section_12_selections?.length > 0 && (
                  <div className="mb-4">
                    <p className="font-medium text-gray-700">Damage Zones (Section 12):</p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {result.analysis.form_checkboxes.section_12_selections.map(zone => (
                        <span key={zone} className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm">
                          Zone {zone}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {result.analysis.form_checkboxes.section_13_selections?.length > 0 && (
                  <div className="mb-4">
                    <p className="font-medium text-gray-700">Accident Scenarios (Section 13):</p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {result.analysis.form_checkboxes.section_13_selections.map(scenario => (
                        <span key={scenario} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                          Scenario {scenario}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {result.analysis.photo_analyses?.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-3">Photo Analysis</h3>
                <div className="space-y-3">
                  {result.analysis.photo_analyses.map((photo, idx) => (
                    <div key={idx} className="bg-gray-50 rounded-lg p-4">
                      <p className="font-medium text-gray-700">Photo {photo.photo_id}:</p>
                      <p className="text-gray-600 mt-1">{photo.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.analysis.recommended_actions?.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-3">Recommended Actions</h3>
                <ul className="space-y-2">
                  {result.analysis.recommended_actions.map((action, idx) => (
                    <li key={idx} className="flex items-start">
                      <FaCheckCircle className="text-accent mt-1 mr-2 flex-shrink-0" />
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );

      case 'full':
        return (
          <div className="prose max-w-none">
            {parse(result.briefing_html)}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Success Banner */}
      <div className="bg-green-50 border-l-4 border-accent p-4 rounded-r-lg">
        <div className="flex items-center">
          <FaCheckCircle className="text-accent text-2xl mr-3" />
          <div className="flex-1">
            <h3 className="font-semibold">Analysis Complete!</h3>
            <p className="text-sm text-gray-600">
              Your accident report has been successfully analyzed. Review the findings below.
            </p>
          </div>
        </div>
      </div>

      {/* Data Quality Indicator */}
      {result.analysis.extraction_confidence && (
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <span className="font-medium">Analysis Confidence</span>
            <span className="text-lg font-bold text-accent">
              {Math.round(result.analysis.extraction_confidence * 100)}%
            </span>
          </div>
          <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-accent h-full rounded-full transition-all duration-500"
              style={{ width: `${result.analysis.extraction_confidence * 100}%` }}
            />
          </div>
          {result.analysis.missing_information?.length > 0 && (
            <div className="mt-3 text-sm text-orange-600">
              <FaExclamationTriangle className="inline mr-1" />
              Missing: {result.analysis.missing_information.join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="card">
        <div className="border-b mb-6">
          <div className="flex space-x-6">
            {[
              { id: 'summary', label: 'Summary' },
              { id: 'parties', label: 'Parties' },
              { id: 'details', label: 'Details' },
              { id: 'full', label: 'Full Report' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`pb-3 px-1 border-b-2 transition-colors font-medium
                  ${activeTab === tab.id 
                    ? 'border-accent text-accent' 
                    : 'border-transparent text-gray-600 hover:text-primary'}`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="min-h-[400px]">
          {renderTabContent()}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={() => downloadBriefing('html')}
          className="btn-primary flex items-center justify-center space-x-2"
        >
          <FaDownload />
          <span>Download HTML Report</span>
        </button>
        
        <button
          onClick={() => downloadBriefing('pdf')}
          className="btn-secondary flex items-center justify-center space-x-2"
        >
          <FaDownload />
          <span>Download PDF Report</span>
        </button>
        
        <button
          onClick={onReset}
          className="bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold 
                   hover:bg-gray-700 transition-colors duration-200
                   flex items-center justify-center space-x-2"
        >
          <FaRedo />
          <span>Analyze Another Case</span>
        </button>
      </div>
    </div>
  );
};

export default AnalysisResults;