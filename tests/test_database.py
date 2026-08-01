import os
import pytest
import sqlite3
import struct
from wikify.database import DatabaseManager

@pytest.fixture
def temp_db_path(tmp_path):
    db_file = tmp_path / "test_knowledge.db"
    return str(db_file)

def serialize_float_list(vector: list[float]) -> bytes:
    """Helper to convert float list to float32 binary format for sqlite-vec."""
    return struct.pack(f"{len(vector)}f", *vector)

def test_init_db_creates_tables(temp_db_path):
    db = DatabaseManager(temp_db_path)
    db.init_db()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Check file_hashes table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='file_hashes';")
        assert cursor.fetchone() is not None
        
        # Check wiki_pages table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_pages';")
        assert cursor.fetchone() is not None

def test_file_hash_operations(temp_db_path):
    db = DatabaseManager(temp_db_path)
    db.init_db()
    
    # Test setting hash
    db.set_file_hash("src/main.py", "hash123")
    assert db.get_file_hash("src/main.py") == "hash123"
    
    # Test updating hash
    db.set_file_hash("src/main.py", "hash456")
    assert db.get_file_hash("src/main.py") == "hash456"
    
    # Test non-existent file
    assert db.get_file_hash("nonexistent.py") is None

def test_vector_storage_and_query(temp_db_path):
    db = DatabaseManager(temp_db_path)
    db.init_db(vector_dim=4)
    
    # Create dummy 4-dimensional vectors for testing
    v1 = [1.0, 0.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0, 0.0]
    
    db.save_chunk("chunk_1", "src/auth.py", "def login(): pass", v1)
    db.save_chunk("chunk_2", "src/db.py", "def connect(): pass", v2)
    
    # Query with vector close to v1
    query_vec = [0.9, 0.1, 0.0, 0.0]
    results = db.search_similar_chunks(query_vec, top_k=1)
    
    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk_1"
    assert results[0]["filepath"] == "src/auth.py"
