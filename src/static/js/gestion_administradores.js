// JS para la gestión de administradores

document.addEventListener('DOMContentLoaded', function() {
    const addBtn = document.querySelector('.add-admin-btn');
    if (addBtn) {
        addBtn.addEventListener('click', mostrarFormularioAgregar);
    }

    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const adminId = row.querySelector('td:first-child').textContent;
            const nombre = row.querySelector('td:nth-child(2)').textContent;
            const email = row.querySelector('td:nth-child(3)').textContent;
            const permisos = row.querySelector('td:nth-child(4)').textContent;
            mostrarFormularioEditar(adminId, nombre, email, permisos);
        });
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const adminId = row.querySelector('td:first-child').textContent;
            eliminarAdministrador(adminId);
        });
    });
});

function mostrarFormularioAgregar() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Agregar Administrador</h2>
            <form id="addAdminForm">
                <input type="text" name="nombre" placeholder="Nombre" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Contraseña" required>
                <select name="permisos">
                    <option value="Limitado">Limitado</option>
                    <option value="Total">Total</option>
                </select>
                <div class="button-group">
                    <button type="submit">Guardar</button>
                    <button type="button" onclick="this.closest('.modal').remove()">Cancelar</button>
                </div>
            </form>
        </div>
    `;
    document.body.appendChild(modal);

    modal.querySelector('form').addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = {
            nombre: formData.get('nombre'),
            email: formData.get('email'),
            password: formData.get('password'),
            permisos: formData.get('permisos')
        };

        try {
            const response = await fetch('/api/administradores', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                location.reload();
            } else {
                const error = await response.json();
                alert(error.error || 'Error al crear administrador');
            }
        } catch (error) {
            alert('Error de conexión');
        }
    });
}

function mostrarFormularioEditar(id, nombre, email, permisos) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Editar Administrador</h2>
            <form id="editAdminForm">
                <input type="text" name="nombre" value="${nombre}" required>
                <input type="email" name="email" value="${email}" required>
                <input type="password" name="password" placeholder="Nueva contraseña (opcional)">
                <select name="permisos">
                    <option value="Limitado" ${permisos === 'Limitado' ? 'selected' : ''}>Limitado</option>
                    <option value="Total" ${permisos === 'Total' ? 'selected' : ''}>Total</option>
                </select>
                <div class="button-group">
                    <button type="submit">Guardar</button>
                    <button type="button" onclick="this.closest('.modal').remove()">Cancelar</button>
                </div>
            </form>
        </div>
    `;
    document.body.appendChild(modal);

    modal.querySelector('form').addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = {
            nombre: formData.get('nombre'),
            email: formData.get('email'),
            permisos: formData.get('permisos')
        };
        
        if (formData.get('password')) {
            data.password = formData.get('password');
        }

        try {
            const response = await fetch(`/api/administradores/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                location.reload();
            } else {
                const error = await response.json();
                alert(error.error || 'Error al actualizar administrador');
            }
        } catch (error) {
            alert('Error de conexión');
        }
    });
}

async function eliminarAdministrador(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este administrador?')) {
        return;
    }

    try {
        const response = await fetch(`/api/administradores/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            location.reload();
        } else {
            const error = await response.json();
            alert(error.error || 'Error al eliminar administrador');
        }
    } catch (error) {
        alert('Error de conexión');
    }
}
