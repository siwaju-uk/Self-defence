"""
Document processing module for analyzing skeleton arguments and generating defence points
"""

import os
import json
import logging
from openai import OpenAI
import PyPDF2
import docx
from io import BytesIO
import re

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

class DocumentProcessor:
    """Process and analyze legal documents for defence strategy"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text_from_file(self, file_content, filename):
        """Extract text from uploaded file based on file type"""
        try:
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                return self._extract_from_pdf(file_content)
            elif file_extension in ['doc', 'docx']:
                return self._extract_from_docx(file_content)
            elif file_extension == 'txt':
                return file_content.decode('utf-8')
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            self.logger.error(f"Error extracting text from {filename}: {str(e)}")
            raise
    
    def _extract_from_pdf(self, file_content):
        """Extract text from PDF file"""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error extracting PDF text: {str(e)}")
            raise ValueError("Could not extract text from PDF file")
    
    def _extract_from_docx(self, file_content):
        """Extract text from DOCX file"""
        try:
            doc_file = BytesIO(file_content)
            doc = docx.Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error extracting DOCX text: {str(e)}")
            raise ValueError("Could not extract text from Word document")
    
    def analyze_skeleton_argument(self, document_text):
        """Analyze skeleton argument and generate comprehensive defence strategy"""
        try:
            analysis_prompt = f"""
You are a specialist UK civil litigation barrister with expertise in defending claims up to £100,000. 
Analyze the following claimant's skeleton argument and provide a comprehensive defence strategy.

CLAIMANT'S SKELETON ARGUMENT:
{document_text}

Please provide a detailed analysis in JSON format with the following structure:

{{
    "document_summary": "Brief summary of the claimant's case and main arguments",
    "claim_value_estimate": "Estimated monetary value of the claim in pounds (number only, or 0 if unclear)",
    "track_assessment": "small_claims|fast_track|multi_track",
    "legal_categories": ["contract", "tort", "debt", "employment", "property", "consumer", "professional_negligence"],
    "claimant_arguments": [
        {{
            "argument": "Description of claimant's argument",
            "legal_basis": "Legal principle or statute relied upon",
            "strength": "weak|moderate|strong"
        }}
    ],
    "defence_points": [
        {{
            "defence_strategy": "Specific defence point to counter claimant's argument",
            "legal_basis": "Supporting case law, statute, or legal principle",
            "evidence_required": "What evidence would be needed to support this defence",
            "strength": "weak|moderate|strong",
            "track": "Relevant to which track type"
        }}
    ],
    "procedural_considerations": [
        "Key procedural points and deadlines to consider"
    ],
    "evidence_strategy": [
        "Recommended evidence gathering approaches"
    ],
    "settlement_considerations": "Assessment of settlement prospects and strategy",
    "costs_considerations": "Likely costs implications and Part 36 offer prospects",
    "urgency_level": "low|medium|high"
}}

