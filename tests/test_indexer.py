import os
import pytest
from wikify.database import DatabaseManager
from wikify.chunker import chunk_text
from wikify.indexer import Indexer

@pytest.fixture
def temp_workspace(tmp_path):
    """Creates a temporary workspace with test files."""
    db_path = str(tmp_path / ".wikify" / "knowledge.db")
    db = DatabaseManager(db_path)
    db.init_db(vector_dim=4)
    
    # Create sample files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    file1 = src_dir / "main.py"
    file1.write_text("def hello():\n    print('Hello World')\n", encoding="utf-8")
    
    file2 = src_dir / "README.md"
    file2.write_text("# Project Title\nThis is a sample readme file.", encoding="utf-8")
    
    # Ignored directory
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("git config data", encoding="utf-8")
    
    return tmp_path, db

def test_chunker_basic_text():
    text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
    chunks = chunk_text(text, max_chunk_size=20, overlap=5)
    assert len(chunks) > 0
    assert "Line 1" in chunks[0]

def test_indexer_scan_files(temp_workspace):
    root_dir, db = temp_workspace
    indexer = Indexer(str(root_dir), db)
    
    changed_files = indexer.get_changed_files()
    relative_paths = [f["relative_path"] for f in changed_files]
    
    assert any("main.py" in p for p in relative_paths)
    assert any("README.md" in p for p in relative_paths)
    # Ensure .git/config was ignored
    assert not any(".git" in p for p in relative_paths)

def test_indexer_incremental_updates(temp_workspace):
    root_dir, db = temp_workspace
    indexer = Indexer(str(root_dir), db)
    
    # First sync
    changed_1 = indexer.get_changed_files()
    assert len(changed_1) == 2
    
    # Record hashes in DB
    for item in changed_1:
        db.set_file_hash(item["relative_path"], item["sha256"])
        
    # Second sync without file changes -> should detect 0 changed files
    changed_2 = indexer.get_changed_files()
    assert len(changed_2) == 0
    
    # Modify main.py
    main_py = root_dir / "src" / "main.py"
    main_py.write_text("def hello():\n    print('Hello Modified!')\n", encoding="utf-8")
    
    # Third sync -> should detect 1 modified file
    changed_3 = indexer.get_changed_files()
    assert len(changed_3) == 1
    assert "main.py" in changed_3[0]["relative_path"]
