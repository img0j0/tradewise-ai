// Enhanced notification system for the trading platform

class NotificationManager {
    constructor() {
        this.notifications = [];
        this.maxNotifications = 5;
        this.defaultDuration = 5000; // 5 seconds
        this.container = this.createContainer();
        this.addStyles();
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        document.body.appendChild(container);
        return container;
    }

    addStyles() {
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .notification-container {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    pointer-events: none;
                }
                
                .notification {
                    margin-bottom: 10px;
                    padding: 15px;
                    border-radius: 8px;
                    color: white;
                    min-width: 300px;
                    max-width: 400px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    opacity: 0;
                    transform: translateX(100%);
                    transition: all 0.3s ease;
                    pointer-events: auto;
                }
                
                .notification.show {
                    opacity: 1;
                    transform: translateX(0);
                }
                
                .notification.hide {
                    opacity: 0;
                    transform: translateX(100%);
                }
                
                .notification-success { background: linear-gradient(135deg, #28a745, #20c997); }
                .notification-error { background: linear-gradient(135deg, #dc3545, #fd7e14); }
                .notification-warning { background: linear-gradient(135deg, #ffc107, #fd7e14); }
                .notification-info { background: linear-gradient(135deg, #17a2b8, #6f42c1); }
                .notification-trade { background: linear-gradient(135deg, #6f42c1, #e83e8c); }
                
                .notification-header {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .notification-header i {
                    font-size: 16px;
                    flex-shrink: 0;
                }
                
                .notification-message {
                    flex-grow: 1;
                    font-size: 14px;
                    line-height: 1.4;
                }
                
                .notification-close {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 14px;
                    cursor: pointer;
                    padding: 0;
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    opacity: 0.7;
                    transition: opacity 0.2s;
                }
                
                .notification-close:hover {
                    opacity: 1;
                    background: rgba(255,255,255,0.1);
                }
                
                .notification-actions {
                    margin-top: 10px;
                    display: flex;
                    gap: 8px;
                }
                
                .notification-actions .btn {
                    font-size: 12px;
                    padding: 4px 8px;
                    border-radius: 4px;
                }
            `;
            document.head.appendChild(style);
        }
    }

    show(message, type = 'info', duration = this.defaultDuration, actions = null) {
        const notification = this.createNotification(message, type, duration, actions);
        
        // Add to notifications array
        this.notifications.push(notification);
        
        // Remove oldest if exceeding max
        if (this.notifications.length > this.maxNotifications) {
            this.remove(this.notifications[0]);
        }
        
        // Add to DOM
        this.container.appendChild(notification.element);
        
        // Trigger animation
        setTimeout(() => {
            notification.element.classList.add('show');
        }, 10);
        
        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }
        
        return notification;
    }

    createNotification(message, type, duration, actions) {
        const element = document.createElement('div');
        element.className = `notification notification-${type}`;
        
        const icon = this.getIcon(type);
        let actionsHtml = '';
        
        if (actions && actions.length > 0) {
            actionsHtml = `
                <div class="notification-actions">
                    ${actions.map(action => `
                        <button class="btn btn-sm btn-outline-light" onclick="${action.onClick}">
                            ${action.text}
                        </button>
                    `).join('')}
                </div>
            `;
        }
        
        element.innerHTML = `
            <div class="notification-content">
                <div class="notification-header">
                    <i class="${icon}"></i>
                    <span class="notification-message">${message}</span>
                    <button class="notification-close" onclick="notificationManager.removeElement(this.closest('.notification'))">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                ${actionsHtml}
            </div>
        `;
        
        return { element, id: Date.now() + Math.random() };
    }

    getIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle',
            trade: 'fas fa-chart-line'
        };
        return icons[type] || icons.info;
    }

    remove(notification) {
        if (!notification || !notification.element) return;
        
        notification.element.classList.remove('show');
        notification.element.classList.add('hide');
        
        setTimeout(() => {
            if (notification.element.parentNode) {
                notification.element.parentNode.removeChild(notification.element);
            }
            
            const index = this.notifications.indexOf(notification);
            if (index > -1) {
                this.notifications.splice(index, 1);
            }
        }, 300);
    }

    removeElement(element) {
        const notification = this.notifications.find(n => n.element === element);
        if (notification) {
            this.remove(notification);
        }
    }

    clear() {
        this.notifications.forEach(notification => this.remove(notification));
    }

    // Specialized notification methods
    showSuccess(message, duration = this.defaultDuration) {
        return this.show(message, 'success', duration);
    }

    showError(message, duration = 8000) {
        return this.show(message, 'error', duration);
    }

    showWarning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    }

    showInfo(message, duration = this.defaultDuration) {
        return this.show(message, 'info', duration);
    }

    showTradeAlert(message, actions = null, duration = 10000) {
        return this.show(message, 'trade', duration, actions);
    }
}

// Initialize global notification manager
if (!window.notificationManager) {
    window.notificationManager = new NotificationManager();
}