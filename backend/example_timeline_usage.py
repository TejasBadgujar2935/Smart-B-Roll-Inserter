"""
Example usage of Timeline Planner Module

Demonstrates creating a timeline from A-roll segments and B-roll matches.
"""

from app.services.timeline import TimelinePlanner

# Example A-roll segments (from transcribe.py)
aroll_segments = [
    {"start_time": 0.0, "end_time": 3.5, "text": "Welcome to today's tutorial on smart video editing."},
    {"start_time": 3.5, "end_time": 7.2, "text": "We'll be exploring how AI can help automate the B-roll insertion process."},
    {"start_time": 7.2, "end_time": 11.8, "text": "First, let's understand what makes a good B-roll clip."},
    {"start_time": 11.8, "end_time": 15.4, "text": "B-roll should complement your main content and add visual interest."},
    {"start_time": 15.4, "end_time": 19.1, "text": "Now, let's see how our system analyzes your A-roll content."},
    {"start_time": 19.1, "end_time": 23.7, "text": "The AI identifies natural pause points and topic transitions."},
    {"start_time": 23.7, "end_time": 27.3, "text": "This allows for seamless B-roll insertion at the perfect moments."},
    {"start_time": 27.3, "end_time": 31.0, "text": "Let's take a look at the product demonstration."},
    {"start_time": 31.0, "end_time": 35.6, "text": "As you can see, the interface is intuitive and user-friendly."},
    {"start_time": 35.6, "end_time": 40.2, "text": "The timeline view shows exactly where each B-roll clip will be placed."}
]

# Example B-roll matches (from matcher.py)
broll_matches = [
    {
        "start_sec": 27.3,
        "duration_sec": 3.7,
        "broll_id": "broll_1",
        "confidence": 0.856,
        "reason": "Highly relevant match: both mention 'product'"
    },
    {
        "start_sec": 31.0,
        "duration_sec": 4.6,
        "broll_id": "broll_1",
        "confidence": 0.823,
        "reason": "Highly relevant match: both mention 'interface'"
    },
    {
        "start_sec": 35.6,
        "duration_sec": 4.6,
        "broll_id": "broll_4",
        "confidence": 0.791,
        "reason": "Relevant match: both mention 'analytics'"
    }
]

if __name__ == "__main__":
    # Initialize planner
    planner = TimelinePlanner(aroll_video_path="uploads/a_roll_video.mp4")
    
    print("=" * 80)
    print("TIMELINE PLANNER")
    print("=" * 80)
    print(f"\nA-roll segments: {len(aroll_segments)}")
    print(f"B-roll insertions: {len(broll_matches)}")
    print("\nCreating timeline...\n")
    
    # Create timeline
    timeline = planner.create_timeline(aroll_segments, broll_matches)
    
    # Print summary
    planner.print_timeline_summary(timeline)
    
    # Save timeline
    output_path = "timeline.json"
    planner.save_timeline(timeline, output_path)
    print(f"\n✓ Timeline saved to: {output_path}")
    
    # Display some debug info
    print("\n" + "=" * 80)
    print("DEBUG INFORMATION")
    print("=" * 80)
    print(f"\nOriginal A-roll segments: {timeline['debug_info']['original_aroll_segments']}")
    print(f"B-roll matches found: {timeline['debug_info']['broll_matches_found']}")
    print(f"Timeline segments created: {timeline['debug_info']['timeline_segments_created']}")
    
    print("\nB-roll Insertions:")
    for insertion in timeline['debug_info']['broll_insertions']:
        print(f"  - {insertion['broll_id']} at {insertion['at_time']}s (confidence: {insertion['confidence']:.3f})")

