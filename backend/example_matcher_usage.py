"""
Example usage of Semantic Matching Module

Demonstrates matching A-roll segments with B-roll descriptions.
"""

from app.services.matcher import SemanticMatcher

# Example A-roll segments (from transcribe.py output)
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

# Example B-roll descriptions (from broll_analysis.py output)
broll_descriptions = {
    "broll_1": "Product Close-up shows mobile application with smartphone, screen, app interface - Close-up shot of smartphone screen showing app interface (professional tone)",
    "broll_2": "Office Environment at office - Wide shot of modern office workspace with people working (productive tone)",
    "broll_3": "Hand Typing shows typing on keyboard - Close-up of hands typing on laptop keyboard (focused tone)",
    "broll_4": "Data Visualization features data analytics with charts, graphs, analytics dashboard - Animated charts and graphs displaying analytics",
    "broll_5": "Team Collaboration shows collaborating at meeting room - People discussing around a whiteboard (collaborative tone)",
    "broll_6": "Code Editor shows coding with code editor, programming syntax - Screen recording of code being written in editor"
}

if __name__ == "__main__":
    # Initialize matcher with default settings
    matcher = SemanticMatcher(
        similarity_threshold=0.72,
        min_insertions=3,
        max_insertions=6
    )
    
    print("=" * 70)
    print("SEMANTIC MATCHING: A-ROLL SEGMENTS → B-ROLL DESCRIPTIONS")
    print("=" * 70)
    print(f"\nA-roll segments: {len(aroll_segments)}")
    print(f"B-roll clips: {len(broll_descriptions)}")
    print(f"Similarity threshold: {matcher.similarity_threshold}")
    print(f"Insertion range: {matcher.min_insertions}-{matcher.max_insertions}")
    print("\n" + "-" * 70)
    print("Matching in progress...\n")
    
    # Perform matching
    matches = matcher.match(aroll_segments, broll_descriptions)
    
    # Display results
    print("=" * 70)
    print(f"MATCHING RESULTS: {len(matches)} matches found")
    print("=" * 70)
    print()
    
    for i, match in enumerate(matches, 1):
        print(f"Match {i}:")
        print(f"  ⏱️  Time: {match['start_sec']}s (duration: {match['duration_sec']}s)")
        print(f"  🎬 B-roll: {match['broll_id']}")
        print(f"  📊 Confidence: {match['confidence']:.3f} ({match['confidence']*100:.1f}%)")
        print(f"  💡 Reason: {match['reason']}")
        print()
    
    # Save results
    output_path = "matches.json"
    matcher.save_matches(matches, output_path)
    print(f"✓ Results saved to: {output_path}")
    print(f"✓ Total matches: {len(matches)}")

