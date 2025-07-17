// AI Assistant functionality
let assistantMinimized = false;
let messageId = 1;

// Fix scroll behavior for AI assistant modal
document.addEventListener('DOMContentLoaded', function() {
    const aiMessages = document.getElementById('ai-messages');
    if (aiMessages) {
        // Prevent scroll propagation to background
        aiMessages.addEventListener('wheel', function(e) {
            // Check if scrolling would exceed bounds
            const isAtTop = aiMessages.scrollTop === 0;
            const isAtBottom = aiMessages.scrollTop + aiMessages.clientHeight >= aiMessages.scrollHeight;
            
            // Only prevent default if we're not at the bounds
            if ((e.deltaY < 0 && !isAtTop) || (e.deltaY > 0 && !isAtBottom)) {
                e.stopPropagation();
            }
        });
        
        // Prevent touch scroll propagation on mobile
        aiMessages.addEventListener('touchmove', function(e) {
            e.stopPropagation();
        });
    }
});

// Toggle assistant visibility
function toggleAssistant() {
    const assistant = document.getElementById('ai-assistant');
    const button = document.getElementById('ai-assistant-button');
    
    if (assistant.style.display === 'none' || assistant.style.display === '') {
        assistant.style.display = 'block';
        button.style.display = 'none';
        // Prevent body scroll when AI assistant is open
        document.body.classList.add('ai-assistant-open');
    } else {
        assistant.style.display = 'none';
        button.style.display = 'flex';
        // Restore body scroll when AI assistant is closed
        document.body.classList.remove('ai-assistant-open');
    }
}

