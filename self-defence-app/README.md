# Self-Defence - UK Legal Chatbot

## Quick Start
1. Extract this zip file
2. Install Python 3.11+
3. Install dependencies: pip install -r requirements.txt
4. Set your OpenAI API key: export OPENAI_API_KEY="your-key-here"
5. Run: python main.py
6. Open http://localhost:5000

## Features
- AI-powered legal chat using ChatGPT-4o
- Document analysis for claimant skeleton arguments
- Defence strategy generation with legal basis
- Multi-track support (Small Claims, Fast Track, Multi-Track)
- Professional legal branding inspired by SprintLaw

## Environment Variables
- OPENAI_API_KEY: Required for ChatGPT integration
- DATABASE_URL: Optional PostgreSQL URL (defaults to SQLite)
- SESSION_SECRET: Optional Flask session secret

## Usage
1. Chat: Ask legal questions via the main chat interface
2. Document Analysis: Upload PDF/Word documents for defence analysis
3. Navigation: Use the top menu to switch between features

## Legal Disclaimer
This application provides general legal information only and does not constitute legal advice.
Always consult a qualified solicitor for specific legal guidance.

## Technology Stack
- Backend: Flask, SQLAlchemy, OpenAI GPT-4o
- Frontend: Bootstrap 5, Vanilla JavaScript
- Database: SQLite (default) or PostgreSQL
- Document Processing: PyPDF2, python-docx
