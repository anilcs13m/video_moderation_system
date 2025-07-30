from typing import Dict, Tuple, Optional
import os
import json
from dataclasses import dataclass
import concurrent.futures
from datetime import datetime

@dataclass
class ModerationResult:
    status: str  # APPROVED/REJECTED/FLAGGED
    level: str   # HIGH/MEDIUM/LOW
    thumbnail_path: Optional[str]
    details: Dict
    metadata: dict

class Moderator:
    """Orchestrates all moderation checks and makes final decision"""
    
    def __init__(self):
        self.nsfw_detector = NSFWDetector()
        self.ocr_processor = OCRProcessor()
        self.object_detector = ObjectDetector()
        self.copyright_detector = CopyrightDetector()
        self.quality_detector = QualityDetector()
        self.content_checker = ContentChecker()
        self.thumbnail_generator = ThumbnailGenerator()
        
    def _run_parallel_checks(self, video_path: str) -> Dict:
        """Run all checks in parallel"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                "nsfw": executor.submit(self.nsfw_detector.classify_video, video_path),
                "ocr": executor.submit(self.ocr_processor.process_video, video_path),
                "objects": executor.submit(self.object_detector.process_video, video_path),
                "copyright": executor.submit(self.copyright_detector.detect_copyright, video_path),
                "quality": executor.submit(self.quality_detector.assess_quality, video_path),
                "content": executor.submit(self.content_checker.run_content_checks, video_path)
            }
            
            results = {}
            for key, future in futures.items():
                try:
                    results[key] = future.result()
                except Exception as e:
                    results[key] = {"error": str(e)}
                    
            return results
            
    def _determine_moderation_level(self, results: Dict) -> str:
        """Determine overall moderation level"""
        if results['nsfw'][0] == 1 and results['nsfw'][1] > 0.9:
            return "HIGH"
            
        if len(results['copyright']['detected_logos']) > 0:
            return "HIGH"
            
        if results['quality']['video_score'] < 0.3:
            return "MEDIUM"
            
        if any(obj['class_id'] in [1, 2, 3] for obj in results['objects']['objects']):  # Example restricted classes
            return "MEDIUM"
            
        return "LOW"
        
    def _make_decision(self, results: Dict, level: str) -> str:
        """Make final moderation decision"""
        if level == "HIGH":
            return "REJECTED"
        elif level == "MEDIUM":
            return "FLAGGED"
        return "APPROVED"
        
    def process_video(self, video_path: str) -> ModerationResult:
        """Run complete moderation pipeline"""
        # Run all checks in parallel
        check_results = self._run_parallel_checks(video_path)
        
        # Determine moderation level
        level = self._determine_moderation_level(check_results)
        
        # Make final decision
        status = self._make_decision(check_results, level)
        
        # Generate thumbnail if approved
        thumbnail_path = None
        if status == "APPROVED":
            thumbnail_result = self.thumbnail_generator.generate_thumbnail(video_path)
            thumbnail_path = thumbnail_result.thumbnail_path
            
        result = ModerationResult(
            status=status,
            level=level,
            thumbnail_path=thumbnail_path,
            details=check_results,
            metadata={
                "path": video_path,
                "timestamp": str(datetime.now()),
                "version": "1.0"
            }
        )
        
        return result
