from flask import Blueprint, render_template, jsonify, request, make_response
from datetime import datetime, timedelta
from db.conexion import get_db_connection
from mysql.connector import Error
import csv
import io
import json
from routes.admin import admin_login_required

alerta_stock_bp = Blueprint('alerta_stock', __name__)

# Constantes para configuración
STOCK_BAJO_THRESHOLD = 10
STOCK_CRITICO_THRESHOLD = 5

@alerta_stock_bp.route('/admin/alerta-stock')
@admin_login_required
def stock_empanadas():
    """Renderiza la página principal de stock de empanadas con datos"""
    connection = get_db_connection()
    if not connection:
        return render_template('alerta-stock/alerta-stock.html.j2', 
                             empanadas=[], 
                             summary={}, 
                             alertas=[],
                             error="Error de conexión a la base de datos")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Obtener datos de empanadas - consulta corregida para tu BD
        empanadas_query = """
        SELECT 
            p.id_producto,
            p.nombre_producto as nombre,
            tp.descripcion_producto as descripcion,
            p.cantidad_disponible as stock,
            p.precio_producto as precio,
            p.img_producto
        FROM producto p
        JOIN tipo_producto tp ON p.id_tipo_producto = tp.id_tipo_producto
        ORDER BY p.cantidad_disponible ASC, p.nombre_producto ASC
        """
        cursor.execute(empanadas_query)
        empanadas = cursor.fetchall()
        
        # Procesar datos y calcular estado
        for empanada in empanadas:
            stock_cantidad = empanada['stock']
            
            # Determinar estado del stock
            if stock_cantidad <= STOCK_CRITICO_THRESHOLD:
                empanada['estado'] = 'CRÍTICO'
                empanada['estado_clase'] = 'critico'
            elif stock_cantidad <= STOCK_BAJO_THRESHOLD:
                empanada['estado'] = 'STOCK BAJO'
                empanada['estado_clase'] = 'bajo'
            else:
                empanada['estado'] = 'Disponible'
                empanada['estado_clase'] = 'disponible'
            
            # Formatear precio
            empanada['precio'] = f"${empanada['precio']:,.0f}"
        
        # Obtener resumen estadístico - consulta corregida
        summary_query = """
        SELECT 
            COUNT(*) as total_productos,
            SUM(CASE WHEN cantidad_disponible <= %s THEN 1 ELSE 0 END) as stock_bajo,
            SUM(CASE WHEN cantidad_disponible > %s THEN 1 ELSE 0 END) as disponibles,
            SUM(CASE WHEN cantidad_disponible <= %s THEN 1 ELSE 0 END) as stock_critico,
            AVG(cantidad_disponible) as promedio_stock,
            MIN(cantidad_disponible) as stock_minimo,
            MAX(cantidad_disponible) as stock_maximo
        FROM producto p
        JOIN tipo_producto tp ON p.id_tipo_producto = tp.id_tipo_producto
        """
        cursor.execute(summary_query, (STOCK_BAJO_THRESHOLD, STOCK_BAJO_THRESHOLD, STOCK_CRITICO_THRESHOLD))
        summary = cursor.fetchone()
        
        # Calcular porcentajes
        total = summary['total_productos']
        if total > 0:
            summary['porcentaje_bajo'] = round((summary['stock_bajo'] / total) * 100, 1)
            summary['porcentaje_disponibles'] = round((summary['disponibles'] / total) * 100, 1)
            summary['porcentaje_critico'] = round((summary['stock_critico'] / total) * 100, 1)
        else:
            summary['porcentaje_bajo'] = 0
            summary['porcentaje_disponibles'] = 0
            summary['porcentaje_critico'] = 0
        
        # Formatear promedio
        summary['promedio_stock'] = round(summary['promedio_stock'], 1) if summary['promedio_stock'] else 0
        
        # Obtener alertas de stock bajo - consulta corregida
        alertas_query = """
        SELECT 
            p.id_producto,
            p.nombre_producto as nombre,
            p.cantidad_disponible as stock,
            tp.descripcion_producto as descripcion,
            CASE 
                WHEN p.cantidad_disponible <= %s THEN 'CRÍTICO'
                WHEN p.cantidad_disponible <= %s THEN 'BAJO'
                ELSE 'NORMAL'
            END as nivel_alerta
        FROM producto p
        JOIN tipo_producto tp ON p.id_tipo_producto = tp.id_tipo_producto
        WHERE p.cantidad_disponible <= %s
        ORDER BY p.cantidad_disponible ASC
        """
        cursor.execute(alertas_query, (STOCK_CRITICO_THRESHOLD, STOCK_BAJO_THRESHOLD, STOCK_BAJO_THRESHOLD))
        alertas = cursor.fetchall()
        
        # Renderizar template con datos
        return render_template('alerta-stock/alerta-stock.html.j2', 
                             empanadas=empanadas, 
                             summary=summary, 
                             alertas=alertas,
                             config={'STOCK_BAJO_THRESHOLD': STOCK_BAJO_THRESHOLD, 
                                   'STOCK_CRITICO_THRESHOLD': STOCK_CRITICO_THRESHOLD})
        
    except Error as e:
        print(f"Error fetching stock data: {e}")
        return render_template('alerta-stock/alerta-stock.html.j2', 
                             empanadas=[], 
                             summary={}, 
                             alertas=[],
                             error="Error al obtener datos de stock")
    except Exception as e:
        print(f"Unexpected error: {e}")
        return render_template('alerta-stock/alerta-stock.html.j2', 
                             empanadas=[], 
                             summary={}, 
                             alertas=[],
                             error="Error interno del servidor")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@alerta_stock_bp.route('/api/stock-empanadas')
