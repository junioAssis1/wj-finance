function formatBRL(value) {
    if (value === null || value === undefined) return "R$ 0,00";
    return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatDate(dateStr) {
    if (!dateStr) return "-";
    const parts = dateStr.split('-');
    if (parts.length === 3) {
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
    }
    return dateStr;
}

async function apiFetch(url, options = {}) {
    options.headers = options.headers || {};
    if (!options.headers['Content-Type'] && !(options.body instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
    }

    try {
        const res = await fetch(url, options);
        if (res.status === 401) {
            window.location.href = '/login';
            return null;
        }
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || 'Ocorreu um erro na requisição.');
        }
        return data;
    } catch (err) {
        alert(err.message);
        throw err;
    }
}

async function logout() {
    await fetch('/auth/logout', { method: 'POST' });
    window.location.href = '/login';
}
