# Trendy Post MCP 🚀✨

A Model Context Protocol (MCP) service that:
1. Takes a screenshot from the user 📸
2. Uses OCR to extract text and analyze the image 🔍
3. Generates a trending Xiaohongshu-style post based on the content 📱💬

## Features ✨

- **Image Processing** 🖼️: Extract text and analyze images
- **Content Generation** 📝: Create engaging Xiaohongshu-style posts
- **LLM Integration** 🧠: Uses AI to generate post styles, hashtags, and titles
- **MCP Compatibility** 🔌: Works with any MCP client

## Setup 🛠️

This MCP uses the `trendy_post_mcp` conda environment with Python 3.12 and Surya OCR.

```bash
# Activate the conda environment
conda activate trendy_post_mcp

# Run the MCP server
python server.py
```

## Usage 📋

Once the server is running, it can be used as an MCP service that provides functions for:
- Processing screenshots 📸
- Analyzing image content 🔍
- Generating trending social media posts in the style of Xiaohongshu 📱

### MCP Functions

The server exposes the following MCP functions:

- `process_screenshot`: Extract text from an image URL 🔤
- `generate_post`: Create a Xiaohongshu post from image analysis data ✍️
- `process_and_generate`: Combine both functions in one step (recommended) 🔄
- `health_check`: Check if the server is running properly 🩺

## Project Structure 📁

- `server.py`: Main MCP server implementation
- `image_processor.py`: Screenshot processing and OCR functionality
- `post_generator.py`: Xiaohongshu post generation logic
- `requirements.txt`: Python dependencies

## Dependencies 📦

### OCR Engine

This project uses [Surya OCR](https://github.com/VikParuchuri/surya) for text extraction, which is licensed under the **GPL-3.0 License**. Surya is a powerful OCR engine that supports multiple languages and provides excellent results for complex layouts.

⚠️ **Important License Note**: As Surya is licensed under GPL-3.0, any distribution of this software must comply with the GPL-3.0 license terms. Please ensure you understand these terms if you plan to distribute or modify this software.

### Other Dependencies

- FastMCP: For MCP server implementation
- Pydantic: For data validation
- Pillow: For image processing
- ZhipuAI: For LLM-based content generation

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.
(Note: Components like Surya OCR have their own licenses as mentioned above)
