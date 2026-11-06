from flask import Blueprint, jsonify, request, render_template
from datetime import datetime, timedelta
from db.conexion import get_db_connection
import mysql.connector
from mysql.connector import Error
from routes.admin import admin_login_required

# Configuración del Blueprint porcentaje_ventas
porcentaje_ventas_bp = Blueprint('porcentaje_ventas', __name__)

# Funciones de servicio
def get_sales_data(periodo='month'):
    """
    Obtiene datos de ventas por período especificado
    """
    connection = None
    cursor = None
    
    try:
        # Obtener conexión a la base de datos
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Calcular fecha de inicio según el período
        hoy = datetime.now()
        
        if periodo == 'day':
            fecha_inicio = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'week':
            fecha_inicio = hoy - timedelta(days=hoy.weekday())
            fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'year':
            fecha_inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # month
            fecha_inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Query para obtener ventas por producto
        query = """
        SELECT 
            p.nombre_producto,
            p.img_producto,
            SUM(df.cantidad_producto) as total
        FROM producto p
        INNER JOIN detalle_facturacion df ON df.id_producto = p.id_producto
        INNER JOIN facturacion f ON f.id_factura = df.id_factura
        WHERE f.fecha_compra >= %s
        GROUP BY p.id_producto, p.nombre_producto, p.img_producto
        ORDER BY total DESC
        """
        
        cursor.execute(query, (fecha_inicio.date(),))
        ventas_por_producto = cursor.fetchall()
        
        # Procesar datos
        labels = []
        data = []
        productos = []
        
        for producto in ventas_por_producto:
            labels.append(producto['nombre_producto'])
            data.append(int(producto['total']))
            productos.append({
                'nombre': producto['nombre_producto'],
                'imagen': producto['img_producto'],
                'total': int(producto['total'])
            })
        
        # Calcular totales
        total_ventas = sum(data) if data else 0
        
        # Producto más vendido
        top_product = {
            'name': ventas_por_producto[0]['nombre_producto'] if ventas_por_producto else 'N/A',
            'image': ventas_por_producto[0]['img_producto'] if ventas_por_producto else '',
            'count': int(ventas_por_producto[0]['total']) if ventas_por_producto else 0,
            'percentage': round((ventas_por_producto[0]['total'] / total_ventas * 100), 1) if ventas_por_producto and total_ventas > 0 else 0
        }
        
        return {
            'labels': labels,
            'data': data,
            'topProduct': top_product,
            'productos': productos,
            'totalVentas': total_ventas
        }
        
    except Error as e:
        print(f"Error al obtener datos de ventas: {e}")
        return {
            'labels': [],
            'data': [],
            'topProduct': {'name': 'Error', 'image': '', 'count': 0, 'percentage': 0},
            'productos': [],
            'totalVentas': 0
        }
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_sales_by_period_detailed(periodo='month'):
    """
    Obtiene datos detallados de ventas por período con información adicional
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Calcular fecha de inicio según el período
        hoy = datetime.now()
        
        if periodo == 'day':
            fecha_inicio = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'week':
            fecha_inicio = hoy - timedelta(days=hoy.weekday())
            fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'year':
            fecha_inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # month
            fecha_inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Query más detallada con información de facturación
        query = """
        SELECT 
            p.nombre_producto,
            p.img_producto,
            p.precio_producto,
            SUM(df.cantidad_producto) as total_vendido,
            COUNT(DISTINCT f.id_factura) as numero_facturas,
            SUM(df.cantidad_producto * p.precio_producto) as total_ingresos
        FROM producto p
        INNER JOIN detalle_facturacion df ON df.id_producto = p.id_producto
        INNER JOIN facturacion f ON f.id_factura = df.id_factura
        WHERE f.fecha_compra >= %s
        GROUP BY p.id_producto, p.nombre_producto, p.img_producto, p.precio_producto
        ORDER BY total_vendido DESC
        """
        
        cursor.execute(query, (fecha_inicio.date(),))
        ventas_detalladas = cursor.fetchall()
        
        # Procesar datos detallados
        productos_detallados = []
        total_ingresos_general = 0
        
        for producto in ventas_detalladas:
            total_ingresos_general += float(producto['total_ingresos'])
            productos_detallados.append({
                'nombre': producto['nombre_producto'],
                'imagen': producto['img_producto'],
                'precio': float(producto['precio_producto']),
                'total_vendido': int(producto['total_vendido']),
                'numero_facturas': int(producto['numero_facturas']),
                'total_ingresos': float(producto['total_ingresos'])
            })
        
        return {
            'productos': productos_detallados,
            'total_ingresos_general': total_ingresos_general,
            'total_productos_vendidos': sum(p['total_vendido'] for p in productos_detallados)
        }
        
    except Error as e:
        print(f"Error al obtener datos detallados de ventas: {e}")
        return {
            'productos': [],
            'total_ingresos_general': 0,
            'total_productos_vendidos': 0
        }
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_sales_statistics(periodo='month'):
    """
    Obtiene estadísticas generales de ventas
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Calcular fecha de inicio según el período
        hoy = datetime.now()
        
        if periodo == 'day':
            fecha_inicio = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'week':
            fecha_inicio = hoy - timedelta(days=hoy.weekday())
            fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'year':
            fecha_inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # month
            fecha_inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Estadísticas generales
        stats_query = """
        SELECT 
            COUNT(DISTINCT f.id_factura) as total_facturas,
            SUM(df.cantidad_producto) as total_productos_vendidos,
            AVG(df.cantidad_producto) as promedio_productos_por_factura,
            COUNT(DISTINCT f.id_usuario) as clientes_unicos
        FROM facturacion f
        INNER JOIN detalle_facturacion df ON df.id_factura = f.id_factura
        WHERE f.fecha_compra >= %s
        """
        
        cursor.execute(stats_query, (fecha_inicio.date(),))
        estadisticas = cursor.fetchone()
        
        # Ventas por día
        ventas_por_dia_query = """
        SELECT 
            DATE(f.fecha_compra) as fecha,
            SUM(df.cantidad_producto) as total_vendido
        FROM facturacion f
        INNER JOIN detalle_facturacion df ON df.id_factura = f.id_factura
        WHERE f.fecha_compra >= %s
        GROUP BY DATE(f.fecha_compra)
        ORDER BY fecha
        """
        
        cursor.execute(ventas_por_dia_query, (fecha_inicio.date(),))
        ventas_por_dia = cursor.fetchall()
        
        # Método de pago más usado
        metodo_pago_query = """
        SELECT 
            mp.nombre_pago,
            COUNT(f.id_factura) as total_uso
        FROM facturacion f
        INNER JOIN metodo_pago mp ON mp.id_pago = f.id_pago
        WHERE f.fecha_compra >= %s
        GROUP BY mp.id_pago, mp.nombre_pago
        ORDER BY total_uso DESC
        LIMIT 1
        """
        
        cursor.execute(metodo_pago_query, (fecha_inicio.date(),))
        metodo_pago_preferido = cursor.fetchone()
        
        return {
            'total_facturas': int(estadisticas['total_facturas']) if estadisticas['total_facturas'] else 0,
            'total_productos_vendidos': int(estadisticas['total_productos_vendidos']) if estadisticas['total_productos_vendidos'] else 0,
            'promedio_productos_por_factura': round(float(estadisticas['promedio_productos_por_factura']), 2) if estadisticas['promedio_productos_por_factura'] else 0,
            'clientes_unicos': int(estadisticas['clientes_unicos']) if estadisticas['clientes_unicos'] else 0,
            'ventas_por_dia': [
                {
                    'fecha': venta['fecha'].strftime('%Y-%m-%d'),
                    'total_vendido': int(venta['total_vendido'])
                } for venta in ventas_por_dia
            ],
            'metodo_pago_preferido': metodo_pago_preferido['nombre_pago'] if metodo_pago_preferido else 'N/A'
        }
        
    except Error as e:
        print(f"Error al obtener estadísticas de ventas: {e}")
        return {
            'total_facturas': 0,
            'total_productos_vendidos': 0,
            'promedio_productos_por_factura': 0,
            'clientes_unicos': 0,
            'ventas_por_dia': [],
            'metodo_pago_preferido': 'N/A'
        }
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Rutas del Blueprint
@porcentaje_ventas_bp.route('/admin/porcentaje-ventas')
@admin_login_required
def ventas_page():
    """
    Página principal de ventas
    """
    return render_template('porcentaje_ventas/diseño.html')

