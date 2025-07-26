import cv2
import pytesseract
from typing import List, Dict
from moviepy.editor import VideoFileClip

class OCRProcessor:
    """
    Handles OCR (Optical Character Recognition) on video frames.
    Processes one frame per second to extract text content.
    """
    
    def __init__(self, tesseract_config: str = None):
        """
        Initialize OCR processor with Tesseract config.
        
        Args:
            tesseract_config: Custom Tesseract configuration
        """
        self.config = tesseract_config or '--oem 3 --psm 6'
        
    def extract_frames(self, video_path: str, fps: int = 1) -> List:
        """
        Extract frames from video at specified FPS.
        
        Args:
            video_path: Path to video file
            fps: Frames per second to extract
            
        Returns:
            List of extracted frames
        """
        pass
        
    def process_frame(self, frame) -> str:
        """
        Perform OCR on single frame.
        
        Args:
            frame: Image frame to process
            
        Returns:
            Extracted text
        """
        pass
        
    def process_video(self, video_path: str) -> Dict[int, str]:
        """
        Process video and return text per second.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary of {second: extracted_text}
        """
        pass
