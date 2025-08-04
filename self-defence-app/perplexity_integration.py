import os
import json
import requests
from typing import Dict, List, Optional
import logging

class PerplexityLegalSearch:
    """Integration with Perplexity AI for enhanced legal information retrieval"""
    
    def __init__(self):
        """Initialize Perplexity API client"""
        self.api_key = os.environ.get('PERPLEXITY_API_KEY')
        self.base_url = 'https://api.perplexity.ai/chat/completions'
        self.model = 'llama-3.1-sonar-small-128k-online'
        
        if not self.api_key:
            logging.warning("PERPLEXITY_API_KEY not found. Enhanced legal search will be unavailable.")
    
    def search_legal_information(self, query: str, legal_category: Optional[str] = None, 
                                track_type: Optional[str] = None) -> Dict:
        """Search for legal information using Perplexity AI"""
        
        if not self.api_key:
            return {
                'success': False,
                'error': 'Perplexity API key not available',
                'response': None,
                'citations': []
            }
        
        try:
            # Construct specialized legal query
            legal_query = self._construct_legal_query(query, legal_category, track_type)
            
            # Make API request
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': self._get_legal_system_prompt()
                    },
                    {
                        'role': 'user',
                        'content': legal_query
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.2,
                'top_p': 0.9,
                'search_domain_filter': [
                    'bailii.org',
                    'legislation.gov.uk',
                    'gov.uk',
                    'justice.gov.uk'
                ],
                'return_images': False,
                'return_related_questions': True,
                'search_recency_filter': 'year',
                'stream': False,
                'presence_penalty': 0,
                'frequency_penalty': 0.1
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_response(data)
            else:
                logging.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'API request failed with status {response.status_code}',
                    'response': None,
                    'citations': []
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'response': None,
                'citations': []
            }
        except Exception as e:
            logging.error(f"Unexpected error in Perplexity search: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'response': None,
                'citations': []
            }
    
    def _construct_legal_query(self, query: str, legal_category: Optional[str] = None, 
                              track_type: Optional[str] = None) -> str:
        """Construct a specialized legal query for better results"""
        
        base_query = f"UK civil litigation: {query}"
        
        # Add category context
        if legal_category:
            category_context = {
                'contract_dispute': 'contract law and breach of contract',
                'debt_recovery': 'debt recovery and money claims',
                'personal_injury': 'personal injury compensation',
                'employment': 'employment law disputes',
                'property_dispute': 'property and landlord tenant law',
                'consumer_dispute': 'consumer rights and disputes',
                'professional_negligence': 'professional negligence claims'
            }
            context = category_context.get(legal_category, legal_category)
            base_query += f" relating to {context}"
        
        # Add track context
        if track_type:
            track_context = {
                'small_claims': 'small claims track procedures (up to £10,000)',
                'fast_track': 'fast track procedures (£10,000-£25,000)',
                'multi_track': 'multi-track procedures (£25,000-£100,000)'
            }
            context = track_context.get(track_type, track_type)
            base_query += f" under {context}"
        
        # Add specific requirements for legal information
        base_query += ". Please provide current UK law, relevant case law with proper citations, applicable procedures, and any recent legal changes. Focus on practical guidance for England and Wales jurisdiction."
        
        return base_query
    
    def _get_legal_system_prompt(self) -> str:
        """Get the system prompt for legal queries"""
        return """You are a specialized UK legal information assistant focusing on civil litigation up to £100,000. Provide accurate, current information about:

1. UK civil litigation procedures (Small Claims, Fast Track, Multi-Track)
2. Relevant case law with proper citations
3. Court procedures and requirements
4. Legal principles and their applications
5. Current court fees and costs

IMPORTANT GUIDELINES:
- Only provide information about England and Wales law
- Include proper legal citations in standard format
- Distinguish between different court tracks
- Mention limitation periods where relevant
- Reference current Civil Procedure Rules
- Be precise about monetary thresholds
- Always include disclaimers about seeking professional legal advice

Format citations as: Case Name [Year] Court Reference or Case Name (Year) Citation
Example: Dunlop v New Garage [1915] AC 79"""
    
    def _process_response(self, data: Dict) -> Dict:
        """Process Perplexity API response"""
        try:
            if 'choices' not in data or not data['choices']:
                return {
                    'success': False,
                    'error': 'No response choices available',
                    'response': None,
                    'citations': []
                }
            
            choice = data['choices'][0]
            message_content = choice.get('message', {}).get('content', '')
            
            # Extract citations from the response
            citations = []
            if 'citations' in data:
                for citation_url in data['citations']:
                    citations.append({
                        'type': 'web_source',
                        'url': citation_url,
                        'title': self._extract_title_from_url(citation_url)
                    })
            
            return {
                'success': True,
                'error': None,
                'response': message_content,
                'citations': citations,
                'usage': data.get('usage', {}),
                'model': data.get('model', self.model)
            }
            
        except Exception as e:
            logging.error(f"Error processing Perplexity response: {e}")
            return {
                'success': False,
                'error': f'Response processing error: {str(e)}',
                'response': None,
                'citations': []
            }
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a readable title from URL"""
        if 'bailii.org' in url:
            return 'BAILII - British and Irish Legal Information'
        elif 'legislation.gov.uk' in url:
            return 'UK Legislation'
        elif 'gov.uk' in url:
            return 'Government Legal Information'
        elif 'justice.gov.uk' in url:
            return 'Ministry of Justice'
        else:
            return 'Legal Source'
    
    def get_case_law_summary(self, case_name: str) -> Dict:
        """Get detailed information about a specific case"""
        
        if not self.api_key:
            return {'success': False, 'error': 'API key not available'}
        
        query = f"Provide detailed summary of the UK legal case {case_name} including: citation, court, key legal principles, significance, and current relevance to civil litigation"
        
        return self.search_legal_information(query)
    
    def get_procedure_guidance(self, procedure_type: str, track_type: Optional[str] = None) -> Dict:
        """Get specific procedural guidance"""
        
        if not self.api_key:
            return {'success': False, 'error': 'API key not available'}
        
        query = f"UK civil litigation procedure guidance for {procedure_type}"
        if track_type:
            query += f" in {track_type} cases"
        
        query += ". Include current Civil Procedure Rules, forms required, time limits, and practical steps."
        
        return self.search_legal_information(query, track_type=track_type)
    
    def check_recent_legal_changes(self, area_of_law: str) -> Dict:
        """Check for recent changes in specific areas of law"""
        
        if not self.api_key:
            return {'success': False, 'error': 'API key not available'}
        
        query = f"Recent changes and updates in UK {area_of_law} law in the last 12 months. Include new legislation, important court decisions, and procedural changes affecting civil litigation."
        
        return self.search_legal_information(query)