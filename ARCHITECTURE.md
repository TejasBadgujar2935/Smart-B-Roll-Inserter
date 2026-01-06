# Smart B-Roll Inserter - Architecture Design

## System Overview

The Smart B-Roll Inserter analyzes an A-roll talking-head video and multiple B-roll clips to automatically generate a timeline plan indicating where each B-roll should be inserted.

## High-Level Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │  HTTP   │   Python     │  API    │   OpenAI    │
│  Frontend   │◄───────►│   Backend    │◄───────►│     API     │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              │ (optional)
                              ▼
                        ┌─────────────┐
                        │   FFmpeg    │
                        │  (Rendering)│
                        └─────────────┘
```

## Folder Structure

```
smart/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration management
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── video.py            # Video data models
│   │   │   ├── timeline.py         # Timeline plan models
│   │   │   └── request.py          # API request/response models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── video_processor.py  # Video analysis & processing
│   │   │   ├── ai_analyzer.py      # OpenAI API integration
│   │   │   ├── timeline_generator.py # Timeline plan generation
│   │   │   └── renderer.py         # Optional: FFmpeg rendering
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py           # API endpoints
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── file_handler.py     # File upload/download utilities
│   │       └── validators.py       # Input validation
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_video_processor.py
│   │   ├── test_ai_analyzer.py
│   │   └── test_timeline_generator.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoUploader/
│   │   │   │   ├── VideoUploader.jsx
│   │   │   │   └── VideoUploader.css
│   │   │   ├── TimelineViewer/
│   │   │   │   ├── TimelineViewer.jsx
│   │   │   │   └── TimelineViewer.css
│   │   │   └── RenderControls/
│   │   │       ├── RenderControls.jsx
│   │   │       └── RenderControls.css
│   │   ├── services/
│   │   │   └── api.js              # API client
│   │   ├── utils/
│   │   │   └── constants.js        # Constants & config
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── public/
│
├── uploads/                         # Temporary video storage
├── outputs/                         # Generated timeline plans & rendered videos
├── .gitignore
└── README.md
```

## Backend Architecture Details

### Core Components

#### 1. **main.py** (FastAPI Application)
**Responsibilities:**
- Initialize FastAPI application
- Configure CORS, middleware, and error handlers
- Register API routes
- Set up file upload handling
- Application lifecycle management

**Key Features:**
- FastAPI for async API handling
- File upload size limits
- Request/response logging
- Health check endpoint

---

#### 2. **config.py** (Configuration Management)
**Responsibilities:**
- Load environment variables (OpenAI API key, file paths, etc.)
- Application settings (max file size, allowed formats, etc.)
- Configuration validation
- Default values management

**Key Settings:**
- `OPENAI_API_KEY`
- `UPLOAD_DIR`
- `OUTPUT_DIR`
- `MAX_FILE_SIZE`
- `ALLOWED_VIDEO_FORMATS`

---

#### 3. **models/** (Data Models)

**video.py:**
- `VideoMetadata`: File info (path, duration, format, resolution)
- `VideoSegment`: Time range with metadata
- `ARollVideo`: A-roll specific model
- `BRollVideo`: B-roll specific model with tags/categories

**timeline.py:**
- `TimelinePlan`: Complete timeline structure
- `TimelineSegment`: Individual segment (A-roll or B-roll)
- `InsertionPoint`: Where B-roll should be inserted
- `TimelineMetadata`: Overall timeline info (total duration, etc.)

**request.py:**
- `UploadRequest`: File upload payload
- `GenerateTimelineRequest`: Timeline generation parameters
- `TimelineResponse`: API response model
- `ErrorResponse`: Error handling model

---

#### 4. **services/video_processor.py** (Video Analysis)
**Responsibilities:**
- Extract video metadata (duration, fps, resolution)
- Generate video thumbnails/previews
- Detect scene changes or silence gaps
- Extract audio for transcription
- Video format validation

**Key Methods:**
- `extract_metadata(video_path) -> VideoMetadata`
- `extract_audio(video_path) -> audio_path`
- `detect_silence_gaps(video_path) -> List[TimeRange]`
- `generate_thumbnail(video_path, timestamp) -> image_path`

**Dependencies:**
- `moviepy` or `opencv-python` for video processing
- `ffmpeg-python` for advanced operations

---

#### 5. **services/ai_analyzer.py** (OpenAI Integration)
**Responsibilities:**
- Transcribe A-roll video audio using Whisper API
- Analyze transcript to identify insertion opportunities
- Match B-roll clips to content topics
- Generate semantic descriptions of video segments

**Key Methods:**
- `transcribe_video(audio_path) -> Transcript`
- `analyze_content(transcript) -> ContentAnalysis`
- `suggest_insertions(transcript, b_rolls) -> List[InsertionPoint]`
- `match_broll_to_content(b_roll, content_segment) -> float` (similarity score)

**OpenAI APIs Used:**
- Whisper API: Audio transcription
- GPT-4: Content analysis and insertion point suggestions
- Embeddings API: B-roll matching (optional)

**Prompt Strategy:**
- Analyze transcript for natural pause points
- Identify topics that match available B-roll
- Suggest optimal insertion timings
- Consider pacing and narrative flow

---

#### 6. **services/timeline_generator.py** (Timeline Logic)
**Responsibilities:**
- Combine AI analysis with video processing data
- Generate structured timeline plan
- Optimize B-roll placement
- Handle edge cases (overlapping, gaps, etc.)
- Validate timeline consistency

**Key Methods:**
- `generate_timeline(a_roll, b_rolls, analysis) -> TimelinePlan`
- `optimize_placements(timeline) -> TimelinePlan`
- `validate_timeline(timeline) -> bool`
- `export_timeline(timeline, format) -> JSON/XML`

**Logic Flow:**
1. Receive AI-suggested insertion points
2. Validate against video metadata
3. Resolve conflicts (overlapping suggestions)
4. Generate final timeline structure
5. Export as JSON

---

#### 7. **services/renderer.py** (Optional FFmpeg Rendering)
**Responsibilities:**
- Render final video from timeline plan
- Apply transitions between clips
- Handle audio mixing
- Export in various formats

**Key Methods:**
- `render_video(timeline_plan) -> video_path`
- `apply_transitions(video_segments) -> video_path`
- `mix_audio(a_roll_audio, b_roll_audio) -> audio_path`

**Dependencies:**
- `ffmpeg-python` for video rendering

---

#### 8. **api/routes.py** (API Endpoints)
**Responsibilities:**
- Define REST API endpoints
- Handle HTTP requests/responses
- Request validation
- Error handling

**Endpoints:**
- `POST /api/upload` - Upload A-roll or B-roll videos
- `POST /api/generate-timeline` - Generate timeline plan
- `GET /api/timeline/{timeline_id}` - Retrieve timeline
- `POST /api/render` - Render video from timeline (optional)
- `GET /api/health` - Health check

**Request Flow:**
1. Upload videos → Store in `uploads/`
2. Generate timeline → Process → Return JSON
3. Optional render → Queue job → Return status

---

#### 9. **utils/file_handler.py** (File Management)
**Responsibilities:**
- Handle file uploads securely
- Validate file types and sizes
- Generate unique file names
- Clean up temporary files
- Manage storage paths

**Key Methods:**
- `save_upload(file, file_type) -> file_path`
- `validate_video(file_path) -> bool`
- `cleanup_temp_files(file_paths) -> None`

---

#### 10. **utils/validators.py** (Input Validation)
**Responsibilities:**
- Validate video file formats
- Check file sizes
- Validate timeline data structures
- Sanitize user inputs

---

## Frontend Architecture (Brief)

### Components

**VideoUploader:**
- Drag-and-drop interface
- Progress indicators
- File type validation
- Separate sections for A-roll and B-roll

**TimelineViewer:**
- Visual timeline representation
- Interactive timeline scrubbing
- B-roll insertion markers
- Preview controls

**RenderControls:**
- Trigger video rendering
- Monitor render progress
- Download rendered video

### API Client (services/api.js)
- Axios-based HTTP client
- Request/response interceptors
- Error handling
- Upload progress tracking

---

## Data Flow

```
1. User uploads A-roll + B-rolls
   ↓
