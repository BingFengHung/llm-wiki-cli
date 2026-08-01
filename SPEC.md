# System Specification: wikify (llm-wiki-cli)

## Problem Statement

Developers and knowledge workers often maintain fragmented project documentation, Markdown notes, and complex codebases across local repositories. Standard naive RAG solutions either require uploading sensitive local code to third-party cloud services, lack persistent incremental indexing (re-indexing everything on every run), lose semantic structural context (chunking blindly across function boundaries), or require running heavy vector database servers.

## Solution

`wikify` is a lightweight, local-first CLI tool inspired by Andrej Karpathy's LLM Wiki concept. It automatically digests local project files, builds an interlinked Markdown Wiki inside `.wikify/wiki/`, indexes vectors using a local C-extension (`sqlite-vec`), tracks file modifications via SHA-256 hashes for fast incremental syncs, and provides intelligent Q&A via a decoupled LLM provider interface (`agy cli`).

## User Stories

1. As a developer, I want to run `wikify sync [PATH]` in my repository so that my local code and notes are automatically parsed, summarized into a structured Wiki, and indexed into a local SQLite vector database.
2. As a developer, I want `wikify sync` to skip unchanged files based on SHA-256 hashes so that syncing is fast and efficient.
3. As a developer, I want `wikify ask "QUESTION"` to search both compiled Wiki notes and code vectors so that I receive accurate answers with precise file and line citations.
4. As a developer, I want `wikify status` to show me statistics about my knowledge base (indexed file count, total chunks, database size, and last sync timestamp).
5. As a developer, I want my project's `.agent/` skills and `.wikify/` database to be excluded from Git commits via `.gitignore` so that my repository stays clean.

## Implementation Decisions

- **CLI Framework:** Built with Python `typer` for command handling and `rich` for terminal UI (progress bars, spinners, colored outputs).
- **Storage Layer:** Local `.wikify/knowledge.db` SQLite database with the `sqlite-vec` extension for zero-server vector similarity queries.
- **Incremental Tracker:** SQLite table `file_hashes` storing `(filepath, sha256_hash, last_updated_at)` to determine diffs during `sync`.
- **Vector Embedding Engine:** Local HuggingFace `sentence-transformers` (`all-MiniLM-L6-v2`) generating 384-dimensional vector embeddings on local CPU.
- **LLM Integration:** Abstracted `LLMProvider` interface, defaulting to executing `agy cli` via Python `subprocess.Popen` for 0-cost local LLM synthesis.
- **Code & Text Chunking:** Language-aware chunking for Python (`.py`), C# (`.cs`), JavaScript/TypeScript (`.js`/`.ts`), and Markdown (`.md`).

## Testing Decisions

- Tests will focus exclusively on external behavior and non-UI logic.
- **Core Seams to Test:**
  - `HashTracker`: Correctly detects modified, new, and deleted files.
  - `Chunker`: Correctly splits code/markdown without breaking syntactic blocks.
  - `VectorDB`: Correctly initializes `sqlite-vec` virtual table, inserts vectors, and executes KNN similarity search.
- Framework: `pytest` with mock fixtures for external subprocess calls.

## Out of Scope

- Web UI or graphical user interfaces (CLI-only).
- Remote cloud vector database synchronization (100% local focus for v1).
- Multi-user authentication or ACL (single local developer tool).

## Further Notes

- `.agent/` contains Matt Pocock's development skills used during project creation.
- Initial git repository initialized and configured with GitHub remote (`https://github.com/BingFengHung/llm-wiki-cli.git`).
