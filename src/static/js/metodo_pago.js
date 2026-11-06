document.addEventListener('DOMContentLoaded', function () {

    // Variables globales
    let selectedPayment = null;
    let selectedElement = null;

    // Inicializar event listeners para métodos de pago
    document.querySelectorAll('.payment-option').forEach(option => {
        option.addEventListener('click', function () {
            selectPayment(option, option.dataset.method);
        });
    });

    // Función para seleccionar método de pago
    function selectPayment(element, method) {
        const payButton = document.getElementById('payButton');

        // Si se hace clic en el mismo elemento, deseleccionar
        if (selectedElement === element) {
            element.classList.remove('selected');
            selectedElement = null;
            selectedPayment = null;
            payButton.disabled = true;
            payButton.innerHTML = 'Selecciona un método de pago';
            payButton.classList.remove('enabled');
            return;
        }

        // Remover selección anterior
        document.querySelectorAll('.payment-option').forEach(option => {
            option.classList.remove('selected');
        });

        // Agregar selección actual
        element.classList.add('selected');
        selectedElement = element;
        selectedPayment = method;
        payButton.disabled = false;
        payButton.innerHTML = `Ya realicé el pago con ${method === 'nequi' ? 'Nequi' : 'Daviplata'} <i class="fas fa-arrow-right"></i>`;
        payButton.classList.add('enabled');
    }

    // Animaciones de entrada
    document.querySelectorAll('.item, .payment-option').forEach((el, index) => {
        el.style.animationDelay = `${index * 0.1}s`;
    });

    // Hacer funciones globales
    window.selectPayment = selectPayment;

    // Función principal para procesar el pago
    window.processPayment = async function () {
        if (!selectedPayment) {
            showAlert('Por favor selecciona un método de pago', 'error');
            return;
        }

        const container = document.getElementById('paymentContainer');
        const payButton = document.getElementById('payButton');

        // Efectos visuales de carga
        container.classList.add('loading');
        payButton.disabled = true;
        payButton.innerHTML = 'Procesando ...';

        try {
            const response = await fetch('/Metodo-pago/procesar-pago', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    metodo_pago: selectedPayment
                })
            });

            const result = await response.json();

            if (result.success) {
                showAlert(result.message, 'success');
                
                // Mantener el delay para mejor UX
                setTimeout(() => {
                    window.location.href = '../Tus-Comprobantes';
                }, 2000);
                
            } else {
                showAlert(result.message, 'error');
                // Rehabilitar botón en caso de errors
                container.classList.remove('loading');
                payButton.disabled = false;
                payButton.innerHTML = `Ya realicé el pago con ${selectedPayment === 'nequi' ? 'Nequi' : 'Daviplata'} <i class="fas fa-arrow-right"></i>`;
            }

        } catch (error) {
            console.error('Error al procesar el pago:', error);
            showAlert('Error de conexión. Por favor intenta nuevamente.', 'error');
            
            // Rehabilitar botón en caso de error
            container.classList.remove('loading');
            payButton.disabled = false;
            payButton.innerHTML = `Ya realicé el pago con ${selectedPayment === 'nequi' ? 'Nequi' : 'Daviplata'} <i class="fas fa-arrow-right"></i>`;
        }
    };

    // Función para volver atrás con confirmación
    window.goBack = function () {
        if (confirm('¿Estás seguro de que quieres volver? Se perderá la información del pedido.')) {
            window.history.back();
        }
    };
});

// Función para mostrar alertas (fuera del DOMContentLoaded)
function showAlert(message, type) {
    // Remover alertas existentes
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // Crear nueva alerta
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.position = 'fixed';
    alert.style.top = '20px';
    alert.style.left = '50%';
    alert.style.transform = 'translateX(-50%)';
    alert.style.zIndex = '9999';
    alert.style.width = '90%';
    alert.style.maxWidth = '500px';
    alert.innerHTML = `
        <span class="alert-message">${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // Insertar alerta directamente en el body
    document.body.appendChild(alert);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}