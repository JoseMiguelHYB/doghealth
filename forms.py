from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired

class MascotaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    raza = StringField('Raza', validators=[DataRequired()])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    submit = SubmitField('Guardar')

class VacunaForm(FlaskForm):
    tipo = StringField('Tipo de Vacuna', validators=[DataRequired()])
    fecha_administracion = DateField('Fecha de Administración', validators=[DataRequired()])
    fecha_proxima_dosis = DateField('Fecha de Próxima dosis', validators=[DataRequired()])
    submit = SubmitField('Guardar')