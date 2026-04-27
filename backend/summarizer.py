"""
Enhanced Advanced Text Summarization Module
Optimized for accuracy, efficiency, and context-awareness
Version: 3.0 - Production Ready
"""

from typing import List, Dict, Optional, Literal, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from collections import Counter
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
import openai
import logging
import hashlib
from functools import lru_cache

logger = logging.getLogger(__name__)


class SummaryComplexity(Enum):
    """Text complexity levels for adaptive summarization"""
    SIMPLE = "simple"          # News articles, blog posts
    MODERATE = "moderate"      # Reports, documentation
    COMPLEX = "complex"        # Academic papers, technical docs
    HIGHLY_TECHNICAL = "technical"  # Scientific papers, code docs


@dataclass
class SummaryMetrics:
    """Quality metrics for summary evaluation"""
    coherence_score: float
    coverage_score: float
    conciseness_score: float
    factual_consistency: float
    readability_score: float
    
    @property
    def overall_quality(self) -> float:
        """Calculate weighted overall quality score"""
        weights = {
            'coherence': 0.25,
            'coverage': 0.25,
            'conciseness': 0.15,
            'factual': 0.25,
            'readability': 0.10
        }
        return (
            self.coherence_score * weights['coherence'] +
            self.coverage_score * weights['coverage'] +
            self.conciseness_score * weights['conciseness'] +
            self.factual_consistency * weights['factual'] +
            self.readability_score * weights['readability']
        )


class TextAnalyzer:
    """Advanced text analysis for context-aware processing"""
    
    @staticmethod
    def detect_complexity(text: str) -> SummaryComplexity:
        """Detect text complexity using multiple heuristics"""
        # Calculate various metrics
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        # Technical indicators
        technical_terms = len(re.findall(r'\b[A-Z]{2,}\b', text))  # Acronyms
        citations = len(re.findall(r'\[\d+\]|\(\d{4}\)', text))  # References
        formulas = len(re.findall(r'[=+\-*/^]', text))
        
        # Complexity scoring
        complexity_score = 0
        
        if avg_word_length > 6:
            complexity_score += 1
        if avg_sentence_length > 25:
            complexity_score += 1
        if technical_terms > len(words) * 0.05:
            complexity_score += 2
        if citations > 5:
            complexity_score += 1
        if formulas > 10:
            complexity_score += 1
        
        # Map score to complexity level
        if complexity_score >= 5:
            return SummaryComplexity.HIGHLY_TECHNICAL
        elif complexity_score >= 3:
            return SummaryComplexity.COMPLEX
        elif complexity_score >= 1:
            return SummaryComplexity.MODERATE
        else:
            return SummaryComplexity.SIMPLE
    
    @staticmethod
    def extract_key_entities(text: str) -> Dict[str, List[str]]:
        """Extract key entities using pattern matching"""
        entities = {
            'numbers': re.findall(r'\b\d+(?:\.\d+)?%?\b', text),
            'dates': re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text),
            'acronyms': re.findall(r'\b[A-Z]{2,}\b', text),
            'proper_nouns': re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', text)
        }
        
        # Deduplicate and limit
        for key in entities:
            entities[key] = list(dict.fromkeys(entities[key]))[:10]
        
        return entities
    
    @staticmethod
    def identify_document_structure(text: str) -> Dict[str, any]:
        """Identify document structure and sections"""
        structure = {
            'has_headers': bool(re.search(r'^#{1,6}\s+.+$|^[A-Z][^.!?]*:$', text, re.MULTILINE)),
            'has_lists': bool(re.search(r'^\s*[-*•]\s+', text, re.MULTILINE)),
            'has_numbered_lists': bool(re.search(r'^\s*\d+\.\s+', text, re.MULTILINE)),
            'has_quotes': bool(re.search(r'["""].*?["""]|^>\s+', text, re.MULTILINE)),
            'paragraph_count': len(text.split('\n\n')),
            'section_count': len(re.findall(r'^#{1,6}\s+|^[A-Z][^.!?]*:$', text, re.MULTILINE))
        }
        
        return structure
    
    @staticmethod
    def calculate_information_density(text: str) -> float:
        """Calculate information density score (0-1)"""
        words = text.split()
        if not words:
            return 0.0
        
        # Unique word ratio
        unique_ratio = len(set(words)) / len(words)
        
        # Content word ratio (exclude stopwords)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                    'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'}
        content_words = [w for w in words if w.lower() not in stopwords]
        content_ratio = len(content_words) / len(words)
        
        # Combine metrics
        density = (unique_ratio * 0.6 + content_ratio * 0.4)
        
        return min(density, 1.0)


