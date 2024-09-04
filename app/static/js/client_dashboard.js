//Para el saludo inicial de Buenos días, Buenas tardes o Buenas noches
document.addEventListener('DOMContentLoaded', function() {
    // Selecciona el elemento con el ID 'greeting'
    const greetingElement = document.getElementById('greeting');

    // Verifica si el elemento existe
    if (greetingElement) {
        const greetingText = greetingElement.textContent;

        let emoji;
        const currentHour = new Date().getHours();

        // Determina el emoji en función de la hora actual
        if (currentHour < 12) {
            emoji = '🌞'; // Emoji de sol para la mañana
        } else if (currentHour < 18) {
            emoji = '🌤️'; // Emoji de sol con nube para la tarde
        } else {
            emoji = '🌜'; // Emoji de luna para la noche
        }

        // Añade el emoji al texto del saludo
        greetingElement.textContent = `${greetingText} ${emoji}`;
    } else {
        console.error("Elemento con ID 'greeting' no encontrado.");
    }
});

// Sirve para sacar los emojis del Historial de Eventos de mis Perros
document.addEventListener('DOMContentLoaded', function() {
    // Lista de emojis de perros o relacionados con mascotas
    const emojis = ['🐶', '🐕', '🐩', '🐾', '🐕‍🦺'];

    // Selecciona todos los elementos h4 que contienen el nombre del perro
    const dogNameElements = document.querySelectorAll('.dog-name');

    // Asigna un emoji aleatorio a cada nombre de perro
    dogNameElements.forEach(function(element) {
        const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
        element.innerHTML = `${randomEmoji} ${element.textContent}`;
    });
});

// Agregar un efecto de rotación al pasar el ratón
document.querySelectorAll('.dog-image').forEach(function(img) {
    img.addEventListener('mouseover', function() {
        img.style.transform = 'scale(1.1) rotate(5deg)';
    });
    img.addEventListener('mouseout', function() {
        img.style.transform = 'scale(1)';
    });
});

