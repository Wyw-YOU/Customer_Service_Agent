"use client";

import { Bot, Headset, LockKeyhole, LogIn, MessageSquareText, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, ReactNode, useEffect, useState } from "react";

import { CurrentUser, getCurrentUser, login } from "@/services/api";

type LoginVariant = "user" | "admin";

type Preset = {
  key: string;
  label: string;
  username: string;
  password: string;
};

const userPresets: Preset[] = [
  { key: "user", label: "普通用户", username: "zhangsan", password: "user123" },
];

const adminPresets: Preset[] = [
  { key: "cs", label: "客服", username: "cs_agent", password: "cs123" },
  { key: "admin", label: "管理员", username: "admin", password: "admin123" },
];

export function LoginExperience({ variant }: { variant: LoginVariant }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const isAdmin = variant === "admin";
  const presets = isAdmin ? adminPresets : userPresets;
  const defaultPreset = presets[0];
  const [username, setUsername] = useState(defaultPreset.username);
  const [password, setPassword] = useState(defaultPreset.password);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const nextPath = sanitizeNextPath(searchParams.get("next"));

  useEffect(() => {
    const savedToken = window.localStorage.getItem("agent_token");
    if (!savedToken) {
      return;
    }
    void getCurrentUser(savedToken)
      .then((user) => {
        if (isAdmin && !canUseAdmin(user)) {
          return;
        }
        router.replace(resolveNextPath(user, isAdmin, nextPath));
      })
      .catch(() => {
        window.localStorage.removeItem("agent_token");
        window.localStorage.removeItem("agent_conversation_id");
      });
  }, [isAdmin, nextPath, router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await login(username.trim(), password);
      const user = await getCurrentUser(result.access_token);
      if (isAdmin && !canUseAdmin(user)) {
        setError("当前账号不是客服或管理员，不能进入管理端。");
        return;
      }
      if (canUseAdmin(user)) {
        window.localStorage.removeItem("agent_conversation_id");
      }
      window.localStorage.setItem("agent_token", result.access_token);
      router.push(resolveNextPath(user, isAdmin, nextPath));
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "登录失败");
    } finally {
      setLoading(false);
    }
  }

  function usePreset(preset: Preset) {
    setUsername(preset.username);
    setPassword(preset.password);
  }

  return (
    <main className={isAdmin ? "loginPage adminLoginPage" : "loginPage"}>
      <section className="loginHero">
        <div className="brandMark">{isAdmin ? <ShieldCheck size={20} /> : <Bot size={20} />}</div>
        <h1>{isAdmin ? "Agent Console" : "Digital Mall Agent"}</h1>
        <p>
          {isAdmin
            ? "客服在这里接入用户会话、处理退款审批；管理员在后台管理客服、审批和链路监控。"
            : "用户在这里进入 AI 客服会话，完成商品咨询、订单查询和售后申请。"}
        </p>
        <div className="loginFeatureList">
          {isAdmin ? (
            <>
              <Feature icon={<ShieldCheck size={16} />} label="Trace" />
              <Feature icon={<LockKeyhole size={16} />} label="Approval" />
              <Feature icon={<Headset size={16} />} label="会话工作台" />
            </>
          ) : (
            <>
              <Feature icon={<MessageSquareText size={16} />} label="Chat" />
              <Feature icon={<Bot size={16} />} label="商品咨询" />
              <Feature icon={<LockKeyhole size={16} />} label="售后申请" />
            </>
          )}
        </div>
      </section>

      <section className="loginCard">
        <div className="loginCardHeader">
          <h2>{isAdmin ? "管理端登录" : "用户登录"}</h2>
          <p>{isAdmin ? "使用客服或管理员账号。" : "使用普通用户账号进入 Chat。"}</p>
        </div>

        <div className={presets.length > 1 ? "accountPresets" : "accountPresets single"}>
          {presets.map((preset) => (
            <button key={preset.key} type="button" onClick={() => usePreset(preset)}>
              {preset.label}
            </button>
          ))}
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

        <Link className="backLink" href={isAdmin ? "/login" : "/admin/login"}>
          {isAdmin ? "切换到用户登录" : "切换到管理端登录"}
        </Link>
      </section>
    </main>
  );
}

function Feature({ icon, label }: { icon: ReactNode; label: string }) {
  return (
    <span>
      {icon}
      {label}
    </span>
  );
}

function canUseAdmin(user: CurrentUser) {
  return user.role === "CUSTOMER_SERVICE" || user.role === "ADMIN";
}

function resolveNextPath(user: CurrentUser, isAdmin: boolean, nextPath: string | null) {
  if (nextPath && (!nextPath.startsWith("/admin") || canUseAdmin(user))) {
    return nextPath;
  }
  if (isAdmin || canUseAdmin(user)) {
    return user.role === "ADMIN" ? "/admin" : "/admin/service";
  }
  return "/chat";
}

function sanitizeNextPath(value: string | null) {
  if (!value || !value.startsWith("/") || value.startsWith("//")) {
    return null;
  }
  return value;
}