class EnhancedSummarizer:
    """
    Production-grade summarizer with:
    - Adaptive processing based on text complexity
    - Multi-level summarization (extractive + abstractive)
    - Context preservation and entity tracking
    - Quality assessment and validation
    - Caching for performance
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
        
        # Initialize LLM with optimized settings
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.3,  # Lower for more focused summaries
            openai_api_key=api_key,
            request_timeout=120,
            max_retries=3
        )
        
        # Analyzer for context-aware processing
        self.analyzer = TextAnalyzer()
        
        # Adaptive text splitters
        self.splitters = {
            SummaryComplexity.SIMPLE: RecursiveCharacterTextSplitter(
                chunk_size=2000, chunk_overlap=200, separators=["\n\n", "\n", ". ", " "]
            ),
            SummaryComplexity.MODERATE: RecursiveCharacterTextSplitter(
                chunk_size=2500, chunk_overlap=300, separators=["\n\n", "\n", ". ", " "]
            ),
            SummaryComplexity.COMPLEX: RecursiveCharacterTextSplitter(
                chunk_size=3000, chunk_overlap=400, separators=["\n\n", "\n", ". ", " "]
            ),
            SummaryComplexity.HIGHLY_TECHNICAL: RecursiveCharacterTextSplitter(
                chunk_size=3500, chunk_overlap=500, separators=["\n\n", "\n", ". ", " "]
            )
        }
        
        # Summary cache
        self._cache = {}
        self._cache_size_limit = 100
        
        logger.info(f"Enhanced Summarizer initialized with {model}")
    
    @lru_cache(maxsize=128)
    def _get_cache_key(self, text: str, style: str, language: str, length: int) -> str:
        """Generate cache key for summary"""
        content = f"{text[:500]}_{style}_{language}_{length}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[Dict]:
        """Check if summary exists in cache"""
        return self._cache.get(cache_key)
    
    def _update_cache(self, cache_key: str, summary: Dict):
        """Update cache with LRU eviction"""
        if len(self._cache) >= self._cache_size_limit:
            # Remove oldest entry
            self._cache.pop(next(iter(self._cache)))
        self._cache[cache_key] = summary
    
    def summarize_advanced(
        self,
        text: str,
        style: Literal["executive", "technical", "academic", "bullet", "narrative"] = "executive",
        language: str = "English",
        target_length: int = 300,
        preserve_entities: bool = True,
        include_metrics: bool = True,
        use_cache: bool = True
    ) -> Dict:
        """
        Advanced summarization with context-awareness and quality metrics
        
        Args:
            text: Input text to summarize
            style: Summary style
            language: Target language
            target_length: Desired word count
            preserve_entities: Keep important entities intact
            include_metrics: Include quality metrics
            use_cache: Use cached results if available
        
        Returns:
            Comprehensive summary dictionary with metrics and metadata
        """
        
        # Check cache
        cache_key = self._get_cache_key(text, style, language, target_length)
        if use_cache:
            cached = self._check_cache(cache_key)
            if cached:
                logger.info("Using cached summary")
                return cached
        
        # Analyze text complexity
        complexity = self.analyzer.detect_complexity(text)
        structure = self.analyzer.identify_document_structure(text)
        density = self.analyzer.calculate_information_density(text)
        
        logger.info(f"Text complexity: {complexity.value}, Density: {density:.2f}")
        
        # Extract key entities if requested
        entities = self.analyzer.extract_key_entities(text) if preserve_entities else {}
        
        # Choose processing strategy
        if len(text.split()) > 5000:
            summary_result = self._hierarchical_summarization(
                text, style, language, target_length, complexity, entities
            )
        else:
            summary_result = self._direct_summarization(
                text, style, language, target_length, complexity, entities
            )
        
        # Add analysis metadata
        summary_result['analysis'] = {
            'complexity': complexity.value,
            'structure': structure,
            'information_density': density,
            'entities': entities
        }
        
        # Calculate quality metrics if requested
        if include_metrics:
            metrics = self._evaluate_summary_quality(
                original_text=text,
                summary=summary_result['summary'],
                entities=entities
            )
            summary_result['metrics'] = metrics
            summary_result['quality_score'] = metrics.overall_quality
        
        # Cache result
        if use_cache:
            self._update_cache(cache_key, summary_result)
        
        return summary_result
    
    def _direct_summarization(
        self,
        text: str,
        style: str,
        language: str,
        target_length: int,
        complexity: SummaryComplexity,
        entities: Dict
    ) -> Dict:
        """Direct summarization for shorter texts"""
        
        # Build context-aware prompt
        prompt = self._build_advanced_prompt(
            text, style, language, target_length, complexity, entities
        )
        
        try:
            with get_openai_callback() as cb:
                summary_text = self.llm.predict(prompt)
                
                # Post-process summary
                summary_text = self._post_process_summary(summary_text, entities)
                
                result = {
                    'summary': summary_text,
                    'style': style,
                    'language': language,
                    'word_count': len(summary_text.split()),
                    'original_word_count': len(text.split()),
                    'compression_ratio': len(summary_text.split()) / len(text.split()),
                    'method': 'direct',
                    'complexity': complexity.value,
                    'tokens_used': cb.total_tokens,
                    'cost': cb.total_cost
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            raise
    
    def _hierarchical_summarization(
        self,
        text: str,
        style: str,
        language: str,
        target_length: int,
        complexity: SummaryComplexity,
        entities: Dict
    ) -> Dict:
        """
        Hierarchical map-reduce summarization for long documents
        Optimized for context preservation
        """
        
        logger.info("Using hierarchical summarization")
        
        # Select appropriate splitter
        splitter = self.splitters[complexity]
        chunks = splitter.split_text(text)
        
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Phase 1: Summarize each chunk (extractive + abstractive)
        chunk_summaries = []
        important_entities_per_chunk = []
        
        for i, chunk in enumerate(chunks):
            # Extract key information from chunk
            chunk_entities = self.analyzer.extract_key_entities(chunk)
            important_entities_per_chunk.append(chunk_entities)
            
            # Create focused prompt for chunk
            chunk_prompt = f"""Summarize this section concisely, preserving key facts, numbers, and entities:

