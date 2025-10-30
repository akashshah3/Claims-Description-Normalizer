"""
Prompt templates and configuration for Gemini API
"""

# System prompt that defines the AI's role and capabilities
SYSTEM_PROMPT = """You are an expert insurance claims analyst AI assistant. Your role is to extract structured information from unstructured insurance claim descriptions.

You must analyze the claim text carefully and extract the following information:
- loss_type: The type of loss (e.g., Accident, Fire, Flood, Theft, Water Damage, Storm, Vandalism, etc.)
- severity: The severity level (Low, Medium, High, Critical)
- affected_assets: What was damaged or affected (be specific)
- estimated_loss: The estimated monetary loss mentioned (include currency if mentioned, or "Not specified")
- incident_date: When the incident occurred (extract date/time if mentioned, or "Not specified")
- location: Where the incident occurred (be specific, or "Not specified")
- confidence: Your confidence level in this extraction (Low, Medium, High)
- extraction_explanation: A brief explanation of why you classified it this way, highlighting key words/phrases that influenced your decision

Return ONLY a valid JSON object with these exact field names. Do not include any other text, markdown formatting, or code blocks."""

# Few-shot examples to guide the model
FEW_SHOT_EXAMPLES = """

EXAMPLE 1:
Input: "Customer reported minor accident on rear bumper, scratches only, no injuries, estimated cost ₹7,000. Incident happened yesterday at parking lot near office."

Output:
{
  "loss_type": "Accident",
  "severity": "Low",
  "affected_assets": "Rear bumper (scratches)",
  "estimated_loss": "₹7,000",
  "incident_date": "Yesterday",
  "location": "Parking lot near office",
  "confidence": "High",
  "extraction_explanation": "Classified as 'Accident' with 'Low' severity due to keywords 'minor accident' and 'scratches only'. No injuries reported. Clear cost estimate provided. Location and timeframe specified."
}

EXAMPLE 2:
Input: "Vehicle submerged during flood, engine not starting, electrical damage suspected. Major repairs needed."

Output:
{
  "loss_type": "Flood",
  "severity": "Critical",
  "affected_assets": "Vehicle engine, electrical system",
  "estimated_loss": "Not specified",
  "incident_date": "Not specified",
  "location": "Not specified",
  "confidence": "High",
  "extraction_explanation": "Classified as 'Flood' due to keyword 'submerged during flood'. Severity marked 'Critical' because of non-starting engine and electrical damage, indicating extensive damage requiring major repairs."
}

EXAMPLE 3:
Input: "Fire reported in kitchen at 2:00 AM on Oct 15. Cabinets, microwave, and wall damaged. Customer estimates around $5000 damage. Fire department attended."

Output:
{
  "loss_type": "Fire",
  "severity": "High",
  "affected_assets": "Kitchen cabinets, microwave, wall",
  "estimated_loss": "$5000",
  "incident_date": "Oct 15, 2:00 AM",
  "location": "Kitchen",
  "confidence": "High",
  "extraction_explanation": "Classified as 'Fire' with 'High' severity due to multiple damaged items (cabinets, microwave, wall) and fire department involvement. Specific date, time, location, and cost estimate provided."
}

EXAMPLE 4:
Input: "Customer called about water leakage from ceiling damaging furniture below. Not sure when it started, probably last week."

Output:
{
  "loss_type": "Water Damage",
  "severity": "Medium",
  "affected_assets": "Furniture, ceiling",
  "estimated_loss": "Not specified",
  "incident_date": "Approximately last week",
  "location": "Not specified",
  "confidence": "Medium",
  "extraction_explanation": "Classified as 'Water Damage' due to 'water leakage from ceiling'. Severity marked 'Medium' as multiple items affected but no critical damage mentioned. Confidence is 'Medium' due to uncertainty about start date and lack of cost estimate."
}
"""

def build_prompt(claim_description: str) -> str:
    """
    Constructs the complete prompt for Gemini API
    
    Args:
        claim_description: The raw claim text to analyze
        
    Returns:
        Complete prompt string combining system prompt, examples, and user input
    """
    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLES}

Now analyze this new claim:

Input: "{claim_description}"

Output:"""
    
    return prompt


# Configuration for Gemini API
GEMINI_CONFIG = {
    "temperature": 0.3,  # Lower temperature for more consistent, factual outputs
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 1024,
}