def get_stock_data():
    """Obtiene todos los datos de stock para la tabla principal (API)"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            p.id_producto,
            p.nombre_producto as nombre,
            tp.descripcion_producto as descripcion,
            p.cantidad_disponible as stock,
            p.precio_producto as precio,
            p.img_producto
        FROM producto p
        JOIN tipo_producto tp ON p.id_tipo_producto = tp.id_tipo_producto
        ORDER BY p.cantidad_disponible ASC, p.nombre_producto ASC
        """
        cursor.execute(query)
        empanadas = cursor.fetchall()
        
        # Procesar datos y calcular estado
        for empanada in empanadas:
            stock_cantidad = empanada['stock']
            
            # Determinar estado del stock
            if stock_cantidad <= STOCK_CRITICO_THRESHOLD:
                empanada['estado'] = 'CRÍTICO'
                empanada['estado_clase'] = 'critico'
            elif stock_cantidad <= STOCK_BAJO_THRESHOLD:
                empanada['estado'] = 'STOCK BAJO'
                empanada['estado_clase'] = 'bajo'
            else:
                empanada['estado'] = 'Disponible'
                empanada['estado_clase'] = 'disponible'
            
            # Formatear precio
            empanada['precio'] = f"${empanada['precio']:,.0f}"
        
        return jsonify(empanadas)
        
    except Error as e:
        print(f"Error fetching stock data: {e}")
        return jsonify({'error': 'Error al obtener datos de stock'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@alerta_stock_bp.route('/api/stock-summary')
def get_stock_summary():
    """Obtiene el resumen estadístico del stock (API)"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            COUNT(*) as total_productos,
            SUM(CASE WHEN cantidad_disponible <= %s THEN 1 ELSE 0 END) as stock_bajo,
            SUM(CASE WHEN cantidad_disponible > %s THEN 1 ELSE 0 END) as disponibles,
            SUM(CASE WHEN cantidad_disponible <= %s THEN 1 ELSE 0 END) as stock_critico,
            AVG(cantidad_disponible) as promedio_stock,
            MIN(cantidad_disponible) as stock_minimo,
            MAX(cantidad_disponible) as stock_maximo
        FROM producto p
        JOIN tipo_producto tp ON p.id_tipo_producto = tp.id_tipo_producto
        """
        cursor.execute(query, (STOCK_BAJO_THRESHOLD, STOCK_BAJO_THRESHOLD, STOCK_CRITICO_THRESHOLD))
        summary = cursor.fetchone()
        
        # Calcular porcentajes
        total = summary['total_productos']
        if total > 0:
            summary['porcentaje_bajo'] = round((summary['stock_bajo'] / total) * 100, 1)
            summary['porcentaje_disponibles'] = round((summary['disponibles'] / total) * 100, 1)
            summary['porcentaje_critico'] = round((summary['stock_critico'] / total) * 100, 1)
        else:
            summary['porcentaje_bajo'] = 0
            summary['porcentaje_disponibles'] = 0
            summary['porcentaje_critico'] = 0
        
        # Formatear promedio
        summary['promedio_stock'] = round(summary['promedio_stock'], 1) if summary['promedio_stock'] else 0
        
        return jsonify(summary)
        
    except Error as e:
        print(f"Error fetching stock summary: {e}")
        return jsonify({'error': 'Error al obtener resumen de stock'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@alerta_stock_bp.route('/api/stock-alerts')
def get_stock_alerts():
    """Obtiene productos con stock bajo para alertas (API)"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            p.id_producto,
            p.nombre_producto as nombre,
            p.cantidad_disponible as stock,
            tp.descripcion_producto as descripcion,
            CASE 
                WHEN p.cantidad_disponible <= %s THEN 'CRÍTICO'
                WHEN p.cantidad_disponible <= %s THEN 'BAJO'
                ELSE 'NORMAL'
            END as nivel_alerta
        FROM producto p
        JOIN tipo_producto tp ON p.id_tipo_producto = tp.id_tipo_producto
        WHERE p.cantidad_disponible <= %s
        ORDER BY p.cantidad_disponible ASC
        """
        cursor.execute(query, (STOCK_CRITICO_THRESHOLD, STOCK_BAJO_THRESHOLD, STOCK_BAJO_THRESHOLD))
        alerts = cursor.fetchall()
        
        return jsonify(alerts)
        
    except Error as e:
        print(f"Error fetching stock alerts: {e}")
        return jsonify({'error': 'Error al obtener alertas de stock'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@alerta_stock_bp.route('/api/export-csv')
def export_to_csv():
    """Exporta los datos de stock a formato CSV"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            p.id_producto as 'ID',
            p.nombre_producto as 'Producto',
            tp.descripcion_producto as 'Descripción',
            p.cantidad_disponible as 'Stock',
            p.precio_producto as 'Precio',
            CASE 
                WHEN p.cantidad_disponible <= %s THEN 'CRÍTICO'
                WHEN p.cantidad_disponible <= %s THEN 'STOCK BAJO'
                ELSE 'Disponible'
            END as 'Estado'
        FROM producto p
        JOIN tipo_producto tp ON p.id_tipo_producto = tp.id_tipo_producto
        ORDER BY p.cantidad_disponible ASC
        """
        cursor.execute(query, (STOCK_CRITICO_THRESHOLD, STOCK_BAJO_THRESHOLD))
        data = cursor.fetchall()
        
        # Crear archivo CSV en memoria
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            
            for row in data:
                # Formatear datos para CSV
                if row['Precio']:
                    row['Precio'] = f"${row['Precio']:,.0f}"
                writer.writerow(row)
        
        # Crear respuesta
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=stock_empanadas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Error as e:
        print(f"Error exporting to CSV: {e}")
        return jsonify({'error': 'Error al exportar a CSV'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@alerta_stock_bp.route('/api/stock-data-pdf')
def get_stock_data_for_pdf():
    """Obtiene datos formateados para exportación a PDF"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            p.id_producto,
            p.nombre_producto as nombre,
            tp.descripcion_producto as descripcion,
            p.cantidad_disponible as stock,
            p.precio_producto as precio,
            CASE 
                WHEN p.cantidad_disponible <= %s THEN 'CRÍTICO'
                WHEN p.cantidad_disponible <= %s THEN 'STOCK BAJO'
                ELSE 'Disponible'
            END as estado
        FROM producto p
        JOIN tipo_producto tp ON p.id_tipo_producto = tp.id_tipo_producto
        ORDER BY p.cantidad_disponible ASC
        """
        cursor.execute(query, (STOCK_CRITICO_THRESHOLD, STOCK_BAJO_THRESHOLD))
        data = cursor.fetchall()
        
        # Formatear datos para PDF
        for item in data:
            item['precio'] = f"${item['precio']:,.0f}"
        
        # Obtener resumen
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN cantidad_disponible <= %s THEN 1 ELSE 0 END) as bajo,
                SUM(CASE WHEN cantidad_disponible > %s THEN 1 ELSE 0 END) as disponibles
            FROM producto p
        """, (STOCK_BAJO_THRESHOLD, STOCK_BAJO_THRESHOLD))
        
        summary = cursor.fetchone()
        
        return jsonify({
            'data': data,
            'summary': summary,
            'fecha_reporte': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        })
        
    except Error as e:
        print(f"Error fetching data for PDF: {e}")
        return jsonify({'error': 'Error al obtener datos para PDF'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@alerta_stock_bp.route('/api/update-stock', methods=['POST'])
@admin_login_required
def update_stock():
    """Actualiza el stock de un producto específico"""
    data = request.get_json()
    
    if not data or 'id_producto' not in data or 'nueva_cantidad' not in data:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        query = """
        UPDATE producto 
        SET cantidad_disponible = %s
        WHERE id_producto = %s
        """
        cursor.execute(query, (data['nueva_cantidad'], data['id_producto']))
        connection.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'message': 'Stock actualizado correctamente'})
        else:
            return jsonify({'error': 'Producto no encontrado'}), 404
            
    except Error as e:
        print(f"Error updating stock: {e}")
        connection.rollback()
        return jsonify({'error': 'Error al actualizar stock'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def init_stock_system(app):
    """Inicializa el sistema de stock con configuraciones adicionales"""
    # Configuraciones específicas para el sistema de stock
    app.config['STOCK_BAJO_THRESHOLD'] = STOCK_BAJO_THRESHOLD
    app.config['STOCK_CRITICO_THRESHOLD'] = STOCK_CRITICO_THRESHOLD
    
    # Registrar el blueprint
    app.register_blueprint(alerta_stock_bp)
    
    print("Sistema de stock inicializado correctamente")

# Funciones auxiliares
def get_stock_status(cantidad):
    """Determina el estado del stock según la cantidad"""
    if cantidad <= STOCK_CRITICO_THRESHOLD:
        return 'CRÍTICO'
    elif cantidad <= STOCK_BAJO_THRESHOLD:
        return 'STOCK BAJO'
    else:
        return 'Disponible'

def format_currency(amount):
    """Formatea un monto como moneda"""
    return f"${amount:,.0f}"