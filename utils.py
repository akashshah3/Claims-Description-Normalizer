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


def parse_estimated_loss(loss_str: str) -> float:
    """
    Extract numeric value from estimated loss string
    
    Args:
        loss_str: Estimated loss string (e.g., "₹7,000", "$5000", "Over $200,000")
        
    Returns:
        Numeric value or 0 if not parseable
    """
    if not loss_str or loss_str.lower() in ["not specified", "unknown", "n/a"]:
        return 0
    
    # Remove currency symbols and common words
    cleaned = loss_str.lower().replace('₹', '').replace('$', '').replace('€', '')
    cleaned = cleaned.replace('over', '').replace('around', '').replace('approximately', '')
    cleaned = cleaned.replace(',', '').strip()
    
    try:
        # Extract first number found
        import re
        numbers = re.findall(r'\d+\.?\d*', cleaned)
        if numbers:
            return float(numbers[0])
    except:
        pass
    
    return 0


def generate_recommendations(extracted_data: Dict) -> List[Dict]:
    """
    Generate actionable recommendations based on claim data using rule-based logic
    
    Args:
        extracted_data: Extracted claim data
        
    Returns:
        List of recommendation dictionaries with action, priority, category, and icon
    """
    recommendations = []
    
    severity = extracted_data.get("severity", "Unknown").lower()
    confidence = extracted_data.get("confidence", "Unknown").lower()
    loss_type = extracted_data.get("loss_type", "Unknown").lower()
    estimated_loss = parse_estimated_loss(extracted_data.get("estimated_loss", "0"))
    incident_date = extracted_data.get("incident_date", "Not specified")
    location = extracted_data.get("location", "Not specified")
    
    # Check for missing critical information
    missing_info = []
    if incident_date.lower() in ["not specified", "unknown"]:
        missing_info.append("incident date")
    if location.lower() in ["not specified", "unknown"]:
        missing_info.append("location")
    if estimated_loss == 0:
        missing_info.append("cost estimate")
    
    # Rule 1: Low Confidence - Always request clarification
    if confidence == "low":
        recommendations.append({
            "action": "Request Additional Documentation",
            "priority": "High",
            "category": "Verification",
            "icon": "📄",
            "reasoning": "Low confidence in data extraction. Need customer clarification to ensure accuracy."
        })
        recommendations.append({
            "action": "Contact Customer for Details",
            "priority": "High",
            "category": "Communication",
            "icon": "📞",
            "reasoning": "Missing or unclear information requires direct customer contact."
        })
    
    # Rule 2: Low Severity + High Confidence = Fast Track
    if severity == "low" and confidence == "high" and estimated_loss < 10000:
        recommendations.append({
            "action": "Fast-track Approval",
            "priority": "High",
            "category": "Processing",
            "icon": "🚀",
            "reasoning": "Low severity with high confidence and minimal cost. Safe for quick approval."
        })
        recommendations.append({
            "action": "Simple Phone Verification",
            "priority": "Medium",
            "category": "Verification",
            "icon": "📞",
            "reasoning": "Quick call to confirm details before approval."
        })
    
    # Rule 3: Medium Severity = Standard Process
    elif severity == "medium":
        recommendations.append({
            "action": "Standard Review Process",
            "priority": "Medium",
            "category": "Processing",
            "icon": "📋",
            "reasoning": "Medium severity requires standard assessment procedures."
        })
        recommendations.append({
            "action": "Request Photos/Documentation",
            "priority": "Medium",
            "category": "Documentation",
            "icon": "📸",
            "reasoning": "Visual evidence needed to validate damage extent."
        })
        recommendations.append({
            "action": "Schedule Assessment Within 5 Days",
            "priority": "Medium",
            "category": "Administrative",
            "icon": "📅",
            "reasoning": "Timely assessment ensures accurate damage evaluation."
        })
    
    # Rule 4: High/Critical Severity = Intensive Review
    elif severity in ["high", "critical"]:
        recommendations.append({
            "action": "Detailed Investigation Required",
            "priority": "Critical",
            "category": "Processing",
            "icon": "🔍",
            "reasoning": "High severity claim requires thorough investigation and documentation."
        })
        recommendations.append({
            "action": "Assign Senior Adjuster",
            "priority": "High",
            "category": "Administrative",
            "icon": "👨‍💼",
            "reasoning": "Complex case requiring experienced adjuster expertise."
        })
        recommendations.append({
            "action": "Schedule On-site Inspection",
            "priority": "Critical",
            "category": "Verification",
            "icon": "🚨",
            "reasoning": "Physical inspection mandatory for high-value claims."
        })
    
    # Rule 5: High Value Claims (>$50,000)
    if estimated_loss > 50000:
        recommendations.append({
            "action": "Supervisor Approval Required",
            "priority": "Critical",
            "category": "Administrative",
            "icon": "👔",
            "reasoning": f"Claim value (${estimated_loss:,.0f}) exceeds standard approval threshold."
        })
        recommendations.append({
            "action": "Request Independent Assessment",
            "priority": "High",
            "category": "Verification",
            "icon": "🔎",
            "reasoning": "High-value claim requires third-party validation."
        })
    
    # Rule 6: Loss Type Specific Recommendations
    if "theft" in loss_type:
        recommendations.append({
            "action": "Verify Police Report",
            "priority": "Critical",
            "category": "Verification",
            "icon": "🚔",
            "reasoning": "Theft claims require official police documentation."
        })
    
    if "fire" in loss_type:
        recommendations.append({
            "action": "Request Fire Department Report",
            "priority": "High",
            "category": "Documentation",
            "icon": "🚒",
            "reasoning": "Fire incident requires official fire department documentation."
        })
    
    if "flood" in loss_type or "water" in loss_type:
        recommendations.append({
            "action": "Verify Weather Records",
            "priority": "Medium",
            "category": "Verification",
            "icon": "🌧️",
            "reasoning": "Cross-reference with official weather data for validation."
        })
    
    if "accident" in loss_type or "collision" in loss_type:
        recommendations.append({
            "action": "Request Accident Report",
            "priority": "High",
            "category": "Documentation",
            "icon": "📋",
            "reasoning": "Vehicle accidents require official accident documentation."
        })
    
    # Rule 7: Missing Information
    if missing_info:
        recommendations.append({
            "action": f"Collect Missing Information",
            "priority": "High",
            "category": "Documentation",
            "icon": "⚠️",
            "reasoning": f"Critical fields missing: {', '.join(missing_info)}. Required for processing."
        })
    
    # Rule 8: Urgent Cases (recent incidents)
    if "today" in incident_date.lower() or "yesterday" in incident_date.lower():
        recommendations.append({
            "action": "Priority Processing",
            "priority": "High",
            "category": "Processing",
            "icon": "⚡",
            "reasoning": "Recent incident requires prompt attention and quick response."
        })
    
    # If no specific recommendations, provide default
    if not recommendations:
        recommendations.append({
            "action": "Standard Claim Processing",
            "priority": "Medium",
            "category": "Processing",
            "icon": "📋",
            "reasoning": "Process through standard workflow with routine verification."
        })
    
    return recommendations


