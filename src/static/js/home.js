// FUNCIÓN DE VERIFICACIÓN DE SESIÓN MEJORADA
function checkSessionStatus(redirectTo = '/Home') {
    if (isFromLogout()) {
        console.log('No redirigir porque venimos de logout');
        window.history.replaceState({}, document.title, "/Home");
        return Promise.resolve(false);
    }

    return fetch('/api/usuario/actual', {
        method: 'GET',
        credentials: 'same-origin',
        cache: 'no-cache',
        headers: {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    }).then(response => {
        if (response.status !== 200) {
            console.log('Sesión inválida');
            // Solo redirigir si no estamos en home y es una página protegida
            if (isProtectedPage()) {
                console.log('Redirigiendo a:', redirectTo);
                window.location.replace(redirectTo);
            }
            return false;
        }
        return true;
    }).catch(error => {
        console.error('Error verificando sesión:', error);
        // Solo redirigir si no estamos en home y es una página protegida
        if (isProtectedPage()) {
            window.location.replace(redirectTo);
        }
        return false;
    });
}

// FUNCIÓN PARA DETERMINAR QUÉ PÁGINAS REQUIEREN AUTENTICACIÓN
function isProtectedPage() {
    const currentPath = window.location.pathname.toLowerCase();

    // Detectar si estamos en la versión privada de opiniones
    if (currentPath.includes('/opiniones')) {
        const params = new URLSearchParams(window.location.search);
        return params.get('privado') === 'true';
    }

    const protectedPaths = [
        '/carrito',
        '/comprobante',
        '/tus-comprobantes',
        '/metodo-pago',
        '/profile',
        '/domiciliario'
    ];

    return protectedPaths.some(path => currentPath.includes(path));
}

// FUNCIÓN PARA VERIFICAR SI ESTAMOS EN HOME
function isHomePage() {
    const homePaths = ['/', '/Home', '/index'];
    const currentPath = window.location.pathname.toLowerCase();
    return homePaths.includes(currentPath) || currentPath === '';
}

// FUNCIÓN PARA VERIFICAR SI VENIMOS DE LOGOUT
function isFromLogout() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.has('logout_success');
}

// VERIFICACIÓN INICIAL DE SESIÓN MEJORADA
function initialSessionCheck() {
    // Si venimos de logout, no verificar sesión para evitar redirección
    if (isFromLogout()) {
        console.log('Venimos de logout, limpiando UI sin verificar sesión');
        clearUserUI();

        window.history.replaceState({}, document.title, "/Home");
        return;
    }
    
    if (isProtectedPage()) {
        // Página protegida: verificar sesión y redirigir al login si no está autenticado
        checkSessionStatus('/Home');
    } else if (isHomePage()) {
        // Página home: verificar sesión pero NO redirigir, solo actualizar UI
        checkSessionStatus().then(isValid => {
            if (!isValid) {
                // Usuario no autenticado en home, mostrar versión sin sesión
                console.log('Usuario no autenticado en home, mostrando versión sin sesión');
                clearUserUI();
                showHomeWithoutSession();
            } else {
                // Usuario autenticado en home, mostrar versión con sesión
                console.log('Usuario autenticado en home, mostrando versión con sesión');
                showHomeWithSession();
            }
        }).catch(() => {
            console.log('Error verificando sesión en home, mostrando versión sin sesión');
            clearUserUI();
            showHomeWithoutSession();
        });
    }
}

// FUNCIÓN PARA MOSTRAR HOME SIN SESIÓN
function showHomeWithoutSession() {
    console.log('Mostrando home sin sesión');
    // Aquí puedes agregar cualquier lógica adicional específica para home sin sesión
    // Por ejemplo, mostrar elementos específicos, ocultar otros, etc.
    
    // Ejemplo: Mostrar elementos específicos para usuarios no autenticados
    const guestElements = document.querySelectorAll('.guest-only');
    guestElements.forEach(el => el.style.display = 'block');
    
    const userElements = document.querySelectorAll('.user-only');
    userElements.forEach(el => el.style.display = 'none');
}

// FUNCIÓN PARA MOSTRAR HOME CON SESIÓN
function showHomeWithSession() {
    console.log('Mostrando home con sesión');
    // Aquí puedes agregar cualquier lógica adicional específica para home con sesión
    
    // Ejemplo: Mostrar elementos específicos para usuarios autenticados
    const userElements = document.querySelectorAll('.user-only');
    userElements.forEach(el => el.style.display = 'block');
    
    const guestElements = document.querySelectorAll('.guest-only');
    guestElements.forEach(el => el.style.display = 'none');
}

