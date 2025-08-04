from flask import render_template, request, session, jsonify
from flask_socketio import emit, disconnect
from app import app, socketio, db
from models import User, ChatMessage, LegalCase, LegalKnowledge, SolicitorReferral, DocumentAnalysis
from nlp_processor import LegalNLPProcessor
from legal_knowledge import LegalKnowledgeRetriever
from referral_system import SolicitorReferralSystem
from openai_integration import ChatGPTLegalAssistant
from document_processor import DocumentProcessor
import uuid
import json
import logging
import os
from werkzeug.utils import secure_filename

# Initialize components
nlp_processor = LegalNLPProcessor()
knowledge_retriever = LegalKnowledgeRetriever()
referral_system = SolicitorReferralSystem()
chatgpt_assistant = ChatGPTLegalAssistant()

@app.route('/')
def index():
    """Landing page with legal disclaimer"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Main chat interface"""
    # Create or get user session
    if 'user_session' not in session:
        session['user_session'] = str(uuid.uuid4())
        
        # Create user record
        user = User()
        user.session_id = session['user_session']
        db.session.add(user)
        db.session.commit()
    
    return render_template('chat.html')

@app.route('/legal-disclaimer')
def legal_disclaimer():
    """Legal disclaimer page"""
    return render_template('legal_disclaimer.html')

@app.route('/api/chat-history')
def get_chat_history():
    """Get chat history for current session"""
    if 'user_session' not in session:
        return jsonify([])
    
    user = User.query.filter_by(session_id=session['user_session']).first()
    if not user:
        return jsonify([])
    
    messages = ChatMessage.query.filter_by(user_id=user.id).order_by(ChatMessage.created_at).all()
    
    history = []
    for msg in messages:
        history.append({
            'message': msg.message,
            'response': msg.response,
            'created_at': msg.created_at.isoformat(),
            'legal_category': msg.legal_category,
            'citations': json.loads(msg.citations) if msg.citations else []
        })
    
    return jsonify(history)

