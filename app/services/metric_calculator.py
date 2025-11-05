"""
Metric Calculator - Calculates quality metrics for LLM responses from text
"""
import re
import math
from typing import Dict


class MetricCalculator:
    """Service for calculating response quality metrics from text"""
    
    def calculate_all_metrics(self, text: str) -> Dict[str, Dict]:
        """
        Calculate all quality metrics for a response
        
        Returns:
            Dictionary mapping metric names to their values and metadata
        """
        return {
            "length_score": self.calculate_length_score(text),
            "coherence_score": self.calculate_coherence_score(text),
            "completeness_score": self.calculate_completeness_score(text),
            "structure_score": self.calculate_structure_score(text),
            "readability_score": self.calculate_readability_score(text),
            "overall_score": self.calculate_overall_score(text)
        }
    
    def calculate_length_score(self, text: str) -> Dict:
        """
        Calculate length appropriateness score
        - Too short: < 50 chars
        - Good: 50-2000 chars
        - Too long: > 2000 chars
        """
        length = len(text)
        
        if length < 50:
            score = max(0.0, length / 50.0)  # Linear scale from 0-50
        elif length <= 2000:
            score = 1.0  # Optimal length
        else:
            # Penalize very long responses
            excess = length - 2000
            score = max(0.0, 1.0 - (excess / 5000.0))  # Gradual penalty
        
        return {
            "value": round(score, 3),
            "metadata": {"length": length, "optimal_range": "50-2000"}
        }
    
    def calculate_coherence_score(self, text: str) -> Dict:
        """
        Calculate coherence score based on sentence structure and transitions
        """
        if not text.strip():
            return {"value": 0.0, "metadata": {}}
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return {"value": 0.5, "metadata": {"sentence_count": len(sentences)}}
        
        # Check for transition words
        transition_words = [
            'however', 'therefore', 'furthermore', 'moreover', 'additionally',
            'consequently', 'meanwhile', 'subsequently', 'thus', 'hence',
            'also', 'besides', 'further', 'next', 'then', 'finally'
        ]
        
        transition_count = sum(1 for word in transition_words if word.lower() in text.lower())
        transition_score = min(1.0, transition_count / max(len(sentences), 1))
        
        # Check sentence length variation (too uniform = less coherent)
        sentence_lengths = [len(s.split()) for s in sentences]
        if len(sentence_lengths) > 1:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            variation_score = min(1.0, variance / 100.0)  # Normalize
        else:
            variation_score = 0.5
        
        # Combine scores
        coherence = (transition_score * 0.4 + variation_score * 0.6)
        
        return {
            "value": round(coherence, 3),
            "metadata": {
                "sentence_count": len(sentences),
                "transition_count": transition_count
            }
        }
    
    def calculate_completeness_score(self, text: str) -> Dict:
        """
        Calculate completeness score - checks for conclusion and answer quality
        """
        if not text.strip():
            return {"value": 0.0, "metadata": {}}
        
        text_lower = text.lower()
        
        # Check for conclusion indicators
        conclusion_words = [
            'conclusion', 'summary', 'in summary', 'to conclude',
            'in conclusion', 'to sum up', 'overall', 'finally'
        ]
        has_conclusion = any(word in text_lower for word in conclusion_words)
        
        # Check for question words (might indicate incomplete answer)
        question_words = ['?', 'what', 'how', 'why', 'when', 'where', 'who']
        question_count = sum(1 for word in question_words if word in text_lower)
        has_questions = question_count > 3
        
        # Length factor (longer responses more likely complete)
        length_factor = min(1.0, len(text) / 500.0)
        
        # Calculate completeness
        if has_questions and not has_conclusion:
            completeness = 0.6 * length_factor
        elif has_conclusion:
            completeness = 0.8 + (0.2 * length_factor)
        else:
            completeness = 0.7 * length_factor
        
        return {
            "value": round(completeness, 3),
            "metadata": {
                "has_conclusion": has_conclusion,
                "question_count": question_count
            }
        }
    
    def calculate_structure_score(self, text: str) -> Dict:
        """
        Calculate structure score - checks for paragraphs, lists, headers
        """
        if not text.strip():
            return {"value": 0.0, "metadata": {}}
        
        # Check for paragraphs (double newlines)
        paragraphs = text.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        # Check for lists (bullet points or numbered)
        list_patterns = [
            r'^\s*[-*•]\s+',  # Bullet points
            r'^\s*\d+[\.\)]\s+',  # Numbered lists
        ]
        list_items = sum(
            len(re.findall(pattern, text, re.MULTILINE))
            for pattern in list_patterns
        )
        
        # Check for headers (lines that are short and followed by content)
        lines = text.split('\n')
        header_count = sum(
            1 for i, line in enumerate(lines)
            if len(line.strip()) < 80 and line.strip() and
            (i == 0 or lines[i-1].strip() == '') and
            (i < len(lines) - 1 and lines[i+1].strip() != '')
        )
        
        # Calculate structure score
        structure_score = 0.0
        
        # Paragraph structure (optimal: 2-5 paragraphs)
        if 2 <= paragraph_count <= 5:
            structure_score += 0.4
        elif paragraph_count > 5:
            structure_score += 0.3
        else:
            structure_score += 0.1
        
        # List structure
        if list_items > 0:
            structure_score += 0.3
        elif paragraph_count > 1:
            structure_score += 0.2
        
        # Header structure
        if header_count > 0:
            structure_score += 0.3
        else:
            structure_score += 0.1
        
        return {
            "value": round(min(1.0, structure_score), 3),
            "metadata": {
                "paragraph_count": paragraph_count,
                "list_items": list_items,
                "header_count": header_count
            }
        }
    
    def calculate_readability_score(self, text: str) -> Dict:
        """
        Calculate readability score using Flesch-like metrics
        """
        if not text.strip():
            return {"value": 0.0, "metadata": {}}
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {"value": 0.0, "metadata": {}}
        
        words = text.split()
        word_count = len(words)
        
        # Calculate average sentence length
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Simple readability score (inverse of complexity)
        # Optimal: 10-20 words per sentence, 4-5 chars per word
        sentence_score = 1.0 - abs(avg_sentence_length - 15) / 30.0  # Penalize deviation from 15
        sentence_score = max(0.0, min(1.0, sentence_score))
        
        word_score = 1.0 - abs(avg_word_length - 4.5) / 3.0  # Penalize deviation from 4.5
        word_score = max(0.0, min(1.0, word_score))
        
        readability = (sentence_score * 0.6 + word_score * 0.4)
        
        return {
            "value": round(readability, 3),
            "metadata": {
                "avg_sentence_length": round(avg_sentence_length, 1),
                "avg_word_length": round(avg_word_length, 1),
                "word_count": word_count
            }
        }
    
    def calculate_overall_score(self, text: str) -> Dict:
        """
        Calculate overall quality score (weighted average of all metrics)
        Note: This calculates metrics directly to avoid circular recursion
        """
        # Calculate individual metrics directly (don't call calculate_all_metrics)
        length_score = self.calculate_length_score(text)["value"]
        coherence_score = self.calculate_coherence_score(text)["value"]
        completeness_score = self.calculate_completeness_score(text)["value"]
        structure_score = self.calculate_structure_score(text)["value"]
        readability_score = self.calculate_readability_score(text)["value"]
        
        # Weights for different metrics
        weights = {
            "length_score": 0.15,
            "coherence_score": 0.25,
            "completeness_score": 0.20,
            "structure_score": 0.15,
            "readability_score": 0.25
        }
        
        overall = (
            length_score * weights["length_score"] +
            coherence_score * weights["coherence_score"] +
            completeness_score * weights["completeness_score"] +
            structure_score * weights["structure_score"] +
            readability_score * weights["readability_score"]
        )
        
        return {
            "value": round(overall, 3),
            "metadata": {
                "component_scores": {
                    "length_score": length_score,
                    "coherence_score": coherence_score,
                    "completeness_score": completeness_score,
                    "structure_score": structure_score,
                    "readability_score": readability_score
                }
            }
        }
