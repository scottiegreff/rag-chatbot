// Store the session ID
let sessionId = null;

// Near the top with other variables, add an AbortController
let currentStreamController = null;
let isStreaming = false;

// Session management variables
let sessions = [];
let currentSession = null; // Current active session
let isEditingSession = false; // Flag to track if we're currently editing a session title

// Centralized State Management
const AppState = {
    // UI States
    ui: {
        chatOpen: false,
        sidebarOpen: false,
        sidebarCollapsed: true,
        modalOpen: false,
        modalType: null, // 'upload', 'settings', 'help', etc.
        sessionEditing: false,
        streaming: false,
        uploading: false
    },

    // Session State
    session: {
        currentSessionId: null,
        editingSessionId: null,
        sessions: []
    },

    // Chat State
    chat: {
        messages: [],
        currentStreamController: null
    },

    // Modal State
    modal: {
        uploadForm: {
            file: null,
            title: '',
            category: '',
            location: '',
            tags: '',
            questions: '',
            description: '',
            uploadedBy: ''
        }
    },

    // Methods to update state
    updateUI(newState) {
        this.ui = { ...this.ui, ...newState };
        this.renderUI();
    },

    updateSession(newState) {
        this.session = { ...this.session, ...newState };
        this.renderSessions();
    },

    updateModal(newState) {
        this.modal = { ...this.modal, ...newState };
        this.renderModal();
    },

    // Render methods
    renderUI() {
        // Chat interface
        if (chatInterface) {
            if (this.ui.chatOpen) {
                chatInterface.classList.add('open');
            } else {
                chatInterface.classList.remove('open');
            }
        }

        // Chat toggle button
        if (chatToggleBtn) {
            if (this.ui.chatOpen) {
                chatToggleBtn.style.transform = 'scale(0.8)';
                chatToggleBtn.style.opacity = '0.7';
            } else {
                chatToggleBtn.style.transform = 'scale(1)';
                chatToggleBtn.style.opacity = '1';
            }
        }

        // Sidebar
        if (sidebar) {
            console.log('Rendering sidebar - sidebarOpen:', this.ui.sidebarOpen, 'sidebarCollapsed:', this.ui.sidebarCollapsed, 'window width:', window.innerWidth);
            if (window.innerWidth <= 768) {
                // Mobile: use sidebarOpen state
                if (this.ui.sidebarOpen) {
                    sidebar.classList.add('expanded');
                    sidebar.classList.remove('collapsed');
                    console.log('Mobile: sidebar expanded');
                } else {
                    sidebar.classList.remove('expanded');
                    sidebar.classList.add('collapsed');
                    console.log('Mobile: sidebar collapsed');
                }
            } else {
                // Desktop: use sidebarCollapsed state
                if (this.ui.sidebarCollapsed) {
                    sidebar.classList.remove('expanded');
                    sidebar.classList.add('collapsed');
                    sidebar.style.width = '';
                    if (sidebarToggle) {
                        sidebarToggle.classList.add('collapsed');
                        sidebarToggle.innerHTML = '<img src="/static/icons/chat.svg" alt="Expand Sidebar" class="sidebar-toggle-icon" />';
                        sidebarToggle.title = 'Expand Sidebar';
                        sidebarToggle.style.display = 'block'; // Show toggle button when collapsed
                    }
                } else {
                    sidebar.classList.add('expanded');
                    sidebar.classList.remove('collapsed');
                    if (sidebarToggle) {
                        sidebarToggle.classList.remove('collapsed');
                        sidebarToggle.style.display = 'none'; // Hide toggle button when expanded
                    }
                }
            }
        }

        // Modal
        if (uploadModal) {
            if (this.ui.modalOpen && this.ui.modalType === 'upload') {
                uploadModal.classList.remove('hidden');
                document.body.style.overflow = 'hidden';
            } else {
                uploadModal.classList.add('hidden');
                document.body.style.overflow = '';
            }
        }

        // Focus management
        if (this.ui.chatOpen && userInput) {
            setTimeout(() => {
                userInput.focus();
            }, 300);
        }
    },

    renderSessions() {
        // Update session list rendering
        if (sessionsList) {
            renderSessionsList();
        }
    },

    renderModal() {
        // Update modal form fields
        if (this.ui.modalType === 'upload') {
            if (modalTitleInput) modalTitleInput.value = this.modal.uploadForm.title;
            if (modalCategorySelect) modalCategorySelect.value = this.modal.uploadForm.category;
            if (modalLocationSelect) modalLocationSelect.value = this.modal.uploadForm.location;
            if (modalTagsInput) modalTagsInput.value = this.modal.uploadForm.tags;
            if (modalQuestionsTextarea) modalQuestionsTextarea.value = this.modal.uploadForm.questions;
            if (modalDescriptionTextarea) modalDescriptionTextarea.value = this.modal.uploadForm.description;
            if (modalUploadedByInput) modalUploadedByInput.value = this.modal.uploadForm.uploadedBy;
        }
    },

    // State getters
    isChatOpen() { return this.ui.chatOpen; },
    isModalOpen() { return this.ui.modalOpen; },
    getModalType() { return this.ui.modalType; },
    isStreaming() { return this.ui.streaming; },
    isUploading() { return this.ui.uploading; },
    isSessionEditing() { return this.ui.sessionEditing; },

    // State setters
    setChatOpen(open) { this.updateUI({ chatOpen: open }); },
    setModalOpen(open, type = null) { this.updateUI({ modalOpen: open, modalType: type }); },
    setStreaming(streaming) { this.updateUI({ streaming }); },
    setUploading(uploading) { this.updateUI({ uploading }); },
    setSessionEditing(editing) { this.updateUI({ sessionEditing: editing }); },
    setSidebarOpen(open) {
        console.log('setSidebarOpen called with:', open);
        this.updateUI({ sidebarOpen: open });
    },
    setSidebarCollapsed(collapsed) { this.updateUI({ sidebarCollapsed: collapsed }); }
};

