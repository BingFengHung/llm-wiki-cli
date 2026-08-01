import os
import sqlite3
import struct
from typing import List, Dict, Any, Optional

try:
    import sqlite_vec
    HAS_SQLITE_VEC = True
except ImportError:
    HAS_SQLITE_VEC = False

class DatabaseManager:
    """Manages SQLite database connections, tables, hashes, and vector operations via sqlite-vec."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.enable_load_extension(True)
        if HAS_SQLITE_VEC:
            sqlite_vec.load(conn)
        return conn

    def init_db(self, vector_dim: int = 384):
        """Initializes database tables and vector index."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # File hash tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_hashes (
                    filepath TEXT PRIMARY KEY,
                    sha256 TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Wiki Pages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wiki_pages (
                    title TEXT PRIMARY KEY,
                    filepath TEXT NOT NULL,
                    content TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Text Chunks Metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    filepath TEXT NOT NULL,
                    content TEXT NOT NULL
                );
            """)

            # Vector Search Virtual Table using sqlite-vec
            # Drop if dimension changed, or create if not exists
            if HAS_SQLITE_VEC:
                cursor.execute(f"""
                    CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0(
                        chunk_id TEXT PRIMARY KEY,
                        embedding float[{vector_dim}]
                    );
                """)
            conn.commit()

    def get_file_hash(self, filepath: str) -> Optional[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sha256 FROM file_hashes WHERE filepath = ?;", (filepath,))
            row = cursor.fetchone()
            return row["sha256"] if row else None

    def set_file_hash(self, filepath: str, sha256: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO file_hashes (filepath, sha256, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(filepath) DO UPDATE SET
                    sha256 = excluded.sha256,
                    updated_at = CURRENT_TIMESTAMP;
            """, (filepath, sha256))
            conn.commit()

    def save_chunk(self, chunk_id: str, filepath: str, content: str, embedding: List[float]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Save metadata
            cursor.execute("""
                INSERT OR REPLACE INTO chunks (chunk_id, filepath, content)
                VALUES (?, ?, ?);
            """, (chunk_id, filepath, content))
            
            # Save vector embedding
            if HAS_SQLITE_VEC:
                vec_blob = struct.pack(f"{len(embedding)}f", *embedding)
                cursor.execute("""
                    INSERT OR REPLACE INTO vec_chunks (chunk_id, embedding)
                    VALUES (?, ?);
                """, (chunk_id, vec_blob))
            conn.commit()

    def search_similar_chunks(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if not HAS_SQLITE_VEC:
                return []

            vec_blob = struct.pack(f"{len(query_embedding)}f", *query_embedding)
            
            cursor.execute("""
                SELECT
                    c.chunk_id,
                    c.filepath,
                    c.content,
                    v.distance
                FROM vec_chunks v
                JOIN chunks c ON c.chunk_id = v.chunk_id
                WHERE v.embedding MATCH ?
                  AND k = ?
                ORDER BY v.distance ASC;
            """, (vec_blob, top_k))
            
            rows = cursor.fetchall()
            return [
                {
                    "chunk_id": row["chunk_id"],
                    "filepath": row["filepath"],
                    "content": row["content"],
                    "distance": row["distance"]
                }
                for row in rows
            ]
