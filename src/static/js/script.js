document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const productItems = document.querySelectorAll('.product-item');
    const messageContainer = document.getElementById('message-container');

    let cart = {};
    let isProcessing = false;
    let versionCheckInterval = null;
    let stockCheckInterval = null;

    function stopStockMonitoring() {
        if (stockCheckInterval) {
            clearInterval(stockCheckInterval);
            stockCheckInterval = null;
        }
    }

    // Función para mostrar mensajes de feedback
    function showMessage(message, type = 'success') {
        const existingMessages = messageContainer.querySelectorAll('.message');
        for (let msg of existingMessages) {
            if (msg.textContent === message) {
                return;
            }
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type === 'success' ? 'bg-green-500' : type === 'warning' ? 'bg-yellow-500' : 'bg-red-500'} text-white p-3 rounded-lg shadow-lg mb-2 transition-all duration-300 fade-out`;
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

    // Función para verificar versión del carrito
    // async function checkCartVersion() {
    //     try {
    //         const response = await fetch('/Carrito/obtener-carrito', {
    //             method: 'GET',
    //             headers: {
    //                 'Content-Type': 'application/json'
    //             }
    //         });
            
    //         if (response.ok) {
    //             const data = await response.json();
    //             if (data.status === 'success') {
    //                 // Calcular versión basada en el contenido del carrito
    //                 const cartContent = JSON.stringify(data.cart || {});
    //                 const timestamp = data.timestamp || Date.now();
    //                 const version = btoa(cartContent + timestamp).substring(0, 8);
                    
    //                 return {
    //                     version: version,
    //                     cart: data.cart || {},
    //                     total_items: Object.keys(data.cart || {}).length,
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

    // async function monitorCartChanges() {
    //     const currentVersion = await checkCartVersion();
        
    //     if (currentVersion) {
    //         // Primera vez o cambio de versión
    //         if (cartVersion === null) {
    //             cartVersion = currentVersion;
    //             console.log('Versión inicial del carrito establecida');
    //             return;
    //         }

    //         // Verificar si hay cambios
    //         const hasVersionChanged = cartVersion.version !== currentVersion.version;
    //         const hasContentChanged = JSON.stringify(cartVersion.cart) !== JSON.stringify(currentVersion.cart);
            
    //         if (hasVersionChanged || hasContentChanged) {
    //             console.log('Cambio detectado en el carrito, refrescando...', {
    //                 anterior: cartVersion,
    //                 actual: currentVersion
    //             });
                
    //             cartVersion = currentVersion;
                
    //             // Actualizar carrito local con datos del servidor
    //             cart = currentVersion.cart;
    //             saveCartToSession();
                
    //             // Actualizar UI de todos los productos
    //             productItems.forEach(item => {
    //                 const productId = item.dataset.id;
    //                 if (productId) {
    //                     updateProductUI(productId);
    //                 }
    //             });
                
    //             showMessage('Carrito actualizado desde otra sesión', 'success');
    //         }
    //     }
    // }

    // Función para cargar carrito desde servidor
     async function loadCartFromServer() {
        try {
            console.log('🔄 Cargando carrito del servidor...');

            const response = await fetch('/Carrito/obtener-carrito', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Datos recibidos del servidor:', data);
                
                if (data.status === 'success') {
                    return data.cart || {};
                } else {
                    console.warn('⚠️ El servidor respondió con error:', data.message);
                    return loadCartFromSession();
                }
            } else {
                console.error('❌ Error del servidor:', response.status);
                return loadCartFromSession();
            }
            
        
        } catch (error) {
            console.error('❌ Error de red:', error);
            return loadCartFromSession();
        }
     }

    // Función para cargar carrito desde sessionStorage (fallback)
    function loadCartFromSession() {
        try {
            const cachedCart = sessionStorage.getItem('cart');
            return cachedCart ? JSON.parse(cachedCart) : {};
        } catch (error) {
            console.error('Error al cargar carrito desde sessionStorage:', error);
            return {};
        }
    }

    // Función para limpiar carrito local
    function clearLocalCart() {
        cart = {};
        sessionStorage.removeItem('cart');
        
        // Actualizar UI de todos los productos
        productItems.forEach(item => {
            const productId = item.dataset.id;
            if (productId) {
                updateProductUI(productId);
            }
        });
    }

    // Función para limpiar tanto local como servidor
    async function clearBothCarts() {
        try {
            // Limpiar en el servidor enviando carrito vacío
            const response = await fetch('/Carrito/pagar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            if (response.ok) {
                clearLocalCart();
                console.log('Carrito limpiado completamente (servidor y local)');
                showMessage('Carrito limpiado completamente', 'success');
                return true;
            } else {
                console.error('Error al limpiar carrito del servidor');
                clearLocalCart();
                return false;
            }
        } catch (error) {
            console.error('Error al limpiar carrito:', error);
            clearLocalCart();
            return false;
        }
    }

    // Función para guardar carrito en sessionStorage
    let saveTimeout;
    function saveCartToSession() {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            try {
                sessionStorage.setItem('cart', JSON.stringify(cart));
            } catch (error) {
                console.error('Error al guardar carrito en sessionStorage:', error);
            }
        }, 100);
    }

    // Función para sincronizar carrito con el backend
    async function syncCartWithBackend(retries = 2) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);

        try {
            const response = await fetch('/Carrito/pagar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(cart),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Carrito sincronizado con backend:', data);
                
                return data;
            } else {
                throw new Error(`Error del servidor: ${response.status}`);
            }
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('La operación tardó demasiado tiempo');
            }
            
            if (retries > 0 && (error.name === 'TypeError' || error.message.includes('Failed to fetch'))) {
                console.log(`Reintentando sincronización... (${retries} intentos restantes)`);
                await new Promise(resolve => setTimeout(resolve, 1000));
                return syncCartWithBackend(retries - 1);
            }
            
            console.error('Error al sincronizar carrito:', error);
            throw error;
        }
    }

    // Función para actualizar la UI de un producto
    function updateProductUI(productId) {
        const quantityDisplay = document.getElementById(`quantity-${productId}`);
        const productItem = document.querySelector(`[data-id="${productId}"]`);
        const addButton = productItem?.querySelector('.add-to-cart-btn');
        const quantityButtons = productItem?.querySelectorAll('.quantity-btn');
        
        // Actualizar cantidad en el display
        if (cart[productId] && cart[productId].quantity > 0) {
            if (quantityDisplay) quantityDisplay.textContent = cart[productId].quantity;
        } else {
            if (quantityDisplay) quantityDisplay.textContent = '0';
        }
        
        // Verificar stock disponible del producto
        if (productItem) {
            const stockDisponible = parseInt(productItem.dataset.stock) || 0;
            const estadoStock = productItem.dataset.estado || 'disponible';
            
            // Deshabilitar si no hay stock o stock crítico
            const shouldDisable = stockDisponible <= 0 || estadoStock === 'sin_stock';
            const isLowStock = stockDisponible <= 10 && stockDisponible > 0;
            
            // Actualizar botón de agregar
            if (addButton) {
                addButton.disabled = shouldDisable;
                
                if (shouldDisable) {
                    addButton.innerHTML = '❌ Agotado';
                    addButton.style.background = '#9ca3af';
                    addButton.style.cursor = 'not-allowed';
                    addButton.classList.add('btn-disabled');
                } else if (isLowStock) {
                    addButton.innerHTML = '⚠️ Stock Bajo - Agregar';
                    addButton.style.background = 'linear-gradient(135deg, #fbbf24, #f59e0b)';
                    addButton.style.cursor = 'pointer';
                    addButton.classList.remove('btn-disabled');
                } else {
                    addButton.innerHTML = '🛒 Agregar al carrito';
                    addButton.style.background = 'linear-gradient(135deg, #fbbf24, #f59e0b)';
                    addButton.style.cursor = 'pointer';
                    addButton.classList.remove('btn-disabled');
                }
            }
            
            // Deshabilitar botones de cantidad si no hay stock
            if (quantityButtons) {
                quantityButtons.forEach(btn => {
                    if (shouldDisable) {
                        btn.disabled = true;
                        btn.style.opacity = '0.5';
                    } else {
                        btn.disabled = false;
                        btn.style.opacity = '1';
                    }
                });
            }
            
            // Actualizar clases CSS del producto
            productItem.classList.toggle('product-agotado', shouldDisable);
            productItem.classList.toggle('stock-bajo', isLowStock && !shouldDisable);
            
            // Mostrar/ocultar advertencia de stock bajo
            const stockWarning = productItem.querySelector('.stock-warning');
            if (stockWarning) {
                stockWarning.style.display = isLowStock ? 'block' : 'none';
            }
        }
    }
    
    // Función para verificar stock antes de agregar producto
    async function verifyStockBeforeAdd(productId, requestedQuantity = 1) {
        try {
            const response = await fetch('/Catalogo/verificar-stock', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    producto_id: productId,
                    cantidad: requestedQuantity
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                return { success: true, message: data.message };
            } else if (data.status === 'warning') {
                showMessage(data.message, 'warning');
                return { success: true, message: data.message, warning: true };
            } else {
                showMessage(data.message, 'error');
                return { success: false, message: data.message };
            }
            
        } catch (error) {
            console.error('Error al verificar stock:', error);
            showMessage('Error al verificar disponibilidad', 'error');
            return { success: false, message: 'Error de conexión' };
        }
    }

    // Función para actualizar el estado del stock de todos los productos
    // async function updateAllProductsStock() {
    //     try {
    //         const response = await fetch('/Catalogo/estado-stock', {
    //             method: 'GET',
    //             headers: {
    //                 'Content-Type': 'application/json'
    //             }
    //         });
            
    //         if (response.ok) {
    //             const data = await response.json();
                
    //             if (data.status === 'success') {
    //                 // Actualizar datos de stock en el DOM
    //                 Object.keys(data.productos).forEach(productId => {
    //                     const productItem = document.querySelector(`[data-id="${productId}"]`);
    //                     if (productItem) {
    //                         const producto = data.productos[productId];
    //                         productItem.dataset.stock = producto.cantidad;
    //                         productItem.dataset.estado = producto.estado;
                            
    //                         // Actualizar display de stock
    //                         const stockDisplay = productItem.querySelector('.stock-display');
    //                         if (stockDisplay) {
    //                             stockDisplay.textContent = producto.cantidad;
    //                             stockDisplay.classList.toggle('cantidad-critica', producto.cantidad <= 10);
    //                         }
                            
    //                         // Actualizar UI del producto
    //                         updateProductUI(productId);
    //                     }
    //                 });
                    
    //                 console.log('Stock actualizado para todos los productos');
    //             }
    //         }
    //     } catch (error) {
    //         console.error('Error al actualizar stock:', error);
    //     }
    // }

    // Función para agregar producto al carrito
    async function addToCart(productId, productName, productPrice) {
        if (isProcessing) {
            showMessage('Procesando solicitud anterior...', 'warning');
            return;
        }

        // Verificar stock antes de proceder
        const currentQuantity = cart[productId] ? cart[productId].quantity : 0;
        const stockCheck = await verifyStockBeforeAdd(productId, currentQuantity + 1);
        
        if (!stockCheck.success) {
            return; // No continuar si no hay stock
        }

        isProcessing = true;
        const button = document.querySelector(`[data-product-id="${productId}"]`);
        
        if (!button) {
            isProcessing = false;
            return;
        }

        // Verificar si el botón está deshabilitado
        if (button.disabled) {
            isProcessing = false;
            showMessage('Producto no disponible', 'error');
            return;
        }

        const originalText = button.innerHTML;
        
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Agregando...';
        button.disabled = true;

        const previousState = JSON.parse(JSON.stringify(cart));
        
        if (cart[productId]) {
            cart[productId].quantity++;
        } else {
            cart[productId] = {
                name: productName,
                price: productPrice,
                quantity: 1
            };
        }
        
        saveCartToSession();
        updateProductUI(productId);
        
        // Mostrar mensaje apropiado
        if (stockCheck.warning) {
            showMessage(`${productName} agregado (Stock bajo)`, 'warning');
        } else {
            showMessage(`${productName} agregado al carrito`, 'success');
        }

        try {
            await syncCartWithBackend();
            // Actualizar stock después de agregar exitosamente
        } catch (error) {
            console.error('Error al agregar producto:', error);
            cart = previousState;
            saveCartToSession();
            updateProductUI(productId);
            
            let errorMessage = 'Error al sincronizar con el servidor';
            if (error.message.includes('tiempo')) {
                errorMessage = 'La operación tardó demasiado tiempo. Inténtalo de nuevo.';
            } else if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Sin conexión a internet. El producto se agregó localmente.';
            }
            
            showMessage(errorMessage, 'error');
        } finally {
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
                isProcessing = false;
            }, 500);
        }
    }

    // Función para actualizar cantidad
    async function updateQuantity(productId, change) {
        if (cart[productId]) {
            const oldQuantity = cart[productId].quantity;
            const newQuantity = oldQuantity + change;
            
            const productItem = document.querySelector(`[data-id="${productId}"]`);
            const maxStock = parseInt(productItem?.dataset.stock || "0");

            if (change > 0 && newQuantity > maxStock) {
                showMessage(`Solo quedan ${maxStock} unidades disponibles`, 'warning');
                return;
            }
            
            cart[productId].quantity = newQuantity;
            
            if (cart[productId].quantity <= 0) {
                delete cart[productId];
            }
            
            saveCartToSession();
            updateProductUI(productId);
            
            try {
                await syncCartWithBackend();
                showMessage('Cantidad actualizada', 'success');
                // Actualizar stock después de cambiar cantidad
            } catch (error) {
                console.error('Error al sincronizar con backend:', error);
                if (cart[productId]) {
                    cart[productId].quantity = oldQuantity;
                } else {
                    cart[productId] = {
                        name: '',
                        price: 0,
                        quantity: oldQuantity
                    };
                }
                saveCartToSession();
                updateProductUI(productId);
                showMessage('Error al actualizar cantidad', 'error');
            }
        }
    }

    // Función para eliminar del carrito
    async function removeFromCart(productId) {
        const removedItem = cart[productId];
        if (!removedItem) return;
        
        delete cart[productId];
        
        saveCartToSession();
        updateProductUI(productId);
        
        try {
            await syncCartWithBackend();
            showMessage(`${removedItem.name} eliminado del carrito`, 'success');
        } catch (error) {
            console.error('Error al sincronizar con backend:', error);
            cart[productId] = removedItem;
            saveCartToSession();
            updateProductUI(productId);
            showMessage('Error al eliminar producto', 'error');
        }
    }

    async function refreshCartFromServer() {
        try {
            const serverCart = await loadCartFromServer();
            cart = serverCart;
            saveCartToSession();
            
            // Actualizar UI de todos los productos
            productItems.forEach(item => {
                const productId = item.dataset.id;
                if (productId) {
                    updateProductUI(productId);
                }
            });
            
            console.log('Carrito refrescado desde servidor:', cart);
            return true;
        } catch (error) {
            console.error('Error al refrescar carrito:', error);
            return false;
        }
    }

    function stopCartMonitoring() {
        if (versionCheckInterval) {
            clearInterval(versionCheckInterval);
            versionCheckInterval = null;
        }
        stopStockMonitoring();
    }

    // Inicializar carrito
    async function initializeCart() {
        // Cargar carrito inicial
        const serverCart = await loadCartFromServer();
        cart = serverCart;
        
        // Actualizar estado del stock de todos los productos
        
        // Guardar en sessionStorage como backup
        saveCartToSession();
        
        console.log('Carrito inicializado:', cart);
        
        // Actualizar UI de todos los productos
        Object.keys(cart).forEach(productId => {
            updateProductUI(productId);
        });
        
        // Actualizar UI de productos no en carrito también
        productItems.forEach(item => {
            const productId = item.dataset.id;
            if (productId && !cart[productId]) {
                updateProductUI(productId);
            }
        });

    }

    // Función para debouncing
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    const handleAddToCart = debounce((productId, productName, productPrice) => {
        addToCart(productId, productName, productPrice);
    }, 300);

    // Inicializar la aplicación
    initializeCart();

    // Event listeners para botones de agregar al carrito
    productItems.forEach(item => {
        const button = item.querySelector('.add-to-cart-btn');
        if (button) {
            const productId = item.dataset.id;
            const productName = item.dataset.name;
            const productPrice = parseFloat(item.dataset.price);

            if (!productId || !productName || isNaN(productPrice)) {
                console.warn('Producto con datos inválidos:', { productId, productName, productPrice });
                return;
            }

            button.dataset.productId = productId;
            button.dataset.productName = productName;
            button.dataset.productPrice = productPrice;

            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                if (button.disabled) {
                    return;
                }
                
                handleAddToCart(productId, productName, productPrice);
            });
        }
    });

    // Event listeners para teclas
    productItems.forEach(item => {
        item.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const button = item.querySelector('.add-to-cart-btn');
                if (button && !button.disabled) {
                    button.click();
                }
            }
        });
    });

    // Event listeners para conexión
    window.addEventListener('online', () => {
        showMessage('Conexión restaurada', 'success');
        monitorCartChanges();
    });

    window.addEventListener('offline', () => {
        showMessage('Sin conexión a internet', 'warning');
    });

    // Limpieza
    window.addEventListener('beforeunload', () => {
        clearTimeout(saveTimeout);
        stopCartMonitoring();
    });

    // Exponer funciones globalmente
    window.updateQuantity = updateQuantity;
    window.removeFromCart = removeFromCart;
    window.clearLocalCart = clearLocalCart;
    window.clearBothCarts = clearBothCarts;
    window.refreshCartFromServer = refreshCartFromServer;
    window.verifyStockBeforeAdd = verifyStockBeforeAdd;


    console.log('Catálogo inicializado correctamente con monitoreo sincronizado');
});