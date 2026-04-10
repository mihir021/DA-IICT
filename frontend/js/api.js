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
