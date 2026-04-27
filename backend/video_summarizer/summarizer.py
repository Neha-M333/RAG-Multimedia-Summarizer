# from typing import Dict, Any
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from transformers import pipeline, MarianMTModel, MarianTokenizer
# import torch
# import config

# class MultilingualSummarizer:
#     """Enhanced Multilingual Summarizer with Modality-Specific Prompts"""
    
#     def __init__(self):
#         print("🤖 Initializing Enhanced Multilingual Summarizer...")
        
#         self.device = 0 if torch.cuda.is_available() else -1
#         print(f"   Using device: {'GPU' if self.device == 0 else 'CPU'}")
        
#         # Initialize embeddings
#         self.embeddings = HuggingFaceEmbeddings(
#             model_name=config.EMBEDDING_MODEL
#         )
        
#         # Text splitter for RAG
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=config.CHUNK_SIZE,
#             chunk_overlap=config.CHUNK_OVERLAP
#         )
        
#         # Load summarization model
#         print("   Loading summarization model...")
#         self.en_summarizer = pipeline(
#             "summarization",
#             model="facebook/bart-large-cnn",
#             device=self.device,
#             truncation=True
#         )
        
#         # Translation models cache
#         self.translation_models = {}
        
#         # Modality-specific prompt templates
#         self.prompt_templates = {
#             "pdf": "This is a PDF document. Summarize the main points, key findings, and important information in a clear and concise manner.",
#             "pptx": "This is a PowerPoint presentation. Summarize the key slides, main messages, and important takeaways from the presentation.",
#             "docx": "This is a Word document. Provide a comprehensive summary of the main topics, arguments, and conclusions.",
#             "xlsx": "This is an Excel spreadsheet containing data. Summarize the key data insights, trends, and important figures.",
#             "csv": "This is CSV data. Analyze and summarize the main data patterns, statistics, and significant findings.",
#             "image": "This is text extracted from an image. Summarize the visible information, key messages, and important content shown in the image.",
#             "audio": "This is transcribed audio content. Summarize the main discussion points, key messages, and important information from the audio.",
#             "general": "Summarize the following content in a clear, engaging, and informative manner."
#         }
        
#         print("✅ Enhanced Summarizer initialized")
    
#     def _load_translation_model(self, target_lang: str):
#         """Load translation model on demand with proper error handling"""
#         if target_lang in self.translation_models:
#             return
        
#         lang_model_map = {
#             "hindi": "Helsinki-NLP/opus-mt-en-hi",
#             "kannada": "Helsinki-NLP/opus-mt-en-dra"
#         }
        
#         if target_lang not in lang_model_map:
#             return
        
#         try:
#             print(f"   Loading translation model for {target_lang}...")
#             model_name = lang_model_map[target_lang]
            
#             tokenizer = MarianTokenizer.from_pretrained(model_name)
#             model = MarianMTModel.from_pretrained(model_name)
            
#             if torch.cuda.is_available():
#                 model = model.cuda()
            
#             self.translation_models[target_lang] = {
#                 "tokenizer": tokenizer,
#                 "model": model
#             }
#             print(f"✅ Loaded translation model for {target_lang}")
            
#         except Exception as e:
#             print(f"⚠️ Could not load translation model for {target_lang}: {e}")
    
#     async def generate_summary(
#         self, 
#         text: str, 
#         language: str,
#         max_words: int = config.MAX_SUMMARY_WORDS,
#         file_type: str = "general",
#         metadata: Dict = None
#     ) -> Dict[str, Any]:
#         """Generate intelligent summary with modality-specific prompts"""
#         try:
#             print(f"📝 Generating summary in {language} for {file_type}...")
            
#             # Validate input
#             if not text or len(text.strip()) < 20:
#                 raise ValueError("Input text is too short (minimum 20 characters required)")
            
#             # Step 1: Analyze document type and content
#             print("   Step 1: Analyzing document type and content...")
#             analysis = await self._analyze_document(text, file_type, metadata)
            
