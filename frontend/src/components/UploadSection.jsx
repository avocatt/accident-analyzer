import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaFileUpload, FaFilePdf, FaImage, FaTrash, FaCheckCircle } from 'react-icons/fa';

const UploadSection = ({ onAnalyze }) => {
  const [mainReport, setMainReport] = useState(null);
  const [additionalPhotos, setAdditionalPhotos] = useState([]);
  const [clientInfo, setClientInfo] = useState({
    name: '',
    email: '',
    notes: ''
  });
  const [errors, setErrors] = useState({});

  // Main report dropzone
  const onDropReport = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setMainReport(acceptedFiles[0]);
      setErrors(prev => ({ ...prev, report: null }));
    }
  }, []);

  const { getRootProps: getReportRootProps, getInputProps: getReportInputProps, isDragActive: isReportDragActive } = useDropzone({
    onDrop: onDropReport,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    },
    multiple: false,
    maxSize: 10485760 // 10MB
  });

  // Photos dropzone
  const onDropPhotos = useCallback((acceptedFiles) => {
    setAdditionalPhotos(prev => [...prev, ...acceptedFiles].slice(0, 5)); // Max 5 photos
  }, []);

  const { getRootProps: getPhotosRootProps, getInputProps: getPhotosInputProps, isDragActive: isPhotosDragActive } = useDropzone({
    onDrop: onDropPhotos,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    },
    multiple: true,
    maxSize: 10485760 // 10MB per file
  });

  const removePhoto = (index) => {
    setAdditionalPhotos(prev => prev.filter((_, i) => i !== index));
  };

  const validateForm = () => {
    const newErrors = {};
    if (!mainReport) {
      newErrors.report = 'Kaza Tespit Tutanağı is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const formData = new FormData();
    formData.append('accident_report', mainReport);
    
    additionalPhotos.forEach((photo) => {
      formData.append('photos', photo);
    });
    
    if (clientInfo.name) {
      formData.append('client_name', clientInfo.name);
    }
    if (clientInfo.email) {
      formData.append('client_email', clientInfo.email);
    }
    if (clientInfo.notes) {
      formData.append('additional_notes', clientInfo.notes);
    }

    onAnalyze(formData);
  };

  const getFileIcon = (file) => {
    if (file.type === 'application/pdf') {
      return <FaFilePdf className="text-red-500" />;
    }
    return <FaImage className="text-blue-500" />;
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-2xl font-heading mb-6">Upload Documents</h2>
        
        {/* Step 1: Main Report */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <span className="bg-accent text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">1</span>
            Upload Kaza Tespit Tutanağı (Required)
          </h3>
          
          <div
            {...getReportRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isReportDragActive ? 'border-accent bg-green-50' : 'border-gray-300 hover:border-accent'}
              ${errors.report ? 'border-red-500 bg-red-50' : ''}
              ${mainReport ? 'bg-green-50 border-green-500' : ''}`}
          >
            <input {...getReportInputProps()} />
            {mainReport ? (
              <div className="flex items-center justify-center space-x-3">
                <FaCheckCircle className="text-green-500 text-2xl" />
                <div className="text-left">
                  <p className="font-semibold">{mainReport.name}</p>
                  <p className="text-sm text-gray-600">
                    {(mainReport.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setMainReport(null);
                  }}
                  className="ml-4 text-red-500 hover:text-red-700"
                >
                  <FaTrash />
                </button>
              </div>
            ) : (
              <>
                <FaFileUpload className="text-4xl text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">
                  {isReportDragActive ? 'Drop the file here' : 'Drag & drop your accident report here'}
                </p>
                <p className="text-sm text-gray-500 mt-2">or click to select (PDF or Image, max 10MB)</p>
              </>
            )}
          </div>
          {errors.report && (
            <p className="text-red-500 text-sm mt-2">{errors.report}</p>
          )}
        </div>

        {/* Step 2: Additional Photos */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <span className="bg-primary text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">2</span>
            Upload Additional Photos (Optional)
          </h3>
          
          <div
            {...getPhotosRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isPhotosDragActive ? 'border-accent bg-green-50' : 'border-gray-300 hover:border-accent'}`}
          >
            <input {...getPhotosInputProps()} />
            <FaImage className="text-4xl text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">
              {isPhotosDragActive ? 'Drop photos here' : 'Drag & drop accident photos here'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              or click to select (max 5 photos, 10MB each)
            </p>
          </div>
          
          {additionalPhotos.length > 0 && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3">
              {additionalPhotos.map((photo, index) => (
                <div key={index} className="relative group">
                  <div className="bg-gray-100 rounded-lg p-3 flex flex-col items-center">
                    <FaImage className="text-blue-500 text-2xl mb-2" />
                    <p className="text-xs text-gray-600 truncate w-full text-center">
                      {photo.name}
                    </p>
                    <button
                      type="button"
                      onClick={() => removePhoto(index)}
                      className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 
                               opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <FaTrash className="text-xs" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Step 3: Additional Information */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <span className="bg-utility text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">3</span>
            Additional Information (Optional)
          </h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Client Name
              </label>
              <input
                type="text"
                value={clientInfo.name}
                onChange={(e) => setClientInfo(prev => ({ ...prev, name: e.target.value }))}
                className="input-field"
                placeholder="Enter client name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Client Email
              </label>
              <input
                type="email"
                value={clientInfo.email}
                onChange={(e) => setClientInfo(prev => ({ ...prev, email: e.target.value }))}
                className="input-field"
                placeholder="Enter client email"
              />
            </div>
          </div>
          
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Notes
            </label>
            <textarea
              value={clientInfo.notes}
              onChange={(e) => setClientInfo(prev => ({ ...prev, notes: e.target.value }))}
              className="input-field"
              rows={3}
              placeholder="Any additional information about the accident..."
            />
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-center">
          <button
            onClick={handleSubmit}
            disabled={!mainReport}
            className={`btn-primary flex items-center space-x-2 ${!mainReport ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <FaCheckCircle />
            <span>Analyze My Case</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadSection;