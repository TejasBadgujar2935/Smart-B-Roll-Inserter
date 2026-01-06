import React from 'react';
import './GenerateButton.css';

// UI-only: button + inline loading spinner when generating
function GenerateButton({ onClick, loading, disabled }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`generate-button ${loading ? 'loading' : ''}`}
    >
      {loading && <span className="generate-spinner" aria-hidden="true" />}
      <span className="generate-label">
        {loading ? 'Generating timeline…' : 'Generate Timeline'}
      </span>
    </button>
  );
}

export default GenerateButton;

