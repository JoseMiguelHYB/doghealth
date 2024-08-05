from flask_sqlalchemy import SLQAlchemy

db = SLQAlchemy()

class Mascota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    raza = db.Column(db.String(50), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)

class Vacuna(db.Model):
    id = db.Colum(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    fecha_administracion = db.Column(db.Date, nullable=False)
    fecha_proxima_dosis = db.Column(db.Date, nullable=False)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascota.id'), nullable=False)


