
import re
import pandas as pd
from dateutil import parser

def extract_date(text):
    """Extract date from claim text"""
    if pd.isna(text):
        return None
    
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
        r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                parsed_date = parser.parse(matches[0], fuzzy=True)
                return parsed_date.strftime('%Y-%m-%d')
            except:
                continue
    
    try:
        parsed_date = parser.parse(text, fuzzy=True)
        if 2020 <= parsed_date.year <= 2025:
            return parsed_date.strftime('%Y-%m-%d')
    except:
        pass
    
    return None

def extract_location(text):
    """Extract location from claim text"""
    if pd.isna(text):
        return None
    
    us_states = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    }
    
    location_pattern = r'\b([A-Z][a-zA-Z\s]+),\s+([A-Z]{2})\b'
    matches = re.findall(location_pattern, text)
    
    for city, state in matches:
        if state in us_states:
            return f"{city.strip()}, {state}"
    
    return None

def extract_affected_item(text, max_length=50):
    """Extract what was damaged"""
    if pd.isna(text) or len(text) < 20:
        return None
    
    damage_keywords = ['damage', 'broke', 'cracked', 'shattered', 'dent', 'scratch', 
                      'collision', 'hit', 'impact', 'destroyed', 'broken']
    
    sentences = re.split(r'[.!?]', text)
    relevant_sentences = []
    
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in damage_keywords):
            relevant_sentences.append(sentence.strip())
    
    if relevant_sentences:
        return relevant_sentences[0][:max_length]
    
    return sentences[0][:max_length] if sentences else None
