// Definir Constantes
window.addEventListener('pageshow', function (event) {
    if (event.persisted || window.performance && performance.getEntriesByType("navigation")[0].type === "back_forward") {
        window.location.reload(); // Recarga sin caché
    }
});

const email = document.getElementById("email");
const password = document.getElementById("password");
const form = document.getElementById("form");
const parrafo = document.getElementById("warnings")

//Cuando se envie el formulario o se presione el botón 
form.addEventListener("submit", e => {
    //Prevenir lo del default
    e.preventDefault();
    let regexEmail = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/
    let warnings = "";
    let entrar = false
    if (email.value.length == 0) {
        warnings += 'El campo de Correo electrónico no puede estar vacio <br>';
        entrar = true
    }
    if (email.value.length > 70) {
        warnings += 'El correo electrónico no debe tener más de 70 caracteres <br>';
        entrar = true
    }
    // Validar el email
    console.log(regexEmail.test(email.value))
    if (!regexEmail.test(email.value)) {
        warnings += 'El correo electrónico no es válido <br>';
        entrar = true
    }
    if (password.value.length == 0) {
        warnings += 'La contraseña no puede estar vacia <br>';
        entrar = true
    }
    if (email.value !== 'rodolfarias@gmail.com') {
        warnings += 'El correo electrónico no es válido <br>';
        entrar = true
    }
    if (password.value !== 'rodolfo528') {
        warnings += 'La contraseña no es válida <br>';
        entrar = true
    }
    if (entrar) {
        parrafo.innerHTML = warnings
    } else {
        parrafo.innerHTML = ""
        alert('Bienvenido Administrador')
    }
})

document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flashes li');
    
    if (flashMessages.length > 0) {
        flashMessages.forEach((message, index) => {
            setupFlashMessage(message, index);
        });
    }
    
    function setupFlashMessage(message, index) {
        // Agregar estilos iniciales para la animación
        message.style.opacity = '0';
        message.style.transform = 'translateY(-20px)';
        message.style.transition = 'all 0.5s ease-in-out';
        message.style.cursor = 'pointer';
        message.style.position = 'relative';
        message.style.marginBottom = '10px';
        
        // Agregar botón de cerrar
        const closeButton = document.createElement('span');
        closeButton.innerHTML = '&times;';
        closeButton.style.cssText = `
            position: absolute;
            top: 5px;
            right: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            color: inherit;
            opacity: 0.7;
            transition: opacity 0.2s ease;
        `;
        
        closeButton.addEventListener('mouseenter', function() {
            this.style.opacity = '1';
        });
        
        closeButton.addEventListener('mouseleave', function() {
            this.style.opacity = '0.7';
        });
        
        message.appendChild(closeButton);
        
        // Animar entrada con delay escalonado
        setTimeout(() => {
            message.style.opacity = '1';
            message.style.transform = 'translateY(0)';
        }, 100 * (index + 1));
        
        // Auto-desaparecer después de 5 segundos
        const autoHideTimeout = setTimeout(() => {
            hideMessage(message);
        }, 5000);
        
        // Función para ocultar mensaje
        function hideMessage(msgElement) {
            msgElement.style.opacity = '0';
            msgElement.style.transform = 'translateY(-20px)';
            msgElement.style.maxHeight = msgElement.offsetHeight + 'px';
            
            setTimeout(() => {
                msgElement.style.maxHeight = '0';
                msgElement.style.marginBottom = '0';
                msgElement.style.padding = '0';
            }, 500);
            
            setTimeout(() => {
                msgElement.remove();
            }, 1000);
        }
        
        // Cerrar al hacer clic en el botón X
        closeButton.addEventListener('click', function(e) {
            e.stopPropagation();
            clearTimeout(autoHideTimeout);
            hideMessage(message);
        });
        
        // Cerrar al hacer clic en el mensaje
        message.addEventListener('click', function() {
            clearTimeout(autoHideTimeout);
            hideMessage(message);
        });
        
        // Pausar auto-hide cuando el mouse está encima
        message.addEventListener('mouseenter', function() {
            clearTimeout(autoHideTimeout);
        });
        
        // Reanudar auto-hide cuando el mouse sale
        message.addEventListener('mouseleave', function() {
            const newTimeout = setTimeout(() => {
                hideMessage(message);
            }, 2000);
        });
    }
});