// ===== FUNCIONES PARA REGISTRO DE DOMICILIARIOS =====
window.addEventListener('pageshow', function (event) {
    if (event.persisted || window.performance && performance.getEntriesByType("navigation")[0].type === "back_forward") {
        window.location.reload(); // Recarga sin caché
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registroForm');
    if (form) {
        form.addEventListener('submit', registrarDomiciliario);
        setupValidacionesTiempoReal();
    }

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', loginDomiciliario);
    }
});

// ===== FUNCIÓN PRINCIPAL DE REGISTRO =====
async function registrarDomiciliario(e) {
    e.preventDefault();

    const cedula = document.getElementById('cedula').value.trim();
    const nombre = document.getElementById('nombre').value.trim();
    const telefono = document.getElementById('telefono').value.trim();
    const email = document.getElementById('email').value.trim().toLowerCase();
    const password = document.getElementById('password').value;

    if (!validarFormulario(cedula, nombre, telefono, email, password)) {
        return;
    }

    await enviarRegistroDomiciliario(cedula, nombre, telefono, email, password);
}

// ===== VALIDACIONES DEL FORMULARIO =====
function validarFormulario(cedula, nombre, telefono, email, password) {
    limpiarErrores();
    let esValido = true;

    // Validación de cédula
    if (!cedula || cedula.length < 7) {
        mostrarError('cedula', 'La cédula debe tener al menos 7 dígitos');
        esValido = false;
    } else if (cedula.length > 10) {
        mostrarError('cedula', 'La cédula no puede exceder 10 dígitos');
        esValido = false;
    } else if (!/^\d+$/.test(cedula)) {
        mostrarError('cedula', 'La cédula solo puede contener números');
        esValido = false;
    }

    // Validación de nombre
    if (!nombre || nombre.length < 3) {
        mostrarError('nombre', 'El nombre debe tener al menos 3 caracteres');
        esValido = false;
    } else if (nombre.length > 100) {
        mostrarError('nombre', 'El nombre no puede exceder 100 caracteres');
        esValido = false;
    } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(nombre)) {
        mostrarError('nombre', 'El nombre solo puede contener letras y espacios');
        esValido = false;
    }

    // Validación de teléfono
    if (!/^\d{10}$/.test(telefono)) {
        mostrarError('telefono', 'El teléfono debe tener exactamente 10 dígitos');
        esValido = false;
    }

    // Validación de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        mostrarError('email', 'Formato de email inválido');
        esValido = false;
    }

    // Validación de password
    if (password.length < 6) {
        mostrarError('password', 'La contraseña debe tener al menos 6 caracteres');
        esValido = false;
    } else if (password.length > 50) {
        mostrarError('password', 'La contraseña no puede exceder 50 caracteres');
        esValido = false;
    } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(password)) {
        mostrarError('password', 'La contraseña debe contener al menos una letra y un número');
        esValido = false;
    }

    return esValido;
}

// ===== ENVÍO AL SERVIDOR (REGISTRO) =====
async function enviarRegistroDomiciliario(cedula, nombre, telefono, email, password) {
    const submitButton = document.querySelector('input[type="submit"]');
    const textoOriginal = submitButton.value;

    try {
        submitButton.disabled = true;
        submitButton.value = 'Registrando...';
        submitButton.style.opacity = '0.7';

        const response = await fetch('/domiciliarios/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                cedula,
                nombre,
                telefono,
                email,
                password
            })
        });

        const data = await response.json();

        if (data.success) {
            mostrarMensajeExito(data.message);
            limpiarFormulario();
            setTimeout(() => {
                window.location.href = data.redirect || '/domiciliarios/login';
            }, 5000);
        } else {
            mostrarMensajeError(data.message || 'Error en el registro.');
            if (data.errors) {
                Object.keys(data.errors).forEach(campo => {
                    mostrarError(campo, data.errors[campo]);
                });
            }
        }

    } catch (error) {
        console.error('Error:', error);
        mostrarMensajeError('Error de conexión. Intenta nuevamente.');
    } finally {
        submitButton.disabled = false;
        submitButton.value = textoOriginal;
        submitButton.style.opacity = '1';
    }
}

// ===== VALIDACIONES EN TIEMPO REAL =====
function setupValidacionesTiempoReal() {
    // Validación en tiempo real para cédula
    const cedulaInput = document.getElementById('cedula');
    if (cedulaInput) {
        cedulaInput.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
            if (this.value.length >= 7 && this.value.length <= 10) {
                this.style.borderColor = '#28a745';
            } else if (this.value.length > 0) {
                this.style.borderColor = '#ffc107';
            } else {
                this.style.borderColor = '';
            }
        });
    }

    const telefonoInput = document.getElementById('telefono');
    if (telefonoInput) {
        telefonoInput.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
            if (this.value.length === 10) this.style.borderColor = '#28a745';
            else if (this.value.length > 0) this.style.borderColor = '#ffc107';
            else this.style.borderColor = '';
        });
    }

    const nombreInput = document.getElementById('nombre');
    if (nombreInput) {
        nombreInput.addEventListener('input', function () {
            this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '').slice(0, 100);
            if (this.value.length >= 3) this.style.borderColor = '#28a745';
            else if (this.value.length > 0) this.style.borderColor = '#ffc107';
            else this.style.borderColor = '';
        });
    }

    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function () {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (emailRegex.test(this.value)) this.style.borderColor = '#28a745';
            else if (this.value.length > 0) this.style.borderColor = '#dc3545';
            else this.style.borderColor = '';
        });
    }

    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            const password = this.value;
            let fuerza = 0;
            if (password.length >= 6) fuerza++;
            if (password.length >= 8) fuerza++;
            if (/[A-Z]/.test(password)) fuerza++;
            if (/[a-z]/.test(password)) fuerza++;
            if (/\d/.test(password)) fuerza++;
            if (/[^A-Za-z0-9]/.test(password)) fuerza++;

            if (fuerza < 2) this.style.borderColor = '#dc3545';
            else if (fuerza < 4) this.style.borderColor = '#ffc107';
            else this.style.borderColor = '#28a745';
        });
    }
}