#             # Step 2: Create context-aware prompt
#             print("   Step 2: Creating modality-specific prompt...")
#             prompt = self._create_modality_prompt(text, file_type, analysis)
            
#             # Step 3: Generate English summary with enhanced prompting
#             print("   Step 3: Generating English summary...")
#             en_summary = await self._generate_english_summary(
#                 prompt, 
#                 analysis,
#                 max_words
#             )
            
#             if not en_summary or len(en_summary.strip()) < 20:
#                 raise ValueError("Failed to generate meaningful summary")
            
#             print(f"   ✅ English summary: {len(en_summary.split())} words")
            
#             # Step 4: Translate to target language if needed
#             if language == "english":
#                 final_summary = en_summary
#             else:
#                 print(f"   Step 4: Translating to {language}...")
#                 self._load_translation_model(language)
#                 final_summary = await self._translate_with_quality(en_summary, language)
#                 print(f"   ✅ Translated to {language}")
            
#             # Calculate metrics
#             word_count = len(final_summary.split())
#             estimated_duration = (word_count / config.WORDS_PER_MINUTE) * 60
            
#             print(f"✅ Summary complete: {word_count} words, ~{estimated_duration:.1f}s")
            
#             return {
#                 "success": True,
#                 "summary": final_summary,
#                 "language": language,
#                 "word_count": word_count,
#                 "estimated_duration": estimated_duration,
#                 "metadata": {
#                     "original_length": len(text.split()),
#                     "compression_ratio": len(text.split()) / word_count if word_count > 0 else 0,
#                     "file_type": file_type,
#                     "document_analysis": analysis
#                 }
#             }
#         except Exception as e:
#             print(f"❌ Summary generation failed: {e}")
#             import traceback
#             traceback.print_exc()
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "summary": "",
#                 "language": language
#             }
    
#     async def _analyze_document(self, text: str, file_type: str, metadata: Dict) -> Dict[str, Any]:
#         """Comprehensive document analysis"""
        
#         analysis = {
#             "file_type": file_type,
#             "length": len(text.split()),
#             "has_numbers": any(char.isdigit() for char in text),
#             "metadata": metadata or {}
#         }
        
#         # File type specific analysis
#         if file_type == "image":
#             analysis["type"] = "visual_content"
#             analysis["focus"] = "visual elements and text visible in image"
#         elif file_type == "pptx":
#             analysis["type"] = "presentation"
#             analysis["focus"] = "key slides and main messages"
#             analysis["slide_count"] = metadata.get("slides", 0) if metadata else 0
#         elif file_type == "xlsx" or file_type == "csv":
#             analysis["type"] = "data_content"
#             analysis["focus"] = "data insights and statistics"
#         elif file_type == "audio":
#             analysis["type"] = "spoken_content"
#             analysis["focus"] = "discussion points and messages"
#         else:
#             analysis["type"] = "document"
#             analysis["focus"] = "main content and key points"
        
#         return analysis
    
#     def _create_modality_prompt(self, text: str, file_type: str, analysis: Dict) -> str:
#         """Create context-aware prompt based on file type"""
        
#         base_prompt = self.prompt_templates.get(file_type, self.prompt_templates["general"])
        
#         # Enhance prompt based on analysis
#         if file_type == "image":
#             prompt = f"{base_prompt}\n\nExtracted text from image:\n{text}\n\nProvide a clear summary of what information is shown in this image."
#         elif file_type == "pptx":
#             slide_count = analysis.get("slide_count", "multiple")
#             prompt = f"{base_prompt}\n\nThis presentation contains {slide_count} slides.\n\nContent:\n{text}\n\nSummarize the main presentation flow and key takeaways."
#         elif file_type in ["xlsx", "csv"]:
#             prompt = f"{base_prompt}\n\nData content:\n{text}\n\nAnalyze and present the key insights from this data."
#         elif file_type == "audio":
#             prompt = f"{base_prompt}\n\nTranscribed audio:\n{text}\n\nSummarize the main discussion and key points."
#         else:
#             prompt = f"{base_prompt}\n\nContent:\n{text}"
        
#         return prompt
    
