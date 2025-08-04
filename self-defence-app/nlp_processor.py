import re
import spacy
from typing import Dict, List, Optional
import logging

class LegalNLPProcessor:
    """Natural Language Processing for legal queries"""
    
    def __init__(self):
        """Initialize NLP processor with legal-specific patterns"""
        try:
            # Load spaCy model (using small model for compatibility)
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("spaCy model not found, using basic processing")
            self.nlp = None
        
        # Legal categories and their indicators
        self.legal_categories = {
            'contract_dispute': [
                'contract', 'breach', 'agreement', 'terms', 'conditions',
                'warranty', 'guarantee', 'supplier', 'purchase', 'sale'
            ],
            'debt_recovery': [
                'debt', 'owed', 'payment', 'invoice', 'outstanding',
                'money', 'loan', 'credit', 'arrears', 'default'
            ],
            'personal_injury': [
                'injury', 'accident', 'compensation', 'damages', 'hurt',
                'medical', 'hospital', 'pain', 'suffering', 'negligence'
            ],
            'employment': [
                'employment', 'dismissal', 'redundancy', 'discrimination',
                'harassment', 'wages', 'salary', 'workplace', 'employer'
            ],
            'property_dispute': [
                'property', 'landlord', 'tenant', 'deposit', 'rent',
                'lease', 'eviction', 'repairs', 'housing', 'possession'
            ],
            'consumer_dispute': [
                'consumer', 'goods', 'services', 'faulty', 'refund',
                'return', 'warranty', 'shop', 'purchase', 'defective'
            ],
            'professional_negligence': [
                'solicitor', 'accountant', 'surveyor', 'negligence',
                'professional', 'malpractice', 'advice', 'service'
            ]
        }
        
        # Track type indicators based on value and complexity
        self.track_indicators = {
            'small_claims': [
                'small claim', 'under £10,000', 'simple', 'consumer',
                'deposit', 'refund', 'minor'
            ],
            'fast_track': [
                'fast track', '£10,000', '£25,000', 'standard',
                'road traffic', 'employment tribunal'
            ],
            'multi_track': [
                'multi track', 'complex', 'commercial', 'substantial',
                'over £25,000', 'case management', 'expert witness'
            ]
        }
        
        # Money value patterns
        self.money_patterns = [
            r'£(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?) pounds?',
            r'(\d+)k',  # e.g., "50k"
            r'(\d+) thousand'
        ]
    
    def analyze_query(self, query: str) -> Dict:
        """Analyze legal query and extract key information"""
        query_lower = query.lower()
        
        analysis = {
            'category': self._identify_category(query_lower),
            'track_type': self._determine_track_type(query_lower),
            'money_values': self._extract_money_values(query),
            'entities': self._extract_entities(query),
            'urgency': self._assess_urgency(query_lower),
            'complexity': self._assess_complexity(query_lower)
        }
        
        # Refine track type based on money values
        if analysis['money_values']:
            max_value = max(analysis['money_values'])
            if max_value <= 10000:
                analysis['track_type'] = 'small_claims'
            elif max_value <= 25000:
                analysis['track_type'] = 'fast_track'
            elif max_value <= 100000:
                analysis['track_type'] = 'multi_track'
            else:
                analysis['track_type'] = 'high_court'
        
        return analysis
    
    def _identify_category(self, query: str) -> str:
        """Identify the legal category of the query"""
        category_scores = {}
        
        for category, keywords in self.legal_categories.items():
            score = sum(1 for keyword in keywords if keyword in query)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores.keys(), key=lambda k: category_scores[k])
        
        return 'general'
    
    def _determine_track_type(self, query: str) -> str:
        """Determine the likely court track based on query content"""
        track_scores = {}
        
        for track, indicators in self.track_indicators.items():
            score = sum(1 for indicator in indicators if indicator in query)
            if score > 0:
                track_scores[track] = score
        
        if track_scores:
            return max(track_scores.keys(), key=lambda k: track_scores[k])
        
        # Default based on complexity indicators
        complexity_indicators = [
            'complex', 'multiple parties', 'expert', 'commercial',
            'substantial', 'significant'
        ]
        
        if any(indicator in query for indicator in complexity_indicators):
            return 'multi_track'
        
        return 'small_claims'  # Default to most accessible track
    
    def _extract_money_values(self, query: str) -> List[float]:
        """Extract monetary values from the query"""
        values = []
        
        for pattern in self.money_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                try:
                    if 'k' in match.group(0).lower():
                        value = float(match.group(1)) * 1000
                    elif 'thousand' in match.group(0).lower():
                        value = float(match.group(1)) * 1000
                    else:
                        # Remove commas and extract number
                        value_str = match.group(1).replace(',', '')
                        value = float(value_str)
                    
                    values.append(value)
                except (ValueError, IndexError):
                    continue
        
        return values
    
    def _extract_entities(self, query: str) -> List[Dict]:
        """Extract named entities using spaCy if available"""
        entities = []
        
        if self.nlp is None:
            return entities
        
        try:
            doc = self.nlp(query)
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'description': spacy.explain(ent.label_)
                })
        except Exception as e:
            logging.error(f"Entity extraction error: {e}")
        
        return entities
    
    def _assess_urgency(self, query: str) -> str:
        """Assess the urgency level of the query"""
        urgent_indicators = [
            'urgent', 'emergency', 'immediate', 'asap', 'court date',
            'deadline', 'tomorrow', 'today', 'served', 'claim form'
        ]
        
        high_urgency = [
            'injunction', 'freezing order', 'search order', 'arrest',
            'bailiff', 'eviction notice'
        ]
        
        if any(indicator in query for indicator in high_urgency):
            return 'high'
        elif any(indicator in query for indicator in urgent_indicators):
            return 'medium'
        else:
            return 'low'
    
    def _assess_complexity(self, query: str) -> str:
        """Assess the complexity level of the query"""
        complex_indicators = [
            'multiple parties', 'cross-claim', 'counterclaim',
            'expert witness', 'disclosure', 'international',
            'regulatory', 'appeal', 'judicial review'
        ]
        
        medium_indicators = [
            'contract', 'negligence', 'employment', 'commercial',
            'professional', 'substantial'
        ]
        
        if any(indicator in query for indicator in complex_indicators):
            return 'high'
        elif any(indicator in query for indicator in medium_indicators):
            return 'medium'
        else:
            return 'low'
