"""
Semantic Matching Module

Matches A-roll transcript segments with B-roll descriptions using
OpenAI embeddings and cosine similarity.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path
import openai


class SemanticMatcher:
    """Matches A-roll segments with B-roll clips using semantic similarity."""
    
    def __init__(
        self, 
        api_key: str = None,
        similarity_threshold: float = 0.72,
        min_insertions: int = 3,
        max_insertions: int = 6
    ):
        """
        Initialize the semantic matcher.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
            similarity_threshold: Minimum cosine similarity for a match (0.0-1.0)
            min_insertions: Minimum number of B-roll insertions (default: 3)
            max_insertions: Maximum number of B-roll insertions (default: 6)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.similarity_threshold = similarity_threshold
        self.min_insertions = min_insertions
        self.max_insertions = max_insertions
        
        # Embedding model
        self.embedding_model = "text-embedding-3-small"  # Fast and cost-effective
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings for a list of texts using OpenAI API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            NumPy array of embeddings (n_texts, embedding_dim)
        """
        # Batch API call for efficiency
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=texts
        )
        
        # Extract embeddings
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0.0-1.0)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _calculate_similarity_matrix(
        self, 
        aroll_embeddings: np.ndarray,
        broll_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Calculate similarity matrix between A-roll and B-roll embeddings.
        
        Args:
            aroll_embeddings: Embeddings for A-roll segments (n_segments, dim)
            broll_embeddings: Embeddings for B-roll descriptions (n_brolls, dim)
            
        Returns:
            Similarity matrix (n_segments, n_brolls)
        """
        # Normalize embeddings for cosine similarity
        aroll_norm = aroll_embeddings / np.linalg.norm(aroll_embeddings, axis=1, keepdims=True)
        broll_norm = broll_embeddings / np.linalg.norm(broll_embeddings, axis=1, keepdims=True)
        
        # Calculate cosine similarity matrix
        similarity_matrix = np.dot(aroll_norm, broll_norm.T)
        
        return similarity_matrix
    
    def _generate_reason(
        self, 
        aroll_text: str, 
        broll_description: str, 
        similarity: float
    ) -> str:
        """
        Generate a short reason for the match.
        
        Args:
            aroll_text: A-roll segment text
            broll_description: B-roll description
            similarity: Similarity score
            
        Returns:
            Short reason string
        """
        # Extract key words/phrases for context
        if similarity >= 0.85:
            strength = "highly relevant"
        elif similarity >= 0.75:
            strength = "relevant"
        else:
            strength = "somewhat relevant"
        
        # Try to identify common themes
        aroll_lower = aroll_text.lower()
        broll_lower = broll_description.lower()
        
        # Check for common keywords
        common_keywords = []
        keywords_to_check = [
            "product", "demo", "demonstration", "app", "application",
            "office", "work", "working", "code", "coding", "programming",
            "team", "collaboration", "data", "analytics", "visualization",
            "typing", "keyboard", "interface", "screen"
        ]
        
        for keyword in keywords_to_check:
            if keyword in aroll_lower and keyword in broll_lower:
                common_keywords.append(keyword)
        
        if common_keywords:
            theme = common_keywords[0]
            return f"{strength.capitalize()} match: both mention '{theme}'"
        else:
            return f"{strength.capitalize()} semantic match"
    
    def _select_best_matches(
        self,
        similarity_matrix: np.ndarray,
        aroll_segments: List[Dict[str, Any]],
        broll_ids: List[str],
        broll_descriptions: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Select best matches while avoiding random insertions.
        
        Args:
            similarity_matrix: Similarity scores (n_segments, n_brolls)
            aroll_segments: List of A-roll segments with timestamps
            broll_ids: List of B-roll IDs
            broll_descriptions: Dictionary mapping broll_id to description
            
        Returns:
            List of match dictionaries
        """
        matches = []
        
        # Find all potential matches above threshold
        potential_matches = []
        
        for seg_idx, segment in enumerate(aroll_segments):
            for broll_idx, broll_id in enumerate(broll_ids):
                similarity = similarity_matrix[seg_idx, broll_idx]
                
                if similarity >= self.similarity_threshold:
                    potential_matches.append({
                        "segment_idx": seg_idx,
                        "broll_id": broll_id,
                        "similarity": float(similarity),
                        "start_time": segment["start_time"],
                        "end_time": segment["end_time"],
                        "aroll_text": segment["text"],
                        "broll_description": broll_descriptions[broll_id]
                    })
        
        # Sort by similarity (highest first)
        potential_matches.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Select matches with constraints:
        # 1. Avoid inserting multiple B-rolls too close together (min 5 seconds apart)
        # 2. Don't reuse the same B-roll too frequently
        # 3. Select top matches up to max_insertions
        
        selected_indices = set()
        used_brolls = {}  # Track how many times each B-roll is used
        last_insertion_time = -10.0  # Track last insertion to avoid clustering
        
        for match in potential_matches:
            # Check if we've reached max insertions
            if len(matches) >= self.max_insertions:
                break
            
            seg_idx = match["segment_idx"]
            broll_id = match["broll_id"]
            start_time = match["start_time"]
            
            # Skip if this segment already has a match
            if seg_idx in selected_indices:
                continue
            
            # Skip if B-roll is used too many times (max 2 uses per B-roll)
            if used_brolls.get(broll_id, 0) >= 2:
                continue
            
            # Skip if too close to previous insertion (min 5 seconds gap)
            if start_time - last_insertion_time < 5.0:
                continue
            
            # Add this match
            matches.append(match)
            selected_indices.add(seg_idx)
            used_brolls[broll_id] = used_brolls.get(broll_id, 0) + 1
            last_insertion_time = start_time
        
        # If we have fewer than min_insertions, relax constraints slightly
        if len(matches) < self.min_insertions:
            # Relax time constraint to 3 seconds
            for match in potential_matches:
                if len(matches) >= self.min_insertions:
                    break
                
                seg_idx = match["segment_idx"]
                broll_id = match["broll_id"]
                start_time = match["start_time"]
                
                if seg_idx in selected_indices:
                    continue
                
                if start_time - last_insertion_time < 3.0:
                    continue
                
                matches.append(match)
                selected_indices.add(seg_idx)
                used_brolls[broll_id] = used_brolls.get(broll_id, 0) + 1
                last_insertion_time = start_time
        
        # Sort matches by start_time for chronological order
        matches.sort(key=lambda x: x["start_time"])
        
        return matches
    
    def match(
        self,
        aroll_segments: List[Dict[str, Any]],
        broll_descriptions: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Match A-roll segments with B-roll descriptions.
        
        Args:
            aroll_segments: List of A-roll segments with start_time, end_time, text
            broll_descriptions: Dictionary mapping broll_id to description string
            
        Returns:
            List of match dictionaries with:
            - start_sec: Start time in seconds
            - duration_sec: Duration of the A-roll segment
            - broll_id: ID of matched B-roll
            - confidence: Similarity score (0.0-1.0)
            - reason: Short explanation of the match
        """
        if not aroll_segments:
            raise ValueError("A-roll segments list is empty")
        
        if not broll_descriptions:
            raise ValueError("B-roll descriptions dictionary is empty")
        
        # Extract texts for embedding
        aroll_texts = [seg["text"] for seg in aroll_segments]
        broll_ids = list(broll_descriptions.keys())
        broll_texts = [broll_descriptions[b_id] for b_id in broll_ids]
        
        # Get embeddings
        print(f"Generating embeddings for {len(aroll_texts)} A-roll segments and {len(broll_texts)} B-rolls...")
        aroll_embeddings = self._get_embeddings(aroll_texts)
        broll_embeddings = self._get_embeddings(broll_texts)
        
        # Calculate similarity matrix
        similarity_matrix = self._calculate_similarity_matrix(aroll_embeddings, broll_embeddings)
        
        # Select best matches
        matches = self._select_best_matches(
            similarity_matrix,
            aroll_segments,
            broll_ids,
            broll_descriptions
        )
        
        # Format output
        formatted_matches = []
        for match in matches:
            segment = aroll_segments[match["segment_idx"]]
            duration = segment["end_time"] - segment["start_time"]
            
            formatted_match = {
                "start_sec": round(segment["start_time"], 2),
                "duration_sec": round(duration, 2),
                "broll_id": match["broll_id"],
                "confidence": round(match["similarity"], 3),
                "reason": self._generate_reason(
                    match["aroll_text"],
                    match["broll_description"],
                    match["similarity"]
                )
            }
            formatted_matches.append(formatted_match)
        
        return formatted_matches
    
    def match_from_files(
        self,
        aroll_transcript_path: str,
        broll_descriptions_path: str
    ) -> List[Dict[str, Any]]:
        """
        Match from JSON files.
        
        Args:
            aroll_transcript_path: Path to A-roll transcript JSON
            broll_descriptions_path: Path to B-roll descriptions JSON
            
        Returns:
            List of match dictionaries
        """
        # Load A-roll transcript
        with open(aroll_transcript_path, 'r', encoding='utf-8') as f:
            aroll_data = json.load(f)
            aroll_segments = aroll_data.get("segments", [])
        
        # Load B-roll descriptions
        with open(broll_descriptions_path, 'r', encoding='utf-8') as f:
            broll_data = json.load(f)
            broll_descriptions = broll_data.get("broll_descriptions", {})
        
        return self.match(aroll_segments, broll_descriptions)
    
    def save_matches(
        self,
        matches: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """
        Save matches to JSON file.
        
        Args:
            matches: List of match dictionaries
            output_path: Path to save JSON file
            
        Returns:
            Path to saved file
        """
        output_data = {
            "matches": matches,
            "total_matches": len(matches),
            "settings": {
                "similarity_threshold": self.similarity_threshold,
                "min_insertions": self.min_insertions,
                "max_insertions": self.max_insertions
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return output_path


def main():
    """Example usage of the semantic matcher."""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python matcher.py <aroll_transcript.json> <broll_descriptions.json>")
        sys.exit(1)
    
    aroll_path = sys.argv[1]
    broll_path = sys.argv[2]
    
    try:
        matcher = SemanticMatcher(
            similarity_threshold=0.72,
            min_insertions=3,
            max_insertions=6
        )
        
        matches = matcher.match_from_files(aroll_path, broll_path)
        
        print(f"\nFound {len(matches)} matches:\n")
        for i, match in enumerate(matches, 1):
            print(f"Match {i}:")
            print(f"  Time: {match['start_sec']}s (duration: {match['duration_sec']}s)")
            print(f"  B-roll: {match['broll_id']}")
            print(f"  Confidence: {match['confidence']:.3f}")
            print(f"  Reason: {match['reason']}\n")
        
        # Save results
        output_path = "matches.json"
        matcher.save_matches(matches, output_path)
        print(f"Results saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

