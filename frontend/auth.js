
const API_URL = "http://127.0.0.1:5000";

// ================= REGISTER =================

const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const name = document.getElementById("registerName").value.trim();
        const email = document.getElementById("registerEmail").value.trim();
        const password = document.getElementById("registerPassword").value;
        const confirm = document.getElementById("confirmPassword").value;

        const message = document.getElementById("registerMessage");
        const button = document.getElementById("registerButton");

        if (password !== confirm) {
            message.textContent = "Passwords do not match!";
            message.style.color = "red";
            return;
        }

        button.disabled = true;
        button.textContent = "Creating Account...";

        try {
            const response = await fetch(`${API_URL}/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || data.error || "Registration failed");
            }

            message.textContent = "Registration successful! Please login.";
            message.style.color = "green";

            registerForm.reset();

        } catch (error) {
            message.textContent = error.message;
            message.style.color = "red";

        } finally {
            button.disabled = false;
            button.textContent = "Create My Account →";
        }
    });
}


// ================= LOGIN =================

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const email = document.getElementById("loginEmail").value.trim();
        const password = document.getElementById("loginPassword").value;

        const message = document.getElementById("loginMessage");
        const button = document.getElementById("loginButton");

        button.disabled = true;
        button.textContent = "Logging in...";

        try {
            const response = await fetch(`${API_URL}/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || data.error || "Login failed");
            }

            message.textContent = "Login successful!";
            message.style.color = "green";

            // Current backend returns a success message,
            // but does not yet establish a browser session.
            setTimeout(() => {
                window.location.href = "index.html";
            }, 1000);

        } catch (error) {
            message.textContent = error.message;
            message.style.color = "red";

        } finally {
            button.disabled = false;
            button.textContent = "Login to Account →";
        }
    });
}
