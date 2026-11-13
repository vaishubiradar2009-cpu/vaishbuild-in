/**
 * ====================================================================
 * MediCare AI - Chatbot Controller
 * File: static/js/chatbot.js
 * ====================================================================
 */

class ChatbotController {
    constructor() {
        this.messagesContainer = document.getElementById('chat-messages');
        this.inputField = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('chat-send-btn');
        this.clearBtn = document.getElementById('chat-clear-btn');
        this.suggestionsContainer = document.getElementById('chat-suggestions');
        
        // Session identifier
        this.sessionId = sessionStorage.getItem('medicare_chat_session') || this.generateSessionId();
        sessionStorage.setItem('medicare_chat_session', this.sessionId);

        this.init();
    }

    generateSessionId() {
        return 'sess_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    init() {
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.sendMessage());
        }

        if (this.inputField) {
            this.inputField.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        if (this.clearBtn) {
            this.clearBtn.addEventListener('click', () => this.clearChat());
        }

        // Quick suggestion chips
        if (this.suggestionsContainer) {
            this.suggestionsContainer.addEventListener('click', (e) => {
                const chip = e.target.closest('.suggestion-chip');
                if (chip) {
                    const text = chip.getAttribute('data-prompt') || chip.innerText;
                    this.inputField.value = text;
                    this.sendMessage();
                }
            });
        }

        // Load greeting message if empty
        if (this.messagesContainer && this.messagesContainer.children.length === 0) {
            this.showWelcomeGreeting();
        }
    }

    showWelcomeGreeting() {
        const lang = window.currentLanguage || 'en';
        let greeting = "";
        let disclaimer = "";

        if (lang === 'hi') {
            greeting = "नमस्ते! मैं मेडीकेयर एआई स्वास्थ्य सहायक हूँ। मैं सामान्य स्वास्थ्य जानकारी, जीवनशैली सुझावों और लक्षणों को समझने में आपकी सहायता कर सकता हूँ। आज मैं आपकी क्या मदद कर सकता हूँ?";
            disclaimer = "सूचना: मेडीकेयर एआई केवल सूचनात्मक मार्गदर्शन प्रदान करता है और यह नैदानिक चिकित्सा सलाह नहीं है।";
        } else if (lang === 'kn') {
            greeting = "ನಮಸ್ಕಾರ! ನಾನು ಮೆಡಿಕೇರ್ ಎಐ ಆರೋಗ್ಯ ಸಹಾಯಕ. ಸಾಮಾನ್ಯ ಆರೋಗ್ಯ ಮಾಹಿತಿ, ಆಹಾರ ಪಥ್ಯ ಮತ್ತು ಆರೋಗ್ಯ ಸಲಹೆಗಳಿಗೆ ನಾನು ನಿಮಗೆ ಮಾರ್ಗದರ್ಶನ ನೀಡಬಲ್ಲೆ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?";
            disclaimer = "ಮಾಹಿತಿ: ಮೆಡಿಕೇರ್ ಎಐ ಮಾಹಿತಿಗಾಗಿ ಮಾತ್ರ ಮತ್ತು ಇದು ವೈದ್ಯಕೀಯ ರೋಗನಿರ್ಣಯವಲ್ಲ.";
        } else {
            greeting = "Hello! I am your MediCare AI healthcare assistant. I can help answer wellness queries, provide healthy lifestyle guidance, and help you navigate care options. How can I assist you today?";
            disclaimer = "Notice: MediCare AI provides informational guidance only and is not a medical diagnosis.";
        }

        this.appendMessage('ai', greeting, { disclaimer });
    }

    async sendMessage() {
        const text = this.inputField.value.trim();
        if (!text) return;

        // Render user message
        this.appendMessage('user', text);
        this.inputField.value = '';
        this.inputField.focus();

        // Show typing indicator
        const typingId = this.showTypingIndicator();

        try {
            const lang = window.currentLanguage || 'en';
            const data = await api.sendChatMessage(text, this.sessionId, lang);
            this.removeTypingIndicator(typingId);

            this.appendMessage('ai', data.reply, {
                is_emergency: data.is_emergency,
                disclaimer: data.disclaimer
            });

            if (data.is_emergency) {
                window.showToast("Emergency alert detected! Dial 108 immediately.", "error");
            }
        } catch (err) {
            this.removeTypingIndicator(typingId);
            this.appendMessage('ai', "I am currently having difficulty connecting to the medical AI service. Please try again or consult a doctor directly.", {
                is_emergency: false
            });
            window.showToast(err.message, "error");
        }
    }

    appendMessage(sender, text, options = {}) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender}`;

        if (options.is_emergency) {
            bubble.classList.add('emergency-alert');
        }

        // Simple markdown parsing for bold & bullets
        let formatted = this.formatMessageText(text);

        let html = `<div>${formatted}</div>`;
        if (options.disclaimer && sender === 'ai') {
            html += `<div class="chat-disclaimer-note">${options.disclaimer}</div>`;
        }

        bubble.innerHTML = html;
        this.messagesContainer.appendChild(bubble);
        this.scrollToBottom();
    }

    formatMessageText(text) {
        if (!text) return "";
        let safe = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Format **bold**
        safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Format bullet points
        safe = safe.replace(/^[•\-\*]\s+(.*)$/gm, '• $1');
        // Convert linebreaks
        safe = safe.replace(/\n/g, '<br>');
        return safe;
    }

    showTypingIndicator() {
        const id = 'typing_' + Date.now();
        const indicator = document.createElement('div');
        indicator.id = id;
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        this.messagesContainer.appendChild(indicator);
        this.scrollToBottom();
        return id;
    }

    removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    clearChat() {
        this.sessionId = this.generateSessionId();
        sessionStorage.setItem('medicare_chat_session', this.sessionId);
        this.messagesContainer.innerHTML = '';
        this.showWelcomeGreeting();
        window.showToast("Conversation cleared", "info");
    }
}