// Initialize state with current values - moved to after DOM is ready
function initializeAppState() {
    AppState.session.sessions = sessions;
    AppState.ui.streaming = isStreaming;
    AppState.ui.sessionEditing = isEditingSession;
}

// At the top, declare md as let instead of const to allow reassignment
let md = { render: text => text.replace(/\n/g, '<br>') }; // Simple fallback renderer

// Function to dynamically load markdown-it if not already available
function loadMarkdownIt() {
    return new Promise((resolve, reject) => {
        if (typeof window.markdownit === 'function') {
            // Reassign md without redeclaring it
            md = window.markdownit({
                html: false,
                breaks: true,
                linkify: true
            });
            // Make all links open in a new tab
            md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
                // If the link does not already have target="_blank", add it
                const aIndex = tokens[idx].attrIndex('target');
                if (aIndex < 0) {
                    tokens[idx].attrPush(['target', '_blank']);
                } else {
                    tokens[idx].attrs[aIndex][1] = '_blank';
                }
                // Add rel="noopener noreferrer" for security
                const relIndex = tokens[idx].attrIndex('rel');
                if (relIndex < 0) {
                    tokens[idx].attrPush(['rel', 'noopener noreferrer']);
                } else {
                    tokens[idx].attrs[relIndex][1] = 'noopener noreferrer';
                }
                return self.renderToken(tokens, idx, options);
            };
            resolve();
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/markdown-it@12/dist/markdown-it.min.js';
        script.onload = () => {
            // Reassign md without redeclaring it
            md = window.markdownit({
                html: false,
                breaks: true,
                linkify: true
            });
            // Make all links open in a new tab
            md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
                // If the link does not already have target="_blank", add it
                const aIndex = tokens[idx].attrIndex('target');
                if (aIndex < 0) {
                    tokens[idx].attrPush(['target', '_blank']);
                } else {
                    tokens[idx].attrs[aIndex][1] = '_blank';
                }
                // Add rel="noopener noreferrer" for security
                const relIndex = tokens[idx].attrIndex('rel');
                if (relIndex < 0) {
                    tokens[idx].attrPush(['rel', 'noopener noreferrer']);
                } else {
                    tokens[idx].attrs[relIndex][1] = 'noopener noreferrer';
                }
                return self.renderToken(tokens, idx, options);
            };
            resolve();
        };
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// DOM elements - will be initialized in setupEventListeners
let chatForm = null;
let userInput = null;
let chatMessages = null;
let sidebar = null;
let sessionsList = null;
let newChatBtn = null;
let sidebarToggle = null;
let mobileSidebarToggle = null;
let sidebarResizeHandle = null;
let sidebarCloseBtn = null;
let searchBtn = null;

// Sidebar resize variables
let isResizing = false;
let startX = 0;
let startWidth = 0;

// Chat widget elements - will be initialized in setupEventListeners
let chatWidget = null;
let chatToggleBtn = null;
let chatInterface = null;

// Modal and metadata upload functionality
let uploadModal = null;
let metadataUploadForm = null;
let modalFileInput = null;
let modalTitleInput = null;
let modalCategorySelect = null;
let modalLocationSelect = null;
let modalTagsInput = null;
let modalQuestionsTextarea = null;
let modalDescriptionTextarea = null;
let modalUploadedByInput = null;
let modalUploadBtn = null;
let modalCancelBtn = null;
let closeModalBtn = null;

// Function to show typing indicator
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'message assistant typing-indicator';

    // Create dots that match the CSS classes
    indicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;

    indicator.id = 'typing-indicator';
    chatMessages.appendChild(indicator);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Function to add a message to the chat UI
function addMessage(content, role, isMarkdown = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    // Check if content contains HTML (like img tags for icons)
    const containsHTML = /<[^>]*>/g.test(content);

    if (isMarkdown || role === 'assistant') {  // Auto-enable markdown for assistant messages
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const renderedHTML = md.render(content);
        contentDiv.innerHTML = renderedHTML;
        messageDiv.appendChild(contentDiv);
    } else if (containsHTML) {
        // For messages with HTML content (like icons)
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = content;
        messageDiv.appendChild(contentDiv);
    } else {
        // For plain text messages
        messageDiv.textContent = content;
    }

    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to update the submit button state
function updateSubmitButton(streaming) {
    const button = document.querySelector('#chat-form button');
    if (!button) return;

    AppState.setStreaming(streaming);

    if (streaming) {
        // Switch to stop mode
        button.textContent = 'Stop';
        button.classList.add('stop-mode');
    } else {
        // Switch back to send mode
        button.textContent = 'Send';
        button.classList.remove('stop-mode');
    }
}

// Modify your sendMessageStreaming function
async function sendMessageStreaming(message, customSystemInstruction = null, userClickTime = null) {
    // Use provided userClickTime or create new one
    const startTime = userClickTime || performance.now();

    // Add user message to chat
    addMessage(message, 'user');

    // Show typing indicator
    showTypingIndicator();

    // Create a new AbortController for this stream
    currentStreamController = new AbortController();
    const signal = currentStreamController.signal;

    // Change button to stop mode
    updateSubmitButton(true);

    try {
        // Clear the input field after sending
        userInput.value = '';

        // Prepare payload
        const payload = {
            message: message
        };

        if (sessionId) {
            payload.session_id = sessionId;
        }

        // Add custom system instruction if provided
        if (customSystemInstruction) {
            payload.system_instruction = customSystemInstruction;
        }

        // Fetch streaming response with abort signal
        const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
            signal: signal  // Pass the abort signal
        });

        if (!response.ok) {
            throw new Error('Failed to get streaming response');
        }

        // Create a message div for the response that we'll build gradually
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';

        // Create content div for markdown rendering
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        messageDiv.appendChild(contentDiv);

        // Set up SSE reader first - don't remove typing indicator yet
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedContent = '';
        let partialChunk = '';
        let isFirstChunk = true;
        let messageStarted = false;
        let responseStartTime = null;

        while (true) {
            const { value, done } = await reader.read();

            if (done) break;

            // Decode and process chunks
            const chunk = decoder.decode(value, { stream: true });

            // Special handling for first chunk
            if (isFirstChunk) {
                isFirstChunk = false;
                const firstChunkTime = performance.now();
                const firstChunkDuration = firstChunkTime - startTime;

                if (!chunk.trimStart().startsWith('data:')) {
                    partialChunk = 'data: {"delta": "' + chunk + '"}';
                    continue;
                }
            }

            const lines = (partialChunk + chunk).split('\n');
            partialChunk = lines.pop() || '';

            for (const line of lines) {
                if (line.trim() && line.startsWith('data:')) {
                    try {
                        const jsonText = line.slice(5).trim();
                        const data = JSON.parse(jsonText);

                        if (data.delta) {
                            // Remove typing indicator on first content
                            if (!messageStarted) {
                                messageStarted = true;
                                removeTypingIndicator();
                                chatMessages.appendChild(messageDiv);
                                responseStartTime = performance.now();
                            }

                            // Accumulate content
                            accumulatedContent += data.delta;

                            // Render markdown and update content
                            const rendered = md.render(accumulatedContent);
                            contentDiv.innerHTML = rendered;

                            // Scroll to bottom
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                        }
                    } catch (e) {
                        // Handle non-JSON lines gracefully
                        if (line.trim() !== 'data: [DONE]') {
                            console.log('Error parsing JSON:', e, 'Line:', line);
                        }
                    }
                }
            }
        }

        // Final rendering after stream completes
        if (messageStarted) {
            const finalRendered = md.render(accumulatedContent);
            contentDiv.innerHTML = finalRendered;

            const totalTime = performance.now() - startTime;
            const responseTime = responseStartTime ? performance.now() - responseStartTime : 0;
        }

    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Stream was stopped by user');
        } else {
            console.error('Streaming error:', error);
            removeTypingIndicator();
            addMessage('Sorry, I encountered an error. Please try again.', 'system');
        }
    } finally {
        // Reset button state
        updateSubmitButton(false);
        currentStreamController = null;
    }
}

