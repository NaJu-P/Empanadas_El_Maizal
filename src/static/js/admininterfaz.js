window.addEventListener('pageshow', function (event) {
    if (event.persisted || window.performance && performance.getEntriesByType("navigation")[0].type === "back_forward") {
        window.location.reload(); // Recarga sin caché
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const userIcon = document.getElementById('user-icon');
    const dropdownMenu = document.getElementById('dropdown-menu');
    const logoutLink = document.getElementById('logout-link');
    let touchStartY = 0;

    // Manejo del menú dropdown
    userIcon.addEventListener('click', toggleDropdown);
    userIcon.addEventListener('touchstart', toggleDropdown);

    // Manejo del logout con fetch (versión robusta)
    logoutLink.addEventListener('click', handleLogoutWithFetch);

    // Cerrar dropdown al hacer click fuera
    document.addEventListener('click', function(e) {
        if (!userIcon.contains(e.target) && !dropdownMenu.contains(e.target)) {
            dropdownMenu.classList.remove('show');
        }
    });

    // Soporte para gestos táctiles
    document.addEventListener('touchstart', function(e) {
        touchStartY = e.touches[0].clientY;
    });

    document.addEventListener('touchmove', function(e) {
        if (dropdownMenu.classList.contains('show')) {
            const touchEndY = e.touches[0].clientY;
            const diff = touchStartY - touchEndY;

            if (Math.abs(diff) > 30) {
                dropdownMenu.classList.remove('show');
            }
        }
    });

    // Detección de orientación del dispositivo
    window.addEventListener('orientationchange', function() {
        dropdownMenu.classList.remove('show');
        adjustLayout();
    });

    // Ajustar layout según el tamaño de la pantalla
    function adjustLayout() {
        const width = window.innerWidth;
        const adminCards = document.querySelectorAll('.admin-card');

        adminCards.forEach(card => {
            if (width <= 768) {
                card.style.animation = 'none';
                setTimeout(() => {
                    card.style.animation = '';
                }, 10);
            }
        });
    }

    function toggleDropdown(e) {
        e.preventDefault();
        e.stopPropagation();
        dropdownMenu.classList.toggle('show');
    }

    // Función robusta para manejar el logout con fetch
    async function handleLogoutWithFetch(e) {
        e.preventDefault();
        
        if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
            try {
                // Mostrar indicador de carga
                const originalContent = logoutLink.innerHTML;
                logoutLink.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cerrando...';
                
                // Hacer la petición al endpoint de logout
                const response = await fetch('/admin/logout', {
                    method: 'GET',
                    credentials: 'same-origin', // Incluir cookies de sesión
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (response.ok) {
                    // Mostrar mensaje de éxito
                    logoutLink.innerHTML = '<i class="fas fa-check"></i> Sesión cerrada';
                    
                    // Redirigir al login después de un breve delay
                    setTimeout(() => {
                        window.location.href = '/admin/login';
                    }, 1000);
                } else {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
            } catch (error) {
                console.error('Error al cerrar sesión:', error);
                alert('Error al cerrar sesión. Inténtalo de nuevo.');
                
                // Restaurar el texto original del botón
                logoutLink.innerHTML = '<i class="fas fa-sign-out-alt"></i> Cerrar Sesión';
            }
        }
    }

    // Ajustar layout inicial
    adjustLayout();
});