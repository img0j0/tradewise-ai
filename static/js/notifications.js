// Enhanced notification system for the trading platform

if (!window.NotificationManager) {
    window.NotificationManager = class {
    constructor() {
        this.notifications = [];
        this.maxNotifications = 5;
        this.defaultDuration = 5000; // 5 seconds
        this.container = this.createContainer();
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        document.body.appendChild(container);
        return container;
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
        
        return {
            element,
            type,
            message,
            timestamp: Date.now()
        };
    }

    getIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-triangle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle',
            trade: 'fas fa-chart-line'
        };
        return icons[type] || icons.info;
    }

    remove(notification) {
        if (notification && notification.element) {
            notification.element.classList.add('removing');
            setTimeout(() => {
                if (notification.element.parentNode) {
                    notification.element.parentNode.removeChild(notification.element);
                }
                this.notifications = this.notifications.filter(n => n !== notification);
            }, 300);
        }
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