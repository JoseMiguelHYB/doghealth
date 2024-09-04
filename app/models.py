from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user
from datetime import datetime, timedelta

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    address = db.Column(db.String(256), nullable=False)
    city = db.Column(db.String(128), nullable=False)
    locality = db.Column(db.String(128), nullable=False)
    code_postal = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    dogs = db.relationship('Dog', backref='owner', lazy=True)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_current_user():
        """Retorna el usuario actualmente autenticado."""
        return current_user if current_user.is_authenticated else None
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Dog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dog_breed = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    photo = db.Column(db.String(255), nullable=True)
    weight = db.Column(db.Integer, nullable=False)
    allergys = db.Column(db.String(500), nullable=True)
    aniadir_nota = db.Column(db.String(500), nullable=False)
    microchip = db.Column(db.String(15), nullable=False)
    
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vaccines = db.relationship('Vaccine', backref='dog', lazy=True)
    medications = db.relationship('Medication', backref='dog', lazy=True)

    @staticmethod
    def get_by_name(name):
        return Dog.query.filter_by(name=name).first()

    @property
    def events(self):
        """Consolidate vaccines, medications, and custom events into a single list of events sorted by date."""
        all_events = []
        # Convert vaccines to a common event structure
        for vaccine in self.vaccines:
            all_events.append({
                'event_type': 'Vacuna',
                'description': vaccine.name,
                'event_date': vaccine.date_administered
            })
        # Convert medications to a common event structure
        for medication in self.medications:
            all_events.append({
                'event_type': 'Medicamento',
                'description': f'{medication.name}, {medication.doses_per_day} dosis por día',
                'event_date': medication.date_start
            })
        # Add custom events
        for event in self.events:
            all_events.append({
                'event_type': event.event_type,
                'description': event.description,
                'event_date': event.event_date
            })
        # Sort by date
        all_events.sort(key=lambda x: x['event_date'])
        return all_events

class Vaccine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_administered = db.Column(db.DateTime, nullable=False)
    veterinarian = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default="No Aplicada")
    notification_sent = db.Column(db.Boolean, default=False)
    dog_id = db.Column(db.Integer, db.ForeignKey('dog.id'), nullable=False)

    @staticmethod
    def get_by_dog_id(dog_id):
        return Vaccine.query.filter_by(dog_id=dog_id).all()
    
class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_start = db.Column(db.Date, nullable=False)
    date_end = db.Column(db.Date, nullable=False)
    doses_per_day = db.Column(db.Integer, nullable=False, default=2)
    time_of_first_dose = db.Column(db.Time, nullable=False)
    interval_hours = db.Column(db.Integer, nullable=False, default=12)
    notes = db.Column(db.Text, nullable=True)
    dog_id = db.Column(db.Integer, db.ForeignKey('dog.id'), nullable=False)

    doses = db.relationship('Dose', backref='medication', lazy=True)

    @staticmethod
    def get_by_dog_id(dog_id):
        """Devuelve una lista de medicamentos asociados a un perro específico."""
        return Medication.query.filter_by(dog_id=dog_id).all()

class Dose(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)

    @staticmethod
    def get_by_id(dose_id):
        return Dose.query.get(dose_id)

    @staticmethod
    def get_by_medication_id(medication_id):
        return Dose.query.filter_by(medication_id=medication_id).all()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)  # Tipo de evento, ej: Corte de pelo, Revisión médica
    description = db.Column(db.String(255), nullable=True)  # Descripción adicional del evento
    event_date = db.Column(db.DateTime, nullable=False)  # Fecha y hora del evento
    notification_sent = db.Column(db.Boolean, default=False) #campo para enviar los mensaje nuevo

    dog_id = db.Column(db.Integer, db.ForeignKey('dog.id'), nullable=False)  # Relación con la tabla Dog
    dog = db.relationship('Dog', backref=db.backref('events', lazy=True))  # Relación inversa

    def __repr__(self):
        return f'<Event {self.event_type} - {self.event_date}>'
    
