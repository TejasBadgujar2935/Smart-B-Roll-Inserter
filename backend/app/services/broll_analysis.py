"""
B-roll Understanding Module

Converts B-roll video metadata into standardized text descriptions
for semantic matching with A-roll content.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class BRollAnalyzer:
    """Analyzes B-roll videos by converting metadata into text descriptions."""
    
    def __init__(self):
        """Initialize the B-roll analyzer."""
        pass
    
    def _normalize_metadata(self, metadata: Any) -> Dict[str, Any]:
        """
        Normalize metadata from various formats into a standard dictionary.
        
        Args:
            metadata: Can be dict, JSON string, or file path to JSON
            
        Returns:
            Normalized metadata dictionary
        """
        if isinstance(metadata, str):
            # Check if it's a file path
            if os.path.exists(metadata):
                with open(metadata, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                # Assume it's a JSON string
                metadata = json.loads(metadata)
        
        if not isinstance(metadata, dict):
            raise ValueError(f"Metadata must be dict, JSON string, or file path. Got: {type(metadata)}")
        
        return metadata
    
    def _extract_key_fields(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key fields from metadata that are useful for description.
        
        Args:
            metadata: Normalized metadata dictionary
            
        Returns:
            Dictionary with extracted key fields
        """
        # Common metadata field names (case-insensitive matching)
        field_mapping = {
            'title': ['title', 'name', 'clip_name', 'video_title'],
            'description': ['description', 'desc', 'summary', 'content'],
            'category': ['category', 'type', 'genre', 'tag'],
            'subject': ['subject', 'topic', 'theme', 'focus'],
            'action': ['action', 'activity', 'what', 'shows'],
            'location': ['location', 'place', 'setting', 'where'],
            'objects': ['objects', 'items', 'products', 'things'],
            'mood': ['mood', 'tone', 'atmosphere', 'feeling'],
            'tags': ['tags', 'keywords', 'labels']
        }
        
        extracted = {}
        metadata_lower = {k.lower(): v for k, v in metadata.items()}
        
        for standard_key, possible_keys in field_mapping.items():
            for key in possible_keys:
                if key.lower() in metadata_lower:
                    value = metadata_lower[key.lower()]
                    if value:  # Only include non-empty values
                        extracted[standard_key] = value
                        break
        
        # Also include any remaining fields that might be useful
        for key, value in metadata.items():
            if key.lower() not in [k.lower() for keys in field_mapping.values() for k in keys]:
                if isinstance(value, (str, int, float)) and value:
                    extracted[key] = value
        
        return extracted
    
    def _build_description(self, fields: Dict[str, Any]) -> str:
        """
        Build a natural language description from extracted fields.
        
        Args:
            fields: Extracted metadata fields
            
        Returns:
            Concise text description of the B-roll clip
        """
        parts = []
        
        # Start with title if available
        if 'title' in fields:
            parts.append(fields['title'])
        
        # Add action/subject
        if 'action' in fields:
            parts.append(f"shows {fields['action']}")
        elif 'subject' in fields:
            parts.append(f"features {fields['subject']}")
        
        # Add objects if mentioned
        if 'objects' in fields:
            objects_str = fields['objects']
            if isinstance(objects_str, list):
                objects_str = ', '.join(str(o) for o in objects_str)
            parts.append(f"with {objects_str}")
        
        # Add location context
        if 'location' in fields:
            parts.append(f"at {fields['location']}")
        
        # Add description if available (but keep it concise)
        if 'description' in fields:
            desc = fields['description']
            # If description is too long, truncate it
            if len(desc) > 100:
                desc = desc[:97] + "..."
            if parts:
                parts.append(f"- {desc}")
            else:
                parts.append(desc)
        
        # Add category/type context
        if 'category' in fields:
            if not parts:  # Only add if we don't have other content
                parts.append(f"{fields['category']} clip")
        
        # Add mood if available
        if 'mood' in fields and len(parts) < 3:  # Don't make it too long
            parts.append(f"({fields['mood']} tone)")
        
        # If we have tags, append them
        if 'tags' in fields and len(parts) < 2:
            tags = fields['tags']
            if isinstance(tags, list):
                tags_str = ', '.join(str(t) for t in tags[:3])  # Limit to 3 tags
            else:
                tags_str = str(tags)
            parts.append(f"[{tags_str}]")
        
        # Build final description
        if parts:
            description = ' '.join(parts)
            # Clean up any double spaces or awkward punctuation
            description = ' '.join(description.split())
            return description.strip()
        else:
            # Fallback: use any available field
            for key, value in fields.items():
                if value:
                    return str(value)
            return "B-roll video clip"
    
    def analyze_broll(
        self, 
        broll_id: str, 
        metadata: Any
    ) -> str:
        """
        Analyze a single B-roll and generate its description.
        
        Args:
            broll_id: Unique identifier for the B-roll (e.g., "broll_1", "broll_2")
            metadata: Metadata describing the B-roll (dict, JSON string, or file path)
            
        Returns:
            Text description of the B-roll
        """
        normalized = self._normalize_metadata(metadata)
        fields = self._extract_key_fields(normalized)
        description = self._build_description(fields)
        
        return description
    
    def analyze_brolls(
        self, 
        broll_metadata: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Analyze multiple B-rolls and return descriptions dictionary.
        
        Args:
            broll_metadata: Dictionary mapping broll_id to metadata
                           Format: { "broll_1": {...metadata...}, "broll_2": {...}, ... }
            
        Returns:
            Dictionary mapping broll_id to description
            Format: { "broll_1": "description", "broll_2": "description", ... }
        """
        descriptions = {}
        
        for broll_id, metadata in broll_metadata.items():
            try:
                description = self.analyze_broll(broll_id, metadata)
                descriptions[broll_id] = description
            except Exception as e:
                # Log error but continue with other B-rolls
                print(f"Warning: Failed to analyze {broll_id}: {e}")
                descriptions[broll_id] = f"B-roll clip {broll_id}"
        
        return descriptions
    
    def analyze_from_files(
        self, 
        metadata_files: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Analyze B-rolls from metadata JSON files.
        
        Args:
            metadata_files: Dictionary mapping broll_id to metadata file path
                          Format: { "broll_1": "path/to/metadata1.json", ... }
            
        Returns:
            Dictionary mapping broll_id to description
        """
        broll_metadata = {}
        
        for broll_id, file_path in metadata_files.items():
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Metadata file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                broll_metadata[broll_id] = json.load(f)
        
        return self.analyze_brolls(broll_metadata)
    
    def save_descriptions(
        self, 
        descriptions: Dict[str, str], 
        output_path: str
    ) -> str:
        """
        Save descriptions to JSON file.
        
        Args:
            descriptions: Dictionary mapping broll_id to description
            output_path: Path to save the JSON file
            
        Returns:
            Path to the saved file
        """
        output_data = {
            "broll_descriptions": descriptions,
            "total_brolls": len(descriptions)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return output_path


def main():
    """Example usage of the B-roll analyzer."""
    import sys
    
    # Example metadata for 6 B-rolls
    example_metadata = {
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
    
    analyzer = BRollAnalyzer()
    descriptions = analyzer.analyze_brolls(example_metadata)
    
    print("B-roll Descriptions:\n")
    for broll_id, description in descriptions.items():
        print(f"{broll_id}: {description}\n")
    
    # Save to file
    output_path = "broll_descriptions.json"
    analyzer.save_descriptions(descriptions, output_path)
    print(f"\nDescriptions saved to: {output_path}")


if __name__ == "__main__":
    main()

