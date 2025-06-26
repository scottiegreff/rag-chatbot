// Store the session ID
let sessionId = null;

// Near the top with other variables, add an AbortController
let currentStreamController = null;
let isStreaming = false;

// Store the uploaded file
let uploadedFile = null;

// Session management variables
let currentSession = null;
let sessions = [];
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
        console.log("🎨 renderUI called with state:", this.ui);
        
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
            console.log("🔧 Rendering sidebar...");
            console.log("📱 Window width:", window.innerWidth);
            console.log("🔧 sidebarOpen:", this.ui.sidebarOpen, "sidebarCollapsed:", this.ui.sidebarCollapsed);
            
            if (window.innerWidth <= 768) {
                // Mobile: use sidebarOpen state
                console.log("📱 Mobile mode");
                if (this.ui.sidebarOpen) {
                    console.log("📱 Adding 'expanded' class");
                    sidebar.classList.add('expanded');
                    sidebar.classList.remove('collapsed');
                } else {
                    console.log("📱 Removing 'expanded' class");
                    sidebar.classList.remove('expanded');
                    sidebar.classList.remove('collapsed');
                }
            } else {
                // Desktop: use sidebarCollapsed state
                console.log("🖥️ Desktop mode");
                if (this.ui.sidebarCollapsed) {
                    console.log("🖥️ Adding 'collapsed' class");
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
                    console.log("🖥️ Adding 'expanded' class");
                    sidebar.classList.add('expanded');
                    sidebar.classList.remove('collapsed');
                    if (sidebarToggle) {
                        sidebarToggle.classList.remove('collapsed');
                        sidebarToggle.style.display = 'none'; // Hide toggle button when expanded
                    }
                }
            }
            
            console.log("🔧 Final sidebar classes:", sidebar.className);
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
    setSidebarOpen(open) { this.updateUI({ sidebarOpen: open }); },
    setSidebarCollapsed(collapsed) { this.updateUI({ sidebarCollapsed: collapsed }); }
};

// Initialize state with current values - moved to after DOM is ready
function initializeAppState() {
    AppState.session.sessions = sessions;
    AppState.ui.streaming = isStreaming;
    AppState.ui.sessionEditing = isEditingSession;
}

// At the beginning of your chat.js file
console.log("Checking for markdown-it:", typeof window.markdownit);

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
let sidebarResizeHandle = null;
let searchBtn = null;

// Sidebar resize variables
let isResizing = false;
let startX = 0;
let startWidth = 0;

// Chat widget elements - will be initialized in setupEventListeners
let chatWidget = null;
let chatToggleBtn = null;
let chatInterface = null;

