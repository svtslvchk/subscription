document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    let currentUser = null;

    if (token) {
        fetch("/auth/me", {
            headers: { Authorization: "Bearer " + token }
        })
        .then(res => res.json())
        .then(user => {
            currentUser = user;
            showUIAfterLogin(user);
        });
    }

    document.getElementById("register-form").addEventListener("submit", async e => {
        e.preventDefault();
        const data = {
            username: document.getElementById("reg-username").value,
            email: document.getElementById("reg-email").value,
            password: document.getElementById("reg-password").value
        };
        await fetch("/users/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        alert("Пользователь создан! Теперь войдите.");
    });

    document.getElementById("login-form").addEventListener("submit", async e => {
        e.preventDefault();
        const formData = new URLSearchParams();
        formData.append("username", document.getElementById("login-username").value);
        formData.append("password", document.getElementById("login-password").value);

        const res = await fetch("/auth/token", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData
        });

        const result = await res.json();
        localStorage.setItem("token", result.access_token);

        const userRes = await fetch("/auth/me", {
            headers: { Authorization: "Bearer " + result.access_token }
        });
        const user = await userRes.json();
        currentUser = user;
        showUIAfterLogin(user);
    });

    document.getElementById("logout-btn").addEventListener("click", () => {
        localStorage.removeItem("token");
        location.reload();
    });

    document.getElementById("create-subscription-form")?.addEventListener("submit", async e => {
        e.preventDefault();
        const data = {
            name: document.getElementById("sub-name").value,
            price: parseFloat(document.getElementById("sub-price").value),
            duration_days: parseInt(document.getElementById("sub-days").value),
        };
        await fetch("/subscriptions/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + localStorage.getItem("token")
            },
            body: JSON.stringify(data)
        });
        alert("Подписка создана");
        loadSubscriptions(currentUser);
    });

    document.getElementById("topup-form")?.addEventListener("submit", async e => {
        e.preventDefault();
        const token = localStorage.getItem("token");

        const data = {
            amount: parseFloat(document.getElementById("topup-amount").value),
            description: document.getElementById("topup-desc").value
        };

        const res = await fetch("/wallet/topup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            },
            body: JSON.stringify(data)
        });

        if (res.ok) {
            alert("Баланс пополнен!");
            document.getElementById("topup-form").reset();
            loadWallet();
        } else {
            const err = await res.json();
            alert("Ошибка: " + err.detail);
        }
    });

    document.getElementById("withdraw-form")?.addEventListener("submit", async e => {
        e.preventDefault();
        const token = localStorage.getItem("token");

        const data = {
            amount: parseFloat(document.getElementById("withdraw-amount").value),
            description: document.getElementById("withdraw-desc").value
        };

        const res = await fetch("/wallet/withdraw", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            },
            body: JSON.stringify(data)
        });

        if (res.ok) {
            alert("Средства успешно списаны!");
            document.getElementById("withdraw-form").reset();
            loadWallet();
        } else {
            const err = await res.json();
            alert("Ошибка: " + err.detail);
        }
    });

    document.getElementById("pay-subscription-form")?.addEventListener("submit", async e => {
        e.preventDefault();

        const token = localStorage.getItem("token");

        const data = {
            subscription_id: parseInt(document.getElementById("pay-subscription-id").value),
            amount: parseFloat(document.getElementById("pay-amount").value),
            payment_method: document.getElementById("payment-method").value
        };

        const res = await fetch("/payments/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (res.ok) {
            alert("Подписка успешно оплачена!");
            document.getElementById("pay-subscription-form").reset();
            loadWallet();  // обновим баланс
        } else {
            alert("Ошибка: " + result.detail);
        }
    });

    document.getElementById("refund-form")?.addEventListener("submit", async e => {
        e.preventDefault();
        const token = localStorage.getItem("token");

        const data = {
            reason: document.getElementById("refund-reason").value
        };

        const paymentId = document.getElementById("refund-payment-id").value;

        const res = await fetch(`/payments/${paymentId}/refund`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + token
            },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (res.ok) {
            alert("Средства возвращены!");
            document.getElementById("refund-form").reset();
            loadWallet();  // обновим баланс
        } else {
            alert("Ошибка: " + result.detail);
        }
    });

});

