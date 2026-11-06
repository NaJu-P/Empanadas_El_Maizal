// opiniones.js - Código simplificado complementario
// Este archivo se mantiene como respaldo o funcionalidad adicional

document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de opiniones cargado como respaldo');
    
    // Función de utilidad para verificar SweetAlert2
    function verificarSweetAlert() {
        if (typeof Swal !== 'undefined') {
            console.log('SweetAlert2 disponible');
            return true;
        } else {
            console.log('SweetAlert2 no disponible, usar notificaciones nativas');
            return false;
        }
    }
    
    // Función alternativa para mostrar alertas
    function mostrarAlertaAlternativa(mensaje, tipo = 'info') {
        if (verificarSweetAlert()) {
            const iconos = {
                'success': 'success',
                'error': 'error',
                'info': 'info',
                'warning': 'warning'
            };
            
            Swal.fire({
                icon: iconos[tipo] || 'info',
                title: tipo === 'error' ? 'Error' : 'Información',
                text: mensaje,
                confirmButtonColor: '#FF6B35'
            });
        } else {
            // Fallback a alert nativo
            alert(mensaje);
        }
    }
    
    // Función de utilidad para formatear fechas
    function formatearFecha(fechaString) {
        const fecha = new Date(fechaString);
        return fecha.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    // Función de utilidad para generar estrellas HTML
    function generarEstrellasHTML(calificacion) {
        let estrellas = '';
        for (let i = 0; i < 5; i++) {
            estrellas += i < calificacion ? 
                '<i class="fas fa-star"></i>' : 
                '<i class="far fa-star"></i>';
        }
        return estrellas;
    }
    
    // Función de utilidad para validar email
    function validarEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }
    
    // Función de utilidad para sanitizar texto
    function sanitizarTexto(texto) {
        const div = document.createElement('div');
        div.textContent = texto;
        return div.innerHTML;
    }
    
    // Exportar funciones para uso global si es necesario
    window.OpinionesUtils = {
        mostrarAlerta: mostrarAlertaAlternativa,
        formatearFecha: formatearFecha,
        generarEstrellasHTML: generarEstrellasHTML,
        validarEmail: validarEmail,
        sanitizarTexto: sanitizarTexto
    };
    
    console.log('Utilidades de opiniones disponibles globalmente');
});