from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, g, current_app
from flask_caching import Cache
from db.conexion import get_db_connection
import time
from datetime import datetime
import hashlib
from routes.auth import login_required

carrito_bp = Blueprint('carrito', __name__)

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
        get_cache_key(user_id, "cart_version"),
        get_cache_key(user_id, "cart_productos")
    ]
    
    for key in cache_keys:
        cache.delete(key)

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

def obtener_carrito_productos():
    """Obtener los productos del carrito del usuario actual desde la base de datos"""
    user_id = session.get('user_id')

    if not user_id:
        return []
    
    cache = get_cache()
    cached_productos = None
    
    # Solo verificar cache si está disponible
    if cache is not None:
        cache_key = get_cache_key(user_id, "cart_productos")
        cached_productos = cache.get(cache_key)
    
    if cached_productos is not None:
        return cached_productos
        
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        # MEJORA: Consulta más específica para evitar conflictos
        cursor.execute("""
            SELECT 
                producto.id_producto,
                producto.nombre_producto,
                producto.precio_producto,
                producto.img_producto,
                producto.cantidad_disponible,
                detalle_facturacion.cantidad_producto,
                facturacion.id_factura
            FROM usuario
            INNER JOIN facturacion ON usuario.id_usuario = facturacion.id_usuario
            INNER JOIN detalle_facturacion ON facturacion.id_factura = detalle_facturacion.id_factura
            INNER JOIN producto ON detalle_facturacion.id_producto = producto.id_producto
            INNER JOIN metodo_pago ON facturacion.id_pago = metodo_pago.id_pago
            WHERE usuario.id_usuario = %s
            AND metodo_pago.nombre_pago = %s
            ORDER BY facturacion.fecha_compra DESC, facturacion.id_factura DESC
        """, (user_id, 'no_pago'))

        productos = cursor.fetchall()
        cursor.close()
        conexion.close()

        # Solo guardar en cache si está disponible
        if cache is not None:
            cache_key = get_cache_key(user_id, "cart_productos")
            cache.set(cache_key, productos, timeout=120)

        return productos

    except Exception as e:
        print(f"Error al obtener carrito: {e}")
        # Limpiar cache en caso de error
        if cache is not None:
            invalidate_user_cart_cache(user_id)
        return []

def invalidar_cache_despues_pago(user_id):
    """Invalidar completamente el cache del usuario después de un pago"""
    invalidate_user_cart_cache(user_id)
    print(f"Cache invalidado para usuario {user_id} después del pago")

def invalidar_cache_carrito(user_id):
    """Invalidar cache cuando se modifica el carrito"""
    invalidate_user_cart_cache(user_id)
    print(f"Cache invalidado para usuario {user_id}")

def limpiar_cache_usuario(user_id):
    """Función para limpiar completamente el cache de un usuario"""
    invalidate_user_cart_cache(user_id)
    print(f"Cache completamente limpiado para usuario {user_id}")

@carrito_bp.route("/Carrito")
@login_required
def carrito():
    # Verificar si el usuario está logueado
    if not session.get('user_id'):
        return redirect(url_for('auth.login_page'))
    
    # Obtener productos del carrito del usuario
    productos = obtener_carrito_productos()
    
    return render_template(
        'carrito/carrito_de_compras.html',
        productos=productos,
        producto=productos  # Agregamos también como 'producto' por si el HTML lo usa
    )

@carrito_bp.route('/Carrito/obtener-carrito', methods=['GET'])
@login_required
def obtener_carrito():
    try:
        if not session.get('user_id'):
            return jsonify({'status': 'error', 'message': 'Usuario no autenticado'}), 401
        
        user_id = session.get('user_id')
        
        productos = obtener_carrito_productos()
        
        # Convertir a formato que espera el frontend
        cart = {
            str(p['id_producto']): {
                'name': p['nombre_producto'],
                'price': float(p['precio_producto']),
                'quantity': int(p['cantidad_producto']),
                'img': p['img_producto'],
                'stock': int(p['cantidad_disponible'])
            }
            for p in productos
        }
        
        return jsonify({
            'status': 'success',
            'cart': cart,
            'timestamp': int(time.time())
        })
    except Exception as e:
        print(f"Error al obtener carrito: {e}")
        # Limpiar cache en caso de error
        user_id = session.get('user_id')
        if user_id:
            invalidar_cache_carrito(user_id)
        return jsonify({'status': 'error', 'message': 'Error al obtener el carrito'}), 500

