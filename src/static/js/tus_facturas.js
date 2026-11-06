document.addEventListener('DOMContentLoaded', function() {
    
    const rows = document.querySelectorAll('.facturas-table tbody tr');
    rows.forEach((row, index) => {
        row.style.animationDelay = `${index * 0.1}s`;
    });

    document.querySelectorAll('.action-button').forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.02)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    document.querySelectorAll('.facturas-table tbody tr').forEach(row => {
        row.addEventListener('click', function(e) {
            if (!e.target.closest('.action-button')) {
                const button = this.querySelector('.action-button');
                if (button) {
                    window.location.href = button.href;
                }
            }
        });
    });
});

function addShimmerEffect() {
    const container = document.querySelector('.facturas-container');
    container.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
    });
    
    container.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
}

document.addEventListener('DOMContentLoaded', addShimmerEffect);