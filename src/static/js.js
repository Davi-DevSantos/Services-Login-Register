// ====== Aparência — toggle do painel ======
const coverPanel = document.querySelector(".cover-panel");
const registerLink = document.querySelector("#register-link");
const loginLink = document.querySelector("#login-link");

registerLink.addEventListener("click", (e) => {
    e.preventDefault();
    coverPanel.classList.add("active");
});

loginLink.addEventListener("click", (e) => {
    e.preventDefault();
    coverPanel.classList.remove("active");
});

// ====== Integração com a API ======
const API_BASE = window.location.origin;
const LOGIN_URL = `${API_BASE}/api/v1/auth/login`;
const REGISTER_URL = `${API_BASE}/api/v1/auth/register`;
const REFRESH_URL = `${API_BASE}/api/v1/auth/refresh`;

function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = "fadeOut 0.3s ease forwards";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function showMsg(elementId, text, isError = false) {
    const el = document.getElementById(elementId);
    if (!el) {
        showToast(text, isError ? "error" : "success");
        return;
    }
    el.textContent = text;
    el.className = `msg ${isError ? "error" : "success"} show`;
    // auto-esconde inline após 4s
    clearTimeout(el._hideTimer);
    el._hideTimer = setTimeout(() => {
        el.classList.remove("show");
        // mantém texto para leitura mas esconde visual
    }, 4000);
    // também mostra toast para feedback mais visível
    showToast(text, isError ? "error" : "success");
}

async function handleResponse(response) {
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        const detail = data.detail || JSON.stringify(data) || `Erro ${response.status}`;
        throw new Error(detail);
    }
    return data;
}

async function loginRequest() {
    const email = document.querySelector("#login-email").value.trim();
    const password = document.querySelector("#login-password").value;

    if (!email || !password) {
        showMsg("login-msg", "Preencha email e senha.", true);
        return;
    }

    try {
        const response = await fetch(LOGIN_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });
        const data = await handleResponse(response);
        console.log("Login OK", data);
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        showMsg("login-msg", "Login realizado com sucesso!");
    } catch (error) {
        console.error("Login error:", error);
        showMsg("login-msg", error.message || "Falha no login.", true);
    }
}

async function registerRequest() {
    const username = document.querySelector("#register-username").value.trim();
    const email = document.querySelector("#register-email").value.trim();
    const password = document.querySelector("#register-password").value;
    const confirmPassword = document.querySelector("#register-confirm-password").value;

    if (!username || !email || !password) {
        showMsg("register-msg", "Preencha todos os campos.", true);
        return;
    }
    if (password !== confirmPassword) {
        showMsg("register-msg", "Senhas não conferem.", true);
        return;
    }
    if (password.length < 8) {
        showMsg("register-msg", "Senha deve ter no mínimo 8 caracteres.", true);
        return;
    }

    try {
        const response = await fetch(REGISTER_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password }),
        });
        const data = await handleResponse(response);
        console.log("Register OK", data);
        showMsg("register-msg", "Conta criada! Faça login.");
        // auto alterna para login após sucesso
        setTimeout(() => coverPanel.classList.remove("active"), 800);
    } catch (error) {
        console.error("Register error:", error);
        showMsg("register-msg", error.message || "Falha no cadastro.", true);
    }
}

// Bind dos botões
document.querySelector("#login-btn")?.addEventListener("click", loginRequest);
document.querySelector("#register-btn")?.addEventListener("click", registerRequest);

// Enter para submeter
document.querySelector("#login-password")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") loginRequest();
});
document.querySelector("#register-confirm-password")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") registerRequest();
});

// Fallback legacy: mantém nome antigo exposto globalmente
window.loginreq = loginRequest;
