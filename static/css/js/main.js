// ========================================
// CareerMantra AI - Global Animations & UX
// Glass Morphism + Smooth Micro-interactions
// ========================================

// 🎬 Init on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    initGlassAnimations();
    initScrollReveal();
    initThemeWatcher();
    initKeyboardShortcuts();
    initLoadingStates();
});

// 🌟 Glass Morphism Animations
function initGlassAnimations() {
    // Staggered card entrance
    const cards = document.querySelectorAll('.glass-card, .group, [class*="glass"]');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate-fadeInUp');
        
        // Hover parallax effect
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-10px) scale(1.02)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Button micro-interactions
    document.querySelectorAll('button, .btn, [role="button"]').forEach(btn => {
        btn.addEventListener('mousedown', () => btn.classList.add('scale-95'));
        btn.addEventListener('mouseup', () => btn.classList.remove('scale-95'));
        btn.addEventListener('mouseleave', () => btn.classList.remove('scale-95'));
    });
}

// 📜 Scroll Reveal Animations
function initScrollReveal() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-slideInUp');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll, section, .glass-card').forEach(el => {
        observer.observe(el);
    });
}

// 🌙 Dark/Light Theme Watcher
function initThemeWatcher() {
    const themeToggle = document.querySelector('[data-theme-toggle]');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
        });

        // Load saved theme
        if (localStorage.getItem('theme') === 'dark') {
            document.body.classList.add('dark-theme');
        }
    }
}

// ⌨️ Keyboard Shortcuts (Pro UX)
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // ESC = Close modals/popups
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show, [data-modal]');
            modals.forEach(modal => modal.classList.remove('show'));
        }

        // Ctrl/Cmd + K = Quick search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[placeholder*="search"], input[type="search"]');
            if (searchInput) searchInput.focus();
        }
    });
}

// ⏳ Smart Loading States
function initLoadingStates() {
    // Auto-remove loading spinners
    const observer = new MutationObserver(() => {
        document.querySelectorAll('.loading').forEach(el => {
            setTimeout(() => {
                el.classList.remove('loading');
            }, 2000);
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
}

// 🌈 Utility Animation Functions
window.fadeIn = (element, duration = 500) => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    requestAnimationFrame(() => {
        element.style.transition = `all ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    });
};

window.fadeOut = (element, duration = 500, callback) => {
    element.style.transition = `all ${duration}ms ease`;
    element.style.opacity = '0';
    element.style.transform = 'translateY(-20px)';
    setTimeout(callback, duration);
};

window.slideInFromLeft = (element) => {
    element.style.opacity = '0';
    element.style.transform = 'translateX(-50px)';
    requestAnimationFrame(() => {
        element.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
        element.style.opacity = '1';
        element.style.transform = 'translateX(0)';
    });
};

window.slideInFromRight = (element) => {
    element.style.opacity = '0';
    element.style.transform = 'translateX(50px)';
    requestAnimationFrame(() => {
        element.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
        element.style.opacity = '1';
        element.style.transform = 'translateX(0)';
    });
};

// 🎪 Page Transition Handler
window.initPageTransitions = () => {
    // Intercept all internal links
    document.querySelectorAll('a[href^="/"]:not([href="/#"])').forEach(link => {
        link.addEventListener('click', (e) => {
            const isModal = link.closest('.modal');
            if (!isModal) {
                e.preventDefault();
                const href = link.getAttribute('href');
                fadeOut(document.body, 300, () => {
                    window.location.href = href;
                });
            }
        });
    });
};

// 📱 Mobile Menu Toggle
window.toggleMobileMenu = () => {
    const menu = document.querySelector('[data-mobile-menu]');
    const overlay = document.querySelector('[data-overlay]');
    menu.classList.toggle('translate-x-full');
    overlay.classList.toggle('opacity-0');
};

// 🎯 Confetti Celebration (Level Complete!)
window.celebrate = (score) => {
    // Simple canvas confetti
    const canvas = document.createElement('canvas');
    canvas.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999;';
    document.body.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const confetti = [];
    for (let i = 0; i < 100; i++) {
        confetti.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height - canvas.height,
            r: Math.random() * 6 + 2,
            d: Math.random() * 200 + 100,
            color: `hsl(${Math.random() * 60 + 0}, 70%, 60%)`,
            tilt: Math.random() * 10,
            tiltAngle: 0
        });
    }
    
    let animationFrame;
    const animate = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        confetti.forEach((c, i) => {
            c.tiltAngle += 0.1;
            c.y += (Math.cos(c.d + c.tiltAngle) + 3) * 2;
            c.tilt = Math.sin(c.tiltAngle) * 15;
            
            if (c.y > canvas.height) {
                confetti.splice(i, 1);
            } else {
                ctx.save();
                ctx.translate(c.x, c.y);
                ctx.rotate(c.tiltAngle);
                ctx.fillStyle = c.color;
                ctx.fillRect(-c.r, -c.r, c.r * 2, c.r * 2);
                ctx.restore();
            }
        });
        
        if (confetti.length > 0) {
            animationFrame = requestAnimationFrame(animate);
        } else {
            document.body.removeChild(canvas);
            cancelAnimationFrame(animationFrame);
        }
    };
    animate();
};

// 🔔 Toast Notifications
window.showToast = (message, type = 'success') => {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 p-4 rounded-2xl shadow-2xl z-50 transform translate-x-full animate-slideInRight transition-all duration-300 ${
        type === 'success' ? 'bg-emerald-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('animate-slideOutRight');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

// 📊 Auto-save Progress (LocalStorage)
window.saveProgress = (level, score) => {
    const progress = JSON.parse(localStorage.getItem('careermantra_progress') || '{}');
    progress[level] = Math.max(progress[level] || 0, score);
    localStorage.setItem('careermantra_progress', JSON.stringify(progress));
};

// 🎨 Custom CSS Animations (Fallback)
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideInUp { 
        from { opacity: 0; transform: translateY(50px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    .animate-fadeInUp { animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) both; }
    .animate-slideInUp { animation: slideInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) both; }
    .animate-slideInRight { animation: slideInRight 0.4s ease-out both; }
    .animate-slideOutRight { animation: slideOutRight 0.3s ease-in both; }
`;
document.head.appendChild(style);

// 🔥 Initialize everything
window.initCareerMantra = () => {
    initGlassAnimations();
    initScrollReveal();
    initPageTransitions();
};
