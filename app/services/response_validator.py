"""
Response Validator - Validates and sanitizes LLM responses
"""
import re
from typing import Dict, Tuple


class ResponseValidator:
    """Service for validating and cleaning LLM responses"""
    
    # Patterns that indicate corrupted or low-quality responses
    CORRUPTION_PATTERNS = [
        r'[a-zA-Z]{20,}',  # Very long words (likely gibberish)
        r'[^\w\s]{10,}',  # Many consecutive special characters
        r'[A-Z]{15,}',  # Many consecutive uppercase letters
        r'[a-z]{20,}',  # Many consecutive lowercase letters
        r'\d{10,}',  # Very long number sequences
    ]
    
    # Common code/script patterns that shouldn't be in normal text
    CODE_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'function\s+\w+\s*\([^)]*\)\s*\{',
        r'import\s+\w+',
        r'from\s+\w+\s+import',
        r'class\s+\w+',
        r'def\s+\w+\s*\(',
        r'const\s+\w+\s*=',
        r'var\s+\w+\s*=',
        r'\.(js|py|html|css|json|xml)\b',
    ]
    
    def validate_response(self, text: str, finish_reason: str = "stop") -> Dict[str, any]:
        """
        Validate and analyze a response
        
        Returns:
            Dictionary with validation results:
            - is_valid: bool
            - is_corrupted: bool
            - is_truncated: bool
            - corruption_score: float (0-1, higher = more corrupted)
            - cleaned_text: str (sanitized version)
            - warnings: list of warning messages
        """
        warnings = []
        is_truncated = finish_reason == "length"
        corruption_score = 0.0
        cleaned_text = text
        
        # Check for truncation
        if is_truncated:
            warnings.append("Response was truncated due to max_tokens limit")
        
        # Calculate corruption score
        corruption_indicators = 0
        total_checks = 0
        
        # Check for corruption patterns
        for pattern in self.CORRUPTION_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                corruption_indicators += len(matches)
            total_checks += 1
        
        # Check for code patterns (unusual in normal text responses)
        code_matches = 0
        for pattern in self.CODE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                code_matches += 1
        
        # Check for excessive special characters
        special_char_ratio = len(re.findall(r'[^\w\s]', text)) / max(len(text), 1)
        if special_char_ratio > 0.3:  # More than 30% special chars
            corruption_indicators += 1
        
        # Check for very long words (likely gibberish)
        words = text.split()
        if words:
            avg_word_length = sum(len(w) for w in words) / len(words)
            if avg_word_length > 15:  # Unusually long average word length
                corruption_indicators += 1
        
        # Calculate corruption score (0-1)
        corruption_score = min(1.0, corruption_indicators / max(total_checks, 1))
        
        # Check for suspicious patterns
        if code_matches > 2:
            corruption_score += 0.3
            warnings.append("Response contains code-like patterns")
        
        # Check response quality
        if len(text.strip()) < 10:
            corruption_score = 1.0
            warnings.append("Response is extremely short")
        elif corruption_score > 0.5:
            warnings.append("Response may be corrupted or low quality")
        
        # Clean the text (basic sanitization)
        cleaned_text = self.clean_text(text)
        
        # Determine if corrupted
        is_corrupted = corruption_score > 0.6 or (is_truncated and corruption_score > 0.3)
        
        # Overall validity
        is_valid = not is_corrupted and len(text.strip()) > 0
        
        return {
            "is_valid": is_valid,
            "is_corrupted": is_corrupted,
            "is_truncated": is_truncated,
            "corruption_score": round(corruption_score, 3),
            "cleaned_text": cleaned_text,
            "warnings": warnings,
            "original_length": len(text),
            "cleaned_length": len(cleaned_text)
        }
    
    def clean_text(self, text: str) -> str:
        """
        Basic text cleaning - remove excessive whitespace and normalize
        Also attempts to truncate at corruption point if detected
        """
        if not text:
            return ""
        
        # Try to detect where text becomes corrupted
        # Look for sudden appearance of code-like patterns or excessive special chars
        words = text.split()
        if len(words) > 50:
            # Check for sudden degradation in text quality
            corruption_point = None
            for i in range(len(words) - 100, len(words)):
                if i < 0:
                    continue
                # Check if this section has corruption indicators
                section = ' '.join(words[max(0, i-10):i+10])
                special_char_ratio = len(re.findall(r'[^\w\s]', section)) / max(len(section), 1)
                avg_word_len = sum(len(w) for w in words[max(0, i-10):i+10]) / max(len(words[max(0, i-10):i+10]), 1)
                
                # If we detect corruption indicators, mark this as potential break point
                if special_char_ratio > 0.4 or avg_word_len > 20:
                    corruption_point = i
                    break
            
            # If we found a corruption point and it's not too early, truncate there
            if corruption_point and corruption_point > len(words) * 0.3:  # At least 30% of text is good
                # Find the last complete sentence before corruption
                truncated_text = ' '.join(words[:corruption_point])
                # Find last sentence ending
                last_period = max(
                    truncated_text.rfind('.'),
                    truncated_text.rfind('!'),
                    truncated_text.rfind('?')
                )
                if last_period > len(truncated_text) * 0.8:  # Sentence ending is near the end
                    text = truncated_text[:last_period + 1]
                else:
                    text = truncated_text
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def should_reject_response(self, text: str, finish_reason: str = "stop") -> Tuple[bool, str]:
        """
        Determine if a response should be rejected
        Returns: (should_reject, reason)
        """
        validation = self.validate_response(text, finish_reason)
        
        if not validation["is_valid"]:
            return True, "Response is invalid or corrupted"
        
        if validation["is_corrupted"]:
            return True, f"Response appears corrupted (score: {validation['corruption_score']})"
        
        if len(text.strip()) < 10:
            return True, "Response is too short"
        
        return False, ""
