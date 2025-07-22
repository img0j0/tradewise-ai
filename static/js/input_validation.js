// Professional Input Validation for TradeWise AI
// Ensures first-class user experience with real-time feedback

class InputValidator {
    constructor() {
        this.patterns = {
            stock_symbol: /^[A-Z]{1,5}$/,
            email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            price: /^\d+(\.\d{1,2})?$/,
            percentage: /^-?\d+(\.\d{1,2})?$/
        };
    }

    // Real-time stock symbol validation
    validateStockSymbol(input) {
        const symbol = input.value.toUpperCase().trim();
        const isValid = this.patterns.stock_symbol.test(symbol) && symbol.length <= 5;
        
        this.updateFieldState(input, isValid, {
            valid: "Valid stock symbol",
            invalid: "Enter 1-5 letter stock symbol (e.g., AAPL)"
        });
        
        return isValid;
    }

    // Email validation for account forms
    validateEmail(input) {
        const email = input.value.trim();
        const isValid = this.patterns.email.test(email);
        
        this.updateFieldState(input, isValid, {
            valid: "Email format is correct",
            invalid: "Please enter a valid email address"
        });
        
        return isValid;
    }

    // Price validation for alerts and analysis
    validatePrice(input) {
        const price = input.value.trim();
        const isValid = this.patterns.price.test(price) && parseFloat(price) > 0;
        
        this.updateFieldState(input, isValid, {
            valid: "Valid price format",
            invalid: "Enter a valid price (e.g., 150.50)"
        });
        
        return isValid;
    }

    // Update visual feedback for input fields
    updateFieldState(input, isValid, messages) {
        const container = input.closest('.form-group') || input.parentElement;
        let feedback = container.querySelector('.validation-feedback');
        
        // Create feedback element if it doesn't exist
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'validation-feedback';
            container.appendChild(feedback);
        }
        
        // Remove existing classes
        input.classList.remove('is-valid', 'is-invalid');
        feedback.classList.remove('valid-feedback', 'invalid-feedback');
        
        if (isValid) {
            input.classList.add('is-valid');
            feedback.classList.add('valid-feedback');
            feedback.textContent = messages.valid;
            feedback.style.color = '#10b981';
        } else {
            input.classList.add('is-invalid');
            feedback.classList.add('invalid-feedback');
            feedback.textContent = messages.invalid;
            feedback.style.color = '#ef4444';
        }
        
        feedback.style.fontSize = '0.875rem';
        feedback.style.marginTop = '0.25rem';
        feedback.style.fontWeight = '500';
    }

    // Sanitize input to prevent XSS
    sanitizeInput(value) {
        if (typeof value !== 'string') return value;
        return value
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;')
            .replace(/\//g, '&#x2F;');
    }

    // Professional form submission with validation
    validateForm(formElement) {
        const inputs = formElement.querySelectorAll('input[data-validate]');
        let isValid = true;
        
        inputs.forEach(input => {
            const validateType = input.getAttribute('data-validate');
            let inputValid = true;
            
            switch (validateType) {
                case 'stock-symbol':
                    inputValid = this.validateStockSymbol(input);
                    break;
                case 'email':
                    inputValid = this.validateEmail(input);
                    break;
                case 'price':
                    inputValid = this.validatePrice(input);
                    break;
            }
            
            if (!inputValid) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    // Add loading state to buttons
    setButtonLoading(button, loading = true) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = `
                <div class="analysis-loading" style="display: inline-block; margin-right: 8px;"></div>
                Processing...
            `;
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
        }
    }

    // Professional error handling with user-friendly messages
    handleError(error, context = 'operation') {
        console.error(`Error in ${context}:`, error);
        
        const userMessage = this.getFriendlyErrorMessage(error);
        this.showNotification(userMessage, 'error');
        
        return userMessage;
    }

    // Convert technical errors to user-friendly messages
    getFriendlyErrorMessage(error) {
        const message = error.message || error.toString();
        
        if (message.includes('rate limit')) {
            return 'Too many requests. Please wait a moment before trying again.';
        }
        if (message.includes('network') || message.includes('fetch')) {
            return 'Connection issue. Please check your internet and try again.';
        }
        if (message.includes('unauthorized')) {
            return 'Session expired. Please refresh the page and log in again.';
        }
        if (message.includes('not found')) {
            return 'Stock symbol not found. Please check the symbol and try again.';
        }
        
        return 'Something went wrong. Our team has been notified and we\'re working on a fix.';
    }

    // Professional notification system
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            animation: slideInRight 0.3s ease-out;
            color: white;
            font-weight: 500;
        `;
        
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        
        notification.style.background = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }
}

// Initialize global validator
const validator = new InputValidator();

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: inherit;
        cursor: pointer;
        padding: 0.25rem;
        margin-left: auto;
        opacity: 0.8;
        transition: opacity 0.2s;
    }
    
    .notification-close:hover {
        opacity: 1;
    }
    
    .is-valid {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 0.2rem rgba(16, 185, 129, 0.25) !important;
    }
    
    .is-invalid {
        border-color: #ef4444 !important;
        box-shadow: 0 0 0 0.2rem rgba(239, 68, 68, 0.25) !important;
    }
`;
document.head.appendChild(style);