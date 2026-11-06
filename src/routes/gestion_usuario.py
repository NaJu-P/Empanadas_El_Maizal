from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from db.conexion import get_db_connection  # Ajusta si la ruta es distinta
from routes.admin import admin_login_required
from datetime import datetime
import logging

gestion_usuario_bp = Blueprint("gestion_usuario", __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------
# Gestión de usuarios (mostrar clientes y domiciliarios)
# ---------------------------------------
@gestion_usuario_bp.route('/admin/usuarios')
@admin_login_required
def gestion_usuarios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Paginación para clientes
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page

        # Obtener total de clientes
        cursor.execute("SELECT COUNT(*) as total FROM usuario")
        total_clientes = cursor.fetchone()['total']

        # Obtener clientes paginados
        cursor.execute("""
            SELECT 
                id_usuario, 
                nombres_usuario, 
                apellidos_usuario, 
                email_usuario, 
                telefono, 
                fecha_nacimiento
            FROM usuario
            ORDER BY id_usuario DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        clientes = cursor.fetchall()
        
        # Formatear fechas de clientes
        for cliente in clientes:
            if cliente['fecha_nacimiento']:
                cliente['fecha_nacimiento'] = cliente['fecha_nacimiento'].strftime('%d/%m/%Y')

        # Obtener todos los domiciliarios (sin paginación por ahora)
        cursor.execute("""
            SELECT 
                id_domiciliario, 
                nombres_domiciliario, 
                email_domiciliario, 
                telefono
            FROM domiciliario
            ORDER BY id_domiciliario DESC
        """)
        domiciliarios = cursor.fetchall()
        
        # Calcular número total de páginas para clientes
        total_pages = (total_clientes + per_page - 1) // per_page
        
        return render_template('gestion_usuarios/gestion_usuarios.html.j2', 
                            clientes=clientes,
                            domiciliarios=domiciliarios,
                            titulo="Gestión de Usuarios",
                            now=datetime.now(),
                            pagination={
                                'page': page,
                                'per_page': per_page,
                                'total': total_clientes,
                                'pages': total_pages
                            })
    except Exception as e:
        logger.error(f"Error al obtener usuarios: {e}")
        flash("Error al cargar la lista de usuarios", "danger")
        return render_template('gestion_usuarios/gestion_usuarios.html.j2', 
                            clientes=[],
                            domiciliarios=[],
                            titulo="Gestión de Usuarios",
                            now=datetime.now(),
                            pagination={
                                'page': 1,
                                'per_page': per_page,
                                'total': 0,
                                'pages': 0
                            })
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------------------------------
# Obtener contraseña de cliente (API)
# ---------------------------------------
@gestion_usuario_bp.route('/obtener_clave/<int:id>')
@admin_login_required
def obtener_clave(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT contraseña FROM usuario WHERE id_usuario = %s", (id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            return jsonify({'error': 'Cliente no encontrado'}), 404
            
        return jsonify({'clave': cliente['contraseña']})
    except Exception as e:
        logger.error(f"Error al obtener clave: {e}")
        return jsonify({'error': 'Error al obtener la clave'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------------------------------
# Obtener contraseña de domiciliario (API)
# ---------------------------------------
@gestion_usuario_bp.route('/obtener_clave_domiciliario/<int:id>')
@admin_login_required
def obtener_clave_domiciliario(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT contraseña_domiciliario FROM domiciliario WHERE id_domiciliario = %s", (id,))
        domiciliario = cursor.fetchone()
        
        if not domiciliario:
            return jsonify({'error': 'Domiciliario no encontrado'}), 404
            
        return jsonify({'clave': domiciliario['contraseña_domiciliario']})
    except Exception as e:
        logger.error(f"Error al obtener clave del domiciliario: {e}")
        return jsonify({'error': 'Error al obtener la clave'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------------------------------
# Eliminar cliente
# ---------------------------------------
@gestion_usuario_bp.route('/eliminar_cliente/<int:id>', methods=['POST'])
@admin_login_required
def eliminar_cliente(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si el cliente tiene pedidos
        cursor.execute("SELECT id_factura FROM facturacion WHERE id_usuario = %s LIMIT 1", (id,))
        if cursor.fetchone():
            flash("No se puede eliminar el cliente porque tiene pedidos asociados", "warning")
            return redirect(url_for('gestion_usuario.gestion_usuarios'))
            
        # Eliminar el cliente
        cursor.execute("DELETE FROM usuario WHERE id_usuario = %s", (id,))
        conn.commit()
        flash("Cliente eliminado exitosamente", "success")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al eliminar cliente {id}: {e}")
        flash("Error al eliminar el cliente", "danger")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('gestion_usuario.gestion_usuarios'))

# ---------------------------------------
# Eliminar domiciliario
# ---------------------------------------
@gestion_usuario_bp.route('/eliminar_domiciliario/<int:id>', methods=['POST'])
@admin_login_required
def eliminar_domiciliario(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si el domiciliario tiene entregas
        cursor.execute("SELECT id_tipo_entrega FROM tipo_entrega WHERE id_domiciliario = %s LIMIT 1", (id,))
        if cursor.fetchone():
            flash("No se puede eliminar el domiciliario porque tiene entregas asociadas", "warning")
            return redirect(url_for('gestion_usuario.gestion_usuarios'))
            
        # Eliminar el domiciliario
        cursor.execute("DELETE FROM domiciliario WHERE id_domiciliario = %s", (id,))
        conn.commit()
        flash("Domiciliario eliminado exitosamente", "success")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al eliminar domiciliario {id}: {e}")
        flash("Error al eliminar el domiciliario", "danger")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('gestion_usuario.gestion_usuarios'))

# ---------------------------------------
# Editar cliente
# ---------------------------------------
@gestion_usuario_bp.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
@admin_login_required
def editar_cliente(id):
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_usuario, nombres_usuario, apellidos_usuario, 
                       email_usuario, telefono 
                FROM usuario WHERE id_usuario = %s
            """, (id,))
            cliente = cursor.fetchone()
            
            if not cliente:
                flash("Cliente no encontrado", "error")
                return redirect(url_for('gestion_usuario.gestion_usuarios'))
            
            return jsonify(cliente)
        except Exception as e:
            logger.error(f"Error al obtener cliente {id}: {e}")
            return jsonify({'error': 'Error al obtener el cliente'}), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    elif request.method == 'POST':
        try:
            data = request.json
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE usuario 
                SET nombres_usuario = %s, apellidos_usuario = %s, 
                    email_usuario = %s, telefono = %s
                WHERE id_usuario = %s
            """, (
                data['nombres_usuario'],
                data['apellidos_usuario'], 
                data['email_usuario'],
                data['telefono'],
                id
            ))
            conn.commit()
            
            return jsonify({'success': True, 'message': 'Cliente actualizado exitosamente'})
        except Exception as e:
            conn.rollback()
            logger.error(f"Error al actualizar cliente {id}: {e}")
            return jsonify({'error': 'Error al actualizar el cliente'}), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# ---------------------------------------
# Editar domiciliario
# ---------------------------------------
@gestion_usuario_bp.route('/editar_domiciliario/<int:id>', methods=['GET', 'POST'])
@admin_login_required
def editar_domiciliario(id):
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_domiciliario, nombres_domiciliario, 
                       email_domiciliario, telefono 
                FROM domiciliario WHERE id_domiciliario = %s
            """, (id,))
            domiciliario = cursor.fetchone()
            
            if not domiciliario:
                flash("Domiciliario no encontrado", "error")
                return redirect(url_for('gestion_usuario.gestion_usuarios'))
            
            return jsonify(domiciliario)
        except Exception as e:
            logger.error(f"Error al obtener domiciliario {id}: {e}")
            return jsonify({'error': 'Error al obtener el domiciliario'}), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    elif request.method == 'POST':
        try:
            data = request.json
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE domiciliario 
                SET nombres_domiciliario = %s, email_domiciliario = %s, telefono = %s 
                WHERE id_domiciliario = %s
            """, (
                data['nombres_domiciliario'],
                data['email_domiciliario'],
                data['telefono'],
                id
            ))
            conn.commit()
            
            return jsonify({'success': True, 'message': 'Domiciliario actualizado exitosamente'})
        except Exception as e:
            conn.rollback()
            logger.error(f"Error al actualizar domiciliario {id}: {e}")
            return jsonify({'error': 'Error al actualizar el domiciliario'}), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()