document.addEventListener('DOMContentLoaded', function() {
    // Inicializar funciones solo si los elementos existen
    initializeFilters();
    initializeSearch();
    initializeDropdown();
    
    // Solo ejecutar funciones de estadísticas si estamos en la página correcta
    if (document.getElementById('ventasMes')) {
        initializeDatePickers();
        cargarEstadisticas();
        cargarVentas();
        initializeFormHandlers();
    }
});

function initializeDropdown() {
    // Dropdown menu functionality
    const userIcon = document.getElementById('user-icon');
    const dropdownMenu = document.getElementById('dropdown-menu');
    
    if (userIcon && dropdownMenu) {
        userIcon.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });
        
        // Cerrar dropdown al hacer clic fuera
        document.addEventListener('click', function() {
            dropdownMenu.classList.remove('show');
        });
    }
}

function initializeDatePickers() {
    // Solo inicializar si los elementos existen
    const fechaInicioElement = document.getElementById('fechaInicio');
    const fechaFinElement = document.getElementById('fechaFin');
    
    if (!fechaInicioElement || !fechaFinElement) return;

    const commonConfig = {
        locale: 'es',
        dateFormat: 'd-m-Y',
        maxDate: 'today',
        disableMobile: true,
        animate: true,
        static: true,
        allowInput: true,
        altFormat: 'd-m-Y',
        altInput: true,
        altInputClass: 'form-control form-control-sm',
        formatDate: (date) => {
            return date.getDate() + '-' +
                (date.getMonth() + 1) + '-' +
                date.getFullYear();
        }
    };

    const fechaInicio = flatpickr('#fechaInicio', {
        ...commonConfig,
        defaultDate: null,
        placeholder: 'Fecha inicial',
        onChange: function(selectedDates) {
            if (selectedDates[0]) {
                fechaFin.set('minDate', selectedDates[0]);
            }
        }
    });

    const fechaFin = flatpickr('#fechaFin', {
        ...commonConfig,
        defaultDate: new Date(),
        onChange: function(selectedDates) {
            if (selectedDates[0]) {
                fechaInicio.set('maxDate', selectedDates[0]);
            }
        }
    });
}

function initializeFormHandlers() {
    // Event listener for Excel export
    const btnExportar = document.getElementById('btnExportar');
    if (btnExportar) {
        btnExportar.addEventListener('click', function() {
            const tabla = document.getElementById('tablaVentas');
            if (tabla) {
                const wb = XLSX.utils.table_to_book(tabla, { sheet: "Ventas" });
                XLSX.writeFile(wb, `Reporte_Ventas_${new Date().toISOString().split('T')[0]}.xlsx`);
            }
        });
    }

    // Event listener for form submission
    const formFiltros = document.getElementById('formFiltros');
    if (formFiltros) {
        formFiltros.addEventListener('submit', async function(e) {
            e.preventDefault();

            try {
                const fechaInicio = document.getElementById('fechaInicio').value;
                const fechaFin = document.getElementById('fechaFin').value;

                const response = await fetch(`/api/ventas?inicio=${fechaInicio}&fin=${fechaFin}`);
                if (!response.ok) throw new Error('Error al cargar datos');

                const ventas = await response.json();
                actualizarTablaVentas(ventas);

            } catch (error) {
                console.error('Error:', error);
                alert('Error al cargar los datos');
            }
        });
    }
}

