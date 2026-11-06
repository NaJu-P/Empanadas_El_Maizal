// logica.js - Sistema completo de manejo de opiniones
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const opinionForm = document.getElementById('opinionForm');
    const thankYouMessage = document.getElementById('thankYouMessage');
    const newOpinionBtn = document.getElementById('newOpinionBtn');
    const productoSelect = document.getElementById('producto-select');
    const otraSaborContainer = document.getElementById('otra-sabor-container');
    const listaOpiniones = document.getElementById('listaOpiniones');
    
    // Variable para almacenar datos del usuario
    let currentUser = null;
    
    // Inicialización
    initializeApp();
    
    // Función principal de inicialización
    async function initializeApp() {
        initializeStarRating();
        setupEventListeners();
        await cargarDatosUsuario();
        await cargarProductosDisponibles();
        await cargarOpinionesPublicas();
    }
    
    // Configurar event listeners
    function setupEventListeners() {
        // Manejar cambio de producto
        if (productoSelect) {
            productoSelect.addEventListener('change', handleProductChange);
        }
        
        // Manejar envío del formulario
        if (opinionForm) {
            opinionForm.addEventListener('submit', handleFormSubmit);
        }
        
        // Manejar botón de nueva opinión
        if (newOpinionBtn) {
            newOpinionBtn.addEventListener('click', handleNewOpinion);
        }
    }
    
    // Manejar cambio de producto
    async function handleProductChange() {
        // Mostrar/ocultar campo "otro sabor"
        if (productoSelect.value === 'otro') {
            if (otraSaborContainer) {
                otraSaborContainer.style.display = 'block';
                const otraSaborInput = document.getElementById('otra-sabor');
                if (otraSaborInput) otraSaborInput.required = true;
            }
        } else {
            if (otraSaborContainer) {
                otraSaborContainer.style.display = 'none';
                const otraSaborInput = document.getElementById('otra-sabor');
                if (otraSaborInput) otraSaborInput.required = false;
            }
        }
        
        // Cargar opiniones del producto seleccionado (opcional)
        if (productoSelect.value && productoSelect.value !== 'otro') {
            const opiniones = await cargarOpinionesPorProducto(productoSelect.value);
            console.log(`Opiniones para producto ${productoSelect.value}:`, opiniones);
        }
    }
    
    // Manejar envío del formulario
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        // Verificar usuario autenticado
        if (!currentUser || !currentUser.logged_in) {
            showNotification('Debes iniciar sesión para opinar', 'error');
            return;
        }
        
        // Verificar si hay usuario hidden o usar currentUser
        let idUsuario = currentUser.user?.id_usuario;
        const hiddenUserId = document.getElementById('id_usuario_hidden')?.value;
        if (hiddenUserId) {
            idUsuario = parseInt(hiddenUserId);
        }
        
        if (!idUsuario) {
            showNotification('Error: No se pudo identificar al usuario', 'error');
            return;
        }
        
        // Validar calificación
        const rating = document.querySelector('input[name="rating"]:checked');
        if (!rating) {
            showNotification('Por favor selecciona una calificación', 'error');
            return;
        }
        
        // Validar producto seleccionado
        if (!productoSelect.value) {
            showNotification('Por favor selecciona un producto', 'error');
            return;
        }
        
        // Preparar datos del formulario
        const formData = {
            id_usuario: idUsuario,
            id_producto: productoSelect.value === 'otro' ? null : parseInt(productoSelect.value),
            calificacion: parseInt(rating.value),
            descripcion_opinion: document.getElementById('comentario').value.trim(),
            publicar: document.getElementById('publicar').checked,
            id_tipo_entrega: 1, // Valor fijo
            otro_sabor: productoSelect.value === 'otro' ? document.getElementById('otra-sabor')?.value : null
        };
        
        // Incluir email si está presente
        const emailField = document.getElementById('email');
        if (emailField) {
            formData.email = emailField.value;
        }
        
        // Validar datos requeridos
        if (!formData.descripcion_opinion) {
            showNotification('Por favor escribe tu opinión', 'error');
            return;
        }
        
        if (productoSelect.value === 'otro' && !formData.otro_sabor) {
            showNotification('Por favor especifica el otro sabor', 'error');
            return;
        }
        
        const submitBtn = opinionForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        try {
            // Mostrar estado de carga
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
            submitBtn.disabled = true;
            
            console.log('Enviando opinión:', formData);
            
            // Enviar al servidor
            const response = await fetch('/api/opiniones/crear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                // Éxito
                showSuccessMessage();
                
                // Si la opinión es pública, agregarla a la lista
                if (result.opinion && formData.publicar) {
                    addOpinionToList(result.opinion);
                } else {
                    // Recargar todas las opiniones públicas
                    await cargarOpinionesPublicas();
                }
                
                showNotification('¡Opinión enviada exitosamente!', 'success');
                console.log('Opinión guardada exitosamente');
            } else {
                throw new Error(result.message || 'Error al enviar la opinión');
            }
            
        } catch (error) {
            console.error('Error enviando opinión:', error);
            showNotification(error.message || 'Error de conexión. Intenta de nuevo.', 'error');
        } finally {
            // Restaurar botón
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }
    
    // Mostrar mensaje de éxito
    function showSuccessMessage() {
        if (opinionForm && thankYouMessage) {
            opinionForm.classList.add('hidden');
            thankYouMessage.classList.remove('hidden');
        }
    }
    
    // Manejar nueva opinión
    function handleNewOpinion() {
        if (opinionForm && thankYouMessage) {
            opinionForm.reset();
            opinionForm.classList.remove('hidden');
            thankYouMessage.classList.add('hidden');
            
            // Resetear estrellas completamente
            const ratings = opinionForm.querySelectorAll('input[name="rating"]');
            ratings.forEach(rating => rating.checked = false);
            clearStarRating();
            
            // Ocultar campo adicional
            if (otraSaborContainer) {
                otraSaborContainer.style.display = 'none';
                const otraSaborInput = document.getElementById('otra-sabor');
                if (otraSaborInput) otraSaborInput.required = false;
            }
        }
    }
    
    // Función para cargar datos del usuario desde el servidor
    async function cargarDatosUsuario() {
        try {
            const response = await fetch('/api/usuario/actual', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const result = await response.json();
                currentUser = result;
                
                if (result.logged_in) {
                    console.log('Usuario logueado:', result.user);
                } else {
                    console.log('Usuario no logueado');
                    showNotification('Debes iniciar sesión para poder opinar', 'info');
                }
            } else {
                currentUser = { logged_in: false };
                console.log('Usuario no autenticado');
            }
        } catch (error) {
            console.error('Error cargando datos del usuario:', error);
            currentUser = { logged_in: false };
        }
    }
    
    // Función para cargar productos disponibles
    async function cargarProductosDisponibles() {
        try {
            const response = await fetch('/api/productos/disponibles', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    mostrarProductos(result.productos);
                }
            }
        } catch (error) {
            console.error('Error cargando productos:', error);
        }
    }
    
    // Función para mostrar productos en el select
    function mostrarProductos(productos) {
        if (!productoSelect) return;
        
        productoSelect.innerHTML = '<option value="">Selecciona una empanada...</option>';
        
        productos.forEach(producto => {
            const option = document.createElement('option');
            option.value = producto.id_producto;
            option.textContent = `${producto.nombre_producto} - $${producto.precio_producto}`;
            productoSelect.appendChild(option);
        });
        
        // Agregar opción "Otro" si no existe
        const otroOption = document.createElement('option');
        otroOption.value = 'otro';
        otroOption.textContent = 'Otro sabor...';
        productoSelect.appendChild(otroOption);
    }
    
    // Función para cargar opiniones públicas desde el servidor
    async function cargarOpinionesPublicas() {
        try {
            const response = await fetch('/api/opiniones/publicas', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    mostrarOpiniones(result.opiniones);
                }
            }
        } catch (error) {
            console.error('Error cargando opiniones:', error);
        }
    }
    
    // Función para cargar opiniones por producto
    async function cargarOpinionesPorProducto(idProducto) {
        try {
            const response = await fetch(`/api/opiniones/producto/${idProducto}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    return result.opiniones;
                }
            }
        } catch (error) {
            console.error('Error cargando opiniones por producto:', error);
        }
        return [];
    }
    
    // Función para mostrar las opiniones en la página
    function mostrarOpiniones(opinionesData) {
        if (!listaOpiniones) return;
        
        listaOpiniones.innerHTML = '';
        
        if (!opinionesData || opinionesData.length === 0) {
            listaOpiniones.innerHTML = '<p class="text-center text-gray-500 no-opinions">Aún no hay opiniones públicas. ¡Sé el primero en opinar!</p>';
            return;
        }
        
        // Mostrar las opiniones
        opinionesData.forEach(opinion => {
            const opinionElement = createOpinionElement(opinion);
            listaOpiniones.insertAdjacentHTML('beforeend', opinionElement);
        });
    }
    
    // Agregar opinión a la lista (para opiniones nuevas)
    function addOpinionToList(opinion) {
        if (!listaOpiniones) return;
        
        // Remover mensaje de "no hay opiniones" si existe
        const noOpinions = listaOpiniones.querySelector('.no-opinions');
        if (noOpinions) {
            noOpinions.remove();
        }
        
        const opinionElement = createOpinionElement(opinion);
        listaOpiniones.insertAdjacentHTML('afterbegin', opinionElement);
    }
    
    // Crear elemento HTML de opinión
    function createOpinionElement(opinion) {
        const fecha = new Date(opinion.fecha_creacion);
        const fechaFormateada = fecha.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const fechaLarga = fecha.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        const estrellas = generateStars(opinion.calificacion);
        
        return `
            <div class="opinion-item bg-white rounded-lg shadow-md p-4 mb-4 border border-gray-200">
                <div class="opinion-header flex justify-between items-center mb-2">
                    <div class="flex items-center">
                        <span class="font-semibold text-gray-800">${opinion.nombres_usuario || 'Usuario'}</span>
                        ${opinion.email_usuario ? `<span class="text-gray-500 text-sm ml-2">${opinion.email_usuario}</span>` : ''}
                    </div>
                    <span class="opinion-rating text-yellow-500 text-lg">${estrellas}</span>
                </div>
                <div class="opinion-producto mb-2">
                    <span class="text-sm text-gray-600">Probó: </span>
                    <span class="font-medium text-blue-600">${opinion.nombre_producto || 'Empanada'}</span>
                    ${opinion.precio_producto ? `<span class="text-sm text-gray-500 ml-2">($${opinion.precio_producto})</span>` : ''}
                </div>
                <p class="opinion-descripcion text-gray-700 mb-3">${opinion.descripcion_opinion}</p>
                <div class="opinion-footer flex justify-between items-center">
                    <div class="opinion-date text-sm text-gray-500">${fechaLarga}</div>
                    ${opinion.img_producto ? 
                        `<img src="/static/img/${opinion.img_producto}" 
                             alt="${opinion.nombre_producto}" 
                             class="w-12 h-12 rounded-full object-cover">` 
                        : ''
                    }
                </div>
            </div>
        `;
    }
    
    // Generar estrellas para calificación
    function generateStars(calificacion) {
        return '★'.repeat(calificacion) + '☆'.repeat(5 - calificacion);
    }
    
    // Inicializar sistema de calificación por estrellas - CORREGIDO
    function initializeStarRating() {
        const stars = document.querySelectorAll('.rating input[type="radio"]');
        const labels = document.querySelectorAll('.rating label');
        
        if (!stars.length || !labels.length) return;
        
        // Event listeners para cada estrella
        stars.forEach((star, index) => {
            const starValue = parseInt(star.value);
            const label = star.nextElementSibling;
            
            if (label) {
                // Evento click - seleccionar estrella
                label.addEventListener('click', (e) => {
                    e.preventDefault();
                    selectStar(starValue);
                });
                
                // Evento hover - resaltar estrellas
                label.addEventListener('mouseenter', () => {
                    highlightStars(starValue);
                });
            }
        });
        
        // Event listener para cuando el mouse sale del contenedor
        const ratingContainer = document.querySelector('.rating');
        if (ratingContainer) {
            ratingContainer.addEventListener('mouseleave', () => {
                const checkedStar = document.querySelector('.rating input[type="radio"]:checked');
                if (checkedStar) {
                    highlightStars(parseInt(checkedStar.value));
                } else {
                    clearStarRating();
                }
            });
        }
    }
    
    // Resaltar estrellas - CORREGIDO
    function highlightStars(rating) {
        const labels = document.querySelectorAll('.rating label');
        
        labels.forEach((label) => {
            const input = label.previousElementSibling;
            if (input && input.type === 'radio') {
                const starValue = parseInt(input.value);
                
                // Resaltar estrellas desde 1 hasta el rating seleccionado
                if (starValue <= rating) {
                    label.classList.add('active');
                } else {
                    label.classList.remove('active');
                }
            }
        });
    }
    
    // Seleccionar estrella - CORREGIDO
    function selectStar(rating) {
        // Marcar el radio button correspondiente
        const radioBtn = document.querySelector(`.rating input[value="${rating}"]`);
        if (radioBtn) {
            radioBtn.checked = true;
        }
        
        // Actualizar visualización
        highlightStars(rating);
        
        console.log(`Estrella seleccionada: ${rating}`);
    }
    
    // Limpiar calificación - CORREGIDO
    function clearStarRating() {
        const labels = document.querySelectorAll('.rating label');
        labels.forEach(label => label.classList.remove('active'));
    }
    
    // Función para mostrar notificaciones (unificada)
    function showNotification(mensaje, tipo = 'info') {
        // Usar la función más moderna
        mostrarNotificacion(mensaje, tipo);
    }
    
    function mostrarNotificacion(mensaje, tipo = 'info') {
        // Remover notificación existente
        const existing = document.querySelector('.opinion-notification');
        if (existing) {
            existing.remove();
        }
        
        const notification = document.createElement('div');
        notification.className = `opinion-notification fixed top-4 right-4 p-4 rounded-md shadow-lg z-50 max-w-sm transition-all duration-300 transform translate-x-full`;
        
        const bgColor = tipo === 'success' ? 'bg-green-500' : 
                        tipo === 'error' ? 'bg-red-500' : 'bg-blue-500';
        
        notification.className += ` ${bgColor} text-white`;
        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <p class="text-sm font-medium">${mensaje}</p>
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
});