// ===== LOGIN DOMICILIARIO =====
async function loginDomiciliario(e) {
    e.preventDefault();

    // Obtener los valores del formulario
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    // Validar que los elementos existan
    if (!emailInput || !passwordInput) {
        mostrarMensajeError('Error: Faltan campos en el formulario');
        return;
    }

    const email = emailInput.value.trim().toLowerCase();
    const password = passwordInput.value;

    // Validar que los campos no estén vacíos
    if (!email || !password) {
        mostrarMensajeError('Por favor completa todos los campos');
        return;
    }

    const submitButton = document.querySelector('input[type="submit"]');
    const textoOriginal = submitButton.value;

    try {
        submitButton.disabled = true;
        submitButton.value = 'Iniciando sesión...';
        submitButton.style.opacity = '0.7';

        const response = await fetch('/domiciliarios/authenticate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ 
                email: email, 
                password: password
            })
        });

        const data = await response.json();

        if (data.success) {
            mostrarMensajeExito(data.message || 'Login exitoso');
            setTimeout(() => {
                window.location.href = data.redirect || '/domiciliarios/dashboard';
            }, 1500);
        } else {
            mostrarMensajeError(data.message || 'Error en el login');
        }

    } catch (error) {
        console.error('Error:', error);
        mostrarMensajeError('Error de conexión. Intenta nuevamente.');
    } finally {
        submitButton.disabled = false;
        submitButton.value = textoOriginal;
        submitButton.style.opacity = '1';
    }
}

// ===== LOGOUT DOMICILIARIO =====
async function logoutDomiciliario() {
    try {
        const response = await fetch('/domiciliarios/logout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            window.location.href = data.redirect || '/domiciliarios/login';
        } else {
            mostrarMensajeError('Error cerrando sesión');
        }

    } catch (error) {
        console.error('Error:', error);
        window.location.href = '/domiciliarios/login';
    }
}

// ===== FUNCIÓN PARA MOSTRAR/OCULTAR CONTRASEÑA =====
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const toggle = document.querySelector('.password-toggle');
    
    if (field.type === 'password') {
        field.type = 'text';
        toggle.classList.remove('fa-eye');
        toggle.classList.add('fa-eye-slash');
    } else {
        field.type = 'password';
        toggle.classList.remove('fa-eye-slash');
        toggle.classList.add('fa-eye');
    }
}

// ===== MENSAJES Y ERRORES =====
function mostrarError(campoId, mensaje) {
    const campo = document.getElementById(campoId);
    if (!campo) return;
    const errorPrevio = campo.parentNode.querySelector('.error-message');
    if (errorPrevio) errorPrevio.remove();

    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '12px';
    errorDiv.style.marginTop = '5px';
    errorDiv.textContent = mensaje;

    campo.parentNode.appendChild(errorDiv);
    campo.style.borderColor = '#dc3545';
}

function limpiarErrores() {
    document.querySelectorAll('.error-message').forEach(e => e.remove());
    ['cedula', 'nombre', 'telefono', 'email', 'password'].forEach(id => {
        const campo = document.getElementById(id);
        if (campo) campo.style.borderColor = '';
    });
}

function mostrarMensajeExito(mensaje) {
    const div = crearMensajeGeneral(mensaje, 'success');
    document.body.insertBefore(div, document.body.firstChild);
    setTimeout(() => div.remove(), 8000);
}

function mostrarMensajeError(mensaje) {
    const div = crearMensajeGeneral(mensaje, 'error');
    document.body.insertBefore(div, document.body.firstChild);
    setTimeout(() => div.remove(), 5000);
}

function crearMensajeGeneral(mensaje, tipo) {
    const div = document.createElement('div');
    div.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        max-width: 90%;
        text-align: center;
        ${tipo === 'success' ? 'background-color: #28a745;' : 'background-color: #dc3545;'}
    `;
    div.textContent = mensaje;

    const close = document.createElement('span');
    close.innerHTML = ' ×';
    close.style.cssText = 'margin-left:10px;cursor:pointer;font-size:18px;';
    close.onclick = () => div.remove();
    div.appendChild(close);

    return div;
}

function limpiarFormulario() {
    ['cedula', 'nombre', 'telefono', 'email', 'password'].forEach(id => {
        const campo = document.getElementById(id);
        if (campo) {
            campo.value = '';
            campo.style.borderColor = '';
        }
    });
    limpiarErrores();
}