// Function to clear chat messages
function clearChat(keepSystemMessages = true) {
    if (keepSystemMessages) {
        // Keep only system messages
        const systemMessages = Array.from(chatMessages.children).filter(msg =>
            msg.classList.contains('system')
        );
        chatMessages.innerHTML = '';
        systemMessages.forEach(msg => chatMessages.appendChild(msg));
    } else {
        // Clear all messages
        chatMessages.innerHTML = '';
    }
}

// Load sessions from the backend
async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        if (response.ok) {
            sessions = await response.json();
            AppState.updateSession({ sessions: sessions });

            // Auto-select first session if none selected
            if (!currentSession && sessions.length > 0) {
                currentSession = sessions[0];
                await switchToSession(sessions[0].session_id);
            }
        }
    } catch (error) {
        console.error('Failed to load sessions:', error);
    }
}

// Render the sessions list
function renderSessionsList() {
    if (!sessionsList) return;

    sessionsList.innerHTML = '';

    sessions.forEach(session => {
        const sessionItem = document.createElement('div');
        sessionItem.className = 'session-item';
        sessionItem.dataset.sessionId = session.session_id;

        // Highlight current session
        if (currentSession && currentSession.session_id === session.session_id) {
            sessionItem.classList.add('active');
        }

        // Create session content
        const sessionContent = document.createElement('div');
        sessionContent.className = 'session-content';

        const titleSpan = document.createElement('span');
        titleSpan.className = 'session-title';
        titleSpan.textContent = session.title || 'Untitled Session';
        sessionContent.appendChild(titleSpan);

        const dateSpan = document.createElement('span');
        dateSpan.className = 'session-date';
        const date = new Date(session.created_at);
        dateSpan.textContent = date.toLocaleDateString();
        sessionContent.appendChild(dateSpan);

        sessionItem.appendChild(sessionContent);

        // Add edit and delete buttons
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'session-actions';

        const editBtn = document.createElement('button');
        editBtn.className = 'session-edit-btn';
        editBtn.innerHTML = '<img src="/static/icons/edit.svg" alt="Edit" />';
        editBtn.onclick = (e) => {
            e.stopPropagation();
            startInlineEdit(session.session_id);
        };

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'session-delete-btn';
        deleteBtn.innerHTML = '<img src="/static/icons/delete.svg" alt="Delete" />';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteSession(session.session_id);
        };

        actionsDiv.appendChild(editBtn);
        actionsDiv.appendChild(deleteBtn);
        sessionItem.appendChild(actionsDiv);

        // Add click handler to switch sessions
        sessionItem.onclick = () => switchToSession(session.session_id);

        sessionsList.appendChild(sessionItem);
    });
}

