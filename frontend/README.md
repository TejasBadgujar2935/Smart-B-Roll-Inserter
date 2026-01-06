# Smart B-Roll Inserter - React Frontend

Minimal React frontend for the Smart B-Roll Inserter system.

## Features

- Upload A-roll video
- Add B-roll metadata
- Configure matching settings
- Generate timeline plan
- Display transcript and timeline JSON

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL

Create a `.env` file in the `frontend` directory (optional):

```env
REACT_APP_API_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`.

### 3. Start Development Server

```bash
npm start
```

The app will open at `http://localhost:3000`.

## Usage

1. **Upload A-Roll Video**: Click to select your A-roll video file
2. **Add B-Roll Metadata**: 
   - Enter B-roll ID (e.g., `broll_1`)
   - Fill in metadata fields (title, description, category, etc.)
   - Click "Add B-Roll"
   - Repeat for all B-rolls
3. **Configure Settings** (optional):
   - Similarity threshold (default: 0.72)
   - Min/Max insertions (default: 3-6)
4. **Generate Timeline**: Click the "Generate Timeline" button
5. **View Results**: 
   - See timeline JSON
   - View transcript segments

## Component Structure

```
src/
├── App.js                 # Main application component
├── App.css               # Main styles
├── components/
│   ├── VideoUploader.js  # File upload component
│   ├── BRollMetadataInput.js  # B-roll metadata form
│   ├── GenerateButton.js     # Generate button
│   └── ResultsDisplay.js      # Results display with tabs
├── services/
│   └── api.js            # API integration
└── index.js              # Entry point
```

## API Integration

The frontend calls the `/generate` endpoint:

```javascript
import { generateTimeline } from './services/api';

const timeline = await generateTimeline(
  arollVideo,        // File object
  brollMetadata,     // { broll_1: {...}, broll_2: {...} }
  similarityThreshold,
  minInsertions,
  maxInsertions
);
```

## B-Roll Metadata Format

```javascript
{
  "broll_1": {
    "title": "Product Demo",
    "description": "Close-up of smartphone",
    "category": "product_demo",
    "subject": "mobile application",
    "action": "demonstrating",
    "location": "studio",
    "mood": "professional"
  },
  "broll_2": {
    "title": "Office Scene",
    "description": "People working",
    "category": "environment",
    "location": "office"
  }
}
```

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Notes

- Simple, minimal UI - no fancy styling
- Focus on functionality over aesthetics
- Error handling for API failures
- Loading states during processing
- Results displayed in tabs (Timeline JSON / Transcript)

