export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type CurrentUser = {
  id: number;
  username: string;
  email?: string | null;
  phone?: string | null;
  role: "USER" | "CUSTOMER_SERVICE" | "ADMIN" | string;
};

export type ChatResponse = {
  conversation_id: number;
  answer: string;
  intent?: string | null;
  sources?: string[] | null;
};

export type TraceStep = {
  id: number;
  node_name: string;
  input_data?: Record<string, unknown> | null;
  output_data?: Record<string, unknown> | null;
  duration_ms?: number | null;
};

export type TraceRun = {
  id: number;
  conversation_id: number;
  query: string;
  intent?: string | null;
  status: string;
  latency_ms?: number | null;
  confidence?: number | null;
  created_at?: string | null;
  steps: TraceStep[];
};

export type ApprovalTask = {
  id: number;
  type: string;
  target_id: number;
  risk_level: string;
  status: string;
  created_at?: string | null;
};

export type ApprovalActionResponse = {
  id: number;
  status: string;
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

export async function getCurrentUser(token: string): Promise<CurrentUser> {
  const response = await fetch(`${API_BASE_URL}/api/users/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return parseJson<CurrentUser>(response);
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

function authHeaders(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

export async function listTraces(token: string): Promise<TraceRun[]> {
  const response = await fetch(`${API_BASE_URL}/api/admin/traces`, {
    headers: authHeaders(token),
  });
  return parseJson<TraceRun[]>(response);
}

export async function getTrace(token: string, runId: number): Promise<TraceRun> {
  const response = await fetch(`${API_BASE_URL}/api/admin/traces/${runId}`, {
    headers: authHeaders(token),
  });
  return parseJson<TraceRun>(response);
}

export async function listApprovals(token: string): Promise<ApprovalTask[]> {
  const response = await fetch(`${API_BASE_URL}/api/admin/approvals`, {
    headers: authHeaders(token),
  });
  return parseJson<ApprovalTask[]>(response);
}

export async function approveTask(
  token: string,
  approvalId: number,
): Promise<ApprovalActionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/admin/approvals/${approvalId}/approve`, {
    method: "POST",
    headers: authHeaders(token),
  });
  return parseJson<ApprovalActionResponse>(response);
}

export async function rejectTask(
  token: string,
  approvalId: number,
): Promise<ApprovalActionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/admin/approvals/${approvalId}/reject`, {
    method: "POST",
    headers: authHeaders(token),
  });
  return parseJson<ApprovalActionResponse>(response);
}