// Handle quick action clicks
async function askAssistant(action) {
    const messagesContainer = document.getElementById('ai-messages');
    
    // Add user message
    const userMessage = createUserMessage(getActionText(action));
    messagesContainer.appendChild(userMessage);
    
    // Show typing indicator
    const typingIndicator = createTypingIndicator();
    messagesContainer.appendChild(typingIndicator);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    try {
        // Make API call to AI assistant
        const response = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ type: action })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        typingIndicator.remove();
        
        let aiResponse = '';
        switch(action) {
            case 'market-overview':
                aiResponse = await getMarketOverviewResponse();
                break;
            case 'top-picks':
                aiResponse = await getTopPicksResponse();
                break;
            case 'portfolio-advice':
                aiResponse = await getPortfolioAdviceResponse();
                break;
            case 'risk-analysis':
                aiResponse = await getRiskAnalysisResponse();
                break;
        }
        
        const aiMessage = createAIMessage(aiResponse);
        messagesContainer.appendChild(aiMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
    } catch (error) {
        console.error('Error communicating with AI assistant:', error);
        typingIndicator.remove();
        const errorMessage = createAIMessage('<p>Sorry, I encountered an error. Please try again.</p>');
        messagesContainer.appendChild(errorMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Create user message element
function createUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'ai-message user-message';
    messageDiv.innerHTML = `
        <div class="message-content user-content">
            <p>${text}</p>
        </div>
        <div class="message-avatar user-avatar">
            <i class="fas fa-user"></i>
        </div>
    `;
    return messageDiv;
}

// Create AI message element
function createAIMessage(html) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'ai-message';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            ${html}
        </div>
    `;
    return messageDiv;
}

// Create typing indicator
function createTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'ai-message typing-indicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    return typingDiv;
}

// Get action text
function getActionText(action) {
    const actionTexts = {
        'market-overview': 'Show me the current market overview',
        'top-picks': 'What are today\'s top stock picks?',
        'portfolio-advice': 'Can you give me portfolio advice?',
        'risk-analysis': 'Analyze my portfolio risk'
    };
    return actionTexts[action] || 'Help me with trading';
}

// Get market overview response
async function getMarketOverviewResponse() {
    if (!dashboardData.market_overview) {
        return '<p>Loading market data... Please try again in a moment.</p>';
    }
    
    const overview = dashboardData.market_overview;
    const topMovers = dashboardData.top_movers;
    
    let response = '<p>📊 <strong>Current Market Overview:</strong></p>';
    response += '<div class="ai-data-card">';
    response += `<p>The market is showing <strong>${overview.gainers}</strong> gainers and <strong>${overview.losers}</strong> losers out of <strong>${overview.total_stocks}</strong> tracked stocks.</p>`;
    
    if (overview.gainers > overview.losers) {
        response += '<p>🟢 <strong>Bullish sentiment</strong> - More stocks are gaining today, indicating positive market momentum.</p>';
    } else if (overview.losers > overview.gainers) {
        response += '<p>🔴 <strong>Bearish sentiment</strong> - More stocks are declining, suggesting market caution.</p>';
    } else {
        response += '<p>⚪ <strong>Neutral market</strong> - Equal gainers and losers, indicating market consolidation.</p>';
    }
    
    if (topMovers && topMovers.top_gainers && topMovers.top_gainers.length > 0) {
        const topGainer = topMovers.top_gainers[0];
        response += `<p>💹 Top performer: <strong>${topGainer.symbol}</strong> is up <span class="text-success">${topGainer.change_pct.toFixed(2)}%</span></p>`;
    }
    
    response += '</div>';
    response += '<p>Would you like me to analyze any specific sector or stock?</p>';
    
    return response;
}

// Get top picks response
async function getTopPicksResponse() {
    if (!stocksData || stocksData.length === 0) {
        // Load stocks data first
        await loadStocks();
    }
    
    let response = '<p>⭐ <strong>Today\'s AI-Powered Top Picks:</strong></p>';
    response += '<div class="ai-picks-list">';
    
    // Filter stocks with high confidence scores
    const topPicks = stocksData
        .filter(stock => stock.ai_insights && stock.ai_insights.confidence_score > 70)
        .sort((a, b) => b.ai_insights.confidence_score - a.ai_insights.confidence_score)
        .slice(0, 3);
    
    if (topPicks.length > 0) {
        topPicks.forEach((stock, index) => {
            const insights = stock.ai_insights;
            response += `
                <div class="ai-pick-item">
                    <h6>${index + 1}. ${stock.symbol} - ${stock.name}</h6>
                    <p>💰 Current Price: <strong>$${stock.current_price.toFixed(2)}</strong></p>
                    <p>🎯 AI Confidence: <span class="confidence-badge confidence-${getConfidenceClass(insights.confidence_score)}">${insights.confidence_score.toFixed(0)}%</span></p>
                    <p>📈 Recommendation: <strong>${insights.recommendation}</strong></p>
                    <p class="small">${insights.analysis}</p>
                    <button class="btn btn-sm btn-primary mt-2" onclick="showTradeModal('${stock.symbol}')">
                        <i class="fas fa-bolt"></i> Quick Trade
                    </button>
                </div>
            `;
        });
    } else {
        response += '<p>No high-confidence picks found at the moment. The market might be volatile today.</p>';
    }
    
    response += '</div>';
    return response;
}

// Get portfolio advice response
async function getPortfolioAdviceResponse() {
    if (!portfolioData || !portfolioData.summary) {
        return '<p>📊 You don\'t have any holdings yet. Would you like me to suggest some starter positions based on your risk tolerance?</p>';
    }
    
    const summary = portfolioData.summary;
    const holdings = portfolioData.portfolio_items;
    
    let response = '<p>💼 <strong>Portfolio Analysis & Advice:</strong></p>';
    response += '<div class="ai-data-card">';
    
    response += `<p>Your portfolio value: <strong>$${summary.total_value.toFixed(2)}</strong></p>`;
    
    if (summary.total_pnl >= 0) {
        response += `<p>🟢 You're up <span class="text-success">$${summary.total_pnl.toFixed(2)} (${summary.total_pnl_pct.toFixed(2)}%)</span> - Great job!</p>`;
    } else {
        response += `<p>🔴 Current loss: <span class="text-danger">$${Math.abs(summary.total_pnl).toFixed(2)} (${summary.total_pnl_pct.toFixed(2)}%)</span></p>`;
    }
    
    // Diversification advice
    const sectors = new Set(holdings.map(h => {
        const stock = stocksData.find(s => s.symbol === h.symbol);
        return stock ? stock.sector : 'Unknown';
    }));
    
    if (sectors.size < 3) {
        response += '<p>⚠️ <strong>Diversification Alert:</strong> Your portfolio is concentrated in only ' + sectors.size + ' sector(s). Consider diversifying across different industries to reduce risk.</p>';
    } else {
        response += '<p>✅ Good diversification across ' + sectors.size + ' sectors.</p>';
    }
    
    response += '</div>';
    response += '<p>Would you like specific recommendations to optimize your portfolio?</p>';
    
    return response;
}

