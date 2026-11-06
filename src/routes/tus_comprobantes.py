from flask import Blueprint, render_template, session, request
from db.conexion import get_db_connection
from datetime import datetime, timedelta
import threading
from routes.auth import login_required

tus_comprobantes_bp = Blueprint('tus-Comprobantes', __name__)

# Caché global con lock para thread safety
_cache = {}
_cache_lock = threading.Lock()
CACHE_DURATION = timedelta(minutes=5)

def get_cached_comprobantes(user_id):
    """Obtiene comprobantes del caché si están disponibles y válidos"""
    with _cache_lock:
        cache_key = f'comprobantes_{user_id}'
        if cache_key in _cache:
            data, timestamp = _cache[cache_key]
            if datetime.now() - timestamp < CACHE_DURATION:
                return data
    return None

def set_cached_comprobantes(user_id, data):
    """Guarda comprobantes en el caché"""
    with _cache_lock:
        cache_key = f'comprobantes_{user_id}'
        _cache[cache_key] = (data, datetime.now())

@tus_comprobantes_bp.route("/Tus-Comprobantes")
@login_required
def tus_comprobantes():
    user_id = session.get('user_id')
    force_refresh = request.args.get('refresh', False)
    
    # Intentar obtener del caché solo si no se fuerza el refresh
    productos = None if force_refresh else get_cached_comprobantes(user_id)
    
    if productos is not None:
        return render_template("/tus_facturas/tus_facturas.html", productos=productos)
    
    # Intentar obtener del caché
    productos = get_cached_comprobantes(user_id)
    
    if productos is not None:
        return render_template("/tus_facturas/tus_facturas.html", productos=productos)
    
    # Si no hay caché, hacer consulta
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    
    cursor.execute(
        """
        SELECT 
            usuario.id_usuario,
            facturacion.id_factura,
            facturacion.fecha_compra,
            facturacion.hora,
            metodo_pago.nombre_pago
        FROM usuario
        INNER JOIN facturacion ON usuario.id_usuario = facturacion.id_usuario
        INNER JOIN metodo_pago ON facturacion.id_pago = metodo_pago.id_pago
        WHERE usuario.id_usuario = %s
        AND metodo_pago.nombre_pago != 'no_pago'
        ORDER BY facturacion.id_factura DESC
        """,
        (user_id,)
    )
    productos = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    # Guardar en caché
    set_cached_comprobantes(user_id, productos)
    
    return render_template("/tus_facturas/tus_facturas.html", productos=productos)