// FUNCIÓN PARA LIMPIAR UI DE USUARIO LOGUEADO
function clearUserUI() {
    const userIcon = document.getElementById('user-icon');
    const dropdownMenu = document.getElementById('dropdown-menu');
    
    if (userIcon) {
        userIcon.style.display = 'none';
    }
    if (dropdownMenu) {
        dropdownMenu.classList.add('hidden');
    }
    
    // Mostrar botones de login/registro si existen
    const loginButtons = document.querySelectorAll('.login-button, .register-button');
    loginButtons.forEach(button => {
        button.style.display = 'block';
    });
}

// EJECUTAR VERIFICACIÓN INICIAL
initialSessionCheck();

// MANEJO MEJORADO DEL CACHÉ Y NAVEGACIÓN
window.addEventListener('pageshow', function (event) {
    console.log('Page show event:', event.persisted);
    
    // Si venimos de logout, no verificar sesión
    if (isFromLogout()) {
        console.log('Pageshow: Venimos de logout, solo limpiando UI');
        clearUserUI();
        showHomeWithoutSession();
        window.history.replaceState({}, document.title, "/Home");
        return;
    }
    
    if (event.persisted || performance.navigation.type === 2) {
        // Página viene del caché (navegación hacia atrás/adelante)
        console.log('Página cargada desde caché, verificando sesión...');
        
        if (isProtectedPage()) {
            checkSessionStatus('/Home');
        } else if (isHomePage()) {
            // En home, verificar sesión pero NO redirigir
            checkSessionStatus().then(isValid => {
                if (!isValid) {
                    clearUserUI();
                    showHomeWithoutSession();
                    console.log('Usuario no autenticado en home, UI limpiada y versión sin sesión mostrada');
                } else {
                    showHomeWithSession();
                    console.log('Usuario autenticado en home, versión con sesión mostrada');
                }
            }).catch(() => {
                clearUserUI();
                showHomeWithoutSession();
            });
        }
    }
});

// MANEJO DEL BOTÓN ATRÁS DEL NAVEGADOR
window.addEventListener('popstate', function(event) {
    console.log('Popstate event detected');
    
    // Si venimos de logout, no verificar sesión
    if (isFromLogout()) {
        console.log('Popstate: Venimos de logout, solo limpiando UI');
        clearUserUI();
        showHomeWithoutSession();
        window.history.replaceState({}, document.title, "/Home");
        return;
    }
    
    // Pequeño delay para permitir que la URL se actualice
    setTimeout(() => {
        if (isProtectedPage()) {
            checkSessionStatus('/Home');
        } else if (isHomePage()) {
            checkSessionStatus().then(isValid => {
                if (!isValid) {
                    clearUserUI();
                    showHomeWithoutSession();
                } else {
                    showHomeWithSession();
                }
            }).catch(() => {
                clearUserUI();
                showHomeWithoutSession();
            });
        }
    }, 100);
});

// MANEJO DE VISIBILIDAD DE LA PÁGINA
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        console.log('Página visible, verificando sesión...');
        
        // Si venimos de logout, no verificar sesión
        if (isFromLogout()) {
            console.log('Visibilitychange: Venimos de logout, solo limpiando UI');
            clearUserUI();
            showHomeWithoutSession();
            window.history.replaceState({}, document.title, "/Home");
            return;
        }
        
        if (isProtectedPage()) {
            checkSessionStatus('/Home');
        } else if (isHomePage()) {
            checkSessionStatus().then(isValid => {
                if (!isValid) {
                    clearUserUI();
                    showHomeWithoutSession();
                } else {
                    showHomeWithSession();
                }
            }).catch(() => {
                clearUserUI();
                showHomeWithoutSession();
            });
        }
    }
});

// VERIFICACIÓN PERIÓDICA DE SESIÓN (solo en páginas protegidas)
let sessionCheckInterval;
function startSessionMonitoring() {
    if (isProtectedPage()) {
        sessionCheckInterval = setInterval(() => {
            checkSessionStatus('/Home');
        }, 5 * 60 * 1000); // Cada 5 minutos
    }
}

function stopSessionMonitoring() {
    if (sessionCheckInterval) {
        clearInterval(sessionCheckInterval);
        sessionCheckInterval = null;
    }
}

// PREVENIR CACHÉ DEL NAVEGADOR PARA PÁGINAS PROTEGIDAS
window.addEventListener('beforeunload', function() {
    stopSessionMonitoring();
});

