# Self-Defence - UK Legal Chatbot

## Overview

Self-Defence is a specialized Flask-based web application that provides a conversational AI chatbot for UK civil litigation matters. The system focuses exclusively on money civil litigation cases up to £100,000, covering Small Claims Track (up to £10,000), Fast Track (£10,000-£25,000), and Multi-Track (£25,000-£100,000) procedures. The application features an elegant, law-like design inspired by SprintLaw's aesthetic with a green color palette and professional typography. The chatbot provides conversational AI-powered legal information through ChatGPT (OpenAI) integration with proper legal disclaimers and solicitor referrals while maintaining clear disclaimers that it does not provide legal advice.

## Key Features Added (August 2025):
- **Document Analysis Module**: Upload claimant's skeleton arguments for AI-powered defence strategy analysis
- **Defence Point Generation**: Comprehensive counter-argument suggestions with legal basis and evidence requirements
- **Multi-format Support**: PDF, Word (.docx), and text file processing capabilities
- **Track Assessment**: Automatic classification into appropriate court tracks based on claim value and complexity
- **Strategic Planning**: Procedural considerations, evidence strategy, and settlement assessments

## User Preferences

Preferred communication style: Simple, everyday language.
Branding: Application rebranded as "Self-Defence" with elegant law-like logo and SprintLaw-inspired color scheme featuring green accents (#4A7C59, #2C5530) on clean white background.
Design aesthetic: Professional, minimalist, accessible with sophisticated typography using Inter font family.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM for database operations
- **Real-time Communication**: Flask-SocketIO for bidirectional chat functionality between client and server
- **Session Management**: Flask sessions with UUID-based user identification for chat history tracking
- **Database**: SQLite default with configurable PostgreSQL support via environment variables
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **JavaScript**: Vanilla JavaScript with Socket.IO client for real-time chat interface
- **Design System**: Dark theme Bootstrap with custom CSS for legal branding
- **Chat Interface**: Message history display with typing indicators and smooth animations

### Data Models
- **User Model**: Session-based user tracking with relationship to chat messages and document analyses
- **ChatMessage Model**: Stores user queries and bot responses with legal categorization and citations
- **LegalCase Model**: Case law database with citation, court, track type, and claim value fields
- **LegalKnowledge Model**: Structured legal information categorized by procedure types and track relevance
- **SolicitorReferral Model**: Referral system for connecting users with appropriate legal professionals
- **DocumentAnalysis Model**: Stores uploaded documents, extracted text, AI analysis results, defence points, and legal assessments

### AI Integration and Natural Language Processing
- **Primary AI**: ChatGPT (OpenAI GPT-4o) integration for conversational legal assistance with specialized UK civil litigation system prompt
- **Document Processing AI**: Specialized GPT-4o integration for analyzing skeleton arguments and generating defence strategies
- **NLP Processor**: spaCy-based processor with fallback for basic text processing and legal entity extraction
- **Legal Classification**: Pattern matching system for categorizing queries into legal domains (contract disputes, debt recovery, personal injury, employment, property, consumer disputes, professional negligence)
- **Track Assignment**: Automatic classification into Small Claims, Fast Track, or Multi-Track based on claim values and complexity indicators
- **Context Management**: Chat history integration for contextual conversations with legal continuity
- **Document Analysis**: Text extraction from PDF, Word, and text files with comprehensive legal strategy generation

### Knowledge Retrieval System
- **Legal Knowledge Retriever**: Database-driven search across case law, procedures, and statutory provisions
- **Search Strategy**: Keyword-based filtering with category and track type constraints
- **Content Types**: Case precedents, procedural guidance, and statutory provisions with relevance scoring

### Referral and Advisory System
- **Solicitor Matching**: Algorithm-based matching of legal cases to appropriate solicitors based on specialization and claim value
- **Funding Options**: Assessment of legal funding options including legal aid eligibility and after-the-event insurance
- **Urgency Assessment**: Categorization of cases by urgency level for appropriate resource allocation

### Security and Compliance
- **Legal Disclaimers**: Prominent disclaimers throughout the application emphasizing that information provided is not legal advice
- **Session Security**: Secure session management with configurable secret keys
- **Data Privacy**: User session isolation with proper database relationships

## External Dependencies

### Core Framework Dependencies
- **Flask**: Main web framework with SQLAlchemy integration
- **Flask-SocketIO**: Real-time bidirectional communication
- **SQLAlchemy**: ORM for database operations with declarative base

### Natural Language Processing
- **spaCy**: Primary NLP library using en_core_web_sm model
- **NLTK**: Alternative/supplementary text processing (referenced but not actively used)

### Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme variant
- **Font Awesome**: Icon library for UI elements
- **Socket.IO Client**: JavaScript library for real-time communication

### Database
- **SQLite**: Default development database
- **PostgreSQL**: Production database option via DATABASE_URL environment variable
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability

### Deployment and Infrastructure
- **Werkzeug ProxyFix**: Middleware for deployment behind proxies
- **Environment Configuration**: Support for SESSION_SECRET and DATABASE_URL environment variables
- **CORS**: Cross-origin resource sharing configured for SocketIO connections

### Development Tools
- **Logging**: Python logging with debug level configuration
- **Hot Reload**: Development server with debug mode enabled
- **Static Assets**: CSS and JavaScript served through Flask static file handling