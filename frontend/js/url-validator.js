// URL Validation Utility
class URLValidator {
    constructor() {
        this.validatedUrls = new Map(); // Cache validated URLs
        this.pendingValidations = new Set(); // Track ongoing validations
    }

    /**
     * Validate if a URL is accessible (not 404)
     * @param {string} url - The URL to validate
     * @param {number} timeout - Timeout in milliseconds (default: 5000)
     * @returns {Promise<{valid: boolean, status: number, error?: string}>}
     */
    async validateURL(url, timeout = 5000) {
        // Check cache first
        if (this.validatedUrls.has(url)) {
            return this.validatedUrls.get(url);
        }

        // Check if already validating this URL
        if (this.pendingValidations.has(url)) {
            // Wait for existing validation to complete
            return new Promise((resolve) => {
                const checkInterval = setInterval(() => {
                    if (this.validatedUrls.has(url)) {
                        clearInterval(checkInterval);
                        resolve(this.validatedUrls.get(url));
                    }
                }, 100);
            });
        }

        this.pendingValidations.add(url);

        try {
            // Basic URL format validation
            if (!this.isValidURLFormat(url)) {
                const result = { valid: false, status: 0, error: 'Invalid URL format' };
                this.validatedUrls.set(url, result);
                this.pendingValidations.delete(url);
                return result;
            }

            // Use a CORS proxy or backend endpoint to check URL
            const result = await this.checkURLStatus(url, timeout);
            this.validatedUrls.set(url, result);
            this.pendingValidations.delete(url);
            return result;

        } catch (error) {
            const result = { valid: false, status: 0, error: error.message };
            this.validatedUrls.set(url, result);
            this.pendingValidations.delete(url);
            return result;
        }
    }

    /**
     * Check if URL format is valid
     * @param {string} url 
     * @returns {boolean}
     */
    isValidURLFormat(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    /**
     * Check URL status using backend endpoint
     * @param {string} url 
     * @param {number} timeout 
     * @returns {Promise<{valid: boolean, status: number, error?: string}>}
     */
    async checkURLStatus(url, timeout) {
        try {
            const response = await fetch('/api/validate-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, timeout }),
                signal: AbortSignal.timeout(timeout + 1000) // Add 1s buffer
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return result;

        } catch (error) {
            if (error.name === 'AbortError') {
                return { valid: false, status: 0, error: 'Request timeout' };
            }
            throw error;
        }
    }

    /**
     * Extract URLs from text content
     * @param {string} text 
     * @returns {string[]}
     */
    extractURLs(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.match(urlRegex) || [];
    }

    /**
     * Validate all URLs in a message
     * @param {string} message 
     * @returns {Promise<Array<{url: string, valid: boolean, status: number, error?: string}>>}
     */
    async validateURLsInMessage(message) {
        const urls = this.extractURLs(message);
        const results = [];

        for (const url of urls) {
            const validation = await this.validateURL(url);
            results.push({ url, ...validation });
        }

        return results;
    }

    /**
     * Add visual indicators to URLs in DOM elements
     * @param {HTMLElement} element 
     * @param {Array<{url: string, valid: boolean}>} urlValidations 
     */
    addURLIndicators(element, urlValidations) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const html = element.innerHTML;

        let newHtml = html;
        urlValidations.forEach(({ url, valid }) => {
            const indicator = valid ?
                '<span class="url-valid" title="Valid URL">✅</span>' :
                '<span class="url-invalid" title="Invalid URL (404 or inaccessible)">❌</span>';

            newHtml = newHtml.replace(
                new RegExp(`(${url.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'g'),
                `$1 ${indicator}`
            );
        });

        element.innerHTML = newHtml;
    }

    /**
     * Clear validation cache
     */
    clearCache() {
        this.validatedUrls.clear();
        this.pendingValidations.clear();
    }
}

// Global instance
window.urlValidator = new URLValidator();

// Auto-validate URLs in chat messages
document.addEventListener('DOMContentLoaded', () => {
    // Observe chat messages for new content
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE &&
                        node.classList.contains('message') &&
                        node.classList.contains('assistant')) {

                        // Validate URLs in new assistant messages
                        const messageContent = node.querySelector('.message-content');
                        if (messageContent) {
                            const urls = window.urlValidator.extractURLs(messageContent.textContent);
                            if (urls.length > 0) {
                                window.urlValidator.validateURLsInMessage(messageContent.textContent)
                                    .then(validations => {
                                        window.urlValidator.addURLIndicators(messageContent, validations);
                                    });
                            }
                        }
                    }
                });
            });
        });

        observer.observe(chatMessages, { childList: true, subtree: true });
    }
}); 