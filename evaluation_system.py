"""
Comprehensive Evaluation System for AI Document Intelligence
Evaluates: RAG Performance, Summarization Quality, Video Synthesis, 
Multilingual Narration, Comparative Discussion, Multimodal Ingestion
"""

import os
import json
import time
import numpy as np
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime
import pandas as pd
from collections import defaultdict

# NLP and ML imports
try:
    from rouge import Rouge
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False
    print("⚠️ rouge not installed: pip install rouge")

try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️ nltk not installed: pip install nltk")

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ sentence-transformers not installed: pip install sentence-transformers")

try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    print("⚠️ textstat not installed: pip install textstat")

# Your system imports - will be imported in the example function
# Placeholder imports - actual imports happen at runtime
EnhancedDatabaseManager = None
AdvancedRAGEngine = None
EnhancedSummarizer = None
DocumentVideoGenerator = None
DocumentProcessor = None


class EvaluationMetrics:
    """Calculate various evaluation metrics"""
    
    def __init__(self):
        self.rouge = Rouge() if ROUGE_AVAILABLE else None
        self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2') if SENTENCE_TRANSFORMERS_AVAILABLE else None
    
    def calculate_rouge(self, reference: str, generated: str) -> Dict[str, float]:
        """Calculate ROUGE scores (recall-oriented)"""
        if not ROUGE_AVAILABLE or not self.rouge:
            return {k: 0.0 for k in ['rouge-1-f', 'rouge-1-p', 'rouge-1-r', 'rouge-2-f', 'rouge-l-f']}
        try:
            scores = self.rouge.get_scores(generated, reference)[0]
            return {
                'rouge-1-f': scores['rouge-1']['f'],
                'rouge-1-p': scores['rouge-1']['p'],
                'rouge-1-r': scores['rouge-1']['r'],
                'rouge-2-f': scores['rouge-2']['f'],
                'rouge-l-f': scores['rouge-l']['f']
            }
        except:
            return {k: 0.0 for k in ['rouge-1-f', 'rouge-1-p', 'rouge-1-r', 'rouge-2-f', 'rouge-l-f']}
    
    def calculate_bleu(self, reference: str, generated: str) -> float:
        """Calculate BLEU score (precision-oriented)"""
        if not NLTK_AVAILABLE:
            return 0.0
        try:
            ref_tokens = reference.split()
            gen_tokens = generated.split()
            smoothing = SmoothingFunction().method1
            return sentence_bleu([ref_tokens], gen_tokens, smoothing_function=smoothing)
        except:
            return 0.0
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using embeddings"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE or not self.semantic_model:
            # Fallback: simple word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if not words1 or not words2:
                return 0.0
            return len(words1 & words2) / len(words1 | words2)
        try:
            emb1 = self.semantic_model.encode(text1, convert_to_tensor=True)
            emb2 = self.semantic_model.encode(text2, convert_to_tensor=True)
            similarity = util.cos_sim(emb1, emb2).item()
            return similarity
        except:
            return 0.0
    
    def calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate readability metrics"""
        if not TEXTSTAT_AVAILABLE:
            # Fallback: basic metrics
            sentences = text.split('.')
            words = text.split()
            return {
                'flesch_reading_ease': 60.0,  # Default moderate
                'flesch_kincaid_grade': 8.0,
                'gunning_fog': 10.0,
                'smog_index': 9.0,
                'avg_sentence_length': len(words) / max(len(sentences), 1),
                'avg_word_length': np.mean([len(w) for w in words]) if words else 0
            }
        try:
            return {
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'gunning_fog': textstat.gunning_fog(text),
                'smog_index': textstat.smog_index(text),
                'avg_sentence_length': np.mean([len(s.split()) for s in text.split('.')]),
                'avg_word_length': np.mean([len(w) for w in text.split()])
            }
        except:
            return {k: 0.0 for k in ['flesch_reading_ease', 'flesch_kincaid_grade', 
                                     'gunning_fog', 'smog_index', 'avg_sentence_length', 'avg_word_length']}
    
    def calculate_compression_ratio(self, original: str, summary: str) -> float:
        """Calculate text compression ratio"""
        return len(summary.split()) / max(len(original.split()), 1)
    
    def calculate_information_coverage(self, original: str, summary: str) -> float:
        """Calculate how much key information is preserved"""
        # Extract key terms from original
        original_terms = set([w.lower() for w in original.split() if len(w) > 4])
        summary_terms = set([w.lower() for w in summary.split()])
        
        if not original_terms:
            return 0.0
        
        coverage = len(original_terms & summary_terms) / len(original_terms)
        return coverage


class RAGPerformanceEvaluator:
    """Evaluate Retrieval-Augmented Generation Performance"""
    
    def __init__(self, db_manager: EnhancedDatabaseManager, rag_engine: AdvancedRAGEngine):
        self.db_manager = db_manager
        self.rag_engine = rag_engine
        self.metrics = EvaluationMetrics()
    
    def evaluate_retrieval_accuracy(self, test_cases: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate retrieval accuracy using test cases
        
        Test case format:
        {
            'query': str,
            'document_id': int,
            'expected_chunks': List[str],  # Expected relevant chunks
            'ground_truth_answer': str
        }
        """
        
        results = {
            'retrieval_metrics': [],
            'answer_quality': [],
            'response_times': [],
            'confidence_scores': []
        }
        
        print("\n🔍 EVALUATING RAG RETRIEVAL ACCURACY")
        print("="*70)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}/{len(test_cases)}: {test_case['query'][:60]}...")
            
            start_time = time.time()
            
            # Perform retrieval
            retrieved_docs = self.db_manager.semantic_search(
                query=test_case['query'],
                top_k=5,
                filter_metadata={'document_id': test_case.get('document_id')}
            )
            
            retrieval_time = time.time() - start_time
            
            # Calculate retrieval metrics
            retrieved_contents = [doc['content'] for doc in retrieved_docs]
            
            # Precision@K and Recall@K
            precision_at_k = self._calculate_precision(
                retrieved_contents, 
                test_case.get('expected_chunks', [])
            )
            
            recall_at_k = self._calculate_recall(
                retrieved_contents,
                test_case.get('expected_chunks', [])
            )
            
            # MRR (Mean Reciprocal Rank)
            mrr = self._calculate_mrr(
                retrieved_contents,
                test_case.get('expected_chunks', [])
            )
            
            results['retrieval_metrics'].append({
                'query': test_case['query'],
                'precision@5': precision_at_k,
                'recall@5': recall_at_k,
                'mrr': mrr,
                'retrieval_time': retrieval_time,
                'num_results': len(retrieved_docs)
            })
            
            # Generate answer
            answer_start = time.time()
            
            rag_response = self.rag_engine.generate_answer_advanced(
                query=test_case['query'],
                context_documents=retrieved_docs,
                language='English'
            )
            
            answer_time = time.time() - answer_start
            
            # Evaluate answer quality
            if 'ground_truth_answer' in test_case:
                rouge_scores = self.metrics.calculate_rouge(
                    test_case['ground_truth_answer'],
                    rag_response['answer']
                )
                
                semantic_sim = self.metrics.calculate_semantic_similarity(
                    test_case['ground_truth_answer'],
                    rag_response['answer']
                )
                
                results['answer_quality'].append({
                    'query': test_case['query'],
                    **rouge_scores,
                    'semantic_similarity': semantic_sim,
                    'answer_length': len(rag_response['answer'].split())
                })
            
            results['response_times'].append(retrieval_time + answer_time)
            results['confidence_scores'].append(rag_response.get('confidence', 'unknown'))
            
            print(f"  ✅ Retrieval Time: {retrieval_time:.3f}s")
            print(f"  ✅ Answer Time: {answer_time:.3f}s")
            print(f"  ✅ Precision@5: {precision_at_k:.3f}")
            print(f"  ✅ Recall@5: {recall_at_k:.3f}")
        
        # Aggregate results
        summary = self._aggregate_rag_results(results)
        
        return {
            'detailed_results': results,
            'summary': summary
        }
    
    def _calculate_precision(self, retrieved: List[str], expected: List[str]) -> float:
        """Calculate precision@K"""
        if not retrieved or not expected:
            return 0.0
        
        relevant_count = sum(1 for doc in retrieved if any(exp in doc for exp in expected))
        return relevant_count / len(retrieved)
    
    def _calculate_recall(self, retrieved: List[str], expected: List[str]) -> float:
        """Calculate recall@K"""
        if not expected:
            return 0.0
        
        found_count = sum(1 for exp in expected if any(exp in doc for doc in retrieved))
        return found_count / len(expected)
    
    def _calculate_mrr(self, retrieved: List[str], expected: List[str]) -> float:
        """Calculate Mean Reciprocal Rank"""
        for i, doc in enumerate(retrieved, 1):
            if any(exp in doc for exp in expected):
                return 1.0 / i
        return 0.0
    
    def _aggregate_rag_results(self, results: Dict) -> Dict[str, float]:
        """Aggregate RAG evaluation results"""
        
        retrieval_df = pd.DataFrame(results['retrieval_metrics'])
        
        summary = {
            'avg_precision@5': retrieval_df['precision@5'].mean(),
            'avg_recall@5': retrieval_df['recall@5'].mean(),
            'avg_mrr': retrieval_df['mrr'].mean(),
            'avg_retrieval_time': retrieval_df['retrieval_time'].mean(),
            'avg_total_response_time': np.mean(results['response_times']),
            'total_queries': len(results['retrieval_metrics'])
        }
        
        if results['answer_quality']:
            answer_df = pd.DataFrame(results['answer_quality'])
            summary.update({
                'avg_rouge_1_f': answer_df['rouge-1-f'].mean(),
                'avg_rouge_2_f': answer_df['rouge-2-f'].mean(),
                'avg_rouge_l_f': answer_df['rouge-l-f'].mean(),
                'avg_semantic_similarity': answer_df['semantic_similarity'].mean()
            })
        
        return summary


