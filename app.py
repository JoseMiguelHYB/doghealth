from flask import Flask
from models import db, Mascota, Vacuna
from routes import main

app = Flask(__name__)
app.config['SQL_ALCHEMY_DATABASE_URI'] = 'sqlite:///vacunas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(main)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
