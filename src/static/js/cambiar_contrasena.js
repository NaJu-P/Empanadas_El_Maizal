let currentStep = 1;

function toggleMobileNav() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('active');
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

function validateEmail() {
    const email = document.getElementById('email');
    const error = document.getElementById('emailError');
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(email.value)) {
        email.classList.add('error');
        error.textContent = 'Por favor ingresa un email válido';
        error.style.display = 'block';
        return false;
    } else {
        email.classList.remove('error');
        email.classList.add('success');
        error.style.display = 'none';
        return true;
    }
}

function checkPasswordStrength() {
    const password = document.getElementById('newPassword').value;
    const strengthContainer = document.getElementById('passwordStrength');
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');
    
    if (password.length === 0) {
        strengthContainer.style.display = 'none';
        return;
    }
    
    strengthContainer.style.display = 'block';
    
    let strength = 0;
    let feedback = '';
    
    if (password.length >= 8) strength += 25;
    if (password.length >= 12) strength += 10;
    
    if (/[a-z]/.test(password)) strength += 15;
    if (/[A-Z]/.test(password)) strength += 15;
    if (/[0-9]/.test(password)) strength += 15;
    if (/[^A-Za-z0-9]/.test(password)) strength += 20;
    
    strengthFill.style.width = strength + '%';
    
    if (strength < 40) {
        strengthFill.className = 'strength-fill strength-weak';
        feedback = 'Débil';
    } else if (strength < 70) {
        strengthFill.className = 'strength-fill strength-medium';
        feedback = 'Media';
    } else {
        strengthFill.className = 'strength-fill strength-strong';
        feedback = 'Fuerte';
    }
    
    strengthText.textContent = `Fortaleza: ${feedback}`;
    strengthText.style.color = getComputedStyle(strengthFill).backgroundColor;
}

function validatePasswordMatch() {
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword');
    const error = document.getElementById('confirmError');
    const success = document.getElementById('confirmSuccess');
    
    if (newPassword !== confirmPassword.value) {
        confirmPassword.classList.add('error');
        error.textContent = 'Las contraseñas no coinciden';
        error.style.display = 'block';
        success.style.display = 'none';
        return false;
    } else if (confirmPassword.value.length > 0) {
        confirmPassword.classList.remove('error');
        confirmPassword.classList.add('success');
        error.style.display = 'none';
        success.textContent = 'Las contraseñas coinciden';
        success.style.display = 'block';
        return true;
    }
}

function updateStep(step) {
    for (let i = 1; i <= 3; i++) {
        const stepEl = document.getElementById(`step${i}`);
        stepEl.classList.remove('active', 'completed');
    }
    
    for (let i = 1; i < step; i++) {
        document.getElementById(`step${i}`).classList.add('completed');
    }
    document.getElementById(`step${step}`).classList.add('active');
}

function showSuccess() {
    const container = document.getElementById('resetContainer');
    container.innerHTML = `
        <div class="success-state">
            <div class="success-icon">
                <i class="fas fa-check"></i>
            </div>
            <h2 style="color: var(--success-color); margin-bottom: 16px;">¡Contraseña Cambiada!</h2>
            <p style="color: #6C757D; margin-bottom: 32px;">
                Tu contraseña ha sido actualizada exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.
            </p>
            <button class="submit-btn" onclick="goToLogin()">
                <i class="fas fa-sign-in-alt"></i> Ir a Iniciar Sesión
            </button>
        </div>
    `;
    updateStep(3);
}

function handleSubmit(event) {
    event.preventDefault();
    
    const email = validateEmail();
    const passwordMatch = validatePasswordMatch();
    const password = document.getElementById('newPassword').value;
    
    if (!email || !passwordMatch || password.length < 8) {
        return;
    }
    
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    
    updateStep(2);
    
    setTimeout(() => {
        showSuccess();
    }, 2000);
}

function goHome() {
    window.location.href = '#home';
}

function goBack() {
    window.location.href = '#login';
}

function goToLogin() {
    window.location.href = '#login';
}

document.addEventListener('DOMContentLoaded', function() {
    updateStep(1);
});

function showFlashMessage(message, type) {
    const flashContainer = document.getElementById('flashMessages');
    const flashDiv = document.createElement('div');
    flashDiv.className = `flash-message flash-${type}`;
    flashDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        ${message}
    `;
    flashContainer.appendChild(flashDiv);
    
    setTimeout(() => {
        flashDiv.remove();
    }, 5000);
}

function updateSteps(currentStep) {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        if (index < currentStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

function transitionToPasswordChange(userEmail) {
    const tokenSection = document.getElementById('tokenVerificationSection');
    const passwordSection = document.getElementById('passwordChangeSection');
    const userEmailDisplay = document.getElementById('userEmailDisplay');
    
    userEmailDisplay.textContent = userEmail;
    
    tokenSection.style.opacity = '0';
    tokenSection.style.transform = 'translateY(-20px)';
    
    setTimeout(() => {
        tokenSection.style.display = 'none';
        passwordSection.style.display = 'block';
        passwordSection.style.opacity = '0';
        passwordSection.style.transform = 'translateY(20px)';
        
        updateSteps(2);
        
        setTimeout(() => {
            passwordSection.style.opacity = '1';
            passwordSection.style.transform = 'translateY(0)';
        }, 50);
    }, 300);
}

document.addEventListener('DOMContentLoaded', function() {
    const tokenInput = document.getElementById('token_input');
    if (tokenInput) {
        tokenInput.addEventListener('input', function(e) {
            if (this.value.length > 7) {
                this.value = this.value.slice(0, 7);
            }
        });
    }

    const tokenForm = document.getElementById('tokenForm');
    if (tokenForm) {
        tokenForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = document.getElementById('verifyTokenBtn');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verificando...';
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showFlashMessage(data.message, 'success');
                    setTimeout(() => {
                        transitionToPasswordChange(data.user_email);
                    }, 1000);
                } else {
                    showFlashMessage(data.message, 'error');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showFlashMessage('Error de conexión. Inténtalo de nuevo.', 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
    }

    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!validatePasswordMatch()) {
                return false;
            }
            
            const formData = new FormData(this);
            const submitBtn = document.getElementById('changePasswordBtn');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cambiando...';
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showFlashMessage(data.message, 'success');
                    updateSteps(3);
                    
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 2000);
                } else {
                    showFlashMessage(data.message, 'error');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showFlashMessage('Error de conexión. Inténtalo de nuevo.', 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
    }
});