// Get risk analysis response
async function getRiskAnalysisResponse() {
    let response = '<p>🛡️ <strong>Portfolio Risk Analysis:</strong></p>';
    response += '<div class="ai-risk-analysis">';
    
    if (!portfolioData || !portfolioData.portfolio_items || portfolioData.portfolio_items.length === 0) {
        response += '<p>No portfolio holdings to analyze. Start building your portfolio to get personalized risk insights!</p>';
    } else {
        const holdings = portfolioData.portfolio_items;
        
        // Calculate volatility indicators
        let highRiskCount = 0;
        let totalAllocation = 0;
        
        holdings.forEach(holding => {
            const allocation = (holding.current_value / portfolioData.summary.total_value) * 100;
            totalAllocation += allocation;
            
            // Check if any position is too large
            if (allocation > 25) {
                highRiskCount++;
            }
        });
        
        // Risk score calculation
        let riskScore = 'MODERATE';
        let riskColor = 'warning';
        
        if (highRiskCount > 0) {
            riskScore = 'HIGH';
            riskColor = 'danger';
        } else if (holdings.length > 5) {
            riskScore = 'LOW';
            riskColor = 'success';
        }
        
        response += `<p>Overall Risk Level: <span class="badge bg-${riskColor}">${riskScore}</span></p>`;
        
        if (highRiskCount > 0) {
            response += '<p>⚠️ <strong>Concentration Risk:</strong> Some positions are too large (>25% of portfolio). Consider rebalancing.</p>';
        }
        
        response += '<h6>Risk Mitigation Strategies:</h6>';
        response += '<ul>';
        response += '<li>Set stop-loss orders at 5-10% below purchase price</li>';
        response += '<li>Regularly review and rebalance your portfolio</li>';
        response += '<li>Keep 10-20% in cash for opportunities</li>';
        response += '</ul>';
    }
    
    response += '</div>';
    return response;
}

// Add custom styles for AI assistant
const aiStyles = document.createElement('style');
aiStyles.textContent = `
    .user-message {
        flex-direction: row-reverse;
    }
    
    .user-content {
        background: linear-gradient(135deg, rgba(163, 113, 247, 0.2) 0%, rgba(74, 158, 255, 0.15) 100%);
        border-color: rgba(163, 113, 247, 0.3);
    }
    
    .user-avatar {
        background: rgba(163, 113, 247, 0.3);
        color: var(--accent-purple);
    }
    
    .typing-indicator .message-content {
        padding: 1rem;
    }
    
    .typing-dots {
        display: flex;
        gap: 0.3rem;
    }
    
    .typing-dots span {
        width: 8px;
        height: 8px;
        background: var(--primary-color);
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.7;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
    
    .ai-data-card {
        background: rgba(74, 158, 255, 0.05);
        border: 1px solid rgba(74, 158, 255, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .ai-picks-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .ai-pick-item {
        background: rgba(74, 158, 255, 0.05);
        border: 1px solid rgba(74, 158, 255, 0.2);
        border-radius: 8px;
        padding: 1rem;
    }
    
    .ai-pick-item h6 {
        color: var(--text-bright);
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .ai-risk-analysis {
        background: rgba(255, 166, 87, 0.05);
        border: 1px solid rgba(255, 166, 87, 0.2);
        border-radius: 8px;
        padding: 1rem;
    }
    
    .ai-risk-analysis h6 {
        color: var(--accent-orange);
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
`;
document.head.appendChild(aiStyles);