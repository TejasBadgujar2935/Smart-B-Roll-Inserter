"""
FastAPI Backend for Smart B-Roll Inserter

Main API endpoint that orchestrates the complete pipeline:
1. Transcribe A-roll
2. Analyze B-rolls
3. Match segments
4. Generate timeline
"""
from dotenv import load_dotenv
from pathlib import Path


import os
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


print("your_api_key_here=", os.getenv("your_api_key_here"))

import tempfile

from typing import Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import uvicorn

from app.services.transcribe import ArollTranscriber
from app.services.broll_analysis import BRollAnalyzer
from app.services.matcher import SemanticMatcher
from app.services.timeline import TimelinePlanner


# Initialize FastAPI app
app = FastAPI(
    title="Smart B-Roll Inserter API",
    description="Automatically generates timeline plans for B-roll insertion",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class BRollMetadata(BaseModel):
    """B-roll metadata structure."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subject: Optional[str] = None
    action: Optional[str] = None
    location: Optional[str] = None
    objects: Optional[list] = None
    mood: Optional[str] = None
    tags: Optional[list] = None


class GenerateRequest(BaseModel):
    """Request model for /generate endpoint."""
    broll_metadata: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Dictionary mapping broll_id to metadata. Example: {'broll_1': {'title': 'Product Demo', 'description': '...'}}"
    )
    similarity_threshold: Optional[float] = Field(
        0.72,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold for matching (0.0-1.0)"
    )
    min_insertions: Optional[int] = Field(
        3,
        ge=0,
        le=20,
        description="Minimum number of B-roll insertions"
    )
    max_insertions: Optional[int] = Field(
        6,
        ge=1,
        le=20,
        description="Maximum number of B-roll insertions"
    )


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Smart B-Roll Inserter API",
        "version": "1.0.0",
        "endpoints": {
            "/generate": "POST - Generate timeline plan",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


@app.post("/generate")
async def generate_timeline(
    aroll_video: UploadFile = File(..., description="A-roll video file (.mp4)"),
    broll_metadata: str = Form(..., description="JSON string of B-roll metadata"),
    similarity_threshold: float = Form(0.72, description="Similarity threshold (0.0-1.0)"),
    min_insertions: int = Form(3, description="Minimum insertions"),
    max_insertions: int = Form(6, description="Maximum insertions")
):
    """
    Generate timeline plan for B-roll insertion.
    
    Pipeline:
    1. Transcribe A-roll video
    2. Analyze B-roll metadata
    3. Match A-roll segments with B-rolls
    4. Generate timeline JSON
    
    Returns:
        Complete timeline JSON with segments, statistics, and debug info
    """
    temp_dir = None
    temp_aroll_path = None
    
    try:
        # Validate OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            )
        
        # Validate video file
        if not aroll_video.filename.endswith(('.mp4', '.mov', '.avi', '.mkv')):
            raise HTTPException(
                status_code=400,
                detail="Invalid video format. Supported: .mp4, .mov, .avi, .mkv"
            )
        
        # Create temporary directory for file handling
        temp_dir = tempfile.mkdtemp()
        temp_aroll_path = os.path.join(temp_dir, aroll_video.filename)
        
        # Save uploaded A-roll video
        with open(temp_aroll_path, "wb") as f:
            content = await aroll_video.read()
            f.write(content)
        
        # Parse B-roll metadata
        try:
            broll_metadata_dict = json.loads(broll_metadata)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON in broll_metadata: {str(e)}"
            )
        
        # Validate B-roll metadata structure
        if not isinstance(broll_metadata_dict, dict):
            raise HTTPException(
                status_code=400,
                detail="broll_metadata must be a dictionary mapping broll_id to metadata"
            )
        
        # Step 1: Transcribe A-roll
        print("Step 1: Transcribing A-roll video...")
        transcriber = ArollTranscriber()
        aroll_segments = transcriber.transcribe_video(temp_aroll_path, keep_audio_file=False)
        print(f"✓ Transcribed {len(aroll_segments)} segments")
        
        # Step 2: Analyze B-rolls
        print("Step 2: Analyzing B-roll metadata...")
        analyzer = BRollAnalyzer()
        broll_descriptions = analyzer.analyze_brolls(broll_metadata_dict)
        print(f"✓ Analyzed {len(broll_descriptions)} B-rolls")
        
        # Step 3: Match segments
        print("Step 3: Matching A-roll segments with B-rolls...")
        matcher = SemanticMatcher(
            similarity_threshold=similarity_threshold,
            min_insertions=min_insertions,
            max_insertions=max_insertions
        )
        broll_matches = matcher.match(aroll_segments, broll_descriptions)
        print(f"✓ Found {len(broll_matches)} matches")
        
        # Step 4: Generate timeline
        print("Step 4: Generating timeline...")
        planner = TimelinePlanner(aroll_video_path=aroll_video.filename)
        timeline = planner.create_timeline(aroll_segments, broll_matches)
        print(f"✓ Timeline generated with {len(timeline['segments'])} segments")
        
        # Return timeline JSON
        return JSONResponse(content=timeline)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    
    finally:
        # Cleanup temporary files
        if temp_aroll_path and os.path.exists(temp_aroll_path):
            try:
                os.remove(temp_aroll_path)
            except:
                pass
        if temp_dir and os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except:
                pass




if __name__ == "__main__":
    # Run server locally
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

