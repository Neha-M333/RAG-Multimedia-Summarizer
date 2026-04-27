"""
Advanced RAG Engine with Multi-Strategy Processing - FIXED
Production-ready implementation with context-aware summarization
"""
from typing import List, Dict, Optional, Tuple, Literal
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
# FIXED: Updated imports for LangChain compatibility
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
import openai
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryComplexity(Enum):
    """Query complexity levels for adaptive processing"""
    SIMPLE = "simple"          # Fact-based, single document
    MODERATE = "moderate"      # Multi-document, comparative
    COMPLEX = "complex"        # Analytical, reasoning required
    EXPERT = "expert"          # Domain-specific, technical

@dataclass
class ProcessingStrategy:
    """Strategy configuration for document processing"""
    chunk_size: int
    chunk_overlap: int
    temperature: float
    max_tokens: int
    use_reasoning_chain: bool
    
    @classmethod
    def get_strategy(cls, complexity: QueryComplexity) -> 'ProcessingStrategy':
        """Get optimal strategy based on query complexity"""
        # Handle both enum and string values
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
    
        # Use .get() with default instead of direct access
        return strategies.get(complexity, cls(1500, 300, 0.5, 800, False))
    




class AdvancedRAGEngine:
    """
    Production-grade RAG engine with:
    - Multi-strategy processing
    - Context-aware summarization
    - Query complexity detection
    - Chain-of-thought reasoning
    - Self-reflection and validation
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):  # FIXED: Use gpt-3.5-turbo as default
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
        
        # Initialize LLM with advanced configuration - FIXED: Updated to ChatOpenAI from langchain_openai
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            openai_api_key=api_key,
            request_timeout=120,
            max_retries=3
        )
        
        # Executor for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Cache for repeated queries
        self.query_cache = {}
        
    def analyze_query_complexity(self, query: str) -> QueryComplexity:
        """
        Analyze query to determine processing strategy
        Uses LLM to classify query complexity
        """
        complexity_prompt = f"""Analyze this query and classify its complexity:

Query: {query}

Classification criteria:
- SIMPLE: Direct fact retrieval, single concept (e.g., "What is X?", "When did Y happen?")
- MODERATE: Comparison, multiple concepts (e.g., "Compare X and Y", "List all...")
- COMPLEX: Analysis, reasoning required (e.g., "Why did X cause Y?", "Analyze the impact...")
- EXPERT: Technical/domain-specific, advanced reasoning (e.g., "Evaluate the methodology...", "Critique...")

