# blueprints/domiciliarios.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import string
import re
import logging
from datetime import datetime
from functools import wraps
from db.conexion import get_db_connection

# Crear blueprint para domiciliarios
domiciliarios_bp = Blueprint('domiciliarios', __name__, url_prefix='/domiciliarios')
VERIFICAR_PASSWORD = True

# ==================== FUNCIONES AUXILIARES ====================

def hash_password(password):
    """Hashear contraseña usando werkzeug"""
    return generate_password_hash(password)

def es_contraseña_haseada(contraseña):
    """
    Verifica si una contraseña parece estar hasheada
    (basado en prefijos comunes usados por werkzeug.security)
    """
    return any(
        contraseña.startswith(prefijo)
        for prefijo in ('pbkdf2:', 'scrypt:', 'argon2:')
    )

def validar_datos_domiciliario(cedula, nombre, telefono, email, password):
    """Validar datos específicos para registro de domiciliario"""
    errores = {}
    
    # Validación de cédula
    if not cedula or not cedula.strip():
        errores['cedula'] = 'La cédula es obligatoria'
    elif not re.match(r'^\d{7,10}$', cedula):
        errores['cedula'] = 'La cédula debe tener entre 7 y 10 dígitos'
    
    # Validación de nombre
    if not nombre or len(nombre.strip()) < 3:
        errores['nombre'] = 'El nombre debe tener al menos 3 caracteres'
    elif len(nombre) > 100:
        errores['nombre'] = 'El nombre no puede exceder 100 caracteres'
    elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
        errores['nombre'] = 'El nombre solo puede contener letras y espacios'
    
    # Validación de teléfono
    if not re.match(r'^[0-9]{10}$', telefono):
        errores['telefono'] = 'El teléfono debe tener exactamente 10 dígitos'
    
    # Validación de email
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        errores['email'] = 'Formato de email inválido'
    
    # Validación de password
    if len(password) < 6:
        errores['password'] = 'La contraseña debe tener al menos 6 caracteres'
    elif len(password) > 50:
        errores['password'] = 'La contraseña no puede exceder 50 caracteres'
    elif not re.search(r'(?=.*[a-zA-Z])(?=.*\d)', password):
        errores['password'] = 'La contraseña debe contener al menos una letra y un número'
    
    return errores

# ==================== DECORADORES ====================
def is_domiciliario():
    """Verificar si el usuario logueado es domiciliario"""
    try:
        return (session.get('logged_in', False) and 
                session.get('user_id') is not None)
    except Exception as e:
        logging.error(f"Error verificando sesión de domiciliario: {e}")
        return False
    
