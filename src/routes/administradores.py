administradores_bp = Blueprint('administradores', __name__)
from flask import Blueprint, render_template

gestion_administradores_bp = Blueprint('gestion_administradores', __name__)

@gestion_administradores_bp.route('/gestion_administradores')
def gestion_administradores():
    administradores = [
        {'id': 1, 'nombre': 'Juan Pérez', 'email': 'juan@maizal.com', 'permisos': 'Total'},
        {'id': 2, 'nombre': 'Ana Gómez', 'email': 'ana@maizal.com', 'permisos': 'Limitado'},
    ]
    return render_template('admin_interfaz/gestion_administradores.html', administradores=administradores)
