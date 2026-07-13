export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type ChatResponse = {
  conversation_id: number;
  answer: string;
  intent?: string | null;
  sources?: string[] | null;
};

export type ApiError = {
  detail?: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const error = data as ApiError;
    throw new Error(error.detail ?? `Request failed: ${response.status}`);
  }
  return data as T;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });
  return parseJson<LoginResponse>(response);
}

export async function sendChatMessage(
  token: string,
  message: string,
  conversationId: number | null,
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
  });
  return parseJson<ChatResponse>(response);
}
