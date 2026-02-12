const API = "http://127.0.0.1:8000";

function saveToken(token) {
    localStorage.setItem("token", token);
    document.getElementById("auth-box").style.display = "none";
    document.getElementById("chat-box").style.display = "block";
}

async function signup() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${API}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    saveToken(data.access_token);
}

async function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    console.log("LOGIN DATA:", { email, password }); // DEBUG

    const res = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    });

    const data = await res.json();
    console.log("LOGIN RESPONSE:", data);

    if (!res.ok) {
        alert(data.detail || "Login failed");
        return;
    }

    localStorage.setItem("token", data.access_token);
    alert("Login successful");
}

function logout() {
    localStorage.removeItem("token");
    location.reload();
}

window.onload = () => {
    const token = localStorage.getItem("token");
    if (token) {
        document.getElementById("auth-box").style.display = "none";
        document.getElementById("chat-box").style.display = "block";
    }
};