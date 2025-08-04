import json
from typing import Dict, List, Optional
from app import db
from models import LegalCase, LegalKnowledge
import logging

class LegalKnowledgeRetriever:
    """Retrieve relevant legal knowledge based on queries"""
    
    def __init__(self):
        """Initialize knowledge retriever"""
        pass
    
    def get_relevant_information(self, query: str, legal_category: Optional[str] = None, 
                               track_type: Optional[str] = None) -> Dict:
        """Retrieve relevant legal information for a query"""
        
        results = {
            'cases': self._search_cases(query, legal_category, track_type),
            'procedures': self._search_procedures(query, legal_category, track_type),
            'statutory_provisions': self._search_statutory_provisions(query, legal_category)
        }
        
        return results
    
    def _search_cases(self, query: str, category: Optional[str] = None, 
                     track_type: Optional[str] = None) -> List[Dict]:
        """Search for relevant case law"""
        
        # Build query filters
        filters = []
        if category:
            filters.append(LegalCase.case_summary.contains(category))
        if track_type:
            filters.append(LegalCase.track_type == track_type)
        
        # Search by keywords in query
        query_words = query.lower().split()
        keyword_filters = []
        for word in query_words:
            if len(word) > 3:  # Only search meaningful words
                keyword_filters.append(LegalCase.case_summary.contains(word))
                keyword_filters.append(LegalCase.legal_principles.contains(word))
        
        try:
            if keyword_filters:
                # Combine filters with OR for keywords
                cases = LegalCase.query.filter(
                    *filters,
                    db.or_(*keyword_filters)
                ).limit(5).all()
            else:
                cases = LegalCase.query.filter(*filters).limit(5).all()
            
            return [{
                'case_name': case.case_name,
                'citation': case.citation,
                'court': case.court,
                'year': case.year,
                'summary': case.case_summary[:200] + '...' if len(case.case_summary) > 200 else case.case_summary,
                'legal_principles': case.legal_principles,
                'url': case.url,
                'track_type': case.track_type,
                'claim_value': case.claim_value
            } for case in cases]
            
        except Exception as e:
            logging.error(f"Error searching cases: {e}")
            return []
    
    def _search_procedures(self, query: str, category: Optional[str] = None, 
                          track_type: Optional[str] = None) -> List[Dict]:
        """Search for relevant procedural information"""
        
        filters = []
        if category:
            filters.append(LegalKnowledge.category == 'procedure')
            filters.append(LegalKnowledge.subcategory.contains(category))
        if track_type:
            filters.append(LegalKnowledge.track_relevance.contains(track_type))
        
        # Search by keywords
        query_words = query.lower().split()
        keyword_filters = []
        for word in query_words:
            if len(word) > 3:
                keyword_filters.append(LegalKnowledge.content.contains(word))
                keyword_filters.append(LegalKnowledge.keywords.contains(word))
        
        try:
            if keyword_filters:
                procedures = LegalKnowledge.query.filter(
                    LegalKnowledge.category == 'procedure',
                    *filters,
                    db.or_(*keyword_filters)
                ).limit(3).all()
            else:
                procedures = LegalKnowledge.query.filter(
                    LegalKnowledge.category == 'procedure',
                    *filters
                ).limit(3).all()
            
            return [{
                'title': proc.title,
                'summary': proc.content[:300] + '...' if len(proc.content) > 300 else proc.content,
                'source': proc.source_url,
                'track_relevance': json.loads(proc.track_relevance) if proc.track_relevance else []
            } for proc in procedures]
            
        except Exception as e:
            logging.error(f"Error searching procedures: {e}")
            return []
    
    def _search_statutory_provisions(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search for relevant statutory provisions"""
        
        filters = [LegalKnowledge.category == 'statute']
        if category:
            filters.append(LegalKnowledge.subcategory.contains(category))
        
        query_words = query.lower().split()
        keyword_filters = []
        for word in query_words:
            if len(word) > 3:
                keyword_filters.append(LegalKnowledge.content.contains(word))
                keyword_filters.append(LegalKnowledge.keywords.contains(word))
        
        try:
            if keyword_filters:
                statutes = LegalKnowledge.query.filter(
                    *filters,
                    db.or_(*keyword_filters)
                ).limit(3).all()
            else:
                statutes = LegalKnowledge.query.filter(*filters).limit(3).all()
            
            return [{
                'title': stat.title,
                'summary': stat.content[:250] + '...' if len(stat.content) > 250 else stat.content,
                'source': stat.source_url
            } for stat in statutes]
            
        except Exception as e:
            logging.error(f"Error searching statutes: {e}")
            return []
    
    def _initialize_sample_data(self):
        """Initialize sample legal data if database is empty"""
        try:
            # Check if data already exists
            if LegalCase.query.first() is not None:
                return
            
            # Sample legal cases
            sample_cases = [
                {
                    'case_name': 'Dunlop Pneumatic Tyre Co Ltd v New Garage and Motor Co Ltd',
                    'citation': '[1915] AC 79',
                    'court': 'House of Lords',
                    'year': 1915,
                    'track_type': 'multi_track',
                    'claim_value': 5000000,  # Historical value in pence
                    'case_summary': 'Landmark case establishing the difference between penalty clauses and liquidated damages in contract law.',
                    'legal_principles': 'Penalty clauses are unenforceable if they are disproportionate to the actual loss. Liquidated damages must be a genuine pre-estimate of loss.',
                    'url': 'https://www.bailii.org/uk/cases/UKHL/1915/1.html'
                },
                {
                    'case_name': 'Hadley v Baxendale',
                    'citation': '(1854) 9 Exch 341',
                    'court': 'Court of Exchequer',
                    'year': 1854,
                    'track_type': 'fast_track',
                    'claim_value': 2500000,
                    'case_summary': 'Established the test for remoteness of damage in contract law.',
                    'legal_principles': 'Damages for breach of contract are limited to losses that arise naturally from the breach or were reasonably foreseeable.',
                    'url': 'https://www.bailii.org/ew/cases/EWHC/Exch/1854/J70.html'
                },
                {
                    'case_name': 'Jarvis v Swans Tours Ltd',
                    'citation': '[1973] QB 233',
                    'court': 'Court of Appeal',
                    'year': 1973,
                    'track_type': 'small_claims',
                    'claim_value': 31050,  # £31.05 in 1973
                    'case_summary': 'Established that damages for disappointment and distress can be recovered in consumer contracts.',
                    'legal_principles': 'Non-pecuniary losses including disappointment and distress are recoverable in consumer contracts for holidays and leisure.',
                    'url': 'https://www.bailii.org/ew/cases/EWCA/Civ/1972/12.html'
                }
            ]
            
            for case_data in sample_cases:
                case = LegalCase(**case_data)
                db.session.add(case)
            
            # Sample procedural knowledge
            sample_procedures = [
                {
                    'title': 'Small Claims Track Procedure',
                    'content': 'Small claims are designed for disputes up to £10,000. The procedure is simplified with limited disclosure, no requirement for legal representation, and restricted costs recovery. Hearings are informal and conducted by District Judges.',
                    'category': 'procedure',
                    'subcategory': 'small_claims',
                    'track_relevance': '["small_claims"]',
                    'keywords': 'small claims, simplified procedure, district judge, informal hearing',
                    'source_url': 'https://www.gov.uk/make-court-claim-for-money'
                },
                {
                    'title': 'Fast Track Case Management',
                    'content': 'Fast track claims (£10,000-£25,000) follow standard directions with a trial window of 30 weeks. Fixed trial costs apply and the procedure balances accessibility with proper case management.',
                    'category': 'procedure',
                    'subcategory': 'fast_track',
                    'track_relevance': '["fast_track"]',
                    'keywords': 'fast track, standard directions, fixed costs, 30 weeks',
                    'source_url': 'https://www.justice.gov.uk/courts/procedure-rules/civil'
                },
                {
                    'title': 'Multi-Track Case Management Conference',
                    'content': 'Multi-track claims over £25,000 require active case management including Case Management Conferences (CMC), costs budgeting under Precedent H, and tailored directions. The court controls the litigation timetable.',
                    'category': 'procedure',
                    'subcategory': 'multi_track',
                    'track_relevance': '["multi_track"]',
                    'keywords': 'multi track, case management conference, costs budgeting, precedent h',
                    'source_url': 'https://www.justice.gov.uk/courts/procedure-rules/civil'
                }
            ]
            
            for proc_data in sample_procedures:
                procedure = LegalKnowledge(**proc_data)
                db.session.add(procedure)
            
            db.session.commit()
            logging.info("Sample legal data initialized")
            
        except Exception as e:
            logging.error(f"Error initializing sample data: {e}")
            db.session.rollback()
