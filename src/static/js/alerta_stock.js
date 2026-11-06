// alerta_stock.js - Versión actualizada para consumir datos del backend

// Variables globales para almacenar datos
let empanadas = [];
let summary = {};
let alertas = [];

// Inicializar cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Obtener datos iniciales del backend (pasados desde el template)
    initializeData();
    
    // Actualizar interfaz
    updateStockSummary();
    updateStockTable();
    updateStockAlerts();
    
    // Configurar actualización automática cada 5 minutos
    setInterval(refreshAllData, 300000);
});

// Inicializar datos desde el backend
function initializeData() {
    try {
        // Los datos son pasados desde el template HTML
        if (window.stockData) {
            empanadas = window.stockData.empanadas || [];
            summary = window.stockData.summary || {};
            alertas = window.stockData.alertas || [];
        }
    } catch (error) {
        console.error('Error inicializando datos:', error);
        showError('Error al cargar los datos iniciales');
    }
}

// Actualizar resumen de stock
function updateStockSummary() {
    try {
        const totalElement = document.getElementById('total-productos');
        const bajoElement = document.getElementById('stock-bajo');
        const disponiblesElement = document.getElementById('disponibles');
        const criticoElement = document.getElementById('stock-critico');
        
        if (totalElement) totalElement.textContent = summary.total_productos || 0;
        if (bajoElement) bajoElement.textContent = summary.stock_bajo || 0;
        if (disponiblesElement) disponiblesElement.textContent = summary.disponibles || 0;
        if (criticoElement) criticoElement.textContent = summary.stock_critico || 0;
    } catch (error) {
        console.error('Error actualizando resumen:', error);
    }
}

// Actualizar tabla de stock
function updateStockTable() {
    try {
        const tbody = document.getElementById('stock-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (!empanadas || empanadas.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="empty-state">
                        <div class="empty-message">
                            <p>No hay productos en el inventario</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }
        
        empanadas.forEach(empanada => {
            const fila = document.createElement('tr');
            
            // Agregar clase según estado del stock
            if (empanada.estado_clase === 'critico') {
                fila.classList.add('critical-stock');
            } else if (empanada.estado_clase === 'bajo') {
                fila.classList.add('low-stock');
            }
            
            fila.innerHTML = `
                <td>${empanada.id_producto}</td>
                <td>${empanada.nombre}</td>
                <td>${empanada.descripcion}</td>
                <td class="stock-cell">${empanada.stock}</td>
                <td class="status-cell ${empanada.estado_clase}">${empanada.estado}</td>
            `;
            
            tbody.appendChild(fila);
        });
    } catch (error) {
        console.error('Error actualizando tabla:', error);
    }
}

// Actualizar alertas de stock
function updateStockAlerts() {
    try {
        const alertBanner = document.getElementById('alert-banner');
        if (!alertBanner) return;
        
        if (alertas && alertas.length > 0) {
            let mensaje = '⚠️ ALERTA DE STOCK: ';
            alertas.forEach((alerta, index) => {
                mensaje += `${alerta.nombre} (${alerta.stock} unidades)`;
                if (index < alertas.length - 1) {
                    mensaje += ', ';
                }
            });
            
            alertBanner.innerHTML = `<strong>${mensaje}</strong>`;
            alertBanner.style.display = 'block';
        } else {
            alertBanner.style.display = 'none';
        }
    } catch (error) {
        console.error('Error actualizando alertas:', error);
    }
}

// Refrescar todos los datos desde el backend
async function refreshAllData() {
    try {
        showLoading(true);
        
        // Obtener datos actualizados del backend
        const [stockResponse, summaryResponse, alertsResponse] = await Promise.all([
            fetch('/api/stock-empanadas'),
            fetch('/api/stock-summary'),
            fetch('/api/stock-alerts')
        ]);
        
        if (!stockResponse.ok || !summaryResponse.ok || !alertsResponse.ok) {
            throw new Error('Error al obtener datos del servidor');
        }
        
        empanadas = await stockResponse.json();
        summary = await summaryResponse.json();
        alertas = await alertsResponse.json();
        
        // Actualizar interfaz
        updateStockSummary();
        updateStockTable();
        updateStockAlerts();
        
        showSuccess('Datos actualizados correctamente');
        
    } catch (error) {
        console.error('Error refrescando datos:', error);
        showError('Error al actualizar los datos');
    } finally {
        showLoading(false);
    }
}

// Actualizar stock de un producto específico
async function updateProductStock(idProducto, nuevaCantidad) {
    try {
        showLoading(true);
        
        const response = await fetch('/api/update-stock', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id_producto: idProducto,
                nueva_cantidad: nuevaCantidad
            })
        });
        
        if (!response.ok) {
            throw new Error('Error al actualizar el stock');
        }
        
        const result = await response.json();
        
        // Refrescar datos después de actualizar
        await refreshAllData();
        
        showSuccess(result.message || 'Stock actualizado correctamente');
        
    } catch (error) {
        console.error('Error actualizando stock:', error);
        showError('Error al actualizar el stock');
    } finally {
        showLoading(false);
    }
}

