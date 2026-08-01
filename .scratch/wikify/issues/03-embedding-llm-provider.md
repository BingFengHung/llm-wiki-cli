# 03 — Local Embeddings & LLM Provider Subprocess

**What to build:**
Implement `wikify/embeddings.py` using `sentence-transformers` and `wikify/llm.py` wrapping `agy cli` via Python `subprocess.Popen` for LLM synthesis.

**Blocked by:** 02 — Incremental Hash Tracker & Chunker

**Status:** ready-for-agent

- [ ] `wikify/embeddings.py` generates 384-d vectors using `all-MiniLM-L6-v2`.
- [ ] `wikify/llm.py` calls `agy` via subprocess and streams response text.
- [ ] PyTest test `tests/test_llm.py` with mock subprocess passes.
