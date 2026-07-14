"use client";

import {
  Bot,
  ClipboardCheck,
  Headset,
  LayoutDashboard,
  LogIn,
  LogOut,
  MessageSquareText,
  PanelLeftClose,
  PanelLeftOpen,
  Route,
  ShieldCheck,
  Sparkles,
  Users,
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
  active: "chat" | "dashboard" | "service" | "traces" | "approvals" | "users";
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

const navItems: Array<{
  href: string;
  label: string;
  icon: typeof MessageSquareText;
  key: AppShellProps["active"];
  minRole: Role;
}> = [
  { href: "/chat", label: "用户 Chat", icon: MessageSquareText, key: "chat", minRole: "USER" },
  { href: "/admin/service", label: "会话工作台", icon: Headset, key: "service", minRole: "CUSTOMER_SERVICE" },
  { href: "/admin/approvals", label: "退款审批", icon: ClipboardCheck, key: "approvals", minRole: "CUSTOMER_SERVICE" },
  { href: "/admin", label: "运营概览", icon: LayoutDashboard, key: "dashboard", minRole: "ADMIN" },
  { href: "/admin/users", label: "客服管理", icon: Users, key: "users", minRole: "ADMIN" },
  { href: "/admin/traces", label: "Trace 监控", icon: Route, key: "traces", minRole: "ADMIN" },
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
  const loginPath = requiredRole === "USER" ? "/login" : "/admin/login";

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

  useEffect(() => {
    function handleAuthExpired() {
      setToken("");
      setUser(null);
      setError("登录已过期，请重新登录。");
    }

    window.addEventListener("agent-auth-expired", handleAuthExpired);
    return () => window.removeEventListener("agent-auth-expired", handleAuthExpired);
  }, []);

  const isAuthed = Boolean(token && user);
  const shellState: AppShellState = { token, user, isAuthed, setError };
  const currentRoleLevel = user ? (roleLevel[user.role as Role] ?? 0) : roleLevel.ADMIN;
  const visibleNavItems = navItems.filter((item) => currentRoleLevel >= roleLevel[item.minRole]);
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
    router.push(`${loginPath}?next=${encodeURIComponent(pathname)}`);
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
          <button
            className="iconButton collapseButton"
            type="button"
            onClick={toggleSidebar}
            title={collapsed ? "展开侧栏" : "收起侧栏"}
          >
            {collapsed ? <PanelLeftOpen size={17} /> : <PanelLeftClose size={17} />}
          </button>
        </div>

        <nav className="appNav" aria-label="Workspace navigation">
          {visibleNavItems.map((item) => {
            const Icon = item.icon;
            const selected = item.key === active;
            return (
              <Link key={item.href} className={selected ? "active" : ""} href={item.href} title={item.label}>
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
            <Link className="loginLink" href={`${loginPath}?next=${encodeURIComponent(pathname)}`}>
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
            actionHref={`${loginPath}?next=${encodeURIComponent(pathname)}`}
            actionLabel="前往登录"
          />
        ) : !hasRequiredRole ? (
          <AuthState
            icon={<ShieldCheck size={28} />}
            title="当前账号权限不足"
            description="管理页面需要 CUSTOMER_SERVICE 或 ADMIN 角色。"
            secondaryHref="/chat"
            secondaryLabel="返回 Chat"
            actionHref={`/admin/login?next=${encodeURIComponent(pathname)}`}
            actionLabel="切换账号"
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
  secondaryHref,
  secondaryLabel,
}: {
  icon: ReactNode;
  title: string;
  description?: string;
  actionHref?: string;
  actionLabel?: string;
  secondaryHref?: string;
  secondaryLabel?: string;
}) {
  return (
    <div className="authState">
      <div className="emptyIcon">{icon}</div>
      <h3>{title}</h3>
      {description ? <p>{description}</p> : null}
      <div className="authActions">
        {actionHref && actionLabel ? (
          <Link className="primaryLink" href={actionHref}>
            {actionLabel}
          </Link>
        ) : null}
        {secondaryHref && secondaryLabel ? (
          <Link className="secondaryLink" href={secondaryHref}>
            {secondaryLabel}
          </Link>
        ) : null}
      </div>
    </div>
  );
}
