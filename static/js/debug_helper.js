/* Bloomberg Terminal Debug Helper */

class DebugHelper {
    constructor() {
        this.errors = [];
        this.warnings = [];
        this.init();
    }

    init() {
        // Intercept console errors
        window.addEventListener('error', (e) => {
            this.logError('JavaScript Error', e.message, e.filename, e.lineno);
        });

        // Intercept unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            this.logError('Unhandled Promise Rejection', e.reason);
        });

        // Override console methods for better debugging
        this.overrideConsole();
    }

    overrideConsole() {
        const originalError = console.error;
        const originalWarn = console.warn;

        console.error = (...args) => {
            this.logError('Console Error', ...args);
            originalError(...args);
        };

        console.warn = (...args) => {
            this.logWarning('Console Warning', ...args);
            originalWarn(...args);
        };
    }

    logError(type, ...details) {
        const error = {
            type,
            details,
            timestamp: new Date().toISOString(),
            stack: new Error().stack
        };
        this.errors.push(error);
        
        // Only keep last 50 errors
        if (this.errors.length > 50) {
            this.errors = this.errors.slice(-50);
        }
    }

    logWarning(type, ...details) {
        const warning = {
            type,
            details,
            timestamp: new Date().toISOString()
        };
        this.warnings.push(warning);
        
        // Only keep last 50 warnings
        if (this.warnings.length > 50) {
            this.warnings = this.warnings.slice(-50);
        }
    }

    getDebugInfo() {
        return {
            errors: this.errors,
            warnings: this.warnings,
            componentStatus: this.checkComponents(),
            jsFiles: this.checkJSFiles(),
            intervals: this.checkIntervals()
        };
    }

    checkComponents() {
        const requiredComponents = [
            'mainAnalysisContainer',
            'watchlistContainer',
            'marketNewsContainer',
            'aiAlertsContainer',
            'detailedMetricsTable',
            'mainChart',
            'search-input',
            'search-suggestions'
        ];

        const status = {};
        requiredComponents.forEach(id => {
            const element = document.getElementById(id);
            status[id] = {
                exists: !!element,
                hasParent: element && !!element.parentNode,
                hasStyle: element && typeof element.style === 'object',
                visible: element && element.offsetParent !== null
            };
        });

        return status;
    }

    checkJSFiles() {
        const expectedGlobals = [
            'bloombergTerminal',
            'searchStockAI',
            'analyzeStock',
            'Chart'
        ];

        const status = {};
        expectedGlobals.forEach(global => {
            status[global] = typeof window[global] !== 'undefined';
        });

        return status;
    }

    checkIntervals() {
        // Check if Bloomberg Terminal intervals are running
        const terminal = window.bloombergTerminal;
        if (terminal) {
            return {
                terminalInitialized: terminal.isInitialized,
                activeIntervals: terminal.updateIntervals ? terminal.updateIntervals.length : 0,
                componentsCount: terminal.terminalComponents ? terminal.terminalComponents.size : 0
            };
        }
        return { terminalFound: false };
    }

    generateReport() {
        const info = this.getDebugInfo();
        
        console.group('🔍 Bloomberg Terminal Debug Report');
        
        // Recent errors
        console.group('❌ Recent Errors');
        info.errors.slice(-5).forEach(error => {
            console.error(`[${error.timestamp}] ${error.type}:`, ...error.details);
        });
        console.groupEnd();
        
        // Component status
        console.group('🧩 Component Status');
        Object.entries(info.componentStatus).forEach(([id, status]) => {
            const icon = status.exists ? '✅' : '❌';
            console.log(`${icon} ${id}:`, status);
        });
        console.groupEnd();
        
        // JS Files status
        console.group('📜 JavaScript Files');
        Object.entries(info.jsFiles).forEach(([global, exists]) => {
            const icon = exists ? '✅' : '❌';
            console.log(`${icon} ${global}: ${exists ? 'Loaded' : 'Missing'}`);
        });
        console.groupEnd();
        
        // Intervals status
        console.group('⏰ Intervals Status');
        console.log('Terminal Status:', info.intervals);
        console.groupEnd();
        
        console.groupEnd();
        
        return info;
    }

    fixCommonIssues() {
        console.log('🔧 Attempting to fix common issues...');
        
        // Fix missing components
        this.createMissingComponents();
        
        // Clear problematic intervals
        this.clearProblematicIntervals();
        
        // Reinitialize terminal if needed
        this.reinitializeTerminal();
        
        console.log('✅ Auto-fix completed');
    }

    createMissingComponents() {
        const missingComponents = [
            { id: 'search-suggestions', parent: 'search-input', tag: 'div', className: 'desktop-search-suggestions' }
        ];

        missingComponents.forEach(comp => {
            if (!document.getElementById(comp.id)) {
                const parent = document.getElementById(comp.parent);
                if (parent && parent.parentNode) {
                    const element = document.createElement(comp.tag);
                    element.id = comp.id;
                    element.className = comp.className;
                    parent.parentNode.appendChild(element);
                    console.log(`✅ Created missing component: ${comp.id}`);
                }
            }
        });
    }

    clearProblematicIntervals() {
        // Clear all interval timers to prevent the recurring errors
        const highestId = setTimeout(() => {}, 0);
        for (let i = 0; i <= highestId; i++) {
            clearTimeout(i);
            clearInterval(i);
        }
        console.log('✅ Cleared all intervals/timeouts');
    }

    reinitializeTerminal() {
        if (window.bloombergTerminal && !window.bloombergTerminal.isInitialized) {
            try {
                window.bloombergTerminal.initialize();
                console.log('✅ Bloomberg Terminal reinitialized');
            } catch (error) {
                console.error('❌ Failed to reinitialize terminal:', error);
            }
        }
    }
}

// Create global debug helper
window.debugHelper = new DebugHelper();

// Add keyboard shortcut for debug report
document.addEventListener('keydown', (e) => {
    // Ctrl+Shift+D for debug report
    if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        window.debugHelper.generateReport();
    }
    // Ctrl+Shift+F for auto-fix
    if (e.ctrlKey && e.shiftKey && e.key === 'F') {
        e.preventDefault();
        window.debugHelper.fixCommonIssues();
    }
});

console.log('🔍 Debug Helper loaded. Press Ctrl+Shift+D for debug report, Ctrl+Shift+F for auto-fix');