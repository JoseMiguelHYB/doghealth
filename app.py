from flask import Flask
from models import db
from routes import main
#from flask_mail import Mail, Message

app = Flask(__name__)

# Configuración de la clave secreta (necesaria para CSRF y sesiones seguras)
app.config['SECRET_KEY'] = 'miguel123'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vacunas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de Flask-Mail
""" app.config['MAIL_SERVER'] = 'smtp.exameple.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] ='josemiguelhyb@gmail.com'
app.config['MAIL_PASSWORD'] = 'miguel123'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app) """

 # Inicialización de la base de datos
db.init_app(app)

# Registro del blueprint
app.register_blueprint(main)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