def domiciliario_required(f):
    """Decorador para requerir autenticación de domiciliario en rutas protegidas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_domiciliario():
            flash('Debes iniciar sesión como domiciliario', 'error')
            return redirect(url_for('domiciliarios.login'))
        return f(*args, **kwargs)
    return decorated_function

def domiciliario_required(f):
    """Decorador para requerir autenticación de domiciliario en rutas protegidas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_domiciliario():
            flash('Debes iniciar sesión como domiciliario', 'error')
            return redirect(url_for('domiciliarios.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_domiciliario():
    """Obtener datos del domiciliario actual de la sesión"""
    try:
        if is_domiciliario():
            return {
                'id': session.get('user_id'),
                'name': session.get('user_name'),
                'email': session.get('user_email')
            }
        return None
    except Exception as e:
        logging.error(f"Error obteniendo datos del domiciliario actual: {e}")
        return None

def login_domiciliario(user_data):
    """Crear sesión de domiciliario después de validar credenciales"""
    try:
        # Validar que user_data tenga los campos necesarios
        required_fields = ['id_domiciliario', 'nombres_domiciliario', 'email_domiciliario']
        
        for field in required_fields:
            if field not in user_data or user_data[field] is None:
                raise ValueError(f"Campo requerido '{field}' no encontrado en user_data")
        
        # Limpiar sesión anterior
        session.clear()
        
        # Establecer nuevos valores de sesión
        session['user_id'] = str(user_data['id_domiciliario'])
        session['user_name'] = str(user_data['nombres_domiciliario'])
        session['user_email'] = str(user_data['email_domiciliario'])
        session['logged_in'] = True
        
        # Hacer la sesión permanente para que persista
        session.permanent = True
        
        logging.info(f"Sesión creada exitosamente para domiciliario: {user_data['id_domiciliario']}")
        
    except Exception as e:
        logging.error(f"Error creando sesión de domiciliario: {str(e)}")
        raise Exception(f"Error al crear sesión: {str(e)}")

# ==================== RUTAS ====================

@domiciliarios_bp.route('/login')
def login():
    """Página de login de domiciliarios"""
    return render_template('Login_Domiciliario/Login_dom.html')

@domiciliarios_bp.route('/authenticate', methods=['POST'])
def authenticate():
    """Autenticar domiciliario usando SOLO LA TABLA DOMICILIARIO"""
    conn = None
    cursor = None
    
    try:
        # Obtener datos del formulario
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validar campos requeridos
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email, teléfono o cédula es requerido'
            }), 400
        
        if not password:
            return jsonify({
                'success': False,
                'message': 'Contraseña es requerida'
            }), 400
        
        # Establecer conexión a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar domiciliario por email, teléfono o cédula EN LA TABLA DOMICILIARIO
        query = '''
            SELECT * FROM domiciliario 
            WHERE (email_domiciliario = %s OR telefono = %s OR id_domiciliario = %s)
        '''
        cursor.execute(query, (email, email, email))
        
        domiciliario = cursor.fetchone()
        
        print(f"Domiciliario encontrado: {domiciliario is not None}")
        
        if not domiciliario:
            return jsonify({
                'success': False,
                'message': 'Domiciliario no encontrado. Verifica email, teléfono o cédula.',
                'error_field': 'email'
            }), 401

        # Verificar contraseña si está habilitada la verificación
        if VERIFICAR_PASSWORD:
            stored_password = domiciliario.get('contraseña_domiciliario')

            if not stored_password:
                print("Error: Contraseña no configurada")
                return jsonify({
                    'success': False,
                    'message': 'Contraseña no configurada para este domiciliario'
                }), 401

            if es_contraseña_haseada(stored_password):
                # Comparar usando werkzeug si está hasheada
                password_match = check_password_hash(stored_password, password)
                print(f"Verificación con hash: {password_match}")
                if not password_match:
                    return jsonify({
                        'success': False,
                        'message': 'Contraseña incorrecta'
                    }), 401
            else:
                # Comparar directamente si no está hasheada (temporal durante migración)
                password_match = stored_password == password
                print(f"Verificación directa: {password_match}")
                if not password_match:
                    return jsonify({
                        'success': False,
                        'message': 'Contraseña incorrecta (sin hashear)'
                    }), 401
        
        # Crear sesión de domiciliario
        login_domiciliario(domiciliario)
        
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'redirect': '/domiciliarios/dashboard'
        }), 200
        
    except Exception as e:
        logging.error(f"Error en autenticación de domiciliario: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error del servidor. Intenta nuevamente.'
        }), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@domiciliarios_bp.route('/perfil')
@domiciliario_required
def perfil():
    """Perfil del domiciliario"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT * FROM domiciliario WHERE id_domiciliario = %s
        ''', (session['user_id'],))
        
        domiciliario = cursor.fetchone()
        
        if not domiciliario:
            return redirect(url_for('domiciliarios.login'))
        
        return render_template('perfil_domiciliario/perfil_dom.html', 
                             domiciliario=domiciliario)
        
    finally:
        cursor.close()
        conn.close()

@domiciliarios_bp.route('/logout', methods=['POST'])
def logout():
    """Cerrar sesión de domiciliario"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Sesión cerrada exitosamente',
        'redirect': '/Home'
    }), 200