#     async def _generate_english_summary(
#         self,
#         prompt: str,
#         analysis: Dict,
#         max_words: int
#     ) -> str:
#         """Generate high-quality English summary"""
        
#         try:
#             # Prepare text for summarization
#             text_to_summarize = prompt
            
#             # If text is too long, use key extraction
#             words = text_to_summarize.split()
#             if len(words) > 500:
#                 # Extract most important sentences
#                 sentences = [s.strip() + '.' for s in text_to_summarize.split('.') if s.strip()]
#                 scored = [(s, self._score_sentence_importance(s, analysis)) for s in sentences[:50]]
#                 scored.sort(key=lambda x: x[1], reverse=True)
#                 text_to_summarize = " ".join([s for s, _ in scored[:15]])
            
#             # Calculate target length
#             target_max = min(max_words, 120)
#             target_min = max(40, target_max // 2)
            
#             print(f"   Generating summary (target: {target_min}-{target_max} words)...")
            
#             # Generate summary
#             result = self.en_summarizer(
#                 text_to_summarize,
#                 max_length=target_max,
#                 min_length=target_min,
#                 do_sample=False,
#                 truncation=True,
#                 no_repeat_ngram_size=3,
#                 length_penalty=1.0,
#                 num_beams=4
#             )
            
#             if not result or len(result) == 0:
#                 raise ValueError("Summarizer returned empty result")
            
#             summary = result[0]['summary_text']
            
#             # Post-process
#             summary = self._optimize_summary_quality(summary, analysis)
            
#             return summary
            
#         except Exception as e:
#             print(f"   Error in summary generation: {e}")
#             # Fallback: extractive summary
#             sentences = [s.strip() + '.' for s in prompt.split('.')[:4] if s.strip()]
#             return " ".join(sentences)
    
#     def _score_sentence_importance(self, sentence: str, analysis: Dict) -> float:
#         """Score sentence importance"""
#         score = 0.0
#         sent_lower = sentence.lower()
        
#         # Universal importance indicators
#         importance_words = [
#             'important', 'significant', 'key', 'main', 'primary',
#             'shows', 'demonstrates', 'indicates', 'reveals', 'found'
#         ]
        
#         for word in importance_words:
#             if word in sent_lower:
#                 score += 2.0
        
#         # Has numbers (often important facts)
#         if any(char.isdigit() for char in sentence):
#             score += 1.5
        
#         # Optimal length
#         word_count = len(sentence.split())
#         if 10 <= word_count <= 25:
#             score += 1.0
        
#         return score
    
#     def _optimize_summary_quality(self, summary: str, analysis: Dict) -> str:
#         """Optimize summary quality for speech"""
        
#         # Ensure proper ending
#         if not summary.endswith('.'):
#             summary += '.'
        
#         # Replace abbreviations
#         replacements = {
#             ' e.g. ': ' for example ',
#             ' i.e. ': ' that is ',
#             ' etc.': ' and so on',
#             ' vs. ': ' versus '
#         }
        
#         for abbr, full in replacements.items():
#             summary = summary.replace(abbr, full)
        
#         # Clean up whitespace
#         summary = ' '.join(summary.split())
        
#         return summary.strip()
    
#     async def _translate_with_quality(self, text: str, target_lang: str) -> str:
#         """High-quality translation to Hindi or Kannada"""
        
#         if target_lang not in self.translation_models:
#             print(f"⚠️ Translation model not available for {target_lang}, using English")
#             return text
        
#         try:
#             tokenizer = self.translation_models[target_lang]["tokenizer"]
#             model = self.translation_models[target_lang]["model"]
            
#             # Split into sentences for better translation
#             sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
#             translated_sentences = []
            
#             print(f"   Translating {len(sentences)} sentences...")
            
#             for i, sentence in enumerate(sentences):
#                 try:
#                     # Tokenize
#                     inputs = tokenizer(
#                         sentence,
#                         return_tensors="pt",
#                         padding=True,
#                         truncation=True,
#                         max_length=512
#                     )
                    
