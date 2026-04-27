"""
Enhanced Database Manager with Advanced Features - FIXED
Production-ready with connection pooling, caching, and analytics
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path
import logging
from collections import defaultdict
import threading
from functools import lru_cache
import hashlib

logger = logging.getLogger(__name__)

class ConnectionPool:
    """SQLite connection pool for better performance"""
    
    def __init__(self, database_path: str, pool_size: int = 5):
        self.database_path = database_path
        self.pool_size = pool_size
        self._pool = []
        self._lock = threading.Lock()
        
        # Initialize pool
        for _ in range(pool_size):
            conn = sqlite3.connect(database_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            self._pool.append(conn)
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool"""
        with self._lock:
            if self._pool:
                conn = self._pool.pop()
            else:
                # Create new connection if pool is empty
                conn = sqlite3.connect(self.database_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
        
        try:
            yield conn
        finally:
            with self._lock:
                if len(self._pool) < self.pool_size:
                    self._pool.append(conn)
                else:
                    conn.close()

class EnhancedDatabaseManager:
    """
    Production-grade database manager with:
    - Connection pooling
    - Query caching
    - Advanced analytics
    - Batch operations
    - Transaction support
    - Performance monitoring
    """
    
    def __init__(self, sqlite_path: str, chromadb_path: str, pool_size: int = 5):
        self.sqlite_path = sqlite_path
        self.chromadb_path = chromadb_path
        
        # Initialize connection pool
        self.pool = ConnectionPool(sqlite_path, pool_size)
        
        # Initialize SQLite schema
        self._init_sqlite()
        
        # Initialize ChromaDB with better configuration
        self.chroma_client = chromadb.PersistentClient(
            path=str(chromadb_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedding model with caching
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Query cache
        self._query_cache = {}
        self._cache_lock = threading.Lock()
        
        # Performance metrics
        self.metrics = {
            'queries_executed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_query_time': 0
        }
        
        logger.info("Enhanced Database Manager initialized")
    
    def _init_sqlite(self):
        """Initialize SQLite database with enhanced schema - FIXED SQL SYNTAX"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Documents table with additional fields - FIXED: Removed INDEX from column definition
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER,
                    file_hash TEXT UNIQUE,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    metadata TEXT,
                    processed BOOLEAN DEFAULT 0,
                    processing_time REAL,
                    tags TEXT
                )
            ''')
            
            # Create indexes separately - CORRECT WAY
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_type ON documents(file_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_upload_date ON documents(upload_date)')
            
            # Enhanced chunks table - FIXED
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    chunk_index INTEGER,
                    content TEXT NOT NULL,
                    content_hash TEXT,
                    embedding_id TEXT,
                    metadata TEXT,
                    word_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes separately
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_document_id ON chunks(document_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON chunks(content_hash)')
            
            # Chat history with enhanced tracking - FIXED
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    language TEXT DEFAULT 'en',
                    query_complexity TEXT,
                    response_time REAL,
                    tokens_used INTEGER,
                    cost REAL,
                    confidence_level TEXT,
                    source_documents TEXT,
                    feedback_rating INTEGER
                )
            ''')
            
            # Create indexes separately
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON chat_history(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history(timestamp)')
            
            # Summaries table with versioning - FIXED
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    summary TEXT NOT NULL,
                    summary_type TEXT DEFAULT 'standard',
                    language TEXT DEFAULT 'en',
                    version INTEGER DEFAULT 1,
                    word_count INTEGER,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes separately
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_doc_id_summaries ON summaries(document_id)')
            
            # Analytics table for usage tracking - FIXED
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes separately
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON analytics(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)')
            
            # User feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                    comment TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES chat_history(id)
                )
            ''')
            
            conn.commit()
    
    def add_document(self, file_name: str, file_type: str, metadata: Dict,
                    file_size: int = 0, file_hash: Optional[str] = None,
                    tags: List[str] = None) -> int:
        """Add document with deduplication check"""
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check for duplicate
            if file_hash:
                cursor.execute('SELECT id FROM documents WHERE file_hash = ?', (file_hash,))
                existing = cursor.fetchone()
                if existing:
                    logger.warning(f"Duplicate document detected: {file_name}")
                    return existing[0]
            
            cursor.execute('''
                INSERT INTO documents (file_name, file_type, file_size, file_hash, metadata, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (file_name, file_type, file_size, file_hash, 
                  json.dumps(metadata), json.dumps(tags) if tags else None))
            
            doc_id = cursor.lastrowid
            conn.commit()
            
            # Log analytics
            self._log_analytics('document_added', {
                'document_id': doc_id,
                'file_type': file_type,
                'file_size': file_size
            })
            
            logger.info(f"Document added: {file_name} (ID: {doc_id})")
            return doc_id
    
    def add_chunks_to_vector_db(self, document_id: int, chunks: List[str], 
                            metadata: List[Dict], batch_size: int = 100):
        """Add chunks with CORRECT document_id in metadata"""
        
        try:
            start_time = datetime.now()
            
            # Process in batches
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i + batch_size]
                batch_metadata = metadata[i:i + batch_size]
                
                # Generate IDs
                ids = [f"doc_{document_id}_chunk_{j}" for j in range(i, i + len(batch_chunks))]
                
                # CRITICAL: Ensure document_id is in metadata for filtering
                for meta in batch_metadata:
                    meta['document_id'] = document_id  # Force correct document_id
                
                # Add to ChromaDB
                self.collection.add(
                    documents=batch_chunks,
                    ids=ids,
                    metadatas=batch_metadata
                )
                
                # Store in SQLite
                with self.pool.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    for j, (chunk, meta) in enumerate(zip(batch_chunks, batch_metadata)):
                        content_hash = hashlib.md5(chunk.encode()).hexdigest()
                        word_count = len(chunk.split())
                        
                        cursor.execute('''
                            INSERT INTO chunks 
                            (document_id, chunk_index, content, content_hash, 
                            embedding_id, metadata, word_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (document_id, i + j, chunk, content_hash, 
                            ids[j], json.dumps(meta), word_count))
                    
                    conn.commit()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update document processing status
            self.mark_document_processed(document_id, processing_time)
            
            logger.info(f"Added {len(chunks)} chunks for document {document_id} in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error adding chunks: {str(e)}")
            raise
    
    def semantic_search(self, query: str, top_k: int = 5, 
                    filter_metadata: Optional[Dict] = None,
                    use_cache: bool = True) -> List[Dict]:
        """Enhanced semantic search with STRICT filtering"""
        
        # Create cache key
        cache_key = f"{query}_{top_k}_{json.dumps(filter_metadata, sort_keys=True)}"
        
        # Check cache
        if use_cache:
            with self._cache_lock:
                if cache_key in self._query_cache:
                    self.metrics['cache_hits'] += 1
                    logger.debug(f"Cache hit for query: {query[:50]}")
                    return self._query_cache[cache_key]
                else:
                    self.metrics['cache_misses'] += 1
        
        start_time = datetime.now()
        
        try:
            # Build ChromaDB where clause for filtering
            where_clause = None
            if filter_metadata and 'document_id' in filter_metadata:
                # CRITICAL: Strict filtering by document_id
                where_clause = {"document_id": {"$eq": filter_metadata['document_id']}}
                logger.info(f"STRICT FILTER: Searching only document_id = {filter_metadata['document_id']}")
            
            # Perform search with filter
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k * 2,  # Get more to account for filtering
                where=where_clause
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    
                    # DOUBLE-CHECK: Verify document_id matches filter
                    if filter_metadata and 'document_id' in filter_metadata:
                        result_doc_id = metadata.get('document_id')
                        expected_doc_id = filter_metadata['document_id']
                        
                        if result_doc_id != expected_doc_id:
                            logger.warning(f"Skipping result from doc {result_doc_id}, expected {expected_doc_id}")
                            continue  # Skip this result
                    
                    result = {
                        'content': doc,
                        'metadata': metadata,
                        'distance': results['distances'][0][i] if results['distances'] else None,
                        'id': results['ids'][0][i] if results['ids'] else None,
                        'relevance_score': self._calculate_relevance_score(
                            results['distances'][0][i] if results['distances'] else 1.0
                        )
                    }
                    formatted_results.append(result)
            
            # Limit to top_k after filtering
            formatted_results = formatted_results[:top_k]
            
            query_time = (datetime.now() - start_time).total_seconds()
            
            # Update metrics
            self.metrics['queries_executed'] += 1
            self.metrics['avg_query_time'] = (
                (self.metrics['avg_query_time'] * (self.metrics['queries_executed'] - 1) + query_time) /
                self.metrics['queries_executed']
            )
            
            # Log results for debugging
            if filter_metadata and 'document_id' in filter_metadata:
                logger.info(f"Search returned {len(formatted_results)} results from document {filter_metadata['document_id']}")
                for r in formatted_results[:3]:
                    logger.info(f"  - Doc ID: {r['metadata'].get('document_id')}, Relevance: {r['relevance_score']:.1f}%")
            
            # Cache result
            if use_cache:
                with self._cache_lock:
                    self._query_cache[cache_key] = formatted_results
                    
                    # Limit cache size
                    if len(self._query_cache) > 100:
                        # Remove oldest entry
                        self._query_cache.pop(next(iter(self._query_cache)))
            
            # Log analytics
            self._log_analytics('semantic_search', {
                'query_length': len(query),
                'results_count': len(formatted_results),
                'query_time': query_time,
                'filtered': filter_metadata is not None
            })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return []
    
    def _calculate_relevance_score(self, distance: float) -> float:
        """Convert distance to relevance score (0-100)"""
        # Cosine distance: 0 = identical, 2 = opposite
        # Convert to score: 100 = identical, 0 = opposite
        return max(0, min(100, (1 - distance / 2) * 100))
    
    def save_chat_message(self, session_id: str, user_message: str, 
                         assistant_message: str, language: str = 'en',
                         source_documents: Optional[List] = None,
                         query_complexity: str = None,
                         response_time: float = 0,
                         tokens_used: int = 0,
                         cost: float = 0,
                         confidence_level: str = None) -> int:
        """Save chat with enhanced tracking"""
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO chat_history 
                (session_id, user_message, assistant_message, language, 
                 query_complexity, response_time, tokens_used, cost, 
                 confidence_level, source_documents)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, user_message, assistant_message, language, 
                  query_complexity, response_time, tokens_used, cost,
                  confidence_level, json.dumps(source_documents) if source_documents else None))
            
            chat_id = cursor.lastrowid
            conn.commit()
            
            return chat_id
    
    def get_chat_history(self, session_id: str, limit: int = 50,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Dict]:
        """Get chat history with date filtering"""
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT id, timestamp, user_message, assistant_message, language, 
                       query_complexity, response_time, confidence_level, source_documents
                FROM chat_history
                WHERE session_id = ?
            '''
            params = [session_id]
            
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date.isoformat())
            
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date.isoformat())
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'user_message': row['user_message'],
                    'assistant_message': row['assistant_message'],
                    'language': row['language'],
                    'query_complexity': row['query_complexity'],
                    'response_time': row['response_time'],
                    'confidence_level': row['confidence_level'],
                    'source_documents': json.loads(row['source_documents']) if row['source_documents'] else None
                })
            
            return history
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM documents ORDER BY upload_date DESC')
            rows = cursor.fetchall()
            
            documents = []
            for row in rows:
                documents.append({
                    'id': row['id'],
                    'file_name': row['file_name'],
                    'file_type': row['file_type'],
                    'file_size': row['file_size'],
                    'upload_date': row['upload_date'],
                    'processed': row['processed'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'tags': json.loads(row['tags']) if row['tags'] else []
                })
            
            return documents    
    
    def save_summary(self, document_id: int, summary: str, language: str = 'en'):
        """Save document summary"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            word_count = len(summary.split())
            
            cursor.execute('''
                INSERT INTO summaries (document_id, summary, language, word_count)
                VALUES (?, ?, ?, ?)
            ''', (document_id, summary, language, word_count))
            
            conn.commit()

    def log_video_generation(self, document_id: int, language: str, 
                        duration: float, file_size: int):
        """Log video generation event"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analytics (event_type, event_data)
                VALUES (?, ?)
            ''', ('video_generated', json.dumps({
                'document_id': document_id,
                'language': language,
                'duration': duration,
                'file_size': file_size
            })))
            conn.commit()        
    
    def get_analytics_dashboard(self) -> Dict:
        """Get comprehensive analytics dashboard data"""
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            analytics = {
                'documents': {},
                'chat': {},
                'performance': {},
                'usage_trends': {}
            }
            
            # Document analytics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(file_size) as total_size,
                    AVG(processing_time) as avg_processing_time
                FROM documents
            ''')
            row = cursor.fetchone()
            analytics['documents']['total'] = row['total']
            analytics['documents']['total_size_mb'] = (row['total_size'] or 0) / (1024 * 1024)
            analytics['documents']['avg_processing_time'] = row['avg_processing_time'] or 0
            
            # Documents by type
            cursor.execute('''
                SELECT file_type, COUNT(*) as count
                FROM documents
                GROUP BY file_type
            ''')
            analytics['documents']['by_type'] = {row['file_type']: row['count'] for row in cursor.fetchall()}
            
            # Chat analytics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_chats,
                    AVG(response_time) as avg_response_time,
                    SUM(tokens_used) as total_tokens,
                    SUM(cost) as total_cost
                FROM chat_history
            ''')
            row = cursor.fetchone()
            analytics['chat']['total_messages'] = row['total_chats']
            analytics['chat']['avg_response_time'] = row['avg_response_time'] or 0
            analytics['chat']['total_tokens'] = row['total_tokens'] or 0
            analytics['chat']['total_cost'] = row['total_cost'] or 0
            
            # Query complexity distribution
            cursor.execute('''
                SELECT query_complexity, COUNT(*) as count
                FROM chat_history
                WHERE query_complexity IS NOT NULL
                GROUP BY query_complexity
            ''')
            analytics['chat']['complexity_distribution'] = {
                row['query_complexity']: row['count'] for row in cursor.fetchall()
            }
            
            # Confidence levels
            cursor.execute('''
                SELECT confidence_level, COUNT(*) as count
                FROM chat_history
                WHERE confidence_level IS NOT NULL
                GROUP BY confidence_level
            ''')
            analytics['chat']['confidence_distribution'] = {
                row['confidence_level']: row['count'] for row in cursor.fetchall()
            }
            
            # Performance metrics
            analytics['performance'] = {
                'queries_executed': self.metrics['queries_executed'],
                'cache_hit_rate': (
                    self.metrics['cache_hits'] / 
                    (self.metrics['cache_hits'] + self.metrics['cache_misses'])
                    if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
                ),
                'avg_query_time': self.metrics['avg_query_time'],
                'cache_size': len(self._query_cache)
            }
            
            # Usage trends (last 7 days)
            cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as message_count
                FROM chat_history
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''')
            analytics['usage_trends']['daily_messages'] = [
                {'date': row['date'], 'count': row['message_count']}
                for row in cursor.fetchall()
            ]
            
            return analytics
    
    def get_document_with_chunks(self, document_id: int) -> Optional[Dict]:
        """Get document with all its chunks"""
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get document
            cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
            
            doc_row = cursor.fetchone()
            if not doc_row:
                return None
            
            # Get chunks
            cursor.execute('''
                SELECT id, chunk_index, content, metadata, word_count
                FROM chunks
                WHERE document_id = ?
                ORDER BY chunk_index
            ''', (document_id,))
            
            chunks = [
                {
                    'id': row['id'],
                    'chunk_index': row['chunk_index'],
                    'content': row['content'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'word_count': row['word_count']
                }
                for row in cursor.fetchall()
            ]
            
            return {
                'id': doc_row['id'],
                'file_name': doc_row['file_name'],
                'file_type': doc_row['file_type'],
                'file_size': doc_row['file_size'],
                'upload_date': doc_row['upload_date'],
                'metadata': json.loads(doc_row['metadata']) if doc_row['metadata'] else {},
                'tags': json.loads(doc_row['tags']) if doc_row['tags'] else [],
                'chunks': chunks,
                'total_chunks': len(chunks)
            }
    
    def mark_document_processed(self, document_id: int, processing_time: float = 0):
        """Mark document as processed with timing"""
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE documents
                SET processed = 1, processing_time = ?
                WHERE id = ?
            ''', (processing_time, document_id))
            
            conn.commit()
    
    def delete_document(self, document_id: int) -> bool:
        """Delete document and all associated data"""
        
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete from SQLite (cascades to chunks and summaries)
                cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
                conn.commit()
            
            # Delete from ChromaDB
            try:
                all_ids = self.collection.get()['ids']
                chunk_ids = [id for id in all_ids if id.startswith(f"doc_{document_id}_")]
                if chunk_ids:
                    self.collection.delete(ids=chunk_ids)
            except Exception as e:
                logger.warning(f"Error deleting from ChromaDB: {str(e)}")
            
            logger.info(f"Document {document_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    def _log_analytics(self, event_type: str, event_data: Dict):
        """Log analytics event"""
        
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO analytics (event_type, event_data)
                    VALUES (?, ?)
                ''', (event_type, json.dumps(event_data)))
                
                conn.commit()
        except Exception as e:
            logger.warning(f"Analytics logging failed: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        
        return {
            'cache_stats': {
                'size': len(self._query_cache),
                'hits': self.metrics['cache_hits'],
                'misses': self.metrics['cache_misses'],
                'hit_rate': (
                    self.metrics['cache_hits'] / 
                    (self.metrics['cache_hits'] + self.metrics['cache_misses'])
                    if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
                )
            },
            'performance': {
                'queries_executed': self.metrics['queries_executed'],
                'avg_query_time': self.metrics['avg_query_time']
            },
            'vector_db': {
                'collection_count': self.collection.count(),
                'embedding_model': 'all-MiniLM-L6-v2'
            }
        }
    
    def get_summary(self, document_id: int) -> Optional[Dict]:
        """Get the most recent summary for a document"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, summary, language, created_date, word_count
                FROM summaries
                WHERE document_id = ?
                ORDER BY created_date DESC
                LIMIT 1
            ''', (document_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'summary': row['summary'],
                    'language': row['language'],
                    'created_date': row['created_date'],
                    'word_count': row['word_count']
                }
            
            return None

    def get_all_summaries(self, document_id: int) -> List[Dict]:
        """Get all summaries for a document (multiple versions/languages)"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, summary, language, created_date, word_count, summary_type
                FROM summaries
                WHERE document_id = ?
                ORDER BY created_date DESC
            ''', (document_id,))
            
            summaries = []
            for row in cursor.fetchall():
                summaries.append({
                    'id': row['id'],
                    'summary': row['summary'],
                    'language': row['language'],
                    'created_date': row['created_date'],
                    'word_count': row['word_count'],
                    'summary_type': row['summary_type']
                })
            
            return summaries
    
    
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            # Close all connections in pool
            with self.pool._lock:
                for conn in self.pool._pool:
                    conn.close()
        except:
            pass