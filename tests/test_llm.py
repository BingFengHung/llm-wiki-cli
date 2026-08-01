import pytest
from unittest.mock import patch, MagicMock
from wikify.embeddings import EmbeddingEngine
from wikify.llm import LLMProvider

def test_embedding_engine_shape():
    engine = EmbeddingEngine()
    vector = engine.embed_text("Test sentence for embedding")
    assert isinstance(vector, list)
    assert len(vector) == 384  # all-MiniLM-L6-v2 dimension

def test_llm_provider_subprocess_mock():
    provider = LLMProvider()
    
    with patch("subprocess.Popen") as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Mocked LLM Response text", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        response = provider.generate("Summarize this code")
        assert "Mocked LLM Response" in response
