# 04 — CLI Commands Engine

**What to build:**
Implement `wikify/cli.py` using `typer` and `rich`. Expose `wikify sync [PATH]`, `wikify ask "QUESTION"`, and `wikify status` commands.

**Blocked by:** 03 — Local Embeddings & LLM Provider Subprocess

**Status:** done

- [x] `wikify sync` command runs end-to-end indexing, wiki compiling, and vector storage.
- [x] `wikify ask` command executes hybrid vector search and streams LLM answer with source citations.
- [x] `wikify status` displays formatted knowledge base statistics.
- [x] PyTest CLI integration tests pass.