function showUIAfterLogin(user) {
    document.getElementById("register-form").style.display = "none";
    document.getElementById("login-form").style.display = "none";
    document.getElementById("logout-btn").style.display = "block";

    if (user.role === "admin") {
        document.getElementById("admin-panel").style.display = "block";
        document.getElementById("subscription-requests").style.display = "block";
        document.getElementById("wallet-section").style.display = "none";
        document.getElementById("payment-history-section").style.display = "none";
        document.getElementById("pay-subscription-form").style.display = "none";  // ❌ скрыть для админа
        loadSubscriptionRequests();
    } else {
        document.getElementById("wallet-section").style.display = "block";
        document.getElementById("payment-history-section").style.display = "block";
        document.getElementById("pay-subscription-form").style.display = "block"; // ✅ показать для пользователя
        loadWallet();
        loadPaymentHistory();
    }

    document.getElementById("subscriptions-section").style.display = "block";
    loadSubscriptions(user);
    loadUserSubscriptions();
}



async function loadSubscriptions(user) {
    const res = await fetch("/subscriptions/?active_only=true");
    const subs = await res.json();
    const list = document.getElementById("subscription-list");
    list.innerHTML = "";

    const userSubRes = await fetch("/user-subscriptions/me", {
        headers: { Authorization: "Bearer " + localStorage.getItem("token") }
    });
    const userSubs = await userSubRes.json();

    for (const sub of subs) {
        const li = document.createElement("li");
        li.innerHTML = `<strong>${sub.name}</strong> — ${sub.price}₽ на ${sub.duration_days} дней`;

        if (user?.role === "admin") {
            const editBtn = document.createElement("button");
            editBtn.textContent = "✏️";
            editBtn.onclick = () => editSubscription(sub.id);
            li.appendChild(editBtn);

            const deleteBtn = document.createElement("button");
            deleteBtn.textContent = "🗑";
            deleteBtn.onclick = () => deleteSubscription(sub.id);
            li.appendChild(deleteBtn);

            const assignBtn = document.createElement("button");
            assignBtn.textContent = "Выдать себе";
            assignBtn.onclick = () => assignSubscriptionToSelf(sub.id);
            li.appendChild(assignBtn);
        } else {
            const userHasSub = userSubs.find(s => s.subscription_id === sub.id);

            if (!userHasSub) {
                const reqBtn = document.createElement("button");
                reqBtn.textContent = "Запросить доступ";
                reqBtn.onclick = () => requestAccess(sub.id);
                li.appendChild(reqBtn);
            } else if (!userHasSub.is_active) {
                const payBtn = document.createElement("button");
                payBtn.textContent = "Оплатить";
                payBtn.onclick = () => {
                    document.getElementById("pay-subscription-id").value = sub.id;
                    document.getElementById("pay-amount").value = sub.price;
                    document.getElementById("pay-subscription-form").scrollIntoView({ behavior: "smooth" });
                };
                li.appendChild(payBtn);
            }
        }

        list.appendChild(li);
    }
}





function editSubscription(id) {
    const name = prompt("Новое название:");
    const price = prompt("Новая цена:");
    const duration = prompt("Длительность в днях:");

    if (!name || !price || !duration) return alert("Все поля обязательны");

    fetch(`/subscriptions/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token")
        },
        body: JSON.stringify({
            name: name,
            price: parseFloat(price),
            duration_days: parseInt(duration)
        })
    })
    .then(res => {
        if (!res.ok) throw new Error("Ошибка обновления");
        return res.json();
    })
    .then(() => {
        alert("Подписка обновлена");
        location.reload();
    })
    .catch(err => {
        alert("Ошибка: " + err.message);
    });
}

function deleteSubscription(id) {
    if (!confirm("Удалить подписку?")) return;

    fetch(`/subscriptions/${id}`, {
        method: "DELETE",
        headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
        }
    })
    .then(res => {
        if (!res.ok) throw new Error("Ошибка удаления");
        alert("Удалено");
        location.reload();
    })
    .catch(err => {
        alert("Ошибка: " + err.message);
    });
}

async function loadWallet() {
    const token = localStorage.getItem("token");

    // Получение баланса
    const balanceRes = await fetch("/wallet/balance", {
        headers: { Authorization: "Bearer " + token }
    });
    const balance = await balanceRes.json();
    document.getElementById("balance-amount").textContent = balance.toFixed(2);

    // Получение истории
    const historyRes = await fetch("/wallet/history", {
        headers: { Authorization: "Bearer " + token }
    });
    const history = await historyRes.json();
    const list = document.getElementById("wallet-history-list");
    list.innerHTML = "";

    history.forEach(entry => {
        const li = document.createElement("li");
        li.textContent = `${entry.type === "topup" ? "➕" : "➖"} ${entry.amount}₽ — ${entry.description || ""} (${new Date(entry.created_at).toLocaleString()})`;
        list.appendChild(li);
    });
}

async function loadPaymentHistory() {
    const token = localStorage.getItem("token");
    const res = await fetch("/payments/", {
        headers: { Authorization: "Bearer " + token }
    });
    const payments = await res.json();

    const list = document.getElementById("payment-history-list");
    list.innerHTML = "";
    payments.forEach(p => {
        const li = document.createElement("li");
        li.textContent = `id:${p.id}: ${p.amount}₽ за подписку #${p.subscription_id}, метод: ${p.payment_method}, статус: ${p.status}`;
        list.appendChild(li);
    });
}