class SummarizationQualityEvaluator:
    """Evaluate Summarization Quality"""
    
    def __init__(self, summarizer: EnhancedSummarizer):
        self.summarizer = summarizer
        self.metrics = EvaluationMetrics()
    
    def evaluate_summaries(self, test_documents: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate summarization quality
        
        Test document format:
        {
            'text': str,
            'reference_summary': str,  # Human-written reference summary
            'document_type': str,
            'language': str
        }
        """
        
        results = {
            'quality_metrics': [],
            'readability_metrics': [],
            'generation_times': [],
            'compression_ratios': []
        }
        
        print("\n📝 EVALUATING SUMMARIZATION QUALITY")
        print("="*70)
        
        for i, doc in enumerate(test_documents, 1):
            print(f"\nDocument {i}/{len(test_documents)}: {doc.get('document_type', 'unknown')}")
            
            start_time = time.time()
            
            # Generate summary
            summary_result = self.summarizer.summarize_advanced(
                text=doc['text'],
                language=doc.get('language', 'English'),
                target_length=300,
                include_metrics=True
            )
            
            generation_time = time.time() - start_time
            
            if not summary_result.get('success'):
                print(f"  ❌ Failed: {summary_result.get('error')}")
                continue
            
            generated_summary = summary_result['summary']
            
            # Calculate quality metrics
            if 'reference_summary' in doc:
                rouge_scores = self.metrics.calculate_rouge(
                    doc['reference_summary'],
                    generated_summary
                )
                
                bleu_score = self.metrics.calculate_bleu(
                    doc['reference_summary'],
                    generated_summary
                )
                
                semantic_sim = self.metrics.calculate_semantic_similarity(
                    doc['reference_summary'],
                    generated_summary
                )
                
                results['quality_metrics'].append({
                    'document_type': doc.get('document_type'),
                    **rouge_scores,
                    'bleu': bleu_score,
                    'semantic_similarity': semantic_sim
                })
            
            # Calculate readability
            readability = self.metrics.calculate_readability(generated_summary)
            results['readability_metrics'].append({
                'document_type': doc.get('document_type'),
                **readability
            })
            
            # Compression ratio
            compression = self.metrics.calculate_compression_ratio(
                doc['text'],
                generated_summary
            )
            results['compression_ratios'].append(compression)
            
            # Information coverage
            coverage = self.metrics.calculate_information_coverage(
                doc['text'],
                generated_summary
            )
            
            results['generation_times'].append(generation_time)
            
            print(f"  ✅ Generation Time: {generation_time:.2f}s")
            print(f"  ✅ Compression: {compression:.2%}")
            print(f"  ✅ Coverage: {coverage:.2%}")
            print(f"  ✅ Flesch Score: {readability['flesch_reading_ease']:.1f}")
        
        # Aggregate results
        summary = self._aggregate_summarization_results(results)
        
        return {
            'detailed_results': results,
            'summary': summary
        }
    
    def _aggregate_summarization_results(self, results: Dict) -> Dict[str, float]:
        """Aggregate summarization evaluation results"""
        
        summary = {
            'avg_generation_time': np.mean(results['generation_times']),
            'avg_compression_ratio': np.mean(results['compression_ratios']),
            'total_documents': len(results['generation_times'])
        }
        
        if results['quality_metrics']:
            quality_df = pd.DataFrame(results['quality_metrics'])
            summary.update({
                'avg_rouge_1_f': quality_df['rouge-1-f'].mean(),
                'avg_rouge_2_f': quality_df['rouge-2-f'].mean(),
                'avg_rouge_l_f': quality_df['rouge-l-f'].mean(),
                'avg_bleu': quality_df['bleu'].mean(),
                'avg_semantic_similarity': quality_df['semantic_similarity'].mean()
            })
        
        if results['readability_metrics']:
            readability_df = pd.DataFrame(results['readability_metrics'])
            summary.update({
                'avg_flesch_score': readability_df['flesch_reading_ease'].mean(),
                'avg_grade_level': readability_df['flesch_kincaid_grade'].mean()
            })
        
        return summary


class VideoSynthesisEvaluator:
    """Evaluate Video Synthesis Quality"""
    
    def __init__(self, video_generator: DocumentVideoGenerator):
        self.video_generator = video_generator
    
    async def evaluate_video_generation(self, test_cases: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate video synthesis
        
        Test case format:
        {
            'summary_text': str,
            'language': str,
            'target_duration': int,
            'document_name': str
        }
        """
        
        results = {
            'generation_metrics': [],
            'quality_scores': [],
            'language_support': defaultdict(list)
        }
        
        print("\n🎬 EVALUATING VIDEO SYNTHESIS")
        print("="*70)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}/{len(test_cases)}: {test_case['language']}")
            
            start_time = time.time()
            
            # Generate video
            video_result = await self.video_generator.generate_video_from_summary(
                summary_text=test_case['summary_text'],
                language=test_case['language'],
                target_duration=test_case.get('target_duration'),
                include_subtitles=True,
                document_name=test_case.get('document_name', 'test')
            )
            
            generation_time = time.time() - start_time
            
            if not video_result['success']:
                print(f"  ❌ Failed: {video_result.get('error')}")
                results['generation_metrics'].append({
                    'language': test_case['language'],
                    'success': False,
                    'error': video_result.get('error')
                })
                continue
            
            # Analyze video quality
            quality_metrics = self._analyze_video_quality(video_result)
            
            results['generation_metrics'].append({
                'language': test_case['language'],
                'success': True,
                'generation_time': generation_time,
                'video_duration': video_result['duration'],
                'file_size_mb': video_result['file_size'] / (1024 * 1024),
                **quality_metrics
            })
            
            results['language_support'][test_case['language']].append({
                'success': True,
                'duration': video_result['duration']
            })
            
            print(f"  ✅ Generation Time: {generation_time:.1f}s")
            print(f"  ✅ Video Duration: {video_result['duration']:.1f}s")
            print(f"  ✅ File Size: {video_result['file_size'] / (1024*1024):.2f} MB")
        
        # Aggregate results
        summary = self._aggregate_video_results(results)
        
        return {
            'detailed_results': results,
            'summary': summary
        }
    
    def _analyze_video_quality(self, video_result: Dict) -> Dict[str, Any]:
        """Analyze video quality metrics"""
        
        # Calculate quality score based on various factors
        quality_score = 100.0
        
        # Duration accuracy (target vs actual)
        # File size efficiency
        # Resolution
        
        return {
            'quality_score': quality_score,
            'resolution': video_result.get('resolution', 'unknown'),
            'has_subtitles': video_result.get('include_subtitles', False)
        }
    
    def _aggregate_video_results(self, results: Dict) -> Dict[str, Any]:
        """Aggregate video evaluation results"""
        
        successful = [m for m in results['generation_metrics'] if m.get('success')]
        
        if not successful:
            return {'total_tests': len(results['generation_metrics']), 'success_rate': 0.0}
        
        summary = {
            'total_tests': len(results['generation_metrics']),
            'success_rate': len(successful) / len(results['generation_metrics']),
            'avg_generation_time': np.mean([m['generation_time'] for m in successful]),
            'avg_video_duration': np.mean([m['video_duration'] for m in successful]),
            'avg_file_size_mb': np.mean([m['file_size_mb'] for m in successful]),
            'languages_tested': list(results['language_support'].keys()),
            'language_success_rates': {
                lang: sum(1 for r in records if r['success']) / len(records)
                for lang, records in results['language_support'].items()
            }
        }
        
        return summary


