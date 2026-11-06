window.addEventListener('pageshow', function (event) {
    if (event.persisted || window.performance && performance.getEntriesByType("navigation")[0].type === "back_forward") {
        window.location.reload(); // Recarga sin caché
    }
});

let cart = {};
let cartItems, emptyCartMessage, cartTotal, totalAmount, checkoutBtn;
let cartVersion = null;
let versionCheckInterval = null;
let isLocalChange = false;
let syncTimeout = null;
let pendingChanges = false;
let isCurrentlySyncing = false;

function loadCartFromMemory() {
    return {};
}

// Nueva función: Verificar versión del carrito
// async function checkCartVersion() {
//     try {
//         const response = await fetch('/Carrito/obtener-carrito', {
//             method: 'GET',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'Cache-Control': 'no-cache', // Evitar caché para verificaciones
//                 'Pragma': 'no-cache'
//             }
//         });
        
//         if (response.ok) {
//             const data = await response.json();
//             if (data.status === 'success') {
//                 // Calcular versión basada en el contenido del carrito
//                 const cartContent = JSON.stringify(data.cart || {});
//                 const timestamp = data.timestamp || Date.now();
//                 const version = btoa(cartContent + timestamp).substring(0, 8);
                
//                 // Contar items totales
//                 const totalItems = Object.keys(data.cart || {}).length;
//                 const totalQuantity = Object.values(data.cart || {}).reduce((sum, item) => sum + (item.quantity || 0), 0);
                
//                 return {
//                     version: version,
//                     cart: data.cart || {},
//                     total_items: totalItems,
//                     total_quantity: totalQuantity,
//                     timestamp: timestamp
//                 };
//             }
//         }
//         return null;
//     } catch (error) {
//         console.error('Error al verificar versión del carrito:', error);
//         return null;
//     }
// }

// Nueva función: Monitorear cambios en el carrito
async function monitorCartChanges() {
    // Si estamos haciendo un cambio local, no verificar
    if (isLocalChange) {
        return;
    }
    
    if (currentVersion) {
        // Si es la primera vez, solo inicializar
        if (cartVersion === null) {
            cartVersion = currentVersion;
            console.log('Versión inicial del carrito establecida:', cartVersion);
            return;
        }
        
        // Verificar si hay cambios REALES (no causados por nosotros)
        const hasVersionChanged = cartVersion.version !== currentVersion.version;
        const hasContentChanged = JSON.stringify(cartVersion.cart) !== JSON.stringify(currentVersion.cart);
        
        if (hasVersionChanged || hasContentChanged) {
            console.log('Cambio externo detectado en el carrito:', {
                anterior: cartVersion,
                actual: currentVersion,
                versionChanged: hasVersionChanged,
                contentChanged: hasContentChanged
            });
            
            // Determinar tipo de cambio
            const wasEmpty = Object.keys(cartVersion.cart).length === 0;
            const isNowEmpty = Object.keys(currentVersion.cart).length === 0;
            const hadItems = Object.keys(cartVersion.cart).length > 0;
            const hasItems = Object.keys(currentVersion.cart).length > 0;
            
            // Mostrar mensaje apropiado
            if (wasEmpty && hasItems) {
                showMessage('Productos agregados desde otra pestaña', 'info');
            } else if (hadItems && isNowEmpty) {
                showMessage('Carrito limpiado desde otra pestaña', 'info');
            } else if (hasItems && hadItems) {
                showMessage('Carrito actualizado desde otra pestaña', 'info');
            }
            
            // Actualizar versión local
            cartVersion = currentVersion;
            
            // Actualizar carrito local con datos del servidor
            cart = currentVersion.cart;
            renderCart();
            updateCartDisplay();
        }
    }
}

