let token = localStorage.getItem("token");
let isAdmin = false;

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const logoutBtn = document.getElementById("logout-btn");
    const depositForm = document.getElementById("deposit-form");
    const withdrawForm = document.getElementById("withdraw-form");

    if (token) {
        fetchUserData();
    }

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const res = await fetch("/token", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });

        if (res.ok) {
            const data = await res.json();
            token = data.access_token;
            localStorage.setItem("token", token);
            fetchUserData();
        } else {
            document.getElementById("login-error").textContent = "Неверный логин или пароль";
        }
    });

    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("token");
        location.reload();
    });

    depositForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const amount = parseFloat(document.getElementById("deposit-amount").value);
        await modifyWallet("/wallet/deposit", amount);
    });

    withdrawForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const amount = parseFloat(document.getElementById("withdraw-amount").value);
        await modifyWallet("/wallet/withdraw", amount);
    });
});

async function fetchPaymentHistory() {
    const res = await fetch("/payments/history", {
        headers: { Authorization: `Bearer ${token}` }
    });

    const list = document.getElementById("payment-history-list");
    list.innerHTML = "";

    if (res.ok) {
        const payments = await res.json();
        if (payments.length === 0) {
            list.innerHTML = "<li>История пуста</li>";
        } else {
            for (const p of payments) {
                const li = document.createElement("li");
                li.textContent = `${p.amount}₽ — ${new Date(p.timestamp).toLocaleString()}` +
                                 (p.subscription_name ? ` (подписка: ${p.subscription_name})` : "");
                list.appendChild(li);
            }
        }
    } else {
        list.innerHTML = "<li>Не удалось загрузить историю</li>";
    }
}

async function fetchUserData() {
    const res = await fetch("/users/me", {
        headers: { Authorization: `Bearer ${token}` }
    });

    if (res.ok) {
        const user = await res.json();
        isAdmin = user.is_admin;
        document.getElementById("user-name").textContent = user.username;
        document.getElementById("login-section").style.display = "none";
        document.getElementById("main-content").style.display = "block";

        if (isAdmin) {
            document.getElementById("admin-panel").style.display = "block";
        }

        fetchWalletBalance();
        fetchSubscriptions();
    } else {
        localStorage.removeItem("token");
    }

    fetchPaymentHistory();
}

async function fetchWalletBalance() {
    const res = await fetch("/wallet/balance", {
        headers: { Authorization: `Bearer ${token}` }
    });

    if (res.ok) {
        const data = await res.json();
        document.getElementById("wallet-balance").textContent = data.balance.toFixed(2);
    } else {
        document.getElementById("wallet-error").textContent = "Не удалось получить баланс";
    }
}

async function modifyWallet(endpoint, amount) {
    const res = await fetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ amount })
    });

    if (res.ok) {
        document.getElementById("wallet-error").textContent = "";
        fetchWalletBalance();
    } else {
        const data = await res.json();
        document.getElementById("wallet-error").textContent = data.detail || "Ошибка";
    }
}

async function fetchSubscriptions() {
    const res = await fetch("/subscriptions", {
        headers: { Authorization: `Bearer ${token}` }
    });

    const list = document.getElementById("subscriptions-list");
    list.innerHTML = "";

    if (res.ok) {
        const subs = await res.json();
        for (const s of subs) {
            const li = document.createElement("li");
            li.textContent = `${s.name} — ${s.price}₽ / ${s.interval_days} дней. Следующий платеж: ${s.next_payment_date || "—"}`;
            list.appendChild(li);
        }
    } else {
        list.innerHTML = "<li>Ошибка загрузки подписок</li>";
    }
}
