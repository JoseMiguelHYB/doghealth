from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, bcrypt, mail
from app.models import User, Dog, Vaccine, Medication, Event,  Dose
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from collections import defaultdict
from flask_mail import Message
from app.forms import *  # Importa el formulario desde forms.py
import logging

# Configuración básica de logging para depurar código
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    # Renderiza la plantilla 'home.html'
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Endpoint para manejar el registro de nuevos usuarios.
    
    - GET: Muestra el formulario de registro al usuario.
    - POST: Procesa los datos enviados desde el formulario.
    
    El formulario incluye datos como nombre de usuario, dirección, ciudad, localidad,
    código postal, teléfono, email, contraseña. Si la validación del formulario es exitosa,
    los datos son almacenados en la base de datos y se redirige al usuario a la página de inicio de sesión.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        # Capturar los datos del formulario
        username = form.username.data
        address = form.address.data
        city = form.city.data
        locality = form.locality.data
        code_postal = form.code_postal.data
        phone = form.phone.data
        email = form.email.data
        password = form.password.data
        
        # Loguear los valores capturados para depuración
        logger.debug(f"Datos capturados - Username: {username}, Address: {address}, City: {city}, "
                     f"Locality: {locality}, Code Postal: {code_postal}, Phone: {phone}, Email: {email}, "
                     f"Password (raw): {password}")
        
        # Hashear la contraseña
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        logger.debug(f"Password (hashed): {hashed_password}")  # Loguear la contraseña hasheada

        # Verificar si el nombre de usuario o el correo ya existen
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        phone_exists = User.query.filter_by(phone=phone).first()

        logger.debug(f"Verificación de existencia - User exists: {bool(user_exists)}, Email exists: {bool(email_exists)}, Phone exists: {bool(phone_exists)}")

        if user_exists:
            flash('El nombre de usuario ya existe.', 'danger')
        
        if email_exists:
            flash('El correo electrónico ya está en uso.', 'danger')
            
        if phone_exists:
            flash('El telefono ya esta en uso.', 'danger')    
        
        if user_exists or email_exists or phone_exists or phone_exists:
            # Redirigir a la misma página para mostrar los errores
            return redirect(url_for('register'))

        # Crear el nuevo usuario con todos los datos capturados
        user = User(
            username=username, 
            address=address,
            city=city,
            locality=locality,
            code_postal=code_postal,
            phone=phone,
            email=email, 
            password=hashed_password
        )
        logger.debug(f"User object created: {user}")  # Loguear el objeto usuario creado

        db.session.add(user)
        db.session.commit()
        logger.info("Nuevo usuario registrado y guardado en la base de datos")  # Confirmar que el usuario ha sido agregado a la base de datos

        flash('Tu cuenta ha sido creada!', 'success')
        return redirect(url_for('login'))

    logger.debug("GET request o form no validado")  # Log para casos donde no se valida el formulario o se hace un GET
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Endpoint para manejar el inicio de sesión de los usuarios.

    - GET: Muestra el formulario de inicio de sesión al usuario.
    - POST: Procesa los datos enviados desde el formulario.
    
    El formulario incluye nombre de usuario y contraseña. Si la validación 
    del formulario es exitosa y las credenciales son correctas, el usuario 
    se loguea y se redirige a client_dashboard.
    """
    form = LoginForm()
    logger.debug("Formulario de login cargado.")  # Log para depurar carga de formulario

    # Verificar si el formulario ha sido enviado y validado correctamente
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        logger.debug(f"Datos recibidos - Username: {username}, Password: {password}")  # Loguear datos capturados (evita loguear la contraseña en producción)

        # Intentar obtener el usuario por nombre de usuario
        user = User.get_by_username(username)
        logger.debug(f"Usuario obtenido: {user}")  # Loguear el objeto usuario o None si no existe

        # Verificar si el usuario existe y si la contraseña es correcta
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            logger.debug(f"Usuario {username} logueado con éxito.")  # Confirmar que el usuario ha iniciado sesión correctamente

            # Redirigir al dashboard del cliente
            logger.debug(f"Redirigiendo a dashboard de cliente para {username}.")
            return redirect(url_for('client_dashboard'))
        else:
            # Si el login falla, ya sea por usuario inexistente o contraseña incorrecta
            logger.debug(f"Login fallido para {username}. Usuario o contraseña incorrectos.")
            flash('Login fallido. Por favor revisa tu nombre de usuario y contraseña', 'danger')
            return redirect(url_for('login'))

    # Si es una solicitud GET o la validación del formulario falla, renderizar el formulario de login
    logger.debug("Mostrando formulario de login (GET o formulario no validado).")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    # Este endpoint maneja el cierre de sesión del usuario.
    # Requiere que el usuario esté autenticado (decorador @login_required).
    # Cuando se accede, se llama a logout_user() para cerrar la sesión actual del usuario.
    # Luego, se redirige al usuario a la página de login.
    
    logout_user()
    return redirect(url_for('login'))

@app.route('/update_client', methods=['GET', 'POST'])
@login_required
def update_client():
    """
    Endpoint para actualizar la información del cliente.
    
    - GET: Muestra el formulario con los datos actuales del cliente prellenados.
    - POST: Procesa los datos enviados desde el formulario y actualiza la información del cliente en la base de datos.
    
    Este endpoint permite a los usuarios autenticados modificar su información personal 
    como nombre de usuario, dirección, ciudad, localidad, código postal, teléfono, y correo electrónico. 
    También permite cambiar la contraseña si se proporciona una nueva.
    """
    form = UpdateClientForm()

    # Si la solicitud es GET, prellenar el formulario con los datos actuales del usuario
    if request.method == 'GET':
        form.username.data = current_user.username
        form.address.data = current_user.address
        form.city.data = current_user.city
        form.locality.data = current_user.locality
        form.code_postal.data = current_user.code_postal
        form.phone.data = current_user.phone
        form.email.data = current_user.email
        # Log para verificar la prellenación de datos del formulario
        logger.debug(f"Formulario prellenado con los datos actuales de {current_user.username}.")

    # Si el formulario es enviado y validado correctamente
    if form.validate_on_submit():
        # Actualizar la información del usuario con los datos del formulario
        current_user.username = form.username.data
        current_user.address = form.address.data
        current_user.city = form.city.data
        current_user.locality = form.locality.data
        current_user.code_postal = form.code_postal.data
        current_user.phone = form.phone.data
        current_user.email = form.email.data
        # Log para verificar la captura de los datos del formulario
        logger.debug(f"Datos actualizados - Username: {current_user.username}, Address: {current_user.address}, "
                     f"City: {current_user.city}, Locality: {current_user.locality}, Code Postal: {current_user.code_postal}, "
                     f"Phone: {current_user.phone}, Email: {current_user.email}")

        # Si el usuario ha ingresado una nueva contraseña, actualizarla
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
            # Log para confirmar el cambio de contraseña
            logger.debug(f"Contraseña actualizada para el usuario {current_user.username}.")

        # Guardar los cambios en la base de datos
        db.session.commit()
        # Confirmación de los cambios guardados
        logger.info(f"Información actualizada en la base de datos para el usuario {current_user.username}.")
        flash('¡Tu información ha sido actualizada!', 'success')
        
        # Redirigir al dashboard del cliente después de la actualización
        return redirect(url_for('client_dashboard'))

    # Renderizar el formulario de edición con los datos del cliente
    return render_template('update_client.html', form=form)


@app.route('/delete_client', methods=['GET', 'POST'])
@login_required
def delete_client():
    """
    Endpoint para eliminar la cuenta de un cliente junto con todos sus perros asociados y sus datos relacionados.

    - GET: Muestra una página de confirmación para la eliminación de la cuenta.
    - POST: Procesa la eliminación de la cuenta del usuario autenticado y sus perros en la base de datos.
    
    Este endpoint permite a los usuarios autenticados eliminar permanentemente su cuenta 
    del sistema, junto con todos los perros asociados y sus datos (vacunas, medicamentos, eventos).
    """
    if request.method == 'POST':
        # Capturar el ID del usuario actual
        user_id = current_user.id
        logger.debug(f"Solicitud de eliminación recibida para el usuario con ID: {user_id}")

        # Obtener al usuario de la base de datos
        user = User.query.get(user_id)
        logger.debug(f"Usuario encontrado en la base de datos: {user}")

        if user:
            # Obtener todos los perros asociados al usuario
            dogs = Dog.query.filter_by(owner_id=user_id).all()
            logger.debug(f"Perros asociados encontrados: {dogs}")

            # Eliminar cada perro usando la función delete_dog
            for dog in dogs:
                logger.debug(f"Eliminando perro con ID {dog.id} y todos sus datos relacionados.")
                delete_dog(dog.id)
                logger.info(f"Perro con ID {dog.id} eliminado junto con sus datos.")

            # Eliminar al usuario y confirmar los cambios en la base de datos
            db.session.delete(user)
            db.session.commit()
            logger.info(f"Usuario con ID {user_id} y todos sus perros asociados han sido eliminados de la base de datos.")

            #flash('Tu cuenta y todos tus perros han sido eliminados.', 'success')
            return redirect(url_for('home'))

        # Manejar el caso donde el usuario no se encuentra en la base de datos
        logger.error(f"Error al intentar eliminar: Usuario con ID {user_id} no encontrado.")
        flash('Hubo un problema al intentar eliminar tu cuenta.', 'danger')
        return redirect(url_for('client_dashboard'))

    # Renderizar la página de confirmación de eliminación
    logger.debug("Mostrando la página de confirmación de eliminación de cuenta.")
    return render_template('delete_client.html')

@app.route('/client_dashboard')
@login_required
def client_dashboard():
    # Este endpoint maneja la vista del dashboard para los usuarios o clientes
    # Requiere que el usuario esté autenticado (decorador @login_required).
    
    # Obtener la fecha y hora actuales
    current_time = datetime.now()
    logger.debug(f"Fecha y hora actuales obtenidas: {current_time}")  # Loguear la fecha y hora actuales
    
    # Generar un saludo basado en la hora del día
    current_hour = current_time.hour
    if current_hour < 12:
        greeting = "Buenos días"
    elif 12 <= current_hour < 18:
        greeting = "Buenas tardes"
    else:
        greeting = "Buenas noches"
    logger.debug(f"Saludo generado: {greeting}")  # Loguear el saludo generado
    
    # Consultar todos los perros asociados al usuario actual utilizando owner_id
    user_id = current_user.id
    dogs = Dog.query.filter_by(owner_id=user_id).all()
    logger.debug(f"Perros obtenidos para el usuario {user_id}: {dogs}")  # Loguear los perros obtenidos
    
    # Renderizar la plantilla, pasando la lista de perros, el saludo y la hora actual
    logger.debug(f"Renderizando client_dashboard.html con {len(dogs)} perros y saludo '{greeting}'")  # Loguear la renderización de la plantilla
    return render_template('client_dashboard.html', 
                           greeting=greeting,
                           dogs=dogs,
                           current_time=current_time,  # Pasar current_time a la plantilla
                           current_user=current_user)

@app.route('/dog/<int:dog_id>')
def dog_profile(dog_id):
    # Obtener el perro por ID o mostrar 404 si no existe
    dog = Dog.query.get_or_404(dog_id)
    logging.debug(f'Dog retrieved: {dog}')
    
    # Obtener todos los perros del usuario excepto el actual (suponiendo que tienes una relación 'owner' en tu modelo)
    other_dogs = Dog.query.filter(Dog.owner_id == dog.owner_id, Dog.id != dog_id).all()
    logging.debug(f'Other dogs retrieved: {other_dogs}')
    
    # Pasar la información del perro y los otros perros al template
    return render_template('dog_profile.html', dog=dog, dogs=other_dogs)

@app.route('/dog/<int:dog_id>/vaccine/add', methods=['GET', 'POST'])
@login_required
def add_vaccine(dog_id):
    # Obtener el objeto del perro utilizando su ID; devuelve un error 404 si no se encuentra.
    dog = Dog.query.get_or_404(dog_id)
    logger.debug(f"Obtenido perro con ID: {dog_id} - {dog}")

    # Si el método de la solicitud es POST, se procesa el formulario para añadir una nueva vacuna.
    if request.method == 'POST':
        # Obtener los datos del formulario
        name = request.form.get('name')
        date_administered = request.form.get('date_administered')
        veterinarian = request.form.get('veterinarian')
        notes = request.form.get('notes')

        logger.debug(f"Datos del formulario recibidos: "
                     f"Nombre: {name}, Fecha de Administración: {date_administered}, "
                     f"Veterinario: {veterinarian}, Notas: {notes}")

        # Crear un nuevo objeto de vacuna con los datos proporcionados
        new_vaccine = Vaccine(
            name=name,
            date_administered=date_administered,
            veterinarian=veterinarian,
            notes=notes,
            dog_id=dog_id
        )

        # Añadir la nueva vacuna a la sesión de la base de datos y confirmar los cambios
        db.session.add(new_vaccine)
        db.session.commit()
        logger.debug(f"Vacuna añadida a la base de datos para el perro con ID: {dog_id}")

        # Mostrar un mensaje de éxito al usuario
        flash('Vacuna añadida exitosamente.', 'success')
        logger.debug(f"Redirigiendo a la vista de vacunas para el perro con ID: {dog_id}")

        # Redirigir al usuario a la página de visualización de vacunas
        return redirect(url_for('view_vaccines', dog_id=dog_id))

    # Si el método es GET, se renderiza la plantilla para añadir una nueva vacuna.
    logger.debug(f"Renderizando el formulario para añadir una vacuna para el perro con ID: {dog_id}")
    return render_template('add_vaccine.html', dog=dog)

# Configuración de la carpeta de subida de archivos
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_dog', methods=['GET', 'POST'])
def add_dog():
    if request.method == 'POST':
        name = request.form['name']
        dog_breed = request.form['dog_breed']
        gender = request.form['gender']
        age = request.form['age']
        photo = request.files['photo']
        weight = request.form['weight']
        allergys = request.form['allergys']
        aniadir_nota = request.form['aniadir_nota']
        microchip = request.form['microchip']

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)

            # Guardar la ruta relativa para la base de datos
            photo_url = f"uploads/{filename}"

            # Crear un nuevo perro y guardar la ruta de la foto relativa a 'static/uploads/'
            dog = Dog(name=name, dog_breed=dog_breed, gender=gender, age=age, photo=photo_url, weight=weight, allergys=allergys, aniadir_nota=aniadir_nota, microchip=microchip, owner_id=current_user.id)
            db.session.add(dog)
            db.session.commit()

            flash('El perro ha sido agregado exitosamente!', 'success')
            return redirect(url_for('client_dashboard'))

    return render_template('add_dog.html')


@app.route('/see_dogs')
@login_required  # Asegura que solo los usuarios autenticados puedan acceder a esta ruta
def see_dogs():
    # Obtener todos los perros del usuario logueado
    dogs = Dog.query.filter_by(owner_id=current_user.id).all()
    return redirect(url_for('client_dashboard'))


@app.route('/update_dog/<int:dog_id>', methods=['GET', 'POST'])
@login_required
def update_dog(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    
    if dog.owner_id != current_user.id:
        flash('No tienes permiso para actualizar este perro.', 'danger')
        return redirect(url_for('see_dogs'))
    
    if request.method == 'POST':
        dog.name = request.form['name']
        dog.dog_breed = request.form['dog_breed']
        dog.age = request.form['age']
        
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
                dog.photo = os.path.join('uploads', filename)
        
        db.session.commit()
        flash('El perro ha sido actualizado exitosamente!', 'success')
        return redirect(url_for('see_dogs'))
    
    return render_template('update_dog.html', dog=dog)

@app.route('/delete_dog/<int:dog_id>', methods=['GET', 'POST'])
@login_required
def delete_dog(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    
    if dog.owner_id != current_user.id:
        flash('No tienes permiso para eliminar este perro.', 'danger')
        return redirect(url_for('see_dogs'))
    
    if request.method == 'POST':
        # Eliminar todas las dosis relacionadas a los medicamentos del perro
        medications = Medication.query.filter_by(dog_id=dog.id).all()
        for medication in medications:
            Dose.query.filter_by(medication_id=medication.id).delete()

        # Eliminar todas las vacunas relacionadas
        Vaccine.query.filter_by(dog_id=dog.id).delete()
        
        # Eliminar todos los medicamentos relacionados
        Medication.query.filter_by(dog_id=dog.id).delete()

        # Eliminar todos los eventos relacionados
        Event.query.filter_by(dog_id=dog.id).delete()

        # Ahora que no hay referencias, eliminamos el perro
        db.session.delete(dog)
        
        # Guardar cambios en la base de datos
        db.session.commit()
        
        #flash(f'{dog.name} ha sido eliminado exitosamente.', 'success')
        return redirect(url_for('see_dogs'))
    
    return render_template('delete_dog.html', dog=dog)

@app.route('/dog/<int:dog_id>/vaccines')
@login_required
def view_vaccines(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    vaccines = Vaccine.get_by_dog_id(dog_id)
    now = datetime.now()  # Obtener la hora actual
    return render_template('view_vaccines.html', dog=dog, vaccines=vaccines, now=now)

@app.route('/dog/vaccine/<int:vaccine_id>/edit', methods=['GET', 'POST'])
@login_required
def update_vaccine(vaccine_id):
    vaccine = Vaccine.query.get_or_404(vaccine_id)
    dog = Dog.query.get_or_404(vaccine.dog_id)

    # Verificar si el usuario actual es el dueño del perro asociado a la vacuna
    if dog.owner_id != current_user.id:
        flash('No tienes permiso para actualizar esta vacuna.', 'danger')
        return redirect(url_for('view_vaccines', dog_id=dog.id))

    if request.method == 'POST':
        # Actualizar los campos de la vacuna con los datos del formulario
        vaccine.name = request.form['name']
        vaccine.veterinarian = request.form['veterinarian']
        vaccine.notes = request.form['notes']

        # Depuración: Imprimir los valores obtenidos para verificar
        print(f'Nombre de la vacuna: {vaccine.name}')
        print(f'Veterinario: {vaccine.veterinarian}')
        print(f'Notas: {vaccine.notes}')

        # Convertir la fecha del formulario en un objeto datetime
        vaccine_date = request.form['date_administered']
        new_vaccine_date = datetime.strptime(vaccine_date, '%Y-%m-%dT%H:%M')

        # Restablecer la notificación si la fecha ha cambiado
        if new_vaccine_date != vaccine.date_administered:
            vaccine.date_administered = new_vaccine_date
            vaccine.notification_sent = False  # Corregido: "notificacion_sent" a "notification_sent"

        db.session.commit()
        flash('La vacuna ha sido actualizada exitosamente!', 'success')
        return redirect(url_for('view_vaccines', dog_id=dog.id))

    # Formatear la fecha de la vacuna para que se muestre correctamente en el formulario
    vaccine_date_formatted = vaccine.date_administered.strftime('%Y-%m-%dT%H:%M')

    return render_template('update_vaccine.html', vaccine=vaccine, vaccine_date_formatted=vaccine_date_formatted)

@app.route('/dog/vaccine/<int:vaccine_id>/delete', methods=['POST'])
@login_required
def delete_vaccine(vaccine_id):
    vaccine = Vaccine.query.get_or_404(vaccine_id)
    dog_id = vaccine.dog_id
    db.session.delete(vaccine)
    db.session.commit()
    flash('Vacuna eliminada exitosamente.', 'danger')
    return redirect(url_for('view_vaccines', dog_id=dog_id))


@app.route('/update_vaccine_status/<int:vaccine_id>', methods=['POST'])
@login_required
def update_vaccine_status(vaccine_id):
    # Obtener la vacuna a través del ID
    logging.debug(f"Obteniendo la vacuna con ID: {vaccine_id}")
    vaccine = Vaccine.query.get_or_404(vaccine_id)

    # Obtener el nuevo estado desde el formulario
    new_status = request.form.get('status')
    logging.debug(f"Nuevo estado recibido del formulario: {new_status}")

    # Actualizar el estado de la vacuna
    if new_status in ['Aplicada', 'No Aplicada']:
        logging.debug(f"Actualizando el estado de la vacuna a: {new_status}")
        vaccine.status = new_status
        db.session.commit()
        logging.debug("Cambio de estado de la vacuna guardado en la base de datos.")
        flash('El estado de la vacuna se actualizó correctamente', 'success')
    else:
        logging.warning(f"Estado inválido recibido: {new_status}")
        flash('Estado inválido. Por favor, seleccione una opción válida.', 'danger')

    # Redirigir a la vista de vacunas, pasando el dog_id
    logging.debug(f"Redirigiendo a la vista de vacunas para el perro con ID: {vaccine.dog_id}")
    return redirect(url_for('view_vaccines', dog_id=vaccine.dog_id))

@app.route('/dog/<int:dog_id>/medications')
@login_required
def view_medications(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    medications = Medication.get_by_dog_id(dog_id)
    
    # Iterar sobre cada medicación y sus dosis asociadas
    #for medication in medications:
        #print(f"Medicación ID: {medication.id}, Nombre: {medication.name}")
        #for dose in medication.doses:
        #    print(f"  Dose ID: {dose.id}, Hora: {dose.time}, Fecha: {dose.date}, Completado: {dose.completed}")

    return render_template('view_medications.html', dog=dog, medications=medications)

@app.route('/dog/<int:dog_id>/medication/add', methods=['GET', 'POST'])
@login_required
def add_medication(dog_id):
    print(f"Adding medication for dog ID: {dog_id}")
    dog = Dog.query.get_or_404(dog_id)
    
    if request.method == 'POST':
        print("POST request received.")

        # Captura y muestra los valores del formulario
        name = request.form.get('name')
        date_start = request.form.get('date_start')
        date_end = request.form.get('date_end')
        doses_per_day = request.form.get('doses_per_day')
        time_of_first_dose = request.form.get('time_of_first_dose')
        interval_hours = request.form.get('interval_hours')
        notes = request.form.get('notes')

        print(f"Form data received: name={name}, date_start={date_start}, date_end={date_end}, doses_per_day={doses_per_day}, time_of_first_dose={time_of_first_dose}, interval_hours={interval_hours}, notes={notes}")

        # Crear una nueva instancia de Medication con los datos del formulario
        new_medication = Medication(
            name=name,
            date_start=datetime.strptime(date_start, '%Y-%m-%d').date(),
            date_end=datetime.strptime(date_end, '%Y-%m-%d').date(),
            doses_per_day=int(doses_per_day),
            time_of_first_dose=datetime.strptime(time_of_first_dose, '%H:%M').time(),
            interval_hours=int(interval_hours),
            notes=notes,
            dog_id=dog_id
        )

        # Insertar la nueva medicación en la base de datos para obtener un ID
        db.session.add(new_medication)
        db.session.commit()  # Esto asegura que new_medication tenga un ID asignado
        print(f"Medication {new_medication.name} added to database with ID: {new_medication.id}")

        # Generar las dosis para este medicamento usando el ID asignado
        print("Generating doses...")
        generate_doses(new_medication)  # Llamada a la función que ahora está en routes.py

        flash('Medicamento añadido exitosamente.', 'success')
        return redirect(url_for('dog_profile', dog_id=dog_id))

    return render_template('add_medication.html', dog=dog)


#IMPORTANTE: Solo genera hora limite 00:00 de la madrugada ya a esa hora no genera doses
def generate_doses(medication):
    logger.debug(f"Generating doses for medication ID: {medication.id}, start date: {medication.date_start}, end date: {medication.date_end}")
    
    # Inicializar la fecha y hora actuales
    start_datetime = datetime.combine(medication.date_start, medication.time_of_first_dose)
    current_datetime = start_datetime

    logger.debug(f"Initial current_datetime: {current_datetime}, date: {current_datetime.date()}, time: {current_datetime.time()}")

    while current_datetime.date() <= medication.date_end:
        logger.debug(f"Starting loop for date: {current_datetime.date()}")

        doses_generated = 0  # Contador de dosis generadas para el día actual

        while doses_generated < medication.doses_per_day:
            if current_datetime.date() > medication.date_end:
                break

            # Crear una nueva dosis
            dose = Dose(
                medication_id=medication.id,
                time=current_datetime.time(),
                date=current_datetime.date()
            )

            logger.debug(f"Generated dose {doses_generated + 1}/{medication.doses_per_day} for date: {current_datetime.date()}, time: {current_datetime.time()}")

            db.session.add(dose)

            # Avanzar al siguiente intervalo de dosis
            doses_generated += 1
            next_datetime = current_datetime + timedelta(hours=medication.interval_hours)

            # Si la hora de la siguiente dosis pasa de la medianoche, ajusta la fecha y hora
            if next_datetime.date() > current_datetime.date():
                logger.debug(f"Next dose time passes midnight. Moving to the next day.")
                break
            else:
                current_datetime = next_datetime

        # Avanzar al siguiente día y reiniciar la hora al tiempo de la primera dosis
        current_datetime = datetime.combine(current_datetime.date() + timedelta(days=1), medication.time_of_first_dose)
        logger.debug(f"Moved to next day: {current_datetime.date()}, resetting time to first dose: {medication.time_of_first_dose}")

    # Confirmar que todas las dosis se han guardado en la base de datos
    db.session.commit()
    logger.debug("Doses generation completed.")

@app.route('/update_dose/<int:dose_id>', methods=['POST'])
@login_required
def update_dose(dose_id):
    try:
        # Obtener los datos JSON de la solicitud
        data = request.get_json()
        completed = data.get('completed', False)

        # Depuración: imprimir los datos recibidos
        print(f"Received request to update dose with ID {dose_id}. Data received: {data}")

        # Buscar la dosis en la base de datos
        dose = Dose.query.get_or_404(dose_id)

        # Depuración: imprimir los detalles de la dosis antes de la actualización
        print(f"Current dose details before update - ID: {dose.id}, Completed: {dose.completed}")

        # Actualizar el estado de la dosis
        dose.completed = completed
        db.session.commit()

        # Depuración: imprimir los detalles de la dosis después de la actualización
        print(f"Updated dose details - ID: {dose.id}, Completed: {dose.completed}")

        # Enviar una respuesta de éxito
        return jsonify({'message': 'Dosis actualizada correctamente'})
    except Exception as e:
        # Depuración: imprimir el error
        print(f"Error updating dose - ID: {dose_id}. Error: {str(e)}")
        
        # Enviar una respuesta de error
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/dog/medication/<int:medication_id>/edit', methods=['GET', 'POST'])
@login_required
def update_medication(medication_id):
    medication = Medication.query.get_or_404(medication_id)
    if request.method == 'POST':
        # Actualizar los campos del medicamento con los valores del formulario
        medication.name = request.form.get('name')
        medication.date_start = request.form.get('date_start')
        medication.date_end = request.form.get('date_end')
        medication.doses_per_day = request.form.get('doses_per_day')
        medication.time_of_first_dose = request.form.get('time_of_first_dose')
        medication.interval_hours = request.form.get('interval_hours')
        medication.notes = request.form.get('notes')

        # Depuración: Imprimir los valores obtenidos para verificar
        print(f'Nombre: {medication.name}')
        print(f'Fecha de Inicio: {medication.date_start}')
        print(f'Fecha de Fin: {medication.date_end}')
        print(f'Dosis por Día: {medication.doses_per_day}')
        print(f'Hora de la primera dosis: {medication.time_of_first_dose}')
        print(f'Intervalo entre dosis (horas): {medication.interval_hours}')
        print(f'Notas: {medication.notes}')

        # Intentar guardar en la base de datos
        try:
            # Primero, confirmar los cambios en el medicamento
            db.session.commit()
            print("Después de commit")

            # Eliminar las dosis anteriores asociadas a este medicamento
            Dose.query.filter_by(medication_id=medication.id).delete()
            db.session.commit()  # Confirmar la eliminación de las dosis

            # Generar nuevas dosis con los valores actualizados
            generate_doses(medication)

            flash('Medicamento actualizado y dosis regeneradas exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el medicamento: {str(e)}', 'danger')
            print(f'Error al actualizar el medicamento: {str(e)}')

        # Redirigir a la vista de medicaciones
        return redirect(url_for('view_medications', dog_id=medication.dog_id))

    return render_template('update_medication.html', medication=medication)

@app.route('/dog/medication/<int:medication_id>/delete', methods=['POST'])
@login_required
def delete_medication(medication_id):
    print(f"Attempting to delete medication with ID: {medication_id}")
    
    medication = Medication.query.get_or_404(medication_id)
    if medication:
        print(f"Medication found: {medication.name} for dog ID: {medication.dog_id}")
    else:
        print(f"Medication with ID {medication_id} not found.")
        flash('Medicamento no encontrado.', 'danger')
        return redirect(url_for('view_medications', dog_id=medication.dog_id))

    dog_id = medication.dog_id

    # Eliminar todas las dosis asociadas al medicamento
    try:
        for dose in medication.doses:
            print(f"Deleting dose with ID: {dose.id} for medication ID: {medication.id}")
            db.session.delete(dose)
        
        # Ahora elimina el medicamento
        db.session.delete(medication)
        db.session.commit()
        print(f"Medication with ID {medication_id} and its doses deleted successfully.")
        flash('Medicamento y todas sus dosis asociadas han sido eliminadas exitosamente.', 'danger')
    except Exception as e:
        print(f"Error deleting medication and its doses: {e}")
        flash('Ocurrió un error al intentar eliminar el medicamento y sus dosis.', 'danger')
        return redirect(url_for('view_medications', dog_id=dog_id))

    return redirect(url_for('view_medications', dog_id=dog_id))

def calculate_dose_times(medication):
    dose_times = []
    current_time = datetime.combine(datetime.today(), medication.time_of_first_dose)
    for _ in range(medication.doses_per_day):
        dose_times.append(current_time.time())
        current_time += timedelta(hours=medication.interval_hours)
    return dose_times

def calculate_dose_times(medication):
    # Asumiendo que esta función calcula los tiempos de las dosis y devuelve una lista de diccionarios
    # Cada diccionario en la lista debe contener: id, time, name, day
    # Aquí se te proporciona un esquema básico para fines ilustrativos
    doses = []
    start_time = datetime.combine(datetime.today(), medication.time_of_first_dose)

    for i in range(medication.doses_per_day):
        time = (start_time + timedelta(hours=medication.interval_hours * i)).strftime("%I:%M %p")
        doses.append({
            'id': i + 1,
            'time': time,
            'name': medication.name,
            'day': (datetime.now() + timedelta(days=i // medication.doses_per_day)).strftime("%d %B %Y")
        })

    return doses


@app.route('/medication_profile/<int:medication_id>')
def medication_profile(medication_id):
    # Obtener la medicación y el perro asociado
    medication = Medication.query.get_or_404(medication_id)
    dog_id = medication.dog_id
    dog = Dog.query.get_or_404(dog_id)

    # Obtener el rango de fechas
    date_start = medication.date_start.date() if isinstance(medication.date_start, datetime) else medication.date_start
    date_end = medication.date_end.date() if isinstance(medication.date_end, datetime) else medication.date_end
    days_range = [(date_start + timedelta(days=i)) for i in range((date_end - date_start).days + 1)]

    # Obtener las dosis asociadas a la medicación
    doses = medication.doses  # Suponiendo que la relación está configurada como medication.doses

    # Imprimir los valores para depuración
    print(f"Medicamento: {medication.name}, ID: {medication.id}")
    print(f"Rango de Fechas: {date_start} - {date_end}")
    print("Dosis Asociadas a la Medicación:")
    for dose in doses:
        print(f"  Dose ID: {dose.id}, Hora: {dose.time}, Fecha: {dose.date}, Completado: {dose.completed}")

    # Preparar los datos para la plantilla
    medication_schedule = defaultdict(list)

    # Organizar dosis por día
    for dose in doses:
        dose_day = dose.date  # Asumiendo que `dose.date` es la fecha de la dosis
        if dose_day in days_range:
            medication_schedule[dose_day].append(dose)

    total_doses = len(doses)

    return render_template(
        'medication_profile.html',
        dog=dog,
        medication=medication,
        medication_schedule=medication_schedule,
        days_range=days_range,
        total_doses=total_doses
    )

# Función para enviar correo para VACUNAS
def enviar_correo(destinatario, nombre_perro, nombre_vacuna):
    with app.app_context():
        try:
            msg = Message('Vacuna Próxima a Expirar',
                          recipients=[destinatario])
            
            # Renderizar la plantilla HTML con los parámetros
            msg.html = render_template('correo_vacuna.html', 
                                       nombre_perro=nombre_perro, 
                                       nombre_vacuna=nombre_vacuna)
            
            mail.send(msg)
            flash(f'Correo enviado a {destinatario}', 'success')
            print(f'Correo enviado a {destinatario} sobre la vacuna {nombre_vacuna} de {nombre_perro}')
        except Exception as e:
            flash(f'Error al enviar el correo: {str(e)}', 'danger')
            print(f'Error al enviar el correo: {str(e)}')

@app.route('/check_expiration/<int:vaccine_id>', methods=['POST'])
def check_expiration(vaccine_id):
    try:
        # Obtener la vacuna por ID
        vaccine = get_vaccine_by_id(vaccine_id)
        print(f"Vacuna obtenida: {vaccine}")

        if not vaccine:
            print(f"Vacuna con ID {vaccine_id} no encontrada")
            return jsonify({'status': 'Vacuna no encontrada'}), 404

        # Verificar si la notificación ya fue enviada
        if vaccine.notification_sent:
            print(f"El email ya ha sido enviado anteriormente para la vacuna ID {vaccine_id}")
            return jsonify({'status': 'El email ya ha sido enviado anteriormente'})

        # Obtener el email del propietario del perro
        user_email = vaccine.dog.owner.email
        print(f"Email del usuario: {user_email}")

        # Obtener la fecha y hora actuales
        now = datetime.now()
        print(f"Fecha y hora actuales: {now}")
        print(f"Fecha de administración de la vacuna: {vaccine.date_administered}")

        # Calcular la diferencia de tiempo en segundos
        time_difference = (vaccine.date_administered - now).total_seconds()
        print(f"Diferencia de tiempo en segundos: {time_difference}")

        # Revisar si la diferencia es exactamente o cercana a 24 horas (en segundos)
        if 86340 <= time_difference <= 86400:
            print(f"Dentro del rango de 24 horas. Procediendo a marcar la vacuna como notificada y a enviar email.")

            # Marcar como enviada en la base de datos antes de enviar el correo
            vaccine.notification_sent = True
            save_vaccine(vaccine)
            print(f"Vacuna marcada como notificada en la base de datos")

            # Enviar el correo
            enviar_correo(user_email, vaccine.dog.name, vaccine.name)
            print(f"Correo enviado a {user_email} para la vacuna {vaccine.name} del perro {vaccine.dog.name}")

            return jsonify({'status': 'Email enviado'})
        else:
            print(f"No es necesario enviar el email para la vacuna ID {vaccine_id}.")
            return jsonify({'status': 'No es necesario enviar el email'})

    except Exception as e:
        print(f"Error en el servidor: {str(e)}")
        return jsonify({'status': 'Error en el servidor', 'error': str(e)}), 500


#obitne la vacuna de la base de datos
def get_vaccine_by_id(vaccine_id):
    try:
        # Intenta obtener la vacuna de la base de datos por su ID.
        vaccine = Vaccine.query.get(vaccine_id)
        return vaccine
    except Exception as e:
        print(f'Error al obtener la vacuna con ID {vaccine_id}: {str(e)}')
        return None

# Guardar la vacuna en la base de datos
def save_vaccine(vaccine):
    try:
        # Añadir la vacuna a la sesión de la base de datos y hacer commit.
        db.session.add(vaccine)
        db.session.commit()
        print(f'Vacuna con ID {vaccine.id} guardada correctamente.')
    except Exception as e:
        # Si ocurre algún error, realiza un rollback para evitar problemas de integridad en la base de datos.
        db.session.rollback()
        print(f'Error al guardar la vacuna con ID {vaccine.id}: {str(e)}')
        return None

@app.route('/add_event/<int:dog_id>', methods=['GET', 'POST'])
def add_event(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    
    if request.method == 'POST':
        event_type = request.form['event_type']
        description = request.form['description']
        event_date = request.form['event_date']
        
        # Convertir la fecha del formulario en un objeto datetime
        event_date = datetime.strptime(event_date, '%Y-%m-%dT%H:%M')

        # Crear un nuevo evento
        new_event = Event(event_type=event_type, description=description, event_date=event_date, dog_id=dog.id)
        db.session.add(new_event)
        db.session.commit()

        flash('El evento ha sido añadido exitosamente!', 'success')
        return redirect(url_for('dog_profile', dog_id=dog.id))

    return render_template('add_event.html', dog=dog)

@app.route('/view_events/<int:dog_id>')
def view_events(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    events = dog.events

    return render_template('view_events.html', dog=dog, events=events)

@app.route('/check_expiration_event/<int:event_id>', methods=['POST'])
def check_expiration_event(event_id):
    try:
        # Obtener el evento por ID
        event = get_event_by_id(event_id)
        print(f"Evento obtenido: {event}")

        if not event:
            print(f"Evento con ID {event_id} no encontrado")
            return jsonify({'status': 'Evento no encontrado'}), 404

        now = datetime.now()
        print(f"Fecha y hora actuales: {now}")
        print(f"Fecha del evento: {event.event_date}")

        # Calcular la diferencia de tiempo en segundos
        time_difference = (event.event_date - now).total_seconds()
        print(f"Diferencia de tiempo en segundos: {time_difference}")

        # Revisar si la diferencia es exactamente o cercana a 24 horas (en segundos)
        if 86340 <= time_difference <= 86400 and not event.notification_sent:
            print(f"Dentro del rango de 24 horas. Procediendo a enviar email.")

            # Enviar el correo
            user_email = event.dog.owner.email
            enviar_correo_event(user_email, event.dog.name, event.event_type, event.event_date)
            print(f"Correo enviado a {user_email} para el evento {event.event_type} del perro {event.dog.name}")

            # Marcar como enviada en la base de datos después de enviar el correo
            event.notification_sent = True
            save_event(event)
            print(f"Evento marcado como notificado en la base de datos")

            return jsonify({'status': 'Email enviado'})
        else:
            print(f"No es necesario enviar el email para el evento ID {event_id}.")
            return jsonify({'status': 'No es necesario enviar el email'})

    except Exception as e:
        print(f"Error en el servidor: {str(e)}")
        return jsonify({'status': 'Error en el servidor', 'error': str(e)}), 500

def get_event_by_id(event_id):
    """
    Obtiene un evento por su ID.
    """
    return Event.query.get(event_id)

def save_event(event):
    """
    Guarda o actualiza un evento en la base de datos.
    """
    db.session.add(event)
    db.session.commit()

# Función para enviar correo sobre un evento
def enviar_correo_event(destinatario, nombre_perro, tipo_evento, fecha_evento):
    with app.app_context():
        try:
            msg = Message('Nuevo Evento para tu Perro',
                          recipients=[destinatario])
            
            # Renderizar la plantilla HTML con los parámetros
            msg.html = render_template('correo_event.html', 
                                       nombre_perro=nombre_perro, 
                                       tipo_evento=tipo_evento,
                                       fecha_evento=fecha_evento.strftime('%d %B %Y %H:%M'))
            
            mail.send(msg)
            flash(f'Correo enviado a {destinatario}', 'success')
            print(f'Correo enviado a {destinatario} sobre el evento {tipo_evento} de {nombre_perro} programado para {fecha_evento}')
        except Exception as e:
            flash(f'Error al enviar el correo: {str(e)}', 'danger')
            print(f'Error al enviar el correo: {str(e)}')

@app.route('/update_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    dog = Dog.query.get_or_404(event.dog_id)

    # Verificar si el usuario actual es el dueño del perro asociado al evento
    if dog.owner_id != current_user.id:
        flash('No tienes permiso para actualizar este evento.', 'danger')
        return redirect(url_for('dog_profile', dog_id=dog.id))

    if request.method == 'POST':
        # Actualizar los campos del evento
        event.event_type = request.form['event_type']
        event.description = request.form['description']
        
        # Convertir la fecha del formulario en un objeto datetime
        event_date = request.form['event_date']
        new_event_date = datetime.strptime(event_date, '%Y-%m-%dT%H:%M')

        # Restablecer la notificación si la fecha ha cambiado
        if new_event_date != event.event_date:
            event.event_date = new_event_date
            event.notification_sent = False
        
        db.session.commit()
        flash('El evento ha sido actualizado exitosamente!', 'success')
        return redirect(url_for('dog_profile', dog_id=dog.id))
    
    # Formatear la fecha del evento para que se muestre correctamente en el formulario
    event_date_formatted = event.event_date.strftime('%Y-%m-%dT%H:%M')

    return render_template('update_event.html', event=event, dog=dog, event_date_formatted=event_date_formatted)

@app.route('/delete_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    dog = Dog.query.get_or_404(event.dog_id)
    
    # Verificar si el usuario actual es el dueño del perro asociado al evento
    if dog.owner_id != current_user.id:
        flash('No tienes permiso para eliminar este evento.', 'danger')
        return redirect(url_for('dog_profile', dog_id=dog.id))

    if request.method == 'POST':
        # Eliminar el evento de la base de datos
        db.session.delete(event)
        db.session.commit()
        flash('El evento ha sido eliminado exitosamente!', 'success')
        return redirect(url_for('dog_profile', dog_id=dog.id))
    
    # Si el método es GET, renderizar la página de confirmación
    return render_template('delete_event.html', event=event, dog=dog)


#---------------BARRA DE BÚSQUEDA DE EVENTOS EN dog_profile.html--------
@app.route('/dog/<int:dog_id>/events')
def view_events_barrabusqueda(dog_id):
    query = request.args.get('q')
    dog = Dog.query.get_or_404(dog_id)
    
    if query:
        # Filtrar eventos por el criterio de búsqueda
        events = Event.query.filter(Event.dog_id == dog_id, Event.event_type.ilike(f'%{query}%')).all()
    else:
        # Cargar todos los eventos si no hay criterio de búsqueda
        events = dog.events
    
    return render_template('events.html', dog=dog, events=events)

@app.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    # Por ahora solo redirige a la página informativa de recuperación de contraseña
    return render_template('password_recover.html')






