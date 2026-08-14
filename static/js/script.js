// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script loaded and DOM ready');
    
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const typingIndicator = document.getElementById('typingIndicator');
    const charCount = document.getElementById('charCount');
    
    if (!messageInput) {
        console.error('messageInput element not found!');
        return;
    }
    
    const maxLength = parseInt(messageInput.getAttribute('maxlength')) || 500;
    console.log('Elements loaded:', { chatMessages, messageInput, sendBtn, typingIndicator });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        
        // Update character count
        const currentLength = this.value.length;
        charCount.textContent = currentLength;
        if (currentLength > maxLength * 0.9) {
            charCount.style.color = '#dc3545';
        } else {
            charCount.style.color = '#6c757d';
        }
    });
    
    // Send message functions
    async function sendMessage() {
        const message = messageInput.value.trim();
        console.log('sendMessage called with:', message);
        
        if (!message) {
            console.warn('Message is empty');
            return;
        }
        
        // Disable input during processing
        messageInput.disabled = true;
        sendBtn.disabled = true;
        
        // Add user message
        addMessage(message, 'user');
        messageInput.value = '';
        messageInput.style.height = 'auto';
        charCount.textContent = '0';
        
        // Show typing indicator
        typingIndicator.classList.add('active');
        scrollToBottom();
        
        try {
            console.log('Sending request to /api/chat');
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });
            
            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);
            
            // Hide typing indicator
            typingIndicator.classList.remove('active');
            
            // Add bot response
            if (data.response) {
                addMessage(data.response, 'bot');
            } else if (data.error) {
                addMessage('Sorry, I encountered an error: ' + data.error, 'bot');
            }
        } catch (error) {
            console.error('Error:', error);
            typingIndicator.classList.remove('active');
            addMessage('Sorry, I encountered a network error. Please try again.', 'bot');
        } finally {
            messageInput.disabled = false;
            sendBtn.disabled = false;
            messageInput.focus();
        }
    }
    
    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = text.replace(/\n/g, '<br>');
        
        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        const now = new Date();
        const timeStr = now.getHours().toString().padStart(2, '0') + ':' + 
                       now.getMinutes().toString().padStart(2, '0');
        timestamp.textContent = (type === 'user' ? 'You' : 'Assistant') + ` • ${timeStr}`;
        
        messageDiv.appendChild(bubble);
        messageDiv.appendChild(timestamp);
        chatMessages.appendChild(messageDiv);
        
        scrollToBottom();
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Event listeners
    console.log('Adding event listeners');
    sendBtn.addEventListener('click', function() {
        console.log('Send button clicked');
        sendMessage();
    });
    
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            console.log('Enter key pressed');
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Quick reply buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            console.log('Quick action clicked:', query);
            if (query) {
                messageInput.value = query;
                messageInput.dispatchEvent(new Event('input'));
                sendMessage();
            }
        });
    });
    
    // Modal handling
    function setupModal(buttonId, modalId, contentId, fetchUrl) {
        const btn = document.getElementById(buttonId);
        const modal = document.getElementById(modalId);
        const closeBtn = modal.querySelector('.modal-close');
        const content = document.getElementById(contentId);
        
        btn.addEventListener('click', async function() {
            modal.classList.add('active');
            content.innerHTML = '<p>Loading...</p>';
            
            try {
                const response = await fetch(fetchUrl);
                const data = await response.json();
                
                if (data.note) {
                    content.innerHTML = `<pre style="white-space: pre-wrap;">${data.note}</pre>`;
                } else if (data.tickets_deflected) {
                    content.innerHTML = `
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                            <div class="metric-card">
                                <h3>Order Status</h3>
                                <p style="font-size: 2rem; color: #0073e6;">${data.intents_handled.order_status}</p>
                            </div>
                            <div class="metric-card">
                                <h3>Returns/Refunds</h3>
                                <p style="font-size: 2rem; color: #28a745;">${data.intents_handled.returns_refunds}</p>
                            </div>
                            <div class="metric-card">
                                <h3>Stock Availability</h3>
                                <p style="font-size: 2rem; color: #ffc107;">${data.intents_handled.stock_availability}</p>
                            </div>
                        </div>
                        <div style="margin-top: 20px; text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                            <h3>Total Deflected: ${data.tickets_deflected.total}</h3>
                            <p>Total Conversations: ${data.total_conversations}</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading modal:', error);
                content.innerHTML = '<p>Error loading data. Please try again.</p>';
            }
        });
        
        closeBtn.addEventListener('click', function() {
            modal.classList.remove('active');
        });
        
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    }
    
    // Setup modals
    setupModal('analyticsBtn', 'analyticsModal', 'analyticsContent', '/api/analytics');
    setupModal('readinessBtn', 'readinessModal', 'readinessContent', '/api/readiness');
    
    // Focus input on load
    messageInput.focus();
    console.log('Initialization complete');
});