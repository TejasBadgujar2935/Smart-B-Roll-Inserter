"""
Timeline Planner Module

Combines A-roll transcript segments and B-roll insertions into
a single structured timeline JSON.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class TimelinePlanner:
    """Plans timeline by combining A-roll segments and B-roll insertions."""
    
    def __init__(self, aroll_video_path: str = None):
        """
        Initialize the timeline planner.
        
        Args:
            aroll_video_path: Path to the A-roll video file (optional, for metadata)
        """
        self.aroll_video_path = aroll_video_path
    
    def _create_timeline_segments(
        self,
        aroll_segments: List[Dict[str, Any]],
        broll_matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create timeline segments by merging A-roll and B-roll data.
        
        Args:
            aroll_segments: List of A-roll transcript segments
            broll_matches: List of B-roll insertion matches
            
        Returns:
            List of timeline segments in chronological order
        """
        timeline_segments = []
        
        # Create a sorted list of insertion points
        insertions = sorted(broll_matches, key=lambda x: x["start_sec"])
        
        # Get total A-roll duration
        if not aroll_segments:
            return []
        
        total_aroll_duration = aroll_segments[-1]["end_time"]
        current_time = 0.0
        
        # Process timeline chronologically
        for insertion in insertions:
            insertion_start = insertion["start_sec"]
            insertion_duration = insertion["duration_sec"]
            
            # Add A-roll segment before insertion (if any)
            if current_time < insertion_start:
                timeline_segments.append({
                    "type": "a_roll",
                    "start_time": round(current_time, 2),
                    "end_time": round(insertion_start, 2),
                    "duration": round(insertion_start - current_time, 2),
                    "source": "a_roll_video",
                    "transcript": self._get_transcript_for_range(
                        aroll_segments, current_time, insertion_start
                    )
                })
            
            # Find the matching A-roll segment for this insertion
            matching_segment = None
            for seg in aroll_segments:
                if abs(seg["start_time"] - insertion_start) < 0.1:  # Allow small tolerance
                    matching_segment = seg
                    break
            
            # Add B-roll insertion
            timeline_segments.append({
                "type": "b_roll",
                "start_time": round(insertion_start, 2),
                "end_time": round(insertion_start + insertion_duration, 2),
                "duration": round(insertion_duration, 2),
                "source": insertion["broll_id"],
                "insertion_reason": insertion["reason"],
                "confidence": insertion["confidence"],
                "matching_segment": {
                    "text": matching_segment["text"] if matching_segment else "",
                    "start_time": matching_segment["start_time"] if matching_segment else insertion_start,
                    "end_time": matching_segment["end_time"] if matching_segment else insertion_start + insertion_duration
                } if matching_segment else None
            })
            
            current_time = insertion_start + insertion_duration
        
        # Add remaining A-roll content after last insertion
        if current_time < total_aroll_duration:
            timeline_segments.append({
                "type": "a_roll",
                "start_time": round(current_time, 2),
                "end_time": round(total_aroll_duration, 2),
                "duration": round(total_aroll_duration - current_time, 2),
                "source": "a_roll_video",
                "transcript": self._get_transcript_for_range(
                    aroll_segments, current_time, total_aroll_duration
                )
            })
        
        # If no insertions, return full A-roll
        if not insertions:
            timeline_segments.append({
                "type": "a_roll",
                "start_time": 0.0,
                "end_time": round(total_aroll_duration, 2),
                "duration": round(total_aroll_duration, 2),
                "source": "a_roll_video",
                "transcript": self._get_transcript_for_range(
                    aroll_segments, 0.0, total_aroll_duration
                )
            })
        
        return timeline_segments
    
    def _get_transcript_for_range(
        self,
        segments: List[Dict[str, Any]],
        start_time: float,
        end_time: float
    ) -> str:
        """
        Get transcript text for a time range.
        
        Args:
            segments: List of transcript segments
            start_time: Start time of range
            end_time: End time of range
            
        Returns:
            Combined transcript text for the range
        """
        relevant_segments = []
        for seg in segments:
            seg_start = seg["start_time"]
            seg_end = seg["end_time"]
            
            # Check if segment overlaps with range
            if not (seg_end < start_time or seg_start > end_time):
                relevant_segments.append(seg["text"])
        
        return " ".join(relevant_segments)
    
    def _calculate_statistics(
        self,
        timeline_segments: List[Dict[str, Any]],
        aroll_segments: List[Dict[str, Any]],
        broll_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate timeline statistics for debugging.
        
        Args:
            timeline_segments: List of timeline segments
            aroll_segments: Original A-roll segments
            broll_matches: B-roll matches
            
        Returns:
            Statistics dictionary
        """
        total_duration = 0.0
        aroll_duration = 0.0
        broll_duration = 0.0
        aroll_count = 0
        broll_count = 0
        
        for seg in timeline_segments:
            duration = seg.get("duration", 0.0)
            total_duration += duration
            
            if seg["type"] == "a_roll":
                aroll_duration += duration
                aroll_count += 1
            elif seg["type"] == "b_roll":
                broll_duration += duration
                broll_count += 1
        
        # Calculate original A-roll duration
        original_aroll_duration = 0.0
        if aroll_segments:
            original_aroll_duration = aroll_segments[-1]["end_time"]
        
        # Calculate average confidence
        avg_confidence = 0.0
        if broll_matches:
            total_confidence = sum(m["confidence"] for m in broll_matches)
            avg_confidence = total_confidence / len(broll_matches)
        
        return {
            "total_duration": round(total_duration, 2),
            "original_aroll_duration": round(original_aroll_duration, 2),
            "aroll_duration": round(aroll_duration, 2),
            "broll_duration": round(broll_duration, 2),
            "aroll_segments": aroll_count,
            "broll_insertions": broll_count,
            "broll_coverage_percent": round((broll_duration / total_duration * 100), 1) if total_duration > 0 else 0.0,
            "average_confidence": round(avg_confidence, 3),
            "total_segments": len(timeline_segments)
        }
    
    def create_timeline(
        self,
        aroll_segments: List[Dict[str, Any]],
        broll_matches: List[Dict[str, Any]],
        aroll_video_path: str = None
    ) -> Dict[str, Any]:
        """
        Create a complete timeline plan.
        
        Args:
            aroll_segments: List of A-roll transcript segments
            broll_matches: List of B-roll insertion matches
            aroll_video_path: Path to A-roll video (optional)
            
        Returns:
            Complete timeline dictionary
        """
        # Use provided path or instance path
        video_path = aroll_video_path or self.aroll_video_path
        
        # Create timeline segments
        timeline_segments = self._create_timeline_segments(aroll_segments, broll_matches)
        
        # Calculate statistics
        stats = self._calculate_statistics(timeline_segments, aroll_segments, broll_matches)
        
        # Build complete timeline
        timeline = {
            "timeline_id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "source_video": video_path or "a_roll_video.mp4",
            "total_duration": stats["total_duration"],
            "segments": timeline_segments,
            "statistics": stats,
            "debug_info": {
                "original_aroll_segments": len(aroll_segments),
                "broll_matches_found": len(broll_matches),
                "timeline_segments_created": len(timeline_segments),
                "aroll_segments": [
                    {
                        "start_time": seg["start_time"],
                        "end_time": seg["end_time"],
                        "text": seg["text"][:50] + "..." if len(seg["text"]) > 50 else seg["text"]
                    }
                    for seg in aroll_segments
                ],
                "broll_insertions": [
                    {
                        "broll_id": match["broll_id"],
                        "at_time": match["start_sec"],
                        "confidence": match["confidence"],
                        "reason": match["reason"]
                    }
                    for match in broll_matches
                ]
            }
        }
        
        return timeline
    
    def create_timeline_from_files(
        self,
        aroll_transcript_path: str,
        broll_matches_path: str,
        aroll_video_path: str = None
    ) -> Dict[str, Any]:
        """
        Create timeline from JSON files.
        
        Args:
            aroll_transcript_path: Path to A-roll transcript JSON
            broll_matches_path: Path to B-roll matches JSON
            aroll_video_path: Path to A-roll video (optional)
            
        Returns:
            Complete timeline dictionary
        """
        # Load A-roll transcript
        with open(aroll_transcript_path, 'r', encoding='utf-8') as f:
            aroll_data = json.load(f)
            aroll_segments = aroll_data.get("segments", [])
        
        # Load B-roll matches
        with open(broll_matches_path, 'r', encoding='utf-8') as f:
            matches_data = json.load(f)
            broll_matches = matches_data.get("matches", [])
        
        return self.create_timeline(aroll_segments, broll_matches, aroll_video_path)
    
    def save_timeline(
        self,
        timeline: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Save timeline to JSON file.
        
        Args:
            timeline: Timeline dictionary
            output_path: Path to save JSON file
            
        Returns:
            Path to saved file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(timeline, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def print_timeline_summary(self, timeline: Dict[str, Any]):
        """
        Print a human-readable summary of the timeline.
        
        Args:
            timeline: Timeline dictionary
        """
        print("=" * 80)
        print("TIMELINE SUMMARY")
        print("=" * 80)
        print(f"Timeline ID: {timeline['timeline_id']}")
        print(f"Created: {timeline['created_at']}")
        print(f"Source Video: {timeline['source_video']}")
        print(f"\nTotal Duration: {timeline['total_duration']}s")
        
        stats = timeline['statistics']
        print(f"\nStatistics:")
        print(f"  - A-roll segments: {stats['aroll_segments']}")
        print(f"  - B-roll insertions: {stats['broll_insertions']}")
        print(f"  - A-roll duration: {stats['aroll_duration']}s")
        print(f"  - B-roll duration: {stats['broll_duration']}s")
        print(f"  - B-roll coverage: {stats['broll_coverage_percent']}%")
        print(f"  - Average confidence: {stats['average_confidence']:.3f}")
        
        print(f"\nTimeline Segments ({len(timeline['segments'])}):")
        print("-" * 80)
        for i, seg in enumerate(timeline['segments'], 1):
            seg_type = "A-ROLL" if seg['type'] == 'a_roll' else "B-ROLL"
            print(f"{i}. [{seg_type}] {seg['start_time']:.2f}s - {seg['end_time']:.2f}s ({seg['duration']:.2f}s)")
            
            if seg['type'] == 'a_roll' and 'transcript' in seg:
                transcript_preview = seg['transcript'][:60] + "..." if len(seg['transcript']) > 60 else seg['transcript']
                print(f"   Transcript: {transcript_preview}")
            elif seg['type'] == 'b_roll':
                print(f"   B-roll: {seg['source']}")
                print(f"   Reason: {seg.get('insertion_reason', 'N/A')}")
                print(f"   Confidence: {seg.get('confidence', 0.0):.3f}")


def main():
    """Example usage of the timeline planner."""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python timeline.py <aroll_transcript.json> <broll_matches.json> [output.json]")
        sys.exit(1)
    
    aroll_path = sys.argv[1]
    matches_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "timeline.json"
    
    try:
        planner = TimelinePlanner()
        timeline = planner.create_timeline_from_files(aroll_path, matches_path)
        
        # Print summary
        planner.print_timeline_summary(timeline)
        
        # Save timeline
        planner.save_timeline(timeline, output_path)
        print(f"\n✓ Timeline saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

