window.addEventListener('pageshow', function (event) {
    if (event.persisted || window.performance && performance.getEntriesByType("navigation")[0].type === "back_forward") {
        window.location.reload(); // Recarga sin caché
    }
});

class DomiciliarioManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    // ==================== EVENTOS ====================
    
    setupEventListeners() {
        document.addEventListener('click', this.handleClicks.bind(this));
        document.addEventListener('submit', this.handleSubmits.bind(this));
    }

    handleClicks(e) {
        const target = e.target;

        if (target.matches('#logoutBtn, .logout-btn')) {
            this.handleLogout();
        }

        if (target.matches('.btn-close')) {
            target.closest('.alert-custom')?.remove();
        }
    }

    handleSubmits(e) {
        const form = e.target;

        // Marcar como entregado
        if (form.matches('form[action*="actualizar_estado_entrega"]')) {
            const confirmado = confirm('¿Confirma que este pedido ha sido entregado?');
            if (!confirmado) {
                e.preventDefault();
            }
        }

        // Registro
        if (form.matches('#registerForm')) {
            e.preventDefault();
            this.handleRegister(form);
        }

        // Login
        if (form.matches('#loginForm')) {
            e.preventDefault();
            this.handleLogin(form);
        }
    }

    // ==================== REGISTRO / LOGIN ====================

    async handleRegister(form) {
        const submitBtn = form.querySelector('button[type="submit"]');

        if (!this.validateForm(form)) return;

        try {
            this.setLoading(submitBtn, true);

            const response = await this.fetchAPI('/domiciliarios/register', {
                method: 'POST',
                body: new FormData(form)
            });

            if (response.success) {
                this.showMessage('success', response.message);
                this.showCodigoUnico(response.codigo_unico);
                setTimeout(() => window.location.href = response.redirect, 3000);
            } else {
                this.showMessage('error', response.message);
                this.displayValidationErrors(response.errors);
            }
        } catch (error) {
            this.handleError(error, 'Error en registro');
        } finally {
            this.setLoading(submitBtn, false);
        }
    }

    async handleLogin(form) {
        const submitBtn = form.querySelector('button[type="submit"]');

        try {
            this.setLoading(submitBtn, true);

            const response = await this.fetchAPI('/domiciliarios/authenticate', {
                method: 'POST',
                body: new FormData(form)
            });

            if (response.success) {
                this.showMessage('success', response.message);
                setTimeout(() => window.location.href = response.redirect, 1000);
            } else {
                this.showMessage('error', response.message);
                this.highlightErrorField(response.error_field);
            }
        } catch (error) {
            this.handleError(error, 'Error en login');
        } finally {
            this.setLoading(submitBtn, false);
        }
    }

    async handleLogout() {
        try {
            const response = await this.fetchAPI('/domiciliarios/logout', { method: 'POST' });
            if (response.success) {
                this.showMessage('success', response.message);
                setTimeout(() => window.location.href = response.redirect, 1000);
            }
        } catch (error) {
            window.location.href = '/domiciliarios/login';
        }
    }

    // ==================== UTILIDADES ====================

    async fetchAPI(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        const response = await fetch(url, { ...defaultOptions, ...options });
        return await response.json();
    }

    handleError(error, message) {
        console.error(message + ':', error);
        this.showMessage('error', message + '. Intenta nuevamente.');
    }

    showMessage(type, message) {
        // Elimina alertas anteriores
        document.querySelectorAll('.alert-custom').forEach(alert => alert.remove());

        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const icon = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert ${alertClass} alert-dismissible fade show alert-custom`;
        alertDiv.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 9999;
            min-width: 300px; max-width: 500px;
        `;
        alertDiv.innerHTML = `
            <i class="${icon} me-2"></i>${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()">×</button>
        `;

        document.body.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }

    setLoading(button, isLoading) {
        if (!button) return;
        if (isLoading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || 'Enviar';
        }
    }

    validateForm(form) {
        const inputs = form.querySelectorAll('input[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showFieldError(input, 'Este campo es obligatorio');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });

        return isValid;
    }

    showFieldError(element, message) {
        this.clearFieldError(element);
        element.classList.add('is-invalid');

        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        element.parentNode.appendChild(errorDiv);
    }

    clearFieldError(element) {
        element.classList.remove('is-invalid');
        const errorDiv = element.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) errorDiv.remove();
    }

    displayValidationErrors(errors) {
        if (!errors) return;

        Object.entries(errors).forEach(([field, message]) => {
            const element = document.getElementById(field);
            if (element) this.showFieldError(element, message);
        });
    }

    highlightErrorField(fieldName) {
        if (!fieldName) return;

        const field = document.getElementById(fieldName);
        if (field) {
            field.classList.add('is-invalid');
            field.focus();
        }
    }

    showCodigoUnico(codigo) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2><i class="fas fa-key"></i> ¡Registro Exitoso!</h2>
                    <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <p>Tu código único de domiciliario es:</p>
                    <div class="codigo-display">${codigo}</div>
                    <p class="warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>¡IMPORTANTE!</strong> Guarda este código en un lugar seguro.
                    </p>
                </div>
                <div class="modal-footer">
                    <button class="btn-primary" onclick="this.closest('.modal-overlay').remove()">
                        <i class="fas fa-check"></i> Entendido
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    window.domiciliarioManager = new DomiciliarioManager();
});