@app.route('/api/chat', methods=['POST'])
def handle_chat_message():
    """Handle chat message via HTTP POST"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Please enter a legal query.',
                'type': 'error'
            })
        
        # Get or create user session
        session_id = session.get('user_session')
        if not session_id:
            session['user_session'] = str(uuid.uuid4())
            session_id = session['user_session']
        
        user = User.query.filter_by(session_id=session_id).first()
        if not user:
            user = User()
            user.session_id = session_id
            db.session.add(user)
            db.session.commit()
        
        # Process the message with NLP
        analysis = nlp_processor.analyze_query(user_message)
        
        # Retrieve relevant legal knowledge from local database
        local_legal_info = knowledge_retriever.get_relevant_information(
            query=user_message,
            legal_category=analysis.get('category'),
            track_type=analysis.get('track_type')
        )
        
        # Get ChatGPT response for enhanced legal information
        chat_history = get_recent_chat_history(user.id)
        chatgpt_response = chatgpt_assistant.get_legal_response(
            user_query=user_message,
            chat_history=chat_history
        )
        
        # Generate enhanced response combining local knowledge and AI
        response_data = generate_enhanced_legal_response(
            user_message, analysis, local_legal_info, chatgpt_response
        )
        
        # Check if solicitor referral is needed
        referral_info = None
        if should_refer_to_solicitor(analysis, user_message):
            referral_info = referral_system.get_referral_recommendations(analysis)
        
        # Save message to database
        chat_message = ChatMessage()
        chat_message.user_id = user.id
        chat_message.message = user_message
        chat_message.response = response_data['response']
        chat_message.legal_category = analysis.get('category')
        chat_message.citations = json.dumps(response_data.get('citations', []))
        db.session.add(chat_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': response_data['response'],
            'citations': response_data.get('citations', []),
            'legal_category': analysis.get('category'),
            'track_type': analysis.get('track_type'),
            'referral_info': referral_info,
            'type': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error processing chat message: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'I apologize, but I encountered an error processing your query. Please try rephrasing your question or contact a qualified solicitor for assistance.',
            'type': 'error'
        })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logging.info('Client connected')
    emit('status', {'msg': 'Connected to UK Legal Chatbot'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logging.info('Client disconnected')

@socketio.on('legal_query')
def handle_legal_query(data):
    """Handle user message and generate response"""
    try:
        user_message = data.get('message', '').strip()
        
        if not user_message:
            emit('legal_response', {
                'message': 'Please enter a legal query.',
                'type': 'error'
            })
            return
        
        # Get or create user
        session_id = session.get('user_session')
        if not session_id:
            session['user_session'] = str(uuid.uuid4())
            session_id = session['user_session']
        
        user = User.query.filter_by(session_id=session_id).first()
        if not user:
            user = User()
            user.session_id = session_id
            db.session.add(user)
            db.session.commit()
        
        # Process the message with NLP
        emit('typing', {'typing': True})
        
        # Analyze the query
        analysis = nlp_processor.analyze_query(user_message)
        
        # Retrieve relevant legal knowledge from local database
        local_legal_info = knowledge_retriever.get_relevant_information(
            query=user_message,
            legal_category=analysis.get('category'),
            track_type=analysis.get('track_type')
        )
        
        # Get ChatGPT response for enhanced legal information
        chat_history = get_recent_chat_history(user.id)
        chatgpt_response = chatgpt_assistant.get_legal_response(
            user_query=user_message,
            chat_history=chat_history
        )
        
        # Generate enhanced response combining local knowledge and AI
        response_data = generate_enhanced_legal_response(
            user_message, analysis, local_legal_info, chatgpt_response
        )
        
        # Check if solicitor referral is needed
        referral_info = None
        if should_refer_to_solicitor(analysis, user_message):
            referral_info = referral_system.get_referral_recommendations(analysis)
        
        # Save message to database
        chat_message = ChatMessage()
        chat_message.user_id = user.id
        chat_message.message = user_message
        chat_message.response = response_data['response']
        chat_message.legal_category = analysis.get('category')
        chat_message.citations = json.dumps(response_data.get('citations', []))
        db.session.add(chat_message)
        db.session.commit()
        
        emit('typing', {'typing': False})
        emit('legal_response', {
            'message': response_data['response'],
            'citations': response_data.get('citations', []),
            'legal_category': analysis.get('category'),
            'track_type': analysis.get('track_type'),
            'referral_info': referral_info,
            'type': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        emit('typing', {'typing': False})
        emit('legal_response', {
            'message': 'I apologize, but I encountered an error processing your query. Please try rephrasing your question or contact a qualified solicitor for assistance.',
            'type': 'error'
        })

def get_recent_chat_history(user_id):
    """Get recent chat history for context"""
    messages = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at.desc()).limit(6).all()
    history = []
    for msg in reversed(messages):  # Reverse to get chronological order
        history.extend([
            {"sender": "user", "content": msg.message},
            {"sender": "assistant", "content": msg.response}
        ])
    return history

def generate_enhanced_legal_response(query, analysis, local_legal_info, chatgpt_response):
    """Generate legal response based on analysis and retrieved information"""
    
    # Determine track type and provide appropriate guidance
    track_type = analysis.get('track_type', 'unknown')
    category = analysis.get('category', 'general')
    
    response_parts = []
    citations = []
    
    # Add track-specific information
    if track_type == 'small_claims':
        response_parts.append("**Small Claims Track (up to £10,000)**\n")
        response_parts.append("This appears to be a small claims matter. Small claims are designed to be accessible to litigants in person, with simplified procedures and limited costs exposure.")
    elif track_type == 'fast_track':
        response_parts.append("**Fast Track (£10,000 - £25,000)**\n")
        response_parts.append("This appears to be a fast track claim. Fast track claims have standard directions and fixed trial costs, with cases typically concluded within 30 weeks.")
    elif track_type == 'multi_track':
        response_parts.append("**Multi-Track (£25,000 - £100,000)**\n")
        response_parts.append("This appears to be a multi-track claim. Multi-track claims involve case management conferences, costs budgeting, and more complex procedures.")
    
    # Add ChatGPT AI enhanced information if available
    if chatgpt_response.get('response'):
        response_parts.append("\n**AI Legal Guidance:**")
        response_parts.append(chatgpt_response['response'])
        
        # Add metadata from ChatGPT analysis
        if chatgpt_response.get('category'):
            citations.append({
                'type': 'ai_analysis',
                'category': chatgpt_response['category'],
                'track': chatgpt_response.get('track'),
                'urgency': chatgpt_response.get('urgency'),
                'source': 'ChatGPT Legal Assistant'
            })
    
    # Add local legal information as backup/supplementary
    if local_legal_info.get('cases'):
        response_parts.append("\n**Relevant Case Law:**")
        for case in local_legal_info['cases'][:2]:  # Limit to 2 most relevant cases
            response_parts.append(f"• {case['case_name']} {case['citation']} - {case['summary']}")
            citations.append({
                'type': 'case',
                'name': case['case_name'],
                'citation': case['citation'],
                'url': case.get('url')
            })
    
    if local_legal_info.get('procedures'):
        response_parts.append("\n**Relevant Procedures:**")
        for procedure in local_legal_info['procedures'][:2]:
            response_parts.append(f"• {procedure['title']}: {procedure['summary']}")
            citations.append({
                'type': 'procedure',
                'title': procedure['title'],
                'source': procedure.get('source')
            })
    
    # Add general guidance
    response_parts.append("\n**Important Notes:**")
    response_parts.append("• This information is for guidance only and does not constitute legal advice")
    response_parts.append("• Consider seeking professional legal advice for your specific circumstances")
    response_parts.append("• Court procedures and deadlines are strict - ensure compliance with all requirements")
    
    # Add costs information if relevant
    if 'costs' in query.lower() or 'fees' in query.lower():
        response_parts.append(f"\n**Court Fees Information:**")
        if track_type == 'small_claims':
            response_parts.append("• Small claims have limited costs exposure - generally only court fees and expert witness costs")
        elif track_type == 'fast_track':
            response_parts.append("• Fast track claims have fixed trial costs and limited recoverable costs")
        elif track_type == 'multi_track':
            response_parts.append("• Multi-track claims require costs budgeting and have full costs exposure")
    
    return {
        'response': '\n'.join(response_parts),
        'citations': citations
    }

def should_refer_to_solicitor(analysis, query):
    """Determine if the query suggests professional legal advice is needed"""
    referral_indicators = [
        'urgent', 'emergency', 'injunction', 'court date', 'deadline',
        'served with', 'claim form', 'defence', 'trial', 'represent me',
        'complex', 'multiple parties', 'international', 'regulatory'
    ]
    
    query_lower = query.lower()
    
    # Check for referral indicators
    for indicator in referral_indicators:
        if indicator in query_lower:
            return True
    
    # Check for high-value claims (multi-track)
    if analysis.get('track_type') == 'multi_track':
        return True
    
    # Check for complex legal categories
    complex_categories = ['professional_negligence', 'commercial_dispute', 'employment']
    if analysis.get('category') in complex_categories:
        return True
    
    return False

# Initialize document processor
document_processor = DocumentProcessor()

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/document-analysis')
def document_analysis():
    """Document analysis page"""
    return render_template('document_analysis.html')

@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    """Handle document upload and analysis"""
    try:
        # Check if file is present
        if 'document' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded. Please select a document to analyze.',
                'type': 'error'
            })
        
        file = request.files['document']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected. Please choose a document to upload.',
                'type': 'error'
            })
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not supported. Please upload PDF, Word (.docx), or text (.txt) files only.',
                'type': 'error'
            })
        
        # Get or create user session
        session_id = session.get('user_session')
        if not session_id:
            session['user_session'] = str(uuid.uuid4())
            session_id = session['user_session']
        
        user = User.query.filter_by(session_id=session_id).first()
        if not user:
            user = User()
            user.session_id = session_id
            db.session.add(user)
            db.session.commit()
        
        # Read file content
        file_content = file.read()
        
        # Check file size
        if len(file_content) == 0:
            return jsonify({
                'success': False,
                'error': 'The uploaded file appears to be empty. Please check the file and try again.',
                'type': 'error'
            })
        
        # Extract text from document
        filename = secure_filename(file.filename or 'unknown.txt')
        try:
            document_text = document_processor.extract_text_from_file(file_content, filename)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Could not read the document. Please ensure the file is not corrupted and try again. Error: {str(e)}',
                'type': 'error'
            })
        
        # Check if we extracted meaningful text
        if not document_text.strip() or len(document_text.strip()) < 50:
            return jsonify({
                'success': False,
                'error': 'The document appears to contain insufficient text for analysis. Please ensure the document contains readable text content.',
                'type': 'error'
            })
        
        # Analyze the document using AI
        try:
            analysis_result = document_processor.analyze_skeleton_argument(document_text)
        except Exception as e:
            logging.error(f"Error analyzing document: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Unable to analyze the document at this time. Please try again later or contact support if the problem persists.',
                'type': 'error'
            })
        
        # Save document analysis to database
        doc_analysis = DocumentAnalysis()
        doc_analysis.user_id = user.id
        doc_analysis.filename = filename
        doc_analysis.document_text = document_text[:10000]  # Store first 10k chars to avoid DB limits
        doc_analysis.analysis_summary = analysis_result.get('document_summary', '')
        doc_analysis.legal_arguments = json.dumps(analysis_result.get('claimant_arguments', []))
        doc_analysis.defence_points = json.dumps(analysis_result.get('defence_points', []))
        doc_analysis.claim_value_estimate = analysis_result.get('claim_value_estimate', 0)
        doc_analysis.track_type = analysis_result.get('track_assessment', 'small_claims')
        doc_analysis.legal_categories = json.dumps(analysis_result.get('legal_categories', []))
        
        db.session.add(doc_analysis)
        db.session.commit()
        
        # Format response for user
        formatted_response = document_processor.format_defence_response(analysis_result)
        
        # Also save as a chat message for context
        chat_message = ChatMessage()
        chat_message.user_id = user.id
        chat_message.message = f"Document Analysis: {filename}"
        chat_message.response = formatted_response
        chat_message.legal_category = analysis_result.get('legal_categories', ['document_analysis'])[0] if analysis_result.get('legal_categories') else 'document_analysis'
        chat_message.citations = json.dumps([{
            'type': 'document_analysis',
            'filename': filename,
            'claim_value': analysis_result.get('claim_value_estimate', 0),
            'track_type': analysis_result.get('track_assessment', 'small_claims')
        }])
        
        db.session.add(chat_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'formatted_response': formatted_response,
            'document_id': doc_analysis.id,
            'filename': filename,
            'type': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error processing document upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred while processing your document. Please try again or contact support.',
            'type': 'error'
        })

@app.route('/api/document-history')
def get_document_history():
    """Get document analysis history for current session"""
    if 'user_session' not in session:
        return jsonify([])
    
    user = User.query.filter_by(session_id=session['user_session']).first()
    if not user:
        return jsonify([])
    
    analyses = DocumentAnalysis.query.filter_by(user_id=user.id).order_by(DocumentAnalysis.created_at.desc()).all()
    
    history = []
    for analysis in analyses:
        history.append({
            'id': analysis.id,
            'filename': analysis.filename,
            'created_at': analysis.created_at.isoformat(),
            'document_type': analysis.document_type,
            'analysis_summary': analysis.analysis_summary,
            'claim_value_estimate': analysis.claim_value_estimate,
            'track_type': analysis.track_type,
            'legal_categories': json.loads(analysis.legal_categories) if analysis.legal_categories else []
        })
    
    return jsonify(history)
