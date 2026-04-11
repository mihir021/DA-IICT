const BASE_URL = "http://localhost:8000";


async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || "Request failed.");
  }
  return payload;
}


export async function loginAdmin(email, password) {
  return request("/api/admin/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}


export async function fetchAdminDashboard(token, range = "7d") {
  return request(`/api/admin/dashboard/summary?range=${range}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}


export async function fetchOperationsSummary(token, range = "7d") {
  return request(`/api/admin/operations/summary?range=${range}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}


export async function fetchUserInsights(token) {
  return request("/api/admin/users/insights", {
    headers: { Authorization: `Bearer ${token}` },
  });
}


export async function fetchAdminLogs(token) {
  return request("/api/admin/admin-logs", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

// Team merge helpers for storefront/auth pages.
function authHeaders() {
  if (typeof window === "undefined") return {};
  const token = window.localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function signupUser(data) {
  return request("/api/auth/signup/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function loginUser(data) {
  const payload = await request("/api/auth/login/", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (typeof window !== "undefined" && payload?.token) {
    window.localStorage.setItem("token", payload.token);
    if (payload.name) window.localStorage.setItem("user_name", payload.name);
  }
  return payload;
}

export function logoutUser() {
  if (typeof window === "undefined") return;
  window.localStorage.clear();
}

export async function fetchStoreProducts(search = "", category = "All") {
  const q = new URLSearchParams({ search, category }).toString();
  const response = await fetch(`${BASE_URL}/api/auth/products/?${q}`);
  return response.json();
}

export async function fetchBestSellers() {
  const response = await fetch(`${BASE_URL}/api/auth/products/best-sellers/`);
  return response.json();
}

export async function fetchOffers() {
  const response = await fetch(`${BASE_URL}/api/auth/products/offers/`);
  return response.json();
}

export async function fetchProfile() {
  return request("/api/profile/profile/", { headers: authHeaders() });
}

export async function updateProfile(data) {
  return request("/api/profile/profile/", {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
}

export async function fetchOrders() {
  return request("/api/orders/orders/", { headers: authHeaders() });
}

export async function fetchExpenses() {
  return request("/api/expenses/expenses/", { headers: authHeaders() });
}

export async function addExpense(data) {
  return request("/api/expenses/expenses/", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
}

export async function fetchExpenseGraph(type) {
  return request(`/api/expenses/expense-graph/${type}/`, {
    headers: authHeaders(),
  });
}
