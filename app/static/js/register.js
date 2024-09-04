    document.addEventListener("DOMContentLoaded", function() {
        const form = document.querySelector("form");
        
        form.addEventListener("submit", function(event) {
            let isValid = true;

            // Clear previous error messages
            const errorMessages = document.querySelectorAll(".error-message");
            errorMessages.forEach(message => message.remove());

            // Remove previous error classes
            const errorFields = document.querySelectorAll(".error");
            errorFields.forEach(field => field.classList.remove("error"));

            // Validate each field
            const fields = form.querySelectorAll("input[required], select[required]");
            fields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    showError(field, "Este campo es obligatorio");
                } else if (field.name === "email" && !validateEmail(field.value.trim())) {
                    isValid = false;
                    showError(field, "Introduce un correo electrónico válido");
                } else if (field.name === "phone" && !validatePhone(field.value.trim())) {
                    isValid = false;
                    showError(field, "Introduce un número de teléfono válido");
                }
                // Puedes añadir más validaciones aquí según sea necesario
            });

            if (!isValid) {
                event.preventDefault();
            }
        });

        function showError(field, message) {
            field.classList.add("error");
            const errorMessage = document.createElement("div");
            errorMessage.classList.add("error-message");
            errorMessage.innerText = message;
            field.parentElement.appendChild(errorMessage);
        }

        function validateEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(String(email).toLowerCase());
        }
       
    });


    document.querySelector('form').addEventListener('submit', function(e) {
        const phone = document.getElementById('phone').value;
        const codePostal = document.getElementById('code_postal').value;
    
        if (!/^\d{9}$/.test(phone)) {
            e.preventDefault();
            alert('El número de teléfono debe tener 9 dígitos.');
        }
    
        if (!/^\d{5}$/.test(codePostal)) {
            e.preventDefault();
            alert('El código postal debe tener 5 dígitos.');
        }
    });



   // Validación de teléfono en tiempo real
   /* document.getElementById('phone').addEventListener('input', function() {
        const phoneInput = this.value;
        const phoneError = document.getElementById('phoneError');
        
        // Expresión regular para validar el número de teléfono (solo dígitos, opcionalmente con espacios, guiones o paréntesis)
        const phonePattern = /^[0-9\s\-()]+$/;

        if (!phonePattern.test(phoneInput)) {
            phoneError.textContent = 'Por favor, introduce un número de teléfono válido.';
        } else {
            phoneError.textContent = ''; // Limpiar mensaje de error si es válido
        }
    });
*/