async function requestAccess(subId) {
    const res = await fetch("/subscription-requests/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token")
        },
        body: JSON.stringify({ subscription_id: subId })
    });

    if (res.ok) {
        alert("Запрос отправлен!");
    } else {
        const data = await res.json();
        alert("Ошибка: " + data.detail);
    }
}

async function loadSubscriptionRequests() {
    const res = await fetch("/subscription-requests/admin", {
        headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
        }
    });

    if (!res.ok) {
        console.error("Ошибка при получении запросов на подписки");
        return;
    }

    const requests = await res.json();
    const list = document.getElementById("request-list");
    list.innerHTML = "";

    if (requests.length === 0) {
        list.innerHTML = "<li>Нет запросов</li>";
        return;
    }

    const pendingRequests = requests.filter(req => req.status === "pending");

    if (pendingRequests.length === 0) {
        list.innerHTML = "<li>Нет новых запросов</li>";
        return;
    }

    pendingRequests.forEach(req => {
        const li = document.createElement("li");
        li.innerHTML = `
            <strong>Пользователь #${req.user_id}</strong> запросил подписку #${req.subscription_id} 
            <button onclick="approveRequest(${req.id})">Одобрить</button>
            <button onclick="rejectRequest(${req.id})">Отклонить</button>
        `;
        list.appendChild(li);
    });

}



async function approveRequest(id) {
    const res = await fetch(`/subscription-requests/admin/${id}/approve`, {
        method: "PATCH",  // ← вот здесь исправляем
        headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
        }
    });

    if (res.ok) {
        alert("Запрос одобрен");
        loadSubscriptionRequests();
    } else {
        const data = await res.json();
        alert("Ошибка: " + data.detail);
    }
}

async function rejectRequest(id) {
    const res = await fetch(`/subscription-requests/admin/${id}/reject`, {
        method: "PATCH",  // ← и здесь тоже
        headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
        }
    });

    if (res.ok) {
        alert("Запрос отклонён");
        loadSubscriptionRequests();
    } else {
        const data = await res.json();
        alert("Ошибка: " + data.detail);
    }
}

async function getUserSubscriptions() {
    const token = localStorage.getItem("token");
    const res = await fetch("/user-subscriptions/me", {
        headers: { Authorization: "Bearer " + token }
    });
    return await res.json();
}

async function loadUserSubscriptions() {
    const token = localStorage.getItem("token");
    const res = await fetch("/user-subscriptions/me", {
        headers: { Authorization: "Bearer " + token }
    });

    if (!res.ok) return;

    const data = await res.json();
    const list = document.getElementById("active-subscriptions-list");
    list.innerHTML = "";

    data.forEach(s => {
        if (s.is_active) {
            const li = document.createElement("li");
            li.textContent = `Подписка: ${s.subscription?.name || "Без названия"}, до ${s.end_date || "∞"}`;

            list.appendChild(li);
        }
    });

    document.getElementById("my-active-subscriptions").style.display = "block";
}

async function assignSubscriptionToSelf(subscriptionId) {
    const token = localStorage.getItem("token");

    const res = await fetch("/user-subscriptions/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + token
        },
        body: JSON.stringify({
            subscription_id: subscriptionId,
            auto_renew: false
        })
    });

    if (res.ok) {
        alert("Подписка выдана себе!");
        loadUserSubscriptions();
    } else {
        const err = await res.json();
        alert("Ошибка: " + err.detail);
    }
}
