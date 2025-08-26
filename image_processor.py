"""
Image processor module for handling screenshots and OCR functionality.
Uses Surya OCR for text extraction from images.
"""
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
from PIL import Image
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from surya.layout import LayoutPredictor

class ImageProcessor:
    """
    Processes images using Surya OCR to extract text and analyze content.
    """
    
    def __init__(self):
        """Initialize the image processor with Surya components."""
        # Initialize Surya components
        
        self.foundation_model = FoundationPredictor()
        self.text_recognizer = RecognitionPredictor(self.foundation_model)
        self.text_detector = DetectionPredictor()
        self.layout_analyzer = LayoutPredictor()
        
    
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Process an image using Surya OCR to extract text and analyze content.
        
        Args:
            image_data: Raw image data in bytes
            
        Returns:
            Dict containing extracted text and analysis results
        """
        # Create a temporary file to save the image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name
        
        try:
            # Open the image with PIL
            image = Image.open(temp_file_path)
            
            # Extract text using Surya components
            ocr_result = self._extract_text(image)
            
            # Analyze the image content
            image_analysis = self._analyze_image(image)
            
            return {
                "text": ocr_result.get("text", ""),
                "text_blocks": ocr_result.get("text_blocks", []),
                "analysis": image_analysis
            }
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def _extract_text(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract text from an image using Surya components.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dict containing extracted text and related information
        """
        try:
            # Detect text regions
            detection_result = self.text_detector([image])[0].__dict__.get("bboxes")
            
            # Extract text from detected regions
            text_blocks = []
            full_text = []
            
            for box in detection_result:
                bbox = box.bbox
                # Crop the image to the detected text region
                x1, y1, x2, y2 = bbox
                text_region = image.crop((x1, y1, x2, y2))
                
                # Recognize text in the region
                # recognition_result = self.text_recognizer.predict(text_region)
                recognition_result = self.text_recognizer([text_region], det_predictor=self.text_detector)[0].__dict__.get("text_lines")
                recognized_text = [recognition_result[i].__dict__.get("text") for i in range(len(recognition_result))]
                recognized_text = " ".join(recognized_text)
                
                if recognized_text:
                    text_blocks.append({
                        "text": recognized_text,
                        "box": bbox
                    })
                    full_text.append(recognized_text)
            
            # Get layout information
            # layout_result = self.layout_analyzer([image])
            
            return {
                "text": " ".join(full_text),
                "text_blocks": text_blocks,
                # "layout": layout_result.get("layout", {})
            }
        except Exception as e:
            print(f"Error extracting text: {e}")
            return {
                "text": "",
                "text_blocks": [],
                # "layout": {}
            }
    
    def _analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze image content to extract additional information.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dict containing analysis results
        """
        # Get image dimensions
        width, height = image.size
        
        # Convert to numpy array for analysis
        img_array = np.array(image)
        
        # Simple color analysis
        if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
            # Calculate average RGB values
            avg_color = np.mean(img_array, axis=(0, 1))
            
            # Determine if image is bright or dark
            brightness = np.mean(avg_color[:3])
            is_bright = brightness > 127
            
            # Detect dominant colors
            dominant_colors = self._get_dominant_colors(img_array)
        else:
            avg_color = [0, 0, 0]
            is_bright = False
            dominant_colors = []
        
        return {
            "dimensions": {
                "width": width,
                "height": height,
                "aspect_ratio": width / height if height > 0 else 0
            },
            "color_info": {
                "average_color": avg_color.tolist() if isinstance(avg_color, np.ndarray) else avg_color,
                "is_bright": int(is_bright),
                "dominant_colors": dominant_colors
            }
        }
    
    def _get_dominant_colors(self, img_array: np.ndarray, num_colors: int = 5) -> List[List[int]]:
        """
        Extract dominant colors from an image.
        
        Args:
            img_array: Numpy array representing the image
            num_colors: Number of dominant colors to extract
            
        Returns:
            List of RGB values representing dominant colors
        """
        # Reshape the array to be a list of pixels
        pixels = img_array.reshape(-1, img_array.shape[2])
        
        # Sample pixels to reduce computation (take every 100th pixel)
        sampled_pixels = pixels[::100]
        
        # Simple clustering to find dominant colors
        # This is a simplified approach; for production, consider using k-means clustering
        unique_colors, counts = np.unique(sampled_pixels, axis=0, return_counts=True)
        
        # Sort by frequency
        sorted_indices = np.argsort(-counts)
        dominant = unique_colors[sorted_indices]
        
        # Return top N colors
        return dominant[:num_colors].tolist()


# Example usage
if __name__ == "__main__":
    processor = ImageProcessor()
    
    # Test with a sample image
    with open("sample.png", "rb") as f:
        image_data = f.read()
    
    result = processor.process_image(image_data)
    print(f"Extracted text: {result['text']}")
    print(f"Image analysis: {result['analysis']}")