def get_domiciliarios_activos():
    """Obtener lista de domiciliarios activos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT id_domiciliario, nombres_domiciliario, email_domiciliario, telefono
            FROM domiciliario 
            ORDER BY nombres_domiciliario
        ''')
        
        domiciliarios = cursor.fetchall()
        return domiciliarios
        
    except Exception as e:
        logging.error(f"Error obteniendo domiciliarios activos: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

class PedidosService:
    """Servicio para gestionar pedidos usando la tabla domiciliario"""
    
    def obtener_pedidos_asignados_domiciliario(self, id_domiciliario):
        """Obtiene pedidos asignados a un domiciliario específico - Excluye pedidos con estado no_pago"""
        conn = get_db_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor(dictionary=True)

            # Obtener los pedidos asignados - EXCLUYENDO los de estado no_pago
            cursor.execute("""
                SELECT 
                    u.id_usuario,
                    u.nombres_usuario,
                    u.apellidos_usuario,
                    u.email_usuario,
                    u.telefono,
                    ub.direccion_usuario,
                    f.id_factura,
                    f.fecha_compra,
                    f.hora,
                    mp.nombre_pago,
                    df.id_detalle,
                    df.cantidad_producto,
                    p.nombre_producto,
                    p.precio_producto,
                    d.id_domiciliario,
                    d.nombres_domiciliario,
                    te.id_tipo_entrega,
                    te.estado_entrega
                FROM usuario u
                INNER JOIN ubicacion ub ON u.id_usuario = ub.id_usuario
                INNER JOIN facturacion f ON u.id_usuario = f.id_usuario
                INNER JOIN metodo_pago mp ON f.id_pago = mp.id_pago
                INNER JOIN detalle_facturacion df ON df.id_factura = f.id_factura
                INNER JOIN producto p ON p.id_producto = df.id_producto
                INNER JOIN domiciliario d ON d.id_domiciliario = %s
                INNER JOIN tipo_entrega te ON f.id_tipo_entrega = te.id_tipo_entrega
                WHERE mp.nombre_pago != 'no_pago'
                    AND mp.nombre_pago IS NOT NULL
                    AND te.estado_entrega = 'no entregado'
                    AND te.id_domiciliario = %s
                ORDER BY f.fecha_compra DESC, f.hora DESC
            """, (id_domiciliario, id_domiciliario,))

            productos = cursor.fetchall()
            return self.procesar_pedidos_con_domiciliario(productos)

        except Exception as e:
            logging.error(f"Error obteniendo pedidos asignados: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def procesar_pedidos_con_domiciliario(self, productos):
        pedidos = {}

        for row in productos:
            id_factura = row['id_factura']
            id_detalle = row.get('id_detalle')

            if id_factura not in pedidos:
                pedidos[id_factura] = {
                    'id_factura': id_factura,
                    'fecha_compra': row.get('fecha_compra'),
                    'hora': row.get('hora'),
                    'metodo_pago': row.get('nombre_pago'),
                    'total': 0,
                    'cliente': {
                        'id_usuario': row.get('id_usuario'),
                        'nombres': row.get('nombres_usuario'),
                        'apellidos': row.get('apellidos_usuario'),
                        'email': row.get('email_usuario'),
                        'telefono': row.get('telefono'),
                        'direccion': row.get('direccion_usuario')
                    },
                    'productos': [],
                    'productos_agregados': set(),
                    'domiciliario': {
                        'id_domiciliario': row.get('id_domiciliario'),
                        'nombres_domiciliario': row.get('nombres_domiciliario')
                    },
                    'estado_entrega': row.get('estado_entrega'),
                    'id_tipo_entrega': row.get('id_tipo_entrega')
                }

            # Agregar producto solo si no se ha agregado ya
            if id_detalle not in pedidos[id_factura]['productos_agregados']:
                pedidos[id_factura]['productos'].append({
                    'id_detalle': id_detalle,
                    'nombre_producto': row.get('nombre_producto'),
                    'cantidad': row.get('cantidad_producto'),
                    'precio_unitario': row.get('precio_producto'),
                    'subtotal': row.get('cantidad_producto') * row.get('precio_producto')
                })

                pedidos[id_factura]['productos_agregados'].add(id_detalle)

                # Sumar al total solo si no estaba duplicado
                pedidos[id_factura]['total'] += row.get('cantidad_producto') * row.get('precio_producto')

        # Eliminar 'productos_agregados' para no enviarlo al frontend
        for pedido in pedidos.values():
            pedido.pop('productos_agregados', None)

        return list(pedidos.values())
    
    def obtener_pedidos_entregados_domiciliario(self, id_domiciliario):
        """Obtiene pedidos entregados por un domiciliario específico"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Obtener los pedidos entregados - solo los que tienen estado 'entregado'
            cursor.execute("""
                SELECT 
                    u.id_usuario,
                    u.nombres_usuario,
                    u.apellidos_usuario,
                    u.email_usuario,
                    u.telefono,
                    ub.direccion_usuario,
                    f.id_factura,
                    f.fecha_compra,
                    f.hora,
                    mp.nombre_pago,
                    df.id_detalle,
                    df.cantidad_producto,
                    p.nombre_producto,
                    p.precio_producto,
                    d.id_domiciliario,
                    d.nombres_domiciliario,
                    te.estado_entrega
                FROM usuario u
                INNER JOIN ubicacion ub ON u.id_usuario = ub.id_usuario
                INNER JOIN facturacion f ON u.id_usuario = f.id_usuario
                INNER JOIN metodo_pago mp ON f.id_pago = mp.id_pago
                INNER JOIN detalle_facturacion df ON df.id_factura = f.id_factura
                INNER JOIN producto p ON p.id_producto = df.id_producto
                INNER JOIN domiciliario d ON d.id_domiciliario = %s
                INNER JOIN tipo_entrega te ON f.id_tipo_entrega = te.id_tipo_entrega
                WHERE mp.nombre_pago != 'no_pago'
                    AND mp.nombre_pago IS NOT NULL
                    AND te.estado_entrega = 'entregado'
                    AND te.id_domiciliario = %s
            """, (id_domiciliario, id_domiciliario))
            
            productos = cursor.fetchall()
            return self.procesar_pedidos_entregados(productos)
            
        except Exception as e:
            logging.error(f"Error obteniendo pedidos entregados: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()

    def procesar_pedidos_entregados(self, productos):
        """Procesa los productos entregados y los agrupa por factura"""
        pedidos = {}
        
        for producto in productos:
            id_factura = producto['id_factura']
            
            if id_factura not in pedidos:
                pedidos[id_factura] = {
                    'id_factura': id_factura,
                    'cliente': {
                        'id_usuario': producto['id_usuario'],
                        'nombres': producto['nombres_usuario'],
                        'apellidos': producto['apellidos_usuario'],
                        'email': producto['email_usuario'],
                        'telefono': producto['telefono'],
                        'direccion': producto['direccion_usuario']
                    },
                    'fecha_compra': producto['fecha_compra'],
                    'metodo_pago': producto['nombre_pago'],
                    'domiciliario': {
                        'id_domiciliario': producto['id_domiciliario'],
                        'nombres_domiciliario': producto['nombres_domiciliario']
                    },
                    'estado_entrega': producto['estado_entrega'],
                    'productos': [],
                    'total': 0
                }
            
            pedidos[id_factura]['productos'].append({
                'id_detalle': producto['id_detalle'],
                'nombre_producto': producto['nombre_producto'],
                'cantidad': producto['cantidad_producto'],
                'precio_unitario': producto['precio_producto'],
                'subtotal': producto['cantidad_producto'] * producto['precio_producto']
            })
            
            pedidos[id_factura]['total'] += producto['cantidad_producto'] * producto['precio_producto']

        return list(pedidos.values())

    
    def obtener_pedido_por_id(self, id_factura):
        """Obtiene un pedido específico por su ID - Excluye pedidos con estado no_pago"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    u.id_usuario,
                    u.nombres_usuario,
                    u.apellidos_usuario,
                    u.email_usuario,
                    u.telefono,
                    ub.direccion_usuario,
                    f.id_factura,
                    f.fecha_compra,
                    f.hora,
                    mp.nombre_pago,
                    df.id_detalle,
                    df.cantidad_producto,
                    p.nombre_producto,
                    p.precio_producto,
                    d.id_domiciliario,
                    d.nombres_domiciliario,
                    te.estado_entrega
                FROM usuario u
                INNER JOIN ubicacion ub ON u.id_usuario = ub.id_usuario
                INNER JOIN facturacion f ON u.id_usuario = f.id_usuario
                INNER JOIN metodo_pago mp ON f.id_pago = mp.id_pago
                INNER JOIN detalle_facturacion df ON df.id_factura = f.id_factura
                INNER JOIN producto p ON p.id_producto = df.id_producto
                INNER JOIN domiciliario d ON d.id_factura = f.id_factura
                LEFT JOIN tipo_entrega te ON te.id_domiciliario = d.id_domiciliario
                WHERE f.id_factura = %s 
                    AND mp.nombre_pago != 'no_pago'
                    AND mp.nombre_pago IS NOT NULL
                    AND te.estado_entrega = 'no entregado'
            """, (id_factura,))
            
            productos = cursor.fetchall()
            if productos:
                pedidos = self.procesar_pedidos_con_domiciliario(productos)
                return pedidos[0] if pedidos else None
            return None
            
        except Exception as e:
            print(f"Error obteniendo pedido: {e}")
            logging.error(f"Error obteniendo pedido por ID: {e}")
            return None
        finally:
            if conn:
                cursor.close()
                conn.close()

