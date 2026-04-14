"""
Docling MCP Server for AutoAgent-TW
Exposes document conversion capabilities (PDF, Docx, etc.) to AI agents.
"""

import os
import sys
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("docling")

try:
    from docling.document_converter import DocumentConverter
    CONVERTER = DocumentConverter()
except ImportError:
    CONVERTER = None
    print("Warning: 'docling' package not found. Please run 'pip install docling'.", file=sys.stderr)

@mcp.tool()
def convert_document(file_path: str) -> str:
    """
    Convert a document (PDF, Docx, PPTX, HTML) to Markdown.
    
    Args:
        file_path: The absolute or relative path to the document file.
    """
    if not CONVERTER:
        return "Error: Docling is not installed on the system. Please run 'pip install docling'."
    
    # Resolve absolute path
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(abs_path):
        return f"Error: File not found at {abs_path}"

    try:
        result = CONVERTER.convert(abs_path)
        # Export to markdown by default
        return result.document.export_to_markdown()
    except Exception as e:
        return f"Error during conversion: {str(e)}"

if __name__ == "__main__":
    mcp.run()
