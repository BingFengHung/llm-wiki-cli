# 01 — SQLite Vector DB Infrastructure

**What to build:**
Initialize the Python package structure (`pyproject.toml`) and implement the SQLite database module (`wikify/database.py`) with `sqlite-vec` C-extension support. It creates tables for file hashes, wiki pages, and 384-dimensional vector embeddings.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] `pyproject.toml` is created with dependencies (`sqlite-vec`, `sentence-transformers`, `typer`, `rich`, `pytest`).
- [x] `wikify/database.py` connects to SQLite and enables `sqlite-vec` extension.
- [x] `file_hashes` table created: `(filepath TEXT PRIMARY KEY, sha256 TEXT, updated_at TIMESTAMP)`.
- [x] `vec_embeddings` virtual table created using `sqlite-vec`.
- [x] PyTest test `tests/test_database.py` passes.
