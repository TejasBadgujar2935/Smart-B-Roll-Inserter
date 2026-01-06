import React from 'react';
import './VideoUploader.css';

function VideoUploader({ onFileSelect, selectedFile, label }) {
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <div className="video-uploader">
      <label className="upload-label">
        <span>{label}:</span>
        <input
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          className="file-input"
        />
        <span className="file-name">
          {selectedFile ? selectedFile.name : 'No file selected'}
        </span>
      </label>
    </div>
  );
}

export default VideoUploader;

