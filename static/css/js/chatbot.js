// ========================================
// CareerMantra AI - Smart Career Chatbot
// OpenAI API + Typing Effect + Voice Input
// ========================================

class CareerChatbot {
    constructor() {
        this.conversation = [];
        this.isTyping = false;
        this.isMobile = window.innerWidth < 768;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadConversationHistory();
        this.scrollToBottom();
        
        // Welcome message
        setTimeout(() => this.addBotMessage('Hi! I\'m CareerMantra AI 🤖\n\nAsk me anything about:\n• Interview prep\n• Resume tips\n• Tech trends\n• Job hunting\n• Coding help', 'welcome'), 500);
    }

    bindEvents() {
        const sendBtn = document.getElementById('send-btn');
        const chatInput = document.getElementById('chat-input');
        const toggleBtn = document.getElementById('chatbot-toggle');

        if (sendBtn) sendBtn.onclick = () => this.sendMessage();
        if (chatInput) {
            chatInput.onkeypress = (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            };
        }
        if (toggleBtn) toggleBtn.onclick = this.toggleChatbot;

        // Voice input
        if ('webkitSpeechRecognition' in window) {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            document.getElementById('voice-btn')?.addEventListener('click', () => {
                recognition.start();
                this.addBotMessage('🎤 Listening... Speak now!');
            });

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('chat-input').value = transcript;
                this.sendMessage();
            };
        }
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message || this.isTyping) return;

        // Add user message
        this.addUserMessage(message);
        input.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await this.getAIResponse(message);
            this.hideTypingIndicator();
            this.addBotMessage(response);
        } catch (error) {
            this.hideTypingIndicator();
            this.addBotMessage('Sorry, I\'m having trouble connecting. Please try again! 😅');
        }
        
        this.saveConversationHistory();
    }

    addUserMessage(message) {
        const chatbox = document.getElementById('chatbox');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat outgoing animate-slideInRight';
        messageDiv.innerHTML = `
            <div class="chat-content">
                <p>${this.escapeHtml(message)}</p>
                <span class="time">${this.getCurrentTime()}</span>
            </div>
        `;
        chatbox.appendChild(messageDiv);
        this.scrollToBottom();
        this.conversation.push({ role: 'user', content: message });
    }

    addBotMessage(message, type = 'normal') {
        const chatbox = document.getElementById('chatbox');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat incoming animate-slideInLeft ${type}`;
        
        messageDiv.innerHTML = `
            <div class="chat-avatar">
                <div class="avatar">🤖</div>
            </div>
            <div class="chat-content">
                <p class="typing-effect" data-text="${this.escapeHtml(message)}">${this.escapeHtml(message)}</p>
                <span class="time">${this.getCurrentTime()}</span>
            </div>
        `;
        
        chatbox.appendChild(messageDiv);
        this.typeWriter(messageDiv.querySelector('.typing-effect'));
        this.scrollToBottom();
        this.conversation.push({ role: 'bot', content: message });
    }

    showTypingIndicator() {
        this.isTyping = true;
        const chatbox = document.getElementById('chatbox');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'chat incoming typing';
        typingDiv.innerHTML = `
            <div class="chat-avatar">
                <div class="avatar">🤖</div>
            </div>
            <div class="chat-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
                <span class="time">${this.getCurrentTime()}</span>
            </div>
        `;
        chatbox.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
        this.scrollToBottom();
    }

    async getAIResponse(message) {
        // Simulate API call to your Flask backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error('API failed');
        }
        
        const data = await response.json();
        return data.response || "That's interesting! Tell me more about your career goals.";
    }

    typeWriter(element) {
        const text = element.getAttribute('data-text');
        let i = 0;
        
        const timer = setInterval(() => {
            element.textContent = text.slice(0, i);
            i++;
            
            if (i > text.length) {
                clearInterval(timer);
            }
        }, 30);
    }

    scrollToBottom() {
        const chatbox = document.getElementById('chatbox');
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getCurrentTime() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    saveConversationHistory() {
        localStorage.setItem('chatbot_history', JSON.stringify(this.conversation.slice(-50))); // Last 50 messages
    }

    loadConversationHistory() {
        const history = localStorage.getItem('chatbot_history');
        if (history) {
            this.conversation = JSON.parse(history);
            this.conversation.forEach(msg => {
                if (msg.role === 'user') {
                    this.addUserMessage(msg.content);
                } else {
                    this.addBotMessage(msg.content);
                }
            });
        }
    }

    toggleChatbot() {
        const chatbot = document.getElementById('chatbot-container');
        const toggleBtn = document.getElementById('chatbot-toggle');
        chatbot.classList.toggle('hidden');
        toggleBtn.classList.toggle('active');
    }

    clearChat() {
        const chatbox = document.getElementById('chatbox');
        chatbox.innerHTML = '';
        this.conversation = [];
        localStorage.removeItem('chatbot_history');
        this.addBotMessage('Chat cleared! How can I help you today? 😊');
    }
}

// 🎮 Initialize Chatbot
const chatbot = new CareerChatbot();

// 🔔 Global Functions (for HTML onclick)
window.toggleChatbot = () => chatbot.toggleChatbot();
window.clearChat = () => chatbot.clearChat();
window.sendMessage = () => chatbot.sendMessage();

// 🎨 CSS Animations (Auto-inject)
const style = document.createElement('style');
style.textContent = `
    .typing-effect { overflow: hidden; border-right: 2px solid #4f46e5; white-space: nowrap; }
    .typing-dots span { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #4f46e5; margin: 0 2px; animation: typing 1.4s infinite; }
    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typing { 0%, 60%, 100% { transform: translateY(0); opacity: 0.4; } 30% { transform: translateY(-10px); opacity: 1; } }
    .animate-slideInRight { animation: slideInRight 0.3s ease-out; }
    .animate-slideInLeft { animation: slideInLeft 0.3s ease-out; }
    @keyframes slideInRight { from { opacity: 0; transform: translateX(100%); } to { opacity: 1; transform: translateX(0); } }
    @keyframes slideInLeft { from { opacity: 0; transform: translateX(-100%); } to { opacity: 1; transform: translateX(0); } }
`;
document.head.appendChild(style);
