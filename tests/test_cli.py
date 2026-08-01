import os
import pytest
from typer.testing import CliRunner
from unittest.mock import patch
from wikify.cli import app

runner = CliRunner()

@pytest.fixture
def temp_project(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    code_file = src / "app.py"
    code_file.write_text("def run():\n    print('Running App')\n", encoding="utf-8")
    return tmp_path

def test_cli_status_command(temp_project):
    result = runner.invoke(app, ["status", "--path", str(temp_project)])
    assert result.exit_code == 0
    assert "wikify Knowledge Base Status" in result.output or "Status" in result.output

def test_cli_sync_command(temp_project):
    with patch("wikify.cli.EmbeddingEngine") as MockEmbeddingEngine, \
         patch("wikify.cli.LLMProvider") as MockLLMProvider:
        
        mock_embed_instance = MockEmbeddingEngine.return_value
        mock_embed_instance.embed_text.return_value = [0.1] * 384
        
        mock_llm_instance = MockLLMProvider.return_value
        mock_llm_instance.generate.return_value = "# Wiki Summary\nApp description."
        
        result = runner.invoke(app, ["sync", "--path", str(temp_project)])
        assert result.exit_code == 0
        assert "Sync Completed" in result.output or "Synced" in result.output

def test_cli_ask_command(temp_project):
    with patch("wikify.cli.EmbeddingEngine") as MockEmbeddingEngine, \
         patch("wikify.cli.LLMProvider") as MockLLMProvider:
        
        mock_embed_instance = MockEmbeddingEngine.return_value
        mock_embed_instance.embed_text.return_value = [0.1] * 384
        
        mock_llm_instance = MockLLMProvider.return_value
        mock_llm_instance.generate.return_value = "The app prints 'Running App'."
        
        # Run sync first to initialize knowledge.db
        runner.invoke(app, ["sync", "--path", str(temp_project)])
        
        result = runner.invoke(app, ["ask", "How does app work?", "--path", str(temp_project)])
        assert result.exit_code == 0
        assert "The app prints" in result.output or "wikify AI Answer" in result.output
