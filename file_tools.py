import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

try:
    from PyPDF2 import PdfReader
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


def read_file(filepath: str) -> Dict[str, Any]:
    try:
        path = Path(filepath)
        if not path.exists():
            return {"success": False, "content": None, "metadata": None, "error": f"Path not found: {filepath}"}

        file_stats = path.stat()
        meta = {
            "filename": path.name,
            "full_path": str(path.absolute()),
            "size": file_stats.st_size,
            "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }

        content = None
        ftype = path.suffix.lower()

        if ftype == ".txt":
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif ftype == ".pdf":
            if not HAS_PDF:
                return {"success": False, "content": None, "metadata": meta, "error": "PyPDF2 not installed"}
            try:
                with open(path, 'rb') as f:
                    reader = PdfReader(f)
                    pages = [page.extract_text() for page in reader.pages]
                    content = '\n'.join(pages)
            except Exception as e:
                return {"success": False, "content": None, "metadata": meta, "error": f"PDF read error: {str(e)}"}
        elif ftype == ".docx":
            if not HAS_DOCX:
                return {"success": False, "content": None, "metadata": meta, "error": "python-docx not installed"}
            try:
                doc = Document(path)
                paragraphs = [p.text for p in doc.paragraphs]
                content = '\n'.join(paragraphs)
            except Exception as e:
                return {"success": False, "content": None, "metadata": meta, "error": f"DOCX read error: {str(e)}"}
        else:
            return {"success": False, "content": None, "metadata": meta, "error": f"Format not supported: {ftype}"}

        return {"success": True, "content": content, "metadata": meta, "error": None}
    except Exception as e:
        return {"success": False, "content": None, "metadata": None, "error": str(e)}


def list_files(directory: str, extension: Optional[str] = None) -> Dict[str, Any]:
    try:
        dirpath = Path(directory)
        if not dirpath.exists():
            return {"success": False, "files": [], "total": 0, "directory": directory, "error": f"Directory not found"}
        if not dirpath.is_dir():
            return {"success": False, "files": [], "total": 0, "directory": directory, "error": f"Not a directory"}

        file_list = []
        for item in dirpath.iterdir():
            if item.is_file():
                if extension and item.suffix.lower() != extension.lower():
                    continue
                stats = item.stat()
                file_list.append({
                    "filename": item.name,
                    "path": str(item.absolute()),
                    "bytes": stats.st_size,
                    "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    "extension": item.suffix.lower()
                })

        file_list.sort(key=lambda x: x['filename'])
        return {"success": True, "files": file_list, "total": len(file_list), "directory": str(dirpath.absolute()), "error": None}
    except Exception as e:
        return {"success": False, "files": [], "total": 0, "directory": directory, "error": str(e)}


def write_file(filepath: str, content: str) -> Dict[str, Any]:
    try:
        fpath = Path(filepath)
        fpath.parent.mkdir(parents=True, exist_ok=True)

        with open(fpath, 'w', encoding='utf-8') as f:
            written = f.write(content)

        return {
            "success": True,
            "filepath": str(fpath.absolute()),
            "bytes_written": written,
            "error": None
        }
    except Exception as e:
        return {"success": False, "filepath": filepath, "bytes_written": 0, "error": str(e)}


def search_in_file(filepath: str, keyword: str) -> Dict[str, Any]:
    try:
        path = Path(filepath)
        if not path.exists():
            return {"success": False, "keyword": keyword, "count": 0, "results": [], "error": f"File not found"}

        file_data = read_file(filepath)
        if not file_data['success']:
            return {"success": False, "keyword": keyword, "count": 0, "results": [], "error": file_data['error']}

        text = file_data['content']
        search_term = keyword.lower()
        results = []

        for idx, line in enumerate(text.split('\n'), 1):
            if search_term in line.lower():
                results.append({
                    "line": idx,
                    "text": line.strip(),
                    "char_pos": line.lower().find(search_term)
                })

        return {"success": True, "keyword": keyword, "count": len(results), "results": results, "error": None}
    except Exception as e:
        return {"success": False, "keyword": keyword, "count": 0, "results": [], "error": str(e)}


TOOLS = [
    {
        "name": "read_file",
        "description": "Read file content from TXT, PDF, or DOCX",
        "input_schema": {
            "type": "object",
            "properties": {"filepath": {"type": "string"}},
            "required": ["filepath"]
        }
    },
    {
        "name": "list_files",
        "description": "List files in directory with optional extension filter",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string"},
                "extension": {"type": "string"}
            },
            "required": ["directory"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["filepath", "content"]
        }
    },
    {
        "name": "search_in_file",
        "description": "Search for keyword in file",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string"},
                "keyword": {"type": "string"}
            },
            "required": ["filepath", "keyword"]
        }
    }
]

