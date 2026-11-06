// ===== FUNCIONES BÁSICAS PARA MODALES =====
function abrirRegistro() {
    document.getElementById("registroModal").style.display = "flex";
}

function cerrarRegistro() {
    document.getElementById("registroModal").style.display = "none";
    limpiarFormularioRegistro();
}

function abrirModal() {
    document.getElementById("loginModal").style.display = "flex";
}

function cerrarModal() {
    document.getElementById("loginModal").style.display = "none";
}

// ===== FUNCIÓN DE REGISTRO (ADAPTADA PARA TU BACKEND) =====
function registrarse() {
    // Obtener valores de los campos (sin ciudad)
    const nombre = document.getElementById('nombre').value.trim();
    const apellido = document.getElementById('apellido').value.trim();
    const correo = document.getElementById('correo').value.trim();
    const telefono = document.getElementById('telefono').value.trim();
    const direccion = document.getElementById('direccion').value.trim();
    const password = document.getElementById('password').value;

    // Validación básica (sin ciudad)
    if (!nombre || !apellido || !correo || !telefono || !direccion || !password) {
        alert("Por favor, completa todos los campos incluyendo la dirección.");
        return;
    }

    if (password.length < 6) {
        alert("La contraseña debe tener al menos 6 caracteres.");
        return;
    }

    // Validar email básico
    if (!correo.includes('@') || !correo.includes('.')) {
        alert("Por favor ingresa un email válido.");
        return;
    }

    // Validar teléfono (solo números)
    if (!/^\d{10}$/.test(telefono)) {
        alert("El teléfono debe tener exactamente 10 dígitos.");
        return;
    }

    // Validar dirección
    if (direccion.length < 10) {
        alert("La dirección debe tener al menos 10 caracteres.");
        return;
    }

    if (direccion.length > 200) {
        alert("La dirección no puede exceder 200 caracteres.");
        return;
    }

    // OPCIÓN 1: Envío simple (sin servidor)
    if (typeof MODO_DESARROLLO !== 'undefined' && MODO_DESARROLLO) {
        alert("Registro exitoso para: " + correo);
        cerrarRegistro();
        return;
    }

    // OPCIÓN 2: Envío al servidor (SIN CIUDAD)
    enviarRegistroAlServidor(nombre, apellido, correo, telefono, direccion, password);
}

// ===== FUNCIÓN DE LOGIN (ADAPTADA) =====
function iniciarSesion() {
    let usuario = document.getElementById("usuario").value;
    let password = document.getElementById("passwordLogin").value;

    if (!usuario || !password) {
        alert("Por favor, completa todos los campos.");
    } else {
        // OPCIÓN 1: Validación simple
        if (typeof MODO_DESARROLLO !== 'undefined' && MODO_DESARROLLO) {
            alert("Inicio de sesión exitoso para: " + usuario);
            cerrarModal();
            return;
        }

        // OPCIÓN 2: Envío al servidor
        enviarLoginAlServidor(usuario, password);
    }
}


async function enviarRegistroAlServidor(nombre, apellido, correo, telefono, direccion, password) {
    const button = document.querySelector('#registroModal .button');
    const textoOriginal = button.textContent;
    
    try {
        // Mostrar estado de carga
        button.disabled = true;
        button.textContent = 'Registrando...';

        // Envío sin campo ciudad
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                nombre: nombre,
                apellidos: apellido,
                email: correo,
                telefono: telefono,
                direccion: direccion,
                ciudad: 'No especificada', // Valor por defecto para evitar conflictos
                password: password,
            })
        });

        // Manejo de respuesta JSON
        const data = await response.json();
        
        if (data.success) {
            alert(data.message || "Registro exitoso para: " + correo);
            cerrarRegistro();
            
            // Si hay redirección, úsala
            if (data.redirect) {
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1500);
            }
        } else {
            alert(data.message || "Error en el registro. Intenta nuevamente.");
        }
    } catch (error) {
        console.error('Error:', error);
        alert("Error de conexión. Verifica tu conexión a internet.");
    } finally {
        // Restaurar botón
        button.disabled = false;
        button.textContent = textoOriginal;
    }
}

async function enviarLoginAlServidor(usuario, password) {
    const button = document.querySelector('#loginModal .button');
    const textoOriginal = button.textContent;
    
    try {
        // Mostrar estado de carga
        button.disabled = true;
        button.textContent = 'Ingresando...';

        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                email: usuario,
                password: password
            })
        });

        // Manejo de respuesta JSON
        const data = await response.json();
        
        if (data.success) {
            alert(data.message || "Inicio de sesión exitoso para: " + usuario);
            cerrarModal();
            
            // Si hay redirección, úsala
            if (data.redirect) {
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1500);
            }
        } else {
            alert(data.message || "Credenciales incorrectas. Intenta nuevamente.");
        }
    } catch (error) {
        console.error('Error:', error);
        alert("Error de conexión. Verifica tu conexión a internet.");
    } finally {
        // Restaurar botón
        button.disabled = false;
        button.textContent = textoOriginal;
    }
}

// ===== FUNCIONES AUXILIARES =====
function limpiarFormularioRegistro() {
    const campos = ['nombre', 'apellido', 'correo', 'telefono', 'direccion', 'password']; // Sin 'ciudad'
    campos.forEach(campoId => {
        const campo = document.getElementById(campoId);
        if (campo) {
            campo.value = '';
            campo.style.borderColor = '';
        }
    });

    // Remover mensajes de error
    const errorMessage = document.querySelector('#registroModal .error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
}
// ===== CONFIGURACIÓN MODO DESARROLLO =====
// Descomenta la siguiente línea para usar modo desarrollo (sin servidor)
// const MODO_DESARROLLO = true;

// ===== VALIDACIONES EN TIEMPO REAL (OPCIONALES) =====
document.addEventListener('DOMContentLoaded', function() {
    // Validar teléfono mientras se escribe
    const telefonoInput = document.getElementById('telefono');
    if (telefonoInput) {
        telefonoInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
            if (this.value.length > 10) {
                this.value = this.value.slice(0, 10);
            }
        });
    }
});

// ===== FUNCIONES ADICIONALES PARA MEJORAR UX =====
function mostrarTerminos() {
    alert("Aquí se mostrarían los términos y condiciones.");
}

function mostrarLogin() {
    cerrarRegistro();
    abrirModal();
}

function mostrarRegistro() {
    cerrarModal();
    abrirRegistro();
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.nextElementSibling;
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}