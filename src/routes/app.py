from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime
from functools import wraps
import pandas as pd
from werkzeug.security import check_password_hash
from db.conexion import get_db_connection

app = Flask(__name__)
app.secret_key = ''  # Cambiar por algo más seguro en producción

# Decorador para verificar login del administrador
def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login_admin'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM administrador WHERE email_administrador = %s", (email,))
            admin = cursor.fetchone()

            if admin and check_password_hash(admin['contraseña'], password):
                session['admin_logged_in'] = True
                session['admin_email'] = email
                return redirect(url_for('dashboard'))
            else:
                return render_template('login_admin.html', error="Credenciales incorrectas")
        except Exception as e:
            return str(e)
        finally:
            if 'conn' in locals():
                conn.close()
    return render_template('login_admin.html')

@app.route('/logout_admin')
def logout_admin():
    session.clear()
    return redirect(url_for('login_admin'))

@app.route('/dashboard')
@login_required_admin
def dashboard():
    return render_template('admin_interfaz/admininterfaz.html')

@app.route('/api/ventas')
@login_required_admin
def get_ventas():
    try:
        conn = get_db_connection()
        fecha_inicio = request.args.get('inicio', datetime.now().strftime('%Y-%m-%d'))
        fecha_fin = request.args.get('fin', datetime.now().strftime('%Y-%m-%d'))

        hoy = datetime.now().date()
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

        if fecha_inicio_dt > hoy or fecha_fin_dt > hoy:
            return jsonify({'error': 'No se pueden consultar fechas futuras'}), 400

        query = """
        SELECT * FROM vista_ventas
        WHERE DATE(fecha_compra) BETWEEN %s AND %s
        ORDER BY fecha_compra DESC, hora DESC
        """

        df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_fin])
        return jsonify(df.to_dict('records'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/estadisticas')
@login_required_admin
def get_estadisticas():
    try:
        conn = get_db_connection()
        mes = request.args.get('mes', datetime.now().month)
        anio = request.args.get('año', datetime.now().year)

        query = """
        SELECT 
            SUM(df.subtotal) as ventas_mes,
            SUM(df.cantidad_producto) as productos_vendidos,
            COUNT(DISTINCT f.id_usuario) as total_clientes,
            COUNT(DISTINCT f.id_factura) as total_ventas,
            AVG(df.subtotal) as promedio_venta
        FROM facturacion f
        JOIN detalle_facturacion df ON f.id_factura = df.id_factura
        WHERE MONTH(f.fecha_compra) = %s AND YEAR(f.fecha_compra) = %s
        AND f.estado = 'pagado'
        """

        df = pd.read_sql(query, conn, params=[mes, anio])

        query_stock = """
        SELECT nombre_producto, stock
        FROM producto
        WHERE stock < 20
        ORDER BY stock ASC
        """
        df_stock = pd.read_sql(query_stock, conn)

        result = df.iloc[0].to_dict()
        result['productos_bajo_stock'] = df_stock.to_dict('records')

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/productos/bajo-stock')
@login_required_admin
def get_productos_bajo_stock():
    try:
        conn = get_db_connection()
        query = """
        SELECT id_producto, nombre_producto, stock, precio_producto
        FROM producto
        WHERE stock < 20
        ORDER BY stock ASC
        """

        df = pd.read_sql(query, conn)
        return jsonify(df.to_dict('records'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.template_filter('fecha_formato')
def fecha_formato(fecha):
    if isinstance(fecha, str):
        fecha = datetime.strptime(fecha, '%Y-%m-%d')
    return fecha.strftime('%d/%m/%Y')
    