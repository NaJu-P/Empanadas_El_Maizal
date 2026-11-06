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

document.getElementById("registroForm").addEventListener("submit", function(event) {
  event.preventDefault();

  const nombre = document.getElementById("nombre").value.trim();
  const telefono = document.getElementById("telefono").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;

  if (nombre === "") {
    alert("Por favor, ingresa tu nombre completo.");
    return;
  }

  if (telefono.length < 7 || isNaN(telefono)) {
    alert("Por favor, ingresa un número de teléfono válido (mínimo 7 dígitos).");
    return;
  }

  if (!emailRegex.test(email)) {
    alert("Por favor, ingresa un correo electrónico válido.");
    return;
  }

  if (password.length < 6) {
    alert("La contraseña debe tener al menos 6 caracteres.");
    return;
  }

  alert("Registro exitoso. ¡Bienvenido, " + nombre + "!");
  // Simula redirección o envío de datos
  // window.location.href = "bienvenida.html";

  document.querySelector('.password-toggle').addEventListener('click', function() {
    togglePassword('password');
  });

});