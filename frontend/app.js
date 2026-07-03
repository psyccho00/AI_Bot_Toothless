document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-container');
    const sendBtn = document.getElementById('send-btn');

    // Hardcode user_id=1 as discussed to keep it beginner-friendly
    const USER_ID = 1;

    // Helper to escape HTML tags to prevent XSS
    function escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // A simple function to render markdown-like text safely
    function formatMessage(text) {
        let safeText = escapeHTML(text);
        // Basic markdown parsing for bold and line breaks
        let html = safeText
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        return html;
    }

    function appendUserMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message user-message';
        // User text is just escaped, no markdown formatting needed
        msgDiv.innerHTML = `<div class="message-content">${escapeHTML(text)}</div>`;
        chatContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendSystemMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message system-message';
        msgDiv.innerHTML = `<div class="message-content">${formatMessage(text)}</div>`;
        chatContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message system-message loading-message';
        loadingDiv.id = 'loading-message';
        loadingDiv.innerHTML = `
            <div class="message-content typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <span class="analyzing-text">Analyzing...</span>
            </div>
        `;
        chatContainer.appendChild(loadingDiv);
        scrollToBottom();
    }

    function hideLoading() {
        const loadingDiv = document.getElementById('loading-message');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const message = chatInput.value.trim();
        if (!message) return;

        // Clear input and append message
        chatInput.value = '';
        appendUserMessage(message);

        // Set loading state
        chatInput.disabled = true;
        sendBtn.disabled = true;
        showLoading();

        try {
            // Send the request to /toothless/chat API
            const payload = {
                user_id: USER_ID,
                message: message,
                context: null
            };

            const response = await fetch(`/toothless/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            hideLoading();

            if (!response.ok) {
                // Handle 404 if user_id=1 doesn't exist
                if (response.status === 404) {
                    throw new Error("User (ID 1) not found. Please register a user first via the API (/docs).");
                }
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to get assessment");
            }

            const data = await response.json();
            
            // Format and display response
            let assessmentText = data.response || "No assessment generated.";
            appendSystemMessage(assessmentText);

        } catch (error) {
            hideLoading();
            appendSystemMessage("⚠️ Error: " + error.message);
            console.error("API Error:", error);
        } finally {
            // Reset state
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    });
});
