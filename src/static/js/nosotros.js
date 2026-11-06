document.addEventListener('DOMContentLoaded', function() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.info-card, .social-section, .page-title');
    animatedElements.forEach(el => observer.observe(el));

    document.querySelectorAll('.info-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) rotateX(2deg)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) rotateX(0deg)';
        });
    });

    document.querySelector('.cta-button').addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        this.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });

    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const cards = document.querySelectorAll('.info-card');
        
        cards.forEach((card, index) => {
            const speed = 1 + (index % 2) * 0.5;
            card.style.transform = `translateY(${scrolled * speed * 0.02}px)`;
        });
    });
});

function goBack() {
    window.history.back();
}

function makeOrder() {
    const button = document.querySelector('.cta-button');
    const container = document.querySelector('.container');
    
    container.classList.add('loading');
    
    setTimeout(() => {
        container.classList.remove('loading');
        alert('¡Redirigiendo al sistema de pedidos!');
    }, 2000);
}