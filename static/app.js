// Alpine.js app logic for AI Image Generator with Fixed Layout
function imageGenApp() {
    return {
        darkMode: localStorage.getItem('darkMode') === 'true',
        prompt: '',
        model: 'flux',
        selectedModel: 'flux',
        style: '',
        selectedStyle: '',
        resolution: '1024x1024',
        resolutions: [
            '512x512 (1:1)', '768x768 (1:1)', '1024x1024 (1:1)', '1536x1536 (1:1)',
            '512x768 (2:3)', '768x512 (3:2)', '768x1024 (3:4)', '1024x768 (4:3)',
            '1024x1536 (2:3)', '1536x1024 (3:2)', '1152x896 (9:7)', '896x1152 (7:9)',
            '2048x2048 (1:1)', '3072x3072 (1:1)', '4096x4096 (1:1)'
        ],
        quality: false,
        hdr: false,
        isGenerating: false,
        generatedImage: '',
        showModal: false,
        showSettings: false,
        chatMessages: [], // Always starts empty
        currentMessage: '',
        isTyping: false,
        showMobileControls: false,
        isEditing: false,
        editingIndex: null,
        style_categories: window.style_categories || [],
        modelFilters: {
            category: '',
            difficulty: '',
            speed: '',
            quality: ''
        },
        styleFilters: {
            category: '',
            difficulty: '',
            complexity: ''
        },
        models: window.models || {},
        model_categories: window.model_categories || [],
        showModelDetails: false,
        showStyleDetails: false,
        selectedModelDetails: null,
        selectedStyleDetails: null,
        notification: '',
        notificationTimeout: null,

        init() {
            // Initialize with welcome message
            this.addWelcomeMessage();
            
            // Load model and style categories
            this.model_categories = window.model_categories || [];
            this.style_categories = window.style_categories || [];
            
            // Set default selected model from first model in categories
            if (this.model_categories.length > 0 && this.model_categories[0].models && this.model_categories[0].models.length > 0) {
                this.selectedModel = this.model_categories[0].models[0].name;
                this.model = this.model_categories[0].models[0].name;
            }

            this.$watch('darkMode', val => {
                localStorage.setItem('darkMode', val);
                document.documentElement.classList.toggle('dark', val);
            });
            
            // Initialize dark mode if preference exists
            if (localStorage.getItem('darkMode') === null) {
                this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
            }
            document.documentElement.classList.toggle('dark', this.darkMode);
            
            // Auto-hide settings panel when clicking outside
            document.addEventListener('click', (e) => {
                if (this.showSettings && !e.target.closest('header')) {
                    this.showSettings = false;
                }
            });

            // Handle escape key to close modals and settings
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    if (this.showModal) {
                        this.showModal = false;
                    } else if (this.showSettings) {
                        this.showSettings = false;
                    }
                }
            });
        },

        setDefaultImage(event, type, key = null) {
            // Set a better placeholder image when the original fails to load
            const width = 200;
            const height = 150;
            
            if (type === 'style') {
                // For styles, use a gradient background with text
                event.target.src = `data:image/svg+xml;base64,${btoa(`
                    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
                                <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:1" />
                            </linearGradient>
                        </defs>
                        <rect width="100%" height="100%" fill="url(#grad)" />
                        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
                              font-family="sans-serif" font-size="12" fill="white">Style</text>
                    </svg>
                `)}`;
            } else if (type === 'model' && key) {
                // For models, create a placeholder with the model name
                event.target.src = `data:image/svg+xml;base64,${btoa(`
                    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
                                <stop offset="100%" style="stop-color:#6366f1;stop-opacity:1" />
                            </linearGradient>
                        </defs>
                        <rect width="100%" height="100%" fill="url(#grad)" />
                        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
                              font-family="sans-serif" font-size="10" fill="white" font-weight="bold">${key}</text>
                    </svg>
                `)}`;
            }
            
            // Ensure consistent styling
            event.target.classList.add('object-cover');
            event.target.classList.remove('object-contain');
        },

        addWelcomeMessage() {
            this.chatMessages = [{
                type: 'bot',
                content: 'Welcome to DreamlitAI! Describe your vision, and I\'ll create stunning artwork for you. Try something like "a majestic dragon soaring over a cyberpunk city at sunset".',
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
                this.selectedModel = msg.model || this.selectedModel;
                this.selectedStyle = msg.style || this.selectedStyle;
                this.resolution = msg.resolution || this.resolution;
                this.scrollToBottom();
                
                // Focus input and position cursor at end
                this.$nextTick(() => {
                    const input = document.querySelector('input[x-model="currentMessage"]');
                    if (input) {
                        input.focus();
                        // Position cursor at the end of the text
                        const length = input.value.length;
                        input.setSelectionRange(length, length);
                    }
                });
            }
        },

        startEditPromptFromUser(idx) {
            for (let i = idx + 1; i < this.chatMessages.length; i++) {
                if (this.chatMessages[i].type === 'image') {
                    this.currentMessage = this.chatMessages[idx].content;
                    this.isEditing = true;
                    this.editingIndex = i;
                    this.prompt = this.chatMessages[idx].content;
                    this.selectedModel = this.chatMessages[i].model || this.selectedModel;
                    this.selectedStyle = this.chatMessages[i].style || this.selectedStyle;
                    this.resolution = this.chatMessages[i].resolution || this.resolution;
                    this.scrollToBottom();
                    
                    // Focus input and position cursor at end
                    this.$nextTick(() => {
                        const input = document.querySelector('input[x-model="currentMessage"]');
                        if (input) {
                            input.focus();
                            // Position cursor at the end of the text
                            const length = input.value.length;
                            input.setSelectionRange(length, length);
                        }
                    });
                    break;
                }
                if (this.chatMessages[i].type === 'user') break;
            }
        },

        async sendMessage() {
            if (!this.currentMessage.trim() || this.isGenerating) return;

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
                content: this.currentMessage.trim(),
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
                    content: 'Please enter a prompt first! Try describing an image you\'d like me to create.',
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                });
                this.scrollToBottom();
                return;
            }

            this.isGenerating = true;

            const loadingId = 'loading-' + Date.now();
            if (!isEdit) {
                this.chatMessages.push({
                    type: 'loading',
                    id: loadingId,
                    prompt: this.prompt,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                });
                this.scrollToBottom();
            }

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        prompt: this.prompt,
                        model: this.selectedModel,
                        style: this.selectedStyle,
                        resolution: this.resolution,
                        quality: this.quality,
                        hdr: this.hdr
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                
                // Remove loading message
                this.chatMessages = this.chatMessages.filter(m => m.id !== loadingId);

                if (data.success) {
                    const imageMessage = {
                        type: 'image',
                        content: data.image_url,
                        prompt: this.prompt,
                        model: this.selectedModel,
                        style: this.selectedStyle,
                        resolution: this.resolution,
                        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    };

                    if (isEdit && this.editingIndex !== null) {
                        this.chatMessages[this.editingIndex] = imageMessage;
                        this.showNotification('Image updated successfully!');
                    } else {
                        this.chatMessages.push(imageMessage);
                        this.showNotification('Image generated successfully!');
                    }
                } else {
                    this.chatMessages.push({
                        type: 'error',
                        content: 'Error: ' + (data.error || 'Failed to generate image. Please try again.'),
                        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    });
                }
            } catch (error) {
                console.error('Generation error:', error);
                
                // Remove loading message
                this.chatMessages = this.chatMessages.filter(m => m.id !== loadingId);
                
                this.chatMessages.push({
                    type: 'error',
                    content: 'Network error occurred. Please check your connection and try again.',
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                });
            } finally {
                this.isGenerating = false;
                this.scrollToBottom();
            }
        },

        async downloadImage(url, filename) {
            try {
                this.showNotification('Downloading image...');
                
                const response = await fetch(url);
                if (!response.ok) throw new Error('Download failed');
                
                const blob = await response.blob();
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = filename + '.jpg';
                
                // Trigger download
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Clean up
                URL.revokeObjectURL(link.href);
                
                this.showNotification('Image downloaded successfully!');
            } catch (error) {
                console.error('Download failed:', error);
                this.showNotification('Download failed. Please try again.');
            }
        },

        showNotification(msg) {
            this.notification = msg;
            if (this.notificationTimeout) {
                clearTimeout(this.notificationTimeout);
            }
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
        },

        clearChat() {
            this.chatMessages = [];
            this.addWelcomeMessage();
            this.showNotification('Chat cleared!');
        },

        exportChat() {
            const chatData = {
                timestamp: new Date().toISOString(),
                messages: this.chatMessages.map(msg => ({
                    type: msg.type,
                    content: msg.content,
                    prompt: msg.prompt,
                    model: msg.model,
                    style: msg.style,
                    resolution: msg.resolution,
                    timestamp: msg.timestamp
                }))
            };

            const blob = new Blob([JSON.stringify(chatData, null, 2)], {
                type: 'application/json'
            });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `dreamlitai-chat-${Date.now()}.json`;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            URL.revokeObjectURL(link.href);
            this.showNotification('Chat exported successfully!');
        },

        // Utility methods for responsive design
        isMobile() {
            return window.innerWidth < 768;
        },

        isTablet() {
            return window.innerWidth >= 768 && window.innerWidth < 1024;
        },

        isDesktop() {
            return window.innerWidth >= 1024;
        },

        // Advanced model and style management
        showModelInfo(modelName) {
            // Find model details from categories
            for (const category of this.model_categories) {
                const model = category.models?.find(m => m.name === modelName);
                if (model) {
                    this.selectedModelDetails = {
                        ...model,
                        categoryName: category.category,
                        categoryDescription: category.description
                    };
                    this.showModelDetails = true;
                    break;
                }
            }
        },

        showStyleInfo(styleName) {
            // Find style details from categories
            for (const category of this.style_categories) {
                const style = category.styles?.find(s => s.name === styleName);
                if (style) {
                    this.selectedStyleDetails = {
                        ...style,
                        categoryName: category.category,
                        categoryDescription: category.description
                    };
                    this.showStyleDetails = true;
                    break;
                }
            }
        },

        closeModelDetails() {
            this.showModelDetails = false;
            this.selectedModelDetails = null;
        },

        closeStyleDetails() {
            this.showStyleDetails = false;
            this.selectedStyleDetails = null;
        },

        getModelsByCategory(categoryName) {
            const category = this.model_categories.find(cat => cat.category === categoryName);
            return category ? category.models : [];
        },

        getStylesByCategory(categoryName) {
            const category = this.style_categories.find(cat => cat.category === categoryName);
            return category ? category.styles : [];
        },

        getFilteredModels() {
            if (!this.modelFilters.category && !this.modelFilters.difficulty && 
                !this.modelFilters.speed && !this.modelFilters.quality) {
                return this.model_categories;
            }

            return this.model_categories.map(category => {
                if (this.modelFilters.category && category.category !== this.modelFilters.category) {
                    return { ...category, models: [] };
                }

                const filteredModels = category.models?.filter(model => {
                    if (this.modelFilters.difficulty && 
                        model.difficulty && 
                        model.difficulty !== this.modelFilters.difficulty) {
                        return false;
                    }
                    if (this.modelFilters.speed && model.rating) {
                        const speedThreshold = this.modelFilters.speed === 'fast' ? 8 : 6;
                        if (model.rating.speed < speedThreshold) return false;
                    }
                    if (this.modelFilters.quality && model.rating) {
                        const qualityThreshold = this.modelFilters.quality === 'high' ? 9 : 7;
                        if (model.rating.quality < qualityThreshold) return false;
                    }
                    return true;
                }) || [];

                return { ...category, models: filteredModels };
            }).filter(category => category.models.length > 0);
        },

        getFilteredStyles() {
            if (!this.styleFilters.category && !this.styleFilters.difficulty && 
                !this.styleFilters.complexity) {
                return this.style_categories;
            }

            return this.style_categories.map(category => {
                if (this.styleFilters.category && category.category !== this.styleFilters.category) {
                    return { ...category, styles: [] };
                }

                const filteredStyles = category.styles?.filter(style => {
                    if (this.styleFilters.difficulty && 
                        style.difficulty && 
                        style.difficulty !== this.styleFilters.difficulty) {
                        return false;
                    }
                    if (this.styleFilters.complexity && style.complexity) {
                        if (style.complexity.level !== this.styleFilters.complexity) return false;
                    }
                    return true;
                }) || [];

                return { ...category, styles: filteredStyles };
            }).filter(category => category.styles.length > 0);
        },

        clearModelFilters() {
            this.modelFilters = {
                category: '',
                difficulty: '',
                speed: '',
                quality: ''
            };
        },

        clearStyleFilters() {
            this.styleFilters = {
                category: '',
                difficulty: '',
                complexity: ''
            };
        },

        getRecommendedModelsForStyle(styleName) {
            for (const category of this.style_categories) {
                const style = category.styles?.find(s => s.name === styleName);
                if (style && style.compatibility && style.compatibility.best_models) {
                    return style.compatibility.best_models.slice(0, 3); // Top 3 recommendations
                }
            }
            return [];
        },

        getRecommendedStylesForModel(modelName) {
            const recommendations = [];
            for (const category of this.model_categories) {
                const model = category.models?.find(m => m.name === modelName);
                if (model && model.compatibility && model.compatibility.styles) {
                    recommendations.push(...model.compatibility.styles.slice(0, 3));
                    break;
                }
            }
            return recommendations;
        },

        getRatingStars(rating) {
            const stars = Math.round(rating);
            return '★'.repeat(stars) + '☆'.repeat(5 - stars);
        },

        getDifficultyColor(difficulty) {
            const colors = {
                'Beginner': 'text-green-500',
                'Intermediate': 'text-yellow-500',
                'Advanced': 'text-orange-500',
                'Expert': 'text-red-500'
            };
            return colors[difficulty] || 'text-gray-500';
        },

        getComplexityColor(level) {
            const colors = {
                'Low': 'text-green-500',
                'Medium': 'text-yellow-500',
                'Medium-High': 'text-orange-500',
                'High': 'text-red-500',
                'Very High': 'text-red-600'
            };
            return colors[level] || 'text-gray-500';
        }
    };
}

// Make function globally available
window.imageGenApp = imageGenApp;

// Add some utility functions for enhanced UX
document.addEventListener('DOMContentLoaded', function() {
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to send message
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const input = document.querySelector('input[x-model="currentMessage"]');
            if (input && input.value.trim()) {
                // Trigger Alpine.js send message
                input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
            }
        }
        
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const input = document.querySelector('input[x-model="currentMessage"]');
            if (input) input.focus();
        }
    });

    // Add smooth scrolling behavior
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add loading states for images
    document.addEventListener('load', function(e) {
        if (e.target.tagName === 'IMG') {
            e.target.classList.add('loaded');
        }
    }, true);
    
    // Optimize for mobile
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
    }
    
    // Handle viewport changes
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
    
    window.addEventListener('resize', () => {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    });
});

// Service worker registration for PWA capabilities
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}