// Chat widget state
let isChatOpen = false;

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
        
        // Debug the markdown rendering
        console.log("Rendering markdown:", content.substring(0, 50) + "...");
        const renderedHTML = md.render(content);
        console.log("Rendered HTML:", renderedHTML.substring(0, 50) + "...");
        
        // Debug: Check if lists are being rendered
        if (content.includes('-') || content.includes('*') || /\d+\./.test(content)) {
            console.log("🔍 List content detected (addMessage):", content);
            console.log("🔍 Rendered HTML (addMessage):", renderedHTML);
            
            // Check if lists are actually in the rendered HTML
            if (renderedHTML.includes('<ul>') || renderedHTML.includes('<ol>') || renderedHTML.includes('<li>')) {
                console.log("✅ Lists properly rendered in HTML (addMessage)");
            } else {
                console.log("⚠️ Lists not found in rendered HTML (addMessage)");
            }
        }
        
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
async function sendMessageStreaming(message, customSystemInstruction = null) {
    // 1. Start timer when user prompt is entered
    const startTime = performance.now();
    console.log(`🚀 User prompt entered: "${message}"`);
    console.log(`⏱️  Starting timer at: ${new Date().toISOString()}`);

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
                console.log("First chunk:", chunk);
                
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
                        console.log("Parsing JSON:", jsonText);
                        const data = JSON.parse(jsonText);

                        if (data.session_id && !sessionId) {
                            sessionId = data.session_id;
                            window.sessionId = data.session_id;  // Also set the window variable
                            localStorage.setItem('chatSessionId', sessionId);
                        }
                        
                        // Only when we have actual content, remove the typing indicator
                        // and add the message div to the chat
                        if (data.delta && !messageStarted) {
                            messageStarted = true;
                            responseStartTime = performance.now();
                            console.log(`📝 Response started at: ${new Date().toISOString()}`);
                            removeTypingIndicator();
                            chatMessages.appendChild(messageDiv);
                        }

                        if (data.delta) {
                            accumulatedContent += data.delta;
                            
                            // Debug
                            console.log("Accumulated content:", accumulatedContent.length, "chars");
                            
                            try {
                                // Try to render markdown
                                const rendered = md.render(accumulatedContent);
                                contentDiv.innerHTML = rendered;
                                
                                // Debug: Check if lists are being rendered
                                if (accumulatedContent.includes('-') || accumulatedContent.includes('*') || /\d+\./.test(accumulatedContent)) {
                                    console.log("🔍 List content detected:", accumulatedContent);
                                    console.log("🔍 Rendered HTML:", rendered);
                                    
                                    // Check if lists are actually in the rendered HTML
                                    if (rendered.includes('<ul>') || rendered.includes('<ol>') || rendered.includes('<li>')) {
                                        console.log("✅ Lists properly rendered in HTML");
                                    } else {
                                        console.log("⚠️ Lists not found in rendered HTML");
                                    }
                                }
                            } catch (e) {
                                console.error("Error rendering markdown:", e);
                                // Fallback to plain text
                                contentDiv.textContent = accumulatedContent;
                            }
                            
                            applyHighlighting();
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                        }

                        if (data.error) {
                            contentDiv.innerHTML = `<p class="error">Error: ${data.error}</p>`;
                        }

                        // 2. Log when response is complete
                        if (data.done) {
                            const endTime = performance.now();
                            const totalTime = endTime - startTime;
                            const responseTime = responseStartTime ? endTime - responseStartTime : 0;
                            
                            console.log(`✅ Response completed at: ${new Date().toISOString()}`);
                            console.log(`⏱️  Total time from prompt to completion: ${totalTime.toFixed(2)}ms`);
                            console.log(`⏱️  Response generation time: ${responseTime.toFixed(2)}ms`);
                            console.log(`📊 Response length: ${accumulatedContent.length} characters`);
                            
                            // Refresh sessions list to update titles
                            await loadSessions();
                        }
                    } catch (e) {
                        console.log('Error parsing JSON:', e, 'Line:', line);
                        
                        // Only add message container when we start getting content
                        if (!messageStarted) {
                            messageStarted = true;
                            responseStartTime = performance.now();
                            console.log(`📝 Response started at: ${new Date().toISOString()}`);
                            removeTypingIndicator();
                            chatMessages.appendChild(messageDiv);
                        }
                        
                        const textChunk = line.slice(5).trim();
                        accumulatedContent += textChunk;
                        const rendered = md.render(accumulatedContent);
                        contentDiv.innerHTML = rendered;
                        
                        // Debug: Check if lists are being rendered
                        if (accumulatedContent.includes('-') || accumulatedContent.includes('*') || /\d+\./.test(accumulatedContent)) {
                            console.log("🔍 List content detected (fallback):", accumulatedContent);
                            console.log("🔍 Rendered HTML (fallback):", rendered);
                        }
                        
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }
                }
            }
        }
        
        // If we never started the message (no data received),
        // do it now before processing any remaining chunk
        if (!messageStarted) {
            removeTypingIndicator();
            chatMessages.appendChild(messageDiv);
        }
        
        // Process any remaining partial chunk
        if (partialChunk && partialChunk.startsWith('data:')) {
             try {
                const data = JSON.parse(partialChunk.slice(5).trim());
                if (data.delta) {
                     accumulatedContent += data.delta;
                     const rendered = md.render(accumulatedContent);
                     contentDiv.innerHTML = rendered;
                     
                     // Debug: Check if lists are being rendered
                     if (accumulatedContent.includes('-') || accumulatedContent.includes('*') || /\d+\./.test(accumulatedContent)) {
                         console.log("🔍 List content detected (final):", accumulatedContent);
                         console.log("🔍 Rendered HTML (final):", rendered);
                     }
                }
            } catch (e) {
                // Handle as plain text
                const textChunk = partialChunk.slice(5).trim();
                accumulatedContent += textChunk;
                const rendered = md.render(accumulatedContent);
                contentDiv.innerHTML = rendered;
                
                // Debug: Check if lists are being rendered
                if (accumulatedContent.includes('-') || accumulatedContent.includes('*') || /\d+\./.test(accumulatedContent)) {
                    console.log("🔍 List content detected (partial):", accumulatedContent);
                    console.log("🔍 Rendered HTML (partial):", rendered);
                }
            }
        }
        
        // Scroll to the bottom
                 chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {
        // Check if this was an abort error
        if (error.name === 'AbortError') {
            console.log('Stream was stopped by user');
            removeTypingIndicator();
            addMessage('Response stopped by user.', 'system');
        } else {
            console.error('Streaming error:', error);
            removeTypingIndicator();
            addMessage('Sorry, there was an error processing your message. Please try again.', 'system');
        }
    } finally {
        // Always change button back to send mode
        updateSubmitButton(false);
        currentStreamController = null;
    }
}

