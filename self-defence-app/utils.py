import re
from datetime import datetime
from typing import Dict, List, Optional
import logging

def format_currency(amount: float) -> str:
    """Format currency amount in British pounds"""
    if amount >= 1000000:
        return f"£{amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"£{amount/1000:.1f}K"
    else:
        return f"£{amount:.2f}"

def extract_case_reference(text: str) -> Optional[str]:
    """Extract legal case reference from text"""
    # Pattern for UK case citations
    patterns = [
        r'\[(\d{4})\]\s*([A-Z]+)\s*(\d+)',  # [2021] EWCA Civ 123
        r'\((\d{4})\)\s*(\d+)\s*([A-Z]+)\s*(\d+)',  # (2021) 1 WLR 123
        r'(\d{4})\s*([A-Z]+)\s*(\d+)'  # 2021 UKSC 1
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return None

def calculate_court_fees(claim_value: float, track_type: str) -> Dict[str, float]:
    """Calculate court fees based on claim value and track type"""
    fees = {}
    
    # Issue fees (as of 2024)
    if claim_value <= 300:
        fees['issue_fee'] = 35
    elif claim_value <= 500:
        fees['issue_fee'] = 50
    elif claim_value <= 1000:
        fees['issue_fee'] = 70
    elif claim_value <= 1500:
        fees['issue_fee'] = 80
    elif claim_value <= 3000:
        fees['issue_fee'] = 115
    elif claim_value <= 5000:
        fees['issue_fee'] = 205
    elif claim_value <= 10000:
        fees['issue_fee'] = 455
    elif claim_value <= 200000:
        fees['issue_fee'] = claim_value * 0.045
    else:
        fees['issue_fee'] = 10000  # Maximum fee
    
    # Hearing fees
    if track_type == 'small_claims':
        if claim_value <= 300:
            fees['hearing_fee'] = 25
        elif claim_value <= 500:
            fees['hearing_fee'] = 55
        elif claim_value <= 1000:
            fees['hearing_fee'] = 80
        else:
            fees['hearing_fee'] = 120
    elif track_type == 'fast_track':
        fees['hearing_fee'] = 545
    elif track_type == 'multi_track':
        fees['hearing_fee'] = 1090
    
    fees['total'] = sum(fees.values())
    return fees

def validate_legal_query(query: str) -> Dict[str, bool]:
    """Validate if query is appropriate for legal assistance"""
    validation = {
        'is_legal': False,
        'is_appropriate': True,
        'requires_immediate_attention': False
    }
    
    # Legal keywords
    legal_keywords = [
        'contract', 'dispute', 'claim', 'court', 'legal', 'law',
        'liability', 'damages', 'compensation', 'breach', 'negligence',
        'debt', 'payment', 'employment', 'property', 'injury'
    ]
    
    # Inappropriate content indicators
    inappropriate_indicators = [
        'illegal', 'criminal', 'fraud', 'money laundering',
        'tax evasion', 'violence', 'threats'
    ]
    
    # Emergency indicators
    emergency_indicators = [
        'served with', 'court date', 'deadline', 'urgent',
        'injunction', 'freezing order', 'arrest'
    ]
    
    query_lower = query.lower()
    
    # Check if query is legal-related
    if any(keyword in query_lower for keyword in legal_keywords):
        validation['is_legal'] = True
    
    # Check for inappropriate content
    if any(indicator in query_lower for indicator in inappropriate_indicators):
        validation['is_appropriate'] = False
    
    # Check for emergency situations
    if any(indicator in query_lower for indicator in emergency_indicators):
        validation['requires_immediate_attention'] = True
    
    return validation

def generate_disclaimer_text() -> str:
    """Generate standard legal disclaimer text"""
    return """
    **Important Legal Disclaimer:**
    
    This chatbot provides general legal information only and does not constitute legal advice. 
    The information provided:
    
    • Is for guidance purposes only
    • Does not create a solicitor-client relationship
    • Should not be relied upon for legal decisions
    • May not reflect the most current legal developments
    • Is limited to England and Wales law
    
    For specific legal advice about your situation, please consult a qualified solicitor.
    Time limits and court procedures are strict - seek professional advice promptly.
    """

def log_user_interaction(session_id: str, query: str, response_type: str):
    """Log user interactions for analysis and improvement"""
    try:
        logging.info(f"Session {session_id}: Query type '{response_type}' - Length: {len(query)} chars")
    except Exception as e:
        logging.error(f"Error logging interaction: {e}")

def format_legal_citation(case_name: str, citation: str, year: Optional[int] = None) -> str:
    """Format legal citation in standard format"""
    if year and str(year) not in citation:
        return f"{case_name} ({year}) {citation}"
    else:
        return f"{case_name} {citation}"

def calculate_limitation_period(claim_type: str, incident_date: Optional[datetime] = None) -> Dict:
    """Calculate limitation periods for different claim types"""
    limitation_periods = {
        'contract': {'years': 6, 'description': 'Six years from breach of contract'},
        'tort': {'years': 6, 'description': 'Six years from cause of action accrued'},
        'personal_injury': {'years': 3, 'description': 'Three years from injury or knowledge'},
        'defamation': {'years': 1, 'description': 'One year from publication'},
        'professional_negligence': {'years': 6, 'description': 'Six years from breach of duty'},
        'product_liability': {'years': 3, 'description': 'Three years from damage occurred'}
    }
    
    if claim_type.lower() in limitation_periods:
        period_info = limitation_periods[claim_type.lower()]
        
        if incident_date:
            # Calculate actual limitation date
            from dateutil.relativedelta import relativedelta
            limitation_date = incident_date + relativedelta(years=period_info['years'])
            days_remaining = (limitation_date - datetime.now()).days
            
            return {
                'period_years': period_info['years'],
                'description': period_info['description'],
                'limitation_date': limitation_date.strftime('%d %B %Y'),
                'days_remaining': max(0, days_remaining),
                'is_expired': days_remaining <= 0
            }
        else:
            return {
                'period_years': period_info['years'],
                'description': period_info['description']
            }
    
    return {
        'period_years': 6,
        'description': 'Six years (general limitation period)'
    }
