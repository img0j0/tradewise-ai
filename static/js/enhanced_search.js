/**
 * Enhanced Smart Search Engine
 * Advanced features: Voice search, search history, fuzzy matching, intelligent suggestions
 */

class SmartSearchEngine {
    constructor() {
        this.searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        this.recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
        this.searchCache = new Map();
        this.voiceRecognition = null;
        this.isListening = false;
        this.searchTimeout = null;
        this.selectedIndex = -1;
        
        this.init();
    }
    
    init() {
        this.setupVoiceSearch();
        this.setupSearchInput();
        this.setupSearchHistory();
        this.setupKeyboardShortcuts();
        this.loadRecentSearches();
        
        // Clean up any existing duplicate buttons on init
        this.cleanupDuplicateButtons();
    }
    
    cleanupDuplicateButtons() {
        // Remove any duplicate buttons with generic class names
        const duplicates = document.querySelectorAll('.search-controls .btn, .search-controls button:not(.voice-search-btn):not(.search-history-btn)');
        duplicates.forEach(btn => {
            if (!btn.classList.contains('voice-search-btn') && !btn.classList.contains('search-history-btn')) {
                btn.remove();
            }
        });
    }
    
    setupSearchInput() {
        const searchInput = document.getElementById('main-search-input');
        const searchBtn = document.querySelector('.chatgpt-search-btn');
        
        if (!searchInput) return;
        
        // Enhanced input events
        searchInput.addEventListener('input', (e) => this.handleSmartInput(e));
        searchInput.addEventListener('focus', () => this.showSearchSuggestions());
        searchInput.addEventListener('keydown', (e) => this.handleKeyNavigation(e));
        
        // Search button
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.executeSmartSearch());
        }
        
        // Add voice search button
        this.addVoiceSearchButton();
        this.addSearchHistoryButton();
    }
    
    setupSearchHistory() {
        // Setup search history functionality
        this.searchHistory = JSON.parse(localStorage.getItem('stockSearchHistory') || '[]');
    }
    
    setupKeyboardShortcuts() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl+K or Cmd+K to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('main-search-input');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            // Ctrl+Shift+V for voice search
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'V') {
                e.preventDefault();
                this.toggleVoiceSearch();
            }
        });
    }
    
    setupVoiceSearch() {
        // Check for speech recognition support
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.voiceRecognition = new SpeechRecognition();
            
            this.voiceRecognition.continuous = false;
            this.voiceRecognition.interimResults = false;
            this.voiceRecognition.lang = 'en-US';
            
            this.voiceRecognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.handleVoiceInput(transcript);
            };
            
            this.voiceRecognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopListening();
            };
            
            this.voiceRecognition.onend = () => {
                this.stopListening();
            };
        }
    }
    
    addVoiceSearchButton() {
        const searchControls = document.querySelector('.search-controls');
        if (!searchControls || !this.voiceRecognition) return;
        
        // Check if voice button already exists to prevent duplicates
        if (searchControls.querySelector('.voice-search-btn')) return;
        
        // Create buttons container if it doesn't exist
        let buttonsContainer = searchControls.querySelector('.search-controls-buttons');
        if (!buttonsContainer) {
            buttonsContainer = document.createElement('div');
            buttonsContainer.className = 'search-controls-buttons';
            searchControls.appendChild(buttonsContainer);
        }
        
        const voiceBtn = document.createElement('button');
        voiceBtn.className = 'voice-search-btn';
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceBtn.title = 'Voice Search - Speak your query';
        voiceBtn.addEventListener('click', () => this.toggleVoiceSearch());
        
        buttonsContainer.appendChild(voiceBtn);
    }
    
    addSearchHistoryButton() {
        const searchControls = document.querySelector('.search-controls');
        if (!searchControls) return;
        
        // Check if history button already exists to prevent duplicates
        if (searchControls.querySelector('.search-history-btn')) return;
        
        // Create buttons container if it doesn't exist
        let buttonsContainer = searchControls.querySelector('.search-controls-buttons');
        if (!buttonsContainer) {
            buttonsContainer = document.createElement('div');
            buttonsContainer.className = 'search-controls-buttons';
            searchControls.appendChild(buttonsContainer);
        }
        
        const historyBtn = document.createElement('button');
        historyBtn.className = 'search-history-btn';
        historyBtn.innerHTML = '<i class="fas fa-history"></i>';
        historyBtn.title = 'Search History - View recent searches';
        historyBtn.addEventListener('click', () => this.toggleSearchHistory());
        
        buttonsContainer.appendChild(historyBtn);
    }
    
    handleSmartInput(event) {
        const query = event.target.value.trim();
        
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Smart suggestions with debouncing
        this.searchTimeout = setTimeout(() => {
            if (query.length >= 2) {
                this.generateSmartSuggestions(query);
            } else if (query.length === 0) {
                this.showRecentSearches();
            } else {
                this.hideSuggestions();
            }
        }, 300);
    }
    
    async generateSmartSuggestions(query) {
        // Check cache first
        const cacheKey = query.toLowerCase();
        if (this.searchCache.has(cacheKey)) {
            this.displaySuggestions(this.searchCache.get(cacheKey));
            return;
        }
        
        try {
            // Show loading indicator
            this.showLoadingSuggestions();
            
            // Fuzzy matching with popular stocks
            const popularStocks = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX'];
            const fuzzyMatches = this.fuzzyMatch(query, popularStocks);
            
            // Get AI-powered suggestions
            const aiSuggestions = await this.getAISuggestions(query);
            
            // Combine all suggestions
            const suggestions = [
                ...fuzzyMatches.map(stock => ({
                    type: 'stock',
                    symbol: stock,
                    text: stock,
                    confidence: 0.9
                })),
                ...aiSuggestions,
                ...this.getHistoryMatches(query)
            ];
            
            // Cache results
            this.searchCache.set(cacheKey, suggestions);
            
            this.displaySuggestions(suggestions);
            
        } catch (error) {
            console.error('Error generating suggestions:', error);
            this.hideSuggestions();
        }
    }
    
    fuzzyMatch(query, items) {
        const threshold = 0.6;
        return items.filter(item => {
            const similarity = this.calculateSimilarity(query.toLowerCase(), item.toLowerCase());
            return similarity >= threshold;
        }).sort((a, b) => {
            const scoreA = this.calculateSimilarity(query.toLowerCase(), a.toLowerCase());
            const scoreB = this.calculateSimilarity(query.toLowerCase(), b.toLowerCase());
            return scoreB - scoreA;
        });
    }
    
    calculateSimilarity(str1, str2) {
        const longer = str1.length > str2.length ? str1 : str2;
        const shorter = str1.length > str2.length ? str2 : str1;
        
        if (longer.length === 0) return 1.0;
        
        const distance = this.levenshteinDistance(longer, shorter);
        return (longer.length - distance) / longer.length;
    }
    
    levenshteinDistance(str1, str2) {
        const matrix = [];
        
        for (let i = 0; i <= str2.length; i++) {
            matrix[i] = [i];
        }
        
        for (let j = 0; j <= str1.length; j++) {
            matrix[0][j] = j;
        }
        
        for (let i = 1; i <= str2.length; i++) {
            for (let j = 1; j <= str1.length; j++) {
                if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1,
                        matrix[i][j - 1] + 1,
                        matrix[i - 1][j] + 1
                    );
                }
            }
        }
        
        return matrix[str2.length][str1.length];
    }
    
    async getAISuggestions(query) {
        try {
            const response = await fetch('/api/ai-search-suggestions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.suggestions || [];
            }
        } catch (error) {
            console.error('Error getting AI suggestions:', error);
        }
        return [];
    }
    
    getHistoryMatches(query) {
        return this.searchHistory
            .filter(item => item.toLowerCase().includes(query.toLowerCase()))
            .slice(0, 3)
            .map(item => ({
                type: 'history',
                text: item,
                confidence: 0.7
            }));
    }
    
    displaySuggestions(suggestions) {
        const container = document.getElementById('search-suggestions');
        if (!container) return;
        
        container.innerHTML = '';
        this.selectedIndex = -1;
        
        if (suggestions.length === 0) {
            container.classList.add('hidden');
            return;
        }
        
        suggestions.slice(0, 8).forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.dataset.index = index;
            
            const icon = this.getSuggestionIcon(suggestion.type);
            const confidence = suggestion.confidence ? Math.round(suggestion.confidence * 100) : '';
            
            item.innerHTML = `
                <div class="suggestion-content">
                    <i class="${icon}"></i>
                    <span class="suggestion-text">${suggestion.text}</span>
                    ${suggestion.symbol ? `<span class="suggestion-symbol">${suggestion.symbol}</span>` : ''}
                </div>
                ${confidence ? `<div class="suggestion-confidence">${confidence}%</div>` : ''}
            `;
            
            item.addEventListener('click', () => this.selectSuggestion(suggestion));
            container.appendChild(item);
        });
        
        container.classList.remove('hidden');
    }
    
    getSuggestionIcon(type) {
        const icons = {
            stock: 'fas fa-chart-line',
            history: 'fas fa-history',
            ai: 'fas fa-robot',
            company: 'fas fa-building'
        };
        return icons[type] || 'fas fa-search';
    }
    
    showLoadingSuggestions() {
        const container = document.getElementById('search-suggestions');
        if (!container) return;
        
        container.innerHTML = `
            <div class="suggestion-loading">
                <div class="loading-spinner"></div>
                <span>Finding smart suggestions...</span>
            </div>
        `;
        container.classList.remove('hidden');
    }
    
    showRecentSearches() {
        if (this.recentSearches.length === 0) return;
        
        const suggestions = this.recentSearches.slice(0, 5).map(search => ({
            type: 'history',
            text: search,
            confidence: 0.8
        }));
        
        this.displaySuggestions(suggestions);
    }
    
    hideSuggestions() {
        const container = document.getElementById('search-suggestions');
        if (container) {
            container.classList.add('hidden');
        }
    }
    
    handleKeyNavigation(event) {
        const suggestions = document.querySelectorAll('.suggestion-item');
        if (suggestions.length === 0) return;
        
        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, suggestions.length - 1);
                this.updateSelection(suggestions);
                break;
                
            case 'ArrowUp':
                event.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection(suggestions);
                break;
                
            case 'Enter':
                event.preventDefault();
                if (this.selectedIndex >= 0) {
                    suggestions[this.selectedIndex].click();
                } else {
                    this.executeSmartSearch();
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }
    
    updateSelection(suggestions) {
        suggestions.forEach((item, index) => {
            item.classList.toggle('selected', index === this.selectedIndex);
        });
    }
    
    selectSuggestion(suggestion) {
        const searchInput = document.getElementById('main-search-input');
        if (searchInput) {
            searchInput.value = suggestion.text;
            this.addToSearchHistory(suggestion.text);
            this.hideSuggestions();
            this.executeSmartSearch();
        }
    }
    
    toggleVoiceSearch() {
        if (!this.voiceRecognition) {
            alert('Voice search not supported in this browser');
            return;
        }
        
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }
    
    startListening() {
        this.isListening = true;
        const voiceBtn = document.querySelector('.voice-search-btn');
        if (voiceBtn) {
            voiceBtn.classList.add('listening');
            voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
        }
        
        // Show voice indicator
        this.showVoiceIndicator();
        
        this.voiceRecognition.start();
    }
    
    stopListening() {
        this.isListening = false;
        const voiceBtn = document.querySelector('.voice-search-btn');
        if (voiceBtn) {
            voiceBtn.classList.remove('listening');
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        }
        
        this.hideVoiceIndicator();
        
        if (this.voiceRecognition) {
            this.voiceRecognition.stop();
        }
    }
    
    showVoiceIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'voice-indicator';
        indicator.innerHTML = `
            <div class="voice-animation">
                <div class="voice-wave"></div>
                <div class="voice-wave"></div>
                <div class="voice-wave"></div>
            </div>
            <span>Listening... Speak now</span>
        `;
        
        document.body.appendChild(indicator);
    }
    
    hideVoiceIndicator() {
        const indicator = document.querySelector('.voice-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    handleVoiceInput(transcript) {
        const searchInput = document.getElementById('main-search-input');
        if (searchInput) {
            searchInput.value = transcript;
            this.addToSearchHistory(transcript);
            
            // Show what was heard
            this.showVoiceResult(transcript);
            
            // Execute search after a short delay
            setTimeout(() => {
                this.executeSmartSearch();
            }, 1000);
        }
    }
    
    showVoiceResult(transcript) {
        const result = document.createElement('div');
        result.className = 'voice-result';
        result.innerHTML = `
            <i class="fas fa-microphone"></i>
            <span>You said: "${transcript}"</span>
        `;
        
        document.body.appendChild(result);
        
        setTimeout(() => {
            result.remove();
        }, 3000);
    }
    
    toggleSearchHistory() {
        const existing = document.querySelector('.search-history-panel');
        if (existing) {
            existing.remove();
            return;
        }
        
        this.showSearchHistoryPanel();
    }
    
    showSearchHistoryPanel() {
        const panel = document.createElement('div');
        panel.className = 'search-history-panel';
        
        const historyItems = this.searchHistory.slice(0, 10);
        
        panel.innerHTML = `
            <div class="history-header">
                <h4><i class="fas fa-history"></i> Search History</h4>
                <button class="clear-history-btn" onclick="smartSearch.clearSearchHistory()">
                    <i class="fas fa-trash"></i> Clear All
                </button>
            </div>
            <div class="history-items">
                ${historyItems.length > 0 ? 
                    historyItems.map(item => `
                        <div class="history-item" onclick="smartSearch.selectHistoryItem('${item}')">
                            <i class="fas fa-search"></i>
                            <span>${item}</span>
                            <button class="remove-item" onclick="event.stopPropagation(); smartSearch.removeHistoryItem('${item}')">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    `).join('') : 
                    '<div class="no-history">No search history yet</div>'
                }
            </div>
        `;
        
        document.body.appendChild(panel);
        
        // Close when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function closeHistory(e) {
                if (!panel.contains(e.target) && !e.target.closest('.search-history-btn')) {
                    panel.remove();
                    document.removeEventListener('click', closeHistory);
                }
            });
        }, 100);
    }
    
    selectHistoryItem(item) {
        const searchInput = document.getElementById('main-search-input');
        if (searchInput) {
            searchInput.value = item;
            this.executeSmartSearch();
        }
        
        const panel = document.querySelector('.search-history-panel');
        if (panel) panel.remove();
    }
    
    removeHistoryItem(item) {
        this.searchHistory = this.searchHistory.filter(h => h !== item);
        this.saveSearchHistory();
        
        // Refresh the panel
        const panel = document.querySelector('.search-history-panel');
        if (panel) {
            panel.remove();
            this.showSearchHistoryPanel();
        }
    }
    
    clearSearchHistory() {
        this.searchHistory = [];
        this.recentSearches = [];
        this.saveSearchHistory();
        
        const panel = document.querySelector('.search-history-panel');
        if (panel) panel.remove();
    }
    
    addToSearchHistory(query) {
        if (!query || query.length < 2) return;
        
        // Remove if already exists
        this.searchHistory = this.searchHistory.filter(item => item !== query);
        this.recentSearches = this.recentSearches.filter(item => item !== query);
        
        // Add to beginning
        this.searchHistory.unshift(query);
        this.recentSearches.unshift(query);
        
        // Limit size
        this.searchHistory = this.searchHistory.slice(0, 50);
        this.recentSearches = this.recentSearches.slice(0, 10);
        
        this.saveSearchHistory();
    }
    
    saveSearchHistory() {
        localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
        localStorage.setItem('recentSearches', JSON.stringify(this.recentSearches));
    }
    
    loadRecentSearches() {
        // Pre-populate suggestions if input is focused and empty
        const searchInput = document.getElementById('main-search-input');
        if (searchInput) {
            searchInput.addEventListener('focus', () => {
                if (!searchInput.value && this.recentSearches.length > 0) {
                    this.showRecentSearches();
                }
            });
        }
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('main-search-input');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
            
            // Ctrl/Cmd + Shift + V for voice search
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'V') {
                e.preventDefault();
                this.toggleVoiceSearch();
            }
        });
    }
    
    executeSmartSearch() {
        const searchInput = document.getElementById('main-search-input');
        if (!searchInput || !searchInput.value.trim()) return;
        
        const query = searchInput.value.trim();
        this.addToSearchHistory(query);
        this.hideSuggestions();
        
        // Call the existing search function
        if (typeof performIntelligentSearch === 'function') {
            performIntelligentSearch();
        } else if (typeof searchStockByName === 'function') {
            searchStockByName(query);
        }
    }
}

// Initialize smart search engine
let smartSearch;
document.addEventListener('DOMContentLoaded', () => {
    smartSearch = new SmartSearchEngine();
});