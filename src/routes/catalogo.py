from flask import Flask, Blueprint, render_template, request, jsonify, session, current_app 
from flask_caching import Cache
from db.conexion import get_db_connection
import traceback
from datetime import datetime
import hashlib
from routes.auth import login_required

catalogo_bp = Blueprint('catalogo', __name__)

def get_cache():
    """Obtiene la instancia de cache desde la aplicación Flask"""
    # Verificar si el cache está configurado
    if hasattr(current_app, 'cache'):
        return current_app.cache
    else:
        # Si no hay cache configurado, devolver None para manejar sin cache
        return None

def get_cache_key(user_id, cache_type):
    """Genera claves de cache consistentes para el usuario"""
    return f"user_{user_id}_{cache_type}"

def invalidate_user_cart_cache(user_id):
    """Invalida todo el cache relacionado con el carrito del usuario"""
    cache = get_cache()
    if cache is None:
        return  # Si no hay cache, no hacer nada
        
    cache_keys = [
        get_cache_key(user_id, "cart"),
        get_cache_key(user_id, "cart_status"),
        get_cache_key(user_id, "cart_version")
    ]
    
    for key in cache_keys:
        cache.delete(key)

def invalidate_products_cache():
    """Invalida el cache de productos"""
    cache = get_cache()
    if cache is None:
        return
    
    cache.delete("all_products")
    cache.delete("products_version")

def get_products_version():
    """Obtiene un hash que representa la versión actual de los productos"""
    conexion = None
    cursor = None
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Crear un hash basado en la suma de productos y sus cantidades
        # Esto nos permitirá detectar cambios en el inventario
        cursor.execute("""
            SELECT 
                COUNT(*) as total_productos,
                SUM(cantidad_disponible) as total_stock,
                MAX(id_producto) as max_id
            FROM producto 
            WHERE cantidad_disponible > 0
        """)
        
        result = cursor.fetchone()
        if result:
            version_data = f"{result[0]}:{result[1]}:{result[2]}"
            return hashlib.md5(version_data.encode()).hexdigest()[:12]
        
        return "empty"
        
    except Exception as e:
        print(f"Error al obtener versión de productos: {e}")
        return "error"
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

def get_all_products():
    """Obtiene todos los productos disponibles con cache optimizado"""
    cache = get_cache()
    
    # Si no hay cache disponible, ir directo a la base de datos
    if cache is None:
        return _fetch_products_from_db()
    
    # 1. Verificar si tenemos productos en cache
    cached_products = cache.get("all_products")
    cached_version = cache.get("products_version")
    
    # 2. Obtener versión actual de productos
    current_version = get_products_version()
    
    # 3. Si el cache es válido, devolverlo
    if cached_products is not None and cached_version == current_version:
        return cached_products
    
    productos = _fetch_products_from_db()
    
    # 5. Guardar en cache por 5 minutos (300 segundos)
    # Los productos no cambian tan frecuentemente
    cache.set("all_products", productos, timeout=300)
    cache.set("products_version", current_version, timeout=300)
    
    return productos

