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
  error_message?: string | null;
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
  error_message?: string | null;
  steps?: TraceStep[] | null;
  tool_logs?: ToolLog[] | null;
};

export type ToolLog = {
  id: number;
  tool_name: string;
  input_data?: Record<string, unknown> | null;
  output_data?: Record<string, unknown> | null;
  status: string;
  latency_ms?: number | null;
  created_at?: string | null;
  error_message?: string | null;
};

export type ApprovalTask = {
  id: number;
  type: string;
  target_id: number;
  risk_level: string;
  status: string;
  created_at?: string | null;
  operator_id?: number | null;
  operator_username?: string | null;
  comment?: string | null;
  refund_id?: number | null;
  refund_reason?: string | null;
  refund_amount?: number | null;
  refund_status?: string | null;
  order_id?: number | null;
  order_no?: string | null;
  order_status?: string | null;
  payment_status?: string | null;
  user_id?: number | null;
  username?: string | null;
};

export type ApprovalActionResponse = {
  id: number;
  status: string;
  comment?: string | null;
};

export type ListQuery = {
  status?: string;
  role?: string;
  limit?: number;
  offset?: number;
};

export type ConversationMessage = {
  id: number;
  conversation_id: number;
  role: string;
  content: string;
  sources?: string | null;
  timestamp?: string | null;
};

export type ConversationSummary = {
  id: number;
  user_id: number;
  username: string;
  user_email?: string | null;
  user_phone?: string | null;
  title?: string | null;
  status: string;
  created_at?: string | null;
  updated_at?: string | null;
  last_message_at?: string | null;
  last_message_role?: string | null;
  last_message_preview?: string | null;
  message_count: number;
};

export type ConversationDetail = ConversationSummary & {
  messages: ConversationMessage[];
};

export type UserSummary = {
  id: number;
  username: string;
  email?: string | null;
  phone?: string | null;
  role: string;
  is_active: boolean;
  created_at?: string | null;
  updated_at?: string | null;
};

export type ApiError = {
  detail?: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};
  if (!response.ok) {
    if (response.status === 401 && typeof window !== "undefined") {
      window.localStorage.removeItem("agent_token");
      window.localStorage.removeItem("agent_conversation_id");
      window.dispatchEvent(new Event("agent-auth-expired"));
    }
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

function buildQuery(params?: ListQuery): string {
  if (!params) {
    return "";
  }
  const query = new URLSearchParams();
  if (params.status) {
    query.set("status", params.status);
  }
  if (params.role) {
    query.set("role", params.role);
  }
  if (params.limit !== undefined) {
    query.set("limit", String(params.limit));
  }
  if (params.offset !== undefined) {
    query.set("offset", String(params.offset));
  }
  const value = query.toString();
  return value ? `?${value}` : "";
}

export async function listTraces(token: string, query?: ListQuery): Promise<TraceRun[]> {
  const response = await fetch(`${API_BASE_URL}/api/admin/traces${buildQuery(query)}`, {
    headers: authHeaders(token),
  });
  const runs = await parseJson<TraceRun[]>(response);
  return runs.map(normalizeTraceRun);
}

export async function getTrace(token: string, runId: number): Promise<TraceRun> {
  const response = await fetch(`${API_BASE_URL}/api/admin/traces/${runId}`, {
    headers: authHeaders(token),
  });
  return normalizeTraceRun(await parseJson<TraceRun>(response));
}

function normalizeTraceRun(run: TraceRun): TraceRun {
  return {
    ...run,
    steps: run.steps ?? [],
    tool_logs: run.tool_logs ?? [],
  };
}

export async function listApprovals(token: string, query?: ListQuery): Promise<ApprovalTask[]> {
  const response = await fetch(`${API_BASE_URL}/api/admin/approvals${buildQuery(query)}`, {
    headers: authHeaders(token),
  });
  return parseJson<ApprovalTask[]>(response);
}

export async function listConversations(
  token: string,
  query?: ListQuery,
): Promise<ConversationSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/admin/conversations${buildQuery(query)}`, {
    headers: authHeaders(token),
  });
  return parseJson<ConversationSummary[]>(response);
}

export async function getConversation(token: string, conversationId: number): Promise<ConversationDetail> {
  const response = await fetch(`${API_BASE_URL}/api/admin/conversations/${conversationId}`, {
    headers: authHeaders(token),
  });
  const detail = await parseJson<ConversationDetail>(response);
  return { ...detail, messages: detail.messages ?? [] };
}

export async function listUsers(token: string, query?: ListQuery): Promise<UserSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/admin/users${buildQuery(query)}`, {
    headers: authHeaders(token),
  });
  return parseJson<UserSummary[]>(response);
}

export async function approveTask(
  token: string,
  approvalId: number,
  comment?: string,
): Promise<ApprovalActionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/admin/approvals/${approvalId}/approve`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ comment: comment?.trim() || null }),
  });
  return parseJson<ApprovalActionResponse>(response);
}

export async function rejectTask(
  token: string,
  approvalId: number,
  comment?: string,
): Promise<ApprovalActionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/admin/approvals/${approvalId}/reject`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ comment: comment?.trim() || null }),
  });
  return parseJson<ApprovalActionResponse>(response);
}
