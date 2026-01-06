"""
Video Rendering Module

Renders final video from timeline plan using ffmpeg.
A-roll audio remains intact, B-roll visuals overlay at planned timestamps.
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class VideoRenderer:
    """Renders video from timeline plan using ffmpeg."""
    
    def __init__(self, ffmpeg_path: str = None):
        """
        Initialize the video renderer.
        
        Args:
            ffmpeg_path: Path to ffmpeg executable. If None, uses 'ffmpeg' from PATH.
        """
        self.ffmpeg_path = ffmpeg_path or self._find_ffmpeg()
        if not self.ffmpeg_path:
            raise ValueError("ffmpeg not found. Please install ffmpeg and ensure it's in PATH.")
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Find ffmpeg executable."""
        # Check environment variable first
        ffmpeg_env = os.getenv("FFMPEG_PATH")
        if ffmpeg_env and os.path.exists(ffmpeg_env):
            return ffmpeg_env
        
        # Try common paths
        common_paths = [
            "ffmpeg",
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"
        ]
        
        for path in common_paths:
            try:
                result = subprocess.run(
                    [path, "-version"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            except:
                continue
        
        return None
    
    def _validate_video_file(self, video_path: str) -> bool:
        """Validate that video file exists and is readable."""
        if not os.path.exists(video_path):
            return False
        
        # Quick check with ffprobe
        try:
            ffprobe_path = self.ffmpeg_path.replace("ffmpeg", "ffprobe")
            result = subprocess.run(
                [ffprobe_path, "-v", "error", video_path],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            # If ffprobe fails, assume file is valid
            return True
    
    def _build_overlay_filters(
        self,
        timeline_segments: List[Dict[str, Any]],
        broll_input_map: Dict[str, int]
    ) -> Tuple[str, List[str]]:
        """
        Build ffmpeg overlay filter complex for B-roll insertions.
        
        Args:
            timeline_segments: List of timeline segments
            broll_input_map: Dictionary mapping broll_id to ffmpeg input index
            
        Returns:
            Tuple of (final_video_label, overlay_filters)
        """
        base_input = "[0:v]"  # A-roll video
        overlay_filters = []
        current_overlay = base_input
        
        # Track output label index
        output_index = 1
        
        for segment in timeline_segments:
            if segment["type"] == "b_roll":
                broll_id = segment["source"]
                start_time = segment["start_time"]
                duration = segment["duration"]
                
                if broll_id not in broll_input_map:
                    print(f"Warning: B-roll {broll_id} not found in input map, skipping...")
                    continue
                
                # Get the input index for this B-roll
                input_index = broll_input_map[broll_id]
                
                # Build overlay filter
                # Format: [previous][input_index:v]overlay=x:y:enable='between(t,start,end)'[output]
                # We'll use fullscreen overlay (x=0:y=0)
                output_label = f"[v{output_index}]"
                
                # Enable overlay only during the specified time range
                enable_expr = f"between(t,{start_time},{start_time + duration})"
                
                overlay_filter = (
                    f"{current_overlay}[{input_index}:v]overlay=0:0:"
                    f"enable='{enable_expr}'{output_label}"
                )
                
                overlay_filters.append(overlay_filter)
                current_overlay = output_label
                output_index += 1
        
        return current_overlay, overlay_filters
    
    def _build_ffmpeg_command(
        self,
        aroll_video_path: str,
        broll_paths: Dict[str, str],
        timeline_segments: List[Dict[str, Any]],
        output_path: str
    ) -> List[str]:
        """
        Build complete ffmpeg command for rendering.
        
        Args:
            aroll_video_path: Path to A-roll video
            broll_paths: Dictionary mapping broll_id to video file path
            timeline_segments: List of timeline segments
            output_path: Output video path
            
        Returns:
            List of command arguments
        """
        # Start building command
        cmd = [self.ffmpeg_path]
        
        # Input files
        # A-roll video (input 0)
        cmd.extend(["-i", aroll_video_path])
        
        # B-roll videos (inputs 1, 2, 3, ...)
        broll_segments = [s for s in timeline_segments if s["type"] == "b_roll"]
        used_brolls = set()
        broll_inputs = []
        
        for segment in broll_segments:
            broll_id = segment["source"]
            if broll_id in broll_paths and broll_id not in used_brolls:
                cmd.extend(["-i", broll_paths[broll_id]])
                broll_inputs.append(broll_id)
                used_brolls.add(broll_id)
        
        # Build B-roll input index map
        # Input 0 = A-roll, Input 1+ = B-rolls
        broll_input_map = {}
        input_index = 1
        for broll_id in broll_inputs:
            broll_input_map[broll_id] = input_index
            input_index += 1
        
        # Build overlay filter complex
        final_video_label, overlay_filters = self._build_overlay_filters(
            timeline_segments,
            broll_input_map
        )
        
        # If no overlays, just copy video
        if not overlay_filters:
            # Simple copy: use A-roll video as-is
            cmd.extend([
                "-c:v", "libx264",
                "-c:a", "copy",  # Copy audio without re-encoding
                "-map", "0:v:0",  # Map A-roll video
                "-map", "0:a:0",  # Map A-roll audio
                "-y",  # Overwrite output
                output_path
            ])
            return cmd
        
        # Build filter complex
        # Format: -filter_complex "[0:v][1:v]overlay=0:0:enable='...'[v1];[v1][2:v]overlay=0:0:enable='...'[v2]"
        filter_complex = ";".join(overlay_filters)
        
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", final_video_label.replace("[", "").replace("]", ""),  # Remove brackets
            "-map", "0:a:0",  # Map A-roll audio
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "copy",  # Copy audio without re-encoding
            "-y",  # Overwrite output
            output_path
        ])
        
        return cmd
    
    def render(
        self,
        timeline: Dict[str, Any],
        aroll_video_path: str,
        broll_paths: Dict[str, str],
        output_path: str = None
    ) -> str:
        """
        Render video from timeline plan.
        
        Args:
            timeline: Timeline JSON dictionary
            aroll_video_path: Path to A-roll video file
            broll_paths: Dictionary mapping broll_id to video file path
            output_path: Output video path (optional, auto-generated if None)
            
        Returns:
            Path to rendered video file
        """
        # Validate inputs
        if not os.path.exists(aroll_video_path):
            raise FileNotFoundError(f"A-roll video not found: {aroll_video_path}")
        
        if not self._validate_video_file(aroll_video_path):
            raise ValueError(f"Invalid A-roll video file: {aroll_video_path}")
        
        # Validate B-roll paths
        timeline_segments = timeline.get("segments", [])
        broll_segments = [s for s in timeline_segments if s["type"] == "b_roll"]
        
        for segment in broll_segments:
            broll_id = segment["source"]
            if broll_id not in broll_paths:
                raise ValueError(f"B-roll path not provided for {broll_id}")
            if not os.path.exists(broll_paths[broll_id]):
                raise FileNotFoundError(f"B-roll video not found: {broll_paths[broll_id]}")
        
        # Generate output path if not provided
        if output_path is None:
            aroll_file = Path(aroll_video_path)
            output_path = str(aroll_file.parent / f"{aroll_file.stem}_rendered.mp4")
        
        # Build ffmpeg command
        cmd = self._build_ffmpeg_command(
            aroll_video_path,
            broll_paths,
            timeline_segments,
            output_path
        )
        
        # Execute ffmpeg
        print(f"Rendering video with ffmpeg...")
        print(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ Video rendered successfully: {output_path}")
            return output_path
        
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg error: {e.stderr}"
            print(f"✗ {error_msg}")
            raise RuntimeError(error_msg)
    
    def render_from_files(
        self,
        timeline_path: str,
        aroll_video_path: str,
        broll_paths: Dict[str, str],
        output_path: str = None
    ) -> str:
        """
        Render video from timeline JSON file.
        
        Args:
            timeline_path: Path to timeline JSON file
            aroll_video_path: Path to A-roll video file
            broll_paths: Dictionary mapping broll_id to video file path
            output_path: Output video path (optional)
            
        Returns:
            Path to rendered video file
        """
        with open(timeline_path, 'r', encoding='utf-8') as f:
            timeline = json.load(f)
        
        return self.render(timeline, aroll_video_path, broll_paths, output_path)
    
    def get_ffmpeg_command_string(
        self,
        timeline: Dict[str, Any],
        aroll_video_path: str,
        broll_paths: Dict[str, str],
        output_path: str
    ) -> str:
        """
        Get the ffmpeg command as a string (for debugging/example).
        
        Args:
            timeline: Timeline JSON dictionary
            aroll_video_path: Path to A-roll video file
            broll_paths: Dictionary mapping broll_id to video file path
            output_path: Output video path
            
        Returns:
            FFmpeg command as string
        """
        timeline_segments = timeline.get("segments", [])
        broll_segments = [s for s in timeline_segments if s["type"] == "b_roll"]
        used_brolls = set()
        broll_inputs = []
        
        for segment in broll_segments:
            broll_id = segment["source"]
            if broll_id in broll_paths and broll_id not in used_brolls:
                broll_inputs.append(broll_id)
                used_brolls.add(broll_id)
        
        cmd = self._build_ffmpeg_command(
            aroll_video_path,
            broll_paths,
            timeline_segments,
            output_path
        )
        
        # Escape spaces in paths for shell
        escaped_cmd = []
        for arg in cmd:
            if " " in arg and not arg.startswith("-"):
                escaped_cmd.append(f'"{arg}"')
            else:
                escaped_cmd.append(arg)
        
        return " ".join(escaped_cmd)


def main():
    """Example usage of the video renderer."""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python render.py <timeline.json> <a_roll_video.mp4> <output.mp4>")
        print("       broll_paths should be provided as JSON: {'broll_1': 'path/to/broll1.mp4', ...}")
        sys.exit(1)
    
    timeline_path = sys.argv[1]
    aroll_path = sys.argv[2]
    output_path = sys.argv[3]
    
    # Example B-roll paths (in real usage, these would come from user input)
    broll_paths = {
        "broll_1": "brolls/broll_1.mp4",
        "broll_2": "brolls/broll_2.mp4",
        "broll_3": "brolls/broll_3.mp4",
        "broll_4": "brolls/broll_4.mp4",
        "broll_5": "brolls/broll_5.mp4",
        "broll_6": "brolls/broll_6.mp4"
    }
    
    try:
        renderer = VideoRenderer()
        
        # Get command string for example
        with open(timeline_path, 'r') as f:
            timeline = json.load(f)
        
        cmd_string = renderer.get_ffmpeg_command_string(
            timeline,
            aroll_path,
            broll_paths,
            output_path
        )
        print("Example FFmpeg command:")
        print(cmd_string)
        print()
        
        # Render video
        result_path = renderer.render_from_files(
            timeline_path,
            aroll_path,
            broll_paths,
            output_path
        )
        
        print(f"✓ Rendered video: {result_path}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