def get_priority_color(priority: str) -> str:
    """
    Get color code for priority level
    
    Args:
        priority: Priority level (Critical, High, Medium, Low)
        
    Returns:
        Hex color code
    """
    priority_colors = {
        "critical": "#D32F2F",  # Dark Red
        "high": "#F57C00",      # Orange
        "medium": "#FBC02D",    # Yellow
        "low": "#388E3C"        # Green
    }
    return priority_colors.get(priority.lower(), "#757575")


def format_recommendations_compact(recommendations: List[Dict]) -> str:
    """
    Format recommendations as a compact, priority-grouped HTML list
    
    Args:
        recommendations: List of recommendation dictionaries
        
    Returns:
        HTML string with formatted recommendations
    """
    if not recommendations:
        return "<p style='color: #666;'>No recommendations available.</p>"
    
    # Group by priority
    priority_groups = {
        "Critical": [],
        "High": [],
        "Medium": [],
        "Low": []
    }
    
    for rec in recommendations:
        priority = rec.get("priority", "Medium")
        if priority in priority_groups:
            priority_groups[priority].append(rec)
    
    # Build HTML
    html = ""
    
    for priority in ["Critical", "High", "Medium", "Low"]:
        recs = priority_groups[priority]
        if not recs:
            continue
        
        color = get_priority_color(priority)
        
        # Priority header
        icon_map = {
            "Critical": "🚨",
            "High": "⚠️",
            "Medium": "📋",
            "Low": "ℹ️"
        }
        
        html += f'''
        <div style="margin: 1rem 0;">
            <div style="
                background-color: {color}15;
                border-left: 4px solid {color};
                padding: 0.5rem 1rem;
                border-radius: 4px 4px 0 0;
                font-weight: 600;
                color: {color};
            ">
                {icon_map.get(priority, "📋")} {priority} Priority ({len(recs)})
            </div>
            <ul style="
                margin: 0;
                padding: 1rem 1rem 1rem 2.5rem;
                background-color: #f9f9f9;
                border-radius: 0 0 4px 4px;
                list-style: none;
            ">
        '''
        
        for rec in recs:
            icon = rec.get("icon", "•")
            action = rec.get("action", "Unknown action")
            html += f'<li style="padding: 0.3rem 0; color: #333;"><span style="margin-right: 0.5rem;">{icon}</span>{action}</li>'
        
        html += '</ul></div>'
    
    return html
