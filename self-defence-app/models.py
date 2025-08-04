from app import db
from datetime import datetime
from sqlalchemy import Text, DateTime, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class User(db.Model):
    """User model for session management"""
    id = db.Column(Integer, primary_key=True)
    session_id = db.Column(String(255), unique=True, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationship to chat messages
    messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")

class ChatMessage(db.Model):
    """Chat message model"""
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('user.id'), nullable=False)
    message = db.Column(Text, nullable=False)
    response = db.Column(Text)
    message_type = db.Column(String(50), default='user')  # 'user' or 'bot'
    created_at = db.Column(DateTime, default=datetime.utcnow)
    legal_category = db.Column(String(100))  # e.g., 'small_claims', 'fast_track', 'multi_track'
    citations = db.Column(Text)  # JSON string of citations
    
    # Relationship
    user = relationship("User", back_populates="messages")

class LegalCase(db.Model):
    """Legal case precedent model"""
    id = db.Column(Integer, primary_key=True)
    case_name = db.Column(String(500), nullable=False)
    citation = db.Column(String(200), nullable=False)
    court = db.Column(String(200))
    year = db.Column(Integer)
    track_type = db.Column(String(50))  # 'small_claims', 'fast_track', 'multi_track'
    claim_value = db.Column(Integer)  # Value in pence
    case_summary = db.Column(Text)
    legal_principles = db.Column(Text)
    url = db.Column(String(500))
    created_at = db.Column(DateTime, default=datetime.utcnow)

class LegalKnowledge(db.Model):
    """Legal knowledge base model"""
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(500), nullable=False)
    content = db.Column(Text, nullable=False)
    category = db.Column(String(100))  # e.g., 'procedure', 'damages', 'costs'
    subcategory = db.Column(String(100))  # e.g., 'small_claims_procedure'
    track_relevance = db.Column(String(200))  # JSON list of relevant tracks
    keywords = db.Column(Text)  # Search keywords
    source_url = db.Column(String(500))
    last_updated = db.Column(DateTime, default=datetime.utcnow)

class SolicitorReferral(db.Model):
    """Solicitor referral information model"""
    id = db.Column(Integer, primary_key=True)
    firm_name = db.Column(String(300), nullable=False)
    contact_name = db.Column(String(200))
    specialties = db.Column(Text)  # JSON list of specialties
    track_experience = db.Column(String(200))  # JSON list of track types
    location = db.Column(String(200))
    contact_email = db.Column(String(200))
    contact_phone = db.Column(String(50))
    website = db.Column(String(300))
    min_claim_value = db.Column(Integer)  # Minimum claim value in pence
    max_claim_value = db.Column(Integer)  # Maximum claim value in pence
    funding_options = db.Column(Text)  # JSON list of funding options
    active = db.Column(Boolean, default=True)

class DocumentAnalysis(db.Model):
    """Document analysis for skeleton arguments and defence points"""
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('user.id'), nullable=False)
    filename = db.Column(String(300), nullable=False)
    document_type = db.Column(String(100), default='skeleton_argument')  # 'skeleton_argument', 'defence_statement'
    document_text = db.Column(Text, nullable=False)  # Extracted text content
    analysis_summary = db.Column(Text)  # AI-generated summary
    legal_arguments = db.Column(Text)  # JSON list of identified arguments
    defence_points = db.Column(Text)  # JSON list of AI-generated defence points
    claim_value_estimate = db.Column(Integer)  # Estimated claim value in pence
    track_type = db.Column(String(50))  # Assessed track type
    legal_categories = db.Column(Text)  # JSON list of legal categories
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", backref="document_analyses")
