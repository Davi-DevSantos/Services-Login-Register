// ====== Aparence ======

const overl = document.querySelector('.cover-panel');
const registerLink = document.querySelector('#register-link');
const loginLink = document.querySelector('#login-link');

registerLink.addEventListener('click', (e) => {
    // document.querySelector('.cover-panel').classList.toggle('active');
    overl.classList.toggle('active');
});

loginLink.addEventListener('click', (e) => {
    // document.querySelector('.cover-panel').classList.toggle('active');
    overl.classList.toggle('active');
});

// ==== Integration ======
async function loginreq() {
    const response = await fetch('http://localhost:3000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: document.querySelector('#email').value,
            password: document.querySelector('#password').value
        })
    });
        

    const data = await response.json();
    console.log(data);
}