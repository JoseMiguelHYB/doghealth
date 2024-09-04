from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import secrets

# Crear una instancia de la aplicación Flask
app = Flask(__name__)
app.config.from_object('config.Config')

# Inicializar la base de datos
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirige a la vista de login si no autenticado

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # El puerto 587 es para TLS
app.config['MAIL_USE_TLS'] = True  # Usa TLS
app.config['MAIL_USE_SSL'] = False  # Desactiva SSL
app.config['MAIL_USERNAME'] = 'josemiguelhyb@gmail.com'
app.config['MAIL_PASSWORD'] = 'ukkh yzzr ajuc pkrh'  # Contraseña de aplicación generada
app.config['MAIL_DEFAULT_SENDER'] = ('MIGUEL', 'josemiguelhyb@gmail.com')

# Inicializar Flask-Mail
mail = Mail(app)

# Secret key para la seguridad de la aplicación
app.secret_key = secrets.token_hex(16)

# Importar las rutas y modelos
from app import routes, models

# Crear las tablas automáticamente si no existen
with app.app_context():
    db.create_all()
