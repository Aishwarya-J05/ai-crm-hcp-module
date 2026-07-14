const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return response.json();
}

export const api = {
  listInteractions: () => request("/api/interactions"),
  createInteraction: (payload) =>
    request("/api/interactions", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  chat: (message) =>
    request("/api/agent/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
};
