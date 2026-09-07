// ============================================
// SMOOTH INTERACTIONS & MICRO-ANIMATIONS
// ============================================

// Handle clickable skill badges on company selection page
document.addEventListener('DOMContentLoaded', function () {
    initializeSkillBadges();
    addPageLoadAnimation();
    initializeFormAnimations();
});

// Initialize skill badge interactions
function initializeSkillBadges() {
    document.querySelectorAll('.skill-badge').forEach(function (btn) {
        // Add hover ripple effect
        btn.addEventListener('mouseenter', function() {
            addRippleEffect(this);
        });

        btn.addEventListener('click', function (e) {
            const companyId = this.dataset.companyId;
            const skillId = this.dataset.skillId;
            if (!companyId || !skillId) return;

            // Add loading state with animation
            const originalText = this.textContent;
            this.style.opacity = '0.7';

            // Send toggle request
            fetch('/student/toggle-skill', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ company_id: companyId, skill_id: skillId })
            }).then(r => r.json()).then(data => {
                this.style.opacity = '1';
                
                if (data && data.success) {
                    if (data.selected) {
                        btn.classList.add('selected');
                        // Animate the checkmark
                        animateSelection(btn);
                    } else {
                        btn.classList.remove('selected');
                        // Animate the deselection
                        animateDeselection(btn);
                    }
                } else {
                    alert(data.message || 'Could not update selection');
                }
            }).catch(err => {
                console.error(err);
                this.style.opacity = '1';
                alert('Network error');
            });
        });
    });
}

// Add ripple effect on button click
function addRippleEffect(element) {
    const rect = element.getBoundingClientRect();
    const ripple = document.createElement('span');
    ripple.style.position = 'absolute';
    ripple.style.borderRadius = '50%';
    ripple.style.background = 'rgba(0, 217, 255, 0.5)';
    ripple.style.transform = 'scale(0)';
    ripple.style.animation = 'ripple-animation 0.6s ease-out';
    ripple.style.pointerEvents = 'none';
    ripple.style.width = '30px';
    ripple.style.height = '30px';
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
}

// Animate skill selection with smooth transition
function animateSelection(element) {
    element.style.animation = 'none';
    setTimeout(() => {
        element.style.animation = 'pulse-glow 0.5s ease-out';
    }, 10);
}

// Animate skill deselection
function animateDeselection(element) {
    element.style.animation = 'none';
    setTimeout(() => {
        element.style.animation = 'fade-pulse 0.5s ease-out';
    }, 10);
}

// Add page load animation
function addPageLoadAnimation() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.animation = `fadeInUp 0.5s ease-out ${index * 0.1}s forwards`;
    });
}

// Initialize form animations
function initializeFormAnimations() {
    const inputs = document.querySelectorAll('.form-control, .form-select');
    
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.transform = 'scale(1.02)';
            this.style.boxShadow = '0 0 20px rgba(0, 217, 255, 0.3)';
        });

        input.addEventListener('blur', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '';
        });

        // Add smooth input animation on value change
        input.addEventListener('input', function() {
            this.style.borderColor = 'rgba(0, 217, 255, 0.5)';
        });
    });
}

// Smooth scroll behavior for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add keyboard navigation enhancements
document.addEventListener('keydown', function(e) {
    // Escape to dismiss alerts
    if (e.key === 'Escape') {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.style.animation = 'fadeOut 0.3s ease-out forwards';
            setTimeout(() => {
                alert.remove();
            }, 300);
        });
    }
});

// Animate alerts on appearance
function animateAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert, index) => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(-20px)';
        alert.style.animation = `slideIn 0.4s ease-out ${index * 0.1}s forwards`;
    });
}

animateAlerts();

// Add smooth number counter animations for stats
function animateCounter(element, target, duration = 1500) {
    if (!element || isNaN(target)) return;
    
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Observe elements and animate counters when they come into view
if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                if (element.classList.contains('stat-card')) {
                    const counterElement = element.querySelector('h3');
                    if (counterElement && !element.dataset.animated) {
                        const value = parseInt(counterElement.textContent);
                        if (!isNaN(value) && value > 0) {
                            animateCounter(counterElement, value);
                            element.dataset.animated = 'true';
                        }
                    }
                }
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.stat-card').forEach(card => {
        observer.observe(card);
    });
}

// Add to stylesheet for smooth animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(-20px);
        }
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes pulse-glow {
        0% {
            box-shadow: 0 0 10px rgba(0, 255, 150, 0.4);
            transform: scale(1);
        }
        50% {
            box-shadow: 0 0 20px rgba(0, 255, 150, 0.6);
            transform: scale(1.05);
        }
        100% {
            box-shadow: 0 0 20px rgba(0, 255, 150, 0.4);
            transform: scale(1);
        }
    }

    @keyframes fade-pulse {
        0% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
        100% {
            opacity: 1;
        }
    }

    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .btn-close {
        background: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='%2300d9ff' d='M.293.293a1 1 0 011.414 0L8 6.586 14.293.293a1 1 0 111.414 1.414L9.414 8l6.293 6.293a1 1 0 01-1.414 1.414L8 9.414l-6.293 6.293a1 1 0 01-1.414-1.414L6.586 8 .293 1.707a1 1 0 010-1.414z'/%3e%3c/svg%3e") center/1em auto no-repeat;
        filter: drop-shadow(0 0 4px rgba(0, 217, 255, 0.3));
    }

    .btn-close:hover {
        filter: drop-shadow(0 0 8px rgba(0, 217, 255, 0.5));
    }
`;
document.head.appendChild(style);