Focus on practical, actionable defence strategies that comply with UK civil procedure rules and recent case law.
Consider all potential defences including limitation, causation, quantum, procedural defects, and substantive legal defences.
"""

            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a specialist UK civil litigation barrister with extensive experience in defending civil claims up to £100,000. You provide detailed, practical legal analysis focusing on actionable defence strategies."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=4000
            )
            
            analysis_result = json.loads(response.choices[0].message.content or "{}")
            
            # Validate and clean the response
            return self._validate_analysis_result(analysis_result)
            
        except Exception as e:
            self.logger.error(f"Error analyzing skeleton argument: {str(e)}")
            return self._generate_fallback_analysis(document_text)
    
    def _validate_analysis_result(self, analysis):
        """Validate and clean the analysis result"""
        # Ensure required fields exist
        required_fields = [
            'document_summary', 'claim_value_estimate', 'track_assessment',
            'legal_categories', 'claimant_arguments', 'defence_points',
            'procedural_considerations', 'evidence_strategy',
            'settlement_considerations', 'costs_considerations', 'urgency_level'
        ]
        
        for field in required_fields:
            if field not in analysis:
                analysis[field] = self._get_default_value(field)
        
        # Validate claim value
        try:
            claim_value = analysis.get('claim_value_estimate', 0)
            if isinstance(claim_value, str):
                # Extract numeric value from string
                numeric_value = re.findall(r'\d+', str(claim_value))
                analysis['claim_value_estimate'] = int(numeric_value[0]) if numeric_value else 0
            else:
                analysis['claim_value_estimate'] = int(claim_value) if claim_value else 0
        except:
            analysis['claim_value_estimate'] = 0
        
        # Validate track assessment
        valid_tracks = ['small_claims', 'fast_track', 'multi_track']
        if analysis.get('track_assessment') not in valid_tracks:
            claim_value = analysis.get('claim_value_estimate', 0)
            if claim_value <= 10000:
                analysis['track_assessment'] = 'small_claims'
            elif claim_value <= 25000:
                analysis['track_assessment'] = 'fast_track'
            else:
                analysis['track_assessment'] = 'multi_track'
        
        return analysis
    
    def _get_default_value(self, field):
        """Get default values for missing fields"""
        defaults = {
            'document_summary': 'Document analysis could not be completed fully',
            'claim_value_estimate': 0,
            'track_assessment': 'small_claims',
            'legal_categories': ['contract'],
            'claimant_arguments': [],
            'defence_points': [],
            'procedural_considerations': ['Review all relevant deadlines and procedural requirements'],
            'evidence_strategy': ['Gather all relevant documents and witness statements'],
            'settlement_considerations': 'Consider settlement prospects based on strength of case',
            'costs_considerations': 'Assess costs implications and Part 36 offer strategy',
            'urgency_level': 'medium'
        }
        return defaults.get(field, '')
    
    def _generate_fallback_analysis(self, document_text):
        """Generate basic fallback analysis when AI analysis fails"""
        return {
            'document_summary': 'Claimant\'s skeleton argument uploaded for analysis',
            'claim_value_estimate': 0,
            'track_assessment': 'small_claims',
            'legal_categories': ['contract'],
            'claimant_arguments': [
                {
                    'argument': 'Analysis could not be completed automatically',
                    'legal_basis': 'Manual review required',
                    'strength': 'moderate'
                }
            ],
            'defence_points': [
                {
                    'defence_strategy': 'Comprehensive document review required - please consult with a solicitor for detailed analysis',
                    'legal_basis': 'General civil procedure rules',
                    'evidence_required': 'All relevant case documents and evidence',
                    'strength': 'moderate',
                    'track': 'all_tracks'
                }
            ],
            'procedural_considerations': [
                'Review all deadlines and filing requirements',
                'Consider whether additional time is needed for defence preparation'
            ],
            'evidence_strategy': [
                'Compile all relevant documents',
                'Identify potential witnesses',
                'Consider expert evidence requirements'
            ],
            'settlement_considerations': 'Manual review required to assess settlement prospects',
            'costs_considerations': 'Consider costs implications and seek legal advice',
            'urgency_level': 'high'
        }
    
    def format_defence_response(self, analysis):
        """Format the analysis into a user-friendly response"""
        try:
            claim_value = analysis.get('claim_value_estimate', 0)
            track_type = analysis.get('track_assessment', 'small_claims')
            
            # Track information
            track_info = {
                'small_claims': 'Small Claims Track (up to £10,000)',
                'fast_track': 'Fast Track (£10,000-£25,000)', 
                'multi_track': 'Multi-Track (£25,000+)'
            }
            
            response = f"""
# 🛡️ Defence Strategy Analysis

## Document Summary
{analysis.get('document_summary', '')}

## Case Assessment
- **Estimated Claim Value:** £{claim_value:,}
- **Appropriate Track:** {track_info.get(track_type, track_type)}
- **Legal Categories:** {', '.join(analysis.get('legal_categories', []))}
- **Urgency Level:** {analysis.get('urgency_level', 'medium').title()}

## Claimant's Key Arguments
"""
            
            for i, arg in enumerate(analysis.get('claimant_arguments', []), 1):
                response += f"""
### {i}. {arg.get('argument', '')}
- **Legal Basis:** {arg.get('legal_basis', '')}
- **Strength Assessment:** {arg.get('strength', 'moderate').title()}
"""
            
            response += "\n## 🎯 Recommended Defence Points\n"
            
            for i, defence in enumerate(analysis.get('defence_points', []), 1):
                response += f"""
### {i}. {defence.get('defence_strategy', '')}
- **Legal Basis:** {defence.get('legal_basis', '')}
- **Evidence Required:** {defence.get('evidence_required', '')}
- **Strength:** {defence.get('strength', 'moderate').title()}
- **Relevant Track:** {defence.get('track', 'all').title()}
"""
            
            response += "\n## ⚖️ Procedural Considerations\n"
            for consideration in analysis.get('procedural_considerations', []):
                response += f"- {consideration}\n"
            
            response += "\n## 📋 Evidence Strategy\n"
            for strategy in analysis.get('evidence_strategy', []):
                response += f"- {strategy}\n"
            
            response += f"""
## 💰 Settlement & Costs
**Settlement Considerations:** {analysis.get('settlement_considerations', '')}

**Costs Considerations:** {analysis.get('costs_considerations', '')}

---
**⚠️ Legal Disclaimer:** This analysis is for informational purposes only and does not constitute legal advice. Always consult with a qualified solicitor for case-specific guidance.
"""
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Error formatting defence response: {str(e)}")
            return "Error formatting defence analysis. Please try uploading the document again."