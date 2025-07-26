import os
import json
from typing import Dict
from moderator import Moderator

class VideoModerationService:
    """
    Main service class that handles video moderation requests.
    """
    
    def __init__(self):
        """Initialize moderation service"""
        self.moderator = Moderator()
        
    def moderate_video(self, video_path: str) -> Dict:
        """
        Moderate video and return results with thumbnail.
        
        Args:
            video_path: Path to video file to moderate
            
        Returns:
            Dictionary containing:
            - video_path: Original video path
            - moderation_status: APPROVED/REJECTED/FLAGGED
            - moderation_level: HIGH/MEDIUM/LOW
            - thumbnail_path: Path to generated thumbnail
            - details: Detailed results from all checks
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        return self.moderator.process_video(video_path)
        
    def save_results(self, results: Dict, output_path: str):
        """
        Save moderation results to JSON file.
        
        Args:
            results: Moderation results dictionary
            output_path: Path to save JSON file
        """
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    # Example usage
    service = VideoModerationService()
    results = service.moderate_video("input_video.mp4")
    service.save_results(results, "moderation_results.json")
    print("Moderation completed. Results saved.")
