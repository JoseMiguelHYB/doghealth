const textElement = document.getElementById('dynamicText');
const subTextElement = document.getElementById('dynamicSubText');

const texts = [
    { 
        title: "Tu compañero peludo, siempre protegido.", 
        subtext: "Gestionamos sus vacunas, para una vida saludable." 
    },
    { 
        title: "Cuidamos su salud, para cuidar tu tranquilidad.", 
        subtext: "Recordatorios de medicamentos para tu mejor amigo." 
    },
    { 
        title: "Nunca más olvides una cita importante.", 
        subtext: "Organiza sus visitas al veterinario sin complicaciones." 
    },
    { 
        title: "Un aliado en el bienestar de tu perro.", 
        subtext: "Nos ocupamos de sus cuidados, tú solo disfruta su compañía." 
    },
    { 
        title: "Mantén a tu perro feliz y saludable.", 
        subtext: "Vacunas, medicación y más, todo en un solo lugar." 
    }
];

let index = 0;
let charIndex = 0;
let isTitle = true;

function typeText() {
    const currentText = isTitle ? texts[index].title : texts[index].subtext;
    const currentElement = isTitle ? textElement : subTextElement;

    // Agregar la siguiente letra al elemento actual
    currentElement.textContent += currentText[charIndex];
    charIndex++;

    // Si hemos terminado de escribir el texto actual
    if (charIndex === currentText.length) {
        // Pasar al siguiente texto (title -> subtext o subtext -> title)
        if (isTitle) {
            charIndex = 0;
            isTitle = false;
            setTimeout(typeText, 600); // Esperar un poco antes de escribir el subtexto
        } else {
            setTimeout(() => {
                fadeOutText();
            }, 1000); // Esperar un poco más antes de comenzar el desvanecimiento
        }
    } else {
        setTimeout(typeText, 50); // Intervalo para la siguiente letra
    }
}

function fadeOutText() {
    textElement.classList.add('fade-out');
    subTextElement.classList.add('fade-out');

    // Esperar a que la animación de desvanecimiento termine
    setTimeout(nextText, 1000); // 1 segundo para el efecto de desvanecimiento
}

function nextText() {
    // Restablecer el estado para el siguiente texto
    charIndex = 0;
    isTitle = true;
    index = (index + 1) % texts.length;

    // Limpiar el contenido anterior y eliminar la clase de desvanecimiento
    textElement.textContent = '';
    subTextElement.textContent = '';
    textElement.classList.remove('fade-out');
    subTextElement.classList.remove('fade-out');

    // Comenzar a escribir el siguiente texto
    typeText();
}

// Iniciar el efecto de escritura al cargar la página
typeText();


/*aleatoria los emjos de perritos*/
// Selecciona el span donde se mostrará el emoticono
const emojiElement = document.getElementById('dogEmoji');

// Lista de emoticonos que deseas usar
const emojis = ["🐕", "🦮", "🐶", "🐩", "🐕‍🦺", "🐾"];

// Función para cambiar el emoticono
function changeEmoji() {
    // Selecciona un emoticono aleatorio de la lista
    const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
    // Actualiza el contenido del span con el nuevo emoticono
    emojiElement.textContent = randomEmoji;
}

// Cambia el emoticono cada 2 segundos (2000 ms)
setInterval(changeEmoji, 2000);