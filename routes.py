from flask import Blueprint, render_template, redirect, url_for
from models import db, Mascota, Vacuna
from forms import MascotaForm, VacunaForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    mascotas = Mascota.query.all()
    return render_template('index.html', mascotas=mascotas)

@main.route('/mascota/nueva',  methods=['GET', 'POST'])
def nueva_mascota():
    form = MascotaForm()
    if form.validate_on_submit():
        nueva_mascota = Mascota(
            nombre=form.nombre.data,
            raza=form.raza.data,
            fecha_nacimiento=form.fecha_nacimiento.data
        )
        db.session.add(nueva_mascota)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('mascota.html', form=form)

@main.route('/vacuna/nueva/<int:mascota_id>', methods=['GET', 'POST'])
def nueva_vacuna(mascota_id):
    form = VacunaForm()
    if form.validate_on_submit():
        nueva_vacuna = Vacuna(
            tipo=form.tipo.data,
            fecha_administracion=form.fecha_administracion.data,
            fecha_proxima_dosis=form.fecha_proxima_dosis.data,
            mascota_id=mascota_id       
        )
        db.session.add(nueva_vacuna)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('vacuna.html', form=form)


@main.route('/mascota/<int:mascota_id>/vacunas')
def ver_vacunas(mascota_id):
    mascota = Mascota.query.get_or_404(mascota_id)
    vacunas = Vacuna.query.filter_by(mascota_id=mascota_id).all()
    return render_template('ver_vacunas.html', mascota=mascota, vacunas=vacunas)