# Rutas del blueprint
@domiciliarios_bp.route("/")
def index():
    """Página principal del domiciliario"""
    return render_template('domiciliario/index.html')

@domiciliarios_bp.route('/dashboard')
@domiciliario_required
def dashboard():
    """Dashboard de domiciliarios con pedidos asignados"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            flash('Error: No se pudo obtener el ID del domiciliario', 'error')
            return redirect(url_for('domiciliarios.login'))
        
        pedidos_service = PedidosService()
        pedidos = pedidos_service.obtener_pedidos_asignados_domiciliario(user_id)
        
        return render_template('pedidos asignados domi/Pedidos ASIGNADOS.html', 
                             nombre=session.get('user_name'),
                             pedidos=pedidos)
    except Exception as e:
        logging.error(f"Error en dashboard: {e}")
        flash('Error al cargar el dashboard', 'error')
        return render_template('pedidos asignados domi/Pedidos ASIGNADOS.html', 
                             nombre=session.get('user_name'),
                             pedidos=[])

@domiciliarios_bp.route("/pedidos-asignados")
@domiciliario_required
def pedidos_asignados():
    """Ruta para mostrar pedidos asignados"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            flash('Error: No se pudo obtener el ID del domiciliario', 'error')
            return redirect(url_for('domiciliarios.login'))
        
        pedidos_service = PedidosService()
        pedidos = pedidos_service.obtener_pedidos_entregados_domiciliario(user_id)
        
        return render_template('pedidos asignados domi/Pedidos ASIGNADOS.html', pedidos=pedidos)
    except Exception as e:
        logging.error(f"Error en ruta pedidos asignados: {e}")
        return render_template('pedidos asignados domi/Pedidos ASIGNADOS.html', pedidos=[])