// Add this function to apply syntax highlighting to code blocks
function applyHighlighting() {
    if (window.hljs) {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightBlock(block);
        });
    }
}

function clearChat(keepSystemMessages = true) {
    if (keepSystemMessages) {
        // Clear all messages except the welcome message
        const messages = chatMessages.querySelectorAll('.message:not(.system)');
        messages.forEach(message => message.remove());
        
        // Add welcome message if it doesn't exist
        const welcomeMessage = chatMessages.querySelector('.message.system');
        if (!welcomeMessage) {
            addMessage('Welcome to FCIAS Chatbot! How can I help you today?', 'system');
        }
    } else {
        // Clear all messages including system messages
        chatMessages.innerHTML = '';
        // Add fresh welcome message
        addMessage('Welcome to FCIAS Chatbot! How can I help you today?', 'system');
    }
}

// Session Management Functions
async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        if (response.ok) {
            sessions = await response.json();
            renderSessionsList();
            
            // If no current session and we have sessions, load the first one
            if (!currentSession && sessions.length > 0) {
                await switchToSession(sessions[0].session_id);
            }
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

function renderSessionsList() {
    sessionsList.innerHTML = '';
    
    sessions.forEach(session => {
        const sessionItem = document.createElement('div');
        sessionItem.className = 'session-item';
        if (currentSession && currentSession.session_id === session.session_id) {
            sessionItem.classList.add('active');
        }
        
        sessionItem.innerHTML = `
            <span class="session-title" data-session-id="${session.session_id}">${session.title}</span>
            <input type="text" class="session-title-edit" data-session-id="${session.session_id}" value="${session.title}" style="display: none;">
            <div class="session-actions">
                <button class="session-action-btn edit-btn" data-session-id="${session.session_id}" title="Edit title">
                    <img src="/static/icons/edit.svg" alt="Edit" class="icon-svg" />
                </button>
                <button class="session-action-btn save-btn" data-session-id="${session.session_id}" title="Save title" style="display: none;">
                    <img src="/static/icons/save.svg" alt="Save" class="icon-svg" />
                </button>
                <button class="session-action-btn cancel-btn" data-session-id="${session.session_id}" title="Cancel edit" style="display: none;">
                    <img src="/static/icons/cancel.svg" alt="Cancel" class="icon-svg" />
                </button>
                <button class="session-action-btn" onclick="deleteSession('${session.session_id}')" title="Delete session">
                    <img src="/static/icons/delete.svg" alt="Delete" class="icon-svg" />
                </button>
            </div>
        `;
        
        // Add event listeners for inline editing
        const editBtn = sessionItem.querySelector('.edit-btn');
        const saveBtn = sessionItem.querySelector('.save-btn');
        const cancelBtn = sessionItem.querySelector('.cancel-btn');
        const titleSpan = sessionItem.querySelector('.session-title');
        const titleInput = sessionItem.querySelector('.session-title-edit');
        
        editBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            startInlineEdit(session.session_id);
        });
        
        saveBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Save button clicked for session:', session.session_id);
            saveInlineEdit(session.session_id);
        });
        
        cancelBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Cancel button clicked for session:', session.session_id);
            cancelInlineEdit(session.session_id);
        });
        
        titleInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveInlineEdit(session.session_id);
            } else if (e.key === 'Escape') {
                e.preventDefault();
                cancelInlineEdit(session.session_id);
            }
        });
        
        titleInput.addEventListener('blur', () => {
            // Small delay to allow for button clicks
            setTimeout(() => {
                // Only cancel if we're still in edit mode and not clicking on save or cancel buttons
                if (isEditingSession) {
                    const activeElement = document.activeElement;
                    if (!activeElement || 
                        (!activeElement.classList.contains('save-btn') && 
                         !activeElement.classList.contains('cancel-btn'))) {
                        cancelInlineEdit(session.session_id);
                    }
                }
            }, 150);
        });
        
        sessionItem.addEventListener('click', (e) => {
            if (!e.target.classList.contains('session-action-btn')) {
                switchToSession(session.session_id);
            }
        });
        
        sessionsList.appendChild(sessionItem);
    });
}

