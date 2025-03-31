"""
Game of Thrones Book Conversion Utility

This module processes Game of Thrones EPUB books into multiple formats:
1. Plain markdown files for easy reading
2. Lambda-style documentation markdown for structured search
3. JSON files containing chunked content for vector-based RAG retrieval

The processing pipeline handles:
- EPUB parsing and text extraction
- Content cleaning and formatting
- Text chunking for optimal retrieval
- Metadata preservation
- Structured output for downstream use

Usage:
    python convert_books.py

Environment:
    Input EPUB files should be placed in the 'input' directory.
    Output will be generated in 'output/{format}' directories.
"""

import os
import json
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from typing import List, Dict

def split_into_chunks(text: str, max_chunk_size: int = 512) -> List[str]:
    """
    Split text into semantically meaningful chunks for RAG processing.
    
    This function breaks text into chunks of approximately max_chunk_size
    characters, attempting to preserve paragraph boundaries for context.
    
    Args:
        text: The input text to be chunked
        max_chunk_size: Maximum target size for each chunk
        
    Returns:
        A list of text chunks suitable for embedding and retrieval
    """
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for paragraph in paragraphs:
        if len(paragraph.strip()) == 0:
            continue
            
        if current_length + len(paragraph) > max_chunk_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_length = len(paragraph)
        else:
            current_chunk.append(paragraph)
            current_length += len(paragraph)
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def create_lambda_style_markdown(text: str, title: str) -> str:
    """
    Convert text to AWS Lambda documentation style markdown.
    
    This creates a structured markdown document following AWS documentation
    patterns, which includes a clear hierarchy of sections with proper
    heading levels. This format is optimized for documentation systems.
    
    Args:
        text: The raw text content to format
        title: The title of the document
        
    Returns:
        Formatted markdown text in Lambda documentation style
    """
    lambda_doc = [
        f"# {title}",
        "",
        "## Overview",
        f"This document contains the content of {title}.",
        "",
        "## Contents",
        "",
    ]
    
    sections = text.split('\n\n')
    current_section = "Main Content"
    
    for section in sections:
        if section.strip().startswith('#'):
            current_section = section.strip('# \n')
            lambda_doc.append(f"### {current_section}")
            lambda_doc.append("")
        else:
            lambda_doc.append(section)
            lambda_doc.append("")
    
    return '\n'.join(lambda_doc)

