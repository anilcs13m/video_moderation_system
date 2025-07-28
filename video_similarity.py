import faiss
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import os
import json
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
import cv2
from moviepy.editor import VideoFileClip
import librosa

@dataclass
class VideoFeatures:
    visual_features: np.ndarray
    audio_features: np.ndarray
    metadata: dict

class VideoSimilarity:
    """Handles video similarity detection using FAISS and feature extraction"""
    
    def __init__(self, faiss_index_path: Optional[str] = None, feature_storage_path: str = "features"):
        os.makedirs(feature_storage_path, exist_ok=True)
        self.feature_storage_path = feature_storage_path
        self.index = self._load_faiss_index(faiss_index_path)
        self.video_model = hub.load("https://tfhub.dev/deepmind/i3d-kinetics-600/1").signatures['default']
        self.audio_model = hub.load("https://tfhub.dev/google/vggish/1").signatures['default']
        
    def _load_faiss_index(self, path: Optional[str]) -> Optional[faiss.Index]:
        if path and os.path.exists(path):
            return faiss.read_index(path)
        return None
        
    def _extract_frames(self, video_path: str, num_frames: int = 16) -> np.ndarray:
        clip = VideoFileClip(video_path)
        frames = []
        for t in np.linspace(0, clip.duration, num_frames):
            frame = clip.get_frame(t)
            frame = cv2.resize(frame, (224, 224))
            frames.append(frame)
        return np.array(frames)
        
    def extract_video_features(self, video_path: str) -> np.ndarray:
        """Extract I3D features from video"""
        frames = self._extract_frames(video_path)
        inputs = tf.convert_to_tensor(frames, dtype=tf.float32)[tf.newaxis, ...]
        outputs = self.video_model(inputs)
        return outputs['default'].numpy().flatten()
        
    def extract_audio_features(self, video_path: str) -> np.ndarray:
        """Extract VGGish audio features"""
        clip = VideoFileClip(video_path)
        audio_path = "temp_audio.wav"
        clip.audio.write_audiofile(audio_path)
        
        # Load audio and extract features
        audio, sr = librosa.load(audio_path, sr=16000)
        inputs = tf.convert_to_tensor(audio, dtype=tf.float32)[tf.newaxis, ...]
        outputs = self.audio_model(inputs)
        os.remove(audio_path)
        return outputs['default'].numpy().flatten()
        
    def save_features(self, video_path: str, features: VideoFeatures):
        """Save extracted features for future use"""
        video_id = os.path.basename(video_path).split('.')[0]
        save_path = os.path.join(self.feature_storage_path, f"{video_id}.npz")
        
        np.savez(
            save_path,
            visual_features=features.visual_features,
            audio_features=features.audio_features,
            metadata=json.dumps(features.metadata)
        )
        
    def load_features(self, video_id: str) -> Optional[VideoFeatures]:
        """Load previously extracted features"""
        path = os.path.join(self.feature_storage_path, f"{video_id}.npz")
        if os.path.exists(path):
            data = np.load(path, allow_pickle=True)
            return VideoFeatures(
                visual_features=data['visual_features'],
                audio_features=data['audio_features'],
                metadata=json.loads(data['metadata'])
            )
        return None
        
    def find_similar_videos(self, video_path: str, threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find similar videos using combined features"""
        features = VideoFeatures(
            visual_features=self.extract_video_features(video_path),
            audio_features=self.extract_audio_features(video_path),
            metadata={"path": video_path, "timestamp": str(datetime.now())}
        )
        self.save_features(video_path, features)
        
        if self.index is None:
            return []
            
        # Combine features and search
        combined_features = np.concatenate([
            features.visual_features,
            features.audio_features
        ])[np.newaxis, ...]
        
        D, I = self.index.search(combined_features, 5)
        return [(str(i), float(d)) for i, d in zip(I[0], D[0]) if d > threshold]
