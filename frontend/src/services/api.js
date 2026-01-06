import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for video processing
});

/**
 * Generate timeline from A-roll video and B-roll metadata
 * 
 * @param {File} arollVideo - A-roll video file
 * @param {Object} brollMetadata - Dictionary mapping broll_id to metadata
 * @param {number} similarityThreshold - Similarity threshold (0.0-1.0)
 * @param {number} minInsertions - Minimum B-roll insertions
 * @param {number} maxInsertions - Maximum B-roll insertions
 * @returns {Promise<Object>} Timeline JSON
 */
export async function generateTimeline(
  arollVideo,
  brollMetadata,
  similarityThreshold = 0.72,
  minInsertions = 3,
  maxInsertions = 6
) {
  const formData = new FormData();
  
  // Add A-roll video
  formData.append('aroll_video', arollVideo);
  
  // Add B-roll metadata as JSON string
  formData.append('broll_metadata', JSON.stringify(brollMetadata));
  
  // Add optional parameters
  formData.append('similarity_threshold', similarityThreshold.toString());
  formData.append('min_insertions', minInsertions.toString());
  formData.append('max_insertions', maxInsertions.toString());

  try {
    const response = await api.post('/generate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    if (error.response) {
      // Server responded with error
      const errorMessage = error.response.data?.detail || error.response.data?.message || 'Unknown error';
      throw new Error(errorMessage);
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Is the backend running?');
    } else {
      // Error setting up request
      throw new Error(error.message);
    }
  }
}

/**
 * Check API health
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Health check failed');
  }
}

export default api;

