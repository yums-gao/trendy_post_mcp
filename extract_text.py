#!/usr/bin/env python
"""
Simple script to extract text from a screenshot using Surya OCR.
"""
import sys
import os
import json
from PIL import Image
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from surya.layout import LayoutPredictor

def extract_text_from_image(image_path, verbose=True):
    """
    Extract text from an image using Surya OCR.
    
    Args:
        image_path: Path to the image file
        verbose: Whether to print detailed information
        
    Returns:
        Dict containing extracted text and additional information
    """
    try:
        # Open the image
        image = Image.open(image_path)
        
        # Initialize Surya components
        foundation_model = FoundationPredictor()
        text_recognizer = RecognitionPredictor(foundation_model)
        text_detector = DetectionPredictor()
        layout_analyzer = LayoutPredictor()
        
        if verbose:
            print(f"Processing image: {image_path}")
        
        # Detect text regions
        detection_results = text_detector([image])
        
        # Extract text from the entire image
        recognition_results = text_recognizer([image], det_predictor=text_detector)
        
        # Get layout information
        layout_results = layout_analyzer([image])
        
        # Process detection results
        text_blocks = []
        full_text = []
        
        if detection_results and len(detection_results) > 0:
            bboxes = detection_results[0].__dict__.get("bboxes", [])
            
            for box in bboxes:
                # Crop the image to the detected text region
                x1, y1, x2, y2 = box.bbox
                text_region = image.crop((x1, y1, x2, y2))
                
                # Recognize text in the region
                region_recognition = text_recognizer([text_region], det_predictor=text_detector)
                
                if region_recognition and len(region_recognition) > 0:
                    text_lines = region_recognition[0].__dict__.get("text_lines", [])
                    recognized_text = [line.__dict__.get("text", "") for line in text_lines]
                    recognized_text = " ".join(filter(None, recognized_text))
                    
                    if recognized_text:
                        text_blocks.append({
                            "text": recognized_text,
                            "box": [x1, y1, x2, y2]
                        })
                        full_text.append(recognized_text)
        
        # Process layout results
        layout_info = {}
        if layout_results and len(layout_results) > 0:
            layout_info = layout_results[0].__dict__
            # Convert any non-serializable objects to strings
            layout_info = {k: str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else v 
                          for k, v in layout_info.items()}
        
        # Combine all extracted text
        extracted_text = " ".join(full_text)
        
        result = {
            "text": extracted_text,
            "text_blocks": text_blocks,
            "layout": layout_info
        }
        
        if verbose:
            print("\nExtracted Text:")
            print(extracted_text)
            print(f"\nDetected Language: {language}")
            print(f"\nFound {len(text_blocks)} text blocks")
        
        return result
            
    except Exception as e:
        print(f"Error extracting text: {e}")
        import traceback
        traceback.print_exc()
        return {"text": "", "text_blocks": [], "language": "unknown", "layout": {}}

if __name__ == "__main__":
    # Check if image path is provided as command line argument
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <image_path>")
        sys.exit(1)
    
    # Get the image path from command line argument
    image_path = sys.argv[1]
    
    # Check if the file exists
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        sys.exit(1)
    
    # Extract text from the image
    result = extract_text_from_image(image_path)
    
    # Save the result to a JSON file
    output_path = os.path.splitext(image_path)[0] + "_ocr.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_path}")