{chunk}

IMPORTANT: Keep all specific numbers, dates, names, and technical terms intact.

Summary (150-200 words):"""
            
            try:
                chunk_summary = self.llm.predict(chunk_prompt)
                chunk_summaries.append(chunk_summary.strip())
            except Exception as e:
                logger.warning(f"Error summarizing chunk {i}: {str(e)}")
                # Fallback: extractive summary
                chunk_summaries.append(self._extractive_summary(chunk, 200))
        
        # Phase 2: Merge chunk summaries
        combined = "\n\n".join(chunk_summaries)
        
        # Consolidate entities from all chunks
        all_entities = self._merge_entities(important_entities_per_chunk)
        
        # Phase 3: Final synthesis
        final_summary = self._direct_summarization(
            combined, style, language, target_length, complexity, all_entities
        )
        
        final_summary['method'] = 'hierarchical'
        final_summary['chunks_processed'] = len(chunks)
        
        return final_summary
    
    def _extract_key_points(self, text: str, max_points: int = 10) -> List[str]:
        """Extract the most important sentences using multiple scoring methods"""
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) > 5]
        
        if not sentences:
            return []
        
        # Method 1: TF-IDF-like scoring
        word_freq = Counter()
        for sentence in sentences:
            words = [w.lower() for w in sentence.split() 
                    if len(w) > 3 and w.lower() not in {'this', 'that', 'with', 'from', 'have', 'been'}]
            word_freq.update(words)
        
        # Method 2: Position scoring (first and last sentences are important)
        position_scores = {}
        for i, sentence in enumerate(sentences):
            if i < 3 or i >= len(sentences) - 3:  # First or last 3
                position_scores[i] = 1.5
            else:
                position_scores[i] = 1.0
        
        # Method 3: Entity scoring (sentences with numbers/names are important)
        entity_scores = {}
        for i, sentence in enumerate(sentences):
            score = 0
            score += len(re.findall(r'\b\d+(?:\.\d+)?%?\b', sentence)) * 2  # Numbers
            score += len(re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', sentence))  # Names
            entity_scores[i] = 1.0 + (score * 0.2)
        
        # Combined scoring
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            words = sentence.lower().split()
            tf_score = sum(word_freq.get(w, 0) for w in words) / max(len(words), 1)
            
            final_score = (
                tf_score * 0.5 +  # Content relevance
                position_scores.get(i, 1.0) * 0.3 +  # Position importance
                entity_scores.get(i, 1.0) * 0.2  # Entity richness
            )
            
            scored_sentences.append((final_score, i, sentence))
        
        # Sort by score and select top sentences
        scored_sentences.sort(reverse=True)
        top_sentences = scored_sentences[:max_points]
        
        # Re-order by original position for coherence
        top_sentences.sort(key=lambda x: x[1])
        
        return [sentence for _, _, sentence in top_sentences]
    
    def _identify_document_theme(self, text: str) -> str:
        """Identify the main theme/topic of the document"""
        
        # Extract frequent meaningful words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Remove common words
        stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 
                    'their', 'there', 'would', 'could', 'should', 'about', 
                    'which', 'these', 'those', 'what', 'when', 'where', 'will'}
        words = [w for w in words if w not in stopwords]
        
        # Get top keywords
        word_freq = Counter(words)
        top_words = [word for word, _ in word_freq.most_common(5)]
        
        # Identify theme based on keywords
        themes = {
            'business': ['business', 'company', 'market', 'revenue', 'growth', 'sales', 'profit'],
            'technical': ['system', 'data', 'algorithm', 'software', 'network', 'code', 'technical'],
            'scientific': ['research', 'study', 'results', 'analysis', 'experiment', 'findings'],
            'healthcare': ['health', 'medical', 'patient', 'treatment', 'disease', 'clinical'],
            'legal': ['legal', 'court', 'rights', 'case', 'law', 'contract', 'agreement'],
            'educational': ['students', 'learning', 'education', 'teaching', 'school', 'course']
        }
        
        # Match keywords to themes
        theme_scores = {}
        for theme, keywords in themes.items():
            score = sum(1 for word in top_words if word in keywords)
            theme_scores[theme] = score
        
        if theme_scores and max(theme_scores.values()) > 0:
            return max(theme_scores, key=theme_scores.get)
        
        return 'general'
    
    def _build_advanced_prompt(
        self,
        text: str,
        style: str,
        language: str,
        target_length: int,
        complexity: SummaryComplexity,
        entities: Dict
    ) -> str:
        """Build highly optimized prompt for document-relevant, concise summaries"""
        
        # Extract key points for focused summarization
        key_points = self._extract_key_points(text, max_points=8)
        
        # Identify document theme
        theme = self._identify_document_theme(text)
        
        # Style-specific instructions with clarity focus
        style_configs = {
            "executive": {
                "tone": "clear, professional, and action-oriented",
                "focus": "most critical insights, decisions, and outcomes that matter",
                "structure": "Lead with the single most important point, then 2-3 key supporting facts",
                "avoid": "jargon, complex sentences, redundancy"
            },
            "technical": {
                "tone": "precise yet accessible, technically accurate but not verbose",
                "focus": "essential technical details, methodologies, and specifications only",
                "structure": "Overview → Key technical elements → Practical implications",
                "avoid": "unnecessary technical depth, redundant explanations"
            },
            "academic": {
                "tone": "scholarly but clear, formal yet readable",
                "focus": "research question, core methodology, main findings, significance",
                "structure": "Purpose → Approach → Key results → Implications",
                "avoid": "excessive detail, tangential information"
            },
            "bullet": {
                "tone": "ultra-clear and direct",
                "focus": "distinct, non-overlapping key points",
                "structure": "Each bullet = one complete, valuable insight",
                "avoid": "similar points, filler words, vague statements"
            },
            "narrative": {
                "tone": "engaging, clear, and flowing",
                "focus": "the story arc with essential context and conclusions",
                "structure": "Setup → Development → Resolution",
                "avoid": "tangents, unnecessary details, repetition"
            }
        }
        
        config = style_configs[style]
        
        # Build focused entity context
        entity_highlights = []
        if entities:
            if entities.get('numbers'):
                entity_highlights.append(f"Key numbers: {', '.join(entities['numbers'][:3])}")
            if entities.get('dates'):
                entity_highlights.append(f"Important dates: {', '.join(entities['dates'][:2])}")
            if entities.get('proper_nouns'):
                entity_highlights.append(f"Key names: {', '.join(entities['proper_nouns'][:3])}")
        
        entity_context = "\n".join(entity_highlights) if entity_highlights else "No specific entities to preserve"
        
        # Theme-specific guidance
        theme_guidance = {
            'business': "Focus on business impact, financial implications, and strategic outcomes.",
            'technical': "Emphasize technical innovations, system capabilities, and implementation aspects.",
            'scientific': "Highlight research objectives, methodology, key findings, and significance.",
            'healthcare': "Prioritize health outcomes, treatment approaches, and patient impact.",
            'legal': "Focus on legal principles, key rulings, rights, and obligations.",
            'educational': "Emphasize learning outcomes, educational methods, and student impact.",
            'general': "Focus on the main message and most valuable insights."
        }
        
        # Complexity-specific clarity instructions
        clarity_by_complexity = {
            SummaryComplexity.SIMPLE: "Use everyday language. Explain concepts simply. Short sentences.",
            SummaryComplexity.MODERATE: "Balance technical terms with clear explanations. Moderate sentence length.",
            SummaryComplexity.COMPLEX: "Maintain technical accuracy but explain key terms. Avoid unnecessary complexity.",
            SummaryComplexity.HIGHLY_TECHNICAL: "Keep specialized terminology but ensure logical flow and clarity."
        }
        
        # Build key points context
        key_points_text = "\n".join([f"• {point}" for point in key_points[:5]])
        
        # Construct optimized prompt
        prompt = f"""You are an expert at creating CONCISE, CLEAR, and HIGHLY RELEVANT summaries.

