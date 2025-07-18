// Mobile Viewport Height Fix for iOS Safari
(function() {
    'use strict';
    
    // Fix viewport height for mobile browsers
    function setVH() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
    
    // Set initial values
    setVH();
    
    // Update on resize and orientation change
    window.addEventListener('resize', setVH);
    window.addEventListener('orientationchange', () => {
        setTimeout(setVH, 100);
    });
    
    // iOS Safari specific fixes
    if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
        // Prevent zoom on input focus
        document.addEventListener('touchstart', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                e.target.style.fontSize = '16px';
            }
        });
        
        // Handle keyboard appearance
        window.addEventListener('resize', function() {
            const currentHeight = window.innerHeight;
            const fullHeight = window.screen.height;
            
            // Check if keyboard is visible
            if (currentHeight < fullHeight * 0.75) {
                document.body.classList.add('keyboard-visible');
            } else {
                document.body.classList.remove('keyboard-visible');
            }
        });
    }
    
    // Prevent overscroll bounce
    document.addEventListener('touchmove', function(e) {
        // Allow scrolling inside search results
        if (e.target.closest('.main-search-results') || 
            e.target.closest('.search-suggestions') ||
            e.target.closest('.overflow-auto')) {
            return;
        }
        
        // Prevent bounce on body
        if (e.target === document.body) {
            e.preventDefault();
        }
    }, { passive: false });
    
    // Smooth scrolling for anchor links
    document.addEventListener('click', function(e) {
        if (e.target.matches('a[href^="#"]')) {
            e.preventDefault();
            const target = document.querySelector(e.target.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
    
    // Add touch feedback for buttons
    document.addEventListener('touchstart', function(e) {
        if (e.target.matches('.btn, .nav-btn, .stock-chip, .chatgpt-search-btn')) {
            e.target.classList.add('touch-active');
        }
    });
    
    document.addEventListener('touchend', function(e) {
        if (e.target.matches('.btn, .nav-btn, .stock-chip, .chatgpt-search-btn')) {
            setTimeout(() => {
                e.target.classList.remove('touch-active');
            }, 150);
        }
    });
    
    // Optimize scroll performance
    let ticking = false;
    
    function updateScrollPosition() {
        const scrollY = window.scrollY;
        document.documentElement.style.setProperty('--scroll-y', scrollY);
        ticking = false;
    }
    
    document.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateScrollPosition);
            ticking = true;
        }
    });
    
    // Handle search input focus on mobile
    document.addEventListener('focusin', function(e) {
        if (e.target.matches('input[type="text"], input[type="search"], textarea')) {
            // Scroll to input after keyboard appears
            setTimeout(() => {
                e.target.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        }
    });
    
    // Add CSS for touch feedback
    const style = document.createElement('style');
    style.textContent = `
        .touch-active {
            transform: scale(0.95);
            opacity: 0.7;
            transition: all 0.1s ease;
        }
        
        .keyboard-visible .main-search-interface {
            min-height: 50vh;
        }
        
        .keyboard-visible .search-welcome {
            margin-bottom: 1rem;
        }
        
        .keyboard-visible .popular-stocks {
            margin-bottom: 1rem;
        }
    `;
    document.head.appendChild(style);
    
    console.log('Mobile viewport optimizations loaded');
})();