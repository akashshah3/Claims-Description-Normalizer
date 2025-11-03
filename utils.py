"""
Utility functions for processing claims and displaying results
"""

import json
import re
from typing import Dict, List, Tuple


def parse_gemini_response(response_text: str) -> Dict:
    """
    Parse the Gemini API response and extract JSON
    
    Args:
        response_text: Raw text response from Gemini
        
    Returns:
        Parsed JSON dictionary
    """
    try:
        # Remove any markdown code blocks if present
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```"):
            # Extract content between code blocks
            cleaned_text = re.sub(r'^```(?:json)?\s*|\s*```$', '', cleaned_text, flags=re.MULTILINE)
        
        # Parse JSON
        result = json.loads(cleaned_text)
        return result
    except json.JSONDecodeError as e:
        # If parsing fails, return error structure
        return {
            "error": "Failed to parse response",
            "raw_response": response_text,
            "details": str(e)
        }


def extract_keywords_from_explanation(explanation: str) -> List[str]:
    """
    Extract keywords/phrases from the explanation that were mentioned as important
    
    Args:
        explanation: The extraction_explanation from Gemini
        
    Returns:
        List of keywords found in quotes
    """
    # Find all text within single or double quotes
    keywords = re.findall(r"['\"]([^'\"]+)['\"]", explanation)
    return keywords


def highlight_keywords_in_text(text: str, keywords: List[str]) -> str:
    """
    Highlight keywords in the original text using HTML/Markdown
    
    Args:
        text: Original claim description
        keywords: List of keywords to highlight
        
    Returns:
        Text with highlighted keywords (HTML)
    """
    highlighted_text = text
    
    # Sort keywords by length (longest first) to avoid partial replacements
    sorted_keywords = sorted(keywords, key=len, reverse=True)
    
    for keyword in sorted_keywords:
        # Case-insensitive replacement with HTML highlighting
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        highlighted_text = pattern.sub(
            lambda m: f'<span style="background-color: #ffeb3b; color: #000000; padding: 2px 4px; border-radius: 3px; font-weight: bold;">{m.group()}</span>',
            highlighted_text
        )
    
    return highlighted_text


def get_severity_color(severity: str) -> str:
    """
    Get color code for severity level
    
    Args:
        severity: Severity level string
        
    Returns:
        Hex color code
    """
    severity_colors = {
        "low": "#4CAF50",      # Green
        "medium": "#FF9800",   # Orange
        "high": "#F44336",     # Red
        "critical": "#9C27B0"  # Purple
    }
    return severity_colors.get(severity.lower(), "#757575")  # Default gray


def get_confidence_color(confidence: str) -> str:
    """
    Get color code for confidence level
    
    Args:
        confidence: Confidence level string
        
    Returns:
        Hex color code
    """
    confidence_colors = {
        "low": "#F44336",      # Red
        "medium": "#FF9800",   # Orange
        "high": "#4CAF50"      # Green
    }
    return confidence_colors.get(confidence.lower(), "#757575")  # Default gray


def get_confidence_percentage(confidence: str) -> int:
    """
    Convert confidence level to percentage for progress bar
    
    Args:
        confidence: Confidence level string
        
    Returns:
        Percentage value (0-100)
    """
    confidence_map = {
        "low": 40,
        "medium": 70,
        "high": 95
    }
    return confidence_map.get(confidence.lower(), 50)


def validate_extracted_data(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate that all required fields are present in extracted data
    
    Args:
        data: Extracted data dictionary
        
    Returns:
        Tuple of (is_valid, list_of_missing_fields)
    """
    required_fields = [
        "loss_type",
        "severity",
        "affected_assets",
        "estimated_loss",
        "incident_date",
        "location",
        "confidence",
        "extraction_explanation"
    ]
    
    missing_fields = [field for field in required_fields if field not in data]
    is_valid = len(missing_fields) == 0
    
    return is_valid, missing_fields


def format_field_name(field_name: str) -> str:
    """
    Convert snake_case field names to Title Case for display
    
    Args:
        field_name: Field name in snake_case
        
    Returns:
        Formatted field name
    """
    return field_name.replace('_', ' ').title()


def create_summary_stats(data: Dict) -> Dict[str, str]:
    """
    Create a summary statistics dictionary for quick overview
    
    Args:
        data: Extracted data dictionary
        
    Returns:
        Summary statistics
    """
    return {
        "Loss Type": data.get("loss_type", "Unknown"),
        "Severity": data.get("severity", "Unknown"),
        "Confidence": data.get("confidence", "Unknown"),
        "Estimated Loss": data.get("estimated_loss", "Not specified")
    }


def calculate_token_count(text: str) -> Tuple[int, int]:
    """
    Calculate word count and character count for text
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (word_count, char_count)
    """
    words = len(text.split())
    chars = len(text)
    return words, chars


def calculate_completeness_score(extracted_data: Dict) -> Tuple[int, int, float]:
    """
    Calculate how many fields were successfully extracted
    
    Args:
        extracted_data: Extracted data dictionary
        
    Returns:
        Tuple of (filled_count, total_count, percentage)
    """
    required_fields = [
        "loss_type",
        "severity",
        "affected_assets",
        "estimated_loss",
        "incident_date",
        "location",
        "confidence",
        "extraction_explanation"
    ]
    
    filled_count = 0
    for field in required_fields:
        value = extracted_data.get(field, "")
        # Check if field has meaningful data
        if value and value not in ["Unknown", "Not specified", "N/A", ""]:
            filled_count += 1
    
    total_count = len(required_fields)
    percentage = (filled_count / total_count) * 100 if total_count > 0 else 0
    
    return filled_count, total_count, percentage


def get_structure_quality_indicator(extracted_data: Dict) -> str:
    """
    Get a visual indicator of structure quality
    
    Args:
        extracted_data: Extracted data dictionary
        
    Returns:
        HTML string with quality indicator
    """
    _, _, completeness = calculate_completeness_score(extracted_data)
    
    if completeness >= 90:
        return "🟢 Excellent"
    elif completeness >= 70:
        return "🟡 Good"
    elif completeness >= 50:
        return "🟠 Fair"
    else:
        return "🔴 Poor"


def create_comparison_metrics(claim_text: str, extracted_data: Dict) -> Dict:
    """
    Create comprehensive metrics for before/after comparison
    
    Args:
        claim_text: Original claim text
        extracted_data: Extracted structured data
        
    Returns:
        Dictionary with comparison metrics
    """
    # Token counts
    words, chars = calculate_token_count(claim_text)
    
    # Completeness
    filled, total, completeness_pct = calculate_completeness_score(extracted_data)
    
    # Structure quality
    structure_quality = get_structure_quality_indicator(extracted_data)
    
    # Confidence
    confidence = extracted_data.get("confidence", "Unknown")
    confidence_pct = get_confidence_percentage(confidence)
    
    return {
        "word_count": words,
        "char_count": chars,
        "fields_filled": filled,
        "fields_total": total,
        "completeness_percentage": completeness_pct,
        "structure_quality": structure_quality,
        "confidence": confidence,
        "confidence_percentage": confidence_pct
    }