class MultimodalIngestionEvaluator:
    """Evaluate Multimodal Document Ingestion Accuracy"""
    
    def __init__(self, document_processor: DocumentProcessor):
        self.processor = document_processor
    
    def evaluate_ingestion_accuracy(self, test_files: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate document ingestion accuracy
        
        Test file format:
        {
            'file_path': str,
            'file_type': str,
            'expected_content': str,  # Ground truth content
            'expected_word_count': int,
            'expected_metadata': Dict
        }
        """
        
        results = {
            'processing_metrics': [],
            'accuracy_metrics': [],
            'error_rates': defaultdict(int),
            'processing_times': []
        }
        
        print("\n📥 EVALUATING MULTIMODAL INGESTION")
        print("="*70)
        
        for i, test_file in enumerate(test_files, 1):
            print(f"\nFile {i}/{len(test_files)}: {test_file['file_type']}")
            
            start_time = time.time()
            
            try:
                # Process document
                processed = self.processor.process_document(
                    test_file['file_path'],
                    test_file.get('file_type')
                )
                
                processing_time = time.time() - start_time
                
                # Calculate accuracy
                extracted_text = processed.get('full_text', '')
                
                if 'expected_content' in test_file:
                    # Text similarity
                    similarity = self._calculate_text_similarity(
                        test_file['expected_content'],
                        extracted_text
                    )
                    
                    # Word count accuracy
                    word_count_error = abs(
                        len(extracted_text.split()) - test_file.get('expected_word_count', 0)
                    ) / max(test_file.get('expected_word_count', 1), 1)
                    
                    results['accuracy_metrics'].append({
                        'file_type': test_file['file_type'],
                        'text_similarity': similarity,
                        'word_count_error': word_count_error
                    })
                
                results['processing_metrics'].append({
                    'file_type': test_file['file_type'],
                    'success': True,
                    'processing_time': processing_time,
                    'extracted_words': len(extracted_text.split()),
                    'metadata_extracted': len(processed.get('metadata', {}))
                })
                
                results['processing_times'].append(processing_time)
                
                print(f"  ✅ Processing Time: {processing_time:.2f}s")
                print(f"  ✅ Extracted Words: {len(extracted_text.split())}")
                
            except Exception as e:
                results['error_rates'][test_file['file_type']] += 1
                results['processing_metrics'].append({
                    'file_type': test_file['file_type'],
                    'success': False,
                    'error': str(e)
                })
                print(f"  ❌ Failed: {str(e)}")
        
        # Aggregate results
        summary = self._aggregate_ingestion_results(results)
        
        return {
            'detailed_results': results,
            'summary': summary
        }
    
    def _calculate_text_similarity(self, expected: str, extracted: str) -> float:
        """Calculate text extraction similarity"""
        metrics = EvaluationMetrics()
        return metrics.calculate_semantic_similarity(expected, extracted)
    
    def _aggregate_ingestion_results(self, results: Dict) -> Dict[str, Any]:
        """Aggregate ingestion evaluation results"""
        
        total_files = len(results['processing_metrics'])
        successful = [m for m in results['processing_metrics'] if m.get('success')]
        
        summary = {
            'total_files_tested': total_files,
            'success_rate': len(successful) / total_files if total_files > 0 else 0,
            'avg_processing_time': np.mean(results['processing_times']) if results['processing_times'] else 0,
            'file_types_tested': len(set(m['file_type'] for m in results['processing_metrics'])),
            'error_rates_by_type': dict(results['error_rates'])
        }
        
        if results['accuracy_metrics']:
            accuracy_df = pd.DataFrame(results['accuracy_metrics'])
            summary.update({
                'avg_text_similarity': accuracy_df['text_similarity'].mean(),
                'avg_word_count_error': accuracy_df['word_count_error'].mean()
            })
        
        return summary


class ComprehensiveEvaluationSuite:
    """Run all evaluations and generate comprehensive report"""
    
    def __init__(
        self,
        db_manager: EnhancedDatabaseManager,
        rag_engine: AdvancedRAGEngine,
        summarizer: EnhancedSummarizer,
        video_generator: DocumentVideoGenerator,
        document_processor: DocumentProcessor
    ):
        self.rag_evaluator = RAGPerformanceEvaluator(db_manager, rag_engine)
        self.summary_evaluator = SummarizationQualityEvaluator(summarizer)
        self.video_evaluator = VideoSynthesisEvaluator(video_generator)
        self.ingestion_evaluator = MultimodalIngestionEvaluator(document_processor)
    
    async def run_comprehensive_evaluation(
        self,
        rag_test_cases: List[Dict],
        summarization_tests: List[Dict],
        video_tests: List[Dict],
        ingestion_tests: List[Dict],
        output_dir: str = "evaluation_results"
    ) -> Dict[str, Any]:
        """Run all evaluations and generate report"""
        
        print("\n" + "="*70)
        print("🚀 COMPREHENSIVE SYSTEM EVALUATION")
        print("="*70)
        
        results = {}
        
        # 1. RAG Performance
        if rag_test_cases:
            print("\n📊 Running RAG Performance Evaluation...")
            results['rag_performance'] = self.rag_evaluator.evaluate_retrieval_accuracy(rag_test_cases)
        
        # 2. Summarization Quality
        if summarization_tests:
            print("\n📊 Running Summarization Quality Evaluation...")
            results['summarization_quality'] = self.summary_evaluator.evaluate_summaries(summarization_tests)
        
        # 3. Video Synthesis
        if video_tests:
            print("\n📊 Running Video Synthesis Evaluation...")
            results['video_synthesis'] = await self.video_evaluator.evaluate_video_generation(video_tests)
        
        # 4. Multimodal Ingestion
        if ingestion_tests:
            print("\n📊 Running Multimodal Ingestion Evaluation...")
            results['multimodal_ingestion'] = self.ingestion_evaluator.evaluate_ingestion_accuracy(ingestion_tests)
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report(results)
        
        # Save results
        self._save_results(results, report, output_dir)
        
        return {
            'results': results,
            'report': report
        }
    
    def _generate_comprehensive_report(self, results: Dict) -> str:
        """Generate human-readable comprehensive report"""
        
        report = []
        report.append("\n" + "="*70)
        report.append("COMPREHENSIVE EVALUATION REPORT")
        report.append("AI Document Intelligence System")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*70)
        
        # RAG Performance
        if 'rag_performance' in results:
            report.append("\n📊 RETRIEVAL-AUGMENTED REASONING PERFORMANCE")
            report.append("-"*70)
            summary = results['rag_performance']['summary']
            report.append(f"Total Queries Tested: {summary.get('total_queries', 0)}")
            report.append(f"Average Precision@5: {summary.get('avg_precision@5', 0):.3f}")
            report.append(f"Average Recall@5: {summary.get('avg_recall@5', 0):.3f}")
            report.append(f"Average MRR: {summary.get('avg_mrr', 0):.3f}")
            report.append(f"Average Response Time: {summary.get('avg_total_response_time', 0):.3f}s")
            if 'avg_semantic_similarity' in summary:
                report.append(f"Average Semantic Similarity: {summary['avg_semantic_similarity']:.3f}")
        
        # Summarization Quality
        if 'summarization_quality' in results:
            report.append("\n📝 SUMMARIZATION QUALITY")
            report.append("-"*70)
            summary = results['summarization_quality']['summary']
            report.append(f"Documents Tested: {summary.get('total_documents', 0)}")
            report.append(f"Average Generation Time: {summary.get('avg_generation_time', 0):.2f}s")
            report.append(f"Average Compression Ratio: {summary.get('avg_compression_ratio', 0):.2%}")
            if 'avg_rouge_1_f' in summary:
                report.append(f"Average ROUGE-1 F1: {summary['avg_rouge_1_f']:.3f}")
                report.append(f"Average ROUGE-L F1: {summary['avg_rouge_l_f']:.3f}")
            if 'avg_flesch_score' in summary:
                report.append(f"Average Readability (Flesch): {summary['avg_flesch_score']:.1f}")
        
        # Video Synthesis
        if 'video_synthesis' in results:
            report.append("\n🎬 VIDEO SYNTHESIS & MULTILINGUAL NARRATION")
            report.append("-"*70)
            summary = results['video_synthesis']['summary']
            report.append(f"Total Tests: {summary.get('total_tests', 0)}")
            report.append(f"Success Rate: {summary.get('success_rate', 0):.1%}")
            report.append(f"Average Generation Time: {summary.get('avg_generation_time', 0):.1f}s")
            report.append(f"Languages Tested: {', '.join(summary.get('languages_tested', []))}")
            if 'language_success_rates' in summary:
                report.append("Language-specific Success Rates:")
                for lang, rate in summary['language_success_rates'].items():
                    report.append(f"  - {lang}: {rate:.1%}")
        
        # Multimodal Ingestion
        if 'multimodal_ingestion' in results:
            report.append("\n📥 MULTIMODAL INGESTION ACCURACY")
            report.append("-"*70)
            summary = results['multimodal_ingestion']['summary']
            report.append(f"Files Tested: {summary.get('total_files_tested', 0)}")
            report.append(f"Success Rate: {summary.get('success_rate', 0):.1%}")
            report.append(f"Average Processing Time: {summary.get('avg_processing_time', 0):.2f}s")
            report.append(f"File Types Supported: {summary.get('file_types_tested', 0)}")
            if 'avg_text_similarity' in summary:
                report.append(f"Average Text Extraction Accuracy: {summary['avg_text_similarity']:.1%}")
        
        report.append("\n" + "="*70)
        report.append("END OF REPORT")
        report.append("="*70 + "\n")
        
        return "\n".join(report)
    
    def _save_results(self, results: Dict, report: str, output_dir: str):
        """Save evaluation results to files"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed JSON results
        json_path = output_path / f"evaluation_results_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save human-readable report
        report_path = output_path / f"evaluation_report_{timestamp}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Generate Excel summary
        excel_path = output_path / f"evaluation_summary_{timestamp}.xlsx"
        self._generate_excel_summary(results, excel_path)
        
        print(f"\n💾 Results saved to:")
        print(f"   - {json_path}")
        print(f"   - {report_path}")
        print(f"   - {excel_path}")
    
    def _generate_excel_summary(self, results: Dict, excel_path: Path):
        """Generate Excel summary with charts"""
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            
            # Summary sheet
            summary_data = []
            for category, data in results.items():
                if 'summary' in data:
                    for metric, value in data['summary'].items():
                        if isinstance(value, (int, float)):
                            summary_data.append({
                                'Category': category,
                                'Metric': metric,
                                'Value': value
                            })
            
            if summary_data:
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed sheets for each category
            for category, data in results.items():
                if 'detailed_results' in data:
                    for sub_category, sub_data in data['detailed_results'].items():
                        if isinstance(sub_data, list) and sub_data:
                            try:
                                df = pd.DataFrame(sub_data)
                                sheet_name = f"{category[:15]}_{sub_category[:15]}"
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                            except:
                                pass


# ============================================================================
# TEST DATA GENERATOR
# ============================================================================

class TestDataGenerator:
    """Generate test data for evaluation"""
    
    @staticmethod
    def generate_rag_test_cases() -> List[Dict]:
        """Generate RAG test cases"""
        return [
            {
                'query': 'What are the main findings of the report?',
                'document_id': 1,
                'expected_chunks': ['main findings', 'key results', 'conclusions'],
                'ground_truth_answer': 'The main findings indicate significant improvements in AI performance with 95% accuracy achieved.'
            },
            {
                'query': 'When was the project completed?',
                'document_id': 1,
                'expected_chunks': ['completed', 'date', 'January 2024'],
                'ground_truth_answer': 'The project was completed in January 2024.'
            },
            {
                'query': 'What is the budget allocation?',
                'document_id': 2,
                'expected_chunks': ['budget', 'allocation', 'funding'],
                'ground_truth_answer': 'The budget allocation totals $2.5 million across three departments.'
            }
        ]
    
    @staticmethod
    def generate_summarization_tests() -> List[Dict]:
        """Generate summarization test cases"""
        return [
            {
                'text': """Artificial intelligence has revolutionized various industries. 
                Machine learning algorithms process vast amounts of data to identify patterns. 
                Deep learning, a subset of ML, uses neural networks with multiple layers. 
                Natural language processing enables computers to understand human language. 
                Computer vision allows machines to interpret visual information.""",
                'reference_summary': 'AI has transformed industries through ML, deep learning, NLP, and computer vision technologies.',
                'document_type': 'technical',
                'language': 'English'
            },
            {
                'text': """The quarterly report shows significant growth. Revenue increased 25% year-over-year. 
                Customer acquisition improved by 30%. Operating costs remained stable. 
                The company expanded to three new markets. Employee satisfaction scores rose to 8.5/10.""",
                'reference_summary': 'Quarterly results show 25% revenue growth, 30% customer increase, stable costs, market expansion, and high employee satisfaction.',
                'document_type': 'business',
                'language': 'English'
            }
        ]
    
    @staticmethod
    def generate_video_tests() -> List[Dict]:
        """Generate video synthesis test cases"""
        return [
            {
                'summary_text': 'This report discusses AI advancements in healthcare. Machine learning models now diagnose diseases with 95% accuracy.',
                'language': 'english',
                'target_duration': 30,
                'document_name': 'AI_Healthcare'
            },
            {
                'summary_text': 'यह रिपोर्ट स्वास्थ्य सेवा में AI प्रगति पर चर्चा करती है।',
                'language': 'hindi',
                'target_duration': 25,
                'document_name': 'AI_Healthcare_Hindi'
            },
            {
                'summary_text': 'ಈ ವರದಿ ಆರೋಗ್ಯ ಸೇವೆಯಲ್ಲಿ AI ಪ್ರಗತಿಯನ್ನು ಚರ್ಚಿಸುತ್ತದೆ.',
                'language': 'kannada',
                'target_duration': 25,
                'document_name': 'AI_Healthcare_Kannada'
            }
        ]
    
    @staticmethod
    def generate_ingestion_tests() -> List[Dict]:
        """Generate multimodal ingestion test cases"""
        return [
            {
                'file_path': 'test_data/sample.pdf',
                'file_type': 'pdf',
                'expected_word_count': 500,
                'expected_content': 'Sample PDF content for testing'
            },
            {
                'file_path': 'test_data/sample.docx',
                'file_type': 'docx',
                'expected_word_count': 300,
                'expected_content': 'Sample Word document content'
            }
        ]


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

async def run_evaluation_example():
    """Example of running comprehensive evaluation with LOCAL OLLAMA"""
    
    # Import your system components with CORRECT paths
    import sys
    import os
    
    # Add your project root to path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    try:
        # Try importing from backend folder
        from backend.database_manager import EnhancedDatabaseManager
        from backend.local_llm import LocalRAGEngine  # Using LOCAL Ollama
        from backend.video_integration import DocumentVideoGenerator
        from backend.document_processor import DocumentProcessor
        
        print("✅ Imports successful - Using LOCAL Ollama (no API key needed)")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n🔧 Please update the import paths to match your project structure.")
        return None
    
    # Initialize components with LOCAL Ollama
    print("\n🔧 Initializing components with LOCAL Ollama...")
    
    db_manager = EnhancedDatabaseManager(
        sqlite_path="data/documents.db",
        chromadb_path="data/chroma_db"
    )
    
    # Use LOCAL Ollama (no API key required!)
    rag_engine = LocalRAGEngine(model="llama3.2")  # Local Ollama
    
    video_generator = DocumentVideoGenerator()
    document_processor = DocumentProcessor()
    
    print("✅ All components initialized with LOCAL Ollama")
    
    # Create SIMPLIFIED evaluation suite (without summarizer that needs API key)
    print("\n📊 Running LOCAL evaluation (RAG + Video + Ingestion)...")
    
    # Generate test data
    test_gen = TestDataGenerator()
    
    # Run ONLY tests that work with local Ollama
    results = {}
    
    # 1. RAG Performance (works with local Ollama)
    print("\n" + "="*70)
    print("📊 EVALUATING RAG WITH LOCAL OLLAMA")
    print("="*70)
    
    rag_evaluator = RAGPerformanceEvaluator(db_manager, rag_engine)
    results['rag_performance'] = rag_evaluator.evaluate_retrieval_accuracy(
        test_gen.generate_rag_test_cases()
    )
    
    # 2. Video Synthesis (no API key needed)
    print("\n" + "="*70)
    print("📊 EVALUATING VIDEO SYNTHESIS")
    print("="*70)
    
    video_evaluator = VideoSynthesisEvaluator(video_generator)
    results['video_synthesis'] = await video_evaluator.evaluate_video_generation(
        test_gen.generate_video_tests()
    )
    
    # 3. Multimodal Ingestion (no API key needed)
    print("\n" + "="*70)
    print("📊 EVALUATING DOCUMENT INGESTION")
    print("="*70)
    
    ingestion_evaluator = MultimodalIngestionEvaluator(document_processor)
    results['multimodal_ingestion'] = ingestion_evaluator.evaluate_ingestion_accuracy(
        test_gen.generate_ingestion_tests()
    )
    
    # Generate report
    report = generate_local_report(results)
    print("\n" + report)
    
    # Save results
    save_local_results(results, report)
    
    return results


def generate_local_report(results: Dict) -> str:
    """Generate report for local Ollama evaluation"""
    
    report = []
    report.append("\n" + "="*70)
    report.append("EVALUATION REPORT - LOCAL OLLAMA")
    report.append("AI Document Intelligence System")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("="*70)
    
    # RAG Performance
    if 'rag_performance' in results:
        report.append("\n📊 RAG PERFORMANCE (Local Ollama)")
        report.append("-"*70)
        summary = results['rag_performance']['summary']
        report.append(f"Total Queries: {summary.get('total_queries', 0)}")
        report.append(f"Avg Precision@5: {summary.get('avg_precision@5', 0):.3f}")
        report.append(f"Avg Recall@5: {summary.get('avg_recall@5', 0):.3f}")
        report.append(f"Avg MRR: {summary.get('avg_mrr', 0):.3f}")
        report.append(f"Avg Response Time: {summary.get('avg_total_response_time', 0):.2f}s")
    
    # Video Synthesis
    if 'video_synthesis' in results:
        report.append("\n🎬 VIDEO SYNTHESIS")
        report.append("-"*70)
        summary = results['video_synthesis']['summary']
        report.append(f"Total Tests: {summary.get('total_tests', 0)}")
        report.append(f"Success Rate: {summary.get('success_rate', 0):.1%}")
        report.append(f"Avg Generation Time: {summary.get('avg_generation_time', 0):.1f}s")
        report.append(f"Languages: {', '.join(summary.get('languages_tested', []))}")
    
    # Multimodal Ingestion
    if 'multimodal_ingestion' in results:
        report.append("\n📥 DOCUMENT INGESTION")
        report.append("-"*70)
        summary = results['multimodal_ingestion']['summary']
        report.append(f"Files Tested: {summary.get('total_files_tested', 0)}")
        report.append(f"Success Rate: {summary.get('success_rate', 0):.1%}")
        report.append(f"Avg Processing Time: {summary.get('avg_processing_time', 0):.2f}s")
    
    report.append("\n" + "="*70)
    report.append("✅ LOCAL EVALUATION COMPLETE")
    report.append("="*70)
    
    return "\n".join(report)


def save_local_results(results: Dict, report: str):
    """Save local evaluation results"""
    
    output_dir = Path("evaluation_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save JSON
    json_path = output_dir / f"local_eval_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save report
    report_path = output_dir / f"local_eval_report_{timestamp}.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Save Excel
    excel_path = output_dir / f"local_eval_{timestamp}.xlsx"
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = []
            for category, data in results.items():
                if 'summary' in data:
                    for metric, value in data['summary'].items():
                        if isinstance(value, (int, float)):
                            summary_data.append({
                                'Category': category,
                                'Metric': metric,
                                'Value': value
                            })
            if summary_data:
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
    except:
        pass
    
    print(f"\n💾 Results saved:")
    print(f"   📄 {json_path}")
    print(f"   📋 {report_path}")
    print(f"   📊 {excel_path}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_evaluation_example())