DOCUMENT ANALYSIS:
- Theme: {theme.upper()}
- Complexity: {complexity.value.upper()}
- {theme_guidance[theme]}

YOUR TASK: Create a {style} summary that captures ONLY the most important information.

CRITICAL REQUIREMENTS:
1. **RELEVANCE**: Focus exclusively on document-specific content - no generic statements
2. **CLARITY**: Use simple, direct language - avoid unnecessary complexity
3. **CONCISENESS**: Every sentence must add unique value - eliminate redundancy
4. **ACCURACY**: Preserve specific facts, numbers, and key terms exactly as stated
5. **KEY POINTS FIRST**: Lead with the most important information

STYLE SPECIFICATIONS:
- Tone: {config['tone']}
- Focus: {config['focus']}
- Structure: {config['structure']}
- Avoid: {config['avoid']}

WRITING GUIDELINES:
- {clarity_by_complexity[complexity]}
- Target length: {target_length} words (±10%)
- Language: {language}
- One idea per sentence
- Active voice preferred
- Remove filler words

KEY INFORMATION TO INCLUDE:
{key_points_text}

ENTITIES TO PRESERVE:
{entity_context}

WHAT NOT TO DO:
❌ Generic introductions ("This document discusses...")
❌ Repetitive phrasing
❌ Vague statements without specifics
❌ Information not in the source text
❌ Unnecessary transitions or filler

