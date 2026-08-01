import os
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.markdown import Markdown
from typing import Optional

from wikify.database import DatabaseManager
from wikify.indexer import Indexer
from wikify.chunker import chunk_text
from wikify.embeddings import EmbeddingEngine
from wikify.llm import LLMProvider

app = typer.Typer(
    name="wikify",
    help="Autonomous CLI Agent compiling local codebases and notes into an interlinked LLM Wiki.",
    add_completion=False
)

console = Console()

def get_db_path(target_path: str) -> str:
    return os.path.join(os.path.abspath(target_path), ".wikify", "knowledge.db")

def get_wiki_dir(target_path: str) -> str:
    wiki_dir = os.path.join(os.path.abspath(target_path), ".wikify", "wiki")
    os.makedirs(wiki_dir, exist_ok=True)
    return wiki_dir

@app.command()
def sync(
    path: str = typer.Option(".", "--path", "-p", help="Target project directory path to sync")
):
    """Scan local directory, build incremental Wiki markdown files, and index vector embeddings."""
    abs_path = os.path.abspath(path)
    console.print(f"[bold cyan]🔍 Scanning repository at:[/bold cyan] {abs_path}")
    
    db_path = get_db_path(abs_path)
    wiki_dir = get_wiki_dir(abs_path)
    
    db = DatabaseManager(db_path)
    db.init_db()
    
    indexer = Indexer(abs_path, db)
    changed_files = indexer.get_changed_files()
    
    if not changed_files:
        console.print("[bold green]✨ Everything up to date! 0 files changed.[/bold green]")
        return

    console.print(f"[bold yellow]📦 Found {len(changed_files)} new/modified files to index.[/bold yellow]")
    
    embedding_engine = EmbeddingEngine()
    llm_provider = LLMProvider()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Indexing & Compiling Wiki...", total=len(changed_files))
        
        for item in changed_files:
            rel_path = item["relative_path"]
            content = item["content"]
            sha256 = item["sha256"]
            
            progress.update(task, description=f"Processing {rel_path}...")
            
            # 1. Chunk content
            chunks = chunk_text(content, max_chunk_size=500, overlap=50)
            for idx, chunk in enumerate(chunks):
                chunk_id = f"{rel_path}#chunk-{idx}"
                vector = embedding_engine.embed_text(chunk)
                db.save_chunk(chunk_id, rel_path, chunk, vector)
                
            # 2. Update SHA256 hash in DB
            db.set_file_hash(rel_path, sha256)
            
            # 3. Generate Wiki Markdown Page
            wiki_filename = rel_path.replace("/", "_").replace("\\", "_") + ".md"
            wiki_file_path = os.path.join(wiki_dir, wiki_filename)
            
            prompt = f"Analyze the following code/text file from '{rel_path}' and generate a structured Markdown wiki entry summary:\n\n{content[:2000]}"
            wiki_summary = llm_provider.generate(prompt)
            
            with open(wiki_file_path, "w", encoding="utf-8") as f:
                f.write(f"# Wiki Entry: {rel_path}\n\n{wiki_summary}\n")
                
            progress.advance(task)
            
    console.print(f"[bold green]✅ Sync Completed! Processed {len(changed_files)} files.[/bold green]")

@app.command()
def ask(
    question: str = typer.Argument(..., help="The question to ask your codebase knowledge base"),
    path: str = typer.Option(".", "--path", "-p", help="Target project directory path")
):
    """Query your local code & wiki knowledge base with AI synthesis."""
    abs_path = os.path.abspath(path)
    db_path = get_db_path(abs_path)
    
    if not os.path.exists(db_path):
        console.print("[bold red]❌ No knowledge base found. Please run 'wikify sync' first.[/bold red]")
        raise typer.Exit(code=1)
        
    db = DatabaseManager(db_path)
    db.init_db()
    
    console.print(f"[bold cyan]🔍 Querying knowledge base for:[/bold cyan] '{question}'")
    
    embedding_engine = EmbeddingEngine()
    llm_provider = LLMProvider()
    
    query_vector = embedding_engine.embed_text(question)
    results = db.search_similar_chunks(query_vector, top_k=3)
    
    if not results:
        console.print("[bold yellow]⚠️ No relevant context found in database.[/bold yellow]")
        return
        
    context_str = ""
    citations = []
    for res in results:
        context_str += f"\n--- Source: {res['filepath']} ---\n{res['content']}\n"
        citations.append(res['filepath'])
        
    prompt = f"Answer the following question based on the provided codebase context.\n\nContext:\n{context_str}\n\nQuestion: {question}"
    answer = llm_provider.generate(prompt)
    
    console.print(Panel(Markdown(answer), title="[bold green]🤖 wikify AI Answer[/bold green]", expand=False))
    
    table = Table(title="📌 Relevant Citations", show_header=True, header_style="bold magenta")
    table.add_column("Filepath", style="cyan")
    table.add_column("Similarity Score (Distance)", style="green")
    
    for res in results:
        table.add_row(res["filepath"], f"{res['distance']:.4f}")
        
    console.print(table)

@app.command()
def status(
    path: str = typer.Option(".", "--path", "-p", help="Target project directory path")
):
    """View knowledge base status and statistics."""
    abs_path = os.path.abspath(path)
    db_path = get_db_path(abs_path)
    wiki_dir = get_wiki_dir(abs_path)
    
    table = Table(title=f"📊 wikify Knowledge Base Status ({abs_path})")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    if not os.path.exists(db_path):
        table.add_row("Status", "[bold red]Not Initialized[/bold red]")
        table.add_row("Database File", "Missing")
    else:
        db = DatabaseManager(db_path)
        db.init_db()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM file_hashes;")
            files_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM chunks;")
            chunks_count = cursor.fetchone()[0]
            
        wiki_files = len(os.listdir(wiki_dir)) if os.path.exists(wiki_dir) else 0
        db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
        
        table.add_row("Status", "[bold green]Active[/bold green]")
        table.add_row("Indexed Files", str(files_count))
        table.add_row("Total Code Chunks", str(chunks_count))
        table.add_row("Compiled Wiki Pages", str(wiki_files))
        table.add_row("Database Size", f"{db_size_mb:.2f} MB")
        
    console.print(table)

if __name__ == "__main__":
    app()
