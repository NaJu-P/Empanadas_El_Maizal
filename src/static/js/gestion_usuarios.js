window.addEventListener('pageshow', function (event) {
    if (event.persisted || window.performance && performance.getEntriesByType("navigation")[0].type === "back_forward") {
        window.location.reload(); // Recarga sin caché
    }
});

let clienteEditandoId = null;
let domiciliarioEditandoId = null;

// FUNCIONES PARA CLIENTES
// Función para mostrar/ocultar contraseña de cliente
async function mostrarClaveCliente(id) {
    const input = document.getElementById('pass-' + id);
    const btn = input.nextElementSibling;
    
    if (input.type === 'password') {
        try {
            const response = await fetch('/obtener_clave/' + id);
            const data = await response.json();
            
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            input.type = 'text';
            input.value = data.clave;
            btn.innerHTML = '👁️‍🗨️';
            btn.title = 'Ocultar clave';
        } catch (error) {
            alert('Error al obtener la contraseña');
        }
    } else {
        input.type = 'password';
        input.value = '********';
        btn.innerHTML = '👁';
        btn.title = 'Mostrar clave';
    }
}

// Función para editar cliente
async function editarCliente(id) {
    try {
        const response = await fetch('/editar_cliente/' + id);
        const cliente = await response.json();
        
        if (cliente.error) {
            alert('Error: ' + cliente.error);
            return;
        }
        
        // Rellenar el formulario
        document.getElementById('edit_nombres').value = cliente.nombres_usuario;
        document.getElementById('edit_apellidos').value = cliente.apellidos_usuario;
        document.getElementById('edit_email').value = cliente.email_usuario;
        document.getElementById('edit_telefono').value = cliente.telefono;
        
        clienteEditandoId = id;
        document.getElementById('editModalCliente').style.display = 'block';
    } catch (error) {
        alert('Error al cargar los datos del cliente');
    }
}

// Función para cerrar modal de cliente
function cerrarModalCliente() {
    document.getElementById('editModalCliente').style.display = 'none';
    clienteEditandoId = null;
}

// Manejar envío del formulario de edición de cliente
document.getElementById('editFormCliente').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!clienteEditandoId) return;
    
    const formData = {
        nombres_usuario: document.getElementById('edit_nombres').value,
        apellidos_usuario: document.getElementById('edit_apellidos').value,
        email_usuario: document.getElementById('edit_email').value,
        telefono: document.getElementById('edit_telefono').value,
    };
    
    try {
        const response = await fetch('/editar_cliente/' + clienteEditandoId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert('Error: ' + result.error);
        } else {
            alert('Cliente actualizado exitosamente');
            location.reload();
        }
    } catch (error) {
        alert('Error al actualizar el cliente');
    }
});

// Función para confirmar eliminación de cliente
function confirmarEliminacionCliente(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este cliente?')) {
        eliminarCliente(id);
    }
}

// Función para eliminar cliente
async function eliminarCliente(id) {
    try {
        const response = await fetch('/eliminar_cliente/' + id, {
            method: 'POST'
        });
        
        if (response.ok) {
            location.reload();
        } else {
            alert('Error al eliminar el cliente');
        }
    } catch (error) {
        alert('Error al eliminar el cliente');
    }
}

// FUNCIONES PARA DOMICILIARIOS
// Función para mostrar/ocultar contraseña de domiciliario
async function mostrarClaveDomiciliario(id) {
    const input = document.getElementById('pass-dom-' + id);
    const btn = input.nextElementSibling;
    
    if (input.type === 'password') {
        try {
            const response = await fetch('/obtener_clave_domiciliario/' + id);
            const data = await response.json();
            
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            input.type = 'text';
            input.value = data.clave;
            btn.innerHTML = '👁️‍🗨️';
            btn.title = 'Ocultar clave';
        } catch (error) {
            alert('Error al obtener la contraseña del domiciliario');
        }
    } else {
        input.type = 'password';
        input.value = '********';
        btn.innerHTML = '👁';
        btn.title = 'Mostrar clave';
    }
}

// Función para editar domiciliario
async function editarDomiciliario(id) {
    try {
        const response = await fetch('/editar_domiciliario/' + id);
        const domiciliario = await response.json();
        
        if (domiciliario.error) {
            alert('Error: ' + domiciliario.error);
            return;
        }
        
        // Rellenar el formulario del domiciliario
        document.getElementById('edit_nombres_domiciliario').value = domiciliario.nombres_domiciliario;
        document.getElementById('edit_email_domiciliario').value = domiciliario.email_domiciliario;
        document.getElementById('edit_telefono_domiciliario').value = domiciliario.telefono;
        
        domiciliarioEditandoId = id;
        document.getElementById('editModalDomiciliario').style.display = 'block';
    } catch (error) {
        alert('Error al cargar los datos del domiciliario');
    }
}

// Función para cerrar modal de domiciliario
function cerrarModalDomiciliario() {
    document.getElementById('editModalDomiciliario').style.display = 'none';
    domiciliarioEditandoId = null;
}

// Manejar envío del formulario de edición de domiciliario
document.getElementById('editFormDomiciliario').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!domiciliarioEditandoId) return;
    
    const formData = {
        nombres_domiciliario: document.getElementById('edit_nombres_domiciliario').value,
        email_domiciliario: document.getElementById('edit_email_domiciliario').value,
        telefono: document.getElementById('edit_telefono_domiciliario').value
    };
    
    try {
        const response = await fetch('/editar_domiciliario/' + domiciliarioEditandoId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert('Error: ' + result.error);
        } else {
            alert('Domiciliario actualizado exitosamente');
            location.reload();
        }
    } catch (error) {
        alert('Error al actualizar el domiciliario');
    }
});

// Función para confirmar eliminación de domiciliario
function confirmarEliminacionDomiciliario(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este domiciliario?')) {
        eliminarDomiciliario(id);
    }
}

// Función para eliminar domiciliario
async function eliminarDomiciliario(id) {
    try {
        const response = await fetch('/eliminar_domiciliario/' + id, {
            method: 'POST'
        });
        
        if (response.ok) {
            location.reload();
        } else {
            alert('Error al eliminar el domiciliario');
        }
    } catch (error) {
        alert('Error al eliminar el domiciliario');
    }
}

// EVENT LISTENERS PARA CERRAR MODALES AL HACER CLIC FUERA
// Modal de cliente
document.getElementById('editModalCliente').addEventListener('click', function(e) {
    if (e.target === this) {
        cerrarModalCliente();
    }
});

// Modal de domiciliario
document.getElementById('editModalDomiciliario').addEventListener('click', function(e) {
    if (e.target === this) {
        cerrarModalDomiciliario();
    }
});

// Cerrar modales con la tecla Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        cerrarModalCliente();
        cerrarModalDomiciliario();
    }
});