@porcentaje_ventas_bp.route('/api/ventas', methods=['GET'])
@admin_login_required
def obtener_ventas():
    """
    API para obtener datos de ventas básicos
    """
    periodo = request.args.get('periodo', 'month')
    
    # Validar período
    if periodo not in ['day', 'week', 'month', 'year']:
        return jsonify({'error': 'Período inválido'}), 400
    
    try:
        data = get_sales_data(periodo)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': f'Error al obtener datos: {str(e)}'}), 500

@porcentaje_ventas_bp.route('/api/ventas/top-productos', methods=['GET'])
@admin_login_required
def obtener_top_productos():
    """
    API para obtener los productos más vendidos
    """
    periodo = request.args.get('periodo', 'month')
    
    # Validar período
    if periodo not in ['day', 'week', 'month', 'year']:
        return jsonify({'error': 'Período inválido'}), 400
    
    try:
        data = get_sales_data(periodo)
        return jsonify({
            'topProduct': data['topProduct'],
            'productos': data['productos']
        })
    except Exception as e:
        return jsonify({'error': f'Error al obtener productos: {str(e)}'}), 500

@porcentaje_ventas_bp.route('/api/ventas/detalladas', methods=['GET'])
@admin_login_required
def obtener_ventas_detalladas():
    """
    API para obtener datos detallados de ventas con ingresos
    """
    periodo = request.args.get('periodo', 'month')
    
    # Validar período
    if periodo not in ['day', 'week', 'month', 'year']:
        return jsonify({'error': 'Período inválido'}), 400
    
    try:
        data = get_sales_by_period_detailed(periodo)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': f'Error al obtener datos detallados: {str(e)}'}), 500

