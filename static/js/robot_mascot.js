/* TradeWise AI Robot Mascot JavaScript */

class RobotMascot {
    constructor() {
        this.thoughts = [
            "Analyzing markets...",
            "Finding good deals!",
            "AI thinking...",
            "Crunching data...",
            "Market insights ready!",
            "Trading wisdom activated",
            "Smart moves ahead!",
            "AI-powered analysis"
        ];
        this.currentThoughtIndex = 0;
        this.init();
    }

    init() {
        this.createRobot();
        this.setupEventListeners();
        this.startThoughtCycle();
    }

    createRobot() {
        const robotHTML = `
            <div class="ai-robot-mascot" id="aiRobotMascot">
                <div class="robot-container" id="robotContainer">
                    <!-- Robot Head -->
                    <div class="robot-head">
                        <div class="robot-antenna"></div>
                        <div class="robot-eyes">
                            <div class="robot-eye"></div>
                            <div class="robot-eye"></div>
                        </div>
                        <div class="robot-mouth"></div>
                    </div>
                    
                    <!-- Robot Body -->
                    <div class="robot-body">
                        <!-- Robot Arms -->
                        <div class="robot-arms">
                            <div class="robot-arm left"></div>
                            <div class="robot-arm right"></div>
                        </div>
                    </div>
                    
                    <!-- Robot Legs -->
                    <div class="robot-legs">
                        <div class="robot-leg"></div>
                        <div class="robot-leg"></div>
                    </div>
                    
                    <!-- Thought Bubble -->
                    <div class="robot-thought" id="robotThought">
                        ${this.thoughts[0]}
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', robotHTML);
    }

    setupEventListeners() {
        const robot = document.getElementById('aiRobotMascot');
        const robotContainer = document.getElementById('robotContainer');

        robot.addEventListener('click', () => {
            this.handleRobotClick();
        });

        robot.addEventListener('mouseenter', () => {
            this.showThought();
        });

        robot.addEventListener('mouseleave', () => {
            this.hideThought();
        });
    }

    handleRobotClick() {
        const robotContainer = document.getElementById('robotContainer');
        
        // Add excited animation
        robotContainer.classList.add('clicked');
        
        // Remove animation class after animation completes
        setTimeout(() => {
            robotContainer.classList.remove('clicked');
        }, 600);

        // Show a random encouraging message
        this.showRandomMessage();

        // Optional: Trigger AI assistant or helpful action
        this.triggerHelpfulAction();
    }

    showRandomMessage() {
        const messages = [
            "Hi there! Need trading help?",
            "Let's find great investments!",
            "Ready to boost your portfolio?",
            "AI analysis at your service!",
            "Smart trading awaits!",
            "Let's make wise trades!",
            "Market opportunities ahead!"
        ];

        const randomMessage = messages[Math.floor(Math.random() * messages.length)];
        this.showTemporaryThought(randomMessage, 2000);
    }

    showTemporaryThought(message, duration = 2000) {
        const thoughtBubble = document.getElementById('robotThought');
        const originalMessage = thoughtBubble.textContent;

        thoughtBubble.textContent = message;
        thoughtBubble.style.opacity = '1';
        thoughtBubble.style.transform = 'translateY(0)';

        setTimeout(() => {
            thoughtBubble.textContent = originalMessage;
            thoughtBubble.style.opacity = '0';
            thoughtBubble.style.transform = 'translateY(5px)';
        }, duration);
    }

    showThought() {
        const thoughtBubble = document.getElementById('robotThought');
        thoughtBubble.style.opacity = '1';
        thoughtBubble.style.transform = 'translateY(0)';
    }

    hideThought() {
        const thoughtBubble = document.getElementById('robotThought');
        thoughtBubble.style.opacity = '0';
        thoughtBubble.style.transform = 'translateY(5px)';
    }

    startThoughtCycle() {
        setInterval(() => {
            this.currentThoughtIndex = (this.currentThoughtIndex + 1) % this.thoughts.length;
            const thoughtBubble = document.getElementById('robotThought');
            thoughtBubble.textContent = this.thoughts[this.currentThoughtIndex];
        }, 5000); // Change thought every 5 seconds
    }

    triggerHelpfulAction() {
        // You can customize this to trigger specific actions
        // For example, scroll to search, show tips, etc.
        
        // Example: Smooth scroll to search if it exists
        const searchInput = document.querySelector('input[type="search"], .search-container input');
        if (searchInput) {
            searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Add a subtle highlight effect
            searchInput.style.boxShadow = '0 0 20px rgba(139, 92, 246, 0.5)';
            setTimeout(() => {
                searchInput.style.boxShadow = '';
            }, 2000);
        }
    }

    // Method to update robot's mood based on market conditions
    updateMood(marketCondition) {
        const robot = document.getElementById('aiRobotMascot');
        
        // Remove existing mood classes
        robot.classList.remove('bullish', 'bearish', 'neutral');
        
        // Add appropriate mood class
        robot.classList.add(marketCondition);
        
        // Update thoughts based on market condition
        switch(marketCondition) {
            case 'bullish':
                this.thoughts = [
                    "Markets looking great!",
                    "Bullish vibes detected!",
                    "Opportunities everywhere!",
                    "Time to invest wisely!",
                    "Green day ahead!"
                ];
                break;
            case 'bearish':
                this.thoughts = [
                    "Stay cautious today",
                    "Good time for research",
                    "Patience is key",
                    "Look for value plays",
                    "Defensive positions?"
                ];
                break;
            default:
                this.thoughts = [
                    "Analyzing markets...",
                    "Finding good deals!",
                    "AI thinking...",
                    "Market insights ready!"
                ];
        }
    }

    // Method to hide/show robot
    toggle(show = true) {
        const robot = document.getElementById('aiRobotMascot');
        robot.style.display = show ? 'block' : 'none';
    }
}

// Initialize the robot mascot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Small delay to ensure other elements are loaded
    setTimeout(() => {
        window.robotMascot = new RobotMascot();
    }, 1000);
});

// Optional: Add market-responsive behavior
document.addEventListener('marketDataUpdated', (event) => {
    if (window.robotMascot && event.detail) {
        const marketTrend = event.detail.trend || 'neutral';
        window.robotMascot.updateMood(marketTrend);
    }
});