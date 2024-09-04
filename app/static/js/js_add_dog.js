document.getElementById('birthdate').addEventListener('change', function() {
    const birthdate = new Date(this.value);
    const today = new Date();
    let age = today.getFullYear() - birthdate.getFullYear();
    const m = today.getMonth() - birthdate.getMonth();

    // Ajustar la edad si el mes actual es menor al mes de nacimiento
    // o si el mes es el mismo pero el día actual es menor al día de nacimiento
    if (m < 0 || (m === 0 && today.getDate() < birthdate.getDate())) {
        age--;
    }

    // Mostrar la edad calculada en el campo correspondiente
    document.getElementById('age').value = age;
});



document.getElementById('photo').addEventListener('change', function() {
    var fileName = this.files.length > 0 ? this.files[0].name : 'Ningún archivo seleccionado';
    document.getElementById('file-name').textContent = fileName;
});