Respond with ONLY one word: SIMPLE, MODERATE, COMPLEX, or EXPERT"""

        try:
            response = self.llm.predict(complexity_prompt).strip().upper()
            return QueryComplexity[response]
        except:
            # Default to moderate if classification fails
            return QueryComplexity.MODERATE
    
    def chunk_text_adaptive(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Adaptive chunking based on query complexity
        """
        # Always use MODERATE strategy - simple and reliable
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
                'complexity': 'moderate',
                **(metadata or {})
            }
            chunked_data.append({
                'content': chunk,
                'metadata': chunk_metadata
            })
        
        return chunked_data
    
    
    def generate_answer_advanced(
        self,
        query: str,
        context_documents: List[Dict],
        language: str = "English",
        use_chain_of_thought: bool = True
    ) -> Dict:
        """
        Advanced answer generation with:
        - Chain-of-thought reasoning
        - Self-reflection
        - Confidence scoring
        - Source attribution
        """
        
        # Check cache
        cache_key = f"{query}_{len(context_documents)}_{language}"
        if cache_key in self.query_cache:
            logger.info(f"Cache hit for query: {query[:50]}")
            return self.query_cache[cache_key]
        
        # Analyze query complexity
        complexity = self.analyze_query_complexity(query)
        strategy = ProcessingStrategy.get_strategy(complexity)
        
        # Format context with relevance scoring
        context_parts = []
        for i, doc in enumerate(context_documents, 1):
            relevance = doc.get('relevance_score', 0)
            
            context_parts.append(
                f"[Source {i} - Relevance: {relevance:.0f}%]\n"
                f"File: {doc.get('metadata', {}).get('file_name', 'Unknown')}\n"
                f"Content: {doc['content']}\n"
            )
        
        context = "\n\n".join(context_parts)
        
        # Advanced prompt with chain-of-thought
        if use_chain_of_thought and strategy.use_reasoning_chain:
            prompt_template = """You are an advanced AI analyst with deep reasoning capabilities.

Context from documents:
{context}

User Question: {question}

Please follow this reasoning process:

1. UNDERSTANDING: First, break down what the question is asking
2. ANALYSIS: Examine the provided context and identify relevant information
3. REASONING: Connect the information logically to form an answer
4. VALIDATION: Check if your answer is well-supported by the sources
5. RESPONSE: Provide a clear, comprehensive answer

Format your response as:

**Understanding:**
[Your interpretation of the question]

**Key Information Found:**
- [Point 1 from Source X]
- [Point 2 from Source Y]
- [Point 3 from Source Z]

**Analysis & Reasoning:**
[Your logical analysis connecting the information]

**Answer:**
[Clear, direct answer to the question]

**Confidence Level:** [High/Medium/Low]
**Sources Used:** [List source numbers]

**Related Considerations:**
[Any important context, limitations, or related insights]

Respond in {language}."""

        else:
            # Standard prompt for simpler queries
            prompt_template = """You are an intelligent assistant helping users understand their documents.

Context from documents:
{context}

User Question: {question}

Instructions:
1. Answer based ONLY on the provided context
2. If information is insufficient, clearly state what's missing
3. Be precise and cite specific sources
4. Provide confidence level (High/Medium/Low)
5. Suggest related questions if appropriate
6. Respond in {language}

Answer:"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question", "language"]
        )
        
        # Generate response with token tracking
        with get_openai_callback() as cb:
            try:
                chain = prompt | self.llm
                response = chain.invoke({
                    "context": context,
                    "question": query,
                    "language": language
                })
                
                response_text = response.content if hasattr(response, 'content') else str(response)
                
                # Extract confidence level
                confidence = self._extract_confidence(response_text)
                
                result = {
                    'answer': response_text.strip(),
                    'sources': context_documents,
                    'source_count': len(context_documents),
                    'complexity': complexity.value,
                    'confidence': confidence,
                    'tokens_used': cb.total_tokens,
                    'cost': cb.total_cost,
                    'processing_strategy': strategy.__dict__
                }
                
                # Cache result
                self.query_cache[cache_key] = result
                
                logger.info(f"Generated answer - Tokens: {cb.total_tokens}, Cost: ${cb.total_cost:.4f}")
                
                return result
                
            except Exception as e:
                logger.error(f"Error generating answer: {str(e)}")
                return {
                    'answer': f"I encountered an error processing your question: {str(e)}",
                    'sources': context_documents,
                    'source_count': 0,
                    'complexity': complexity.value,
                    'confidence': 'low',
                    'error': str(e)
                }
    
    def _extract_confidence(self, text: str) -> str:
        """Extract confidence level from response"""
        text_lower = text.lower()
        if 'confidence level: high' in text_lower or 'high confidence' in text_lower:
            return 'high'
        elif 'confidence level: medium' in text_lower or 'medium confidence' in text_lower:
            return 'medium'
        elif 'confidence level: low' in text_lower or 'low confidence' in text_lower:
            return 'low'
        return 'medium'  # default
    
    def summarize_advanced(
        self,
        text: str,
        style: Literal["executive", "technical", "academic", "bullet", "narrative"] = "executive",
        language: str = "English",
        target_length: int = 300,
        include_metadata: bool = True
    ) -> Dict:
        """
        Advanced summarization with multiple styles and deep analysis
        """
        
        # For very long texts, use hierarchical summarization
        if len(text.split()) > 5000:
            return self._hierarchical_summarization(text, style, language, target_length)
        
        style_configs = {
            "executive": {
                "instruction": "Create an executive summary suitable for business leaders",
                "structure": "Start with key takeaway, then main points, end with implications"
            },
            "technical": {
                "instruction": "Create a technical summary preserving methodologies and specific details",
                "structure": "Overview, technical details, findings, conclusions"
            },
            "academic": {
                "instruction": "Create an academic abstract with background, methods, results, conclusions",
                "structure": "Background, Methodology, Results, Conclusions, Future Work"
            },
            "bullet": {
                "instruction": "Create a bullet-point summary of key information",
                "structure": "Use clear bullet points, each capturing one key idea"
            },
            "narrative": {
                "instruction": "Create a flowing narrative summary that tells the story",
                "structure": "Beginning (context), middle (main content), end (conclusions)"
            }
        }
        
        config = style_configs[style]
        
        prompt = f"""You are an expert summarization specialist.

{config['instruction']}

Text to summarize:
{text[:15000]}

Requirements:
- Target length: approximately {target_length} words
- Language: {language}
- Structure: {config['structure']}
- Preserve key facts, figures, and names
- Maintain original meaning and context
- Be clear and concise

