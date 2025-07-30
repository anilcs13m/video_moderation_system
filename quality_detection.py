import numpy as np
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from typing import Tuple, Dict, Optional
import os
import json
from dataclasses import dataclass
import cv2
import subprocess
import tempfile

@dataclass
class QualityResult:
    video_score: float
    audio_score: float
    metadata: dict

class QualityDetector:
    """Video and audio quality assessment"""
    
    def __init__(self, feature_storage_path: str = "quality_features"):
        os.makedirs(feature_storage_path, exist_ok=True)
        self.feature_storage_path = feature_storage_path
        
    def _extract_sample(self, video_path: str, duration: int = 20):
        """Extract sample clip for analysis"""
        with tempfile.NamedTemporaryFile(suffix='.mp4') as temp:
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-ss', '0',
                '-t', str(duration),
                '-c:v', 'copy',
                '-c:a', 'copy',
                temp.name
            ]
            subprocess.run(cmd, check=True)
            return temp.name
            
    def check_video_quality(self, video_path: str) -> float:
        """Calculate video quality score (simplified)"""
        clip = VideoFileClip(video_path)
        if clip.duration < 3:
            return 0.0
            
        # Calculate simple quality metric (would use NIMA in production)
        frame = clip.get_frame(clip.duration / 2)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        score = cv2.Laplacian(gray, cv2.CV_64F).var() / 1000
        return float(np.clip(score, 0, 1))
        
    def check_audio_quality(self, audio_path: str) -> Tuple[bool, float]:
        """Check basic audio quality metrics"""
        sound = AudioSegment.from_file(audio_path)
        
        # Simple quality metrics
        max_amplitude = sound.max
        silence_ratio = sound.dBFS / -60  # Normalized
        
        # Combined score
        score = 0.7 * (max_amplitude / 32768) + 0.3 * (1 - silence_ratio)
        return (score > 0.5, float(score))
        
    def save_features(self, video_path: str, result: QualityResult):
        """Save quality assessment results"""
        video_id = os.path.basename(video_path).split('.')[0]
        save_path = os.path.join(self.feature_storage_path, f"{video_id}.json")
        
        with open(save_path, 'w') as f:
            json.dump({
                "video_score": result.video_score,
                "audio_score": result.audio_score,
                "metadata": result.metadata
            }, f)
            
    def assess_quality(self, video_path: str) -> QualityResult:
        """Run full quality assessment"""
        sample_path = self._extract_sample(video_path)
        
        video_score = self.check_video_quality(sample_path)
        
        # Extract audio
        with tempfile.NamedTemporaryFile(suffix='.wav') as audio_temp:
            clip = VideoFileClip(sample_path)
            clip.audio.write_audiofile(audio_temp.name)
            _, audio_score = self.check_audio_quality(audio_temp.name)
            
        result = QualityResult(
            video_score=video_score,
            audio_score=audio_score,
            metadata={
                "path": video_path,
                "timestamp": str(datetime.now()),
                "sample_duration": 20
            }
        )
        self.save_features(video_path, result)
        
        return result