@carrito_bp.route('/Carrito/pagar', methods=['POST'])
@login_required
def pagar():
    user_id = session.get('user_id')
    
    # Verificar autenticación
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Usuario no autenticado'}), 401
    
    data = request.get_json()
    
    # Invalidar cache antes de hacer cambios
    invalidate_user_cart_cache(user_id)
    
    conexion = get_db_connection()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            SELECT facturacion.id_factura
            FROM usuario
            INNER JOIN facturacion ON usuario.id_usuario = facturacion.id_usuario
            INNER JOIN metodo_pago ON facturacion.id_pago = metodo_pago.id_pago
            WHERE usuario.id_usuario = %s AND metodo_pago.nombre_pago = %s
        """, (user_id, 'no_pago'))
        row = cursor.fetchone()
        id_factura = row[0] if row else None

        if id_factura:
            cursor.execute("SELECT id_producto, cantidad_producto, id_detalle FROM detalle_facturacion WHERE id_factura = %s", (id_factura,))
            productos_en_bd = cursor.fetchall()

            productos_bd_dict = {
                str(p[0]): {'cantidad': p[1], 'id_detalle': p[2]}
                for p in productos_en_bd
            }

            productos_frontend = set(data.keys()) if data else set()
            productos_bd_ids = set(productos_bd_dict.keys())

            # Eliminar productos que ya no están en el carrito
            for producto_id in productos_bd_ids - productos_frontend:
                cursor.execute("DELETE FROM detalle_facturacion WHERE id_detalle = %s", (productos_bd_dict[producto_id]['id_detalle'],))

            # Actualizar productos existentes
            for producto_id in productos_bd_ids & productos_frontend:
                item = data[producto_id]
                cursor.execute("""
                    UPDATE detalle_facturacion
                    SET cantidad_producto = %s
                    WHERE id_detalle = %s
                """, (item['quantity'], productos_bd_dict[producto_id]['id_detalle']))

            # Insertar nuevos productos
            for producto_id in productos_frontend - productos_bd_ids:
                item = data[producto_id]
                cursor.execute("""
                    INSERT INTO detalle_facturacion (id_factura, id_producto, cantidad_producto)
                    VALUES (%s, %s, %s)
                """, (id_factura, int(producto_id), item['quantity']))

            # Si el carrito está vacío, eliminar la factura
            if not data:
                cursor.execute("DELETE FROM detalle_facturacion WHERE id_factura = %s", (id_factura,))
                cursor.execute("DELETE FROM facturacion WHERE id_factura = %s", (id_factura,))
                id_factura = None

        else:
            # Crear nueva factura si hay productos
            if data:
                cursor.execute("SELECT id_pago FROM metodo_pago WHERE nombre_pago = %s", ('no_pago',))
                id_pago_result = cursor.fetchone()
                if not id_pago_result:
                    raise Exception("No se encontró el método de pago 'no_pago'")
                    
                id_pago = id_pago_result[0]

                hora_actual = datetime.now().strftime('%H:%M:%S')

                cursor.execute("SELECT id_domiciliario FROM domiciliario ORDER BY RAND() LIMIT 1")
                id_domiciliario = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO tipo_entrega (id_domiciliario, estado_entrega)
                    VALUES (%s, %s)
                """, (id_domiciliario, 'no entregado'))

                id_tipo_entrega = cursor.lastrowid
                
                cursor.execute("""
                    INSERT INTO facturacion (id_usuario, fecha_compra, hora, id_pago, id_tipo_entrega) 
                    VALUES (%s, NOW(), %s, %s, %s)
                """, (user_id, hora_actual, id_pago, id_tipo_entrega))
                id_factura = cursor.lastrowid

                for producto_id, item in data.items():
                    cursor.execute("""
                        INSERT INTO detalle_facturacion (id_factura, id_producto, cantidad_producto)
                        VALUES (%s, %s, %s)
                    """, (id_factura, int(producto_id), item['quantity']))

        conexion.commit()
        session['current_factura_id'] = id_factura
        
        print(f"Factura procesada correctamente. ID: {id_factura}, Usuario: {user_id}")
        
        return jsonify({
            "status": "success", 
            "id_factura": id_factura, 
            "empty": not bool(data),
            "user_id": user_id
        })

    except Exception as e:
        conexion.rollback()
        print(f"Error en pagar(): {e}")
        return jsonify({"status": "error", "message": f"Error al procesar el carrito: {str(e)}"}), 500
    finally:
        cursor.close()
        conexion.close()

@carrito_bp.route('/Carrito/limpiar-cache', methods=['POST'])
def limpiar_cache():
    """Ruta para limpiar el cache del carrito del usuario actual"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Usuario no autenticado'}), 401
        
        limpiar_cache_usuario(user_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Cache limpiado correctamente'
        })
    except Exception as e:
        print(f"Error al limpiar cache: {e}")
        return jsonify({'status': 'error', 'message': 'Error al limpiar cache'}), 500

# Función auxiliar para llamar desde otras partes de la aplicación
def invalidar_carrito_usuario(user_id):
    """Función pública para invalidar el carrito desde otros módulos"""
    invalidate_user_cart_cache(user_id)