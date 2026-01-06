"""
Simple test script for the FastAPI backend.

Usage:
    python test_api.py path/to/a_roll_video.mp4
"""

import sys
import json
import requests

# Example B-roll metadata
EXAMPLE_BROLL_METADATA = {
    "broll_1": {
        "title": "Product Close-up",
        "description": "Close-up shot of smartphone screen showing app interface",
        "category": "product_demo",
        "subject": "mobile application",
        "objects": ["smartphone", "screen", "app interface"],
        "mood": "professional"
    },
    "broll_2": {
        "title": "Office Environment",
        "description": "Wide shot of modern office workspace with people working",
        "category": "environment",
        "location": "office",
        "mood": "productive"
    },
    "broll_3": {
        "title": "Hand Typing",
        "action": "typing on keyboard",
        "description": "Close-up of hands typing on laptop keyboard",
        "category": "action",
        "mood": "focused"
    },
    "broll_4": {
        "title": "Data Visualization",
        "description": "Animated charts and graphs displaying analytics",
        "category": "graphics",
        "subject": "data analytics",
        "objects": ["charts", "graphs", "analytics dashboard"]
    },
    "broll_5": {
        "title": "Team Collaboration",
        "description": "People discussing around a whiteboard",
        "category": "teamwork",
        "action": "collaborating",
        "location": "meeting room",
        "mood": "collaborative"
    },
    "broll_6": {
        "title": "Code Editor",
        "description": "Screen recording of code being written in editor",
        "category": "technical",
        "subject": "programming",
        "action": "coding",
        "objects": ["code editor", "programming syntax"]
    }
}


def test_api(video_path: str, api_url: str = "http://localhost:8000"):
    """Test the /generate endpoint."""
    
    print("=" * 70)
    print("Testing Smart B-Roll Inserter API")
    print("=" * 70)
    print(f"\nAPI URL: {api_url}")
    print(f"Video: {video_path}")
    print(f"B-rolls: {len(EXAMPLE_BROLL_METADATA)}")
    print("\n" + "-" * 70)
    print("Sending request...\n")
    
    try:
        # Prepare request
        with open(video_path, "rb") as video_file:
            files = {"aroll_video": video_file}
            data = {
                "broll_metadata": json.dumps(EXAMPLE_BROLL_METADATA),
                "similarity_threshold": "0.72",
                "min_insertions": "3",
                "max_insertions": "6"
            }
            
            # Make request
            response = requests.post(
                f"{api_url}/generate",
                files=files,
                data=data,
                timeout=300  # 5 minute timeout for video processing
            )
        
        # Check response
        if response.status_code == 200:
            timeline = response.json()
            
            print("✓ Success!\n")
            print("=" * 70)
            print("TIMELINE SUMMARY")
            print("=" * 70)
            print(f"Timeline ID: {timeline['timeline_id']}")
            print(f"Total Duration: {timeline['total_duration']}s")
            print(f"Segments: {len(timeline['segments'])}")
            
            stats = timeline['statistics']
            print(f"\nStatistics:")
            print(f"  - A-roll segments: {stats['aroll_segments']}")
            print(f"  - B-roll insertions: {stats['broll_insertions']}")
            print(f"  - B-roll coverage: {stats['broll_coverage_percent']}%")
            print(f"  - Average confidence: {stats['average_confidence']:.3f}")
            
            print(f"\nTimeline Segments:")
            for i, seg in enumerate(timeline['segments'], 1):
                seg_type = "A-ROLL" if seg['type'] == 'a_roll' else "B-ROLL"
                print(f"  {i}. [{seg_type}] {seg['start_time']:.2f}s - {seg['end_time']:.2f}s")
                if seg['type'] == 'b_roll':
                    print(f"     → {seg['source']} (confidence: {seg['confidence']:.3f})")
            
            # Save to file
            output_file = "timeline_output.json"
            with open(output_file, "w") as f:
                json.dump(timeline, f, indent=2)
            print(f"\n✓ Timeline saved to: {output_file}")
            
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            sys.exit(1)
    
    except FileNotFoundError:
        print(f"✗ Error: Video file not found: {video_path}")
        sys.exit(1)
    
    except requests.exceptions.ConnectionError:
        print(f"✗ Error: Could not connect to API at {api_url}")
        print("   Make sure the server is running: python run_server.py")
        sys.exit(1)
    
    except requests.exceptions.Timeout:
        print("✗ Error: Request timed out (video processing took too long)")
        sys.exit(1)
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <path_to_video.mp4> [api_url]")
        print("\nExample:")
        print("  python test_api.py video.mp4")
        print("  python test_api.py video.mp4 http://localhost:8000")
        sys.exit(1)
    
    video_path = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    test_api(video_path, api_url)

