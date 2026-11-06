// Colores para los gráficos
const backgroundColors = [
    'rgba(211, 84, 0, 0.7)',
    'rgba(241, 196, 15, 0.7)',
    'rgba(46, 204, 113, 0.7)',
    'rgba(52, 152, 219, 0.7)',
    'rgba(155, 89, 182, 0.7)',
    'rgba(26, 188, 156, 0.7)'
];

const borderColors = [
    'rgba(211, 84, 0, 1)',
    'rgba(241, 196, 15, 1)',
    'rgba(46, 204, 113, 1)',
    'rgba(52, 152, 219, 1)',
    'rgba(155, 89, 182, 1)',
    'rgba(26, 188, 156, 1)'
];

// Variables para los gráficos
let barChart, pieChart;
let currentPeriod = 'month';

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    setupPeriodButtons();
    loadAndUpdateData();
});

function setupPeriodButtons() {
    const timeButtons = document.querySelectorAll('.time-btn');
    
    // Obtener el período guardado en localStorage o usar 'week' por defecto
    const savedPeriod = localStorage.getItem('selectedPeriod') || 'week';
    currentPeriod = savedPeriod;
    
    // Remover la clase active de todos los botones
    timeButtons.forEach(btn => btn.classList.remove('active'));
    
    // Agregar la clase active al botón correspondiente al período guardado
    const buttonToActivate = document.querySelector(`[data-period="${savedPeriod}"]`);
    if (buttonToActivate) {
        buttonToActivate.classList.add('active');
    }
    
    timeButtons.forEach(button => {
        button.addEventListener('click', function() {
            timeButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            currentPeriod = this.dataset.period;
            
            // Guardar el período seleccionado en localStorage
            localStorage.setItem('selectedPeriod', currentPeriod);
            
            loadAndUpdateData();
        });
    });
}

async function loadAndUpdateData() {
    try {
        const url = `/api/ventas?periodo=${currentPeriod}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        
        if (!contentType || !contentType.includes('application/json')) {
            const textResponse = await response.text();
            throw new Error('La respuesta no es JSON válido');
        }
        
        const salesData = await response.json();
        
        if (!barChart || !pieChart) {
            initializeCharts(salesData);
        } else {
            updateCharts(salesData);
        }
        
        updateHighlight(salesData.topProduct);
        updateTable(salesData.productos, salesData.totalVentas);
        
    } catch (error) {
        alert(`Error al cargar los datos de ventas: ${error.message}`);
    }
}

function initializeCharts(salesData) {
    const barCtx = document.getElementById('barChart').getContext('2d');
    const pieCtx = document.getElementById('pieChart').getContext('2d');
    
    barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: salesData.labels,
            datasets: [{
                label: 'Ventas',
                data: salesData.data,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: context => `${context.parsed.y} unidades`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Unidades vendidas' }
                }
            }
        }
    });

    pieChart = new Chart(pieCtx, {
        type: 'pie',
        data: {
            labels: salesData.labels,
            datasets: [{
                data: salesData.data,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const value = context.raw;
                            const percentage = Math.round((value / total) * 100);
                            return `${context.label}: ${value} unidades (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function updateCharts(salesData) {
    barChart.data.labels = salesData.labels;
    barChart.data.datasets[0].data = salesData.data;
    barChart.update();

    pieChart.data.labels = salesData.labels;
    pieChart.data.datasets[0].data = salesData.data;
    pieChart.update();
}

function updateHighlight(topProduct) {
    const imgElement = document.getElementById('top-product-img');
    const nameElement = document.getElementById('top-product-name');
    const countElement = document.getElementById('top-product-count');
    const percentageElement = document.getElementById('top-product-percentage');
    
    imgElement.src = topProduct.image ? `/static/img/${topProduct.image}` : '/static/img/empanada-de-carne-molida.webp';
    imgElement.alt = topProduct.name;
    nameElement.textContent = topProduct.name;
    countElement.textContent = `${topProduct.count} unidades`;
    percentageElement.textContent = `${topProduct.percentage}% del total de ventas`;
}

function updateTable(productos, totalVentas) {
    const tableBody = document.getElementById('sales-table-body');
    tableBody.innerHTML = '';
    
    productos.forEach(producto => {
        const percentage = Math.round((producto.total / totalVentas) * 100);
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${producto.nombre}</td>
            <td>${producto.total} unidades</td>
            <td>${percentage}%</td>
        `;
        
        tableBody.appendChild(row);
    });
}