WHAT TO DO:
✅ Start with the most important fact immediately
✅ Use specific numbers, names, and terms from the text
✅ Each sentence should reveal new information
✅ End with the most significant implication or outcome
✅ Make every word count

TEXT TO SUMMARIZE:
{text[:15000]}

Generate a {style} summary that is clear, concise, and captures exactly what matters in this document:"""
        
        return prompt
    
    def _post_process_summary(self, summary: str, entities: Dict) -> str:
        """Post-process summary to ensure quality"""
        
        # Remove any artifacts
        summary = re.sub(r'^Summary:\s*', '', summary, flags=re.IGNORECASE)
        summary = re.sub(r'^Here is .*?:\s*', '', summary, flags=re.IGNORECASE)
        
        # Ensure proper capitalization
        sentences = re.split(r'([.!?]+)', summary)
        processed = []
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part.strip():  # Text parts
                part = part.strip()
                if part:
                    part = part[0].upper() + part[1:]
                    processed.append(part)
            else:  # Punctuation
                processed.append(part)
        
        summary = ''.join(processed)
        
        # Ensure single spacing
        summary = re.sub(r'\s+', ' ', summary)
        
        return summary.strip()
    
    def _extractive_summary(self, text: str, max_words: int) -> str:
        """Fallback extractive summarization"""
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Score sentences by word importance
        word_freq = Counter()
        for sentence in sentences:
            words = sentence.lower().split()
            word_freq.update(words)
        
        # Score sentences
        sentence_scores = []
        for sentence in sentences:
            words = sentence.lower().split()
            score = sum(word_freq[w] for w in words) / max(len(words), 1)
            sentence_scores.append((score, sentence))
        
        # Select top sentences
        sentence_scores.sort(reverse=True)
        selected = []
        word_count = 0
        
        for score, sentence in sentence_scores:
            sentence_words = len(sentence.split())
            if word_count + sentence_words <= max_words:
                selected.append(sentence)
                word_count += sentence_words
            if word_count >= max_words:
                break
        
        return '. '.join(selected) + '.'
    
    def _merge_entities(self, entity_lists: List[Dict]) -> Dict:
        """Merge entities from multiple chunks"""
        merged = {}
        
        for entity_dict in entity_lists:
            for category, items in entity_dict.items():
                if category not in merged:
                    merged[category] = []
                merged[category].extend(items)
        
        # Deduplicate and limit
        for category in merged:
            merged[category] = list(dict.fromkeys(merged[category]))[:15]
        
        return merged
    
    def _evaluate_summary_quality(
        self,
        original_text: str,
        summary: str,
        entities: Dict
    ) -> SummaryMetrics:
        """Evaluate summary quality using multiple metrics"""
        
        # 1. Coherence (sentence connectivity)
        coherence = self._calculate_coherence(summary)
        
        # 2. Coverage (entity preservation)
        coverage = self._calculate_coverage(original_text, summary, entities)
        
        # 3. Conciseness (compression vs quality)
        conciseness = self._calculate_conciseness(original_text, summary)
        
        # 4. Factual consistency (entity accuracy)
        factual = self._calculate_factual_consistency(original_text, summary, entities)
        
        # 5. Readability
        readability = self._calculate_readability(summary)
        
        return SummaryMetrics(
            coherence_score=coherence,
            coverage_score=coverage,
            conciseness_score=conciseness,
            factual_consistency=factual,
            readability_score=readability
        )
    
    def _calculate_coherence(self, summary: str) -> float:
        """Calculate coherence score based on sentence connectivity"""
        sentences = re.split(r'[.!?]+', summary)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 1.0
        
        # Calculate word overlap between consecutive sentences
        overlaps = []
        for i in range(len(sentences) - 1):
            words1 = set(sentences[i].lower().split())
            words2 = set(sentences[i + 1].lower().split())
            overlap = len(words1 & words2) / max(len(words1), len(words2), 1)
            overlaps.append(overlap)
        
        # Average overlap is coherence indicator
        return min(sum(overlaps) / len(overlaps) * 2, 1.0)
    
    def _calculate_coverage(self, original: str, summary: str, entities: Dict) -> float:
        """Calculate how well summary covers key entities"""
        if not entities:
            return 0.8  # Default if no entities
        
        total_entities = sum(len(items) for items in entities.values())
        if total_entities == 0:
            return 0.8
        
        preserved = 0
        summary_lower = summary.lower()
        
        for category, items in entities.items():
            for entity in items:
                if entity.lower() in summary_lower:
                    preserved += 1
        
        return preserved / total_entities
    
    def _calculate_conciseness(self, original: str, summary: str) -> float:
        """Calculate conciseness score"""
        orig_words = len(original.split())
        summ_words = len(summary.split())
        
        compression = summ_words / orig_words
        
        # Optimal compression is 0.1-0.3
        if 0.1 <= compression <= 0.3:
            return 1.0
        elif compression < 0.1:
            return 0.7  # Too compressed
        else:
            return max(0.5, 1.0 - (compression - 0.3))
    
    def _calculate_factual_consistency(
        self,
        original: str,
        summary: str,
        entities: Dict
    ) -> float:
        """Check if numbers and facts are preserved correctly"""
        # Extract numbers from both
        orig_numbers = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', original))
        summ_numbers = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', summary))
        
        if not orig_numbers:
            return 1.0
        
        # Check how many summary numbers are from original
        correct = len(summ_numbers & orig_numbers)
        total = len(summ_numbers)
        
        if total == 0:
            return 0.8  # No numbers in summary
        
        return correct / total
    
    def _calculate_readability(self, summary: str) -> float:
        """Calculate readability score (Flesch-Kincaid approximation)"""
        sentences = len(re.split(r'[.!?]+', summary))
        words = summary.split()
        syllables = sum(self._count_syllables(word) for word in words)
        
        if sentences == 0 or len(words) == 0:
            return 0.5
        
        # Simplified Flesch Reading Ease
        avg_sentence_length = len(words) / sentences
        avg_syllables = syllables / len(words)
        
        # Normalize to 0-1 (ideal is 60-70 on Flesch scale)
        flesch = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables
        normalized = min(max(flesch / 100, 0), 1)
        
        return normalized
    
    def _count_syllables(self, word: str) -> int:
        """Approximate syllable count"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(syllable_count, 1)
    
    def clear_cache(self):
        """Clear summary cache"""
        self._cache.clear()
        logger.info("Summary cache cleared")
    
    def get_stats(self) -> Dict:
        """Get summarizer statistics"""
        return {
            'model': self.model,
            'cache_size': len(self._cache),
            'cache_limit': self._cache_size_limit,
            'supported_styles': ['executive', 'technical', 'academic', 'bullet', 'narrative'],
            'complexity_levels': [c.value for c in SummaryComplexity]
        }


