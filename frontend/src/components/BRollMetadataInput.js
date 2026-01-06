import React, { useState } from 'react';
import './BRollMetadataInput.css';

function BRollMetadataInput({ metadata, onMetadataChange }) {
  const [brollId, setBrollId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [subject, setSubject] = useState('');
  const [action, setAction] = useState('');
  const [location, setLocation] = useState('');
  const [mood, setMood] = useState('');

  const handleAdd = () => {
    if (!brollId) {
      alert('Please enter a B-roll ID');
      return;
    }

    const newMetadata = {
      ...metadata,
      [brollId]: {
        ...(title && { title }),
        ...(description && { description }),
        ...(category && { category }),
        ...(subject && { subject }),
        ...(action && { action }),
        ...(location && { location }),
        ...(mood && { mood })
      }
    };

    onMetadataChange(newMetadata);

    // Reset form
    setBrollId('');
    setTitle('');
    setDescription('');
    setCategory('');
    setSubject('');
    setAction('');
    setLocation('');
    setMood('');
  };

  const handleRemove = (id) => {
    const newMetadata = { ...metadata };
    delete newMetadata[id];
    onMetadataChange(newMetadata);
  };

  return (
    <div className="broll-metadata-input">
      <div className="metadata-form">
        <div className="form-row">
          <input
            type="text"
            placeholder="B-roll ID (e.g., broll_1)"
            value={brollId}
            onChange={(e) => setBrollId(e.target.value)}
            className="form-input"
          />
          <button onClick={handleAdd} className="add-button">
            Add B-Roll
          </button>
        </div>

        <div className="form-fields">
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="form-input"
          />
          <textarea
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="form-textarea"
            rows="2"
          />
          <div className="form-row-small">
            <input
              type="text"
              placeholder="Category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="form-input-small"
            />
            <input
              type="text"
              placeholder="Subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="form-input-small"
            />
            <input
              type="text"
              placeholder="Action"
              value={action}
              onChange={(e) => setAction(e.target.value)}
              className="form-input-small"
            />
            <input
              type="text"
              placeholder="Location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="form-input-small"
            />
            <input
              type="text"
              placeholder="Mood"
              value={mood}
              onChange={(e) => setMood(e.target.value)}
              className="form-input-small"
            />
          </div>
        </div>
      </div>

      <div className="metadata-list">
        <h3>Added B-Rolls ({Object.keys(metadata).length})</h3>
        {Object.keys(metadata).length === 0 ? (
          <p className="empty-message">No B-rolls added yet</p>
        ) : (
          <div className="metadata-items">
            {Object.entries(metadata).map(([id, data]) => (
              <div key={id} className="metadata-item">
                <div className="metadata-item-header">
                  <strong>{id}</strong>
                  <button
                    onClick={() => handleRemove(id)}
                    className="remove-button"
                  >
                    Remove
                  </button>
                </div>
                <div className="metadata-item-content">
                  {data.title && <div><strong>Title:</strong> {data.title}</div>}
                  {data.description && (
                    <div><strong>Description:</strong> {data.description}</div>
                  )}
                  {data.category && (
                    <div><strong>Category:</strong> {data.category}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default BRollMetadataInput;

