#!/usr/bin/env python
"""
Trendy Post MCP Server

This script provides an MCP server for generating trending Xiaohongshu posts from screenshots.
"""

import os
import sys
import base64
import logging
import requests
from typing import Dict, Any, List
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Import local modules
from image_processor import ImageProcessor
from post_generator import PostGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("trendy_post_mcp")

# Initialize MCP
mcp = FastMCP("trendy-post-mcp")

# Initialize components
image_processor = ImageProcessor()
post_generator = PostGenerator()

# Define request/response models
class ProcessScreenshotRequest(BaseModel):
    image_url: str = Field(..., description="URL to the image")

class GeneratePostRequest(BaseModel):
    image_analysis: Dict[str, Any] = Field(..., description="Image analysis data from process_screenshot")

class ProcessAndGenerateRequest(BaseModel):
    image_url: str = Field(..., description="URL to the image")
    user_query: str = Field("", description="Optional user query to guide post generation")

class TextBlock(BaseModel):
    text: str = Field(..., description="Extracted text")
    box: List[float] = Field(..., description="Bounding box coordinates [x1, y1, x2, y2]")

class ImageAnalysisResponse(BaseModel):
    text: str = Field(..., description="Extracted text")
    text_blocks: List[TextBlock] = Field(default_factory=list, description="List of text blocks with positions")
    analysis: Dict[str, Any] = Field(default_factory=dict, description="Image analysis data")

class PostResponse(BaseModel):
    title: str = Field(..., description="Generated post title")
    content: str = Field(..., description="Generated post content")
    hashtags: List[str] = Field(default_factory=list, description="Generated hashtags")
    style: str = Field(..., description="Detected post style")

class ProcessAndGenerateResponse(BaseModel):
    image_analysis: ImageAnalysisResponse = Field(..., description="Image analysis results")
    post: PostResponse = Field(..., description="Generated post")

@mcp.tool
def process_screenshot(image_url: str) -> Dict[str, Any]:
    """
    Process a screenshot and extract text using OCR.
    
    Args:
        image_url: URL to the image
        
    Returns:
        OCR results and image analysis
    """
    try:
        # Download the image from URL
        logger.info(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Get the image bytes
        image_bytes = response.content
        
        # Process the image
        image_analysis = image_processor.process_image(image_bytes)
        
        # Convert to response format
        response = {
            "text": image_analysis.get("text", ""),
            "text_blocks": [
                {"text": block.get("text", ""), "box": block.get("box", [0, 0, 0, 0])}
                for block in image_analysis.get("text_blocks", [])
            ],
            "analysis": image_analysis.get("analysis", {})
        }
        
        return response
    except requests.RequestException as e:
        logger.error(f"Error downloading image: {str(e)}")
        raise Exception(f"Error downloading image: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing screenshot: {str(e)}")
        raise Exception(f"Error processing screenshot: {str(e)}")

@mcp.tool
def generate_post(image_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a trending Xiaohongshu post based on image analysis.
    
    Args:
        image_analysis: Image analysis data from process_screenshot
        
    Returns:
        Generated post
    """
    try:
        # Generate the post
        post = post_generator.generate_post(image_analysis)
        
        # Convert to response format
        response = {
            "title": post.get("title", ""),
            "content": post.get("content", ""),
            "hashtags": post.get("hashtags", []),
            "style": post.get("style", "general")
        }
        
        return response
    except Exception as e:
        logger.error(f"Error generating post: {str(e)}")
        raise Exception(f"Error generating post: {str(e)}")

@mcp.tool
def process_and_generate(image_url: str, user_query: str = "") -> Dict[str, Any]:
    """
    Process a screenshot and generate a trending Xiaohongshu post in one step.
    
    Args:
        image_url: URL to the image
        user_query: Optional user query to guide post generation
        
    Returns:
        OCR results and generated post
    """
    try:
        # Download the image from URL
        logger.info(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Get the image bytes
        image_bytes = response.content
        
        # Process the image
        image_analysis = image_processor.process_image(image_bytes)
        
        # Generate post with user query
        post = post_generator.generate_post(image_analysis, user_query)
        
        # Return the combined result
        # result = {
        #     "image_analysis": {
        #         "text": image_analysis.get("text", ""),
        #         "text_blocks": [
        #             {"text": block.get("text", ""), "box": block.get("box", [0, 0, 0, 0])}
        #             for block in image_analysis.get("text_blocks", [])
        #         ],
        #         "analysis": image_analysis.get("analysis", {})
        #     },
        #     "post": {
        #         "title": post.get("title", ""),
        #         "content": post.get("content", ""),
        #         "hashtags": post.get("hashtags", []),
        #         "style": post.get("style", "general")
        #     }
        # }
        result = {
            "post": {
                "title": post.get("title", ""),
                "content": post.get("content", ""),
                "hashtags": post.get("hashtags", []),
                "style": post.get("style", "general")
            }
        }
        print(result)
        return result
    except requests.RequestException as e:
        logger.error(f"Error downloading image: {str(e)}")
        raise Exception(f"Error downloading image: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing and generating: {str(e)}")
        raise Exception(f"Error processing and generating: {str(e)}")

@mcp.tool
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 10301))
    
    # Run the server
    transport = "sse" #"streamable-http"
    mcp.run(transport=transport, host="127.0.0.1", port=port)
