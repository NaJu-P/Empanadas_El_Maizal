# blueprints/auth.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import schedule
import time
import threading
from datetime import datetime, timedelta
from functools import wraps
import logging
import re
from db.conexion import get_db_connection
from utils.email import send_password_change_confirmation, send_reset_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def is_logged_in():
    """Verificar si el usuario tiene sesión activa"""
    return session.get('logged_in', False)

def get_current_user():
    """Obtener datos del usuario actual de la sesión"""
    if is_logged_in():
        return {
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('user_email')
        }
    return None

def login_required(f):
    """Decorador para requerir autenticación en rutas protegidas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            flash('Debes iniciar sesión primero', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def login_user(user_data):
    """Crear sesión de usuario después de validar credenciales"""
    session['user_id'] = user_data['id_usuario']
    session['user_name'] = user_data['nombre_usuario'] 
    session['user_email'] = user_data['email_usuario']
    session['logged_in'] = True

def login_required(f):
    """Decorador para requerir autenticación en rutas protegidas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            flash('Debes iniciar sesión primero', 'error')
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function


def cleanup_expired_tokens():
    """Elimina tokens de restablecimiento de contraseña expirados de la base de datos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Eliminar tokens expirados
        cursor.execute('DELETE FROM reiniciar_contrasena_tokens WHERE expires_at < %s', (datetime.now(),))
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return deleted_count
        
    except Exception as e:
        logging.error(f"Error limpiando tokens expirados: {e}")
        return 0

def cleanup_used_tokens():
    """Elimina solo los tokens que ya fueron utilizados"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('DELETE FROM reiniciar_contrasena_tokens WHERE used = TRUE')
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return deleted_count
        
    except Exception as e:
        logging.error(f"Error limpiando tokens usados: {e}")
        return 0

def cleanup_all_tokens():
    """Elimina TODOS los tokens (incluso los no expirados) - usar con cuidado"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('DELETE FROM reiniciar_contrasena_tokens')
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return deleted_count
        
    except Exception as e:
        logging.error(f"Error eliminando todos los tokens: {e}")
        return 0

def get_tokens_stats():
    """Obtiene estadísticas de los tokens en la base de datos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT COUNT(*) as total FROM reiniciar_contrasena_tokens')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as expired FROM reiniciar_contrasena_tokens WHERE expires_at < %s', (datetime.now(),))
        expired = cursor.fetchone()['expired']
        
        cursor.execute('SELECT COUNT(*) as used FROM reiniciar_contrasena_tokens WHERE used = TRUE')
        used = cursor.fetchone()['used']
        
        cursor.execute('''
            SELECT COUNT(*) as active 
            FROM reiniciar_contrasena_tokens
            WHERE expires_at > %s AND used = FALSE
        ''', (datetime.now(),))
        active = cursor.fetchone()['active']
        
        cursor.close()
        conn.close()
        
        stats = {
            'total': total,
            'expired': expired,
            'used': used,
            'active': active
        }
        
        return stats
        
    except Exception as e:
        logging.error(f"Error obteniendo estadísticas de tokens: {e}")
        return None

def cleanup_expired_tokens_job():
    """Job que se ejecuta periódicamente para limpiar tokens"""
    cleanup_expired_tokens()
    cleanup_used_tokens()  # También limpia tokens usados

def start_cleanup_scheduler():
    """Inicia el scheduler en un hilo separado para limpiar tokens automáticamente"""
    schedule.every(6).hours.do(cleanup_expired_tokens_job)
    
    schedule.every().day.at("03:00").do(cleanup_expired_tokens_job)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()


def is_logged_in():
    """Verificar si el usuario tiene sesión activa"""
    return session.get('logged_in', False)

def get_current_user():
    """Obtener datos del usuario actual de la sesión"""
    if is_logged_in():
        return {
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('user_email')
        }
    return None

