document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es', // Cambia el idioma a español
        events: [
            // Aquí añadimos dinámicamente los eventos del perro
            {% for dogEvent in dog.events %}
            {
                title: getEventTitleWithEmoji('{{ dogEvent.event_type }}', '{{ dogEvent.description }}'),
                start: '{{ dogEvent.event_date.strftime('%Y-%m-%dT%H:%M:%S') }}',
                color: '#007bff' // Ajusta el color según tu necesidad
            },
            {% endfor %}
        ]
    });
    calendar.render();
});

/**
 * Función para añadir emojis según el tipo de evento
 */
function getEventTitleWithEmoji(eventType, description) {
    let emoji = '';
    switch (eventType.toLowerCase()) {
        case 'corte de pelo':
            emoji = '✂️'; // Tijeras
            break;
        case 'test de insulina':
            emoji = '💉'; // Jeringuilla
            break;
        case 'revisión':
            emoji = '👁️'; // Ojo
            break;
        case 'limpieza de dientes':
            emoji = '🪥'; // Cepillo de dientes
            break;
        // Añade más casos según sea necesario
        default:
            emoji = ''; // Sin emoji si no coincide
    }
    return emoji + ' ' + description; // Devuelve el título con el emoji
}
