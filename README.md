# Smart B-Roll Inserter

An AI-powered system that automatically generates timeline plans for inserting B-roll clips into A-roll talking-head videos. The system uses semantic matching to identify optimal insertion points where B-roll visuals complement the spoken content.

## Problem Overview

Video editors spend significant time manually identifying where to insert B-roll clips in talking-head videos. This process requires:
- Watching the entire A-roll video
- Understanding the content context
- Matching B-roll clips to relevant moments
- Creating a timeline plan

**Our Solution**: Automate this process by:
1. Transcribing A-roll audio to extract content and timestamps
2. Converting B-roll metadata into semantic descriptions
3. Using AI embeddings to find semantic matches
4. Generating a structured timeline JSON with insertion points

## System Architecture


┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │  HTTP   │   Python     │  API    │   OpenAI    │
│  Frontend   │◄───────►│   Backend    │◄───────►│     API     │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              │ (optional)
                              ▼
                        ┌─────────────┐
                        │   FFmpeg    │
                        │  (Rendering) │
                        └─────────────┘


### Components

**Backend (Python/FastAPI)**
- `transcribe.py`: A-roll transcription using OpenAI Whisper API
- `broll_analysis.py`: Converts B-roll metadata to text descriptions
- `matcher.py`: Semantic matching using OpenAI embeddings
- `timeline.py`: Combines segments into structured timeline JSON
- `render.py`: Optional video rendering with FFmpeg
- `main.py`: FastAPI server with `/generate` endpoint

**Frontend (React)**
- Video upload interface
- B-roll metadata input form
- Results display (transcript + timeline JSON)

### Data Flow


1. User uploads A-roll video + B-roll metadata
   ↓
2. Backend transcribes A-roll (Whisper API)
   → Returns: [{"start_time": 0.0, "end_time": 3.5, "text": "..."}, ...]
   ↓
3. Backend analyzes B-roll metadata
   → Returns: {"broll_1": "Product Close-up shows mobile application...", ...}
   ↓
4. Backend generates embeddings (OpenAI)
   → Creates similarity matrix (n_segments × n_brolls)
   ↓
5. Backend matches segments (cosine similarity + constraints)
   → Returns: [{"start_sec": 27.3, "broll_id": "broll_1", "confidence": 0.856}, ...]
   ↓
6. Backend generates timeline JSON
   → Returns: Complete timeline with segments, statistics, debug info
   ↓
7. Frontend displays results


## Matching Logic

### Core Algorithm

The matching system uses **semantic similarity** to find relevant B-roll insertion points:

1. **Embedding Generation**
   - A-roll transcript segments → OpenAI embeddings
   - B-roll descriptions → OpenAI embeddings
   - Model: `text-embedding-3-small` (fast, cost-effective)

2. **Similarity Calculation**
   - Cosine similarity between all pairs
   - Creates matrix: `similarity[segment_i][broll_j]`
   - Range: 0.0 (no similarity) to 1.0 (identical meaning)

3. **Threshold Filtering**
   - Only matches above 0.72 similarity are considered
   - Prevents low-quality insertions

4. **Constraint-Based Selection**
   - **Temporal spacing**: Minimum 5 seconds between insertions
   - **Variety**: Max 2 uses per B-roll
   - **Quality ranking**: Selects highest similarity matches first
   - **Limits**: 3-6 insertions per video (configurable)

### Example Matching


A-roll segment: "Let's take a look at the product demonstration"
    ↓
B-roll descriptions:
  - broll_1: "Product Close-up shows mobile application..." → 0.856 ✓
  - broll_2: "Office Environment at office..." → 0.45 ✗
  - broll_3: "Hand Typing shows typing..." → 0.32 ✗
    ↓
Result: Insert broll_1 at 27.3s with confidence 0.856


### Why These Thresholds?

**Similarity Threshold: 0.72**
- Too low (< 0.65): Allows weak matches, random insertions
- Too high (> 0.80): Too restrictive, misses good matches
- 0.72: Balanced - ensures relevance while maintaining flexibility
- Empirically tuned for this use case

**Minimum Gap: 5 seconds**
- Prevents visual overload
- Natural pacing for viewer comprehension
- Relaxed to 3 seconds if needed to meet minimum insertions

**Insertion Limits: 3-6**
- Minimum 3: Ensures engaging content
- Maximum 6: Prevents over-editing
- Optimal for typical 2-5 minute videos

## Trade-offs and Assumptions

### Assumptions

1. **B-roll metadata is available**: We assume users can provide metadata describing B-roll content. This is reasonable for production workflows where clips are cataloged.

2. **A-roll audio is clear**: Whisper API works best with clear speech. Background noise or poor audio quality may affect transcription accuracy.

3. **Semantic matching is sufficient**: We prioritize semantic relevance over visual aesthetics. The system doesn't analyze actual video frames, only text descriptions.

4. **Fixed number of B-rolls**: Currently optimized for exactly 6 B-roll clips. The system works with any number, but constraints are tuned for this scenario.

### Trade-offs

**Accuracy vs. Speed**
- **Chosen**: OpenAI API for transcription and embeddings (fast, accurate)
- **Not chosen**: Local models (slower, less accurate, but more private)

**Metadata vs. Vision Analysis**
- **Chosen**: Metadata-based descriptions (fast, no video processing)
- **Not chosen**: Computer vision analysis (more accurate, but slower and more complex)

