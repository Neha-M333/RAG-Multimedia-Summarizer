"""
Comprehensive test suite for AI Summarization System
Run: pytest tests/test_system.py -v
"""
import pytest
import os
import sys
from pathlib import Path
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.document_processor import DocumentProcessor
from backend.database_manager import DatabaseManager
from backend.rag_engine import RAGEngine
from backend.translator import Translator
from utils.config import Config
from utils.helpers import *

# Test Configuration
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DB_DIR = Path(__file__).parent / "test_db"

@pytest.fixture(scope="session")
def setup_test_env():
    """Setup test environment"""
    TEST_DATA_DIR.mkdir(exist_ok=True)
    TEST_DB_DIR.mkdir(exist_ok=True)
    yield
    # Cleanup after tests
    import shutil
    if TEST_DB_DIR.exists():
        shutil.rmtree(TEST_DB_DIR)

@pytest.fixture
def document_processor():
    """Create DocumentProcessor instance"""
    return DocumentProcessor()

@pytest.fixture
def database_manager():
    """Create DatabaseManager instance"""
    sqlite_db = TEST_DB_DIR / "test.db"
    chromadb_dir = TEST_DB_DIR / "chromadb"
    return DatabaseManager(str(sqlite_db), str(chromadb_dir))

@pytest.fixture
def rag_engine():
    """Create RAGEngine instance"""
    api_key = os.getenv("OPENAI_API_KEY", "test-key")
    return RAGEngine(api_key)

@pytest.fixture
def translator():
    """Create Translator instance"""
    api_key = os.getenv("OPENAI_API_KEY")
    return Translator(api_key)

# ============== Helper Functions Tests ==============

class TestHelpers:
    def test_format_file_size(self):
        assert format_file_size(1024) == "1.00 KB"
        assert format_file_size(1048576) == "1.00 MB"
        assert format_file_size(1073741824) == "1.00 GB"
    
    def test_validate_file_type(self):
        assert validate_file_type("test.pdf", ['.pdf', '.txt'])
        assert not validate_file_type("test.exe", ['.pdf', '.txt'])
    
    def test_clean_text(self):
        text = "  Hello   World  "
        assert clean_text(text) == "Hello World"
    
    def test_truncate_text(self):
        text = "This is a very long text that needs truncation"
        result = truncate_text(text, max_length=20)
        assert len(result) <= 20
        assert result.endswith("...")
    
    def test_count_words(self):
        text = "This is a test sentence"
        assert count_words(text) == 5
    
    def test_count_sentences(self):
        text = "First sentence. Second sentence! Third sentence?"
        assert count_sentences(text) == 3
    
    def test_estimate_reading_time(self):
        text = " ".join(["word"] * 200)  # 200 words
        time = estimate_reading_time(text, words_per_minute=200)
        assert "1 minute" in time or "< 1 minute" in time
    
    def test_generate_summary_stats(self):
        text = "This is a test. It has words."
        stats = generate_summary_stats(text)
        assert 'word_count' in stats
        assert 'sentence_count' in stats
        assert 'character_count' in stats
        assert 'reading_time' in stats

class TestTextPreprocessor:
    def test_remove_extra_spaces(self):
        text = "Hello    World"
        result = TextPreprocessor.remove_extra_spaces(text)
        assert result == "Hello World"
    
    def test_normalize_line_breaks(self):
        text = "Line1\r\nLine2\rLine3\nLine4"
        result = TextPreprocessor.normalize_line_breaks(text)
        assert "\r" not in result
    
    def test_to_lowercase(self):
        text = "Hello WORLD"
        assert TextPreprocessor.to_lowercase(text) == "hello world"
    
    def test_remove_numbers(self):
        text = "Test 123 String 456"
        result = TextPreprocessor.remove_numbers(text)
        assert "123" not in result
        assert "456" not in result

class TestFileValidator:
    def test_is_valid_size(self):
        # Create small temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test data")
            temp_path = f.name
        
        assert FileValidator.is_valid_size(temp_path, max_size_mb=1)
        os.unlink(temp_path)

# ============== Document Processor Tests ==============

class TestDocumentProcessor:
    def test_initialization(self, document_processor):
        assert document_processor is not None
        assert document_processor.recognizer is not None
    
    def test_process_excel_csv(self, document_processor):
        # Create test CSV
        csv_content = "Name,Age,City\nJohn,30,NYC\nJane,25,LA"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = f.name
        
        try:
            result = document_processor.process_excel(csv_path)
            assert 'metadata' in result
            assert 'content' in result
            assert 'full_text' in result
            assert result['metadata']['file_type'] == 'excel'
        finally:
            os.unlink(csv_path)

