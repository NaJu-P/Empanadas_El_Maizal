# opiniones_service.py - Servicio optimizado para gestión de opiniones con JOINs - SIN ALIAS

from flask import Blueprint, render_template, session, request, jsonify
from db.conexion import get_db_connection
import logging
import mysql.connector
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
from routes.auth import login_required

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

opiniones_bp = Blueprint('Opiniones', __name__)

# Cache simple en memoria (para producción usar Redis)
opiniones_cache = {}
productos_cache = {'data': None, 'timestamp': 0}
estadisticas_cache = {'data': None, 'timestamp': 0}

# Configuración de cache
OPINIONES_CACHE_DURATION = 300  # 5 minutos
PRODUCTOS_CACHE_DURATION = 1800  # 30 minutos
ESTADISTICAS_CACHE_DURATION = 600  # 10 minutos

class OpinionesService:
    """Servicio para gestión de opiniones"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validar_opinion_data(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Valida los datos de la opinión"""
        # Validar ID usuario (ahora requerido)
        id_usuario = data.get('id_usuario')
        if not id_usuario:
            return False, "ID de usuario es requerido"
        
        # Validar ID producto (ahora requerido)
        id_producto = data.get('id_producto')
        if not id_producto:
            return False, "ID de producto es requerido"
        
        # Validar calificación
        calificacion = data.get('calificacion')
        if not calificacion or not isinstance(calificacion, int) or calificacion < 1 or calificacion > 5:
            return False, "La calificación debe ser un número entre 1 y 5"
        
        # Validar descripción
        descripcion = data.get('descripcion_opinion', '').strip()
        if not descripcion or len(descripcion) < 10:
            return False, "La opinión debe tener al menos 10 caracteres"
        
        return True, "Datos válidos"
    
    def invalidar_cache_opiniones(self):
        """Invalidar todos los caches relacionados con opiniones"""
        global opiniones_cache, estadisticas_cache
        opiniones_cache.clear()
        estadisticas_cache['data'] = None
        estadisticas_cache['timestamp'] = 0
    
    def crear_opinion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva opinión en la base de datos"""
        connection = None
        cursor = None
        try:
            # Validar datos
            is_valid, message = self.validar_opinion_data(data)
            if not is_valid:
                return {'success': False, 'message': message}
            
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Verificar que el usuario existe
            cursor.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (data['id_usuario'],))
            if not cursor.fetchone():
                return {'success': False, 'message': 'Usuario no encontrado'}
            
            # Verificar que el producto existe
            cursor.execute("SELECT id_producto FROM producto WHERE id_producto = %s", (data['id_producto'],))
            if not cursor.fetchone():
                return {'success': False, 'message': 'Producto no encontrado'}
            
            # Preparar datos para inserción
            insert_query = """
            INSERT INTO opiniones (
                id_usuario,
                id_producto,
                calificacion, 
                descripcion_opinion, 
                fecha_creacion,
                publicar
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # Obtener fecha actual
            fecha_actual = datetime.now()
            
            # Ejecutar inserción
            cursor.execute(insert_query, (
                data['id_usuario'],
                data['id_producto'],
                data['calificacion'],
                data['descripcion_opinion'].strip(),
                fecha_actual,
                data.get('publicar', False)
            ))
            
            connection.commit()
            
            # Invalidar cache después de crear opinión
            self.invalidar_cache_opiniones()
            
            self.logger.info(f"Opinión creada exitosamente. ID: {cursor.lastrowid}")
            
            return {
                'success': True,
                'message': 'Opinión guardada correctamente',
                'id': cursor.lastrowid
            }
            
        except mysql.connector.Error as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Error MySQL al crear opinión: {e}")
            return {'success': False, 'message': f'Error de base de datos: {str(e)}'}
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Error al crear opinión: {e}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def obtener_opiniones_publicas(self, limit: int = 20) -> Dict[str, Any]:
        """Obtiene las opiniones públicas con datos de usuario y producto usando JOINs"""
        # Verificar cache
        cache_key = f"opiniones_publicas_{limit}"
        current_time = time.time()
        
        if (cache_key in opiniones_cache and 
            current_time - opiniones_cache[cache_key]['timestamp'] < OPINIONES_CACHE_DURATION):
            return opiniones_cache[cache_key]['data']
        
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Consulta sin alias - nombres completos de tabla
            query = """
            SELECT 
                opiniones.id_opiniones,
                opiniones.calificacion,
                opiniones.descripcion_opinion,
                opiniones.fecha_creacion,
                usuario.nombres_usuario,
                usuario.email_usuario,
                producto.nombre_producto,
                producto.precio_producto,
                producto.img_producto
            FROM opiniones
            INNER JOIN usuario ON opiniones.id_usuario = usuario.id_usuario
            INNER JOIN producto ON opiniones.id_producto = producto.id_producto
            WHERE opiniones.publicar = 1
            ORDER BY opiniones.fecha_creacion DESC
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            opiniones = cursor.fetchall()
            
            result = {
                'success': True,
                'opiniones': opiniones,
                'total': len(opiniones)
            }
            
            # Guardar en cache
            opiniones_cache[cache_key] = {
                'data': result,
                'timestamp': current_time
            }
            
            return result
            
        except mysql.connector.Error as e:
            self.logger.error(f"Error MySQL al obtener opiniones: {e}")
            return {'success': False, 'message': f'Error de base de datos: {str(e)}'}
        except Exception as e:
            self.logger.error(f"Error al obtener opiniones: {e}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def obtener_opiniones_por_producto(self, id_producto: int, limit: int = 10) -> Dict[str, Any]:
        """Obtiene opiniones de un producto específico"""
        # Verificar cache
        cache_key = f"opiniones_producto_{id_producto}_{limit}"
        current_time = time.time()
        
        if (cache_key in opiniones_cache and 
            current_time - opiniones_cache[cache_key]['timestamp'] < OPINIONES_CACHE_DURATION):
            return opiniones_cache[cache_key]['data']
        
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Sin alias - nombres completos
            query = """
            SELECT 
                opiniones.id_opiniones,
                opiniones.calificacion,
                opiniones.descripcion_opinion,
                opiniones.fecha_creacion,
                usuario.nombres_usuario,
                usuario.apellidos_usuario,
                producto.nombre_producto
            FROM opiniones
            INNER JOIN usuario ON opiniones.id_usuario = usuario.id_usuario
            INNER JOIN producto ON opiniones.id_producto = producto.id_producto
            WHERE opiniones.id_producto = %s AND opiniones.publicar = 1
            ORDER BY opiniones.fecha_creacion DESC
            LIMIT %s
            """
            
            cursor.execute(query, (id_producto, limit))
            opiniones = cursor.fetchall()
            
            result = {
                'success': True,
                'opiniones': opiniones,
                'total': len(opiniones)
            }
            
            # Guardar en cache
            opiniones_cache[cache_key] = {
                'data': result,
                'timestamp': current_time
            }
            
            return result
            
        except mysql.connector.Error as e:
            self.logger.error(f"Error MySQL al obtener opiniones por producto: {e}")
            return {'success': False, 'message': f'Error de base de datos: {str(e)}'}
        except Exception as e:
            self.logger.error(f"Error al obtener opiniones por producto: {e}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def obtener_estadisticas_opiniones(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas de las opiniones con JOINs"""
        # Verificar cache
        current_time = time.time()
        
        if (estadisticas_cache['data'] is not None and 
            current_time - estadisticas_cache['timestamp'] < ESTADISTICAS_CACHE_DURATION):
            return estadisticas_cache['data']
        
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Estadísticas generales - sin alias
            stats_query = """
            SELECT 
                COUNT(*) as total_opiniones,
                AVG(opiniones.calificacion) as promedio_calificacion,
                COUNT(CASE WHEN opiniones.publicar = 1 THEN 1 END) as opiniones_publicas,
                COUNT(DISTINCT opiniones.id_usuario) as usuarios_que_opinaron,
                COUNT(DISTINCT opiniones.id_producto) as productos_con_opinion
            FROM opiniones
            """
            
            cursor.execute(stats_query)
            stats = cursor.fetchone()
            
            # Distribución por calificación - sin alias
            dist_query = """
            SELECT 
                opiniones.calificacion,
                COUNT(*) as cantidad
            FROM opiniones
            GROUP BY opiniones.calificacion
            ORDER BY opiniones.calificacion DESC
            """
            
            cursor.execute(dist_query)
            distribucion = cursor.fetchall()
            
            # Productos mejor calificados - sin alias
            top_productos_query = """
            SELECT 
                producto.nombre_producto,
                producto.precio_producto,
                AVG(opiniones.calificacion) as promedio_calificacion,
                COUNT(opiniones.id_opiniones) as total_opiniones
            FROM opiniones
            INNER JOIN producto ON opiniones.id_producto = producto.id_producto
            WHERE opiniones.publicar = 1
            GROUP BY opiniones.id_producto, producto.nombre_producto, producto.precio_producto
            HAVING COUNT(opiniones.id_opiniones) >= 2
            ORDER BY promedio_calificacion DESC, total_opiniones DESC
            LIMIT 5
            """
            
            cursor.execute(top_productos_query)
            top_productos = cursor.fetchall()
            
            result = {
                'success': True,
                'estadisticas': stats,
                'distribucion': distribucion,
                'top_productos': top_productos
            }
            
            # Guardar en cache
            estadisticas_cache['data'] = result
            estadisticas_cache['timestamp'] = current_time
            
            return result
            
        except mysql.connector.Error as e:
            self.logger.error(f"Error MySQL al obtener estadísticas: {e}")
            return {'success': False, 'message': f'Error de base de datos: {str(e)}'}
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas: {e}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def obtener_productos_disponibles(self) -> Dict[str, Any]:
        """Obtiene la lista de productos disponibles con numeración del 1 al 15"""
        # Verificar cache
        current_time = time.time()
        
        if (productos_cache['data'] is not None and 
            current_time - productos_cache['timestamp'] < PRODUCTOS_CACHE_DURATION):
            return productos_cache['data']
        
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Usar ROW_NUMBER() para numerar desde la consulta ordenando por id_producto
            query = """
            SELECT 
                ROW_NUMBER() OVER (ORDER BY id_producto) as numero_display,
                id_producto,
                nombre_producto,
                precio_producto,
                cantidad_disponible,
                img_producto
            FROM producto
            WHERE cantidad_disponible > 0
            ORDER BY id_producto
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            result = {
                'success': True,
                'productos': productos
            }
            
            # Guardar en cache
            productos_cache['data'] = result
            productos_cache['timestamp'] = current_time
            
            return result
            
        except mysql.connector.Error as e:
            self.logger.error(f"Error MySQL al obtener productos: {e}")
            return {'success': False, 'message': f'Error de base de datos: {str(e)}'}
        except Exception as e:
            self.logger.error(f"Error al obtener productos: {e}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# Crear instancia del servicio
opiniones_service = OpinionesService()

# Función para configurar filtros personalizados de Jinja2
def setup_jinja_filters(app):
    """Configura filtros personalizados para Jinja2"""
    
    @app.template_filter('enumerate_from_one')
    def enumerate_from_one(iterable):
        """Enumera desde 1 en lugar de 0"""
        return enumerate(iterable, 1)
    
    return app

# Rutas
@opiniones_bp.route("/Opiniones")
def mostrar_opiniones():
    """Renderiza la página de opiniones con versión pública o privada"""
    try:
        es_privado = request.args.get('privado') == 'true'

        # Obtener productos (ahora con cache)
        productos_result = opiniones_service.obtener_productos_disponibles()
        productos = productos_result['productos'] if productos_result['success'] else []

        opiniones_result = opiniones_service.obtener_opiniones_publicas()
        opiniones = opiniones_result['opiniones'] if opiniones_result['success'] else []

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT nombres_usuario FROM usuario WHERE id_usuario = %s", (session.get('user_id'),))
        nombre = cursor.fetchone()

        return render_template(
            "/opiniones/Opiniones.html",
            productos=productos,
            opiniones=opiniones,
            es_privado=es_privado,  # Puedes usar esto en el HTML si quieres
            nombre=nombre
        )
        
    except Exception as e:
        logger.error(f"Error al cargar página de opiniones: {e}")
        return render_template("/opiniones/Opiniones.html", productos=[])

@opiniones_bp.route("/api/opiniones/crear", methods=['POST'])
def crear_opinion():
    """API endpoint para crear una nueva opinión"""
    try:
        # Verificar que el usuario esté logueado
        if not session.get('logged_in'):
            return jsonify({'success': False, 'message': 'Debes iniciar sesión para opinar'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Datos no válidos'}), 400
        
        # Agregar el ID del usuario desde la sesión
        data['id_usuario'] = session.get('user_id')
        
        result = opiniones_service.crear_opinion(data)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error en endpoint crear_opinion: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

@opiniones_bp.route("/api/opiniones/publicas", methods=['GET'])
def obtener_opiniones_publicas():
    """API endpoint para obtener opiniones públicas"""
    try:
        limit = request.args.get('limit', 20, type=int)
        result = opiniones_service.obtener_opiniones_publicas(limit)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en endpoint obtener_opiniones_publicas: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

@opiniones_bp.route("/api/opiniones/producto/<int:id_producto>", methods=['GET'])
def obtener_opiniones_producto(id_producto):
    """API endpoint para obtener opiniones de un producto específico"""
    try:
        limit = request.args.get('limit', 10, type=int)
        result = opiniones_service.obtener_opiniones_por_producto(id_producto, limit)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en endpoint obtener_opiniones_producto: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

@opiniones_bp.route("/api/opiniones/estadisticas", methods=['GET'])
def obtener_estadisticas():
    """API endpoint para obtener estadísticas de opiniones"""
    try:
        result = opiniones_service.obtener_estadisticas_opiniones()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en endpoint obtener_estadisticas: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

@opiniones_bp.route("/api/productos/disponibles", methods=['GET'])
def obtener_productos_disponibles():
    """API endpoint para obtener productos disponibles"""
    try:
        result = opiniones_service.obtener_productos_disponibles()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en endpoint obtener_productos_disponibles: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

# Nuevo endpoint para obtener datos del usuario actual
@opiniones_bp.route("/api/usuario/actual", methods=['GET'])
def obtener_usuario_actual():
    """API endpoint para obtener datos del usuario logueado"""
    try:
        if not session.get('logged_in'):
            return jsonify({'success': False, 'logged_in': False}), 401
        
        return jsonify({
            'success': True,
            'logged_in': True,
            'user': {
                'id': session.get('user_id'),
                'name': session.get('user_name'),
                'email': session.get('user_email')
            }
        })
        
    except Exception as e:
        logger.error(f"Error en endpoint obtener_usuario_actual: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

# Función para registrar el blueprint en tu app principal
def register_opiniones_routes(app):
    """Registra las rutas de opiniones en la aplicación Flask"""
    app.register_blueprint(opiniones_bp)
    logger.info("Rutas de opiniones registradas exitosamente")