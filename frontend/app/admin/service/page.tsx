"use client";

import { AlertCircle, Bot, CheckCircle2, Clock3, Headset, RefreshCw, UserRound } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { AdminShell } from "@/app/admin/components/AdminShell";
import {
  ConversationDetail,
  ConversationMessage,
  ConversationSummary,
  getConversation,
  listConversations,
} from "@/services/api";

const PAGE_SIZE = 20;
const conversationStatuses = [
  { label: "全部会话", value: "" },
  { label: "进行中", value: "ACTIVE" },
  { label: "已关闭", value: "CLOSED" },
];

export default function ServiceWorkbenchPage() {
  return (
    <AdminShell
      active="service"
      eyebrow="客服工作台"
      title="会话工作台"
      description="像客服聊天软件一样选择用户会话，查看上下文、用户信息和待处理动作。"
    >
      {({ token, isAuthed, setError }) => (
        <ServiceWorkbench token={token} isAuthed={isAuthed} setError={setError} />
      )}
    </AdminShell>
  );
}

function ServiceWorkbench({
  token,
  isAuthed,
  setError,
}: {
  token: string;
  isAuthed: boolean;
  setError: (message: string) => void;
}) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selected, setSelected] = useState<ConversationDetail | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isAuthed) {
      setConversations([]);
      setSelected(null);
      return;
    }
    void loadConversations(offset);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthed, token, statusFilter, offset]);

  async function loadConversations(nextOffset = offset) {
    if (!token) {
      return;
    }
    setError("");
    setLoading(true);
    try {
      const result = await listConversations(token, {
        status: statusFilter || undefined,
        limit: PAGE_SIZE,
        offset: nextOffset,
      });
      setConversations(result);
      if (result.length > 0) {
        await selectConversation(result[0].id);
      } else {
        setSelected(null);
      }
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "会话列表加载失败");
    } finally {
      setLoading(false);
    }
  }

  async function selectConversation(conversationId: number) {
    setError("");
    try {
      const detail = await getConversation(token, conversationId);
      setSelected(detail);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "会话详情加载失败");
    }
  }

  function goPrev() {
    setOffset((value) => Math.max(value - PAGE_SIZE, 0));
  }

  function goNext() {
    if (conversations.length === PAGE_SIZE) {
      setOffset((value) => value + PAGE_SIZE);
    }
  }

  const summary = useMemo(() => {
    const active = conversations.filter((item) => item.status === "ACTIVE").length;
    const totalMessages = conversations.reduce((total, item) => total + item.message_count, 0);
    return { active, totalMessages };
  }, [conversations]);

  if (!isAuthed) {
    return <ServiceEmpty title="登录后查看用户会话" />;
  }

  return (
    <div className="serviceGrid">
      <div className="adminMetrics">
        <Metric label="本页会话" value={String(conversations.length)} />
        <Metric label="进行中" value={String(summary.active)} tone={summary.active ? "success" : ""} />
        <Metric label="消息数" value={String(summary.totalMessages)} />
        <Metric label="当前页" value={String(Math.floor(offset / PAGE_SIZE) + 1)} />
      </div>

      <div className="adminToolbar">
        <label className="filterGroup">
          <span>状态</span>
          <select
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(event.target.value);
              setOffset(0);
            }}
          >
            {conversationStatuses.map((status) => (
              <option key={status.value || "all"} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </label>
        <div className="pager">
          <button type="button" onClick={goPrev} disabled={loading || offset === 0}>
            上一页
          </button>
          <span>{Math.floor(offset / PAGE_SIZE) + 1}</span>
          <button type="button" onClick={goNext} disabled={loading || conversations.length < PAGE_SIZE}>
            下一页
          </button>
        </div>
        <button type="button" onClick={() => loadConversations(offset)} disabled={loading}>
          <RefreshCw size={16} />
          {loading ? "刷新中" : "刷新"}
        </button>
      </div>

      <div className="serviceLayout">
        <section className="conversationList">
          {conversations.length === 0 ? (
            <ServiceEmpty title="暂无用户会话" compact />
          ) : (
            conversations.map((conversation) => (
              <button
                key={conversation.id}
                type="button"
                className={selected?.id === conversation.id ? "conversationItem active" : "conversationItem"}
                onClick={() => selectConversation(conversation.id)}
              >
                <div className="conversationAvatar">{conversation.username.slice(0, 1).toUpperCase()}</div>
                <div>
                  <strong>{conversation.username}</strong>
                  <span>{conversation.title || `会话 #${conversation.id}`}</span>
                  <p>{conversation.last_message_preview || "暂无消息"}</p>
                </div>
                <StatusBadge status={conversation.status} />
              </button>
            ))
          )}
        </section>

        <section className="agentChatPanel">
          {selected ? (
            <>
              <div className="agentChatHeader">
                <div>
                  <h3>{selected.title || `会话 #${selected.id}`}</h3>
                  <p>
                    {selected.username} · {selected.message_count} 条消息 · {formatDate(selected.last_message_at)}
                  </p>
                </div>
                <StatusBadge status={selected.status} />
              </div>
              <div className="agentMessages">
                {selected.messages.length === 0 ? (
                  <ServiceEmpty title="暂无消息记录" compact />
                ) : (
                  selected.messages.map((message) => <AgentMessage key={message.id} message={message} />)
                )}
              </div>
              <div className="agentReplyDock">
                <textarea value="" placeholder="人工回复接口将在下一阶段接入" disabled rows={2} />
                <button type="button" disabled>
                  发送
                </button>
              </div>
            </>
          ) : (
            <ServiceEmpty title="选择一个用户会话" />
          )}
        </section>

        <aside className="customerPanel">
          {selected ? (
            <>
              <div className="customerProfile">
                <div className="conversationAvatar large">{selected.username.slice(0, 1).toUpperCase()}</div>
                <div>
                  <h3>{selected.username}</h3>
                  <p>用户 #{selected.user_id}</p>
                </div>
              </div>
              <div className="customerFacts">
                <Fact label="邮箱" value={selected.user_email || "-"} />
                <Fact label="手机" value={selected.user_phone || "-"} />
                <Fact label="会话状态" value={selected.status} />
                <Fact label="最近消息" value={formatDate(selected.last_message_at)} />
              </div>
              <div className="actionStack">
                <button type="button" disabled>
                  转接客服
                </button>
                <button type="button" disabled>
                  标记已解决
                </button>
                <button type="button" disabled>
                  创建售后工单
                </button>
              </div>
              <p className="sideNote">动作接口待接入；当前先提供会话查看和处理上下文。</p>
            </>
          ) : (
            <ServiceEmpty title="暂无用户信息" compact />
          )}
        </aside>
      </div>
    </div>
  );
}

function AgentMessage({ message }: { message: ConversationMessage }) {
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";
  return (
    <article className={`agentMessage ${isUser ? "fromUser" : isAssistant ? "fromAssistant" : "fromSystem"}`}>
      <div className="avatar">{isUser ? <UserRound size={16} /> : isAssistant ? <Bot size={16} /> : <Headset size={16} />}</div>
      <div className="agentBubble">
        <div className="messageMeta">
          <strong>{isUser ? "用户" : isAssistant ? "AI 助手" : message.role}</strong>
          <span>{formatDate(message.timestamp)}</span>
        </div>
        <p>{message.content}</p>
      </div>
    </article>
  );
}

function Metric({ label, value, tone = "" }: { label: string; value: string; tone?: string }) {
  return (
    <div className={`metric ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const active = status === "ACTIVE";
  return (
    <span className={`statusBadge ${active ? "success" : "pending"}`}>
      {active ? <CheckCircle2 size={13} /> : <AlertCircle size={13} />}
      {status}
    </span>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="factRow">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ServiceEmpty({ title, compact = false }: { title: string; compact?: boolean }) {
  return (
    <div className={compact ? "adminEmpty compact" : "adminEmpty"}>
      <Headset size={26} />
      <span>{title}</span>
    </div>
  );
}

function formatDate(value?: string | null) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