#                     if torch.cuda.is_available():
#                         inputs = {k: v.cuda() for k, v in inputs.items()}
                    
#                     # Generate translation
#                     with torch.no_grad():
#                         outputs = model.generate(
#                             **inputs,
#                             max_length=512,
#                             num_beams=5,
#                             early_stopping=True,
#                             length_penalty=1.2,
#                             no_repeat_ngram_size=3
#                         )
                    
#                     translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
#                     translated_sentences.append(translated)
                    
#                     if (i + 1) % 5 == 0:
#                         print(f"   Translated {i + 1}/{len(sentences)} sentences")
                    
#                 except Exception as e:
#                     print(f"   ⚠️ Failed to translate sentence {i}: {e}")
#                     translated_sentences.append(sentence)
            
#             final_translation = " ".join(translated_sentences)
            
#             print(f"   ✅ Translation complete: {len(final_translation.split())} words")
            
#             return final_translation
            
#         except Exception as e:
#             print(f"⚠️ Translation failed: {e}")
#             return text
"""
ULTRA-INTELLIGENT Multilingual Summarizer
Creates engaging, natural summaries perfect for video narration
"""
"""
COMPLETELY FIXED Multilingual Summarizer with VERIFIED Hindi/Kannada Translation
Using deep-translator (no dependency conflicts)
"""

from typing import Dict, Any, List
from transformers import pipeline
import torch
import re
from backend.video_summarizer import config

# Import Deep Translator (better than googletrans, no conflicts)
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
    print("✅ Deep Translator available for Hindi/Kannada")
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("⚠️ Install deep-translator: pip install deep-translator")


