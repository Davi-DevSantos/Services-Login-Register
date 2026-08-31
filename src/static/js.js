const coverPanel = document.querySelector('.cover-panel');
const registerLink = document.querySelector('#register-link');

registerLink.addEventListener('click', (e) => {
    e.preventDefault();
    coverPanel.classList.add('active');
});