// Switch to a specific session
async function switchToSession(targetSessionId) {
    try {
        // Clear current chat
        clearChat();

        // Load session messages
        const response = await fetch(`/api/history/${targetSessionId}`);
        if (response.ok) {
            const messages = await response.json();

            // Add messages to chat
            messages.forEach(msg => {
                addMessage(msg.content, msg.role, msg.role === 'assistant');
            });

            // Update session ID
            sessionId = targetSessionId;
            currentSession = sessions.find(s => s.session_id === targetSessionId);

            // Update UI
            renderSessionsList();
        }
    } catch (error) {
        console.error('Failed to switch session:', error);
    }
}

// Create a new session
async function createNewSession() {
    try {
        const response = await fetch('/api/session/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: 'New Chat'
            })
        });

        if (response.ok) {
            const newSession = await response.json();
            sessions.unshift(newSession);
            currentSession = newSession;
            sessionId = newSession.session_id;

            // Clear chat and update UI
            clearChat();
            renderSessionsList();

            // Auto-expand sidebar on mobile
            if (window.innerWidth <= 768) {
                AppState.setSidebarOpen(false);
            }
        }
    } catch (error) {
        console.error('Failed to create session:', error);
    }
}

// Delete a session
async function deleteSession(targetSessionId) {
    try {
        const response = await fetch(`/api/session/${targetSessionId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            // Remove from sessions array
            sessions = sessions.filter(s => s.session_id !== targetSessionId);

            // Clear current session if it was deleted
            if (currentSession && currentSession.session_id === targetSessionId) {
                currentSession = null;
                sessionId = null;
                clearChat();
            }

            // Update UI
            renderSessionsList();
        }
    } catch (error) {
        console.error('Failed to delete session:', error);
    }
}

// Start inline editing for a session title
function startInlineEdit(sessionId) {
    const sessionItem = document.querySelector(`[data-session-id="${sessionId}"]`);
    if (!sessionItem) return;

    const titleSpan = sessionItem.querySelector('.session-title');
    const originalTitle = titleSpan.textContent;

    // Create input field
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'session-title-input';
    input.value = originalTitle;

    // Create save and cancel buttons
    const saveBtn = document.createElement('button');
    saveBtn.className = 'session-save-btn';
    saveBtn.innerHTML = '<img src="/static/icons/save.svg" alt="Save" />';
    saveBtn.onclick = (e) => {
        e.stopPropagation();
        saveInlineEdit(sessionId);
    };

    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'session-cancel-btn';
    cancelBtn.innerHTML = '<img src="/static/icons/cancel.svg" alt="Cancel" />';
    cancelBtn.onclick = (e) => {
        e.stopPropagation();
        cancelInlineEdit(sessionId);
    };

    // Replace title with input
    titleSpan.style.display = 'none';
    titleSpan.parentNode.insertBefore(input, titleSpan);

    // Add save and cancel buttons to the existing session-actions div
    const actionsDiv = sessionItem.querySelector('.session-actions');
    if (actionsDiv) {
        // Clear existing buttons and add new ones
        actionsDiv.innerHTML = '';
        actionsDiv.appendChild(saveBtn);
        actionsDiv.appendChild(cancelBtn);
        actionsDiv.style.opacity = '1'; // Make sure actions are visible
    }

    // Focus input and select text
    input.focus();
    input.select();

    // Add enter key handler
    input.onkeydown = (e) => {
        if (e.key === 'Enter') {
            saveInlineEdit(sessionId);
        } else if (e.key === 'Escape') {
            cancelInlineEdit(sessionId);
        }
    };

    // Prevent click events from bubbling up to session item
    input.onclick = (e) => {
        e.stopPropagation();
    };

    // Mark as editing
    AppState.setSessionEditing(true);
}

// Save inline edit
async function saveInlineEdit(sessionId) {
    const sessionItem = document.querySelector(`[data-session-id="${sessionId}"]`);
    if (!sessionItem) return;

    const input = sessionItem.querySelector('.session-title-input');
    const titleSpan = sessionItem.querySelector('.session-title');
    const saveBtn = sessionItem.querySelector('.session-save-btn');
    const cancelBtn = sessionItem.querySelector('.session-cancel-btn');

    const newTitle = input.value.trim();
    const originalTitle = titleSpan.textContent;

    // Validate title
    if (!newTitle) {
        alert('Session title cannot be empty');
        return;
    }

    // Check if title changed
    if (newTitle === originalTitle) {
        exitEditMode(sessionItem);
        return;
    }

    try {
        // Update session title via API
        const response = await fetch(`/api/session/${sessionId}/title?title=${encodeURIComponent(newTitle)}`, {
            method: 'PUT'
        });

        if (response.ok) {
            // Update local session object
            const session = sessions.find(s => s.session_id === sessionId);
            if (session) {
                session.title = newTitle;
            }

            // Update UI
            titleSpan.textContent = newTitle;
            exitEditMode(sessionItem);
            renderSessionsList();
        } else {
            alert('Failed to update session title');
        }
    } catch (error) {
        console.error('Failed to update session title:', error);
        alert('Failed to update session title');
    }
}

// Cancel inline edit
function cancelInlineEdit(sessionId) {
    const sessionItem = document.querySelector(`[data-session-id="${sessionId}"]`);
    if (sessionItem) {
        exitEditMode(sessionItem);
    }
}

// Exit edit mode
function exitEditMode(sessionItem) {
    const input = sessionItem.querySelector('.session-title-input');
    const titleSpan = sessionItem.querySelector('.session-title');
    const saveBtn = sessionItem.querySelector('.session-save-btn');
    const cancelBtn = sessionItem.querySelector('.session-cancel-btn');

    if (input) input.remove();
    if (saveBtn) saveBtn.remove();
    if (cancelBtn) cancelBtn.remove();

    if (titleSpan) {
        titleSpan.style.display = '';
    }

    AppState.setSessionEditing(false);
}

// Setup event listeners
function setupEventListeners() {
    // Initialize DOM elements first
    initializeDOMElements();

    // Load markdown-it
    loadMarkdownIt();

    // Chat form submission
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }

    // Chat toggle button
    if (chatToggleBtn) {
        chatToggleBtn.addEventListener('click', toggleChatWidget);
    }

    // Sidebar toggle (desktop)
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            AppState.setSidebarCollapsed(!AppState.ui.sidebarCollapsed);
        });
    }

    // Mobile sidebar toggle
    if (mobileSidebarToggle) {
        console.log('Mobile sidebar toggle button found and event listener attached');
        mobileSidebarToggle.addEventListener('click', () => {
            console.log('Mobile sidebar toggle clicked');
            console.log('Current sidebar state:', AppState.ui.sidebarOpen);
            // Toggle the sidebar state
            AppState.setSidebarOpen(!AppState.ui.sidebarOpen);
            console.log('After toggle - sidebarOpen:', AppState.ui.sidebarOpen);
        });
    } else {
        console.log('Mobile sidebar toggle button not found');
    }

    // Sidebar close button (works for both mobile and desktop)
    if (sidebarCloseBtn) {
        console.log('Sidebar close button found and event listener attached');
        sidebarCloseBtn.addEventListener('click', () => {
            console.log('Sidebar close button clicked');
            console.log('Current sidebar state:', AppState.ui.sidebarOpen);
            if (window.innerWidth <= 768) {
                // Mobile: use sidebarOpen state
                AppState.setSidebarOpen(false);
                console.log('Mobile: setting sidebarOpen to false');
            } else {
                // Desktop: use sidebarCollapsed state
                AppState.setSidebarCollapsed(true);
                console.log('Desktop: setting sidebarCollapsed to true');
            }
            console.log('After close action - sidebarOpen:', AppState.ui.sidebarOpen, 'sidebarCollapsed:', AppState.ui.sidebarCollapsed);
        });
    } else {
        console.log('Sidebar close button not found');
    }

    // New chat button
    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => {
            createNewSession();
            // Close sidebar after creating new session
            AppState.setSidebarOpen(false);
        });
    }

    // Search button
    if (searchBtn) {
        searchBtn.addEventListener('click', handleSearchClick);
    }

    // Sidebar resize
    if (sidebarResizeHandle) {
        sidebarResizeHandle.addEventListener('mousedown', startResize);
    }

    // Click outside to close chat (mobile)
    document.addEventListener('click', (e) => {
        if (AppState.isChatOpen() && chatWidget && !chatWidget.contains(e.target)) {
            AppState.setChatOpen(false);
        }
    });

    // Window resize handler
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            // Desktop: reset mobile sidebar state
            AppState.setSidebarOpen(false);
        }
    });

    // Initialize modal
    initializeModal();

    // Load sessions
    loadSessions();

    // Initialize app state
    initializeAppState();
}

// Initialize DOM elements
function initializeDOMElements() {
    const elements = {
        'chat-form': chatForm,
        'user-input': userInput,
        'chat-messages': chatMessages,
        'sidebar': sidebar,
        'sessions-list': sessionsList,
        'new-chat-btn': newChatBtn,
        'sidebar-toggle': sidebarToggle,
        'mobile-sidebar-toggle': null,
        'sidebar-resize-handle': sidebarResizeHandle,
        'sidebar-close-btn': sidebarCloseBtn,
        'search-btn': searchBtn,
        'chat-widget': chatWidget,
        'chat-toggle-btn': chatToggleBtn,
        'chat-interface': chatInterface,
        'upload-modal': uploadModal,
        'metadata-upload-form': metadataUploadForm,
        'modal-file-input': modalFileInput,
        'modal-title': modalTitleInput,
        'modal-category': modalCategorySelect,
        'modal-location': modalLocationSelect,
        'modal-tags': modalTagsInput,
        'modal-questions': modalQuestionsTextarea,
        'modal-description': modalDescriptionTextarea,
        'modal-uploaded-by': modalUploadedByInput,
        'modal-upload-btn': modalUploadBtn,
        'modal-cancel-btn': modalCancelBtn,
        'close-upload-modal': closeModalBtn
    };

    // Initialize each element
    Object.entries(elements).forEach(([id, variable]) => {
        if (variable === null) {
            elements[id] = document.getElementById(id);
        }
    });

    // Assign back to variables
    chatForm = elements['chat-form'];
    userInput = elements['user-input'];
    chatMessages = elements['chat-messages'];
    sidebar = elements['sidebar'];
    sessionsList = elements['sessions-list'];
    newChatBtn = elements['new-chat-btn'];
    sidebarToggle = elements['sidebar-toggle'];
    mobileSidebarToggle = elements['mobile-sidebar-toggle'];
    sidebarResizeHandle = elements['sidebar-resize-handle'];
    sidebarCloseBtn = elements['sidebar-close-btn'];
    searchBtn = elements['search-btn'];
    chatWidget = elements['chat-widget'];
    chatToggleBtn = elements['chat-toggle-btn'];
    chatInterface = elements['chat-interface'];
    uploadModal = elements['upload-modal'];
    metadataUploadForm = elements['metadata-upload-form'];
    modalFileInput = elements['modal-file-input'];
    modalTitleInput = elements['modal-title'];
    modalCategorySelect = elements['modal-category'];
    modalLocationSelect = elements['modal-location'];
    modalTagsInput = elements['modal-tags'];
    modalQuestionsTextarea = elements['modal-questions'];
    modalDescriptionTextarea = elements['modal-description'];
    modalUploadedByInput = elements['modal-uploaded-by'];
    modalUploadBtn = elements['modal-upload-btn'];
    modalCancelBtn = elements['modal-cancel-btn'];
    closeModalBtn = elements['close-upload-modal'];
}

// Handle chat form submission
function handleChatSubmit(event) {
    event.preventDefault();

    const message = userInput.value.trim();
    if (!message) return;

    // Send message with streaming
    sendMessageStreaming(message);
}

// Sidebar resize functionality
function startResize(e) {
    if (window.innerWidth <= 768) {
        return; // Disable resize on mobile
    }

    isResizing = true;
    startX = e.clientX;
    startWidth = sidebar.offsetWidth;

    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);

    sidebarResizeHandle.classList.add('dragging');
}

function resize(e) {
    if (!isResizing) return;

    const currentX = e.clientX;
    const width = Math.max(200, Math.min(400, startWidth + (currentX - startX)));

    sidebar.style.width = width + 'px';
}

function stopResize() {
    isResizing = false;
    document.removeEventListener('mousemove', resize);
    document.removeEventListener('mouseup', stopResize);

    sidebarResizeHandle.classList.remove('dragging');
}

// Toggle chat widget
function toggleChatWidget() {
    AppState.setChatOpen(!AppState.isChatOpen());
}

// Initialize modal functionality
function initializeModal() {
    if (metadataUploadForm) {
        metadataUploadForm.addEventListener('submit', handleMetadataUpload);
    }

    if (modalCancelBtn) {
        modalCancelBtn.addEventListener('click', closeModal);
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    if (modalFileInput) {
        modalFileInput.addEventListener('change', handleFileSelection);
    }

    // Populate dropdowns
    populateDropdowns();
}

// Populate dropdown options
async function populateDropdowns() {
    try {
        // Fetch categories
        const categoriesResponse = await fetch('/api/categories');
        if (categoriesResponse.ok) {
            const categoriesData = await categoriesResponse.json();
            if (modalCategorySelect) {
                populateSelect(modalCategorySelect, categoriesData.categories, 'Select Category');
            }
        }

        // Fetch locations
        const locationsResponse = await fetch('/api/locations');
        if (locationsResponse.ok) {
            const locationsData = await locationsResponse.json();
            if (modalLocationSelect) {
                populateSelect(modalLocationSelect, locationsData.locations, 'Select Location');
            }
        }
    } catch (error) {
        console.error('Failed to load dropdown options:', error);
    }
}

// Populate select element with options
function populateSelect(selectElement, options, placeholder) {
    selectElement.innerHTML = '';

    // Add placeholder option
    const placeholderOption = document.createElement('option');
    placeholderOption.value = '';
    placeholderOption.textContent = placeholder;
    placeholderOption.disabled = true;
    placeholderOption.selected = true;
    selectElement.appendChild(placeholderOption);

    // Add options
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.textContent = option;
        selectElement.appendChild(optionElement);
    });
}

// Handle file selection
function handleFileSelection(event) {
    const file = event.target.files[0];
    if (file) {
        // Auto-populate title from filename
        const title = file.name.replace(/\.[^/.]+$/, ""); // Remove extension
        if (modalTitleInput) {
            modalTitleInput.value = title;
        }
    }
}

// Show upload modal
function showUploadModal() {
    AppState.setModalOpen(true, 'upload');
}

// Make showUploadModal available globally
window.showUploadModal = showUploadModal;

// Close the upload modal
function closeModal() {
    AppState.setModalOpen(false);
    metadataUploadForm.reset();
}

// Handle metadata upload form submission
async function handleMetadataUpload(event) {
    event.preventDefault();

    const file = modalFileInput.files[0];
    if (!file) {
        alert('Please select a file to upload.');
        return;
    }

    // Validate required fields
    if (!modalTitleInput.value.trim()) {
        alert('Please enter a title for the document.');
        return;
    }
    if (!modalCategorySelect.value) {
        alert('Please select a category.');
        return;
    }
    if (!modalLocationSelect.value) {
        alert('Please select a location.');
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', modalTitleInput.value.trim());
    formData.append('category', modalCategorySelect.value);
    formData.append('location', modalLocationSelect.value);
    formData.append('tags', modalTagsInput.value.trim() || '[]');
    formData.append('description', modalDescriptionTextarea.value.trim() || '');
    formData.append('uploaded_by', modalUploadedByInput.value.trim() || 'anonymous');

    // Handle general questions (convert textarea lines to JSON array)
    const questionsText = modalQuestionsTextarea.value.trim();
    let questionsArray = [];
    if (questionsText) {
        questionsArray = questionsText.split('\n')
            .map(q => q.trim())
            .filter(q => q.length > 0);
    }
    formData.append('general_questions', JSON.stringify(questionsArray));

    // Show loading state
    AppState.setUploading(true);
    modalUploadBtn.disabled = true;
    modalUploadBtn.classList.add('loading');
    modalUploadBtn.textContent = 'Uploading...';

    try {
        // Upload file with metadata
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();

            // Show success message
            addMessage(`<img src="/static/icons/upload-success.svg" alt="Success" class="message-icon" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 8px;"> Successfully uploaded "${result.metadata.title}" with metadata. The document is now available for questions.`, 'system');

            // Close modal
            closeModal();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        addMessage(`<img src="/static/icons/upload-fail.svg" alt="Error" class="message-icon" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 8px;"> Upload failed: ${error.message}`, 'system');
    } finally {
        // Reset button state
        AppState.setUploading(false);
        modalUploadBtn.disabled = false;
        modalUploadBtn.classList.remove('loading');
        modalUploadBtn.textContent = 'Upload';
    }
}

// Search functionality
async function handleSearchClick() {
    const message = userInput.value.trim();
    if (!message) {
        alert('Please enter a search query first.');
        return;
    }

    // Clear input
    userInput.value = '';

    // Add user message
    addMessage(message, 'user');

    // Show typing indicator
    showTypingIndicator();

    try {
        // Perform hybrid search
        const searchResults = await performHybridSearch(message);

        // Remove typing indicator
        removeTypingIndicator();

        // Add search results as system message
        if (searchResults.summary) {
            addMessage(searchResults.summary, 'system', true);
        }

        // Generate AI response based on search results
        await generateResponseFromSearch(message, searchResults);

    } catch (error) {
        console.error('Search failed:', error);
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error while searching. Please try again.', 'system');
    }
}

async function performHybridSearch(query) {
    try {
        const response = await fetch('/api/search/hybrid', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                n_local_results: 3,
                n_web_results: 3,
                include_internet: true
            })
        });

        if (!response.ok) {
            throw new Error(`Search failed: ${response.statusText}`);
        }

        return await response.json();

    } catch (error) {
        console.error('Hybrid search error:', error);
        throw error;
    }
}

