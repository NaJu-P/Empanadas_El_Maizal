const loadingText = document.querySelector('.loading-text');
const progress = document.querySelector('.progress');
const loader = document.querySelector('.loader');

let dots = "";
let progressWidth = 0;

const textInterval = setInterval(() => {
    dots = dots.length < 3 ? dots + '.' : '';
    loadingText.textContent = 'Cargando' + dots;
}, 500);

const progressInterval = setInterval(() => {
    progressWidth += 2;
    progress.style.width = progressWidth + '%';

    if (progressWidth >= 100) {
        clearInterval(textInterval);
        clearInterval(progressInterval);
        loadingText.textContent = '¡Bienvenid@ a Empanadas El Maizal!';
        loader.style.display = 'none';

        // Esperar un momento antes de redirigir (opcional)
        setTimeout(() => {
            window.location.href = '../Home/Home.html'; 
        }, 500); 
    }
}, 100);