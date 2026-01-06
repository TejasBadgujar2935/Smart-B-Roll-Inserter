# Quick Start - React Frontend

## Setup (One-time)

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start backend server** (in another terminal):
```bash
cd backend
python run_server.py
```

3. **Start frontend:**
```bash
cd frontend
npm start
```

Frontend opens at: **http://localhost:3000**

## Usage Flow

1. **Upload A-Roll Video**
   - Click "A-Roll Video" area
   - Select your video file (.mp4, .mov, etc.)

2. **Add B-Roll Metadata**
   - Enter B-roll ID: `broll_1`
   - Fill in fields (at minimum: title and description)
   - Click "Add B-Roll"
   - Repeat for all 6 B-rolls

3. **Configure Settings** (optional)
   - Similarity threshold: 0.72 (default)
   - Min insertions: 3 (default)
   - Max insertions: 6 (default)

4. **Generate Timeline**
   - Click "Generate Timeline" button
   - Wait for processing (10-40 seconds)

5. **View Results**
   - **Timeline JSON tab**: Full timeline structure
   - **Transcript tab**: A-roll transcript segments

## Example B-Roll Metadata

```
B-roll ID: broll_1
Title: Product Close-up
Description: Close-up shot of smartphone screen showing app interface
Category: product_demo
Subject: mobile application
```

## Troubleshooting

**"No response from server"**
- Make sure backend is running on port 8000
- Check `http://localhost:8000/health` in browser

**CORS errors**
- Backend should have CORS enabled (already configured)
- Check backend logs for errors

**File upload fails**
- Check file size (backend may have limits)
- Ensure video format is supported (.mp4, .mov, .avi, .mkv)

## API Integration Example

The frontend uses axios to call the backend:

```javascript
// services/api.js
import axios from 'axios';

const formData = new FormData();
formData.append('aroll_video', videoFile);
formData.append('broll_metadata', JSON.stringify(metadata));

const response = await axios.post('http://localhost:8000/generate', formData);
return response.data; // Timeline JSON
```

