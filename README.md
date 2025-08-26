# Trendy Post MCP

A Model Context Protocol (MCP) service that:
1. Takes a screenshot from the user
2. Uses OCR to extract text and analyze the image
3. Generates a trending Xiaohongshu-style post based on the content

## Setup

This MCP uses the `trendy_post_mcp` conda environment with Python 3.12 and Surya OCR.

```bash
# Activate the conda environment
conda activate trendy_post_mcp

# Run the MCP server
python server.py
```

## Usage

Once the server is running, it can be used as an MCP service that provides functions for:
- Processing screenshots
- Analyzing image content
- Generating trending social media posts in the style of Xiaohongshu

## Project Structure

- `server.py`: Main MCP server implementation
- `image_processor.py`: Screenshot processing and OCR functionality
- `post_generator.py`: Xiaohongshu post generation logic
- `requirements.txt`: Python dependencies