async function switchToSession(targetSessionId) {
    try {
        // Load chat history for this session
        const response = await fetch(`/api/history/${targetSessionId}`);
        if (response.ok) {
            const messages = await response.json();
            
            // Clear current chat
            clearChat(false);
            
            // Set current session and global sessionId - FIX: Set both local and window variables
            currentSession = sessions.find(s => s.session_id === targetSessionId);
            sessionId = targetSessionId;  // Set the local variable
            window.sessionId = targetSessionId;  // Set the window variable
            
            // Clear any old sessionId from localStorage to prevent conflicts
            localStorage.removeItem('sessionId');
            localStorage.removeItem('chatSessionId');
            
            // Load messages
            messages.forEach(msg => {
                addMessage(msg.content, msg.role, msg.role === 'assistant');
            });
            
            // Update UI
            renderSessionsList();
            
            console.log(`Switched to session: ${targetSessionId}`);
        }
    } catch (error) {
        console.error('Error switching session:', error);
    }
}

async function createNewSession() {
    console.log("🚀 createNewSession function called - debugging is working!");
    try {
        console.log("🆕 Creating new session...");
        console.log("📱 Current window width:", window.innerWidth);
        console.log("🔧 Current sidebar state:", AppState.ui.sidebarOpen, AppState.ui.sidebarCollapsed);
        
        const response = await fetch('/api/session/new', {
            method: 'POST'
        });
        
        if (response.ok) {
            const newSession = await response.json();
            sessions.unshift(newSession);
            
            // Clear the chat interface completely for new session
            clearChat(false);
            
            // Set current session and sessionId - FIX: Set both local and window variables
            currentSession = newSession;
            sessionId = newSession.session_id;  // Set the local variable
            window.sessionId = newSession.session_id;  // Set the window variable
            
            // Clear any old sessionId from localStorage to prevent conflicts
            localStorage.removeItem('sessionId');
            localStorage.removeItem('chatSessionId');
            
            // Close the sidebar when creating a new chat
            console.log("🔧 Attempting to close sidebar...");
            console.log("📱 Window width:", window.innerWidth);
            
            if (window.innerWidth <= 768) {
                console.log("📱 Mobile: Setting sidebarOpen to false");
                AppState.setSidebarOpen(false);
            } else {
                console.log("🖥️ Desktop: Setting sidebarCollapsed to true");
                AppState.setSidebarCollapsed(true);
            }
            
            console.log("🔧 After setting state:", AppState.ui.sidebarOpen, AppState.ui.sidebarCollapsed);
            
            // Update UI
            renderSessionsList();
            
            console.log(`✅ Created new session: ${newSession.session_id}`);
        }
    } catch (error) {
        console.error('Error creating new session:', error);
    }
}