**Simplicity vs. Features**
- **Chosen**: Focus on correctness over visual polish
- **Not chosen**: Transitions, effects, picture-in-picture (can be added later)

**Quality vs. Quantity**
- **Chosen**: Threshold-based filtering (fewer, higher-quality matches)
- **Not chosen**: Insert at every opportunity (more matches, lower quality)

### Limitations

1. **No visual analysis**: System doesn't analyze actual video frames, only text
2. **No audio mixing**: B-roll audio is not considered (A-roll audio always used)
3. **Fixed overlay style**: B-rolls overlay fullscreen (no picture-in-picture)
4. **No transitions**: Abrupt cuts between A-roll and B-roll
5. **API dependency**: Requires OpenAI API key and internet connection

### Future Improvements

- Visual similarity analysis using video embeddings
- Automatic B-roll metadata extraction from video
- Configurable overlay positions and transitions
- Local model options for privacy
- Batch processing for multiple videos

## Setup Instructions

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm
- **FFmpeg** (optional, for video rendering)
- **OpenAI API key**

### Backend Setup

1. **Install dependencies:**
bash
cd backend
pip install -r requirements.txt


2. **Set environment variables:**
bash
export OPENAI_API_KEY="sk-your-api-key-here"
export PORT=8000  # Optional, defaults to 8000


Or create `.env` file:
env
OPENAI_API_KEY=sk-your-api-key-here
PORT=8000


3. **Verify FFmpeg (optional):**
bash
ffmpeg -version


### Frontend Setup

1. **Install dependencies:**
bash
cd frontend
npm install


2. **Configure API URL (optional):**
Create frontend/.env:
env
REACT_APP_API_URL=http://localhost:8000


## How to Run

### Development Mode

**Terminal 1 - Backend:**
bash
cd backend
python run_server.py

Backend runs at: `http://localhost:8000`

**Terminal 2 - Frontend:**
bash
cd frontend
npm start

Frontend opens at: `http://localhost:3000`

### Production Mode

**Backend:**
   bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000


**Frontend:**
```bash
cd frontend
npm run build
# Serve the build/ directory with a static file server


## Usage

1. **Upload A-roll video** via frontend
2. **Add B-roll metadata** (at minimum: title and description)
3. **Configure settings** (similarity threshold, min/max insertions)
4. **Click "Generate Timeline"**
5. **View results**: Timeline JSON and transcript

### Example B-roll Metadata

   json
{
  "broll_1": {
    "title": "Product Close-up",
    "description": "Close-up shot of smartphone screen showing app interface",
    "category": "product_demo",
    "subject": "mobile application"
  },
  "broll_2": {
    "title": "Office Environment",
    "description": "Wide shot of modern office workspace",
    "category": "environment",
    "location": "office"
  }
}


## API Endpoints

### `POST /generate`
Generate timeline plan from A-roll video and B-roll metadata.

**Request:**
- `aroll_video` (file): A-roll video file
- `broll_metadata` (form field, JSON string): B-roll metadata dictionary
- `similarity_threshold` (optional, default: 0.72)
- `min_insertions` (optional, default: 3)
- `max_insertions` (optional, default: 6)

**Response:**
```json
{
  "timeline_id": "uuid",
  "total_duration": 120.5,
  "segments": [
    {
      "type": "a_roll",
      "start_time": 0.0,
      "end_time": 27.3,
      "transcript": "..."
    },
    {
      "type": "b_roll",
      "start_time": 27.3,
      "end_time": 31.0,
      "source": "broll_1",
      "confidence": 0.856,
      "insertion_reason": "Highly relevant match: both mention 'product'"
    }
  ],
  "statistics": {...},
  "debug_info": {...}
}
```

### `GET /health`
Health check endpoint.

### `GET /docs`
Interactive API documentation (Swagger UI).

## Project Structure

```
smart/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI server
│   │   └── services/
│   │       ├── transcribe.py    # A-roll transcription
│   │       ├── broll_analysis.py # B-roll metadata analysis
│   │       ├── matcher.py        # Semantic matching
│   │       ├── timeline.py      # Timeline generation
│   │       └── render.py        # Video rendering (optional)
│   ├── requirements.txt
│   └── run_server.py
├── frontend/
│   ├── src/
│   │   ├── App.js               # Main component
│   │   ├── components/          # React components
│   │   └── services/
│   │       └── api.js           # API client
│   └── package.json
└── README.md
```

## Testing

**Backend API test:**
```bash
cd backend
python test_api.py path/to/video.mp4
```

**Manual testing:**
1. Start backend and frontend
2. Upload test video
3. Add B-roll metadata
4. Generate timeline
5. Verify results in frontend

## Performance

- **A-roll transcription**: ~10-30 seconds (depends on video length)
- **B-roll analysis**: Instant (metadata-based)
- **Semantic matching**: ~2-5 seconds (embedding generation)
- **Timeline generation**: Instant
- **Total**: ~15-40 seconds for typical 2-5 minute video

## Cost Considerations

- **Whisper API**: ~$0.006 per minute of audio
- **Embeddings API**: ~$0.00002 per 1K tokens
- **Typical video (5 min)**: ~$0.03-0.05 per generation

## License

This project is provided as-is for demonstration purposes.

## Acknowledgments

- OpenAI for Whisper and Embeddings APIs
- FastAPI for the web framework
- React for the frontend framework
- FFmpeg for video processing

