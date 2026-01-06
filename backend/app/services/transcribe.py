"""
A-roll Understanding Module

Transcribes video audio using OpenAI Whisper API and returns
sentence-level timestamped segments.
"""

import os
import json
from typing import List, Dict, Any
from pathlib import Path
import openai
from moviepy.editor import VideoFileClip


class ArollTranscriber:
    """Handles transcription of A-roll videos using OpenAI Whisper API."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the transcriber.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def extract_audio(self, video_path: str, output_audio_path: str = None) -> str:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to the input video file
            output_audio_path: Optional path for output audio file
            
        Returns:
            Path to the extracted audio file
        """
        if output_audio_path is None:
            video_file = Path(video_path)
            output_audio_path = str(video_file.parent / f"{video_file.stem}_audio.mp3")
        
        # Extract audio using moviepy
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(output_audio_path, verbose=False, logger=None)
        audio.close()
        video.close()
        
        return output_audio_path
    
    def transcribe_with_timestamps(
        self, 
        audio_path: str,
        response_format: str = "verbose_json"
    ) -> Dict[str, Any]:
        """
        Transcribe audio using OpenAI Whisper API with timestamps.
        
        Args:
            audio_path: Path to the audio file
            response_format: Response format (verbose_json for word-level timestamps)
            
        Returns:
            Raw Whisper API response with transcription and timestamps
        """
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format=response_format,
                timestamp_granularities=["segment", "word"]
            )
        
        return transcript
    
    def process_segments(self, transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process Whisper response into clean sentence-level segments.
        
        Args:
            transcript_data: Raw Whisper API response
            
        Returns:
            List of segments with start_time, end_time, and text
        """
        segments = []
        
        # Handle both dict and object responses
        if isinstance(transcript_data, dict):
            segments_data = transcript_data.get("segments", [])
        else:
            segments_data = getattr(transcript_data, "segments", [])
        
        for segment in segments_data:
            # Extract segment data
            if isinstance(segment, dict):
                start = segment.get("start", 0.0)
                end = segment.get("end", 0.0)
                text = segment.get("text", "").strip()
            else:
                start = getattr(segment, "start", 0.0)
                end = getattr(segment, "end", 0.0)
                text = getattr(segment, "text", "").strip()
            
            # Only include non-empty segments
            if text:
                segments.append({
                    "start_time": round(start, 2),
                    "end_time": round(end, 2),
                    "text": text
                })
        
        return segments
    
    def transcribe_video(
        self, 
        video_path: str,
        keep_audio_file: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Main method: Transcribe A-roll video and return timestamped segments.
        
        Args:
            video_path: Path to the A-roll video file (.mp4)
            keep_audio_file: Whether to keep the extracted audio file
            
        Returns:
            List of transcript segments with start_time, end_time, and text
        """
        # Validate video file exists
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Extract audio from video
        audio_path = self.extract_audio(video_path)
        
        try:
            # Transcribe with Whisper API
            transcript_data = self.transcribe_with_timestamps(audio_path)
            
            # Process into clean segments
            segments = self.process_segments(transcript_data)
            
            return segments
        
        finally:
            # Clean up audio file if requested
            if not keep_audio_file and os.path.exists(audio_path):
                os.remove(audio_path)
    
    def transcribe_to_json(
        self,
        video_path: str,
        output_json_path: str = None,
        keep_audio_file: bool = False
    ) -> str:
        """
        Transcribe video and save results to JSON file.
        
        Args:
            video_path: Path to the A-roll video file
            output_json_path: Optional path for output JSON file
            keep_audio_file: Whether to keep the extracted audio file
            
        Returns:
            Path to the output JSON file
        """
        segments = self.transcribe_video(video_path, keep_audio_file)
        
        if output_json_path is None:
            video_file = Path(video_path)
            output_json_path = str(video_file.parent / f"{video_file.stem}_transcript.json")
        
        output_data = {
            "video_path": video_path,
            "segments": segments,
            "total_segments": len(segments),
            "total_duration": segments[-1]["end_time"] if segments else 0.0
        }
        
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return output_json_path


def main():
    """Example usage of the transcriber."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    try:
        transcriber = ArollTranscriber()
        segments = transcriber.transcribe_video(video_path)
        
        # Print results
        print(f"\nTranscription complete! Found {len(segments)} segments.\n")
        for i, segment in enumerate(segments, 1):
            print(f"Segment {i}:")
            print(f"  Time: {segment['start_time']:.2f}s - {segment['end_time']:.2f}s")
            print(f"  Text: {segment['text']}\n")
        
        # Save to JSON
        json_path = transcriber.transcribe_to_json(video_path)
        print(f"Results saved to: {json_path}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

