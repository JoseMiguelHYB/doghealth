from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Mascota(db.Model):
    __tablename__ = 'mascota'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    raza = db.Column(db.String(50), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)

class Vacuna(db.Model):
    __tablename__ = 'vacuna'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    fecha_administracion = db.Column(db.Date, nullable=False)
    fecha_proxima_dosis = db.Column(db.Date, nullable=False)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascota.id'), nullable=False)


