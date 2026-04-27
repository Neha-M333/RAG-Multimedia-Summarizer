"""
Multilingual translation module for English, Hindi, and Kannada
"""
from typing import Dict, Optional
import openai
from googletrans import Translator as GoogleTranslator
    
class Translator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.google_translator = GoogleTranslator()
        
        # Language codes
        self.lang_codes = {
            'English': 'en',
            'Hindi': 'hi',
            'Kannada': 'kn'
        }
    
    def translate_text(self, text: str, target_language: str, 
                       source_language: str = 'auto') -> Dict:
        """
        Translate text to target language
        Uses OpenAI for better quality if API key available, else Google Translate
        """
        target_code = self.lang_codes.get(target_language, target_language)
        
        if self.api_key:
            return self._translate_with_openai(text, target_language)
        else:
            return self._translate_with_google(text, target_code, source_language)
    
    def _translate_with_openai(self, text: str, target_language: str) -> Dict:
        """Use OpenAI for high-quality translation"""
        try:
            openai.api_key = self.api_key
            
            prompt = f"""Translate the following text to {target_language}. 
Maintain the tone and meaning accurately.

Text: {text}

Translation:"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a professional translator specializing in English, Hindi, and Kannada."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            return {
                'translated_text': translated_text,
                'source_language': 'auto',
                'target_language': target_language,
                'method': 'openai'
            }
        
        except Exception as e:
            # Fallback to Google Translate
            target_code = self.lang_codes.get(target_language, 'en')
            return self._translate_with_google(text, target_code, 'auto')
    
    def _translate_with_google(self, text: str, target_code: str, 
                              source_code: str = 'auto') -> Dict:
        """Use Google Translate as fallback"""
        try:
            result = self.google_translator.translate(
                text, 
                dest=target_code, 
                src=source_code
            )
            
            return {
                'translated_text': result.text,
                'source_language': result.src,
                'target_language': target_code,
                'method': 'google'
            }
        
        except Exception as e:
            return {
                'translated_text': text,
                'source_language': source_code,
                'target_language': target_code,
                'method': 'error',
                'error': str(e)
            }
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the text"""
        try:
            detection = self.google_translator.detect(text)
            
            # Map code to name
            code_to_name = {v: k for k, v in self.lang_codes.items()}
            return code_to_name.get(detection.lang, detection.lang)
        
        except Exception:
            return 'unknown'
    
    def translate_batch(self, texts: list, target_language: str) -> list:
        """Translate multiple texts"""
        return [
            self.translate_text(text, target_language)
            for text in texts
        ]