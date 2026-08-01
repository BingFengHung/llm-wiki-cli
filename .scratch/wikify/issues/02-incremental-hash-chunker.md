# 02 — Incremental Hash Tracker & Chunker

**What to build:**
Implement `wikify/indexer.py` and `wikify/chunker.py`. Scans a directory, ignores files per `.gitignore` and extension whitelist, computes SHA-256 hashes to detect modified files, and splits code/markdown into structural chunks.

**Blocked by:** 01 — SQLite Vector DB Infrastructure

**Status:** done

- [x] `wikify/indexer.py` scans directory and checks SHA-256 against DB.
- [x] `wikify/chunker.py` splits `.py`, `.cs`, `.js`, `.md` into semantic chunks.
- [x] PyTest test `tests/test_indexer.py` passes.
