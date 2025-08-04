// UK Legal Chatbot - Chat Interface JavaScript

class LegalChatBot {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.isTyping = false;
        this.messageHistory = [];
        
        this.init();
    }
    
    init() {
        this.initializeSocket();
        this.bindEvents();
        this.loadChatHistory();
    }
    
    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.handleConnection(true);
        });
        
        this.socket.on('disconnect', () => {
            this.handleConnection(false);
        });
        
        this.socket.on('status', (data) => {
            console.log('Status:', data.msg);
        });
        
        this.socket.on('bot_response', (data) => {
            this.handleBotResponse(data);
        });
        
        this.socket.on('typing', (data) => {
            this.handleTypingIndicator(data.typing);
        });
    }
    
    bindEvents() {
        // Chat form submission
        const chatForm = document.getElementById('chat-form');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // Character counter
        messageInput.addEventListener('input', (e) => {
            const remaining = 1000 - e.target.value.length;
            const counter = document.querySelector('.char-counter');
            if (counter) {
                counter.textContent = `${remaining} characters remaining`;
            }
        });
        
        // Quick question buttons
        const quickButtons = document.querySelectorAll('.quick-question');
        quickButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const question = e.target.getAttribute('data-question');
                messageInput.value = question;
                this.sendMessage();
            });
        });
        
        // Clear chat button
        const clearButton = document.getElementById('clear-chat');
        clearButton.addEventListener('click', () => {
            this.clearChat();
        });
        
        // Enter key handling
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    handleConnection(connected) {
        this.isConnected = connected;
        const statusElement = document.getElementById('connection-status');
        
        if (connected) {
            statusElement.className = 'badge bg-success';
            statusElement.innerHTML = '<i class="fas fa-circle me-1"></i>Connected';
        } else {
            statusElement.className = 'badge bg-danger';
            statusElement.innerHTML = '<i class="fas fa-circle me-1"></i>Disconnected';
        }
    }
    
    sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message || !this.isConnected) {
            return;
        }
        
        // Validate message
        if (message.length > 1000) {
            this.showError('Message too long. Please keep it under 1000 characters.');
            return;
        }
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input
        messageInput.value = '';
        
        // Send to server
        this.socket.emit('user_message', { message: message });
        
        // Disable send button temporarily
        this.setSendButtonState(false);
    }
    
    addMessage(content, type, data = {}) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const timestamp = new Date().toLocaleTimeString('en-GB', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">
                    ${this.escapeHtml(content)}
                </div>
                <div class="message-timestamp">${timestamp}</div>
            `;
        } else {
            // Bot message with enhanced formatting
            let messageHTML = `
                <div class="message-content">
                    ${this.formatBotMessage(content)}
                    ${this.addTrackBadge(data.track_type)}
                    ${this.addCitations(data.citations)}
                    ${this.addReferralInfo(data.referral_info)}
                </div>
                <div class="message-timestamp">${timestamp}</div>
            `;
            messageDiv.innerHTML = messageHTML;
        }
        
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Store in history
        this.messageHistory.push({
            content: content,
            type: type,
            timestamp: new Date(),
            data: data
        });
    }
    
    formatBotMessage(content) {
        // Convert markdown-style formatting to HTML
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/•/g, '&bull;');
    }
    
    addTrackBadge(trackType) {
        if (!trackType) return '';
        
        const badges = {
            'small_claims': '<span class="badge bg-success track-badge small-claims mb-2">Small Claims Track</span>',
            'fast_track': '<span class="badge bg-warning track-badge fast-track mb-2">Fast Track</span>',
            'multi_track': '<span class="badge bg-danger track-badge multi-track mb-2">Multi-Track</span>'
        };
        
        return badges[trackType] || '';
    }
    
    addCitations(citations) {
        if (!citations || citations.length === 0) return '';
        
        let citationHTML = '<div class="citation mt-3"><h6 class="text-info mb-2"><i class="fas fa-quote-left me-2"></i>Sources:</h6>';
        
        citations.forEach(citation => {
            if (citation.type === 'case') {
                citationHTML += `
                    <div class="citation-item mb-1">
                        <strong>${citation.name}</strong> ${citation.citation}
                        ${citation.url ? `<a href="${citation.url}" target="_blank" class="citation-link ms-2"><i class="fas fa-external-link-alt"></i></a>` : ''}
                    </div>
                `;
            } else if (citation.type === 'procedure') {
                citationHTML += `
                    <div class="citation-item mb-1">
                        ${citation.title}
                        ${citation.source ? `<a href="${citation.source}" target="_blank" class="citation-link ms-2"><i class="fas fa-external-link-alt"></i></a>` : ''}
                    </div>
                `;
            }
        });
        
        citationHTML += '</div>';
        return citationHTML;
    }
    
    addReferralInfo(referralInfo) {
        if (!referralInfo) return '';
        
        let referralHTML = '<div class="referral-box mt-3">';
        referralHTML += '<h6 class="text-warning mb-3"><i class="fas fa-user-tie me-2"></i>Professional Legal Advice</h6>';
        
        if (referralInfo.referral_advice) {
            referralHTML += `<p class="mb-3">${referralInfo.referral_advice}</p>`;
        }
        
        if (referralInfo.recommended_solicitors && referralInfo.recommended_solicitors.length > 0) {
            referralHTML += '<h6 class="mb-2">Recommended Solicitors:</h6>';
            referralInfo.recommended_solicitors.forEach(solicitor => {
                referralHTML += `
                    <div class="card bg-light mb-2">
                        <div class="card-body py-2">
                            <h6 class="card-title mb-1">${solicitor.firm_name}</h6>
                            <p class="card-text small mb-1">
                                <strong>Contact:</strong> ${solicitor.contact_name || 'Contact available'}
                                ${solicitor.location ? `<br><strong>Location:</strong> ${solicitor.location}` : ''}
                            </p>
                            <p class="card-text small mb-1">
                                <strong>Specialties:</strong> ${solicitor.specialties.join(', ')}
                            </p>
                            ${solicitor.contact_phone ? `<small><i class="fas fa-phone me-1"></i>${solicitor.contact_phone}</small>` : ''}
                            ${solicitor.website ? `<small class="ms-2"><a href="${solicitor.website}" target="_blank"><i class="fas fa-globe me-1"></i>Website</a></small>` : ''}
                        </div>
                    </div>
                `;
            });
        }
        
        if (referralInfo.funding_options && referralInfo.funding_options.length > 0) {
            referralHTML += '<h6 class="mb-2 mt-3">Funding Options:</h6>';
            referralHTML += '<div class="row">';
            referralInfo.funding_options.forEach(option => {
                referralHTML += `
                    <div class="col-md-6 mb-2">
                        <div class="card bg-info bg-opacity-10 border-info">
                            <div class="card-body py-2">
                                <h6 class="card-title small mb-1">${option.type}</h6>
                                <p class="card-text small mb-0">${option.description}</p>
                            </div>
                        </div>
                    </div>
                `;
            });
            referralHTML += '</div>';
        }
        
        referralHTML += '</div>';
        return referralHTML;
    }
    
    handleBotResponse(data) {
        this.setSendButtonState(true);
        
        if (data.type === 'error') {
            this.showError(data.message);
        } else {
            this.addMessage(data.message, 'bot', data);
        }
    }
    
    handleTypingIndicator(isTyping) {
        const chatMessages = document.getElementById('chat-messages');
        let typingIndicator = document.getElementById('typing-indicator');
        
        if (isTyping) {
            if (!typingIndicator) {
                typingIndicator = document.createElement('div');
                typingIndicator.id = 'typing-indicator';
                typingIndicator.className = 'message bot-message';
                typingIndicator.innerHTML = `
                    <div class="typing-indicator">
                        <div class="typing-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                        <small class="ms-2">Legal assistant is typing...</small>
                    </div>
                `;
                chatMessages.appendChild(typingIndicator);
                this.scrollToBottom();
            }
        } else {
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }
    }
    
    setSendButtonState(enabled) {
        const sendButton = document.getElementById('send-button');
        const messageInput = document.getElementById('message-input');
        
        if (enabled) {
            sendButton.disabled = false;
            sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
            messageInput.disabled = false;
        } else {
            sendButton.disabled = true;
            sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            messageInput.disabled = true;
        }
    }
    
    showError(message) {
        const chatMessages = document.getElementById('chat-messages');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger mb-3';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Error:</strong> ${this.escapeHtml(message)}
        `;
        
        chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
        
        // Auto-remove error after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            const chatMessages = document.getElementById('chat-messages');
            chatMessages.innerHTML = `
                <div class="message bot-message">
                    <div class="message-content">
                        <strong>Chat Cleared</strong><br><br>
                        Hello! I'm ready to help with your UK legal queries.
                        Please describe your legal issue or ask a specific question.
                    </div>
                    <div class="message-timestamp">Just now</div>
                </div>
            `;
            this.messageHistory = [];
        }
    }
    
    loadChatHistory() {
        fetch('/api/chat-history')
            .then(response => response.json())
            .then(history => {
                history.forEach(item => {
                    this.addMessage(item.message, 'user');
                    if (item.response) {
                        this.addMessage(item.response, 'bot', {
                            legal_category: item.legal_category,
                            citations: item.citations
                        });
                    }
                });
            })
            .catch(error => {
                console.error('Error loading chat history:', error);
            });
    }
    
    scrollToBottom() {
        const chatContainer = document.getElementById('chat-container');
        setTimeout(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 100);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new LegalChatBot();
});

// Add some utility functions for enhanced UX
document.addEventListener('DOMContentLoaded', () => {
    // Add copy functionality to code blocks and citations
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('copy-btn')) {
            const textToCopy = e.target.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(() => {
                e.target.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    e.target.innerHTML = '<i class="fas fa-copy"></i> Copy';
                }, 2000);
            });
        }
    });
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to focus on message input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('message-input').focus();
        }
        
        // Ctrl/Cmd + L to clear chat
        if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
            e.preventDefault();
            document.getElementById('clear-chat').click();
        }
    });
    
    // Add notification permission request
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});