# ============== Database Manager Tests ==============

class TestDatabaseManager:
    def test_initialization(self, database_manager):
        assert database_manager is not None
        assert database_manager.sqlite_path is not None
        assert database_manager.collection is not None
    
    def test_add_document(self, database_manager):
        doc_id = database_manager.add_document(
            file_name="test.pdf",
            file_type="pdf",
            metadata={"pages": 10}
        )
        assert doc_id > 0
    
    def test_add_and_search_chunks(self, database_manager):
        # Add document
        doc_id = database_manager.add_document(
            "test_doc.txt",
            "text",
            {}
        )
        
        # Add chunks
        chunks = [
            "This is the first chunk about machine learning",
            "This is the second chunk about artificial intelligence"
        ]
        metadata = [
            {"chunk_index": 0, "document_id": doc_id},
            {"chunk_index": 1, "document_id": doc_id}
        ]
        
        database_manager.add_chunks_to_vector_db(doc_id, chunks, metadata)
        
        # Search
        results = database_manager.semantic_search("machine learning", top_k=1)
        assert len(results) > 0
    
    def test_save_and_retrieve_chat(self, database_manager):
        session_id = "test-session-123"
        database_manager.save_chat_message(
            session_id=session_id,
            user_message="What is AI?",
            assistant_message="AI is artificial intelligence.",
            language="en"
        )
        
        history = database_manager.get_chat_history(session_id)
        assert len(history) > 0
        assert history[0]['user_message'] == "What is AI?"
    
    def test_get_all_documents(self, database_manager):
        # Add a document
        database_manager.add_document("test.pdf", "pdf", {})
        
        docs = database_manager.get_all_documents()
        assert isinstance(docs, list)
        assert len(docs) > 0

# ============== RAG Engine Tests ==============

class TestRAGEngine:
    def test_initialization(self, rag_engine):
        assert rag_engine is not None
        assert rag_engine.llm is not None
    
    def test_chunk_text(self, rag_engine):
        text = "This is a test sentence. " * 100
        chunks = rag_engine.chunk_text(text, metadata={"source": "test"})
        
        assert len(chunks) > 0
        assert all('content' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), 
                       reason="Requires OpenAI API key")
    def test_summarize_text(self, rag_engine):
        text = """
        Machine learning is a subset of artificial intelligence that focuses on
        the development of algorithms and statistical models that enable computers
        to improve their performance on a specific task through experience.
        """
        
        summary = rag_engine.summarize_text(text, language="English", max_length=50)
        assert isinstance(summary, str)
        assert len(summary) > 0

# ============== Translator Tests ==============

class TestTranslator:
    def test_initialization(self, translator):
        assert translator is not None
        assert translator.lang_codes is not None
    
    def test_detect_language_mock(self, translator, monkeypatch):
        # Mock detection
        class MockDetection:
            lang = 'en'
        
        class MockTranslator:
            def detect(self, text):
                return MockDetection()
        
        monkeypatch.setattr(translator, 'google_translator', MockTranslator())
        lang = translator.detect_language("Hello")
        assert lang in ['English', 'en']

# ============== Integration Tests ==============

class TestIntegration:
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), 
                       reason="Requires OpenAI API key")
    def test_full_pipeline(self, document_processor, database_manager, rag_engine):
        """Test complete document processing pipeline"""
        
        # 1. Create test document
        test_text = """
        Artificial Intelligence (AI) is revolutionizing technology.
        Machine learning enables computers to learn from data.
        """
        
        # 2. Add to database
        doc_id = database_manager.add_document(
            "test_ai_doc.txt",
            "text",
            {"test": True}
        )
        
        # 3. Chunk text
        chunks = rag_engine.chunk_text(test_text, {"document_id": doc_id})
        
        # 4. Add chunks to vector DB
        database_manager.add_chunks_to_vector_db(
            doc_id,
            [c['content'] for c in chunks],
            [c['metadata'] for c in chunks]
        )
        
        # 5. Semantic search
        results = database_manager.semantic_search(
            "What is machine learning?",
            top_k=2
        )
        
        assert len(results) > 0

# Run tests with: pytest tests/test_system.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])