// Nueva función: Limpiar tanto local como servidor
async function clearBothCarts() {
    try {
        console.log('Iniciando limpieza completa del carrito...');
        
        // Marcar que estamos haciendo un cambio local
        isLocalChange = true;
        
        // Limpiar INMEDIATAMENTE en la UI
        cart = {};
        renderCart();
        updateCartDisplay();
        
        // Mostrar mensaje inmediatamente
        showMessage('Carrito limpiado exitosamente', 'success');
        
        // Limpiar en el servidor
        
        if (response.ok) {
            console.log('Carrito del servidor limpiado exitosamente');
            
            // Forzar actualización de versión
            setTimeout(async () => {
                // Permitir verificaciones después de limpiar
                setTimeout(() => {
                    isLocalChange = false;
                }, 300);
            }, 200);
            
            console.log('Carrito limpiado completamente (servidor y local)');
            return true;
        } else {
            console.error('Error al limpiar carrito del servidor');
            isLocalChange = false;
            throw new Error('Error en servidor');
        }
    } catch (error) {
        console.error('Error al limpiar carrito:', error);
        isLocalChange = false;
        showMessage('Error al limpiar carrito', 'error');
        return false;
    }
}

// Nueva función: Limpiar carrito local
function clearLocalCart() {
    cart = {};
    renderCart();
    updateCartDisplay();
}

// Nueva función: Refrescar carrito desde servidor
// async function refreshCartFromServer() {
//     try {
//     } catch (error) {
//         console.error('Error al refrescar carrito desde servidor:', error);
//         return false;
//     }
// }

