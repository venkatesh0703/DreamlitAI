// Alpine.js app logic for AI Image Generator
function imageGenApp() {
    return {
        darkMode: localStorage.getItem('darkMode') === 'true',
        prompt: '',
        model: Object.keys(window.models || {})[0] || 'flux',
        style: '',
        resolution: '1024x1024',
        resolutions: [
            { label: 'Profile (512x512)', value: '512x512' },
            { label: 'Mobile (512x1024)', value: '512x1024' },
            { label: 'Tablet (768x1024)', value: '768x1024' },
            { label: 'Laptop (1024x768)', value: '1024x768' },
            { label: 'Desktop (1536x1536)', value: '1536x1536' },
            { label: 'Square (1024x1024)', value: '1024x1024' }
        ],
        quality: false,
        isGenerating: false,
        generatedImage: '',
        showModal: false,
        chatMessages: [], // Always starts empty
        currentMessage: '',
        isTyping: false,
        showMobileControls: false,
        isEditing: false,
        editingIndex: null,
        style_categories: window.style_categories || [],
        models: window.models || {},
        notification: '',
        notificationTimeout: null,

        init() {
            // Initialize with welcome message
            this.addWelcomeMessage();

            this.$watch('darkMode', val => {
                localStorage.setItem('darkMode', val);
                document.documentElement.classList.toggle('dark', val);
            });
            
            // Initialize dark mode if preference exists
            if (localStorage.getItem('darkMode') === null) {
                this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
            }
            document.documentElement.classList.toggle('dark', this.darkMode);
        },

        addWelcomeMessage() {
            this.chatMessages = [{
                type: 'bot',
                content: '👋 Welcome to DreamlitAI – describe your vision, and I’ll turn it into stunning art.',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }];
        },

        startEditPrompt(idx) {
            const msg = this.chatMessages[idx];
            if (msg && msg.type === 'image') {
                this.currentMessage = msg.prompt;
                this.isEditing = true;
                this.editingIndex = idx;
                this.prompt = msg.prompt;
                this.model = msg.model;
                this.style = msg.style;
                this.resolution = msg.resolution;
                this.scrollToBottom();
            }
        },

        startEditPromptFromUser(idx) {
            for (let i = idx + 1; i < this.chatMessages.length; i++) {
                if (this.chatMessages[i].type === 'image') {
                    this.currentMessage = this.chatMessages[idx].content;
                    this.isEditing = true;
                    this.editingIndex = i;
                    this.prompt = this.chatMessages[idx].content;
                    this.model = this.chatMessages[i].model;
                    this.style = this.chatMessages[i].style;
                    this.resolution = this.chatMessages[i].resolution;
                    this.scrollToBottom();
                    break;
                }
                if (this.chatMessages[i].type === 'user') break;
            }
        },

        async sendMessage() {
            if (!this.currentMessage.trim()) return;

            if (this.isEditing && this.editingIndex !== null) {
                this.prompt = this.currentMessage.trim();
                await this.generateImage(true, true);
                this.isEditing = false;
                this.editingIndex = null;
                this.currentMessage = '';
                return;
            }

            const userMessage = {
                type: 'user',
                content: this.currentMessage,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };

            this.chatMessages.push(userMessage);
            this.scrollToBottom();

            const messageContent = this.currentMessage;
            this.currentMessage = '';
            this.isTyping = true;

            this.prompt = messageContent.trim();
            await this.generateImage(true);
            this.isTyping = false;
        },

        async generateImage(fromChat = false, isEdit = false) {
            if (!this.prompt.trim()) {
                this.chatMessages.push({
                    type: 'bot',
                    content: '⚠️ Please enter a prompt first!',
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                });
                return;
            }

            this.isGenerating = true;

            const loadingId = 'loading-' + Date.now();
            this.chatMessages.push({
                type: 'loading',
                id: loadingId,
                prompt: this.prompt,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            });
            this.scrollToBottom();

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: this.prompt,
                        model: this.model,
                        style: this.style,
                        resolution: this.resolution,
                        quality: this.quality
                    })
                });

                const data = await response.json();
                this.chatMessages = this.chatMessages.filter(m => m.id !== loadingId);

                if (data.success) {
                    if (isEdit && this.editingIndex !== null) {
                        this.chatMessages[this.editingIndex] = {
                            type: 'image',
                            content: data.image_url,
                            prompt: this.prompt,
                            model: this.model,
                            style: this.style,
                            resolution: this.resolution,
                            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                        };
                        this.showNotification('✅ Image updated!');
                    } else {
                        this.chatMessages.push({
                            type: 'image',
                            content: data.image_url,
                            prompt: this.prompt,
                            model: this.model,
                            style: this.style,
                            resolution: this.resolution,
                            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                        });
                        this.showNotification('🎉 Image generated!');
                    }
                } else {
                    this.chatMessages.push({
                        type: 'error',
                        content: '❌ Error: ' + (data.error || 'Unknown error'),
                        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    });
                }
            } catch (error) {
                this.chatMessages = this.chatMessages.filter(m => m.id !== loadingId);
                this.chatMessages.push({
                    type: 'error',
                    content: '❌ Network error - try again',
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                });
            } finally {
                this.isGenerating = false;
                this.scrollToBottom();
            }
        },

        downloadImage(url, filename) {
            fetch(url)
                .then(response => response.blob())
                .then(blob => {
                    const link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = filename;
                    link.click();
                    URL.revokeObjectURL(link.href);
                })
                .catch(err => {
                    console.error('Download failed:', err);
                    this.showNotification('❌ Download failed');
                });
        },

        showNotification(msg) {
            this.notification = msg;
            if (this.notificationTimeout) clearTimeout(this.notificationTimeout);
            this.notificationTimeout = setTimeout(() => {
                this.notification = '';
            }, 3000);
        },

        scrollToBottom() {
            this.$nextTick(() => {
                const chatContainer = this.$refs.chatContainer;
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            });
        }
    };
}

window.imageGenApp = imageGenApp;