Summary:"""

        try:
            with get_openai_callback() as cb:
                summary_text = self.llm.predict(prompt)
                
                result = {
                    'summary': summary_text.strip(),
                    'style': style,
                    'language': language,
                    'word_count': len(summary_text.split()),
                    'original_word_count': len(text.split()),
                    'compression_ratio': len(summary_text.split()) / len(text.split()),
                    'tokens_used': cb.total_tokens,
                    'cost': cb.total_cost
                }
                
                if include_metadata:
                    result['metadata'] = self._extract_summary_metadata(text, summary_text)
                
                return result
                
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return {
                'summary': f"Error generating summary: {str(e)}",
                'style': style,
                'error': str(e)
            }
    
    def _hierarchical_summarization(
        self,
        text: str,
        style: str,
        language: str,
        target_length: int
    ) -> Dict:
        """
        Hierarchical summarization for very long documents
        Map-Reduce strategy with quality preservation
        """
        
        # Split into manageable chunks
        chunk_size = 4000
        words = text.split()
        chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        
        logger.info(f"Hierarchical summarization: {len(chunks)} chunks")
        
        # First pass: Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            prompt = f"""Summarize this section concisely, preserving key information:

{chunk}

Summary:"""
            
            summary = self.llm.predict(prompt)
            chunk_summaries.append(summary.strip())
        
        # Second pass: Combine summaries
        combined = "\n\n".join(chunk_summaries)
        
        # Final summarization
        return self.summarize_advanced(
            combined,
            style=style,
            language=language,
            target_length=target_length,
            include_metadata=False
        )
    
    def _extract_summary_metadata(self, original: str, summary: str) -> Dict:
        """Extract metadata about the summarization quality"""
        
        prompt = f"""Analyze this summarization and provide metadata:

Original text length: {len(original.split())} words
Summary length: {len(summary.split())} words

Original (first 500 words):
{' '.join(original.split()[:500])}

Summary:
{summary}

Provide JSON with:
- key_topics: [list of main topics covered]
- entities_preserved: [important names, dates, numbers preserved]
- information_loss: "low/medium/high"
- clarity_score: 1-10
- completeness_score: 1-10

JSON:"""
        
        try:
            response = self.llm.predict(prompt)
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        
        return {
            'key_topics': ['analysis_failed'],
            'information_loss': 'unknown',
            'clarity_score': 0,
            'completeness_score': 0
        }
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract key terms/phrases from text"""
        prompt = f"""Extract the {num_keywords} most important keywords or key phrases from this text.
Return them as a comma-separated list.

Text:
{text[:5000]}

Keywords:"""
        
        keywords_str = self.llm.predict(prompt)
        keywords = [k.strip() for k in keywords_str.split(',')]
        return keywords[:num_keywords]
    
    def generate_questions(self, text: str, num_questions: int = 5) -> List[str]:
        """Generate potential questions that could be answered by the text"""
        prompt = f"""Based on the following text, generate {num_questions} relevant questions 
that this text could answer. Return one question per line.

Text:
{text[:5000]}

Questions:"""
        
        questions_str = self.llm.predict(prompt)
        questions = [q.strip() for q in questions_str.split('\n') if q.strip()]
        return questions[:num_questions]
    
    def multi_document_synthesis(
        self,
        documents: List[Dict],
        query: str,
        language: str = "English"
    ) -> Dict:
        """
        Synthesize information across multiple documents
        Advanced cross-document reasoning
        """
        
        prompt = f"""You are synthesizing information from multiple documents to answer a complex query.

Query: {query}

Documents:
"""
        
        for i, doc in enumerate(documents, 1):
            prompt += f"\n[Document {i}: {doc.get('metadata', {}).get('file_name', 'Unknown')}]\n"
            prompt += f"{doc['content'][:1000]}\n"
        
        prompt += f"""

Task: Provide a comprehensive synthesis that:
1. Identifies common themes across documents
2. Highlights differences or contradictions
3. Provides a unified answer drawing from all sources
4. Notes which documents support which points
5. Indicates confidence level for each major point

Respond in {language}.

Synthesis:"""

        try:
            response = self.llm.predict(prompt)
            
            return {
                'synthesis': response.strip(),
                'documents_analyzed': len(documents),
                'query': query,
                'language': language
            }
        except Exception as e:
            return {
                'synthesis': f"Error in synthesis: {str(e)}",
                'error': str(e)
            }
    
    def generate_follow_up_questions(
        self,
        query: str,
        answer: str,
        num_questions: int = 3
    ) -> List[str]:
        """
        Generate intelligent follow-up questions
        Enhances interactive exploration
        """
        
        prompt = f"""Based on this Q&A, generate {num_questions} insightful follow-up questions:

Original Question: {query}
Answer: {answer}

Generate questions that:
1. Dig deeper into the topic
2. Explore related areas
3. Challenge assumptions
4. Seek clarification

Questions (one per line):"""

        try:
            response = self.llm.predict(prompt)
            questions = [q.strip() for q in response.split('\n') if q.strip()]
            return questions[:num_questions]
        except:
            return ["What else would you like to know?"]
    
    def clear_cache(self):
        """Clear query cache"""
        self.query_cache.clear()
        logger.info("Query cache cleared")
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'cached_queries': len(self.query_cache),
            'model': self.model,
            'executor_threads': self.executor._max_workers
        }
    
    