def _fetch_products_from_db():
    """Función auxiliar para obtener productos desde la base de datos"""
    conexion = None
    cursor = None
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Query optimizada para obtener productos con sus descripciones y estado
        cursor.execute("""
            SELECT 
                p.id_producto,
                p.nombre_producto,
                p.precio_producto,
                p.cantidad_disponible,
                p.img_producto,
                tp.descripcion_producto,
                CASE 
                    WHEN p.cantidad_disponible <= 0 THEN 'sin_stock'
                    WHEN p.cantidad_disponible <= 10 THEN 'stock_bajo'
                    ELSE 'disponible'
                END as estado_stock
            FROM producto p
            JOIN tipo_producto tp ON p.id_tipo_producto = tp.id_tipo_producto
            WHERE p.cantidad_disponible > 0
            ORDER BY p.id_producto
        """)
        
        productos = cursor.fetchall()
        
        # Convertir a lista de diccionarios para mayor facilidad de uso
        productos_lista = []
        for producto in productos:
            productos_lista.append({
                'id_producto': producto[0],
                'nombre_producto': producto[1],
                'precio_producto': float(producto[2]),
                'cantidad_disponible': producto[3],
                'img_producto': producto[4],
                'descripcion_producto': producto[5],
                'estado_stock': producto[6]
            })
        
        return productos_lista
        
    except Exception as e:
        print(f"Error en _fetch_products_from_db: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

@catalogo_bp.route("/Catalogo/verificar-stock", methods=["POST"])
@login_required
def verificar_stock():
    """Endpoint para verificar stock antes de agregar productos al carrito"""
    try:
        data = request.get_json()
        producto_id = data.get('producto_id')
        cantidad_solicitada = data.get('cantidad', 1)
        
        if not producto_id:
            return jsonify({"status": "error", "message": "ID de producto requerido"}), 400
        
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Verificar stock actual
        cursor.execute("""
            SELECT cantidad_disponible, nombre_producto 
            FROM producto 
            WHERE id_producto = %s
        """, (producto_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"status": "error", "message": "Producto no encontrado"}), 404
        
        stock_actual = result[0]
        nombre_producto = result[1]
        
        # Verificar si hay suficiente stock
        if stock_actual <= 0:
            return jsonify({
                "status": "error", 
                "message": f"{nombre_producto} está agotado",
                "stock_disponible": stock_actual,
                "estado": "agotado"
            }), 400
        
        if stock_actual <= 10:
            return jsonify({
                "status": "warning", 
                "message": f"⚠️ {nombre_producto} tiene stock bajo (quedan {stock_actual} unidades)",
                "stock_disponible": stock_actual,
                "estado": "stock_bajo"
            })
        
        if cantidad_solicitada > stock_actual:
            return jsonify({
                "status": "error", 
                "message": f"No hay suficiente stock. Disponible: {stock_actual}, Solicitado: {cantidad_solicitada}",
                "stock_disponible": stock_actual,
                "estado": "insuficiente"
            }), 400
        
        return jsonify({
            "status": "success", 
            "message": "Stock disponible",
            "stock_disponible": stock_actual,
            "estado": "disponible"
        })
        
    except Exception as e:
        print(f"Error en verificar_stock: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

def get_cart_version(user_id):
    """Obtiene la versión actual del carrito para detectar cambios"""
    conexion = None
    cursor = None
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        # Buscar la factura más reciente del usuario
        cursor.execute("""
            SELECT f.id_factura, mp.nombre_pago, f.fecha_compra, f.hora,
                COALESCE(SUM(df.cantidad_producto), 0) as total_items
            FROM facturacion f 
            JOIN metodo_pago mp ON f.id_pago = mp.id_pago 
            LEFT JOIN detalle_facturacion df ON f.id_factura = df.id_factura
            WHERE f.id_usuario = %s 
            ORDER BY CONCAT(f.fecha_compra, ' ', f.hora) DESC
            LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if result:
            # Crear un hash que represente el estado actual
            version_data = f"{result[0]}:{result[1]}:{result[3]}"
            version_hash = hashlib.md5(version_data.encode()).hexdigest()[:8]
            return {
                'version': version_hash,
                'id_factura': result[0],
                'metodo_pago': result[1],
                'total_items': result[4]
            }
        
        return {'version': 'empty', 'id_factura': None, 'metodo_pago': None, 'total_items': 0}
        
    except Exception as e:
        print(f"Error al obtener versión del carrito: {e}")
        return {'version': 'error', 'id_factura': None, 'metodo_pago': None, 'total_items': 0}
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

# Función pública para invalidar cache cuando se actualice inventario
def invalidar_cache_productos():
    """Función pública para invalidar cache desde otros módulos (ej: cuando se actualiza stock)"""
    invalidate_products_cache()

@catalogo_bp.route("/Catalogo")
@login_required
def catalogo():
    """Renderiza el catálogo con todos los productos disponibles"""
    try:
        # Obtener todos los productos (ahora con cache optimizado)
        productos = get_all_products()
        
        # Pasar los productos al template
        return render_template('catalogo/catalogo_empanadas.html', productos=productos)
        
    except Exception as e:
        print(f"Error al cargar catálogo: {e}")
        # En caso de error, enviar lista vacía
        return render_template('catalogo/catalogo_empanadas.html', productos=[])

@catalogo_bp.route("/Catalogo/version-carrito", methods=["GET"])
def version_carrito():
    """Endpoint ligero para verificar si el carrito ha cambiado"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({"status": "error", "message": "Usuario no autenticado"}), 401
        
        cache = get_cache()
        cached_version = None
        
        # Solo usar cache si está disponible
        if cache is not None:
            cache_key = get_cache_key(user_id, "cart_version")
            cached_version = cache.get(cache_key)
        
        if cached_version is None:
            # No está en cache o no hay cache, consultar DB
            version_info = get_cart_version(user_id)
            
            # Solo guardar en cache si está disponible
            if cache is not None:
                cache_key = get_cache_key(user_id, "cart_version")
                cache.set(cache_key, version_info, timeout=30)
        else:
            version_info = cached_version
        
        return jsonify({
            "status": "success", 
            "version": version_info['version'],
            "metodo_pago": version_info['metodo_pago'],
            "total_items": version_info['total_items']
        })
        
    except Exception as e:
        print(f"Error en version_carrito: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@catalogo_bp.route("/Catalogo/cargar-carrito", methods=["GET"])
def cargar_carrito_catalogo():
    """Endpoint para cargar el carrito - versión debug"""
    
    try:
        # 1. Verificar sesión
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({
                "status": "error", 
                "message": "Usuario no autenticado",
                "debug": "No hay user_id en session"
            }), 401
        
        # 2. Intentar conexión a BD
        conexion = get_db_connection()
        
        if conexion is None:
            return jsonify({
                "status": "error", 
                "message": "Error de conexión a la base de datos",
                "debug": "get_db_connection() retornó None"
            }), 500
        
        cursor = conexion.cursor()
        
        # Primero verificar si el usuario existe
        cursor.execute("SELECT COUNT(*) FROM facturacion WHERE id_usuario = %s", (user_id,))
        count = cursor.fetchone()[0]
        
        # Query principal simplificada
        cursor.execute("""
            SELECT f.id_factura, mp.nombre_pago
            FROM facturacion f 
            JOIN metodo_pago mp ON f.id_pago = mp.id_pago 
            WHERE f.id_usuario = %s 
            ORDER BY f.fecha_compra DESC, f.hora DESC
            LIMIT 5
        """, (user_id,))
        
        facturas = cursor.fetchall()
        
        # Buscar factura pendiente
        factura_pendiente = None
        for factura in facturas:
            if factura[1] == 'no_pago':
                factura_pendiente = factura
                break
        
        carrito = {}
        
        if factura_pendiente:
            id_factura = factura_pendiente[0]
            
            # Cargar productos
            cursor.execute("""
                SELECT df.id_producto, df.cantidad_producto, p.nombre_producto, p.precio_producto
                FROM detalle_facturacion df
                JOIN producto p ON df.id_producto = p.id_producto
                WHERE df.id_factura = %s
            """, (id_factura,))
            
            productos = cursor.fetchall()
            print(f"🍕 Productos en carrito: {productos}")
            
            for producto in productos:
                carrito[str(producto[0])] = {
                    'quantity': producto[1],
                    'name': producto[2],
                    'price': float(producto[3])
                }
        
        cursor.close()
        conexion.close()
        
        resultado = {
            "status": "success", 
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        
        return jsonify({
            "status": "error", 
            "message": error_msg,
            "debug": {
                "traceback": traceback_str,
                "error_type": type(e).__name__
            }
        }), 500
    
    finally:
        pass

@catalogo_bp.route("/Catalogo/estado-stock", methods=["GET"])
@login_required
def estado_stock():
    """Endpoint para obtener el estado actual del stock de todos los productos"""
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        
        cursor.execute("""
            SELECT 
                p.id_producto,
                p.nombre_producto,
                p.cantidad_disponible,
                CASE 
                    WHEN p.cantidad_disponible <= 0 THEN 'agotado'
                    WHEN p.cantidad_disponible <= 10 THEN 'stock_bajo'
                    ELSE 'disponible'
                END as estado
            FROM producto p
            ORDER BY p.id_producto
        """)
        
        productos = cursor.fetchall()
        
        estado_productos = {}
        for producto in productos:
            estado_productos[str(producto[0])] = {
                'nombre': producto[1],
                'cantidad': producto[2],
                'estado': producto[3]
            }
        
        return jsonify({
            "status": "success",
            "productos": estado_productos
        })
        
    except Exception as e:
        print(f"Error en estado_stock: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

@catalogo_bp.route("/Catalogo/limpiar-carrito", methods=["POST"])
def limpiar_carrito():
    """Endpoint para limpiar completamente el carrito del usuario"""
    conexion = None
    cursor = None
    
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({"status": "error", "message": "Usuario no autenticado"}), 401
        
        # Invalidar cache
        invalidate_user_cart_cache(user_id)
        
        conexion = get_db_connection()
        cursor = conexion.cursor()

        # Eliminar todos los detalles de facturas pendientes
        cursor.execute("""
            DELETE df FROM detalle_facturacion df
            JOIN facturacion f ON df.id_factura = f.id_factura
            JOIN metodo_pago mp ON f.id_pago = mp.id_pago
            WHERE f.id_usuario = %s AND mp.nombre_pago = 'no_pago'
        """, (user_id,))
        
        conexion.commit()
        
        return jsonify({"status": "success", "message": "Carrito limpiado"})
        
    except Exception as e:
        print(f"Error en limpiar_carrito: {e}")
        if conexion:
            conexion.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

# Función auxiliar para llamar desde otras partes de la aplicación
def invalidar_carrito_usuario(user_id):
    """Función pública para invalidar el carrito desde otros módulos"""
    invalidate_user_cart_cache(user_id)

@catalogo_bp.route("/Catalogo/test", methods=["GET"])
def test_endpoint():
    """Endpoint simple para verificar que Flask funciona"""
    return jsonify({
        "status": "success",
        "message": "Flask está funcionando",
        "session": dict(session),
        "timestamp": datetime.now().isoformat()
    })

# ===== NUEVO ENDPOINT PARA FORZAR REFRESH DEL CACHE =====
@catalogo_bp.route("/Catalogo/refresh-productos", methods=["POST"])
@login_required
def refresh_productos():
    """Endpoint para invalidar manualmente el cache de productos"""
    try:
        invalidate_products_cache()
        return jsonify({
            "status": "success",
            "message": "Cache de productos invalidado correctamente"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al invalidar cache: {str(e)}"
        }), 500