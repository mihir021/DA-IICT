const BASE_URL = 'http://localhost:8000/api';

const api = {
    signup: async (userData) => {
        const response = await fetch(`${BASE_URL}/signup/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        return await response.json();
    },
    login: async (credentials) => {
        const response = await fetch(`${BASE_URL}/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
        });
        const data = await response.json();
        if (data.token) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user_name', data.name);
        }
        return data;
    },
    getProfile: async () => {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}/profile/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.status === 401) throw { status: 401 };
        return await response.json();
    },
    getProducts: async () => {
        const response = await fetch(`${BASE_URL}/products/`);
        return await response.json();
    }
};

export default api;
