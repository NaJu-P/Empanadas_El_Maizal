from flask import Blueprint, render_template, session, current_app, g
from db.conexion import get_db_connection
from functools import wraps
import hashlib
from routes.auth import login_required


comprobante_bp = Blueprint('Comprobante', __name__)

def cache_key_for_comprobante(id_factura, user_id):
    """Genera una clave única de cache para el comprobante"""
    return f"comprobante_{id_factura}_{user_id}"

def user_specific_cache(timeout=300):
    """Decorador para cache específico por usuario"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si hay usuario logueado
            user_id = session.get('user_id')
            if not user_id:
                return f(*args, **kwargs)
            
            # Generar clave de cache
            id_factura = kwargs.get('id_factura')
            cache_key = cache_key_for_comprobante(id_factura, user_id)
            
            # Intentar obtener del cache
            try:
                cached_result = current_app.cache.get(cache_key)
                if cached_result:
                    return cached_result
            except Exception as e:
                print(f"Error al acceder al cache: {e}")
            
            # Ejecutar función y cachear resultado
            result = f(*args, **kwargs)
            
            try:
                current_app.cache.set(cache_key, result, timeout=timeout)
            except Exception as e:
                print(f"Error al guardar en cache: {e}")
            
            return result
        return decorated_function
    return decorator

def get_comprobante_data(id_factura, user_id):
    """Función optimizada para obtener datos del comprobante"""
    conexion = get_db_connection()
    
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Query principal optimizada
        cursor.execute(
            """
            SELECT 
                u.id_usuario,
                u.nombres_usuario,
                u.apellidos_usuario,
                u.email_usuario,
                u.telefono,
                ub.direccion_usuario,
                f.id_factura,
                f.fecha_compra,
                mp.nombre_pago,
                df.id_detalle,
                df.cantidad_producto,
                p.nombre_producto,
                p.precio_producto
            FROM usuario u
            INNER JOIN ubicacion ub ON u.id_usuario = ub.id_usuario
            INNER JOIN facturacion f ON u.id_usuario = f.id_usuario
            INNER JOIN metodo_pago mp ON f.id_pago = mp.id_pago
            INNER JOIN detalle_facturacion df ON df.id_factura = f.id_factura
            INNER JOIN producto p ON p.id_producto = df.id_producto
            WHERE f.id_factura = %s AND u.id_usuario = %s
            """,
            (id_factura, user_id)
        )
        productos = cursor.fetchall()
        
        # Segunda query optimizada
        cursor.execute(
            """
            SELECT 
                u.id_usuario,
                f.id_factura,
                df.id_detalle,
                df.cantidad_producto,
                p.id_producto,
                p.nombre_producto,
                p.precio_producto,
                tp.descripcion_producto
            FROM usuario u
            INNER JOIN facturacion f ON u.id_usuario = f.id_usuario
            INNER JOIN detalle_facturacion df ON df.id_factura = f.id_factura
            INNER JOIN producto p ON p.id_producto = df.id_producto
            INNER JOIN tipo_producto tp ON tp.id_tipo_producto = p.id_tipo_producto
            WHERE f.id_factura = %s
            """,
            (id_factura,)
        )
        
        datos = cursor.fetchall()
        
        return productos, datos
        
    except Exception as e:
        print(f"Error en consulta de base de datos: {e}")
        return [], []
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

@comprobante_bp.route("/Tus-Comprobantes/Comprobante-<int:id_factura>")
@login_required
@user_specific_cache(timeout=600)  # Cache por 10 minutos
def comprobante(id_factura):
    user_id = session.get('user_id')
    
    if not user_id:
        # Redirigir al login si no hay usuario
        from flask import redirect, url_for, flash
        flash('Debes iniciar sesión para ver tus comprobantes', 'warning')
        return redirect(url_for('auth.login'))
    
    print(f"Usuario: {user_id}, Factura: {id_factura}")
    
    # Obtener datos de la base de datos
    productos, datos = get_comprobante_data(id_factura, user_id)
    
    if not productos:
        # Manejar caso donde no se encuentra el comprobante
        from flask import abort
        abort(404)
    
    return render_template("/tus_facturas/facturacion.html", 
                         productos=productos[0], 
                         datos=datos)

# Función para invalidar cache cuando se actualice una factura
def invalidate_comprobante_cache(id_factura, user_id=None):
    """Invalida el cache de un comprobante específico"""
    try:
        if user_id:
            # Invalidar cache específico del usuario
            cache_key = cache_key_for_comprobante(id_factura, user_id)
            current_app.cache.delete(cache_key)
        else:
            # Si no se especifica usuario, invalidar todos los caches relacionados
            # Esto es menos eficiente pero más seguro
            cache_pattern = f"comprobante_{id_factura}_*"
            # Flask-Caching no soporta patrones, así que usamos delete_many si está disponible
            # o implementamos una solución personalizada
            pass
    except Exception as e:
        print(f"Error al invalidar cache: {e}")

# Agregar funciones de utilidad para el cache
@comprobante_bp.before_app_request
def setup_cache_utils():
    """Configurar utilidades de cache en g"""
    g.invalidate_comprobante_cache = invalidate_comprobante_cache