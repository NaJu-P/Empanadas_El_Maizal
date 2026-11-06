from flask import Blueprint, render_template, session, request, jsonify
from db.conexion import get_db_connection
from routes.auth import login_required

from routes.carrito_de_compras import invalidar_cache_despues_pago
from routes.auth import login_required

metodo_pago_bp = Blueprint('metodo-pago', __name__)

@metodo_pago_bp.route("/Metodo-pago")
@login_required
def metodo_pago():
    
    id_factura = session.get('current_factura_id')
    user_id = session.get('user_id')
    
    if not id_factura:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT facturacion.id_factura
            FROM facturacion
            INNER JOIN metodo_pago ON facturacion.id_pago = metodo_pago.id_pago
            WHERE facturacion.id_usuario = %s
            AND metodo_pago.nombre_pago = %s
            ORDER BY facturacion.fecha_compra DESC, facturacion.id_factura DESC
            LIMIT 1
            """,
            (user_id, 'no_pago')
        )
        
        result = cursor.fetchone()
        if result:
            id_factura = result['id_factura']
        else:
            cursor.close()
            conexion.close()
            return render_template('tus_facturas/metodo_pago.html', productos=[], mensaje="No hay productos en el carrito")
    
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            usuario.id_usuario,
            usuario.nombres_usuario,
            usuario.apellidos_usuario,
            facturacion.id_factura,
            facturacion.fecha_compra,
            detalle_facturacion.id_detalle,
            detalle_facturacion.cantidad_producto,
            producto.nombre_producto,
            producto.precio_producto,
            producto.img_producto,
            tipo_producto.descripcion_producto,
            tipo_producto.id_tipo_producto,
            metodo_pago.nombre_pago
        FROM usuario
        INNER JOIN facturacion ON facturacion.id_usuario = usuario.id_usuario
        INNER JOIN metodo_pago ON facturacion.id_pago = metodo_pago.id_pago
        INNER JOIN detalle_facturacion ON detalle_facturacion.id_factura = facturacion.id_factura
        INNER JOIN producto ON producto.id_producto = detalle_facturacion.id_producto
        INNER JOIN tipo_producto ON tipo_producto.id_tipo_producto = producto.id_tipo_producto
        WHERE facturacion.id_factura = %s
        AND usuario.id_usuario = %s
        AND metodo_pago.nombre_pago = %s
        """,
        (id_factura, user_id, 'no_pago')
    )

    productos = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template('tus_facturas/metodo_pago.html', productos=productos)


@metodo_pago_bp.route("/Metodo-pago/procesar-pago", methods=['POST'])
def procesar_pago():
    try:
        # Obtener datos de la sesión
        id_factura = session.get('current_factura_id')
        user_id = session.get('user_id')
        
        # Obtener el método de pago seleccionado del request
        data = request.get_json()
        print(f"Datos recibidos: {data}")

        metodo_pago_seleccionado = data.get('metodo_pago') if data else None
        print(f"Método de pago seleccionado: '{metodo_pago_seleccionado}'")

        if metodo_pago_seleccionado:
            metodo_pago_seleccionado = metodo_pago_seleccionado.lower().strip()
            print(f"Método de pago normalizado: '{metodo_pago_seleccionado}'")

        # Validar que se haya seleccionado un método de pago válido
        if not metodo_pago_seleccionado or metodo_pago_seleccionado not in ['nequi', 'daviplata']:
            return jsonify({
                'success': False, 
                'message': f'Método de pago no válido: {metodo_pago_seleccionado}'
            }), 400
        
        # Validar que existan los datos necesarios
        if not id_factura or not user_id:
            return jsonify({
                'success': False, 
                'message': 'Datos de sesión incompletos'
            }), 400
        
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        
        # Primero verificar que la factura existe y pertenece al usuario
        cursor.execute(
            """
            SELECT f.id_factura, f.id_pago
            FROM facturacion f
            INNER JOIN metodo_pago mp ON f.id_pago = mp.id_pago
            WHERE f.id_factura = %s 
            AND f.id_usuario = %s 
            AND mp.nombre_pago = 'no_pago'
            """,
            (id_factura, user_id)
        )
        
        factura = cursor.fetchone()
        if not factura:
            cursor.close()
            conexion.close()
            return jsonify({
                'success': False, 
                'message': 'Factura no encontrada o ya procesada'
            }), 404
        
        # Obtener el ID del método de pago seleccionado
        cursor.execute(
            "SELECT id_pago FROM metodo_pago WHERE nombre_pago = %s",
            (metodo_pago_seleccionado,)
        )
        
        metodo_pago_result = cursor.fetchone()
        if not metodo_pago_result:
            cursor.close()
            conexion.close()
            return jsonify({
                'success': False, 
                'message': 'Método de pago no encontrado en la base de datos'
            }), 404
        
        nuevo_id_pago = metodo_pago_result['id_pago']

        # Descontar stock directamente con JOIN
        cursor.execute("""
            UPDATE producto p
            JOIN detalle_facturacion df ON p.id_producto = df.id_producto
            SET p.cantidad_disponible = p.cantidad_disponible - df.cantidad_producto
            WHERE df.id_factura = %s
        """, (id_factura,))
        
        # Actualizar el método de pago en la factura
        cursor.execute(
            """
            UPDATE facturacion 
            SET id_pago = %s 
            WHERE id_factura = %s AND id_usuario = %s
            """,
            (nuevo_id_pago, id_factura, user_id)
        )
        
        # Confirmar los cambios
        conexion.commit()
        cursor.close()
        conexion.close()
        
        # AGREGAR ESTAS LÍNEAS CRÍTICAS:
        # Invalidar el cache del carrito después del pago exitoso
        try:
            invalidar_cache_despues_pago(user_id)
            print(f"Cache del carrito invalidado para usuario {user_id} después del pago")
        except Exception as cache_error:
            print(f"Error al invalidar cache: {cache_error}")
        
        # Limpiar la sesión después del pago exitoso
        session.pop('current_factura_id', None)
        
        return jsonify({
            'success': True, 
            'message': f'Procesado exitosamente con {metodo_pago_seleccionado.capitalize()}',
            'metodo_pago': metodo_pago_seleccionado
        })
        
    except Exception as e:
        # En caso de error, hacer rollback si la conexión existe
        if 'conexion' in locals():
            conexion.rollback()
            cursor.close()
            conexion.close()
        
        return jsonify({
            'success': False, 
            'message': f'Error interno del servidor: {str(e)}'
        }), 500