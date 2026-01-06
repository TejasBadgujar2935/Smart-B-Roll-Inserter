import React, { useState } from 'react';
import './App.css';
import VideoUploader from './components/VideoUploader';
import BRollMetadataInput from './components/BRollMetadataInput';
import GenerateButton from './components/GenerateButton';
import ResultsDisplay from './components/ResultsDisplay';
import { generateTimeline } from './services/api';

function App() {
  const [arollVideo, setArollVideo] = useState(null);
  const [brollMetadata, setBrollMetadata] = useState({});
  const [similarityThreshold, setSimilarityThreshold] = useState(0.72);
  const [minInsertions, setMinInsertions] = useState(3);
  const [maxInsertions, setMaxInsertions] = useState(6);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState('dark'); // UI-only: light/dark mode

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleGenerate = async () => {
    if (!arollVideo) {
      setError('Please upload an A-roll video');
      return;
    }

    const brollCount = Object.keys(brollMetadata).length;
    if (brollCount < 3) {
      setError('Please add at least 3 B-rolls before generating.');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const timeline = await generateTimeline(
        arollVideo,
        brollMetadata,
        similarityThreshold,
        minInsertions,
        maxInsertions
      );
      setResults(timeline);
    } catch (err) {
      const message = err?.message || 'Failed to generate timeline';
      // Friendly quota/credits message (UI-only)
      if (
        message.toLowerCase().includes('quota') ||
        message.toLowerCase().includes('insufficient') ||
        message.toLowerCase().includes('credit')
      ) {
        setError('AI credits exhausted. Please add credits to continue.');
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`App App--${theme}`}>
      <header className="App-header">
        <div className="App-header-top">
          <h1>Smart B-Roll Inserter</h1>
          <button
            type="button"
            className="theme-toggle-button"
            onClick={toggleTheme}
            aria-label="Toggle dark/light mode"
          >
            <span className="theme-toggle-thumb" />
            <span className="theme-toggle-label">
              {theme === 'dark' ? 'Dark' : 'Light'} mode
            </span>
          </button>
        </div>
        <p>Automatically generate timeline plans for B-roll insertion</p>
      </header>

      <main className="App-main">
        <div className="input-section">
          <h2>1. Upload A-Roll Video</h2>
          <VideoUploader
            onFileSelect={setArollVideo}
            selectedFile={arollVideo}
            label="A-Roll Video"
          />

          <h2>2. Add B-Roll Metadata</h2>
          <BRollMetadataInput
            metadata={brollMetadata}
            onMetadataChange={setBrollMetadata}
          />

          <h2>3. Settings</h2>
          <div className="settings">
            <div className="setting-item">
              <label>
                Similarity Threshold:
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={similarityThreshold}
                  onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                />
              </label>
            </div>
            <div className="setting-item">
              <label>
                Min Insertions:
                <input
                  type="number"
                  min="0"
                  max="20"
                  value={minInsertions}
                  onChange={(e) => setMinInsertions(parseInt(e.target.value))}
                />
              </label>
            </div>
            <div className="setting-item">
              <label>
                Max Insertions:
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={maxInsertions}
                  onChange={(e) => setMaxInsertions(parseInt(e.target.value))}
                />
              </label>
            </div>
          </div>

          <h2>4. Generate Timeline</h2>
          <GenerateButton
            onClick={handleGenerate}
            loading={loading}
            disabled={!arollVideo || Object.keys(brollMetadata).length < 3}
          />
        </div>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {results && (
          <ResultsDisplay results={results} />
        )}
      </main>
    </div>
  );
}

export default App;

