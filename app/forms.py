from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[
        DataRequired(message="El nombre de usuario es obligatorio."), 
        Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres.")])
    
    address = StringField('Dirección Completa', validators=[
        DataRequired(message="La dirección es obligatoria."), 
        Length(min=4, max=100, message="La dirección debe tener entre 4 y 100 caracteres.")])
    
    city = StringField('Ciudad', validators=[
        DataRequired(message="La ciudad es obligatoria."), 
        Length(min=2, max=50,  message="La ciudad debe tener entre 2 y 50 caracteres.")])
    
    locality = StringField('Localidad', validators=[
        DataRequired(message="La localidad es obligatoria."), 
        Length(min=2, max=50, message="La localidad debe tener entre 2 y 50 caracteres.")])
    
    code_postal = StringField('Código Postal', validators=[
        DataRequired(message="El código postal es obligatorio."), 
        Regexp('^[0-9]{5}$', message="El código postal debe ser un número de 5 dígitos.")])
    
    phone = StringField('Teléfono', validators=[
        DataRequired(message="El teléfono es obligatorio."), 
        Regexp('^[0-9]{9}$', message="El teléfono debe ser un número de 9 dígitos.")])
    
    email = StringField('E-Mail', validators=[
        DataRequired(message="El correo electrónico es obligatorio."), 
        Email(message="Debe ser un correo electrónico válido.")])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria."), 
        Length(min=5, max=25, message="La contraseña debe tener entre 8 y 25 caracteres.")]) #CAMBIAR: Hemos cambiado de minimo de 8 a 5 para que sea mas fácil       
        
class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message="El nombre de usuario es obligatorio."), Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres.")])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria."), 
        Length(min=5, max=25, message="La contraseña debe tener entre 8 y 25 caracteres.")])  #CAMBIAR: Hemos cambiado de minimo de 8 a 5 para que sea mas fácil
    
    
class UpdateClientForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[
        DataRequired(message="El nombre de usuario es obligatorio."), 
        Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres.")])
    
    address = StringField('Dirección Completa', validators=[
        DataRequired(message="La dirección es obligatoria."), 
        Length(min=4, max=100, message="La dirección debe tener entre 4 y 100 caracteres.")])
    
    city = StringField('Ciudad', validators=[
        DataRequired(message="La ciudad es obligatoria."), 
        Length(min=2, max=50,  message="La ciudad debe tener entre 2 y 50 caracteres.")])
    
    locality = StringField('Localidad', validators=[
        DataRequired(message="La localidad es obligatoria."), 
        Length(min=2, max=50, message="La localidad debe tener entre 2 y 50 caracteres.")])
    
    code_postal = StringField('Código Postal', validators=[
        DataRequired(message="El código postal es obligatorio."), 
        Regexp('^[0-9]{5}$', message="El código postal debe ser un número de 5 dígitos.")])
    
    phone = StringField('Teléfono', validators=[
        DataRequired(message="El teléfono es obligatorio."), 
        Regexp('^[0-9]{9}$', message="El teléfono debe ser un número de 9 dígitos.")])
    
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message="El correo electrónico es obligatorio."), 
        Email(message="Debe ser un correo electrónico válido.")])
    
    password = PasswordField('Nueva Contraseña', validators=[
        Optional(), 
        Length(min=5, max=25, message="La contraseña debe tener entre 5 y 25 caracteres.")])  # Permitir contraseña opcional






