# Convenience function for quick summarization
def quick_summarize(
    text: str,
    api_key: str,
    style: str = "executive",
    length: int = 300
) -> str:
    """Quick summarization with default settings"""
    summarizer = EnhancedSummarizer(api_key)
    result = summarizer.summarize_advanced(
        text=text,
        style=style,
        target_length=length,
        include_metrics=False
    )
    return result['summary']


# Example usage
if __name__ == "__main__":
    # Example text
    sample_text = """
    Artificial intelligence has revolutionized various industries in recent years.
    Machine learning algorithms have become increasingly sophisticated, enabling
    computers to perform tasks that once required human intelligence. In healthcare,
    AI systems can now diagnose diseases with accuracy rates exceeding 95%, 
    significantly improving patient outcomes. The global AI market was valued at 
    $136.55 billion in 2022 and is expected to grow at a CAGR of 37.3% from 2023 
    to 2030. However, concerns about bias, privacy, and job displacement remain 
    significant challenges that must be addressed.
    """
    
    # Initialize summarizer (replace with your API key)
    summarizer = EnhancedSummarizer(api_key="your-api-key-here")
    
    # Generate summary
    result = summarizer.summarize_advanced(
        text=sample_text,
        style="executive",
        target_length=50,
        include_metrics=True
    )
    
    print("Summary:", result['summary'])
    print("\nQuality Score:", f"{result['quality_score']:.2f}")
    print("Compression:", f"{result['compression_ratio']:.1%}")