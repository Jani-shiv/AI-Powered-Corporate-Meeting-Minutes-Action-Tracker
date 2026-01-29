/**
 * CorpMeet-AI v2.0 - Main JavaScript
 * Author: AI-Powered Corporate Meeting Minutes Tracker
 * License: MIT
 */

(function () {
  'use strict';

  // ========================================
  // DOM Ready Handler
  // ========================================
  document.addEventListener('DOMContentLoaded', function () {
    initUploadZone();
    initMeetingCards();
    initToasts();
  });

  // ========================================
  // File Upload Zone (Drag & Drop)
  // ========================================
  function initUploadZone() {
    const uploadZone = document.querySelector('.upload-zone');
    const fileInput = document.getElementById('transcript_file');

    if (!uploadZone || !fileInput) return;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      uploadZone.addEventListener(eventName, preventDefaults, false);
      document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    // Highlight on drag
    ['dragenter', 'dragover'].forEach(eventName => {
      uploadZone.addEventListener(eventName, () => {
        uploadZone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      uploadZone.addEventListener(eventName, () => {
        uploadZone.classList.remove('dragover');
      }, false);
    });

    // Handle drop
    uploadZone.addEventListener('drop', function (e) {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        fileInput.files = files;
        showFileName(files[0].name);
      }
    }, false);

    // Click to upload
    uploadZone.addEventListener('click', function () {
      fileInput.click();
    });

    // Show selected file name
    fileInput.addEventListener('change', function () {
      if (this.files.length > 0) {
        showFileName(this.files[0].name);
      }
    });

    function showFileName(name) {
      let fileNameDiv = document.getElementById('file-name-display');
      if (!fileNameDiv) {
        fileNameDiv = document.createElement('div');
        fileNameDiv.id = 'file-name-display';
        fileNameDiv.className = 'text-success text-center mt-3 fw-medium';
        uploadZone.parentNode.appendChild(fileNameDiv);
      }
      fileNameDiv.innerHTML = `<i class="bi bi-file-check me-2"></i>Selected: ${name}`;
    }
  }

  // ========================================
  // Meeting Cards Hover Effects
  // ========================================
  function initMeetingCards() {
    const cards = document.querySelectorAll('.meeting-card');
    
    cards.forEach(card => {
      card.addEventListener('mouseenter', function () {
        this.style.transform = 'translateY(-4px)';
        this.style.boxShadow = '0 12px 24px rgba(0,0,0,0.3)';
      });

      card.addEventListener('mouseleave', function () {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '';
      });
    });
  }

  // ========================================
  // Toast Notifications
  // ========================================
  function initToasts() {
    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert[role="alert"]');
    
    alerts.forEach(alert => {
      setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
      }, 5000);
    });
  }

  // ========================================
  // Chat Interface (Global Functions)
  // ========================================
  window.handleEnter = function (e) {
    if (e.key === 'Enter') {
      window.sendMessage();
    }
  };

  window.sendMessage = async function () {
    const input = document.getElementById('chatInput');
    const chatBox = document.getElementById('chatBox');
    const meetingIdEl = document.querySelector('[data-meeting-id]');
    
    if (!input || !chatBox) return;
    
    const question = input.value.trim();
    if (!question) return;

    const meetingId = meetingIdEl ? meetingIdEl.dataset.meetingId : window.meetingId;

    // User message
    appendMessage(chatBox, question, 'user');
    input.value = '';

    // Loading indicator
    const loadingId = 'loading-' + Date.now();
    const loadingEl = document.createElement('div');
    loadingEl.id = loadingId;
    loadingEl.className = 'd-flex mb-3';
    loadingEl.innerHTML = `
      <div class="chat-message chat-bot">
        <div class="spinner-border spinner-border-sm text-light" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    `;
    chatBox.appendChild(loadingEl);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meeting_id: meetingId, question: question })
      });

      const data = await response.json();
      
      // Remove loading
      document.getElementById(loadingId)?.remove();

      // Bot response
      appendMessage(chatBox, data.answer || "I couldn't process that request.", 'bot');

    } catch (error) {
      console.error('Chat error:', error);
      document.getElementById(loadingId)?.remove();
      appendMessage(chatBox, 'An error occurred. Please try again.', 'bot');
    }
  };

  function appendMessage(container, text, type) {
    const wrapper = document.createElement('div');
    wrapper.className = `d-flex ${type === 'user' ? 'justify-content-end' : ''} mb-3`;
    
    const msg = document.createElement('div');
    msg.className = `chat-message chat-${type}`;
    msg.innerHTML = `<p class="mb-0 small">${escapeHtml(text)}</p>`;
    
    wrapper.appendChild(msg);
    container.appendChild(wrapper);
    container.scrollTop = container.scrollHeight;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ========================================
  // Delete Confirmation Modal
  // ========================================
  window.confirmDelete = function (meetingId, meetingTitle) {
    const titleEl = document.getElementById('meetingTitle');
    const formEl = document.getElementById('deleteForm');
    
    if (titleEl) titleEl.textContent = meetingTitle;
    if (formEl) formEl.action = `/delete_meeting/${meetingId}`;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
  };

  // ========================================
  // Form Validation
  // ========================================
  window.validateTranscriptForm = function (formId) {
    const form = document.getElementById(formId);
    const textArea = document.getElementById('transcript_text');
    const fileInput = document.getElementById('transcript_file');
    const submitBtn = form?.querySelector('button[type="submit"]');

    if (!form) return true;

    const hasText = textArea && textArea.value.trim().length > 0;
    const hasFile = fileInput && fileInput.files.length > 0;

    if (!hasText && !hasFile) {
      alert('Please either paste text or upload a file.');
      return false;
    }

    // Show loading state
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    }

    return true;
  };

})();
