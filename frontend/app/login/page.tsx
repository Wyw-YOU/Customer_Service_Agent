"use client";

import { Bot, LockKeyhole, LogIn, MessageSquareText, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useState } from "react";

import { getCurrentUser, login } from "@/services/api";

export default function LoginPage() {
  return (
    <Suspense fallback={<main className="loginPage" />}>
      <LoginPanel />
    </Suspense>
  );
}

function LoginPanel() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next") || "/chat";
  const [username, setUsername] = useState("zhangsan");
  const [password, setPassword] = useState("user123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await login(username.trim(), password);
      await getCurrentUser(result.access_token);
      window.localStorage.setItem("agent_token", result.access_token);
      router.push(nextPath);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "登录失败");
    } finally {
      setLoading(false);
    }
  }

  function useAccount(account: "user" | "admin" | "cs") {
    if (account === "admin") {
      setUsername("admin");
      setPassword("admin123");
      return;
    }
    if (account === "cs") {
      setUsername("cs_agent");
      setPassword("cs123");
      return;
    }
    setUsername("zhangsan");
    setPassword("user123");
  }

  return (
    <main className="loginPage">
      <section className="loginHero">
        <div className="brandMark">
          <Bot size={20} />
        </div>
        <h1>Digital Mall Agent</h1>
        <p>统一登录后进入 AI 客服、Trace 排障和售后审批工作台。</p>
        <div className="loginFeatureList">
          <span>
            <MessageSquareText size={16} />
            Chat
          </span>
          <span>
            <ShieldCheck size={16} />
            Trace
          </span>
          <span>
            <LockKeyhole size={16} />
            Approval
          </span>
        </div>
      </section>

      <section className="loginCard">
        <div className="loginCardHeader">
          <h2>登录</h2>
          <p>选择一个种子账号，或输入已有账号。</p>
        </div>

        <div className="accountPresets">
          <button type="button" onClick={() => useAccount("user")}>
            用户
          </button>
          <button type="button" onClick={() => useAccount("cs")}>
            客服
          </button>
          <button type="button" onClick={() => useAccount("admin")}>
            管理员
          </button>
        </div>

        <form className="loginForm" onSubmit={handleSubmit}>
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

          {error ? <div className="loginError">{error}</div> : null}

          <button type="submit" disabled={loading}>
            <LogIn size={17} />
            {loading ? "登录中" : "登录"}
          </button>
        </form>

        <Link className="backLink" href="/chat">
          返回 Chat
        </Link>
      </section>
    </main>
  );
}
