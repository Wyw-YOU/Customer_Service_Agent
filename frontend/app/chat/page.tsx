"use client";

import {
  AlertCircle,
  Bot,
  CheckCircle2,
  MessageSquareText,
  Plus,
  Send,
  UserRound,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { AppShell } from "@/app/components/AppShell";
import { sendChatMessage } from "@/services/api";

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
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const savedConversationId = window.localStorage.getItem("agent_conversation_id");
    if (savedConversationId) {
      setConversationId(Number(savedConversationId));
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, chatLoading]);

  const sessionLabel = useMemo(() => (conversationId ? `会话 #${conversationId}` : "新会话"), [conversationId]);

  async function handleSend(token: string, event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    const text = draft.trim();
    if (!text || chatLoading) {
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
    <AppShell
      active="chat"
      eyebrow="AI 客服工作台"
      title="Chat"
      sidebarExtra={({ isAuthed }) => (
        <>
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

          <button className="newChatButton" type="button" onClick={startNewConversation} disabled={!isAuthed}>
            <Plus size={16} />
            新会话
          </button>
        </>
      )}
    >
      {({ token, isAuthed }) => (
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

          <form className="composer" onSubmit={(event) => handleSend(token, event)}>
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
      )}
    </AppShell>
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
