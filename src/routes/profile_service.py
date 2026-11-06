from flask import session, jsonify, request, Blueprint, Response
import logging
import mysql.connector
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from db.conexion import get_db_connection

class ProfileService:
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_user_id_from_session(self) -> Optional[int]:
        return session.get('user_id')
    
    def validate_user_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:

        nombre = data.get('nombres_usuario', '').strip()
        if not nombre or len(nombre) < 2:
            return False, "El nombre debe tener al menos 2 caracteres"
        
        email = data.get('email_usuario', '').strip()
        if not email or '@' not in email or '.' not in email:
            return False, "El formato del email no es válido"
        
        telefono = data.get('telefono', '').strip()
        if telefono:
            clean_phone = telefono.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            if not clean_phone.isdigit() or len(clean_phone) < 7:
                return False, "El formato del teléfono no es válido"
        
        return True, "Datos válidos"

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Obtiene el perfil completo del usuario"""
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            user_query = """
            SELECT 
                id_usuario,
                nombres_usuario,     
                email_usuario,
                telefono
            FROM usuario 
            WHERE id_usuario = %s
            """
            cursor.execute(user_query, (user_id,))
            user_result = cursor.fetchone()
            
            if not user_result:
                return {'success': False, 'message': 'Usuario no encontrado'}
            
            location_query = """
            SELECT direccion_usuario 
            FROM ubicacion 
            WHERE id_usuario = %s
            """
            cursor.execute(location_query, (user_id,))
            location_result = cursor.fetchone()
            
            return {
                'success': True,
                'user': {
                    'nombres_usuario': user_result.get('nombres_usuario') or '',     # ← CAMBIO AQUÍ
                    'email_usuario': user_result.get('email_usuario') or '',
                    'telefono': user_result.get('telefono') or '',
                    'direccion_usuario': location_result.get('direccion_usuario') if location_result else ''
                }
            }
                
        except mysql.connector.Error as e:
            self.logger.error(f"Error de MySQL obteniendo perfil de usuario {user_id}: {e}")
            return {'success': False, 'message': f'Error de base de datos: {str(e)}'}
        except Exception as e:
            self.logger.error(f"Error obteniendo perfil de usuario {user_id}: {e}")
            return {'success': False, 'message': 'Error interno del servidor'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_user_profile(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza el perfil del usuario"""
        connection = None
        cursor = None
        try:
            self.logger.info(f"Actualizando perfil para usuario {user_id} con datos: {data}")
            
            is_valid, message = self.validate_user_data(data)
            if not is_valid:
                self.logger.error(f"Datos inválidos: {message}")
                return {'success': False, 'message': message}
            
            connection = get_db_connection()
            cursor = connection.cursor()
            
            check_user_query = "SELECT id_usuario FROM usuario WHERE id_usuario = %s"
            cursor.execute(check_user_query, (user_id,))
            if not cursor.fetchone():
                self.logger.error(f"Usuario {user_id} no encontrado")
                return {'success': False, 'message': 'Usuario no encontrado'}
            
            update_user_query = """
            UPDATE usuario 
            SET nombres_usuario = %s,      
                email_usuario = %s, 
                telefono = %s
            WHERE id_usuario = %s
            """
            cursor.execute(update_user_query, (
                data['nombres_usuario'].strip(),
                data['email_usuario'].strip(),
                data.get('telefono', '').strip() or None,
                user_id
            ))
            
            self.logger.info(f"Usuario actualizado, filas afectadas: {cursor.rowcount}")
            
            direccion = data.get('direccion_usuario', '').strip()
            if direccion:
                check_location_query = "SELECT id_ubicacion FROM ubicacion WHERE id_usuario = %s"
                cursor.execute(check_location_query, (user_id,))
                location_exists = cursor.fetchone()
                
                if location_exists:
                    update_location_query = """
                    UPDATE ubicacion 
                    SET direccion_usuario = %s 
                    WHERE id_usuario = %s
                    """
                    cursor.execute(update_location_query, (direccion, user_id))
                    self.logger.info(f"Ubicación actualizada, filas afectadas: {cursor.rowcount}")
                else:
                    # Insertar nueva ubicación
                    insert_location_query = """
                    INSERT INTO ubicacion (id_usuario, direccion_usuario) 
                    VALUES (%s, %s)
                    """
                    cursor.execute(insert_location_query, (user_id, direccion))
                    self.logger.info(f"Nueva ubicación insertada")
            
            connection.commit()
            
            self.logger.info(f"Perfil actualizado exitosamente para usuario {user_id}")
            return {
                'success': True, 
                'message': 'Perfil actualizado correctamente'
            }
            
        except mysql.connector.Error as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Error de MySQL actualizando perfil de usuario {user_id}: {e}")
            return {'success': False, 'message': f'Error de base de datos: {str(e)}'}
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Error actualizando perfil de usuario {user_id}: {e}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


def create_profile_routes(profile_service):
    """Crea las rutas del perfil para agregar a tu Flask app"""
    profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')
    
    @profile_bp.route('/get', methods=['GET'])
    def get_profile():
        """Endpoint para obtener el perfil del usuario"""
        user_id = profile_service.get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401
        
        result = profile_service.get_user_profile(user_id)
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
    
    @profile_bp.route('/update', methods=['POST'])
    def update_profile():
        """Endpoint para actualizar el perfil del usuario"""
        user_id = profile_service.get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Datos no válidos'}), 400
        
        result = profile_service.update_user_profile(user_id, data)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    
    @profile_bp.route('/debug/columns', methods=['GET'])
    def debug_columns():
        """Endpoint para debug - ver estructura de tablas"""
        user_id = profile_service.get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("DESCRIBE usuario")
            usuario_columns = cursor.fetchall()
            
            cursor.execute("DESCRIBE ubicacion")
            ubicacion_columns = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'tables': {
                    'usuario': [col['Field'] for col in usuario_columns],
                    'ubicacion': [col['Field'] for col in ubicacion_columns]
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    return profile_bp