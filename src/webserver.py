from flask import Flask, render_template, g, request, session, jsonify, redirect, url_for, flash, make_response
from flask_mail import Mail
from flask_compress import Compress
from flask_caching import Cache
from datetime import timedelta
import os
from dotenv import load_dotenv
from routes.auth import login_required

def lazy_import_routes():
    routes = {}

    def get_blueprint(name):
        if name not in routes:
            if name == 'comprobante':
                from routes.comprobante import comprobante_bp
                routes[name] = comprobante_bp
            elif name == 'tus_comprobantes':
                from routes.tus_comprobantes import tus_comprobantes_bp
                routes[name] = tus_comprobantes_bp
            elif name == 'metodo_pago':
                from routes.metodo_pago import metodo_pago_bp
                routes[name] = metodo_pago_bp
            elif name == 'auth':
                from routes.auth import auth_bp
                routes[name] = auth_bp
            elif name == 'carrito':
                from routes.carrito_de_compras import carrito_bp
                routes[name] = carrito_bp
            elif name == 'catalogo':
                from routes.catalogo import catalogo_bp
                routes[name] = catalogo_bp
            elif name == 'domiciliarios':
                from routes.domiciliario import domiciliarios_bp
                routes[name] = domiciliarios_bp
            elif name == 'opiniones':
                from routes.opiniones import opiniones_bp
                routes[name] = opiniones_bp
            elif name == 'porcentaje_ventas':
                from routes.porcentaje_ventas import porcentaje_ventas_bp
                routes[name] = porcentaje_ventas_bp
            elif name == 'admin':
                from routes.admin import admin_bp

                @admin_bp.route('/ventas')
                @login_required
                def panel_ventas():
                    return render_template('admin/ventas.html')

                routes[name] = admin_bp
            elif name == 'alerta_stock':
                from routes.alerta_stock import alerta_stock_bp
                routes[name] = alerta_stock_bp

            elif name == 'gestion_productos':
                from routes.gestion_productos import gestion_productos_bp
                routes[name] = gestion_productos_bp

            elif name == 'gestion_usuario':
                from routes.gestion_usuario import gestion_usuario_bp
                routes[name] = gestion_usuario_bp
        return routes.get(name)

    return get_blueprint

# ------------------------
# Cargar variables de entorno
# ------------------------

load_dotenv()

# ------------------------
# Crear app
# ------------------------

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    configure_app(app)
    init_extensions(app)
    register_blueprints(app)
    setup_hooks(app)

    return app

# ------------------------
# Configuración de la app
# ------------------------

def configure_app(app):
    app.secret_key = os.environ.get('SECRET_KEY', '')

    app.config.update(
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=24),

        CACHE_TYPE='simple',
        CACHE_DEFAULT_TIMEOUT=300,

        COMPRESS_MIMETYPES=[
            'text/html', 'text/css', 'text/javascript',
            'application/javascript', 'application/json',
            'text/xml', 'application/xml'
        ],
        COMPRESS_LEVEL=6,
        COMPRESS_MIN_SIZE=500,

        SEND_FILE_MAX_AGE_DEFAULT=31536000,

        MAIL_SERVER=os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
        MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER')
    )

# ------------------------
# Inicializar extensiones
# ------------------------

def init_extensions(app):
    Compress(app)

    cache = Cache(app)
    app.cache = cache

    mail = Mail(app)
    app.mail = mail

# ------------------------
# Registrar blueprints
# ------------------------

def register_blueprints(app):
    from routes.auth import auth_bp, init_auth_system
    app.register_blueprint(auth_bp)
    init_auth_system()

    blueprint_loader = lazy_import_routes()

    blueprints = [
        'comprobante', 'tus_comprobantes', 'metodo_pago',
        'carrito', 'catalogo', 'domiciliarios', 'opiniones',
        'porcentaje_ventas', 'admin', 'alerta_stock', 'gestion_productos',
        'gestion_usuario'
    ]

    for bp_name in blueprints:
        try:
            bp = blueprint_loader(bp_name)
            if bp:
                app.register_blueprint(bp)
        except ImportError as e:
            print(f"Error cargando blueprint {bp_name}: {e}")

    try:
        from routes.profile_service import ProfileService, create_profile_routes
        profile_service = ProfileService()
        profile_routes = create_profile_routes(profile_service)
        app.register_blueprint(profile_routes)
    except ImportError:
        print("Profile service no disponible")

# ------------------------
# Hooks de Flask
# ------------------------

def setup_hooks(app):
    def run_initial_setup():
        try:
            from routes.auth import cleanup_expired_tokens
            cleanup_expired_tokens()
        except Exception as e:
            print(f"Error en setup inicial: {e}")

    run_initial_setup()

    @app.before_request
    def before_request():
        if request.endpoint == 'home' and request.args.get('logout_success'):
            session.clear()
            g.current_user = None
            g.is_logged_in = False
        elif request.endpoint and not request.endpoint.startswith('static'):
            try:
                from routes.auth import get_current_user, is_logged_in
                g.current_user = get_current_user()
                g.is_logged_in = is_logged_in()
            except Exception:
                g.current_user = None
                g.is_logged_in = False

    @app.after_request
    def after_request(response):
        if request.endpoint == 'static':
            response.headers['Cache-Control'] = 'public, max-age=31536000'
            response.headers['Expires'] = 'Thu, 31 Dec 2025 23:59:59 GMT'
        elif request.endpoint in ['home'] and not getattr(g, 'is_logged_in', False):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        elif request.endpoint in ['home'] or request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    @app.context_processor
    def inject_user():
        return {
            'current_user': getattr(g, 'current_user', None),
            'is_logged_in': getattr(g, 'is_logged_in', False)
        }

# ------------------------
# Instancia de la app
# ------------------------

app = create_app()

# ------------------------
# Rutas principales
# ------------------------

@app.route("/")
@app.route("/Home")
def home():
    logout_success = request.args.get('logout_success', False)

    if logout_success:
        session.clear()
        g.current_user = None
        g.is_logged_in = False
        is_authenticated = False
        current_user = None
    else:
        is_authenticated = getattr(g, 'is_logged_in', False)
        current_user = getattr(g, 'current_user', None)

    response = make_response(render_template('Home/Home.html',
                                             show_user_menu=is_authenticated,
                                             current_user=current_user,
                                             logout_success=logout_success))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/logout-to-home")
def logout_to_home():
    try:
        session.clear()
        g.current_user = None
        g.is_logged_in = False
        return redirect(url_for('home', logout_success=True))
    except Exception as e:
        print(f"Error en logout: {e}")
        return redirect(url_for('home', logout_success=True))

@app.route("/Nosotros")
@app.cache.cached(timeout=600)
def sobre_nosotros():
    return render_template('nosotros/nosotros.html')

@app.route("/Catalogo-Empanadas")
@login_required
def catalogo_empanadas():
    return render_template('catalogo_empanadas/catalo_empanadas.html')

@app.route('/static/<path:filename>')
def custom_static(filename):
    from flask import send_from_directory
    response = send_from_directory('static', filename)

    if filename.endswith(('.css', '.js', '.jpg', '.png', '.webp', '.ico')):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        response.headers['Expires'] = 'Thu, 31 Dec 2025 23:59:59 GMT'

    return response

# ------------------------
# Ejecutar app
# ------------------------

if __name__ == "__main__":
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, threaded=True, host="0.0.0.0", port=5000)
