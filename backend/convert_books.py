import os
import json
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from typing import List, Dict

def split_into_chunks(text: str, max_chunk_size: int = 512) -> List[str]:
    """Split text into chunks of approximately max_chunk_size characters."""
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
    """Convert text to AWS Lambda documentation style"""
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