async function generateResponseFromSearch(userQuery, searchResults) {
    try {
        // Create context from search results
        let context = "Based on my search results:\n\n";

        // Add local results
        if (searchResults.local_results && searchResults.local_results.documents) {
            context += "**Local Documents:**\n";
            searchResults.local_results.documents[0].forEach((doc, index) => {
                context += `${index + 1}. ${doc.substring(0, 200)}...\n\n`;
            });
        }

        // Add web results
        if (searchResults.web_results && searchResults.web_results.length > 0) {
            context += "**Web Results:**\n";
            searchResults.web_results.forEach((result, index) => {
                context += `${index + 1}. ${result.title}\n`;
                context += `   ${result.snippet.substring(0, 150)}...\n`;
                context += `   Source: ${result.url}\n\n`;
            });
        }

        // Add search summary
        if (searchResults.summary) {
            context += `**Search Summary:**\n${searchResults.summary}\n\n`;
        }

        // Generate AI response using the search context
        const systemInstruction = `You are a helpful AI assistant. Use the following search results to answer the user's question. Provide a comprehensive response that combines information from both local documents and web search results. Always cite your sources when possible.

${context}

Please respond to the user's question: "${userQuery}"`;

        // Use the existing streaming response function with the search context
        // Note: This is called from search, so we don't have the original user click time
        await sendMessageStreaming(userQuery, systemInstruction);

    } catch (error) {
        console.error('Error generating response from search:', error);
        addMessage('I found some information but had trouble generating a response. Here are the search results above.', 'system');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', setupEventListeners); 