async function deleteSession(targetSessionId) {
    try {
        const response = await fetch(`/api/session/${targetSessionId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Remove from sessions list
            sessions = sessions.filter(s => s.session_id !== targetSessionId);
            
            // If this was the current session, clear chat and localStorage
            if (currentSession && currentSession.session_id === targetSessionId) {
                currentSession = null;
                // Fix: Set both local and window sessionId variables to null
                sessionId = null;
                window.sessionId = null;
                // Clear localStorage to prevent session conflicts
                localStorage.removeItem('sessionId');
                localStorage.removeItem('chatSessionId');
                clearChat();
            }
            
            renderSessionsList();
        }
    } catch (error) {
        console.error('Error deleting session:', error);
    }
}

// Inline editing functions
function startInlineEdit(sessionId) {
    console.log('Starting inline edit for session:', sessionId);
    isEditingSession = true;
    
    const sessionItem = document.querySelector(`[data-session-id="${sessionId}"]`).closest('.session-item');
    const titleSpan = sessionItem.querySelector('.session-title');
    const titleInput = sessionItem.querySelector('.session-title-edit');
    const editBtn = sessionItem.querySelector('.edit-btn');
    const saveBtn = sessionItem.querySelector('.save-btn');
    const cancelBtn = sessionItem.querySelector('.cancel-btn');
    
    // Store original value for cancel
    titleInput.dataset.originalValue = titleInput.value;
    
    // Show input, hide span
    titleSpan.style.display = 'none';
    titleInput.style.display = 'block';
    
    // Show save/cancel buttons, hide edit button
    editBtn.style.display = 'none';
    saveBtn.style.display = 'block';
    cancelBtn.style.display = 'block';
    
    // Focus and select all text
    titleInput.focus();
    titleInput.select();
}

async function saveInlineEdit(sessionId) {
    console.log('Saving inline edit for session:', sessionId);
    
    const sessionItem = document.querySelector(`[data-session-id="${sessionId}"]`).closest('.session-item');
    if (!sessionItem) {
        console.error('Session item not found for sessionId:', sessionId);
        return;
    }
    
    const titleSpan = sessionItem.querySelector('.session-title');
    const titleInput = sessionItem.querySelector('.session-title-edit');
    const editBtn = sessionItem.querySelector('.edit-btn');
    const saveBtn = sessionItem.querySelector('.save-btn');
    const cancelBtn = sessionItem.querySelector('.cancel-btn');
    
    const newTitle = titleInput.value.trim();
    const originalTitle = titleSpan.textContent.trim();
    
    console.log('New title:', newTitle, 'Original title:', originalTitle);
    
    if (!newTitle) {
        console.log('Empty title, reverting');
        // If empty, revert to original
        cancelInlineEdit(sessionId);
        return;
    }
    
    if (newTitle === originalTitle) {
        console.log('No change, exiting edit mode');
        // No change, just exit edit mode
        cancelInlineEdit(sessionId);
        return;
    }
    
    // Disable buttons during save
    saveBtn.disabled = true;
    cancelBtn.disabled = true;
    saveBtn.textContent = 'Saving...';
    
    try {
        console.log('Sending API request to update title...');
        const response = await fetch(`/api/session/${sessionId}/title?title=${encodeURIComponent(newTitle)}`, {
            method: 'PUT'
        });
        
        console.log('API response status:', response.status);
        
        if (response.ok) {
            console.log('Title updated successfully');
            // Update the session object
            const session = sessions.find(s => s.session_id === sessionId);
            if (session) {
                session.title = newTitle;
                console.log('Updated session object title to:', newTitle);
            }
            
            // Update the display
            titleSpan.textContent = newTitle;
            titleInput.value = newTitle;
            
            // Exit edit mode
            exitEditMode(sessionItem);
            
            // Refresh the sessions list to ensure UI is updated
            renderSessionsList();
        } else {
            console.error('API request failed with status:', response.status);
            const errorText = await response.text();
            console.error('Error response:', errorText);
            // Revert on error
            cancelInlineEdit(sessionId);
        }
    } catch (error) {
        console.error('Error updating session title:', error);
        cancelInlineEdit(sessionId);
    } finally {
        // Re-enable buttons
        saveBtn.disabled = false;
        cancelBtn.disabled = false;
        saveBtn.innerHTML = '<img src="/static/icons/save.svg" alt="Save" class="icon-svg" />';
    }
}

function cancelInlineEdit(sessionId) {
    const sessionItem = document.querySelector(`[data-session-id="${sessionId}"]`).closest('.session-item');
    const titleSpan = sessionItem.querySelector('.session-title');
    const titleInput = sessionItem.querySelector('.session-title-edit');
    
    // Restore original value
    if (titleInput.dataset.originalValue) {
        titleInput.value = titleInput.dataset.originalValue;
    }
    
    exitEditMode(sessionItem);
}

function exitEditMode(sessionItem) {
    console.log('Exiting edit mode');
    isEditingSession = false;
    
    const titleSpan = sessionItem.querySelector('.session-title');
    const titleInput = sessionItem.querySelector('.session-title-edit');
    const editBtn = sessionItem.querySelector('.edit-btn');
    const saveBtn = sessionItem.querySelector('.save-btn');
    const cancelBtn = sessionItem.querySelector('.cancel-btn');
    
    // Hide input, show span
    titleSpan.style.display = 'block';
    titleInput.style.display = 'none';
    
    // Show edit button, hide save/cancel buttons
    editBtn.style.display = 'block';
    saveBtn.style.display = 'none';
    cancelBtn.style.display = 'none';
    
    // Clear original value
    delete titleInput.dataset.originalValue;
}

// Call it when the page loads
window.addEventListener('DOMContentLoaded', () => {
    loadMarkdownIt();
    setupEventListeners();
    initializeAppState(); // Initialize AppState after DOM is ready
});

function setupEventListeners() {
    // Initialize DOM elements first
    initializeDOMElements();
    
    // Initialize modal
    initializeModal();
    
    // Chat form submission
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }
    
    // Search button
    if (searchBtn) {
        searchBtn.addEventListener('click', handleSearchClick);
    }
    
    // Focus input on page load
    if (userInput) {
        userInput.focus();
    }
    
    // Chat toggle
    if (chatToggleBtn) {
        chatToggleBtn.addEventListener('click', toggleChatWidget);
        console.log('Chat toggle button event listener added');
    } else {
        console.error('Chat toggle button not found!');
    }
    
    // Sidebar toggle functionality
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            // Always open sidebar when toggle button is clicked
            if (window.innerWidth <= 768) {
                // Mobile: open sidebar
                AppState.setSidebarOpen(true);
            } else {
                // Desktop: expand sidebar
                AppState.setSidebarCollapsed(false);
            }
        });
    }
    
    // Sidebar close button functionality
    const sidebarCloseBtn = document.getElementById('sidebar-close-btn');
    if (sidebarCloseBtn) {
        sidebarCloseBtn.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                // Mobile: close sidebar
                AppState.setSidebarOpen(false);
            } else {
                // Desktop: collapse sidebar
                AppState.setSidebarCollapsed(true);
            }
        });
    }
    
    // New chat button
    if (newChatBtn) {
        newChatBtn.addEventListener('click', createNewSession);
    }
    
    // Sidebar resize functionality
    if (sidebarResizeHandle) {
        sidebarResizeHandle.addEventListener('mousedown', startResize);
    }
    
    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && sidebar && sidebarToggle) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                AppState.setSidebarOpen(false);
            }
        }
    });
    
    // Close chat when clicking outside (optional)
    document.addEventListener('click', (e) => {
        // Don't close chat if modal is open or if clicking on modal elements
        if (AppState.isModalOpen() || uploadModal?.contains(e.target)) {
            return;
        }
        
        if (AppState.isChatOpen() && chatWidget && !chatWidget.contains(e.target)) {
            toggleChatWidget();
        }
    });
    
    // Load initial data
    loadSessions();
}

// Initialize DOM elements
function initializeDOMElements() {
    console.log('Initializing DOM elements...');
    
    // Main chat elements
    chatForm = document.getElementById('chat-form');
    userInput = document.getElementById('user-input');
    chatMessages = document.getElementById('chat-messages');
    searchBtn = document.getElementById('search-btn');
    
    // Sidebar elements
    sidebar = document.getElementById('sidebar');
    sessionsList = document.getElementById('sessions-list');
    newChatBtn = document.getElementById('new-chat-btn');
    sidebarToggle = document.getElementById('sidebar-toggle');
    sidebarResizeHandle = document.getElementById('sidebar-resize-handle');
    
    // Chat widget elements
    chatWidget = document.getElementById('chat-widget');
    chatToggleBtn = document.getElementById('chat-toggle-btn');
    chatInterface = document.getElementById('chat-interface');
    
    // Log which elements were found
    const elements = {
        'chat-form': chatForm,
        'user-input': userInput,
        'chat-messages': chatMessages,
        'search-btn': searchBtn,
        'sidebar': sidebar,
        'sessions-list': sessionsList,
        'new-chat-btn': newChatBtn,
        'sidebar-toggle': sidebarToggle,
        'sidebar-resize-handle': sidebarResizeHandle,
        'chat-widget': chatWidget,
        'chat-toggle-btn': chatToggleBtn,
        'chat-interface': chatInterface
    };
    
    console.log('DOM element initialization results:');
    Object.entries(elements).forEach(([id, element]) => {
        if (element) {
            console.log(`✅ ${id}: Found`);
        } else {
            console.error(`❌ ${id}: Not found`);
        }
    });
}

// Handle chat form submission
function handleChatSubmit(event) {
    event.preventDefault();
    
    // If we're currently streaming, abort the stream
    if (AppState.isStreaming() && currentStreamController) {
        currentStreamController.abort();
        return;
    }
    
    const message = userInput.value.trim();
    if (!message) return;
    
    // Clear input
    userInput.value = '';
    
    // Send message
    sendMessageStreaming(message);
}

// Sidebar resize functions
function startResize(e) {
    console.log('startResize called', e);
    if (window.innerWidth <= 768) {
        console.log('Resize disabled on mobile');
        return; // Disable on mobile
    }
    
    isResizing = true;
    startX = e.clientX;
    startWidth = parseInt(getComputedStyle(sidebar).width, 10);
    
    console.log('Resize started:', { startX, startWidth });
    
    sidebarResizeHandle.classList.add('dragging');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    
    e.preventDefault();
}

function resize(e) {
    if (!isResizing) return;
    
    const width = startWidth + (e.clientX - startX);
    const minWidth = 200;
    const maxWidth = 500;
    
    console.log('Resizing:', { currentX: e.clientX, newWidth: width });
    
    if (width >= minWidth && width <= maxWidth) {
        sidebar.style.width = width + 'px';
        sidebar.style.transition = 'none'; // Disable transition during resize
    }
}

function stopResize() {
    if (!isResizing) return;
    
    console.log('Resize stopped');
    isResizing = false;
    sidebarResizeHandle.classList.remove('dragging');
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
    sidebar.style.transition = 'all 0.3s ease'; // Re-enable transition
    
    // If sidebar should be collapsed, clear the width to allow CSS to take effect
    if (AppState.ui.sidebarCollapsed && window.innerWidth > 768) {
        sidebar.style.width = '';
    }
}

// Chat widget toggle function
function toggleChatWidget() {
    AppState.setChatOpen(!AppState.isChatOpen());
}

// Initialize modal elements
function initializeModal() {
    uploadModal = document.getElementById('upload-modal');
    metadataUploadForm = document.getElementById('metadata-upload-form');
    modalFileInput = document.getElementById('modal-file-input');
    modalTitleInput = document.getElementById('modal-title');
    modalCategorySelect = document.getElementById('modal-category');
    modalLocationSelect = document.getElementById('modal-location');
    modalTagsInput = document.getElementById('modal-tags');
    modalQuestionsTextarea = document.getElementById('modal-questions');
    modalDescriptionTextarea = document.getElementById('modal-description');
    modalUploadedByInput = document.getElementById('modal-uploaded-by');
    modalUploadBtn = document.getElementById('modal-upload-btn');
    modalCancelBtn = document.getElementById('modal-cancel-btn');
    closeModalBtn = document.getElementById('close-upload-modal');

    // Set up event listeners
    modalFileInput.addEventListener('change', handleFileSelection);
    metadataUploadForm.addEventListener('submit', handleMetadataUpload);
    modalCancelBtn.addEventListener('click', closeModal);
    closeModalBtn.addEventListener('click', closeModal);
    
    // Close modal when clicking outside
    uploadModal.addEventListener('click', (e) => {
        if (e.target === uploadModal) {
            closeModal();
        }
    });

    // Populate dropdowns
    populateDropdowns();
}

// Populate category and location dropdowns
async function populateDropdowns() {
    try {
        // Get categories
        const categoriesResponse = await fetch('/api/categories');
        if (categoriesResponse.ok) {
            const categoriesData = await categoriesResponse.json();
            populateSelect(modalCategorySelect, categoriesData.categories, 'Select Category');
        }

        // Get locations
        const locationsResponse = await fetch('/api/locations');
        if (locationsResponse.ok) {
            const locationsData = await locationsResponse.json();
            populateSelect(modalLocationSelect, locationsData.locations, 'Select Location');
        }
    } catch (error) {
        console.error('Error populating dropdowns:', error);
        // Add default options if API fails - matching backend options
        populateSelect(modalCategorySelect, [
            'Human Resources',
            'Finance & Accounting', 
            'Information Technology',
            'Legal & Compliance',
            'Operations & Management'
        ], 'Select Category');
        populateSelect(modalLocationSelect, [
            'All Locations',
            'Headquarters',
            'Branch Office - North',
            'Branch Office - South', 
            'Remote/Home Office'
        ], 'Select Location');
    }
}

// Helper function to populate select elements
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

// Handle file selection in modal
function handleFileSelection(event) {
    const file = event.target.files[0];
    if (file) {
        // Auto-fill title with filename (without extension)
        const fileName = file.name.replace(/\.[^/.]+$/, "");
        modalTitleInput.value = fileName;
        
        // Auto-fill uploaded by if available
        if (!modalUploadedByInput.value) {
            // You could get this from user session or localStorage
            modalUploadedByInput.value = 'user@company.com';
        }
    }
}

// Show the upload modal
function showUploadModal() {
    AppState.setModalOpen(true, 'upload');
}

// Make it globally accessible
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
            console.log('Upload successful:', result);
            
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
        await sendMessageStreaming(userQuery, systemInstruction);
        
    } catch (error) {
        console.error('Error generating response from search:', error);
        addMessage('I found some information but had trouble generating a response. Here are the search results above.', 'system');
    }
} 