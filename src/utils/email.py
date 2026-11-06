# utils/email.py
from flask import current_app, url_for
from flask_mail import Message, Mail

def get_mail_instance():
    """Obtiene la instancia de Mail desde la aplicación actual"""
    return current_app.extensions.get('mail')

def send_reset_email(recipient_email, token, sender_email=None):
    """
    Envía email de restablecimiento de contraseña
    
    Args:
        email (str): Email del usuario
        token (str): Token de restablecimiento
    
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    """Enviar email de restablecimiento usando el email del usuario en sesión"""
    from flask import current_app
    
    # Si no se proporciona sender_email, usar el de la sesión
    if sender_email is None:
        from flask import session
        sender_email = session.get('user_email')
    
    # Si aún no hay sender_email, usar el configurado por defecto
    if sender_email is None:
        sender_email = current_app.config.get('MAIL_USERNAME')
    
    # Configurar temporalmente el MAIL_USERNAME
    original_username = current_app.config.get('MAIL_USERNAME')
    current_app.config['MAIL_USERNAME'] = sender_email

    try:
        mail = get_mail_instance()
        
        # Crear el enlace de restablecimiento
        reset_url = url_for('auth.cambiar_contrasena', token=token, _external=True)
        
        # Crear el mensaje
        msg = Message(
            subject='Restablecimiento de Contraseña - EMPANADAS EL MAIZAL',
            recipients=[recipient_email]  # ← Cambiar aquí: era 'email'
        )
        
        # Contenido HTML del email
        msg.html = f'''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Restablecimiento de Contraseña</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #ff6b35, #f7931e);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: bold;
                }}
                .content {{
                    padding: 30px 20px;
                    line-height: 1.6;
                    color: #333333;
                }}
                .content h2 {{
                    color: #ff6b35;
                    margin-bottom: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 15px 30px;
                    background: linear-gradient(135deg, #ff6b35, #f7931e);
                    color: white !important;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0;
                    transition: transform 0.3s ease;
                }}
                .button:hover {{
                    transform: translateY(-2px);
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #856404;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #666666;
                    border-top: 1px solid #e9ecef;
                }}
                .logo {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #ff6b35;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🥟 EMPANADAS EL MAIZAL</h1>
                </div>
                <div class="content">
                    <h2>Restablecimiento de Contraseña</h2>
                    <p>¡Hola!</p>
                    <p>Recibiste este correo porque solicitaste restablecer tu contraseña en <strong>EMPANADAS EL MAIZAL</strong>.</p>
                    <p>Para crear una nueva contraseña segura, haz clic en el siguiente botón:</p>
                    
                    <div style="text-align: center;">
                        <p>Tu token de seguridad: { token }</p>
                        <a href="{reset_url}" class="button">🔑 Restablecer Mi Contraseña</a>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Importante:</strong>
                        <ul>
                            <li>Este enlace expirará en <strong>1 hora</strong></li>
                            <li>Solo puedes usarlo una vez</li>
                            <li>Si no solicitaste este cambio, ignora este correo</li>
                        </ul>
                    </div>
                    
                    <p>Si el botón no funciona, copia y pega el siguiente enlace en tu navegador:</p>
                    <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace;">
                        {reset_url}
                    </p>
                    
                    <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                    <p>¡Gracias por confiar en nosotros! 🥟</p>
                </div>
                <div class="footer">
                    <div class="logo">EMPANADAS EL MAIZAL</div>
                    <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                    <p>© 2024 EMPANADAS EL MAIZAL - Todos los derechos reservados</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        # Contenido de texto plano (fallback)
        msg.body = f'''
        EMPANADAS EL MAIZAL - Restablecimiento de Contraseña
        
        ¡Hola!
        
        Recibiste este correo porque solicitaste restablecer tu contraseña.
        
        Para crear una nueva contraseña, copia y pega el siguiente enlace en tu navegador:
        {reset_url}
        
        IMPORTANTE:
        - Este enlace expirará en 1 hora
        - Solo puedes usarlo una vez
        - Si no solicitaste este cambio, ignora este correo
        
        Si tienes alguna pregunta, no dudes en contactarnos.
        
        ¡Gracias por confiar en nosotros!
        
        EMPANADAS EL MAIZAL
        © 2025 - Todos los derechos reservados
        '''
        
        # Enviar el correo
        mail.send(msg)
        print(f"Email de restablecimiento enviado exitosamente a: {recipient_email}")
        return True
        
    except Exception as e:
        print(f"Error enviando email de restablecimiento a {recipient_email}: {str(e)}")
        return False

def send_password_change_confirmation(recipient_email, sender_email=None):
    """
    Envía confirmación de cambio de contraseña exitoso
    
    Args:
        email (str): Email del usuario
    
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    from flask import current_app, session
    
    if sender_email is None:
        sender_email = session.get('user_email')
    
    if sender_email is None:
        sender_email = current_app.config.get('MAIL_USERNAME')
    
    original_username = current_app.config.get('MAIL_USERNAME')
    current_app.config['MAIL_USERNAME'] = sender_email

    try:
        mail = get_mail_instance()
        
        msg = Message(
            subject='Contraseña Actualizada - EMPANADAS EL MAIZAL',
            recipients=[recipient_email]  # ← Cambiar aquí: era 'email'
        )
        
        # Contenido HTML del email
        msg.html = '''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Contraseña Actualizada</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                .header {
                    background: linear-gradient(135deg, #28a745, #20c997);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }
                .header h1 {
                    margin: 0;
                    font-size: 24px;
                    font-weight: bold;
                }
                .content {
                    padding: 30px 20px;
                    line-height: 1.6;
                    color: #333333;
                }
                .content h2 {
                    color: #28a745;
                    margin-bottom: 20px;
                }
                .success-icon {
                    font-size: 48px;
                    text-align: center;
                    margin: 20px 0;
                }
                .security-tips {
                    background-color: #d1ecf1;
                    border: 1px solid #bee5eb;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #0c5460;
                }
                .footer {
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #666666;
                    border-top: 1px solid #e9ecef;
                }
                .logo {
                    font-size: 18px;
                    font-weight: bold;
                    color: #ff6b35;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🥟 EMPANADAS EL MAIZAL</h1>
                </div>
                <div class="content">
                    <div class="success-icon">✅</div>
                    <h2>¡Contraseña Actualizada Exitosamente!</h2>
                    <p>¡Hola!</p>
                    <p>Te confirmamos que tu contraseña ha sido <strong>cambiada exitosamente</strong> en tu cuenta de EMPANADAS EL MAIZAL.</p>
                    
                    <div class="security-tips">
                        <strong>🔒 Consejos de Seguridad:</strong>
                        <ul>
                            <li>Mantén tu contraseña segura y no la compartas</li>
                            <li>Usa una contraseña única para cada servicio</li>
                            <li>Si no realizaste este cambio, contacta con nosotros inmediatamente</li>
                        </ul>
                    </div>
                    
                    <p>Si <strong>NO</strong> realizaste este cambio o tienes alguna sospecha de actividad no autorizada, por favor:</p>
                    <ul>
                        <li>Contacta con nuestro equipo de soporte inmediatamente</li>
                        <li>Revisa la actividad reciente de tu cuenta</li>
                        <li>Considera cambiar las contraseñas de otras cuentas si usabas la misma</li>
                    </ul>
                    
                    <p>¡Gracias por mantener tu cuenta segura! 🥟</p>
                </div>
                <div class="footer">
                    <div class="logo">EMPANADAS EL MAIZAL</div>
                    <p>Este es un correo automático de seguridad.</p>
                    <p>© 2024 EMPANADAS EL MAIZAL - Todos los derechos reservados</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        # Contenido de texto plano (fallback)
        msg.body = '''
        EMPANADAS EL MAIZAL - Contraseña Actualizada
        
        ¡Hola!
        
        Te confirmamos que tu contraseña ha sido cambiada exitosamente.
        
        CONSEJOS DE SEGURIDAD:
        - Mantén tu contraseña segura y no la compartas
        - Usa una contraseña única para cada servicio
        - Si no realizaste este cambio, contacta con nosotros inmediatamente
        
        Si NO realizaste este cambio:
        - Contacta con nuestro equipo de soporte inmediatamente
        - Revisa la actividad reciente de tu cuenta
        - Considera cambiar las contraseñas de otras cuentas si usabas la misma
        
        ¡Gracias por mantener tu cuenta segura!
        
        EMPANADAS EL MAIZAL
        © 2024 - Todos los derechos reservados
        '''
        
        # Enviar el correo
        mail.send(msg)
        print(f"Email de confirmación enviado exitosamente a: {recipient_email}")
        return True
        
    except Exception as e:
        print(f"Error enviando confirmación a {recipient_email}: {str(e)}")
        return False
    
    finally:
        current_app.config['MAIL_USERNAME'] = original_username

def send_welcome_email(email, nombre):
    """
    Envía email de bienvenida a usuarios nuevos
    
    Args:
        email (str): Email del usuario
        nombre (str): Nombre del usuario
    
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    try:
        mail = get_mail_instance()
        
        msg = Message(
            subject='¡Bienvenido a EMPANADAS EL MAIZAL! 🥟',
            recipients=[email]
        )
        
        msg.html = f'''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>¡Bienvenido!</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #ff6b35, #f7931e);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 30px 20px;
                    line-height: 1.6;
                    color: #333333;
                }}
                .welcome-icon {{
                    font-size: 48px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #666666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🥟 EMPANADAS EL MAIZAL</h1>
                </div>
                <div class="content">
                    <div class="welcome-icon">🎉</div>
                    <h2>¡Bienvenido, {nombre}!</h2>
                    <p>¡Gracias por unirte a la familia de EMPANADAS EL MAIZAL!</p>
                    <p>Estamos emocionados de tenerte como parte de nuestra comunidad de amantes de las empanadas.</p>
                    <p>Ya puedes disfrutar de:</p>
                    <ul>
                        <li>🥟 Nuestro delicioso catálogo de empanadas</li>
                        <li>🛒 Proceso de compra rápido y seguro</li>
                        <li>📋 Seguimiento de tus pedidos</li>
                        <li>⭐ Ofertas exclusivas para miembros</li>
                    </ul>
                    <p>¡Esperamos que disfrutes de nuestras empanadas!</p>
                </div>
                <div class="footer">
                    <p>© 2024 EMPANADAS EL MAIZAL - Todos los derechos reservados</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        mail.send(msg)
        print(f"Email de bienvenida enviado exitosamente a: {email}")
        return True
        
    except Exception as e:
        print(f"Error enviando email de bienvenida a {email}: {str(e)}")
        return False