// Exportar a CSV (usando endpoint del backend)
async function exportToCSV() {
    try {
        showLoading(true);
        
        const response = await fetch('/api/export-csv');
        if (!response.ok) {
            throw new Error('Error al exportar datos');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        link.href = url;
        link.download = `stock_empanadas_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.URL.revokeObjectURL(url);
        
        showSuccess('Archivo CSV descargado correctamente');
        
    } catch (error) {
        console.error('Error exportando a CSV:', error);
        showError('Error al exportar a CSV');
    } finally {
        showLoading(false);
    }
}

// Exportar a PDF (usando datos del backend)
async function exportToPDF() {
    try {
        showLoading(true);
        
        // Verificar que las librerías están cargadas
        if (!window.jspdf || !window.jspdf.jsPDF) {
            throw new Error('Las librerías para generar PDF no están cargadas correctamente');
        }
        
        // Obtener datos para PDF desde el backend
        const response = await fetch('/api/stock-data-pdf');
        if (!response.ok) {
            throw new Error('Error al obtener datos para PDF');
        }
        
        const pdfData = await response.json();
        
        // Inicializar jsPDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        // Configurar documento
        doc.setProperties({
            title: 'Reporte de Stock - Empanadas El Maizal',
            subject: 'Stock actual de empanadas',
            author: 'Empanadas El Maizal'
        });
        
        // Título
        doc.setFontSize(18);
        doc.text('Reporte de Stock - Empanadas El Maizal', 105, 20, { align: 'center' });
        
        // Fecha del reporte
        doc.setFontSize(12);
        doc.text(`Fecha: ${pdfData.fecha_reporte}`, 105, 30, { align: 'center' });
        
        // Resumen
        doc.setFontSize(14);
        doc.text('Resumen:', 20, 45);
        doc.setFontSize(10);
        doc.text(`Total productos: ${pdfData.summary.total}`, 20, 55);
        doc.text(`Stock bajo: ${pdfData.summary.bajo}`, 20, 65);
        doc.text(`Disponibles: ${pdfData.summary.disponibles}`, 20, 75);
        
        // Preparar datos para la tabla
        const tableData = pdfData.data.map(item => [
            item.id_producto,
            item.nombre,
            item.descripcion,
            item.stock,
            item.estado
        ]);
        
        // Generar tabla
        doc.autoTable({
            head: [['ID', 'Producto', 'Descripción', 'Stock', 'Estado']],
            body: tableData,
            startY: 85,
            headStyles: {
                fillColor: [231, 76, 60],
                textColor: 255,
                fontStyle: 'bold'
            },
            bodyStyles: {
                textColor: [40, 40, 40]
            },
            columnStyles: {
                0: { halign: 'center', cellWidth: 20 },
                3: { halign: 'center', cellWidth: 25 },
                4: { halign: 'center', cellWidth: 30 }
            },
            didDrawCell: (data) => {
                // Resaltar filas con stock bajo
                if (data.column.index === 4 && data.row.index >= 0) {
                    const estado = tableData[data.row.index][4];
                    if (estado === 'CRÍTICO' || estado === 'STOCK BAJO') {
                        doc.setFillColor(255, 243, 205);
                        doc.rect(data.cell.x, data.cell.y, data.cell.width, data.cell.height, 'F');
                    }
                }
            }
        });
        
        // Guardar PDF
        doc.save(`stock_empanadas_${new Date().toISOString().slice(0, 10)}.pdf`);
        
        showSuccess('PDF generado y descargado correctamente');
        
    } catch (error) {
        console.error('Error generando PDF:', error);
        showError('Error al generar el PDF');
    } finally {
        showLoading(false);
    }
}

// Funciones de utilidad para mostrar mensajes
function showLoading(show) {
    // Implementar indicador de carga
    const loadingElement = document.getElementById('loading-indicator');
    if (loadingElement) {
        loadingElement.style.display = show ? 'block' : 'none';
    }
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

function showNotification(message, type) {
    // Crear notificación temporal
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 10px 20px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        background-color: ${type === 'success' ? '#27ae60' : '#e74c3c'};
    `;
    
    document.body.appendChild(notification);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Función para buscar productos (opcional)
function searchProducts(searchTerm) {
    const filteredEmpanadas = empanadas.filter(empanada => 
        empanada.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        empanada.descripcion.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    updateStockTableWithData(filteredEmpanadas);
}

// Actualizar tabla con datos específicos
function updateStockTableWithData(data) {
    const tbody = document.getElementById('stock-table-body');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    data.forEach(empanada => {
        const fila = document.createElement('tr');
        
        if (empanada.estado_clase === 'critico') {
            fila.classList.add('critical-stock');
        } else if (empanada.estado_clase === 'bajo') {
            fila.classList.add('low-stock');
        }
        
        fila.innerHTML = `
            <td>${empanada.id_producto}</td>
            <td>${empanada.nombre}</td>
            <td>${empanada.descripcion}</td>
            <td class="stock-cell">${empanada.stock}</td>
            <td class="status-cell ${empanada.estado_clase}">${empanada.estado}</td>
        `;
        
        tbody.appendChild(fila);
    });
}

// Event listeners para botones de exportación
document.addEventListener('DOMContentLoaded', function() {
    // Botón CSV
    const csvButton = document.querySelector('.export-csv');
    if (csvButton) {
        csvButton.addEventListener('click', function(e) {
            e.preventDefault();
            exportToCSV();
        });
    }
    
    // Botón PDF
    const pdfButton = document.querySelector('.export-pdf');
    if (pdfButton) {
        pdfButton.addEventListener('click', function(e) {
            e.preventDefault();
            exportToPDF();
        });
    }
    
    // Botón de actualización manual (si existe)
    const refreshButton = document.getElementById('refresh-data');
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshAllData);
    }
});

// Funciones públicas para uso externo
window.stockManager = {
    refresh: refreshAllData,
    updateStock: updateProductStock,
    exportCSV: exportToCSV,
    exportPDF: exportToPDF,
    search: searchProducts
};