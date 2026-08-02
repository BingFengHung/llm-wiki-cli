import os
import hashlib
from typing import List, Dict, Any
from wikify.database import DatabaseManager

DEFAULT_ALLOWED_EXTENSIONS = {
    ".md", ".txt", ".py", ".cs", ".js", ".ts", ".jsx", ".tsx", ".json", ".yaml", ".yml", ".ipynb", ".sql"
}

DEFAULT_IGNORED_DIRS = {
    ".git", ".wikify", ".agent", ".claude", "node_modules", "venv", ".venv",
    "bin", "obj", "__pycache__", ".scratch", "dist", "build"
}

class Indexer:
    """Scans directories, filters files, computes SHA-256 hashes, and detects diffs."""
    
    def __init__(self, root_dir: str, db: DatabaseManager, allowed_extensions=None, ignored_dirs=None):
        self.root_dir = os.path.abspath(root_dir)
        self.db = db
        self.allowed_extensions = allowed_extensions or DEFAULT_ALLOWED_EXTENSIONS
        self.ignored_dirs = ignored_dirs or DEFAULT_IGNORED_DIRS

    @staticmethod
    def calculate_sha256(filepath: str) -> str:
        """Computes SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def should_ignore(self, path: str) -> bool:
        """Determines if a directory or file should be ignored."""
        parts = os.path.normpath(path).split(os.sep)
        for part in parts:
            if part in self.ignored_dirs:
                return True
        return False

    def get_changed_files(self) -> List[Dict[str, Any]]:
        """
        Scans the root_dir for allowed files, compares SHA-256 hashes with the database,
        and returns a list of modified/new files.
        """
        changed_files = []
        
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            # Modify dirnames in-place to skip ignored directories
            dirnames[:] = [d for d in dirnames if not self.should_ignore(os.path.join(dirpath, d))]
            
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in self.allowed_extensions:
                    continue
                    
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, self.root_dir).replace("\\", "/")
                
                if self.should_ignore(rel_path):
                    continue
                    
                try:
                    current_hash = self.calculate_sha256(full_path)
                    stored_hash = self.db.get_file_hash(rel_path)
                    
                    if stored_hash != current_hash:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            raw_content = f.read()
                            
                        # Clean Jupyter Notebook JSON if .ipynb
                        if ext == ".ipynb":
                            try:
                                import json
                                nb_data = json.loads(raw_content)
                                cell_texts = []
                                for cell in nb_data.get("cells", []):
                                    if cell.get("cell_type") in ("code", "markdown"):
                                        source = "".join(cell.get("source", []))
                                        if source.strip():
                                            cell_texts.append(source)
                                content = "\n\n".join(cell_texts)
                            except Exception:
                                content = raw_content
                        else:
                            content = raw_content
                            
                        changed_files.append({
                            "absolute_path": full_path,
                            "relative_path": rel_path,
                            "sha256": current_hash,
                            "content": content
                        })
                except Exception as e:
                    # Skip unreadable files safely
                    continue
                    
        return changed_files