document.addEventListener('DOMContentLoaded', () => {
    // Iniciar monitoreo solo si es página protegida
    if (isProtectedPage()) {
        startSessionMonitoring();
    }

    class ProfileManager {
        constructor() {
            this.apiBaseUrl = '/api/profile';
            this.init();
        }

        init() {
            this.setupEventListeners();
        }

        setupEventListeners() {
            // Elementos del DOM
            this.userIcon = document.getElementById('user-icon');
            this.dropdownMenu = document.getElementById('dropdown-menu');
            this.profileLink = document.getElementById('profile-link');
            this.logoutLink = document.getElementById('logout-link');
            this.profileModal = document.getElementById('profile-modal');
            this.profileForm = document.getElementById('profile-form');
            this.closeModalBtn = document.getElementById('close-profile-modal');

            // Verificar que los elementos existen
            if (!this.profileModal || !this.profileForm) {
                console.warn('Elementos del perfil no encontrados en esta página');
                return;
            }

            // Event listeners para el dropdown
            this.userIcon?.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });

            this.userIcon?.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    e.stopPropagation();
                    this.toggleDropdown();
                }
            });

            // Event listener para abrir el perfil
            this.profileLink?.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.openProfileModal();
            });

            // Event listener para logout MEJORADO
            this.logoutLink?.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogout();
            });

            // Resto de event listeners...
            this.closeModalBtn?.addEventListener('click', () => this.closeProfileModal());
            this.profileForm?.addEventListener('submit', (e) => this.handleProfileSubmit(e));

            this.profileModal?.addEventListener('click', (e) => {
                if (e.target === this.profileModal) {
                    this.closeProfileModal();
                }
            });

            document.addEventListener('click', (e) => {
                if (!this.userIcon?.contains(e.target) && 
                    !this.dropdownMenu?.contains(e.target)) {
                    this.hideDropdown();
                }
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && !this.profileModal?.classList.contains('hidden')) {
                    this.closeProfileModal();
                }
            });

            // Solo cargar perfil si el usuario está autenticado Y no venimos de logout
            if (!isFromLogout()) {
                this.loadProfileIfAuthenticated();
            }
        }

        async loadProfileIfAuthenticated() {
            try {
                const sessionValid = await checkSessionStatus();
                if (sessionValid) {
                    this.loadProfile();
                }
            } catch (error) {
                console.log('Usuario no autenticado, no se carga el perfil');
            }
        }

        toggleDropdown() {
            if (this.dropdownMenu?.classList.contains('hidden')) {
                this.showDropdown();
            } else {
                this.hideDropdown();
            }
        }

        showDropdown() {
            if (this.dropdownMenu) {
                this.dropdownMenu.classList.remove('hidden');
                this.userIcon?.setAttribute('aria-expanded', 'true');
            }
        }

        hideDropdown() {
            if (this.dropdownMenu) {
                this.dropdownMenu.classList.add('hidden');
                this.userIcon?.setAttribute('aria-expanded', 'false');
            }
        }

        async openProfileModal() {
            const sessionValid = await checkSessionStatus('/Home');
            if (!sessionValid) {
                return;
            }
            
            this.hideDropdown();
            
            if (this.profileModal) {
                this.profileModal.classList.remove('hidden');
                await this.loadProfile();
                
                setTimeout(() => {
                    const modalContent = this.profileModal.querySelector('[role="document"]');
                    if (modalContent) {
                        modalContent.classList.remove('scale-95', 'opacity-0');
                        modalContent.classList.add('scale-100', 'opacity-100');
                    }
                }, 10);

                setTimeout(() => {
                    const firstInput = this.profileForm?.querySelector('input');
                    firstInput?.focus();
                }, 100);
            }
        }

        closeProfileModal() {
            const modalContent = this.profileModal?.querySelector('[role="document"]');
            if (modalContent) {
                modalContent.classList.remove('scale-100', 'opacity-100');
                modalContent.classList.add('scale-95', 'opacity-0');
            }
            
            setTimeout(() => {
                this.profileModal?.classList.add('hidden');
            }, 300);
        }

        // LOGOUT MEJORADO - SIEMPRE REDIRIGIR AL HOME CON PARÁMETRO
        async handleLogout() {
            const confirmMessage = '¿Estás seguro de que quieres cerrar sesión?';
                
            if (confirm(confirmMessage)) {
                try {
                    stopSessionMonitoring();
                    
                    const response = await fetch('/auth/logout', {
                        method: 'POST',
                        credentials: 'same-origin',
                        headers: {
                            'Cache-Control': 'no-cache',
                            'Pragma': 'no-cache',
                            'Content-Type': 'application/json'
                        }
                    });

                    // Limpiar caché si está disponible
                    if ('caches' in window) {
                        caches.keys().then(names => {
                            names.forEach(name => {
                                caches.delete(name);
                            });
                        });
                    }
                    
                    console.log('Logout exitoso, redirigiendo al home...');
                    
                    // SIEMPRE redirigir al home con parámetro de logout
                    window.location.replace('/Home');
                    
                } catch (error) {
                    console.error('Error durante logout:', error);
                    // Aún así redirigir al home
                    window.location.replace('/Home');
                }
            }
        }

        // MÉTODO MEJORADO para cargar perfil que verifica logout
        async loadProfile() {
            if (isFromLogout()) {
                console.log('Venimos de logout, no cargando perfil');
                return;
            }

            try {
                this.showLoading(true);
                const response = await fetch(`${this.apiBaseUrl}/get`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                if (!response.ok) {
                    if (response.status === 401 || response.status === 403) {
                        // Cambiar esta parte:
                        if (isHomePage()) {
                            clearUserUI();
                            showHomeWithoutSession();
                        }
                        // Evitar redirección
                        return;
                    }
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                if (data.success) {
                    this.populateForm(data.user);
                } else {
                    this.showNotification('Error al cargar el perfil: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('Error cargando perfil:', error);
                this.showNotification('Error de conexión al cargar el perfil', 'error');
            } finally {
                this.showLoading(false);
            }
        }

        // Resto de métodos sin cambios...
        populateForm(userData) {
            const fields = {
                'profile-name': userData.nombres_usuario,
                'profile-email': userData.email_usuario,
                'profile-phone': userData.telefono,
                'profile-address': userData.direccion_usuario
            };

            Object.entries(fields).forEach(([fieldId, value]) => {
                const field = document.getElementById(fieldId);
                if (field && value !== undefined && value !== null) {
                    field.value = value;
                }
            });
        }

        async handleProfileSubmit(event) {
            event.preventDefault();
            
            const sessionValid = await checkSessionStatus('/Home');
            if (!sessionValid) {
                return;
            }
            
            const formData = this.getFormData();
            if (!this.validateForm(formData)) {
                return;
            }

            try {
                this.showLoading(true);
                
                const response = await fetch(`${this.apiBaseUrl}/update`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache'
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(formData)
                });

                if (!response.ok) {
                    if (response.status === 401 || response.status === 403) {
                        window.location.replace('/Home');
                        return;
                    }
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.success) {
                    this.showNotification('Perfil actualizado correctamente', 'success');
                    this.closeProfileModal();
                } else {
                    this.showNotification('Error al actualizar: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('Error actualizando perfil:', error);
                this.showNotification('Error de conexión al actualizar el perfil', 'error');
            } finally {
                this.showLoading(false);
            }
        }

        getFormData() {
            return {
                nombres_usuario: document.getElementById('profile-name')?.value?.trim() || '',
                email_usuario: document.getElementById('profile-email')?.value?.trim() || '',
                telefono: document.getElementById('profile-phone')?.value?.trim() || '',
                direccion_usuario: document.getElementById('profile-address')?.value?.trim() || ''
            };
        }

        validateForm(formData) {
            const errors = [];

            if (!formData.nombres_usuario || formData.nombres_usuario.length < 2) {
                errors.push('El nombre debe tener al menos 2 caracteres');
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!formData.email_usuario || !emailRegex.test(formData.email_usuario)) {
                errors.push('El email no tiene un formato válido');
            }

            if (formData.telefono) {
                const phoneRegex = /^[0-9+\-\s()]{7,15}$/;
                if (!phoneRegex.test(formData.telefono)) {
                    errors.push('El teléfono no tiene un formato válido');
                }
            }

            if (errors.length > 0) {
                this.showNotification(errors.join('<br>'), 'error');
                return false;
            }

            return true;
        }

        showLoading(show) {
            const submitBtn = this.profileForm?.querySelector('button[type="submit"]');
            if (!submitBtn) return;

            if (show) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
            } else {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Guardar Cambios';
            }
        }

        showNotification(message, type = 'info') {
            const existing = document.querySelector('.profile-notification');
            if (existing) {
                existing.remove();
            }

            const notification = document.createElement('div');
            notification.className = `profile-notification fixed top-4 right-4 p-4 rounded-md shadow-lg z-50 max-w-sm transition-all duration-300 transform translate-x-full`;
            
            const bgColor = type === 'success' ? 'bg-green-500' : 
                        type === 'error' ? 'bg-red-500' : 'bg-blue-500';
            
            notification.className += ` ${bgColor} text-white`;
            notification.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <p class="text-sm font-medium">${message}</p>
                    </div>
                    <button onclick="this.parentElement.parentElement.remove()" class="ml-3 text-white hover:text-gray-200">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;

            document.body.appendChild(notification);

            setTimeout(() => {
                notification.classList.remove('translate-x-full');
            }, 100);

            setTimeout(() => {
                if (notification.parentElement) {
                    notification.classList.add('translate-x-full');
                    setTimeout(() => notification.remove(), 300);
                }
            }, 5000);
        }
    }

    // Inicializar ProfileManager
    const profileManager = new ProfileManager();
    
    console.log('JavaScript cargado correctamente');
});