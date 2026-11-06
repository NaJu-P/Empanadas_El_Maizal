from flask import Blueprint, render_template, request, redirect, jsonify, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime
from db.conexion import get_db_connection  # Ajusta si la ruta es distinta

admin_bp = Blueprint("admin", __name__)

# ---------------------------------------
# Decorador para proteger rutas de admin
# ---------------------------------------
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Debes iniciar sesión como administrador", "danger")
            return redirect(url_for('admin.login_admin'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------
# Función para verificar si una contraseña está hasheada
# ---------------------------------------
def is_password_hashed(password):
    """
    Verifica si una contraseña está hasheada.
    Las contraseñas hasheadas con Werkzeug empiezan con un identificador específico.
    """
    return password and (password.startswith('pbkdf2:') or password.startswith('scrypt:') or password.startswith('bcrypt:'))

# ---------------------------------------
# Función para migrar contraseñas a formato hasheado
# ---------------------------------------
def migrate_password_to_hash(admin_id, plain_password):
    """
    Migra una contraseña en texto plano a formato hasheado.
    
    Args:
        admin_id: ID del administrador
        plain_password: Contraseña en texto plano
    
    Returns:
        bool: True si la migración fue exitosa, False en caso contrario
    """
    try:
        hashed_password = generate_password_hash(plain_password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE administrador SET contrasena_admin = %s WHERE id_administrador = %s",
            (hashed_password, admin_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error al migrar contraseña: {e}")
        return False

# ---------------------------------------
# Función para migrar TODAS las contraseñas de la base de datos
# ---------------------------------------
def migrate_all_passwords():
    """
    Migra todas las contraseñas en texto plano a formato hasheado.
    USAR CON PRECAUCIÓN - Esta función modificará todas las contraseñas no hasheadas.
    
    Returns:
        dict: Resultado de la migración con contadores
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener todos los administradores
        cursor.execute("SELECT id_administrador, email_admin, contrasena_admin FROM administrador")
        admins = cursor.fetchall()
        
        migrated_count = 0
        already_hashed_count = 0
        error_count = 0
        
        for admin in admins:
            if not is_password_hashed(admin['contrasena_admin']):
                # Migrar contraseña en texto plano
                hashed_password = generate_password_hash(admin['contrasena_admin'])
                
                update_cursor = conn.cursor()
                update_cursor.execute(
                    "UPDATE administrador SET contrasena_admin = %s WHERE id_administrador = %s",
                    (hashed_password, admin['id_administrador'])
                )
                update_cursor.close()
                
                migrated_count += 1
                print(f"Migrada contraseña para admin: {admin['email_admin']}")
            else:
                already_hashed_count += 1
                print(f"Contraseña ya hasheada para admin: {admin['email_admin']}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'migrated': migrated_count,
            'already_hashed': already_hashed_count,
            'errors': error_count,
            'total': len(admins)
        }
        
    except Exception as e:
        print(f"Error durante la migración masiva: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# ---------------------------------------
# Ruta para el login del administrador
# ---------------------------------------
@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']  # Email del admin
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM administrador WHERE email_admin = %s", (username,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin:
            stored_password = admin['contrasena_admin']
            
            # Verificar si la contraseña está hasheada
            if is_password_hashed(stored_password):
                # Verificar contraseña hasheada
                if check_password_hash(stored_password, password):
                    session['admin_logged_in'] = True
                    session['admin_username'] = admin['email_admin']
                    flash('Inicio de sesión exitoso', 'success')
                    return redirect(url_for('admin.dashboard'))
                else:
                    flash('Usuario o contraseña incorrectos', 'danger')
            else:
                # Contraseña en texto plano - verificar y migrar
                if stored_password == password:
                    # Migrar la contraseña a formato hasheado
                    if migrate_password_to_hash(admin['id_administrador'], password):
                        session['admin_logged_in'] = True
                        session['admin_username'] = admin['email_admin']
                        flash('Inicio de sesión exitoso (contraseña migrada a formato seguro)', 'success')
                        return redirect(url_for('admin.dashboard'))
                    else:
                        flash('Error al migrar contraseña. Contacta al administrador del sistema.', 'danger')
                else:
                    flash('Usuario o contraseña incorrectos', 'danger')
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('Login_admin/login_admin.html')

# ---------------------------------------
# Ruta para migrar todas las contraseñas (SOLO PARA DESARROLLO/MANTENIMIENTO)
# ---------------------------------------
@admin_bp.route('/admin/migrate-passwords', methods=['POST'])
@admin_login_required
def migrate_passwords_route():
    """
    Ruta para migrar todas las contraseñas.
    SOLO debe usarse en desarrollo o mantenimiento.
    """
    result = migrate_all_passwords()
    
    if result['success']:
        flash(
            f'Migración completada: {result["migrated"]} migradas, '
            f'{result["already_hashed"]} ya hasheadas, '
            f'{result["total"]} total de administradores.',
            'success'
        )
    else:
        flash(f'Error en la migración: {result["error"]}', 'danger')
    
    return redirect(url_for('admin.dashboard'))

# ---------------------------------------
# Panel principal del administrador
# ---------------------------------------
@admin_bp.route('/admin/dashboard')
@admin_login_required
def dashboard():
    return render_template('admin_interfaz/admininterfaz.html.j2')

# ---------------------------------------
# Reporte de ventas
# ---------------------------------------
@admin_bp.route('/admin/ventas')
@admin_login_required
def admin_ventas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.nombre_producto AS producto, 
            SUM(d.cantidad_producto) AS total_vendido, 
            SUM(d.cantidad_producto * p.precio_producto) AS total_ingresos
        FROM detalle_facturacion d
        JOIN producto p ON d.id_producto = p.id_producto
        JOIN facturacion f ON d.id_factura = f.id_factura
        GROUP BY p.id_producto, p.nombre_producto
        ORDER BY total_vendido DESC
    """)
    ventas = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('ventas-sistema/ventas_admin.html.j2', ventas=ventas)

# ---------------------------------------
# API de estadísticas corregida
# ---------------------------------------
@admin_bp.route('/api/estadisticas')
@admin_login_required
def get_estadisticas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener parámetros de fecha
        mes = request.args.get('mes', datetime.now().month)
        anio = request.args.get('anio', datetime.now().year)
        
        # Consulta principal de estadísticas
        cursor.execute("""
            SELECT 
                COALESCE(SUM(df.cantidad_producto * p.precio_producto), 0) as ventas_mes,
                COALESCE(SUM(df.cantidad_producto), 0) as productos_vendidos,
                COALESCE(COUNT(DISTINCT f.id_usuario), 0) as total_clientes,
                COALESCE(COUNT(DISTINCT f.id_factura), 0) as total_ventas,
                COALESCE(AVG(df.cantidad_producto * p.precio_producto), 0) as promedio_venta
            FROM facturacion f
            JOIN detalle_facturacion df ON f.id_factura = df.id_factura
            JOIN producto p ON df.id_producto = p.id_producto
            WHERE MONTH(f.fecha_compra) = %s AND YEAR(f.fecha_compra) = %s
        """, (mes, anio))
        
        estadisticas = cursor.fetchone()
        
        # Consulta de productos con bajo stock
        cursor.execute("""
            SELECT nombre_producto, cantidad_disponible as stock
            FROM producto
            WHERE cantidad_disponible < 20
            ORDER BY cantidad_disponible ASC
            LIMIT 10
        """)
        
        productos_bajo_stock = cursor.fetchall()
        
        # Consulta de productos más vendidos del mes
        cursor.execute("""
            SELECT 
                p.nombre_producto,
                SUM(df.cantidad_producto) as cantidad_vendida,
                SUM(df.cantidad_producto * p.precio_producto) as ingresos_generados
            FROM facturacion f
            JOIN detalle_facturacion df ON f.id_factura = df.id_factura
            JOIN producto p ON df.id_producto = p.id_producto
            WHERE MONTH(f.fecha_compra) = %s AND YEAR(f.fecha_compra) = %s
            GROUP BY p.id_producto, p.nombre_producto
            ORDER BY cantidad_vendida DESC
            LIMIT 5
        """, (mes, anio))
        
        productos_mas_vendidos = cursor.fetchall()
        
        # Preparar respuesta
        resultado = {
            'ventas_mes': float(estadisticas['ventas_mes']) if estadisticas['ventas_mes'] else 0,
            'productos_vendidos': int(estadisticas['productos_vendidos']) if estadisticas['productos_vendidos'] else 0,
            'total_clientes': int(estadisticas['total_clientes']) if estadisticas['total_clientes'] else 0,
            'total_ventas': int(estadisticas['total_ventas']) if estadisticas['total_ventas'] else 0,
            'promedio_venta': float(estadisticas['promedio_venta']) if estadisticas['promedio_venta'] else 0,
            'productos_bajo_stock': productos_bajo_stock,
            'productos_mas_vendidos': productos_mas_vendidos
        }
        
        cursor.close()
        conn.close()
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"Error en get_estadisticas: {e}")
        return jsonify({'error': str(e)}), 500

# ---------------------------------------
# API de ventas detalladas
# ---------------------------------------
@admin_bp.route('/api/ventas')
@admin_login_required
def get_ventas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener parámetros de fecha
        fecha_inicio = request.args.get('inicio', '')
        fecha_fin = request.args.get('fin', '')
        
        # Consulta base
        base_query = """
            SELECT 
                DATE_FORMAT(f.fecha_compra, '%Y-%m-%d') as fecha_compra,
                TIME_FORMAT(f.hora, '%H:%i') as hora,
                p.nombre_producto,
                df.cantidad_producto,
                p.precio_producto as precio_unitario,
                (df.cantidad_producto * p.precio_producto) as subtotal,
                CONCAT(u.nombres_usuario, ' ', u.apellidos_usuario) as cliente
            FROM facturacion f
            JOIN detalle_facturacion df ON f.id_factura = df.id_factura
            JOIN producto p ON df.id_producto = p.id_producto
            JOIN usuario u ON f.id_usuario = u.id_usuario
        """
        
        params = []
        where_clauses = []
        
        # Agregar filtros de fecha si se proporcionan
        if fecha_inicio:
            where_clauses.append("DATE(f.fecha_compra) >= %s")
            params.append(fecha_inicio)
            
        if fecha_fin:
            where_clauses.append("DATE(f.fecha_compra) <= %s")
            params.append(fecha_fin)
        
        # Construir consulta final
        if where_clauses:
            query = base_query + " WHERE " + " AND ".join(where_clauses)
        else:
            query = base_query
            
        query += " ORDER BY f.fecha_compra DESC, f.hora DESC LIMIT 1000"
        
        cursor.execute(query, params)
        ventas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(ventas)
        
    except Exception as e:
        print(f"Error en get_ventas: {e}")
        return jsonify({'error': str(e)}), 500

# ---------------------------------------
# Cerrar sesión del administrador
# ---------------------------------------
@admin_bp.route('/admin/logout')
@admin_login_required
def logout_admin():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('admin.login_admin'))