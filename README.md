# wikify (llm-wiki-cli) 🚀

> An autonomous CLI Agent that compiles local code bases and notes into an interlinked, searchable LLM Wiki powered by SQLite vector search and local AI models.

Inspired by Andrej Karpathy's **LLM Wiki** concept.

## 🌟 Key Features
- **Incremental Indexing:** SHA-256 hash tracking ensures fast updates by re-indexing only modified files.
- **SQLite Vector Search:** High-performance vector similarity search using `sqlite-vec`.
- **Zero API Cost:** Leverages local embedding models (`sentence-transformers`) and local LLM execution.
- **Developer-Centric CLI:** Beautiful terminal output with `rich` and `typer`.

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **CLI Framework:** Typer + Rich
- **Vector DB:** SQLite3 + `sqlite-vec` extension
- **Embedding Model:** `sentence-transformers` (`all-MiniLM-L6-v2`)
- **LLM Provider:** `LLMProvider` abstraction (defaulting to `agy cli`)

## ⚡ Quick Start
*Coming soon as we implement the specification.*

## 📄 License
MIT