@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Mostrar tu página de login existente"""
    return render_template('auth/login2.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        nombre = request.form.get('nombre', '').strip()
        apellidos = request.form.get('apellidos', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()
        ciudad = request.form.get('ciudad', '').strip()
        fecha_nacimiento = datetime.now().date()
        
        if not all([nombre, apellidos, email, password, telefono, direccion, ciudad]):
            return jsonify({
                'success': False, 
                'message': 'Todos los campos son obligatorios'
            }), 400
        
        password = request.form.get('password', '')

        # Verifica longitud antes de hashear
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 6 caracteres'
            }), 400
        
        hashed_password = generate_password_hash(password)
        
        if not re.match(r'^[0-9]{10}$', telefono):
            return jsonify({
                'success': False, 
                'message': 'El teléfono debe tener exactamente 10 dígitos'
            }), 400
        
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({
                'success': False, 
                'message': 'Formato de email inválido'
            }), 400
        
        if len(direccion) < 10:
            return jsonify({
                'success': False, 
                'message': 'La dirección debe tener al menos 10 caracteres'
            }), 400
        
        if len(direccion) > 200:
            return jsonify({
                'success': False, 
                'message': 'La dirección no puede exceder 200 caracteres'
            }), 400
        
        if len(ciudad) < 2:
            return jsonify({
                'success': False, 
                'message': 'La ciudad debe tener al menos 2 caracteres'
            }), 400
        
        if len(ciudad) > 100:
            return jsonify({
                'success': False, 
                'message': 'La ciudad no puede exceder 100 caracteres'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM usuario WHERE email_usuario = %s', (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                if existing_user['email_usuario'] == email:
                    return jsonify({'success': False, 'message': 'Este email ya está registrado'}), 400
                else:
                    return jsonify({'success': False, 'message': 'Esta cédula ya está registrada'}), 400

            cursor.execute('''
                INSERT INTO usuario (nombres_usuario, apellidos_usuario, email_usuario, contraseña, fecha_nacimiento, telefono)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (nombre, apellidos, email, hashed_password, fecha_nacimiento, telefono))

            id_usuario = cursor.lastrowid

            cursor.execute('''
                INSERT INTO ubicacion (id_usuario, direccion_usuario, ciudad) 
                VALUES (%s, %s, %s)
            ''', (id_usuario, direccion, ciudad))

            conn.commit()

            session['user_id'] = id_usuario
            session['user_name'] = nombre
            session['user_email'] = email
            session['user_address'] = direccion
            session['user_city'] = ciudad
            session['logged_in'] = True

            return jsonify({'success': True, 'message': 'Registro exitoso', 'redirect': '/Home'}), 200

        except Exception as e:
            conn.rollback()
            logging.error(f"Error en registro: {e}")
            return jsonify({'success': False, 'message': 'Error al registrar usuario'}), 500

        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        logging.error(f"Error del servidor en registro: {e}")
        return jsonify({'success': False, 'message': 'Error del servidor'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Todos son falsos'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute('''
                SELECT * FROM usuario 
                WHERE email_usuario = %s OR telefono = %s OR id_usuario = %s
            ''', (email, email, email))

            user = cursor.fetchone()

            logging.info(f"Intento de login para: {email}")
            logging.info(f"Datos del usuario encontrado: {user}")

            if user:
                stored_password = user.get('contraseña')

                if not stored_password or not stored_password.startswith(('pbkdf2:', 'scrypt:', 'sha256$')):
                    logging.warning("Contraseña no segura o vacía para usuario: %s", email)
                    return jsonify({
                        'success': False,
                        'message': 'Contraseña almacenada de forma insegura. Por favor restablece tu contraseña.'
                    }), 401

                if check_password_hash(stored_password, password):
                    session['user_id'] = user['id_usuario']
                    session['user_name'] = user['nombres_usuario']
                    session['user_email'] = user['email_usuario']
                    session['logged_in'] = True

                    return jsonify({
                        'success': True,
                        'message': 'Inicio de sesión exitoso',
                        'redirect': '/Home'
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Credenciales incorrectas'
                    }), 401
                
            else:
                return jsonify({
                    'success': False,
                    'message': 'Credenciales incorrectas'
                }), 401

        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        logging.error(f"Error en login: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'Error del servidor'
        }), 500

@auth_bp.route('/Restablecer-Contraseña', methods=['GET', 'POST'])
def restablecer_contrasena():
    if request.method == 'POST':
        email = request.form['email']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuario WHERE email_usuario = %s', (email,))
        user = cursor.fetchone()
        
        if user:
            token = secrets.token_urlsafe(5)
            expires_at = datetime.now() + timedelta(hours=1)
            
            cursor.execute('''
                INSERT INTO reiniciar_contrasena_tokens (email_usuario, token, expires_at, used, id_usuario) 
                SELECT u.email_usuario, %s, %s, %s, u.id_usuario
                FROM usuario u
                WHERE u.email_usuario = %s
            ''', (token, expires_at, False, email))
            conn.commit()
            
            user_session_email = session.get('user_email')
            if send_reset_email(email, token, user_session_email):
                flash('Se ha enviado un enlace de restablecimiento a tu email', 'success')
            else:
                flash('Error al enviar el email. Intenta nuevamente.', 'error')
        else:
            flash('Se ha enviado un enlace de restablecimiento a tu email', 'success')
        
        cursor.close()
        conn.close()
        return redirect(url_for('auth.restablecer_contrasena'))
    
    return render_template('/auth/restablecer_contrasena.html')

@auth_bp.route('/Cambiar-Contraseña', methods=['GET', 'POST'])
@auth_bp.route('/Cambiar-Contraseña/<token>', methods=['GET', 'POST'])
def cambiar_contrasena(token=None):
    from_email_reset = token is not None
    user_email = None
    token_verified = False
    
    if token:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT * FROM reiniciar_contrasena_tokens
            WHERE token = %s AND expires_at > %s AND used = FALSE
        ''', (token, datetime.now()))
        reset_token = cursor.fetchone()
        
        if not reset_token:
            flash('Token inválido o expirado', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('auth.restablecer_contrasena'))
        
        user_email = reset_token['email_usuario']
        cursor.close()
        conn.close()
        
        session_token_key = f"verified_token_{token}"
        token_verified = session.get(session_token_key, False)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'verify_token':
            provided_token = request.form.get('provided_token')
            token_input = request.form.get('token_input')
            
            if not token_input or len(token_input) != 7:
                return jsonify({
                    'success': False,
                    'message': 'El token debe tener 7 caracteres'
                })
            
            if provided_token == token_input:
                session_token_key = f"verified_token_{token}"
                session[session_token_key] = True
                session.permanent = True
                
                return jsonify({
                    'success': True,
                    'message': 'Token verificado correctamente',
                    'user_email': user_email
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Token incorrecto. Por favor verifica el código.'
                })
        
        elif action == 'change_password':
            verified_token = request.form.get('verified_token')
            
            session_token_key = f"verified_token_{verified_token}"
            if not session.get(session_token_key, False):
                return jsonify({
                    'success': False,
                    'message': 'Sesión expirada. Por favor verifica el token nuevamente.'
                })
            
            email = user_email
            new_password = request.form['newPassword']
            confirm_password = request.form['confirmPassword']
            
            if new_password != confirm_password:
                return jsonify({
                    'success': False,
                    'message': 'Las contraseñas no coinciden'
                })
            
            if len(new_password) < 8:
                return jsonify({
                    'success': False,
                    'message': 'La contraseña debe tener al menos 8 caracteres'
                })
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            try:
                # HASH antes de actualizar
                hashed_password = generate_password_hash(new_password)

                cursor.execute('UPDATE usuario SET contraseña = %s WHERE email_usuario = %s',
                            (hashed_password, email))
                cursor.execute('UPDATE reiniciar_contrasena_tokens SET used = TRUE WHERE token = %s',
                            (token,))

                conn.commit()

                session.pop(session_token_key, None)

                user_session_email = session.get('user_email')
                send_password_change_confirmation(email, user_session_email)

                return jsonify({
                    'success': True,
                    'message': 'Contraseña actualizada exitosamente. Redirigiendo al Home...',
                    'redirect': url_for('auth.login_page')
                })

            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': 'Error al actualizar la contraseña'
                })
            finally:
                cursor.close()
                conn.close()
        
        else:
            email = request.form['email']
            new_password = request.form['newPassword']
            confirm_password = request.form['confirmPassword']
            
            if new_password != confirm_password:
                return jsonify({
                    'success': False, 
                    'message': 'Las contraseñas no coinciden'
                })
            
            if len(new_password) < 8:
                return jsonify({
                    'success': False, 
                    'message': 'La contraseña debe tener al menos 8 caracteres'
                })
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM usuario WHERE email_usuario = %s', (email,))
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False, 
                    'message': 'Email no encontrado'
                })
            
            try:
                hashed_password = generate_password_hash(new_password)
                cursor.execute('UPDATE usuario SET contraseña = %s WHERE email_usuario = %s',
                            (hashed_password, email))
                conn.commit()
                
                send_password_change_confirmation(email)
                
                return jsonify({
                    'success': True, 
                    'message': 'Contraseña actualizada exitosamente'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False, 
                    'message': 'Error al actualizar la contraseña'
                })
            finally:
                cursor.close()
                conn.close()
    
    return render_template('auth/cambiar_contrasena.html', 
                         from_email_reset=from_email_reset, 
                         user_email=user_email,
                         token=token,
                         token_verified=token_verified)

@auth_bp.route('/reset-password/<token>')
def reset_password_redirect(token):
    return redirect(url_for('auth.cambiar_contrasena', token=token))

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    
    # Si es una petición AJAX/fetch, devolver JSON
    if request.headers.get('Content-Type') == 'application/json' or request.is_json:
        return jsonify({
            'success': True,
            'message': 'Sesión cerrada exitosamente',
            'redirect': '/Home?logout_success=true'  # Parámetro claro
        })
    
    # Si es una petición normal, redirigir al home con parámetro
    flash('Sesión cerrada exitosamente', 'success')
    return redirect('/Home?logout_success=true')

# ==================== RUTAS ADMINISTRATIVAS ====================

@auth_bp.route('/admin/tokens/stats')
@login_required
def admin_tokens_stats():
    """Endpoint para ver estadísticas de tokens (solo para administradores)"""
    stats = get_tokens_stats()
    return jsonify(stats) if stats else jsonify({'error': 'Error obteniendo estadísticas'})

@auth_bp.route('/admin/tokens/cleanup', methods=['POST'])
@login_required
def admin_cleanup_tokens():
    """Endpoint para limpiar tokens manualmente (solo para administradores)"""
    cleanup_type = request.form.get('type', 'expired')
    
    if cleanup_type == 'expired':
        deleted = cleanup_expired_tokens()
        message = f"Se eliminaron {deleted} tokens expirados"
    elif cleanup_type == 'used':
        deleted = cleanup_used_tokens()
        message = f"Se eliminaron {deleted} tokens usados"
    elif cleanup_type == 'all':
        deleted = cleanup_all_tokens()
        message = f"Se eliminaron {deleted} tokens en total"
    else:
        return jsonify({'success': False, 'message': 'Tipo de limpieza inválido'})
    
    return jsonify({'success': True, 'message': message, 'deleted': deleted})

# ==================== INICIALIZACIÓN ====================

def init_auth_system():
    
    cleanup_expired_tokens()
    cleanup_used_tokens()
    
    start_cleanup_scheduler()
    

def cleanup_expired_tokens_legacy():
    return cleanup_expired_tokens()