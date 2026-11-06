// Variables globales
let currentOperation = null;
let currentProductId = null;
let productos = productosData || [];

// Referencias al DOM
const modal = document.getElementById('operationModal');
const modalTitle = document.getElementById('modalTitle');
const modalInput = document.getElementById('modalInput');
const modalConfirm = document.getElementById('modalConfirm');
const modalCancel = document.getElementById('modalCancel');
const closeSpan = document.querySelector('.close');

// Función para mostrar alertas
function showAlert(message, type = 'success') {
    const alert = document.getElementById(type === 'success' ? 'successAlert' : 'errorAlert');
    alert.textContent = message;
    alert.style.display = 'block';
    setTimeout(() => {
        alert.style.display = 'none';
    }, 3000);
}

// Función para peticiones HTTP
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Error en la petición');
        return data;
    } catch (error) {
        console.error('Error en la petición:', error);
        throw error;
    }
}

// Actualizar stock en el DOM y en el arreglo local
function updateQuantityInDOM(productId, newQuantity) {
    const productCard = document.querySelector(`[data-id="${productId}"]`);
    if (productCard) {
        const quantitySpan = productCard.querySelector('.quantity-value');
        if (quantitySpan) quantitySpan.textContent = newQuantity;
    }

    const productIndex = productos.findIndex(p => p.id === productId);
    if (productIndex !== -1) productos[productIndex].quantity = newQuantity;
}

// Eliminar producto del DOM y del arreglo local
function removeProductFromDOM(productId) {
    const productCard = document.querySelector(`[data-id="${productId}"]`);
    if (productCard) productCard.remove();

    productos = productos.filter(p => p.id !== productId);

    if (productos.length === 0) {
        document.getElementById('productsGrid').innerHTML = '<p>No hay productos disponibles.</p>';
    }
}

// Agregar producto visualmente
function addProductToDOM(producto) {
    const grid = document.getElementById('productsGrid');
    if (grid.querySelector('p')) grid.innerHTML = '';

    const productCard = document.createElement('div');
    productCard.className = 'product-card';
    productCard.setAttribute('data-id', producto.id);
    productCard.innerHTML = `
        <img src="/static/images/${producto.image}" alt="${producto.name}" class="product-image"
             onerror="this.src='/static/images/default-empanada.png'">
        <div class="product-name">${producto.name}</div>
        <div class="product-quantity">Stock: <span class="quantity-value">${producto.quantity}</span></div>
        <div class="product-price">$${producto.price.toFixed(2)}</div>
        <div class="product-description">${producto.description}</div>
        <div class="product-actions">
           <button class="btn btn-add btn-action" onclick="openModal('add', ${producto.id})"><i class='fa fa-plus'></i> Agregar</button>
            <button class="btn btn-edit btn-action" onclick="openModal('edit', ${producto.id})"><i class='fa fa-edit'></i> Modificar</button>
            <button class="btn btn-remove btn-action" onclick="openModal('remove', ${producto.id})"><i class='fa fa-minus'></i> Quitar</button>
            <button class="btn btn-delete btn-action" onclick="deleteProduct(${producto.id})"><i class='fa fa-trash'></i> Eliminar</button>
        </div>
    `;

    grid.appendChild(productCard);
    productos.push(producto);
}

// Abrir el modal para operaciones
function openModal(operation, productId) {
    currentOperation = operation;
    currentProductId = productId;

    const product = productos.find(p => p.id === productId);
    if (!product) return showAlert('Producto no encontrado', 'error');

    modalTitle.textContent = `${operation === 'add' ? 'Agregar' : operation === 'edit' ? 'Modificar' : 'Quitar'} stock - ${product.name}`;
    modalInput.placeholder = operation === 'edit' ? 'Nueva cantidad total' : 'Cantidad';
    modalInput.value = operation === 'edit' ? product.quantity : '';
    modal.style.display = 'block';
    modalInput.focus();
}

// Cerrar modal
function closeModal() {
    modal.style.display = 'none';
    modalInput.value = '';
    currentOperation = null;
    currentProductId = null;
}

// Confirmar operación de stock
async function confirmOperation() {
    const quantity = parseInt(modalInput.value);
    if (isNaN(quantity) || quantity < 0) return showAlert('Por favor ingrese una cantidad válida', 'error');

    const product = productos.find(p => p.id === currentProductId);
    if (!product) return;

    try {
        let nuevaCantidad;

        if (currentOperation === 'add') {
            if (quantity <= 0) return showAlert('La cantidad debe ser mayor a 0', 'error');
            nuevaCantidad = product.quantity + quantity;
        } else if (currentOperation === 'remove') {
            if (quantity > product.quantity) return showAlert('No puedes quitar más unidades de las que tienes', 'error');
            nuevaCantidad = product.quantity - quantity;
        } else if (currentOperation === 'edit') {
            nuevaCantidad = quantity;
        }

        await makeRequest(`/api/productos/${currentProductId}/cantidad`, {
            method: 'PUT',
            body: JSON.stringify({ cantidad: nuevaCantidad })
        });

        updateQuantityInDOM(currentProductId, nuevaCantidad);

        const opMsg = currentOperation === 'add' ? `Se agregaron ${quantity} unidades` :
            currentOperation === 'remove' ? `Se quitaron ${quantity} unidades` :
            `Stock actualizado a ${nuevaCantidad} unidades`;

        showAlert(`${opMsg} de ${product.name}`);
        closeModal();

    } catch (error) {
        showAlert('Error al actualizar el producto: ' + error.message, 'error');
    }
}

// Eliminar producto
async function deleteProduct(productId) {
    const product = productos.find(p => p.id === productId);
    if (!product) return showAlert('Producto no encontrado', 'error');

    if (confirm(`¿Estás seguro de que quieres eliminar "${product.name}"?`)) {
        try {
            await makeRequest(`/api/productos/${productId}`, { method: 'DELETE' });
            removeProductFromDOM(productId);
            showAlert(`${product.name} eliminado exitosamente`);
        } catch (error) {
            showAlert('Error al eliminar el producto: ' + error.message, 'error');
        }
    }
}

// Agregar nuevo producto con imagen
async function addNewProduct(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const name = formData.get('productName').trim();
    const image = formData.get('productImage').trim();
    const quantity = parseInt(formData.get('initialQuantity'));
    const price = parseFloat(formData.get('productPrice'));
    const description = formData.get('productDescription').trim();

    if (!name || !image || isNaN(quantity) || isNaN(price) || !description) {
        return showAlert('Por favor complete todos los campos correctamente', 'error');
    }

    if (quantity < 0 || price < 0) {
        return showAlert('La cantidad y el precio deben ser positivos', 'error');
    }

    try {
        await makeRequest('/api/productos', {
            method: 'POST',
            body: JSON.stringify({
                nombre: name,
                imagen: image,
                cantidad: quantity,
                precio: price,
                descripcion: description
            })
        });

        showAlert(`${name} agregado exitosamente`);
        setTimeout(() => window.location.reload(), 1500);
        document.getElementById('addProductForm').reset();
    } catch (error) {
        showAlert('Error al agregar el producto: ' + error.message, 'error');
    }
}

// Event listeners
document.getElementById('addProductForm').addEventListener('submit', addNewProduct);
modalConfirm.addEventListener('click', confirmOperation);
modalCancel.addEventListener('click', closeModal);
closeSpan.addEventListener('click', closeModal);

// Cerrar modal al hacer clic fuera de él
window.addEventListener('click', (event) => {
    if (event.target === modal) closeModal();
});

// Confirmar con Enter
modalInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') confirmOperation();
});