class MultilingualSummarizer:
    """
    Intelligent summarizer with PROPER Hindi/Kannada translation
    """
    
    def __init__(self):
        print("🤖 Initializing Enhanced Multilingual Summarizer...")
        
        self.device = 0 if torch.cuda.is_available() else -1
        print(f"   Using device: {'GPU' if self.device == 0 else 'CPU'}")
        
        # Initialize translators for each language
        self.translators = {}
        if TRANSLATOR_AVAILABLE:
            try:
                self.translators['hindi'] = GoogleTranslator(source='en', target='hi')
                self.translators['kannada'] = GoogleTranslator(source='en', target='kn')
                print("   ✅ Hindi & Kannada translators initialized")
            except Exception as e:
                print(f"   ⚠️ Translator initialization failed: {e}")
        
        # Load English summarization model
        print("   Loading summarization model...")
        self.en_summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=self.device,
            truncation=True
        )
        
        print("✅ Enhanced Summarizer initialized")
    
    async def generate_summary(
        self,
        text: str,
        language: str,
        max_words: int = 150,
        file_type: str = "general",
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Generate intelligent summary with PROPER translation
        """
        try:
            print(f"\n📝 Generating summary for {file_type} in {language}...")
            
            # Validate input
            if not text or len(text.strip()) < 20:
                raise ValueError("Input text is too short")
            
            # Step 1: Create engaging English summary
            print("   Step 1: Creating English summary...")
            en_summary = await self._create_engaging_summary(text, file_type, max_words)
            
            if not en_summary or len(en_summary.strip()) < 20:
                raise ValueError("Failed to generate meaningful summary")
            
            print(f"   ✅ English summary: {len(en_summary.split())} words")
            print(f"   Preview: {en_summary[:150]}...")
            
            # Step 2: Translate to target language
            if language == "english":
                final_summary = en_summary
                print("   Using English summary directly")
            else:
                print(f"   Step 2: Translating to {language}...")
                final_summary = await self._translate_summary(en_summary, language)
                
                if final_summary == en_summary:
                    print(f"   ⚠️ Translation failed, using English")
                else:
                    print(f"   ✅ Successfully translated to {language}")
                    print(f"   Preview: {final_summary[:150]}...")
            
            # Verify translation quality
            await self._verify_translation(final_summary, language)
            
            # Calculate metrics
            word_count = len(final_summary.split())
            estimated_duration = (word_count / config.WORDS_PER_MINUTE) * 60
            
            result = {
                "success": True,
                "summary": final_summary,
                "language": language,
                "word_count": word_count,
                "estimated_duration": estimated_duration,
                "metadata": {
                    "file_type": file_type,
                    "original_length": len(text.split()),
                    "compression_ratio": len(text.split()) / word_count if word_count > 0 else 0,
                    "translation_method": "deep_translator" if language != "english" else "native"
                }
            }
            
            print(f"\n✅ Summary generation complete!")
            print(f"   Language: {language}")
            print(f"   Words: {word_count}")
            print(f"   Duration: ~{estimated_duration:.1f}s")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Summary generation failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "summary": "",
                "language": language
            }
    
    async def _create_engaging_summary(
        self,
        text: str,
        file_type: str,
        max_words: int
    ) -> str:
        """Create engaging English summary"""
        
        try:
            # Document-specific introductions
            intros = {
                "pdf": "Let me explain what this document covers.",
                "pptx": "This presentation discusses several key points.",
                "docx": "Here's what this document is about.",
                "xlsx": "Let me share the insights from this data.",
                "csv": "This data reveals interesting patterns.",
                "image": "This image shows important information.",
                "audio": "Here's what was discussed.",
                "general": "Let me summarize this content for you."
            }
            
            intro = intros.get(file_type, intros["general"])
            
            # Extract key sentences
            key_text = self._extract_key_info(text)
            
            # Calculate target length
            target_max = min(max_words, 120)
            target_min = max(50, target_max // 2)
            
            print(f"   Generating summary (target: {target_min}-{target_max} words)...")
            
            # Generate with AI
            result = self.en_summarizer(
                key_text,
                max_length=target_max,
                min_length=target_min,
                do_sample=False,
                truncation=True,
                no_repeat_ngram_size=3,
                num_beams=4
            )
            
            if not result or len(result) == 0:
                raise ValueError("Summarizer returned empty result")
            
            core_summary = result[0]['summary_text']
            
            # Make it engaging
            summary = self._make_engaging(intro, core_summary, file_type)
            
            # Optimize for speech
            summary = self._optimize_for_speech(summary)
            
            return summary
            
        except Exception as e:
            print(f"   ⚠️ AI summarization failed: {e}")
            # Fallback: extractive
            sentences = self._split_sentences(text)
            return ". ".join(sentences[:5]) + "."
    
    def _extract_key_info(self, text: str) -> str:
        """Extract most important sentences"""
        
        sentences = self._split_sentences(text)
        
        if len(sentences) <= 10:
            return text
        
        # Score sentences
        scored = []
        for sent in sentences:
            score = self._score_sentence(sent)
            if score > 0:
                scored.append((sent, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s for s, _ in scored[:15]]
        
        return " ".join(top_sentences)
    
    def _score_sentence(self, sentence: str) -> float:
        """Score sentence importance"""
        
        score = 0.0
        sent_lower = sentence.lower()
        
        # Important keywords
        keywords = [
            'important', 'significant', 'key', 'main', 'primary',
            'shows', 'demonstrates', 'reveals', 'found', 'data',
            'conclusion', 'summary', 'result'
        ]
        
        for word in keywords:
            if word in sent_lower:
                score += 2.0
        
        # Has numbers
        if any(c.isdigit() for c in sentence):
            score += 1.5
        
        # Good length
        words = len(sentence.split())
        if 10 <= words <= 25:
            score += 1.0
        
        return score
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split into sentences"""
        sentences = re.split(r'[.!?।]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _make_engaging(self, intro: str, summary: str, file_type: str) -> str:
        """Make summary engaging for narration"""
        
        parts = [intro]
        
        # Clean summary
        summary = summary.strip()
        if not summary.endswith('.'):
            summary += '.'
        
        parts.append(summary)
        
        # Add ending
        endings = {
            "pdf": "These are the key points from the document.",
            "pptx": "These are the main takeaways from the presentation.",
            "xlsx": "These insights summarize the data patterns.",
            "csv": "This covers the important findings.",
            "image": "This describes the key information shown.",
            "audio": "These were the main points discussed.",
            "general": "This summarizes the main content."
        }
        
        parts.append(endings.get(file_type, endings["general"]))
        
        return " ".join(parts)
    
    def _optimize_for_speech(self, text: str) -> str:
        """Optimize text for natural speech"""
        
        # Replace abbreviations
        replacements = {
            ' e.g. ': ' for example ',
            ' i.e. ': ' that is ',
            ' etc.': ' and so on',
            ' vs. ': ' versus ',
            '%': ' percent',
            ' & ': ' and ',
            ' + ': ' plus '
        }
        
        for abbr, full in replacements.items():
            text = text.replace(abbr, full)
        
        # Clean numbers
        text = re.sub(r'(\d+)\.(\d+)', r'\1 point \2', text)
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        if not text.endswith('.'):
            text += '.'
        
        return text.strip()
    
    async def _translate_summary(self, text: str, target_lang: str) -> str:
        """
        Translate using Deep Translator (reliable, no conflicts)
        """
        
        if not TRANSLATOR_AVAILABLE:
            print(f"   ⚠️ Deep Translator not available, returning English")
            return text
        
        if target_lang not in self.translators:
            print(f"   ⚠️ No translator for {target_lang}")
            return text
        
        try:
            translator = self.translators[target_lang]
            
            print(f"   Translating to {target_lang}...")
            
            # Split into chunks (Google Translate has 5000 char limit)
            sentences = self._split_sentences(text)
            translated_sentences = []
            
            for i, sentence in enumerate(sentences):
                try:
                    # Translate sentence
                    if len(sentence.strip()) < 5:
                        translated_sentences.append(sentence)
                        continue
                    
                    translated = translator.translate(sentence)
                    translated_sentences.append(translated)
                    
                    if (i + 1) % 3 == 0:
                        print(f"   Translated {i + 1}/{len(sentences)} sentences")
                    
                    # Show first translation as sample
                    if i == 0:
                        print(f"   Sample: '{sentence[:50]}...'")
                        print(f"        -> '{translated[:50]}...'")
                    
                except Exception as e:
                    print(f"   ⚠️ Failed sentence {i}: {e}")
                    translated_sentences.append(sentence)
            
            # Join all translated sentences
            final_translation = " ".join(translated_sentences)
            
            # Verify translation worked
            if final_translation.strip() == text.strip():
                print(f"   ⚠️ Translation unchanged - may have failed")
                return text
            
            print(f"   ✅ Translation complete: {len(final_translation.split())} words")
            
            return final_translation
            
        except Exception as e:
            print(f"   ❌ Translation failed: {e}")
            import traceback
            traceback.print_exc()
            return text
    
    async def _verify_translation(self, text: str, language: str) -> None:
        """Verify translation quality by checking character sets"""
        
        if language == "hindi":
            # Check for Devanagari script (U+0900 to U+097F)
            hindi_chars = [c for c in text if '\u0900' <= c <= '\u097F']
            
            if hindi_chars:
                print(f"   ✅ VERIFIED: {len(hindi_chars)} Hindi characters found")
                print(f"   ✅ Sample Hindi text: {text[:80]}")
            else:
                print(f"   ❌ WARNING: NO HINDI CHARACTERS FOUND!")
                print(f"   Text appears to be: {text[:80]}")
                print(f"   This means translation FAILED - will produce English audio")
        
        elif language == "kannada":
            # Check for Kannada script (U+0C80 to U+0CFF)
            kannada_chars = [c for c in text if '\u0C80' <= c <= '\u0CFF']
            
            if kannada_chars:
                print(f"   ✅ VERIFIED: {len(kannada_chars)} Kannada characters found")
                print(f"   ✅ Sample Kannada text: {text[:80]}")
            else:
                print(f"   ❌ WARNING: NO KANNADA CHARACTERS FOUND!")
                print(f"   Text appears to be: {text[:80]}")
                print(f"   This means translation FAILED - will produce English audio")
        
        elif language == "english":
            print(f"   ✅ English summary ready")