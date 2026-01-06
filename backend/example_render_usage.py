"""
Example usage of Video Rendering Module

Demonstrates rendering a video from timeline JSON.
"""

import json
from app.services.render import VideoRenderer

# Example timeline (from timeline.py output)
timeline = {
    "timeline_id": "example-timeline",
    "segments": [
        {
            "type": "a_roll",
            "start_time": 0.0,
            "end_time": 27.3,
            "duration": 27.3,
            "source": "a_roll_video"
        },
        {
            "type": "b_roll",
            "start_time": 27.3,
            "end_time": 31.0,
            "duration": 3.7,
            "source": "broll_1"
        },
        {
            "type": "b_roll",
            "start_time": 31.0,
            "end_time": 35.6,
            "duration": 4.6,
            "source": "broll_1"
        },
        {
            "type": "b_roll",
            "start_time": 35.6,
            "end_time": 40.2,
            "duration": 4.6,
            "source": "broll_4"
        }
    ]
}

# Map B-roll IDs to actual video file paths
broll_paths = {
    "broll_1": "brolls/broll_1.mp4",
    "broll_2": "brolls/broll_2.mp4",
    "broll_3": "brolls/broll_3.mp4",
    "broll_4": "brolls/broll_4.mp4",
    "broll_5": "brolls/broll_5.mp4",
    "broll_6": "brolls/broll_6.mp4"
}

if __name__ == "__main__":
    print("=" * 70)
    print("VIDEO RENDERING EXAMPLE")
    print("=" * 70)
    print()
    
    try:
        # Initialize renderer
        renderer = VideoRenderer()
        print(f"✓ FFmpeg found: {renderer.ffmpeg_path}")
        print()
        
        # Get example FFmpeg command
        print("Example FFmpeg command:")
        print("-" * 70)
        cmd_string = renderer.get_ffmpeg_command_string(
            timeline,
            "a_roll_video.mp4",
            broll_paths,
            "rendered_output.mp4"
        )
        print(cmd_string)
        print()
        
        # Note: Actual rendering requires real video files
        print("Note: To actually render, provide valid video file paths:")
        print("  renderer.render(")
        print("      timeline,")
        print("      aroll_video_path='path/to/a_roll_video.mp4',")
        print("      broll_paths=broll_paths,")
        print("      output_path='rendered_output.mp4'")
        print("  )")
        
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("   Make sure ffmpeg is installed and in PATH")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