2. Backend stores files & extracts metadata
   ↓
3. Video processor extracts audio from A-roll
   ↓
4. AI analyzer transcribes & analyzes content
   ↓
5. AI analyzer suggests insertion points
   ↓
6. Timeline generator creates structured plan
   ↓
7. Backend returns JSON timeline to frontend
   ↓
8. (Optional) User triggers rendering
   ↓
9. Renderer processes timeline & outputs video
```

---

## Technology Stack

### Backend
- **Framework:** FastAPI (async, auto-docs, type hints)
- **Video Processing:** moviepy, opencv-python, ffmpeg-python
- **AI Integration:** openai (Python SDK)
- **File Handling:** python-multipart
- **Validation:** Pydantic models

### Frontend
- **Framework:** React
- **HTTP Client:** Axios
- **UI Components:** Custom or Material-UI
- **Video Preview:** HTML5 video or video.js

---

## Production Considerations

### Security
- File upload validation (type, size, content)
- Rate limiting on API endpoints
- API key management (environment variables)
- Input sanitization

### Performance
- Async processing for long operations
- Background job queue (Celery) for rendering
- File cleanup after processing
- Caching for repeated analyses

### Scalability
- Stateless API design
- External storage for large files (S3, etc.)
- Database for timeline persistence (optional)
- Horizontal scaling capability

### Error Handling
- Comprehensive error responses
- Logging (structured logs)
- Graceful degradation
- User-friendly error messages

---

## Environment Variables

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Paths
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs

# Limits
MAX_FILE_SIZE_MB=500
MAX_BROLL_COUNT=20

# Optional
ENABLE_RENDERING=true
FFMPEG_PATH=/usr/bin/ffmpeg
```

---

## Timeline JSON Structure (Example)

```json
{
  "timeline_id": "uuid",
  "total_duration": 120.5,
  "segments": [
    {
      "type": "a_roll",
      "start_time": 0.0,
      "end_time": 15.3,
      "source": "a_roll_video.mp4"
    },
    {
      "type": "b_roll",
      "start_time": 15.3,
      "end_time": 18.7,
      "source": "b_roll_1.mp4",
      "transition": "fade",
      "reason": "Topic: Product demonstration"
    },
    {
      "type": "a_roll",
      "start_time": 18.7,
      "end_time": 35.2,
      "source": "a_roll_video.mp4"
    }
  ],
  "metadata": {
    "created_at": "2024-01-01T00:00:00Z",
    "a_roll_duration": 120.5,
    "b_roll_count": 5
  }
}
```

---

## Next Steps

1. Set up project structure
2. Implement core models
3. Build video processor
4. Integrate OpenAI API
5. Create timeline generator
6. Build API endpoints
7. Develop React frontend
8. Add optional rendering
9. Testing & optimization