@porcentaje_ventas_bp.route('/api/ventas/estadisticas', methods=['GET'])
@admin_login_required
def obtener_estadisticas():
    """
    API para obtener estadísticas generales de ventas
    """
    periodo = request.args.get('periodo', 'month')
    
    # Validar período
    if periodo not in ['day', 'week', 'month', 'year']:
        return jsonify({'error': 'Período inválido'}), 400
    
    try:
        data = get_sales_statistics(periodo)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

@porcentaje_ventas_bp.route('/api/ventas/resumen', methods=['GET'])
@admin_login_required
def obtener_resumen_completo():
    """
    API para obtener un resumen completo de ventas
    """
    periodo = request.args.get('periodo', 'month')
    
    # Validar período
    if periodo not in ['day', 'week', 'month', 'year']:
        return jsonify({'error': 'Período inválido'}), 400
    
    try:
        # Obtener todos los datos
        ventas_basicas = get_sales_data(periodo)
        ventas_detalladas = get_sales_by_period_detailed(periodo)
        estadisticas = get_sales_statistics(periodo)
        
        # Combinar todo en un resumen
        resumen = {
            'periodo': periodo,
            'fecha_consulta': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'resumen_basico': ventas_basicas,
            'detalle_productos': ventas_detalladas,
            'estadisticas_generales': estadisticas
        }
        
        return jsonify(resumen)
    except Exception as e:
        return jsonify({'error': f'Error al obtener resumen: {str(e)}'}), 500