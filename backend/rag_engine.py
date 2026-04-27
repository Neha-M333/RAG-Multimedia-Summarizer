"""
Enhanced RAG Engine with Improved Query Understanding and Retrieval
Fixes:
1. Better semantic matching (not exact word matching)
2. Date format understanding
3. Query expansion and reformulation
4. Hybrid search (semantic + keyword)
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime
import dateparser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
import openai
import json
import logging

logger = logging.getLogger(__name__)

class QueryComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"

@dataclass
class ProcessingStrategy:
    chunk_size: int
    chunk_overlap: int
    temperature: float
    max_tokens: int
    use_reasoning_chain: bool
    
    @classmethod
    def get_strategy(cls, complexity: QueryComplexity) -> 'ProcessingStrategy':
        if isinstance(complexity, str):
            try:
                complexity = QueryComplexity(complexity)
            except:
                complexity = QueryComplexity.MODERATE
        
        strategies = {
            QueryComplexity.SIMPLE: cls(1000, 150, 0.3, 500, False),
            QueryComplexity.MODERATE: cls(1500, 300, 0.5, 800, False),
            QueryComplexity.COMPLEX: cls(2000, 400, 0.7, 1200, True),
            QueryComplexity.EXPERT: cls(2500, 500, 0.8, 1500, True)
        }
        return strategies.get(complexity, cls(1500, 300, 0.5, 800, False))


class AdvancedRAGEngine:
    """
    Enhanced RAG with:
    - Query understanding and expansion
    - Date parsing and normalization
    - Hybrid search (semantic + keyword + fuzzy)
    - Better context assembly
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            openai_api_key=api_key,
            request_timeout=120,
            max_retries=3
        )
        
        self.query_cache = {}
        
        logger.info(f"Enhanced RAG Engine initialized with {model}")
    
    def preprocess_query(self, query: str) -> Dict[str, any]:
        """
        Preprocess and understand the query
        - Extract dates and normalize them
        - Identify key entities
        - Expand synonyms
        - Detect query intent
        """
        
        processed = {
            'original': query,
            'normalized': query.lower().strip(),
            'dates': [],
            'entities': [],
            'keywords': [],
            'intent': self._detect_intent(query),
            'expanded_queries': []
        }
        
        # Extract and normalize dates
        dates = self._extract_dates(query)
        processed['dates'] = dates
        
        # Extract keywords (important terms)
        keywords = self._extract_keywords(query)
        processed['keywords'] = keywords
        
        # Generate query variations for better retrieval
        expanded = self._expand_query(query)
        processed['expanded_queries'] = expanded
        
        logger.info(f"Query preprocessed: {processed['intent']} intent, {len(dates)} dates, {len(keywords)} keywords")
        
        return processed
    
    def _extract_dates(self, text: str) -> List[Dict]:
        """
        Extract and normalize all date mentions
        Examples: "January 2024", "01/15/2024", "last week", "2023-05-10"
        """
        dates_found = []
        
        # Common date patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2}',  # 2024-01-15
            r'\d{2}/\d{2}/\d{4}',  # 01/15/2024
            r'\d{2}-\d{2}-\d{4}',  # 01-15-2024
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',  # January 15, 2024
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # 15 January 2024
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group()
                
                # Parse using dateparser (handles many formats)
                try:
                    parsed_date = dateparser.parse(date_str)
                    if parsed_date:
                        dates_found.append({
                            'original': date_str,
                            'normalized': parsed_date.strftime('%Y-%m-%d'),
                            'formats': [
                                parsed_date.strftime('%Y-%m-%d'),  # 2024-01-15
                                parsed_date.strftime('%m/%d/%Y'),  # 01/15/2024
                                parsed_date.strftime('%d/%m/%Y'),  # 15/01/2024
                                parsed_date.strftime('%B %d, %Y'), # January 15, 2024
                                parsed_date.strftime('%d %B %Y'),  # 15 January 2024
                                parsed_date.strftime('%Y/%m/%d'),  # 2024/01/15
                            ]
                        })
                except:
                    pass
        
        return dates_found
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        
        # Remove common stop words
        stop_words = {
            'what', 'when', 'where', 'who', 'how', 'why', 'which', 'the', 'a', 'an',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'can', 'about', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from'
        }
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def _detect_intent(self, query: str) -> str:
        """Detect what the user is trying to do"""
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['when', 'date', 'time', 'year', 'month']):
            return 'date_query'
        elif any(word in query_lower for word in ['who', 'person', 'author', 'name']):
            return 'entity_query'
        elif any(word in query_lower for word in ['how many', 'count', 'number', 'total']):
            return 'quantitative_query'
        elif any(word in query_lower for word in ['compare', 'difference', 'versus', 'vs']):
            return 'comparison_query'
        elif any(word in query_lower for word in ['summarize', 'summary', 'overview', 'main']):
            return 'summary_query'
        elif any(word in query_lower for word in ['why', 'reason', 'cause', 'explain']):
            return 'explanation_query'
        else:
            return 'general_query'
    
    def _expand_query(self, query: str) -> List[str]:
        """
        Generate query variations to improve retrieval
        """
        
        expanded = [query]
        
        # Add variations with synonyms
        synonyms = {
            'document': ['file', 'paper', 'report'],
            'information': ['data', 'details', 'info'],
            'date': ['time', 'when', 'period'],
            'person': ['individual', 'people', 'who'],
            'company': ['organization', 'business', 'firm'],
        }
        
        query_lower = query.lower()
        for original, replacements in synonyms.items():
            if original in query_lower:
                for replacement in replacements:
                    expanded.append(query_lower.replace(original, replacement))
        
        return list(set(expanded))[:5]  # Limit to 5 variations
    
    def hybrid_search(
        self, 
        query: str, 
        db_manager,
        top_k: int = 10,
        document_filter: Optional[int] = None
    ) -> List[Dict]:
        """
        Hybrid search combining:
        1. Semantic search (vector similarity)
        2. Keyword matching (BM25-like)
        3. Date-aware filtering
        4. STRICT document filtering when specified
        """
        
        # Preprocess query
        processed = self.preprocess_query(query)
        
        results_dict = {}  # Use dict to deduplicate by content hash
        
        # Build filter metadata - STRICT filtering for specific document
        filter_meta = None
        if document_filter:
            filter_meta = {'document_id': document_filter}
            logger.info(f"STRICT FILTER: Only searching document ID {document_filter}")
        
        # 1. Semantic search with original query
        semantic_results = db_manager.semantic_search(
            query=processed['original'],
            top_k=top_k * 2,  # Get more candidates
            filter_metadata=filter_meta
        )
        
        for result in semantic_results:
            content_hash = hash(result['content'][:100])
            if content_hash not in results_dict:
                result['retrieval_method'] = 'semantic'
                result['score'] = result.get('relevance_score', 0)
                results_dict[content_hash] = result
        
        # 2. Semantic search with expanded queries
        for expanded_query in processed['expanded_queries'][:3]:
            expanded_results = db_manager.semantic_search(
                query=expanded_query,
                top_k=top_k,
                filter_metadata=filter_meta  # Use same strict filter
            )
            
            for result in expanded_results:
                content_hash = hash(result['content'][:100])
                if content_hash not in results_dict:
                    result['retrieval_method'] = 'expanded'
                    result['score'] = result.get('relevance_score', 0) * 0.9  # Slightly lower weight
                    results_dict[content_hash] = result
        
        # 3. STRICT VALIDATION: Remove any results from wrong documents
        if document_filter:
            filtered_results = {}
            for hash_key, result in results_dict.items():
                result_doc_id = result.get('metadata', {}).get('document_id')
                if result_doc_id == document_filter:
                    filtered_results[hash_key] = result
                else:
                    logger.warning(f"Filtered out result from doc {result_doc_id}, expected {document_filter}")
            results_dict = filtered_results
            logger.info(f"After strict filtering: {len(results_dict)} results from document {document_filter}")
        
        # 4. Keyword boosting
        for result in results_dict.values():
            keyword_matches = sum(1 for kw in processed['keywords'] if kw in result['content'].lower())
            result['score'] += keyword_matches * 5  # Boost by 5 points per keyword match
        
        # 5. Date matching boost
        if processed['dates']:
            for result in results_dict.values():
                content_lower = result['content'].lower()
                for date_info in processed['dates']:
                    # Check if any date format appears in content
                    if any(fmt.lower() in content_lower for fmt in date_info['formats']):
                        result['score'] += 20  # Significant boost for date match
                        result['date_match'] = True
        
        # Convert back to list and sort by score
        all_results = list(results_dict.values())
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Log final results for debugging
        if document_filter:
            logger.info(f"Final results count: {len(all_results)} (all from document {document_filter})")
            for r in all_results[:3]:
                logger.info(f"  - Score: {r['score']:.1f}, Doc ID: {r.get('metadata', {}).get('document_id')}")
        
        # Return top K
        return all_results[:top_k]
    
    def generate_answer_advanced(
        self,
        query: str,
        context_documents: List[Dict],
        language: str = "English",
        use_chain_of_thought: bool = True
    ) -> Dict:
        """
        Generate answer with enhanced understanding
        """
        
        # Preprocess query for better understanding
        processed_query = self.preprocess_query(query)
        
        # Format context with enhanced metadata
        context_parts = []
        for i, doc in enumerate(context_documents, 1):
            relevance = doc.get('relevance_score', 0)
            
            # Highlight if contains dates
            date_indicator = " [CONTAINS DATES]" if doc.get('date_match') else ""
            
            context_parts.append(
                f"[Source {i} - Relevance: {relevance:.0f}%{date_indicator}]\n"
                f"File: {doc.get('metadata', {}).get('file_name', 'Unknown')}\n"
                f"Content: {doc['content']}\n"
            )
        
        context = "\n\n".join(context_parts)
        
        # Build enhanced prompt based on query intent
        if processed_query['intent'] == 'date_query':
            prompt = self._build_date_query_prompt(processed_query, context, language)
        elif processed_query['intent'] == 'comparison_query':
            prompt = self._build_comparison_prompt(processed_query, context, language)
        else:
            prompt = self._build_general_prompt(processed_query, context, language, use_chain_of_thought)
        
        # Generate response
        try:
            with get_openai_callback() as cb:
                response = self.llm.predict(prompt)
                
                return {
                    'answer': response.strip(),
                    'sources': context_documents,
                    'source_count': len(context_documents),
                    'complexity': processed_query['intent'],
                    'confidence': self._calculate_confidence(processed_query, context_documents),
                    'tokens_used': cb.total_tokens,
                    'cost': cb.total_cost,
                    'query_understanding': processed_query
                }
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                'answer': f"I encountered an error: {str(e)}",
                'sources': context_documents,
                'error': str(e)
            }
    
    def _build_date_query_prompt(self, processed: Dict, context: str, language: str) -> str:
        """Build prompt for date-related queries"""
        
        dates_str = ", ".join([d['original'] for d in processed['dates']]) if processed['dates'] else "dates"
        
        return f"""You are answering a date-related question. Pay special attention to dates in the context.

Context from documents:
{context}

User Question: {processed['original']}

IMPORTANT INSTRUCTIONS FOR DATE QUERIES:
1. Look for dates in MULTIPLE formats: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, "Month Day, Year", etc.
2. The user asked about: {dates_str}
3. Match dates by their MEANING, not exact format
4. If you find relevant dates, state them clearly
5. If dates are mentioned in different formats in the document, recognize them as the same date

Answer the question precisely, focusing on date information. Respond in {language}.

Answer:"""
    
    def _build_comparison_prompt(self, processed: Dict, context: str, language: str) -> str:
        """Build prompt for comparison queries"""
        
        return f"""You are answering a comparison question. Analyze differences and similarities.

Context from documents:
{context}

User Question: {processed['original']}

INSTRUCTIONS FOR COMPARISON:
1. Identify the items/concepts being compared
2. List similarities
3. List differences
4. Provide a clear conclusion

Structure your answer with clear sections. Respond in {language}.

Answer:"""
    
    def _build_general_prompt(self, processed: Dict, context: str, language: str, use_cot: bool) -> str:
        """Build general prompt with optional chain-of-thought"""
        
        if use_cot:
            return f"""You are an intelligent assistant helping users understand their documents.

Context from documents:
{context}

User Question: {processed['original']}
Query Keywords: {', '.join(processed['keywords'])}

CRITICAL INSTRUCTIONS:
1. Answer based on the MEANING of the content, not exact word matches
2. If the question asks about a concept, look for that concept even if different words are used
3. Use your understanding to bridge gaps between query and document phrasing
4. Be flexible with matching - synonyms and related terms should be considered
5. If you find relevant information, provide it even if the wording differs
6. Respond in {language}

Think step-by-step:
1. What is the user really asking?
2. What information in the context relates to this?
3. How can I best answer this question?

Answer:"""
        else:
            return f"""You are an intelligent assistant. Answer based on the provided context.

Context:
{context}

Question: {processed['original']}

IMPORTANT:
- Match by MEANING, not exact words
- Consider synonyms and related concepts
- Be helpful even if wording differs slightly
- Respond in {language}

Answer:"""
    
    def _calculate_confidence(self, processed: Dict, results: List[Dict]) -> str:
        """Calculate confidence based on retrieval quality"""
        
        if not results:
            return 'low'
        
        avg_score = sum(r.get('score', 0) for r in results) / len(results)
        
        # Date queries with date matches = high confidence
        if processed['intent'] == 'date_query' and any(r.get('date_match') for r in results):
            return 'high'
        
        # High relevance scores
        if avg_score > 80:
            return 'high'
        elif avg_score > 60:
            return 'medium'
        else:
            return 'low'
    
    def chunk_text_adaptive(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Adaptive chunking"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
        
        chunks = text_splitter.split_text(text)
        
        chunked_data = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_size': len(chunk),
                **(metadata or {})
            }
            chunked_data.append({
                'content': chunk,
                'metadata': chunk_metadata
            })
        
        return chunked_data
    
    # Keep other methods for compatibility
    def summarize_advanced(self, *args, **kwargs):
        """Placeholder - implement if needed"""
        pass
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        return self._extract_keywords(text)[:num_keywords]
    
    def generate_questions(self, text: str, num_questions: int = 5) -> List[str]:
        """Generate questions from text"""
        pass
    
    def generate_follow_up_questions(self, query: str, answer: str, num_questions: int = 3) -> List[str]:
        """Generate follow-up questions"""
        pass
    
    def multi_document_synthesis(self, documents: List[Dict], query: str, language: str = "English") -> Dict:
        """Multi-document synthesis"""
        pass
    
    def clear_cache(self):
        self.query_cache.clear()
    
    def get_stats(self) -> Dict:
        return {
            'cached_queries': len(self.query_cache),
            'model': self.model,
            'provider': 'openai'
        }