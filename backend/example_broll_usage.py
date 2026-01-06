"""
Example usage of B-roll Analysis Module

Demonstrates how to analyze 6 B-roll videos with metadata.
"""

from app.services.broll_analysis import BRollAnalyzer

# Example: 6 B-roll videos with their metadata
broll_metadata = {
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

if __name__ == "__main__":
    # Initialize analyzer
    analyzer = BRollAnalyzer()
    
    # Analyze all 6 B-rolls
    descriptions = analyzer.analyze_brolls(broll_metadata)
    
    # Display results
    print("=" * 60)
    print("B-ROLL DESCRIPTIONS")
    print("=" * 60)
    print()
    
    for broll_id, description in descriptions.items():
        print(f"{broll_id.upper()}:")
        print(f"  {description}\n")
    
    # Save to JSON
    output_path = "broll_descriptions.json"
    analyzer.save_descriptions(descriptions, output_path)
    print(f"\n✓ Descriptions saved to: {output_path}")
    print(f"✓ Total B-rolls analyzed: {len(descriptions)}")