def register_domiciliario_blueprint(app):
    """Función helper para registrar el blueprint en la app"""
    app.register_blueprint(domiciliarios_bp)

@domiciliarios_bp.route("/detalle-pedido/<int:id_factura>")
@domiciliario_required
def detalle_pedido(id_factura):
    """Ruta para mostrar el detalle de un pedido específico"""
    try:
        pedidos_service = PedidosService()
        pedido = pedidos_service.obtener_pedido_por_id(id_factura)
        
        if not pedido:
            flash('Pedido no encontrado', 'error')
            return redirect(url_for('domiciliarios.pedidos_asignados'))
        
        return render_template('domiciliario/detalle_pedido.html', pedido=pedido)
    except Exception as e:
        print(f"Error obteniendo detalle del pedido: {e}")
        logging.error(f"Error en detalle pedido: {e}")
        flash('Error al obtener el detalle del pedido', 'error')
        return redirect(url_for('domiciliarios.pedidos_asignados'))

@domiciliarios_bp.route("/api/pedidos-asignados")
@domiciliario_required
def api_pedidos_asignados():
    """API para obtener pedidos asignados en formato JSON"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'ID de domiciliario no encontrado en sesión'
            }), 400
        
        pedidos_service = PedidosService()
        pedidos = pedidos_service.obtener_pedidos_entregados_domiciliario(user_id)
        
        # Convertir fechas y horas a string para JSON
        for pedido in pedidos:
            if pedido['fecha_compra']:
                pedido['fecha_compra'] = pedido['fecha_compra'].isoformat()
            if pedido['hora']:
                pedido['hora'] = str(pedido['hora'])
        
        return jsonify({
            'success': True,
            'pedidos': pedidos,
            'total': len(pedidos)
        })
    except Exception as e:
        print(f"Error en API pedidos asignados: {e}")
        logging.error(f"Error en API pedidos asignados: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al obtener los pedidos'
        }), 500
    
@domiciliarios_bp.route("/actualizar-estado-entrega", methods=['POST'])
@domiciliario_required
def actualizar_estado_entrega():
    """Actualizar el estado de entrega de un pedido"""
    try:
        id_tipo_entrega = request.form.get('id_tipo_entrega')
        nuevo_estado = request.form.get('estado')
        
        if not id_tipo_entrega or not nuevo_estado:
            return jsonify({
                'success': False,
                'message': 'Datos incompletos'
            }), 400
        
        # Validar estados permitidos
        estados_permitidos = ['asignado', 'entregado']
        if nuevo_estado not in estados_permitidos:
            return jsonify({
                'success': False,
                'message': 'Estado no válido'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar que el pedido pertenece al domiciliario actual
            user_id = session.get('user_id')

            cursor.execute("""
                SELECT te.id_tipo_entrega 
                FROM tipo_entrega te
                WHERE te.id_tipo_entrega = %s AND te.id_domiciliario = %s
            """, (id_tipo_entrega, user_id))
            
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'message': 'No tienes permisos para actualizar este pedido'
                }), 403
            
            # Actualizar el estado
            cursor.execute("""
                UPDATE tipo_entrega 
                SET estado_entrega = %s 
                WHERE id_tipo_entrega = %s
            """, (nuevo_estado, id_tipo_entrega))
            
            conn.commit()
            
            return redirect(url_for('domiciliarios.pedidos_entregados'))
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error actualizando estado: {e}")
            return jsonify({
                'success': False,
                'message': 'Error al actualizar el estado'
            }), 500
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logging.error(f"Error en actualizar estado entrega: {e}")
        return jsonify({
            'success': False,
            'message': 'Error del servidor'
        }), 500

# Agregar estas rutas al blueprint domiciliarios_bp

@domiciliarios_bp.route("/pedidos-entregados")
@domiciliario_required
def pedidos_entregados():
    """Ruta para mostrar pedidos entregados"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            flash('Error: No se pudo obtener el ID del domiciliario', 'error')
            return redirect(url_for('domiciliarios.login'))
        
        pedidos_service = PedidosService()
        pedidos = pedidos_service.obtener_pedidos_entregados_domiciliario(user_id)
        
        return render_template('pedidos asignados domi/Pedidos Entregados.html', 
                             pedidos=pedidos,
                             nombre=session.get('user_name'))
    except Exception as e:
        logging.error(f"Error en ruta pedidos entregados: {e}")
        return render_template('pedidos asignados domi/Pedidos Entregados.html', 
                             pedidos=[],
                             nombre=session.get('user_name'))

