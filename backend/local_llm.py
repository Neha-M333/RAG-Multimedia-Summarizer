"""
Local LLM using Ollama - UPDATED WITH ALL METHODS
No API key required!
"""
import requests
import json
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter

class LocalLLM:
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text using local Ollama model"""
        url = f"{self.base_url}/api/generate"
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=120)
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """Chat with context"""
        url = f"{self.base_url}/api/chat"
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=120)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            return f"Error: {str(e)}"

class LocalRAGEngine:
    """RAG Engine using local Ollama - compatible with AdvancedRAGEngine interface"""
    
    def __init__(self, model: str = "llama3.2"):
        self.llm = LocalLLM(model=model)
        self.model = model
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=300,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def chunk_text_adaptive(self, text: str, metadata: Dict = None, complexity=None) -> List[Dict]:
        """
        Split text into chunks for processing - MATCHES AdvancedRAGEngine SIGNATURE
        """
        chunks = self.text_splitter.split_text(text)
        
        chunked_data = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                'chunk_index': i,
                'total_chunks': len(chunks),
                'complexity': 'moderate',
                **(metadata or {})
            }
            chunked_data.append({
                'content': chunk,
                'metadata': chunk_metadata
            })
        
        return chunked_data
    
    def generate_answer_advanced(self, query: str, context_documents: List[Dict], 
                                 language: str = "English") -> Dict:
        """Generate answer using local LLM - MATCHES AdvancedRAGEngine"""
        
        # Format context from retrieved documents
        context = "\n\n".join([
            f"[Source {i+1}]: {doc['content']}"
            for i, doc in enumerate(context_documents)
        ])
        
        prompt = f"""You are an intelligent assistant helping users understand their documents.

Context from documents:
{context}

User Question: {query}

Instructions:
1. Answer the question based ONLY on the provided context
2. If the answer cannot be found in the context, say "I don't have enough information to answer this question based on the provided documents."
3. Be concise but comprehensive
4. Cite which source(s) you used (e.g., "According to Source 1...")
5. Respond in {language}

Answer:"""
        
        answer = self.llm.generate(prompt, temperature=0.7)
        
        return {
            'answer': answer,
            'sources': context_documents,
            'source_count': len(context_documents),
            'complexity': 'moderate',
            'confidence': 'medium',
            'tokens_used': 0,
            'cost': 0.0
        }
    
    def summarize_text(self, text: str, language: str = "English", 
                      max_length: int = 500) -> str:
        """Generate a summary of the provided text - SIMPLE VERSION"""
        prompt = f"""Summarize the following text in {language}. 
Keep the summary concise (around {max_length} words) but capture all key points.

Text:
{text[:10000]}

Summary:"""
        
        return self.llm.generate(prompt, temperature=0.3)
    
    def summarize_advanced(self, text: str, style: str = "executive",
                          language: str = "English", target_length: int = 300,
                          include_metadata: bool = False) -> Dict:
        """Advanced summarization - MATCHES AdvancedRAGEngine"""
        
        summary_text = self.summarize_text(text, language, target_length)
        
        return {
            'summary': summary_text,
            'style': style,
            'language': language,
            'word_count': len(summary_text.split()),
            'original_word_count': len(text.split()),
            'compression_ratio': len(summary_text.split()) / max(len(text.split()), 1),
            'tokens_used': 0,
            'cost': 0.0
        }
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract key terms/phrases from text"""
        prompt = f"""Extract the {num_keywords} most important keywords or key phrases from this text.
Return them as a comma-separated list.

Text:
{text[:5000]}

Keywords:"""
        
        keywords_str = self.llm.generate(prompt, temperature=0.3)
        keywords = [k.strip() for k in keywords_str.split(',')]
        return keywords[:num_keywords]
    
    def generate_questions(self, text: str, num_questions: int = 5) -> List[str]:
        """Generate potential questions that could be answered by the text"""
        prompt = f"""Based on the following text, generate {num_questions} relevant questions 
that this text could answer. Return one question per line.

Text:
{text[:5000]}

Questions:"""
        
        questions_str = self.llm.generate(prompt, temperature=0.5)
        questions = [q.strip() for q in questions_str.split('\n') if q.strip()]
        return questions[:num_questions]
    
    def generate_follow_up_questions(self, query: str, answer: str, 
                                    num_questions: int = 3) -> List[str]:
        """Generate follow-up questions - MATCHES AdvancedRAGEngine"""
        prompt = f"""Based on this Q&A, generate {num_questions} follow-up questions:

Question: {query}
Answer: {answer}

Generate insightful follow-up questions (one per line):"""
        
        try:
            response = self.llm.generate(prompt, temperature=0.5)
            questions = [q.strip() for q in response.split('\n') if q.strip()]
            return questions[:num_questions]
        except:
            return ["What else would you like to know?"]
    
    def multi_document_synthesis(self, documents: List[Dict], query: str,
                                 language: str = "English") -> Dict:
        """Synthesize information across multiple documents"""
        
        context = "\n\n".join([
            f"[Document {i+1}]: {doc['content'][:1000]}"
            for i, doc in enumerate(documents)
        ])
        
        prompt = f"""Synthesize information from these documents to answer: {query}

Documents:
{context}

Provide a comprehensive synthesis in {language}.

Synthesis:"""
        
        try:
            synthesis = self.llm.generate(prompt, temperature=0.7)
            return {
                'synthesis': synthesis,
                'documents_analyzed': len(documents),
                'query': query,
                'language': language
            }
        except Exception as e:
            return {
                'synthesis': f"Error: {str(e)}",
                'error': str(e)
            }
    
    def clear_cache(self):
        """Clear cache - placeholder for compatibility"""
        pass
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'cached_queries': 0,
            'model': self.model,
            'provider': 'ollama'
        }