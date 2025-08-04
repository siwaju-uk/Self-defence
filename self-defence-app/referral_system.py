import json
from typing import Dict, List, Optional
from app import db
from models import SolicitorReferral
import logging

class SolicitorReferralSystem:
    """System for recommending appropriate solicitor referrals"""
    
    def __init__(self):
        """Initialize referral system"""
        pass
    
    def get_referral_recommendations(self, analysis: Dict) -> Dict:
        """Get solicitor referral recommendations based on case analysis"""
        
        category = analysis.get('category', 'general')
        track_type = analysis.get('track_type', 'small_claims')
        urgency = analysis.get('urgency', 'low')
        money_values = analysis.get('money_values', [])
        
        # Determine claim value for filtering
        max_value = max(money_values) if money_values else 0
        
        # Get suitable solicitors
        suitable_solicitors = self._find_suitable_solicitors(
            category, track_type, max_value, urgency
        )
        
        # Get funding options
        funding_options = self._get_funding_options(max_value, category)
        
        # Generate referral advice
        referral_advice = self._generate_referral_advice(
            category, track_type, urgency, max_value
        )
        
        return {
            'recommended_solicitors': suitable_solicitors,
            'funding_options': funding_options,
            'referral_advice': referral_advice,
            'urgency_level': urgency
        }
    
    def _find_suitable_solicitors(self, category: str, track_type: str, 
                                 claim_value: float, urgency: str) -> List[Dict]:
        """Find solicitors suitable for the case parameters"""
        
        try:
            # Build filters
            filters = [SolicitorReferral.active == True]
            
            # Value range filtering
            if claim_value > 0:
                filters.append(SolicitorReferral.min_claim_value <= claim_value * 100)  # Convert to pence
                filters.append(SolicitorReferral.max_claim_value >= claim_value * 100)
            
            # Get all suitable solicitors
            query = SolicitorReferral.query.filter(*filters)
            all_solicitors = query.all()
            
            # Score solicitors based on specialties and track experience
            scored_solicitors = []
            for solicitor in all_solicitors:
                score = self._score_solicitor(solicitor, category, track_type, urgency)
                if score > 0:
                    solicitor_data = {
                        'firm_name': solicitor.firm_name,
                        'contact_name': solicitor.contact_name,
                        'specialties': json.loads(solicitor.specialties) if solicitor.specialties else [],
                        'track_experience': json.loads(solicitor.track_experience) if solicitor.track_experience else [],
                        'location': solicitor.location,
                        'contact_email': solicitor.contact_email,
                        'contact_phone': solicitor.contact_phone,
                        'website': solicitor.website,
                        'funding_options': json.loads(solicitor.funding_options) if solicitor.funding_options else [],
                        'score': score
                    }
                    scored_solicitors.append(solicitor_data)
            
            # Sort by score and return top 3
            scored_solicitors.sort(key=lambda x: x['score'], reverse=True)
            return scored_solicitors[:3]
            
        except Exception as e:
            logging.error(f"Error finding suitable solicitors: {e}")
            return []
    
    def _score_solicitor(self, solicitor: SolicitorReferral, category: str, 
                        track_type: str, urgency: str) -> int:
        """Score a solicitor based on suitability for the case"""
        score = 0
        
        try:
            # Parse specialties and track experience
            specialties = json.loads(solicitor.specialties) if solicitor.specialties else []
            track_experience = json.loads(solicitor.track_experience) if solicitor.track_experience else []
            
            # Score for specialty match
            if category in specialties:
                score += 10
            elif 'general_litigation' in specialties:
                score += 5
            
            # Score for track experience
            if track_type in track_experience:
                score += 8
            elif 'all_tracks' in track_experience:
                score += 6
            
            # Score for urgency handling
            if urgency == 'high':
                if 'urgent_applications' in specialties:
                    score += 5
                if 'injunctions' in specialties:
                    score += 5
            
            return score
            
        except Exception as e:
            logging.error(f"Error scoring solicitor: {e}")
            return 0
    
    def _get_funding_options(self, claim_value: float, category: str) -> List[Dict]:
        """Get available funding options for the case"""
        
        funding_options = []
        
        # Legal Aid (very limited for civil cases)
        if category in ['housing', 'domestic_violence'] and claim_value < 5000:
            funding_options.append({
                'type': 'Legal Aid',
                'description': 'Limited legal aid may be available for certain housing and domestic violence cases',
                'eligibility': 'Means and merits tested',
                'cost': 'Free if eligible'
            })
        
        # Conditional Fee Arrangements (CFAs)
        if claim_value >= 1000:
            funding_options.append({
                'type': 'Conditional Fee Arrangement (CFA)',
                'description': 'No win, no fee arrangement with success fee',
                'eligibility': 'Cases with good prospects of success',
                'cost': 'Success fee (typically 25-40% of damages) if you win'
            })
        
        # After the Event Insurance
        if claim_value >= 5000:
            funding_options.append({
                'type': 'After the Event (ATE) Insurance',
                'description': 'Insurance to cover opponent\'s costs if you lose',
                'eligibility': 'Available for most civil claims',
                'cost': 'Premium varies based on case value and risk'
            })
        
        # Third Party Funding
        if claim_value >= 50000:
            funding_options.append({
                'type': 'Third Party Litigation Funding',
                'description': 'Commercial funding for high-value claims',
                'eligibility': 'Strong cases with substantial damages',
                'cost': 'Percentage of damages (typically 20-40%)'
            })
        
        # Damages Based Agreements
        if claim_value >= 10000:
            funding_options.append({
                'type': 'Damages Based Agreement (DBA)',
                'description': 'Lawyer takes percentage of damages if successful',
                'eligibility': 'Available for most civil claims',
                'cost': 'Percentage of damages (max 25% for PI, 50% for other claims)'
            })
        
        return funding_options
    
    def _generate_referral_advice(self, category: str, track_type: str, 
                                 urgency: str, claim_value: float) -> str:
        """Generate personalized referral advice"""
        
        advice_parts = []
        
        # Urgency-based advice
        if urgency == 'high':
            advice_parts.append("⚠️ **Urgent Legal Advice Required**: Based on your query, you should seek immediate legal advice from a qualified solicitor.")
        elif urgency == 'medium':
            advice_parts.append("⏱️ **Timely Legal Advice Recommended**: Consider seeking legal advice soon to protect your legal position.")
        else:
            advice_parts.append("💡 **Consider Professional Advice**: While not urgent, professional legal advice could be beneficial for your situation.")
        
        # Track-specific advice
        if track_type == 'multi_track':
            advice_parts.append("Given the complexity and value of your case (multi-track), professional representation is strongly recommended.")
        elif track_type == 'fast_track':
            advice_parts.append("For fast track claims, legal representation can help navigate the procedures and maximize your chances of success.")
        else:
            advice_parts.append("While small claims are designed for litigants in person, legal advice can still be valuable for strategy and preparation.")
        
        # Value-based advice
        if claim_value >= 25000:
            advice_parts.append("The substantial value of your claim justifies the cost of professional legal representation.")
        elif claim_value >= 10000:
            advice_parts.append("The value of your claim supports considering professional legal assistance, particularly with funding arrangements.")
        
        # Category-specific advice
        if category == 'professional_negligence':
            advice_parts.append("Professional negligence claims require specialist expertise and detailed evidence preparation.")
        elif category == 'employment':
            advice_parts.append("Employment disputes have specific procedures and time limits that require careful attention.")
        elif category == 'commercial_dispute':
            advice_parts.append("Commercial disputes often involve complex legal and factual issues requiring specialist advice.")
        
        return ' '.join(advice_parts)
    
    def _initialize_sample_solicitors(self):
        """Initialize sample solicitor data if database is empty"""
        try:
            # Check if data already exists
            if SolicitorReferral.query.first() is not None:
                return
            
            sample_solicitors = [
                {
                    'firm_name': 'City Commercial Law LLP',
                    'contact_name': 'Sarah Johnson',
                    'specialties': '["commercial_dispute", "contract_dispute", "debt_recovery", "multi_track"]',
                    'track_experience': '["fast_track", "multi_track"]',
                    'location': 'London',
                    'contact_email': 'sarah.johnson@citycommercial.co.uk',
                    'contact_phone': '020 7123 4567',
                    'website': 'https://www.citycommercial.co.uk',
                    'min_claim_value': 1000000,  # £10,000 in pence
                    'max_claim_value': 10000000,  # £100,000 in pence
                    'funding_options': '["CFA", "ATE", "DBA"]',
                    'active': True
                },
                {
                    'firm_name': 'Regional Litigation Partners',
                    'contact_name': 'Michael Brown',
                    'specialties': '["personal_injury", "employment", "consumer_dispute", "general_litigation"]',
                    'track_experience': '["small_claims", "fast_track", "multi_track"]',
                    'location': 'Manchester',
                    'contact_email': 'michael.brown@regionallitigation.co.uk',
                    'contact_phone': '0161 234 5678',
                    'website': 'https://www.regionallitigation.co.uk',
                    'min_claim_value': 50000,  # £500 in pence
                    'max_claim_value': 5000000,  # £50,000 in pence
                    'funding_options': '["CFA", "ATE", "legal_aid"]',
                    'active': True
                },
                {
                    'firm_name': 'Professional Negligence Specialists',
                    'contact_name': 'Dr. Emma Wilson',
                    'specialties': '["professional_negligence", "medical_negligence", "legal_negligence"]',
                    'track_experience': '["fast_track", "multi_track"]',
                    'location': 'Birmingham',
                    'contact_email': 'emma.wilson@profnegligence.co.uk',
                    'contact_phone': '0121 345 6789',
                    'website': 'https://www.profnegligence.co.uk',
                    'min_claim_value': 500000,  # £5,000 in pence
                    'max_claim_value': 10000000,  # £100,000 in pence
                    'funding_options': '["CFA", "ATE", "third_party_funding"]',
                    'active': True
                }
            ]
            
            for solicitor_data in sample_solicitors:
                solicitor = SolicitorReferral(**solicitor_data)
                db.session.add(solicitor)
            
            db.session.commit()
            logging.info("Sample solicitor data initialized")
            
        except Exception as e:
            logging.error(f"Error initializing solicitor data: {e}")
            db.session.rollback()