@domiciliarios_bp.route("/api/pedidos-entregados")
@domiciliario_required
def api_pedidos_entregados():
    """API para obtener pedidos entregados en formato JSON"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'ID de domiciliario no encontrado en sesión'
            }), 400
        
        pedidos_service = PedidosService()
        pedidos = pedidos_service.obtener_pedidos_entregados_domiciliario(user_id)
        
        # Convertir fechas y horas a string para JSON
        for pedido in pedidos:
            if pedido['fecha_compra']:
                pedido['fecha_compra'] = pedido['fecha_compra'].isoformat()
            if pedido['hora_compra']:
                pedido['hora_compra'] = str(pedido['hora_compra'])
        
        return jsonify({
            'success': True,
            'pedidos': pedidos,
            'total': len(pedidos)
        })
    except Exception as e:
        logging.error(f"Error en API pedidos entregados: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al obtener los pedidos entregados'
        }), 500
    
def migrar_contraseñas_existentes():
    """
    Script para hashear las contraseñas existentes en la base de datos
    EJECUTAR SOLO UNA VEZ para migrar contraseñas en texto plano
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener todos los domiciliarios con contraseñas en texto plano
        cursor.execute('''
            SELECT id_domiciliario, contraseña_domiciliario 
            FROM domiciliario 
            WHERE contraseña_domiciliario IS NOT NULL 
            AND contraseña_domiciliario != ''
        ''')
        
        domiciliarios = cursor.fetchall()
        
        print(f"Migrando {len(domiciliarios)} contraseñas...")
        
        for domiciliario in domiciliarios:
            # Verificar si ya está hasheada (las contraseñas hasheadas empiezan con prefijos específicos)
            if domiciliario['contraseña_domiciliario'].startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
                print(f"Contraseña de {domiciliario['id_domiciliario']} ya está hasheada")
                continue
            
            # Hashear contraseña
            password_hash = hash_password(domiciliario['contraseña_domiciliario'])
            
            # Actualizar en la base de datos
            cursor.execute('''
                UPDATE domiciliario 
                SET contraseña_domiciliario = %s 
                WHERE id_domiciliario = %s
            ''', (password_hash, domiciliario['id_domiciliario']))
            
            print(f"Contraseña migrada para domiciliario: {domiciliario['id_domiciliario']}")
        
        conn.commit()
        print("Migración completada exitosamente")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error en migración: {e}")
        logging.error(f"Error en migración de contraseñas: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()