function actualizarTablaVentas(ventas) {
    const tbody = document.querySelector('#tablaVentas tbody');
    if (!tbody) return;

    tbody.innerHTML = '';

    ventas.forEach(venta => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${venta.fecha_compra} ${venta.hora}</td>
            <td>${venta.nombre_producto}</td>
            <td class="text-center">${venta.cantidad_producto}</td>
            <td class="text-end">$${parseFloat(venta.precio_unitario).toLocaleString()}</td>
            <td class="text-end">$${parseFloat(venta.subtotal).toLocaleString()}</td>
            <td>${venta.cliente}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function cargarEstadisticas() {
    try {
        const response = await fetch('/api/estadisticas');
        if (!response.ok) throw new Error('Error al cargar estadísticas');
        
        const data = await response.json();

        // Solo actualizar si los elementos existen
        const ventasMes = document.getElementById('ventasMes');
        if (ventasMes) {
            ventasMes.textContent = `$${parseFloat(data.ventas_mes || 0).toLocaleString()}`;
        }

        const productosVendidos = document.getElementById('productosVendidos');
        if (productosVendidos) {
            productosVendidos.textContent = parseFloat(data.productos_vendidos || 0).toLocaleString();
        }

        const totalClientes = document.getElementById('totalClientes');
        if (totalClientes) {
            totalClientes.textContent = parseFloat(data.total_clientes || 0).toLocaleString();
        }

    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
    }
}

async function cargarVentas() {
    try {
        const fechaInicioElement = document.getElementById('fechaInicio');
        const fechaFinElement = document.getElementById('fechaFin');
        
        const fechaInicio = fechaInicioElement ? fechaInicioElement.value : '';
        const fechaFin = fechaFinElement ? fechaFinElement.value : '';

        const response = await fetch(`/api/ventas?inicio=${fechaInicio}&fin=${fechaFin}`);
        if (!response.ok) throw new Error('Error al cargar ventas');
        
        const ventas = await response.json();
        actualizarTablaVentas(ventas);

    } catch (error) {
        console.error('Error al cargar ventas:', error);
    }
}

function initializeFilters() {
    const sortBySelect = document.getElementById('sort-by');
    const sortOrderSelect = document.getElementById('sort-order');
    
    if (sortBySelect && sortOrderSelect) {
        sortBySelect.addEventListener('change', sortTable);
        sortOrderSelect.addEventListener('change', sortTable);
    }
}

function initializeSearch() {
    const searchInput = document.getElementById('search-product');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('#sales-table tbody tr');
            
            tableRows.forEach(row => {
                const productName = row.getAttribute('data-producto');
                if (productName && productName.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}

function sortTable() {
    const sortBy = document.getElementById('sort-by');
    const sortOrder = document.getElementById('sort-order');
    const tbody = document.querySelector('#sales-table tbody');
    
    if (!sortBy || !sortOrder || !tbody) return;
    
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        let aValue, bValue;
        
        switch (sortBy.value) {
            case 'producto':
                aValue = a.getAttribute('data-producto');
                bValue = b.getAttribute('data-producto');
                break;
            case 'total_vendido':
                aValue = parseInt(a.getAttribute('data-vendido'));
                bValue = parseInt(b.getAttribute('data-vendido'));
                break;
            case 'total_ingresos':
                aValue = parseFloat(a.getAttribute('data-ingresos'));
                bValue = parseFloat(b.getAttribute('data-ingresos'));
                break;
            default:
                return 0;
        }
        
        if (sortBy.value === 'producto') {
            // Ordenamiento alfabético
            if (sortOrder.value === 'asc') {
                return aValue.localeCompare(bValue);
            } else {
                return bValue.localeCompare(aValue);
            }
        } else {
            // Ordenamiento numérico
            if (sortOrder.value === 'asc') {
                return aValue - bValue;
            } else {
                return bValue - aValue;
            }
        }
    });
    
    // Reordenar las filas en el DOM
    rows.forEach(row => tbody.appendChild(row));
}

function exportToCSV() {
    const table = document.getElementById('sales-table') || document.getElementById('tablaVentas');
    
    if (!table) {
        alert('No se encontró la tabla de ventas');
        return;
    }
    
    const rows = table.querySelectorAll('tr');
    const csvData = [];
    
    // Procesar cada fila
    rows.forEach((row, index) => {
        const cols = row.querySelectorAll(index === 0 ? 'th' : 'td');
        const rowData = [];
        
        cols.forEach(col => {
            // Limpiar el texto y remover caracteres especiales
            let text = col.textContent.trim();
            // Remover iconos y caracteres especiales (pero mantener números y signos de moneda)
            text = text.replace(/[^\w\s$.,%-]/g, '');
            // Escapar comillas dobles
            text = text.replace(/"/g, '""');
            // Envolver en comillas si contiene comas
            if (text.includes(',')) {
                text = `"${text}"`;
            }
            rowData.push(text);
        });
        
        csvData.push(rowData.join(','));
    });
    
    // Crear y descargar el archivo CSV
    const csvContent = '\uFEFF' + csvData.join('\n'); // Agregar BOM para caracteres especiales
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `reporte_ventas_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url); // Limpiar el objeto URL
    } else {
        alert('Su navegador no soporta la descarga de archivos CSV');
    }
}

// Funciones para reportes
function toggleReportes() {
    const menu = document.getElementById('reportesMenu');
    if (menu) {
        menu.classList.toggle('show');
    }
}

function generarReporte(tipo) {
    const menu = document.getElementById('reportesMenu');
    if (menu) {
        menu.classList.remove('show');
    }

    // Configurar fechas según el tipo de reporte
    const today = new Date();
    let startDate, endDate;

    switch (tipo) {
        case 'diario':
            startDate = endDate = today;
            break;
        case 'semanal':
            startDate = new Date(today.setDate(today.getDate() - 7));
            endDate = new Date();
            break;
        case 'mensual':
            startDate = new Date(today.getFullYear(), today.getMonth(), 1);
            endDate = new Date();
            break;
    }

    // Actualizar los date pickers si existen
    const fechaInicioElement = document.getElementById('fechaInicio');
    const fechaFinElement = document.getElementById('fechaFin');
    
    if (fechaInicioElement && fechaFinElement) {
        fechaInicioElement.value = startDate.toISOString().split('T')[0];
        fechaFinElement.value = endDate.toISOString().split('T')[0];

        // Trigger form submission
        const formFiltros = document.getElementById('formFiltros');
        if (formFiltros) {
            formFiltros.dispatchEvent(new Event('submit'));
        }
    }
}

// Cerrar menú de reportes al hacer clic fuera
document.addEventListener('click', function(e) {
    const menu = document.getElementById('reportesMenu');
    const btn = document.getElementById('reportesBtn');
    if (menu && btn && !btn.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.remove('show');
    }
});

// Funciones utilitarias
function refreshData() {
    location.reload();
}

function formatNumber(num) {
    return new Intl.NumberFormat('es-CO').format(num);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(amount);
}

function animateValue(element, start, end, duration) {
    if (!element) return;
    
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            clearInterval(timer);
            current = end;
        }
        element.textContent = formatCurrency(current);
    }, 16);
}