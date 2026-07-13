"use client";

import {
  Bot,
  ClipboardCheck,
  LogIn,
  LogOut,
  MessageSquareText,
  PanelLeftClose,
  PanelLeftOpen,
  Route,
  ShieldCheck,
  Sparkles,
  UserRound,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useMemo, useState } from "react";

import { CurrentUser, getCurrentUser } from "@/services/api";

type Role = "USER" | "CUSTOMER_SERVICE" | "ADMIN";

export type AppShellState = {
  token: string;
  user: CurrentUser | null;
  isAuthed: boolean;
  setError: (message: string) => void;
};

type AppShellProps = {
  active: "chat" | "traces" | "approvals";
  eyebrow: string;
  title: string;
  requiredRole?: Role;
  sidebarExtra?: ReactNode | ((state: AppShellState) => ReactNode);
  children: (state: AppShellState) => ReactNode;
};

const roleLevel: Record<Role, number> = {
  USER: 1,
  CUSTOMER_SERVICE: 2,
  ADMIN: 3,
};

const navItems = [
  { href: "/chat", label: "Chat", icon: MessageSquareText, key: "chat" },
  { href: "/admin/traces", label: "Trace", icon: Route, key: "traces" },
  { href: "/admin/approvals", label: "Approval", icon: ClipboardCheck, key: "approvals" },
];

export function AppShell({
  active,
  eyebrow,
  title,
  requiredRole = "USER",
  sidebarExtra,
  children,
}: AppShellProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [token, setToken] = useState("");
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [collapsed, setCollapsed] = useState(false);
  const [error, setError] = useState("");
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const savedToken = window.localStorage.getItem("agent_token");
    const savedCollapsed = window.localStorage.getItem("agent_sidebar_collapsed");
    setCollapsed(savedCollapsed === "1");
    if (!savedToken) {
      setChecking(false);
      return;
    }

    setToken(savedToken);
    void getCurrentUser(savedToken)
      .then((result) => {
        setUser(result);
      })
      .catch(() => {
        window.localStorage.removeItem("agent_token");
        window.localStorage.removeItem("agent_conversation_id");
        setToken("");
        setUser(null);
      })
      .finally(() => setChecking(false));
  }, []);

  const isAuthed = Boolean(token && user);
  const shellState: AppShellState = { token, user, isAuthed, setError };
  const hasRequiredRole = useMemo(() => {
    if (!user) {
      return false;
    }
    return (roleLevel[user.role as Role] ?? 0) >= roleLevel[requiredRole];
  }, [requiredRole, user]);

  function toggleSidebar() {
    const nextValue = !collapsed;
    setCollapsed(nextValue);
    window.localStorage.setItem("agent_sidebar_collapsed", nextValue ? "1" : "0");
  }

  function handleLogout() {
    window.localStorage.removeItem("agent_token");
    window.localStorage.removeItem("agent_conversation_id");
    setToken("");
    setUser(null);
    router.push(`/login?next=${encodeURIComponent(pathname)}`);
  }

  return (
    <main className={collapsed ? "shell shellCollapsed" : "shell"}>
      <aside className="sidebar">
        <div className="brand">
          <div className="brandMark">
            {active === "chat" ? <Sparkles size={18} /> : <ShieldCheck size={18} />}
          </div>
          <div className="brandText">
            <h1>Digital Mall Agent</h1>
            <p>{user ? `${user.username} · #${user.id}` : "请登录"}</p>
          </div>
          <button className="iconButton collapseButton" type="button" onClick={toggleSidebar}>
            {collapsed ? <PanelLeftOpen size={17} /> : <PanelLeftClose size={17} />}
          </button>
        </div>

        <nav className="appNav" aria-label="Workspace navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            const selected = item.key === active;
            return (
              <Link key={item.href} className={selected ? "active" : ""} href={item.href}>
                <Icon size={17} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="sidebarExtra">
          {typeof sidebarExtra === "function" ? sidebarExtra(shellState) : sidebarExtra}
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">{eyebrow}</span>
            <h2>{title}</h2>
          </div>

          {isAuthed && user ? (
            <div className="accountCluster">
              <div className="userChip">
                <div className="userAvatar">{user.username.slice(0, 1).toUpperCase()}</div>
                <div>
                  <strong>{user.username}</strong>
                  <span>
                    #{user.id} · {user.role}
                  </span>
                </div>
              </div>
              <button className="iconButton" type="button" onClick={handleLogout} title="退出登录">
                <LogOut size={17} />
              </button>
            </div>
          ) : (
            <Link className="loginLink" href={`/login?next=${encodeURIComponent(pathname)}`}>
              <LogIn size={16} />
              登录
            </Link>
          )}
        </header>

        {error ? <div className="pageError">{error}</div> : null}

        {checking ? (
          <AuthState icon={<Bot size={28} />} title="正在确认登录状态" />
        ) : !isAuthed ? (
          <AuthState
            icon={<LogIn size={28} />}
            title="请先登录"
            description="登录后可以进入 Chat、Trace 和 Approval 工作区。"
            actionHref={`/login?next=${encodeURIComponent(pathname)}`}
            actionLabel="前往登录"
          />
        ) : !hasRequiredRole ? (
          <AuthState
            icon={<ShieldCheck size={28} />}
            title="当前账号权限不足"
            description="管理页面需要 CUSTOMER_SERVICE 或 ADMIN 角色。"
          />
        ) : (
          children(shellState)
        )}
      </section>
    </main>
  );
}

function AuthState({
  icon,
  title,
  description,
  actionHref,
  actionLabel,
}: {
  icon: ReactNode;
  title: string;
  description?: string;
  actionHref?: string;
  actionLabel?: string;
}) {
  return (
    <div className="authState">
      <div className="emptyIcon">{icon}</div>
      <h3>{title}</h3>
      {description ? <p>{description}</p> : null}
      {actionHref && actionLabel ? (
        <Link className="primaryLink" href={actionHref}>
          {actionLabel}
        </Link>
      ) : null}
    </div>
  );
}
