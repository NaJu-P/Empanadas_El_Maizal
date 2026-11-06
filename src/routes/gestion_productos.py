from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, Blueprint, current_app
from db.conexion import get_db_connection
import mysql.connector
from datetime import datetime
from routes.admin import admin_login_required
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

gestion_productos_bp = Blueprint('gestion_productos', __name__)

class ProductoService:
    @staticmethod
    def obtener_todos_productos():
        """Obtiene todos los productos de la base de datos"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    p.id_producto as id,
                    p.nombre_producto as name,
                    p.img_producto as image,
                    p.cantidad_disponible as quantity,
                    p.precio_producto as price,
                    tp.descripcion_producto as description
                FROM producto p
                JOIN tipo_producto tp ON p.id_tipo_producto = tp.id_tipo_producto
                ORDER BY p.id_producto
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return productos
            
        except mysql.connector.Error as e:
            print(f"Error al obtener productos: {e}")
            return []
    
    @staticmethod
    def obtener_producto_por_id(producto_id):
        """Obtiene un producto específico por su ID"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    p.id_producto as id,
                    p.nombre_producto as name,
                    p.img_producto as image,
                    p.cantidad_disponible as quantity,
                    p.precio_producto as price,
                    tp.descripcion_producto as description
                FROM producto p
                JOIN tipo_producto tp ON p.id_tipo_producto = tp.id_tipo_producto
                WHERE p.id_producto = %s
            """
            
            cursor.execute(query, (producto_id,))
            producto = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return producto
            
        except mysql.connector.Error as e:
            print(f"Error al obtener producto: {e}")
            return None
    
    @staticmethod
    def actualizar_cantidad_producto(producto_id, nueva_cantidad):
        """Actualiza la cantidad de un producto"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            query = "UPDATE producto SET cantidad_disponible = %s WHERE id_producto = %s"
            cursor.execute(query, (nueva_cantidad, producto_id))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"Error al actualizar cantidad: {e}")
            return False
    
    @staticmethod
    def crear_producto(nombre, imagen, cantidad_inicial, precio, descripcion):
        """Crea un nuevo producto"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Primero crear el tipo de producto
            cursor.execute(
                "INSERT INTO tipo_producto (descripcion_producto) VALUES (%s)",
                (descripcion,)
            )
            tipo_producto_id = cursor.lastrowid
            
            # Luego crear el producto
            cursor.execute(
                """INSERT INTO producto 
                   (nombre_producto, cantidad_disponible, id_tipo_producto, precio_producto, img_producto) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (nombre, cantidad_inicial, tipo_producto_id, precio, imagen)
            )
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"Error al crear producto: {e}")
            return False
    
    @staticmethod
    def eliminar_producto(producto_id):
        """Elimina un producto y su tipo asociado"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Obtener el id_tipo_producto antes de eliminar
            cursor.execute("SELECT id_tipo_producto FROM producto WHERE id_producto = %s", (producto_id,))
            result = cursor.fetchone()
            
            if result:
                tipo_producto_id = result[0]
                
                # Eliminar el producto (esto eliminará automáticamente por CASCADE)
                cursor.execute("DELETE FROM producto WHERE id_producto = %s", (producto_id,))
                
                # Eliminar el tipo de producto
                cursor.execute("DELETE FROM tipo_producto WHERE id_tipo_producto = %s", (tipo_producto_id,))
                
                connection.commit()
            
            cursor.close()
            connection.close()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"Error al eliminar producto: {e}")
            return False

# Rutas de la aplicación
@gestion_productos_bp.route('/admin/gestion-productos')
@admin_login_required
def index():
    """Página principal con la gestión de productos"""
    # Cargar productos desde la base de datos
    productos = ProductoService.obtener_todos_productos()
    return render_template('/aumento_productos/aumento_productos.html.j2', productos=productos)

@gestion_productos_bp.route('/api/productos', methods=['GET'])
@admin_login_required
def obtener_productos():
    """API para obtener todos los productos"""
    productos = ProductoService.obtener_todos_productos()
    return jsonify(productos)

@gestion_productos_bp.route('/api/productos/<int:producto_id>', methods=['GET'])
@admin_login_required
def obtener_producto(producto_id):
    """API para obtener un producto específico"""
    producto = ProductoService.obtener_producto_por_id(producto_id)
    if producto:
        return jsonify(producto)
    return jsonify({'error': 'Producto no encontrado'}), 404

@gestion_productos_bp.route('/api/productos/<int:producto_id>/cantidad', methods=['PUT'])
@admin_login_required
def actualizar_cantidad(producto_id):
    """API para actualizar la cantidad de un producto"""
    data = request.get_json()
    
    if not data or 'cantidad' not in data:
        return jsonify({'error': 'Cantidad requerida'}), 400
    
    nueva_cantidad = data['cantidad']
    
    if nueva_cantidad < 0:
        return jsonify({'error': 'La cantidad no puede ser negativa'}), 400
    
    if ProductoService.actualizar_cantidad_producto(producto_id, nueva_cantidad):
        return jsonify({'message': 'Cantidad actualizada exitosamente'})
    
    return jsonify({'error': 'Error al actualizar cantidad'}), 500

@gestion_productos_bp.route('/api/productos', methods=['POST'])
@admin_login_required
def crear_producto():
    """API para crear un nuevo producto"""
    data = request.get_json()
    
    campos_requeridos = ['nombre', 'imagen', 'cantidad', 'precio', 'descripcion']
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({'error': f'Campo {campo} requerido'}), 400
    
    if ProductoService.crear_producto(
        data['nombre'], 
        data['imagen'], 
        data['cantidad'], 
        data['precio'], 
        data['descripcion']
    ):
        return jsonify({'message': 'Producto creado exitosamente'})
    
    return jsonify({'error': 'Error al crear producto'}), 500

@gestion_productos_bp.route('/api/productos/<int:producto_id>', methods=['DELETE'])
@admin_login_required
def eliminar_producto(producto_id):
    """API para eliminar un producto"""
    if ProductoService.eliminar_producto(producto_id):
        return jsonify({'message': 'Producto eliminado exitosamente'})
    
    return jsonify({'error': 'Error al eliminar producto'}), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Agregar esta nueva ruta a tu Blueprint
@gestion_productos_bp.route('/api/upload-image', methods=['POST'])
@admin_login_required
def upload_image():
    """API para subir imágenes a la carpeta static/img"""
    try:
        # Verificar si se envió un archivo
        if 'productImageFile' not in request.files:
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        file = request.files['productImageFile']
        
        # Verificar que el archivo tenga un nombre
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        # Verificar que el archivo sea una imagen válida
        if file and allowed_file(file.filename):
            # Hacer el nombre del archivo seguro
            filename = secure_filename(file.filename)
            
            # Crear la carpeta si no existe
            upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
            os.makedirs(upload_path, exist_ok=True)
            
            # Guardar el archivo
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            
            return jsonify({
                'message': 'Imagen subida exitosamente',
                'filename': filename
            })
        
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
    except Exception as e:
        print(f"Error al subir imagen: {e}")
        return jsonify({'error': 'Error al subir la imagen'}), 500