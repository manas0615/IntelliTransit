/**
 * IntelliTransit - AI Assistant Client Module
 */
import { api } from './api.js';
import { auth } from './auth.js';

document.addEventListener('DOMContentLoaded', async () => {
  await auth.initAuthNav();

  const chatMessages = document.getElementById('chatMessages');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const clearChatBtn = document.getElementById('clearChatBtn');
  const chipButtons = document.querySelectorAll('.chip-btn');

  let messageHistory = [];

  // Submit message
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;

    appendMessage('user', message);
    chatInput.value = '';
    sendBtn.disabled = true;

    // Add typing indicator
    const typingElem = appendTypingIndicator();

    try {
      const response = await api.post('/api/ai/chat', {
        message: message,
        history: messageHistory
      });

      removeTypingIndicator(typingElem);

      if (response && (response.success === true || response.status === 'success') && response.data) {
        const reply = response.data.reply || 'Here is what I found for your request.';
        const badge = document.getElementById('aiModelBadge');
        if (badge) {
          if (response.data.mode === 'GEMINI') {
            badge.textContent = 'Powered by Gemini 2.5 Flash & Backend Tools';
          } else {
            badge.textContent = 'Demo AI Mode • Backend-Authoritative Transit Intelligence';
          }
        }
        appendMessage('ai', reply);
        messageHistory.push({ role: 'user', content: message });
        messageHistory.push({ role: 'model', content: reply });
      } else {
        appendMessage('ai', 'Sorry, I could not process that request. Please try again.');
      }
    } catch (err) {
      removeTypingIndicator(typingElem);
      appendMessage('ai', `⚠️ Error: ${err.message || 'Unable to connect to AI Assistant.'}`);
    } finally {
      sendBtn.disabled = false;
      chatInput.focus();
    }
  });

  // Chip buttons
  chipButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const query = btn.getAttribute('data-query');
      if (query) {
        chatInput.value = query;
        chatForm.dispatchEvent(new Event('submit'));
      }
    });
  });

  // Clear chat
  if (clearChatBtn) {
    clearChatBtn.addEventListener('click', () => {
      messageHistory = [];
      chatMessages.innerHTML = `
        <div class="message message-ai">
          Chat cleared. How else can I assist your travels around Pune today?
        </div>
      `;
    });
  }

  function appendMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message message-${role}`;
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function appendTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message message-ai';
    typingDiv.innerHTML = '<span style="font-style: italic; color: #64748b;">Thinking & searching transit network... ⏳</span>';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingDiv;
  }

  function removeTypingIndicator(elem) {
    if (elem && elem.parentNode) {
      elem.parentNode.removeChild(elem);
    }
  }
});
