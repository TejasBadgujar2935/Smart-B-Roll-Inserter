import React, { useState } from 'react';
import './ResultsDisplay.css';

function ResultsDisplay({ results }) {
  const [activeTab, setActiveTab] = useState('timeline');

  if (!results) return null;

  // Extract transcript from segments
  const transcript = results.segments
    ?.filter(seg => seg.type === 'a_roll' && seg.transcript)
    .map(seg => ({
      start: seg.start_time,
      end: seg.end_time,
      text: seg.transcript
    })) || [];

  return (
    <div className="results-display">
      <h2>Results</h2>

      <div className="results-summary">
        <div className="summary-item">
          <strong>Timeline ID:</strong> {results.timeline_id}
        </div>
        <div className="summary-item">
          <strong>Total Duration:</strong> {results.total_duration}s
        </div>
        {results.statistics && (
          <>
            <div className="summary-item">
              <strong>B-roll Insertions:</strong> {results.statistics.broll_insertions}
            </div>
            <div className="summary-item">
              <strong>Average Confidence:</strong> {results.statistics.average_confidence?.toFixed(3)}
            </div>
          </>
        )}
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'timeline' ? 'active' : ''}`}
          onClick={() => setActiveTab('timeline')}
        >
          Timeline JSON
        </button>
        <button
          className={`tab ${activeTab === 'transcript' ? 'active' : ''}`}
          onClick={() => setActiveTab('transcript')}
        >
          Transcript
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'timeline' && (
          <div className="json-display">
            <pre>{JSON.stringify(results, null, 2)}</pre>
          </div>
        )}

        {activeTab === 'transcript' && (
          <div className="transcript-display">
            {transcript.length === 0 ? (
              <p>No transcript available</p>
            ) : (
              <div className="transcript-segments">
                {transcript.map((seg, index) => (
                  <div key={index} className="transcript-segment">
                    <div className="segment-time">
                      {seg.start.toFixed(2)}s - {seg.end.toFixed(2)}s
                    </div>
                    <div className="segment-text">{seg.text}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultsDisplay;

