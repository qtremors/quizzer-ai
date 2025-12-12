/**
 * Alpine.js Toast Notification System
 * Usage: Alpine.store('toast').show('Message', 'success', 5000)
 */

document.addEventListener('alpine:init', () => {
    Alpine.store('toast', {
        toasts: [],
        counter: 0,

        /**
         * Show a toast notification
         * @param {string} message - The message to display
         * @param {string} type - Type: 'success' | 'error' | 'warning' | 'info'
         * @param {number} duration - Duration in ms (default 5000, 0 for persistent)
         * @param {string} title - Optional title
         */
        show(message, type = 'info', duration = 5000, title = null) {
            const id = ++this.counter;
            
            const icons = {
                success: 'check_circle',
                error: 'error',
                warning: 'warning',
                info: 'info'
            };
            
            const titles = {
                success: 'Success',
                error: 'Error',
                warning: 'Warning',
                info: 'Info'
            };

            const toast = {
                id,
                message,
                type,
                icon: icons[type] || 'info',
                title: title || titles[type] || 'Notification',
                duration,
                leaving: false
            };

            this.toasts.push(toast);

            if (duration > 0) {
                setTimeout(() => this.dismiss(id), duration);
            }

            return id;
        },

        /**
         * Dismiss a toast by ID
         */
        dismiss(id) {
            const toast = this.toasts.find(t => t.id === id);
            if (toast) {
                toast.leaving = true;
                setTimeout(() => {
                    this.toasts = this.toasts.filter(t => t.id !== id);
                }, 300); // Match animation duration
            }
        },

        /**
         * Clear all toasts
         */
        clear() {
            this.toasts.forEach(t => t.leaving = true);
            setTimeout(() => {
                this.toasts = [];
            }, 300);
        },

        // Convenience methods
        success(message, title = null, duration = 5000) {
            return this.show(message, 'success', duration, title);
        },

        error(message, title = null, duration = 7000) {
            return this.show(message, 'error', duration, title);
        },

        warning(message, title = null, duration = 6000) {
            return this.show(message, 'warning', duration, title);
        },

        info(message, title = null, duration = 5000) {
            return this.show(message, 'info', duration, title);
        }
    });
});

/**
 * Global helper function for easy access
 */
window.showToast = function(message, type = 'info', duration = 5000) {
    if (window.Alpine && Alpine.store('toast')) {
        return Alpine.store('toast').show(message, type, duration);
    }
    console.warn('Toast system not ready');
};
