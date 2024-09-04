document.getElementById('loginForm').addEventListener('submit', function(event) {
    let isValid = true;

    // Validar el campo de nombre de usuario
    const username = document.getElementById('username').value;
    const usernameError = document.getElementById('usernameError');
    if (username.trim() === "") {
        usernameError.textContent = "Campo obligatorio";
        isValid = false;
    } else {
        usernameError.textContent = "";
    }

    // Validar el campo de contraseña , CAMBIA, LO CAMBIAMOS A TAMAÑO 1 SOLO PARA DEPURAR CON FACILIDAD
    const password = document.getElementById('password').value;
    const passwordError = document.getElementById('passwordError');
    if (password.length < 0 || password.length > 100) {
        passwordError.textContent = "La contraseña debe tener entre 6 y 100 caracteres";
        isValid = false;
    } else {
        passwordError.textContent = "";
    }

    // Prevenir el envío del formulario si hay errores
    if (!isValid) {
        event.preventDefault();
    }
});