def epub_to_all_formats(epub_path: str, book_markdown_dir: str, lambda_markdown_dir: str, rag_dir: str):
    """
    Convert a single EPUB file to all target formats.
    
    This function:
    1. Parses an EPUB file
    2. Extracts and cleans the text content
    3. Creates a standard markdown version
    4. Creates a Lambda-style documentation version
    5. Generates chunked content for RAG with metadata
    
    Args:
        epub_path: Path to the EPUB file
        book_markdown_dir: Output directory for standard markdown
        lambda_markdown_dir: Output directory for Lambda-style markdown
        rag_dir: Output directory for RAG chunks JSON
        
    Returns:
        Tuple containing paths to the generated files, or None values if conversion failed
    """
    try:
        book = epub.read_epub(epub_path)
        title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else os.path.basename(epub_path)
        
        # Prepare content
        book_content = [f'# {title}\n\n']
        rag_chunks = []
        current_chapter = "Introduction"
        chunk_index = 0
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                
                # Try to identify chapter title
                chapter_header = soup.find(['h1', 'h2', 'h3'])
                if chapter_header:
                    current_chapter = chapter_header.get_text().strip()
                
                # Extract and clean text
                text = soup.get_text()
                text = re.sub(r'\n\s*\n', '\n\n', text)
                text = re.sub(r' +', ' ', text)
                
                book_content.append(text)
                
                # Create RAG chunks
                chunks = split_into_chunks(text)
                for chunk in chunks:
                    if chunk.strip():
                        chunk_doc = {
                            "content": chunk.strip(),
                            "metadata": {
                                "book_title": title,
                                "source": os.path.basename(epub_path),
                                "chapter": current_chapter,
                                "chunk_index": chunk_index
                            }
                        }
                        rag_chunks.append(chunk_doc)
                        chunk_index += 1
        
        # Combine all content
        full_content = '\n'.join(book_content)
        
        # Save book markdown
        book_filename = os.path.join(
            book_markdown_dir, 
            f"{os.path.splitext(os.path.basename(epub_path))[0]}.md"
        )
        with open(book_filename, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        # Save Lambda-style markdown
        lambda_content = create_lambda_style_markdown(full_content, title)
        lambda_filename = os.path.join(
            lambda_markdown_dir,
            f"{os.path.splitext(os.path.basename(epub_path))[0]}_lambda.md"
        )
        with open(lambda_filename, 'w', encoding='utf-8') as f:
            f.write(lambda_content)
        
        # Save RAG chunks
        rag_filename = os.path.join(
            rag_dir,
            f"{os.path.splitext(os.path.basename(epub_path))[0]}_rag.json"
        )
        with open(rag_filename, 'w', encoding='utf-8') as f:
            json.dump({
                "book_title": title,
                "chunks": rag_chunks,
                "total_chunks": len(rag_chunks)
            }, f, indent=2)
        
        print(f"Successfully converted: {os.path.basename(epub_path)}")
        print(f"  - Created {len(rag_chunks)} RAG chunks")
        return book_filename, lambda_filename, rag_filename
    
    except Exception as e:
        print(f"Error converting {os.path.basename(epub_path)}: {str(e)}")
        return None, None, None

def convert_folder(input_folder: str, book_markdown_dir: str, lambda_markdown_dir: str, rag_dir: str):
    """
    Process all EPUB files in a directory, converting each to all target formats.
    
    This function creates the necessary output directories and processes
    each EPUB file in the input folder.
    
    Args:
        input_folder: Directory containing EPUB files to process
        book_markdown_dir: Output directory for standard markdown
        lambda_markdown_dir: Output directory for Lambda-style markdown
        rag_dir: Output directory for RAG chunks JSON
        
    Returns:
        List of tuples, each containing the output paths for a successfully converted book
    """
    # Create output folders if they don't exist
    os.makedirs(book_markdown_dir, exist_ok=True)
    os.makedirs(lambda_markdown_dir, exist_ok=True)
    os.makedirs(rag_dir, exist_ok=True)
    
    converted_files = []
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.epub'):
            input_path = os.path.join(input_folder, filename)
            results = epub_to_all_formats(
                input_path, 
                book_markdown_dir, 
                lambda_markdown_dir,
                rag_dir
            )
            if all(results):
                converted_files.append(results)
    
    return converted_files

if __name__ == "__main__":
    """
    Main execution block for the book conversion utility.
    
    This sets up the directory paths relative to the script location and
    executes the conversion process for all EPUB files found in the input directory.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    INPUT_FOLDER = os.path.join(current_dir, "input")
    BOOK_MARKDOWN_DIR = os.path.join(current_dir, "output", "book_markdown")
    LAMBDA_MARKDOWN_DIR = os.path.join(current_dir, "output", "lambda_markdown")
    RAG_DIR = os.path.join(current_dir, "output", "rag_chunks")
    
    print(f"Starting conversion of EPUB files from {INPUT_FOLDER}")
    converted = convert_folder(INPUT_FOLDER, BOOK_MARKDOWN_DIR, LAMBDA_MARKDOWN_DIR, RAG_DIR)
    print(f"\nConverted {len(converted)} files successfully!")
    print(f"Output files are in:")
    print(f"  Book Markdown: {BOOK_MARKDOWN_DIR}")
    print(f"  Lambda Docs: {LAMBDA_MARKDOWN_DIR}")
    print(f"  RAG Chunks: {RAG_DIR}")