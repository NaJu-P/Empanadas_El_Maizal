// profile-manager.js - Gestor centralizado de perfil de usuario

class ProfileManager {
    constructor() {
        this.apiBaseUrl = '/api/profile';
        this.init();
    }

    init() {
        // Inicializar eventos cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupEventListeners());
        } else {
            this.setupEventListeners();
        }
    }

    setupEventListeners() {
        // Elementos del DOM
        this.userIcon = document.getElementById('user-icon');
        this.dropdownMenu = document.getElementById('dropdown-menu');
        this.profileLink = document.getElementById('profile-link');
        this.profileModal = document.getElementById('profile-modal');
        this.profileForm = document.getElementById('profile-form');
        this.closeModalBtn = document.getElementById('close-profile-modal');

        // Verificar que los elementos existen
        if (!this.profileModal || !this.profileForm) {
            console.warn('Elementos del perfil no encontrados en esta página');
            return;
        }

        // Event listeners
        this.userIcon?.addEventListener('click', () => this.toggleDropdown());
        this.userIcon?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.toggleDropdown();
            }
        });

        this.profileLink?.addEventListener('click', (e) => {
            e.preventDefault();
            this.openProfileModal();
        });

        this.closeModalBtn?.addEventListener('click', () => this.closeProfileModal());
        this.profileForm?.addEventListener('submit', (e) => this.handleProfileSubmit(e));

        // Cerrar modal al hacer click fuera
        this.profileModal?.addEventListener('click', (e) => {
            if (e.target === this.profileModal) {
                this.closeProfileModal();
            }
        });

        // Cerrar dropdown al hacer click fuera
        document.addEventListener('click', (e) => {
            if (!this.userIcon?.contains(e.target) && !this.dropdownMenu?.contains(e.target)) {
                this.hideDropdown();
            }
        });

        // Cargar datos del perfil al inicializar
        this.loadProfile();
    }

    toggleDropdown() {
        if (this.dropdownMenu?.classList.contains('hidden')) {
            this.showDropdown();
        } else {
            this.hideDropdown();
        }
    }

    showDropdown() {
        this.dropdownMenu?.classList.remove('hidden');
        this.userIcon?.setAttribute('aria-expanded', 'true');
    }

    hideDropdown() {
        this.dropdownMenu?.classList.add('hidden');
        this.userIcon?.setAttribute('aria-expanded', 'false');
    }

    async openProfileModal() {
        this.hideDropdown();
        await this.loadProfile(); // Cargar datos actuales
        this.profileModal?.classList.remove('hidden');
        
        // Animación de entrada
        setTimeout(() => {
            const modalContent = this.profileModal?.querySelector('[role="document"]');
            modalContent?.classList.remove('scale-95', 'opacity-0');
            modalContent?.classList.add('scale-100', 'opacity-100');
        }, 10);

        // Focus en el primer input
        const firstInput = this.profileForm?.querySelector('input');
        firstInput?.focus();
    }

    closeProfileModal() {
        const modalContent = this.profileModal?.querySelector('[role="document"]');
        modalContent?.classList.remove('scale-100', 'opacity-100');
        modalContent?.classList.add('scale-95', 'opacity-0');
        
        setTimeout(() => {
            this.profileModal?.classList.add('hidden');
        }, 300);
    }

    async loadProfile() {
        try {
            this.showLoading(true);
            const response = await fetch(`${this.apiBaseUrl}/get`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
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

    populateForm(userData) {
        const fields = {
            'profile-name': userData.nombre_usuario,
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
                },
                credentials: 'same-origin',
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.showNotification('Perfil actualizado correctamente', 'success');
                this.closeProfileModal();
            } else {
                this.showNotification(data.message || 'Error al actualizar el perfil', 'error');
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
            nombre_usuario: document.getElementById('profile-name')?.value?.trim() || '',
            email_usuario: document.getElementById('profile-email')?.value?.trim() || '',
            telefono: document.getElementById('profile-phone')?.value?.trim() || '',
            direccion_usuario: document.getElementById('profile-address')?.value?.trim() || ''
        };
    }

    validateForm(formData) {
        const errors = [];

        // Validar nombre
        if (!formData.nombre_usuario || formData.nombre_usuario.length < 2) {
            errors.push('El nombre debe tener al menos 2 caracteres');
        }

        // Validar email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!formData.email_usuario || !emailRegex.test(formData.email_usuario)) {
            errors.push('El email no tiene un formato válido');
        }

        // Validar teléfono (opcional pero si se proporciona, debe ser válido)
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
        // Remover notificación existente
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

        // Animación de entrada
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);

        // Auto remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.add('translate-x-full');
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }
}

// Inicializar el gestor de perfil automáticamente
let profileManager;
if (typeof window !== 'undefined') {
    profileManager = new ProfileManager();
}

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProfileManager;
}