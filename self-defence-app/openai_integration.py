import os
import json
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)

class ChatGPTLegalAssistant:
    """
    ChatGPT integration for Solo Case legal assistant
    Provides UK civil litigation guidance with proper disclaimers
    """
    
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        
        # Legal domain system prompt for UK civil litigation
        self.system_prompt = """You are Solo Case, a specialized UK civil litigation assistant for money claims up to £100,000. You provide general legal information only - NOT legal advice.

JURISDICTION: England and Wales only
SPECIALIZATION: Civil litigation, money claims, contract disputes, debt recovery, personal injury, employment disputes, property disputes, consumer issues, professional negligence

TRACK ALLOCATION:
- Small Claims Track: Up to £10,000 (simplified procedures, no costs awards typically)
- Fast Track: £10,000-£25,000 (streamlined procedures, fixed costs)
- Multi-Track: £25,000-£100,000 (full case management, detailed procedures)

RESPONSE GUIDELINES:
1. Always include appropriate disclaimers about not providing legal advice
2. Provide accurate, current information about UK civil litigation procedures
3. Reference relevant legislation, court rules, and case law where appropriate
4. Suggest track allocation based on claim value and complexity
5. Recommend when professional legal advice is essential
6. Be clear about limitation periods and procedural deadlines
7. Explain court fees and potential costs consequences

TONE: Professional, accessible, helpful but cautious. Use simple language while maintaining legal accuracy.

ALWAYS DISCLAIM: Emphasize this is general information only and specific legal advice requires consultation with a qualified solicitor."""

    def get_legal_response(self, user_query: str, chat_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate ChatGPT response for legal queries
        
        Args:
            user_query: User's legal question
            chat_history: Previous conversation context (optional)
            
        Returns:
            Dict with response, type, and metadata
        """
        try:
            # Build conversation history
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history[-6:]:  # Last 6 messages for context
                    role = "user" if msg.get("sender") == "user" else "assistant"
                    content = msg.get("content", "")
                    if role and content:
                        messages.append({"role": role, "content": content})
            
            # Add current query
            messages.append({"role": "user", "content": user_query})
            
            # Get ChatGPT response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                max_tokens=1000,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            content = response.choices[0].message.content
            
            # Analyze query for legal categorization
            legal_category = self._analyze_legal_category(user_query)
            track_recommendation = self._recommend_track(user_query)
            urgency = self._assess_urgency(user_query)
            
            return {
                "response": content,
                "type": "info",
                "category": legal_category,
                "track": track_recommendation,
                "urgency": urgency,
                "model_used": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            logger.error(f"ChatGPT API error: {str(e)}")
            
            # Check if it's a quota/billing issue
            if "quota" in str(e).lower() or "billing" in str(e).lower() or "429" in str(e):
                return {
                    "response": self._get_fallback_legal_response(user_query),
                    "type": "warning",
                    "category": "quota_exceeded",
                    "track": None,
                    "urgency": "low"
                }
            
            return {
                "response": f"I apologize, but I'm currently unable to process your legal query due to a technical issue. Please try again in a moment. If the problem persists, please contact support.\n\n**Technical Error:** {str(e)}",
                "type": "error",
                "category": "system_error",
                "track": None,
                "urgency": "low"
            }

    def _get_fallback_legal_response(self, user_query):
        """Provide a helpful fallback response when ChatGPT is unavailable due to quota"""
        return f"""**UK Civil Litigation Guidance**

I notice you're asking about: "{user_query}"

**Important:** Due to OpenAI API quota limits, I'm currently unable to provide AI-powered responses. However, I can still offer these legal resources:

**For Contract Disputes:**
• Limitation period: Generally 6 years from breach for simple contracts
• Small Claims Track: Up to £10,000
• Fast Track: £10,000 - £25,000  
• Multi-Track: £25,000 - £100,000

**For Personal Injury Claims:**
• Limitation period: Generally 3 years from date of knowledge
• Claims portal available for RTA claims under £25,000

**For Debt Recovery:**
• No limitation period if debt acknowledged
• Money Claims Online available for straightforward claims

**Next Steps:**
1. **Restore AI functionality:** Check your OpenAI billing at platform.openai.com/account/billing
2. Consider the urgency of your matter - some legal deadlines are strict
3. For immediate assistance, consult a qualified solicitor

**Key Legal Resources:**
• HM Courts & Tribunals Service: gov.uk/courts-tribunals
• Civil Procedure Rules: justice.gov.uk  
• Money Claims Online: moneyclaim.gov.uk
• Free legal advice: citizensadvice.org.uk

**Legal Disclaimer:** This information is for guidance only and does not constitute legal advice. Always seek professional legal advice for your specific circumstances.

**To restore full AI legal assistance:** Please check your OpenAI API billing and quota at platform.openai.com/account/billing"""

    def _analyze_legal_category(self, query: str) -> str:
        """Analyze query to determine legal category"""
        query_lower = query.lower()
        
        # Contract and commercial disputes
        if any(term in query_lower for term in ['contract', 'breach', 'agreement', 'terms', 'commercial', 'business']):
            return 'contract_dispute'
        
        # Debt recovery
        elif any(term in query_lower for term in ['debt', 'owe', 'payment', 'invoice', 'outstanding', 'recovery']):
            return 'debt_recovery'
        
        # Personal injury
        elif any(term in query_lower for term in ['injury', 'accident', 'negligence', 'compensation', 'damages']):
            return 'personal_injury'
        
        # Employment
        elif any(term in query_lower for term in ['employment', 'wrongful dismissal', 'discrimination', 'workplace', 'tribunal']):
            return 'employment'
        
        # Property disputes
        elif any(term in query_lower for term in ['property', 'landlord', 'tenant', 'lease', 'possession', 'deposit']):
            return 'property_dispute'
        
        # Consumer disputes
        elif any(term in query_lower for term in ['consumer', 'goods', 'services', 'refund', 'faulty', 'warranty']):
            return 'consumer_dispute'
        
        # Professional negligence
        elif any(term in query_lower for term in ['solicitor', 'accountant', 'professional', 'negligence', 'malpractice']):
            return 'professional_negligence'
        
        else:
            return 'general_civil'

    def _recommend_track(self, query: str) -> Optional[str]:
        """Recommend court track based on query content"""
        import re
        
        # Look for monetary amounts
        money_patterns = [
            r'£(\d{1,3}(?:,\d{3})*)',
            r'(\d{1,3}(?:,\d{3})*)\s*pounds?',
            r'(\d+)k',  # e.g., "15k"
        ]
        
        amounts = []
        for pattern in money_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                try:
                    if 'k' in query.lower():
                        amounts.append(int(match) * 1000)
                    else:
                        amounts.append(int(match.replace(',', '')))
                except ValueError:
                    continue
        
        if amounts:
            max_amount = max(amounts)
            if max_amount <= 10000:
                return 'small_claims'
            elif max_amount <= 25000:
                return 'fast_track'
            elif max_amount <= 100000:
                return 'multi_track'
            else:
                return 'high_court'
        
        # Default recommendations based on case type
        query_lower = query.lower()
        if any(term in query_lower for term in ['personal injury', 'clinical negligence']):
            return 'fast_track'  # Most PI cases
        elif any(term in query_lower for term in ['commercial', 'business', 'professional negligence']):
            return 'multi_track'  # Typically higher value
        else:
            return 'small_claims'  # Default for simple disputes

    def _assess_urgency(self, query: str) -> str:
        """Assess urgency level of the legal query"""
        query_lower = query.lower()
        
        # High urgency indicators
        high_urgency_terms = [
            'urgent', 'emergency', 'immediate', 'asap', 'court date',
            'hearing', 'deadline', 'tomorrow', 'today', 'injunction',
            'eviction', 'possession', 'freezing order'
        ]
        
        # Medium urgency indicators
        medium_urgency_terms = [
            'soon', 'quickly', 'within days', 'this week', 'next week',
            'limitation', 'time limit', 'expires', 'deadline approaching'
        ]
        
        if any(term in query_lower for term in high_urgency_terms):
            return 'high'
        elif any(term in query_lower for term in medium_urgency_terms):
            return 'medium'
        else:
            return 'low'

    def get_solicitor_recommendation(self, case_details: Dict) -> Dict:
        """
        Generate solicitor recommendation based on case details
        """
        try:
            recommendation_prompt = f"""Based on this UK civil litigation case, recommend the type of solicitor needed:

Case Category: {case_details.get('category', 'Unknown')}
Estimated Value: {case_details.get('estimated_value', 'Not specified')}
Track: {case_details.get('track', 'Not determined')}
Urgency: {case_details.get('urgency', 'Normal')}

Provide:
1. Specific solicitor specialization needed
2. Experience level required
3. Whether legal aid might be available
4. Estimated costs range
5. Key questions to ask potential solicitors

Format as a helpful recommendation for someone seeking legal representation."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[  # type: ignore
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": recommendation_prompt}
                ],
                max_tokens=800,
                temperature=0.6
            )
            
            return {
                "recommendation": response.choices[0].message.content,
                "type": "solicitor_referral"
            }
            
        except Exception as e:
            logger.error(f"Error generating solicitor recommendation: {str(e)}")
            return {
                "recommendation": "I apologize, but I cannot generate a solicitor recommendation at this time. Please contact the Law Society of England and Wales for solicitor referrals in your area.",
                "type": "error"
            }