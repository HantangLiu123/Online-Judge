const BASE_URL = '/api';

async function request(url, options = {}) {
    const res = await fetch(`${BASE_URL}${url}`, {
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        },
        ...options,
    });

    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.message || 'Network response was not ok');
    }

    return res.json();
}

export default {
    get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        return request(fullUrl, {
            method: 'GET',
        });
    },
    post(url, data = {}) {
        return request(url, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },
    put(url, data = {}) {
        return request(url, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
    delete(url) {
        return request(url, {
            method: 'DELETE',
        });
    },
}