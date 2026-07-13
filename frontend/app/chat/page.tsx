"use client";

import {
  AlertCircle,
  Bot,
  CheckCircle2,
  LogIn,
  LogOut,
  MessageSquareText,
  Plus,
  Send,
  Sparkles,
  UserRound,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { login, sendChatMessage } from "@/services/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  intent?: string | null;
  sources?: string[] | null;
};

const quickPrompts = [
  "预算5000以内推荐拍照手机",
  "查询订单10001物流",
  "我要给订单10001申请退款，商品质量问题",
  "七天无理由退货规则是什么？",
];

export default function ChatPage() {
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("zhangsan");
  const [password, setPassword] = useState("user123");
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const savedToken = window.localStorage.getItem("agent_token");
    const savedConversationId = window.localStorage.getItem("agent_conversation_id");
    if (savedToken) {
      setToken(savedToken);
    }
    if (savedConversationId) {
      setConversationId(Number(savedConversationId));
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, chatLoading]);

  const isAuthed = Boolean(token);
  const sessionLabel = useMemo(() => {
    if (!isAuthed) {
      return "待登录";
    }
    return conversationId ? `会话 #${conversationId}` : "新会话";
  }, [conversationId, isAuthed]);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoginLoading(true);
    try {
      const result = await login(username.trim(), password);
      setToken(result.access_token);
      window.localStorage.setItem("agent_token", result.access_token);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "登录失败");
    } finally {
      setLoginLoading(false);
    }
  }

  function handleLogout() {
    setToken("");
    setConversationId(null);
    setMessages([]);
    window.localStorage.removeItem("agent_token");
    window.localStorage.removeItem("agent_conversation_id");
  }

  async function handleSend(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    const text = draft.trim();
    if (!text || !token || chatLoading) {
      return;
    }

    setError("");
    setDraft("");
    setMessages((items) => [
      ...items,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
      },
    ]);
    setChatLoading(true);

    try {
      const result = await sendChatMessage(token, text, conversationId);
      setConversationId(result.conversation_id);
      window.localStorage.setItem("agent_conversation_id", String(result.conversation_id));
      setMessages((items) => [
        ...items,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: result.answer,
          intent: result.intent,
          sources: result.sources,
        },
      ]);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "消息发送失败");
    } finally {
      setChatLoading(false);
    }
  }

  function startNewConversation() {
    setConversationId(null);
    setMessages([]);
    window.localStorage.removeItem("agent_conversation_id");
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brandMark">
            <Sparkles size={18} />
          </div>
          <div>
            <h1>Digital Mall Agent</h1>
            <p>{sessionLabel}</p>
          </div>
        </div>

        <section className="sideSection">
          <div className="sectionHeader">登录身份</div>
          <form className="loginPanel" onSubmit={handleLogin}>
            <label>
              <span>账号</span>
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                autoComplete="username"
              />
            </label>
            <label>
              <span>密码</span>
              <input
                value={password}
                type="password"
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
              />
            </label>
            {isAuthed ? (
              <button className="secondaryButton" type="button" onClick={handleLogout}>
                <LogOut size={16} />
                退出登录
              </button>
            ) : (
              <button type="submit" disabled={loginLoading}>
                <LogIn size={16} />
                {loginLoading ? "登录中" : "登录"}
              </button>
            )}
          </form>
        </section>

        <section className="sideSection">
          <div className="sectionHeader withIcon">
            <MessageSquareText size={16} />
            <span>常用请求</span>
          </div>
          <div className="quickList">
            {quickPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => setDraft(prompt)}
                disabled={!isAuthed}
              >
                {prompt}
              </button>
            ))}
          </div>
        </section>

        <button className="newChatButton" type="button" onClick={startNewConversation}>
          <Plus size={16} />
          新会话
        </button>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">AI 客服工作台</span>
            <h2>Chat</h2>
          </div>
          <div className={isAuthed ? "statusPill active" : "statusPill"}>
            <span />
            {isAuthed ? "已连接" : "待登录"}
          </div>
        </header>

        <div className="chatFrame">
          <div className="chatHeader">
            <div>
              <h3>智能客服会话</h3>
              <p>商品推荐、订单查询、售后申请会自动进入对应 Agent 流程。</p>
            </div>
            <div className="sessionBadge">{sessionLabel}</div>
          </div>

          {error ? (
            <div className="errorBar">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          ) : null}

          <div className="messages">
            {messages.length === 0 ? (
              <EmptyState isAuthed={isAuthed} onPickPrompt={setDraft} />
            ) : (
              messages.map((message) => <MessageBubble key={message.id} message={message} />)
            )}
            {chatLoading ? <TypingBubble /> : null}
            <div ref={messagesEndRef} />
          </div>

          <form className="composer" onSubmit={handleSend}>
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder={isAuthed ? "输入商品、订单或售后问题" : "请先登录后开始会话"}
              disabled={!isAuthed || chatLoading}
              rows={2}
            />
            <button type="submit" disabled={!isAuthed || !draft.trim() || chatLoading}>
              <Send size={18} />
              <span>发送</span>
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}

function EmptyState({
  isAuthed,
  onPickPrompt,
}: {
  isAuthed: boolean;
  onPickPrompt: (prompt: string) => void;
}) {
  return (
    <div className="emptyState">
      <div className="emptyIcon">
        <Bot size={28} />
      </div>
      <h3>{isAuthed ? "可以开始提问了" : "登录后开始会话"}</h3>
      <p>选择一个常用请求，或直接输入你的商品、订单、售后问题。</p>
      <div className="promptGrid">
        {quickPrompts.slice(0, 3).map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onPickPrompt(prompt)}
            disabled={!isAuthed}
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}

function TypingBubble() {
  return (
    <div className="message assistant">
      <div className="avatar">
        <Bot size={17} />
      </div>
      <div className="bubble typing">
        <span />
        <span />
        <span />
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <article className={`message ${isUser ? "user" : "assistant"}`}>
      <div className="avatar">{isUser ? <UserRound size={17} /> : <Bot size={17} />}</div>
      <div className="bubble">
        <div className="content">{message.content}</div>
        {!isUser && (message.intent || message.sources?.length) ? (
          <div className="metaRow">
            {message.intent ? (
              <span>
                <CheckCircle2 size={13} />
                {message.intent}
              </span>
            ) : null}
            {message.sources?.map((source) => (
              <span key={source}>{source}</span>
            ))}
          </div>
        ) : null}
      </div>
    </article>
  );
}