// Nueva función: Mostrar mensajes de feedback
function showMessage(message, type = 'success') {
    const messageContainer = document.getElementById('message-container') || document.body;
    
    const existingMessages = messageContainer.querySelectorAll('.cart-message');
    for (let msg of existingMessages) {
        if (msg.textContent === message) {
            return;
        }
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `cart-message ${type === 'success' ? 'bg-green-500' : type === 'warning' ? 'bg-yellow-500' : type === 'info' ? 'bg-blue-500' : 'bg-red-500'} text-white p-3 rounded-lg shadow-lg mb-2 transition-all duration-300 fade-out fixed top-4 right-4 z-50`;
    messageDiv.textContent = message;
    
    messageContainer.appendChild(messageDiv);
    
    requestAnimationFrame(() => {
        messageDiv.classList.remove('fade-out');
    });
    
    setTimeout(() => {
        messageDiv.classList.add('fade-out');
        setTimeout(() => {
            if (messageContainer.contains(messageDiv)) {
                messageContainer.removeChild(messageDiv);
            }
        }, 300);
    }, 2500);
}

// Nueva función: Detener monitoreo
function stopCartMonitoring() {
    if (versionCheckInterval) {
        clearInterval(versionCheckInterval);
        versionCheckInterval = null;
    }
}

async function syncCartWithBackend(immediate = false) {
    try {
        // Si ya estamos sincronizando, marcar que hay cambios pendientes
        if (isCurrentlySyncing && !immediate) {
            pendingChanges = true;
            return;
        }
        
        // Cancelar sincronización anterior si existe
        if (syncTimeout) {
            clearTimeout(syncTimeout);
            syncTimeout = null;
        }
        
        // Si no es inmediato, usar debounce de 500ms
        if (!immediate) {
            syncTimeout = setTimeout(() => {
                syncCartWithBackend(true);
            }, 500);
            return;
        }
        
        console.log('Sincronizando carrito con backend:', cart);
        
        // Marcar que estamos haciendo un cambio local
        isLocalChange = true;
        isCurrentlySyncing = true;
        
        if (response.ok) {
            const data = await response.json();
            console.log('Carrito sincronizado exitosamente con backend:', data);
            
            // Guardar en memoria
            
            // Actualizar versión local después de sincronizar
            setTimeout(async () => {
                // Permitir verificaciones después de actualizar la versión
                setTimeout(() => {
                    isLocalChange = false;
                    isCurrentlySyncing = false;
                    
                    // Si hay cambios pendientes, sincronizar de nuevo
                    if (pendingChanges) {
                        pendingChanges = false;
                        syncCartWithBackend(true);
                    }
                }, 300);
            }, 200);
            
            return data;
        } else {
            throw new Error(`Error HTTP: ${response.status}`);
        }
    } catch (error) {
        console.error('Error al sincronizar carrito:', error);
        // Resetear flags en caso de error
        isLocalChange = false;
        isCurrentlySyncing = false;
        pendingChanges = false;
        throw error;
    }
}

// Función para actualizar el total - GLOBAL
function updateTotal() {
    let total = 0;
    Object.values(cart).forEach(item => {
        total += item.price * item.quantity;
    });
    
    if (totalAmount) {
        totalAmount.textContent = `$${total.toLocaleString()}`;
    }
}

// Función para actualizar la visualización del carrito - GLOBAL
function updateCartDisplay() {
    const hasItems = Object.keys(cart).length > 0;

    if (emptyCartMessage) {
        if (hasItems) {
            emptyCartMessage.style.display = 'none';
        } else {
            emptyCartMessage.style.display = 'block';
        }
    }

    if (cartTotal) {
        if (hasItems) {
            cartTotal.classList.remove('hidden');
        } else {
            cartTotal.classList.add('hidden');
        }
    }

    if (checkoutBtn) {
        checkoutBtn.disabled = !hasItems;
    }

    updateTotal();
}



// Función para renderizar el carrito - GLOBAL
function renderCart() {
    if (!cartItems) return;

    // Limpiar elementos del carrito (excepto el mensaje vacío)
    const cartChildren = Array.from(cartItems.children);
    cartChildren.forEach(child => {
        if (child.id !== 'empty-cart-message') {
            cartItems.removeChild(child);
        }
    });

    // Agregar elementos del carrito
    Object.entries(cart).forEach(([id, item]) => {
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item bg-white p-4 rounded-lg shadow-md';
        
        // Agregar data attributes
        cartItem.setAttribute('data-id', id);
        cartItem.setAttribute('data-name', item.name);
        cartItem.setAttribute('data-price', item.price);
        cartItem.setAttribute('data-quantity', item.quantity);
        
        cartItem.innerHTML = `
            <div class="flex items-center gap-4">
                <img src="/static/img/${item.img || 'default.jpg'}" 
                     alt="${item.name}"
                     class="w-16 h-16 object-cover rounded"/>
                <div>
                    <h4 class="font-bold text-gray-800 text-lg">${item.name}</h4>
                    <p class="text-sm text-gray-500">Precio unitario: $${item.price.toLocaleString()}</p>
                </div>
            </div>

            <div class="flex justify-between items-center mt-2">
                <div class="quantity-controls">
                    <button class="quantity-btn bg-gray-200 w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-300 transition" 
                            onclick="updateQuantity('${id}', -1)" aria-label="Disminuir cantidad">-</button>
                    <span class="quantity-display mx-2 font-medium">${item.quantity}</span>
                    <button class="quantity-btn bg-gray-200 w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-300 transition" 
                            id="plus-${id}" onclick="updateQuantity('${id}', 1)" aria-label="Aumentar cantidad">+</button>
                    <button class="remove-btn ml-4 text-red-500 hover:text-red-700 transition" 
                            onclick="removeFromCart('${id}')" aria-label="Eliminar producto">
                        <i class="fas fa-trash"></i> Eliminar
                    </button>
                </div>
                <div class="text-right">
                    <p class="text-lg md:text-xl font-bold">
                        $${(item.price * item.quantity).toLocaleString()}
                    </p>
                </div>
            </div>
        `;

        const plusBtn = cartItem.querySelector(`#plus-${id}`);

        if (plusBtn) {
            if (item.quantity >= item.stock) {
                plusBtn.disabled = true;
                plusBtn.classList.add("opacity-50", "cursor-not-allowed");
            } else {
                plusBtn.disabled = false;
                plusBtn.classList.remove("opacity-50", "cursor-not-allowed");
            }
        }
        
        cartItems.appendChild(cartItem);
    });

    updateCartDisplay();
}

// Función para actualizar cantidad - GLOBAL
async function updateQuantity(productId, change) {
    if (cart[productId]) {
        const item = cart[productId];
        const oldQuantity = item.quantity;
        const newQuantity = item.quantity + change;

        const maxStock = item.stock ?? 999;

        if (change > 0 && newQuantity > maxStock) {
            return;
        }

        isLocalChange = true;

        if (newQuantity <= 0) {
            delete cart[productId];
        } else {
            cart[productId].quantity = newQuantity;
        }

        renderCart();

        try {
            await syncCartWithBackend();
        } catch (error) {
            isLocalChange = false;
            cart[productId] = { ...item, quantity: oldQuantity };
            renderCart();
        }
    }
}


// Función para eliminar del carrito - GLOBAL
async function removeFromCart(productId) {
    const removedItem = cart[productId];
    
    // Marcar que estamos haciendo un cambio local
    isLocalChange = true;
    
    // Eliminar INMEDIATAMENTE
    delete cart[productId];
    
    // Guardar y renderizar inmediatamente
    renderCart();
    
    try {
        // Sincronizar con backend (con debounce)
        await syncCartWithBackend();
    } catch (error) {
        console.error('Error al sincronizar con backend:', error);
        // Revertir cambios si hay error
        isLocalChange = false;
        cart[productId] = removedItem;
        renderCart();
    }
}

window.addToCart = async function(productId, productName, productPrice, productImg) {
    try {
        console.log('Agregando producto al carrito:', { productId, productName, productPrice, productImg });
        
        // Marcar que estamos haciendo un cambio local
        isLocalChange = true;
        
        // Agregar o actualizar producto en el carrito local INMEDIATAMENTE
        if (cart[productId]) {
            cart[productId].quantity += 1;
        } else {
            cart[productId] = {
                name: productName,
                price: parseFloat(productPrice),
                quantity: 1,
                img: productImg || 'default.jpg'
            };
        }
        
        // Guardar en memoria
        
        // Actualizar display INMEDIATAMENTE si estamos en la página del carrito
        if (cartItems) {
            renderCart();
            updateCartDisplay();
        }
        
        // Mostrar mensaje inmediatamente
        showMessage(`${productName} agregado al carrito`, 'success');
        
        // Sincronizar con backend (con debounce)
        await syncCartWithBackend();
        
        console.log('Producto agregado exitosamente al carrito');
    } catch (error) {
        console.error('Error al agregar producto al carrito:', error);
        isLocalChange = false;
        showMessage('Error al agregar producto', 'error');
    }
};

let batchOperations = [];
let batchTimeout = null;

function addToBatch(operation) {
    batchOperations.push(operation);
    
    if (batchTimeout) {
        clearTimeout(batchTimeout);
    }
    
    batchTimeout = setTimeout(async () => {
        await processBatch();
    }, 200);
}

async function processBatch() {
    if (batchOperations.length === 0) return;
    
    console.log('Procesando lote de operaciones:', batchOperations.length);
    
    // Procesar todas las operaciones
    batchOperations.forEach(operation => {
        operation();
    });
    
    // Limpiar lote
    batchOperations = [];
    
    // Sincronizar una sola vez
    await syncCartWithBackend(true);
}

// Función optimizada para operaciones rápidas
window.addToCartFast = function(productId, productName, productPrice, productImg) {
    addToBatch(() => {
        if (cart[productId]) {
            cart[productId].quantity += 1;
        } else {
            cart[productId] = {
                name: productName,
                price: parseFloat(productPrice),
                quantity: 1,
                img: productImg || 'default.jpg'
            };
        }
        
        if (cartItems) {
            renderCart();
            updateCartDisplay();
        }
    });
    
    showMessage(`${productName} agregado al carrito`, 'success');
};

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar elementos del DOM
    cartItems = document.getElementById('cart-items');
    emptyCartMessage = document.getElementById('empty-cart-message');
    cartTotal = document.getElementById('cart-total');
    totalAmount = document.getElementById('total-amount');
    checkoutBtn = document.getElementById('checkout-btn');

    initializeCart();

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

            // ===== SOLO USAR ProfileManager PARA LOS EVENT LISTENERS =====
            
            // Event listeners para el dropdown
            this.userIcon?.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('User icon clicked via ProfileManager');
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
                console.log('Profile link clicked via ProfileManager');
                this.openProfileModal();
            });

            // Event listener para logout
            this.logoutLink?.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogout();
            });

            // Event listeners para cerrar el modal
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
                if (!this.userIcon?.contains(e.target) && 
                    !this.dropdownMenu?.contains(e.target)) {
                    this.hideDropdown();
                }
            });

            // Manejar tecla Escape para cerrar modal
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && !this.profileModal?.classList.contains('hidden')) {
                    this.closeProfileModal();
                }
            });

            // Cargar datos del perfil al inicializar
            this.loadProfile();
        }

        toggleDropdown() {
            console.log('Toggle dropdown called via ProfileManager');
            if (this.dropdownMenu?.classList.contains('hidden')) {
                this.showDropdown();
            } else {
                this.hideDropdown();
            }
        }

        showDropdown() {
            console.log('Showing dropdown via ProfileManager');
            if (this.dropdownMenu) {
                this.dropdownMenu.classList.remove('hidden');
                this.userIcon?.setAttribute('aria-expanded', 'true');
            }
        }

        hideDropdown() {
            console.log('Hiding dropdown via ProfileManager');
            if (this.dropdownMenu) {
                this.dropdownMenu.classList.add('hidden');
                this.userIcon?.setAttribute('aria-expanded', 'false');
            }
        }

        async openProfileModal() {
            console.log('=== OPENING PROFILE MODAL ===');
            console.log('Modal element exists:', !!this.profileModal);
            
            // Cerrar dropdown primero
            this.hideDropdown();
            
            if (this.profileModal) {
                // Paso 1: Remover la clase hidden del contenedor
                this.profileModal.classList.remove('hidden');
                console.log('Step 1: Removed hidden class from modal container');
                
                // Paso 2: Encontrar el contenido del modal y configurar clases iniciales
                const modalContent = this.profileModal.querySelector('.bg-white, [role="document"]') || 
                                   this.profileModal.querySelector('div > div');
                
                console.log('Modal content element found:', !!modalContent);
                console.log('Modal content classes before:', modalContent?.className);
                
                if (modalContent) {
                    // Asegurar que el contenido esté inicialmente oculto
                    modalContent.classList.add('scale-95', 'opacity-0');
                    modalContent.classList.remove('scale-100', 'opacity-100');
                    console.log('Step 2: Set initial animation classes');
                }
                
                // Forzar reflow del DOM
                this.profileModal.offsetHeight;
                
                // Paso 3: Cargar datos del perfil
                await this.loadProfile();
                
                // Paso 4: Animación de entrada (hacer visible el contenido)
                setTimeout(() => {
                    if (modalContent) {
                        modalContent.classList.remove('scale-95', 'opacity-0');
                        modalContent.classList.add('scale-100', 'opacity-100');
                        console.log('Step 4: Applied show animation classes');
                        console.log('Modal content classes after animation:', modalContent.className);
                    }
                }, 10);

                // Paso 5: Focus en el primer input
                setTimeout(() => {
                    const firstInput = this.profileForm?.querySelector('input');
                    if (firstInput) {
                        firstInput.focus();
                        console.log('Step 5: Focus set on first input');
                    }
                }, 100);
                
                console.log('=== MODAL SHOULD BE VISIBLE NOW ===');
            } else {
                console.error('Modal element not found!');
            }
        }

        closeProfileModal() {
            console.log('Closing profile modal via ProfileManager');
            const modalContent = this.profileModal?.querySelector('[role="document"]');
            if (modalContent) {
                modalContent.classList.remove('scale-100', 'opacity-100');
                modalContent.classList.add('scale-95', 'opacity-0');
            }
            
            setTimeout(() => {
                this.profileModal?.classList.add('hidden');
            }, 300);
        }

        handleLogout() {
            if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
                window.location.href = '/auth/logout';
            }
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
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.success) {
                    this.populateForm(data.user);
                    console.log('Perfil cargado exitosamente:', data.user);
                } else {
                    this.showNotification('Error al cargar el perfil: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('Error cargando perfil:', error);
                this.showNotification('Error de conexión al cargar el perfil', 'error');
                
                // Cargar datos por defecto en caso de error
                this.populateForm({
                    nombres_usuario: '',
                    email_usuario: '',
                    telefono: '',
                    direccion_usuario: ''
                });
            } finally {
                this.showLoading(false);
            }
        }

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

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.success) {
                    this.showNotification('Perfil actualizado correctamente', 'success');
                    this.closeProfileModal();
                    console.log('Perfil actualizado exitosamente');
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

    // ===== INICIALIZAR ProfileManager - AQUÍ ES DONDE SE CONTROLA TODO =====
    const profileManager = new ProfileManager();

    // ===== FUNCIONES DEL CARRITO =====
    
    // Función para cargar carrito desde backend
    // async function loadCartFromBackend() {
    //     try {
    //         const response = await fetch('/Carrito/obtener-carrito');
    //         if (response.ok) {
    //             const data = await response.json();
    //             const backendCart = data.cart || {};
                
    //             // Comparar con el carrito local
    //             const localCartString = JSON.stringify(cart);
    //             const backendCartString = JSON.stringify(backendCart);
                
    //             if (localCartString !== backendCartString) {
    //                 console.log('Sincronizando carrito con backend...');
    //                 cart = backendCart;
    //                 saveCartToMemory();
    //                 renderCart();
    //                 updateCartDisplay();
    //             }
    //         }
    //     } catch (error) {
    //         console.error('Error al cargar el carrito desde backend:', error);
    //         throw error;
    //     }
    // }

    // Función para inicializar el carrito
    async function initializeCart() {
        console.log('Inicializando carrito...');
        
        // Primero cargar desde memoria
        const cachedCart = loadCartFromMemory();
        if (Object.keys(cachedCart).length > 0) {
            cart = cachedCart;
            console.log('Carrito cargado desde memoria:', cart);
            renderCart();
            updateCartDisplay();
        } else {
            // Fallback: cargar desde HTML de Jinja2
            document.querySelectorAll('.cart-item').forEach(item => {
                const id = item.dataset.id;
                const imgElement = item.querySelector('img');
                const imgSrc = imgElement ? imgElement.src : '';
                const imgName = imgSrc ? imgSrc.split('/').pop() : 'default.jpg';
                
                cart[id] = {
                    name: item.dataset.name,
                    price: parseFloat(item.dataset.price),
                    quantity: parseInt(item.dataset.quantity),
                    img: imgName
                };
            });
            
            if (Object.keys(cart).length > 0) {
                console.log('Carrito cargado desde HTML (fallback):', cart);
                renderCart();
                updateCartDisplay();
            }
        }

        // Intentar sincronizar con backend
        try {
            console.log('Sincronizando con backend...');
        
            const response = await fetch('/Carrito/obtener-carrito', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });
        
            if (response.ok) {
                const data = await response.json();
                const serverCart = data.cart || {};
            
                console.log('Carrito del servidor obtenido:', serverCart);
            
                // Comparar con carrito local
                const localCartString = JSON.stringify(cart);
                const serverCartString = JSON.stringify(serverCart);
            
                if (localCartString !== serverCartString) {
                    console.log('Sincronizando carrito local con servidor...');
                
                    // Actualizar carrito local
                    cart = serverCart;
                    renderCart();
                    updateCartDisplay();
                
                    console.log('Carrito sincronizado exitosamente:', cart);
                }
            
                return true;
            }
            return false;

        } catch (error) {
            console.error('Error al inicializar carrito:', error);
            showMessage('Error al cargar carrito', 'warning');
        }
    }

    // Event listener para el botón de checkout
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', async () => {
            try {
                checkoutBtn.disabled = true;
                checkoutBtn.textContent = 'Guardando Pedido...';
                
                if (response.ok) {
                    const data = await response.json();
                    cart = {};
                    alert('Pedido guardado exitosamente');
                    window.location.href = '/Metodo-pago';
                } else {
                    throw new Error('Error en la respuesta del servidor');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al procesar la compra. Inténtalo de nuevo.');
                
                checkoutBtn.disabled = false;
                checkoutBtn.textContent = 'Proceder al Pago';
            }
        });
    }

    // Event listeners para conexión
    window.addEventListener('online', () => {
        showMessage('Conexión restaurada', 'success');
        monitorCartChanges();
    });

    window.addEventListener('offline', () => {
        showMessage('Sin conexión a internet', 'warning');
    });

    // Limpieza al cerrar la página
    window.addEventListener('beforeunload', () => {
        stopCartMonitoring();
    });

    console.log('Home JavaScript cargado correctamente - Con monitoreo de cambios');
});