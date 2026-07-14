"use client";

import { ClipboardCheck, Headset, LayoutDashboard, Route, Users } from "lucide-react";
import Link from "next/link";
import { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import { AdminShell } from "@/app/admin/components/AdminShell";
import {
  ApprovalTask,
  ConversationSummary,
  TraceRun,
  UserSummary,
  listApprovals,
  listConversations,
  listTraces,
  listUsers,
} from "@/services/api";

export default function AdminDashboardPage() {
  return (
    <AdminShell
      active="dashboard"
      eyebrow="管理后台"
      title="运营概览"
      description="聚合客服会话、退款审批、链路监控和账号管理入口。"
      requiredRole="ADMIN"
    >
      {({ token, isAuthed, setError }) => (
        <AdminDashboard token={token} isAuthed={isAuthed} setError={setError} />
      )}
    </AdminShell>
  );
}

function AdminDashboard({
  token,
  isAuthed,
  setError,
}: {
  token: string;
  isAuthed: boolean;
  setError: (message: string) => void;
}) {
  const [approvals, setApprovals] = useState<ApprovalTask[]>([]);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [traces, setTraces] = useState<TraceRun[]>([]);
  const [users, setUsers] = useState<UserSummary[]>([]);

  useEffect(() => {
    if (!isAuthed || !token) {
      return;
    }

    async function loadDashboard() {
      setError("");
      try {
        const [approvalItems, conversationItems, traceItems, userItems] = await Promise.all([
          listApprovals(token, { limit: 20 }),
          listConversations(token, { limit: 20 }),
          listTraces(token, { limit: 20 }),
          listUsers(token, { limit: 20 }),
        ]);
        setApprovals(approvalItems);
        setConversations(conversationItems);
        setTraces(traceItems);
        setUsers(userItems);
      } catch (exc) {
        setError(exc instanceof Error ? exc.message : "运营概览加载失败");
      }
    }

    void loadDashboard();
  }, [isAuthed, token, setError]);

  const metrics = useMemo(() => {
    return {
      activeConversations: conversations.filter((item) => item.status === "ACTIVE").length,
      pendingApprovals: approvals.filter((item) => item.status === "PENDING").length,
      warningTraces: traces.filter((item) => item.status !== "COMPLETED").length,
      serviceUsers: users.filter((item) => item.role === "CUSTOMER_SERVICE").length,
    };
  }, [approvals, conversations, traces, users]);

  if (!isAuthed) {
    return <DashboardEmpty />;
  }

  return (
    <div className="adminGrid">
      <div className="adminMetrics">
        <Metric icon={<Headset size={18} />} label="进行中会话" value={String(metrics.activeConversations)} />
        <Metric icon={<ClipboardCheck size={18} />} label="待审批退款" value={String(metrics.pendingApprovals)} />
        <Metric icon={<Route size={18} />} label="异常 Trace" value={String(metrics.warningTraces)} />
        <Metric icon={<Users size={18} />} label="客服账号" value={String(metrics.serviceUsers)} />
      </div>

      <div className="dashboardTiles">
        <DashboardTile
          href="/admin/service"
          icon={<Headset size={22} />}
          title="会话工作台"
          description="查看用户会话列表、聊天上下文和用户信息。"
        />
        <DashboardTile
          href="/admin/approvals"
          icon={<ClipboardCheck size={22} />}
          title="退款审批"
          description="处理高风险售后退款，记录处理备注。"
        />
        <DashboardTile
          href="/admin/users"
          icon={<Users size={22} />}
          title="客服管理"
          description="查看用户、客服、管理员账号及启用状态。"
        />
        <DashboardTile
          href="/admin/traces"
          icon={<Route size={22} />}
          title="Trace 监控"
          description="排查 Agent 执行链路、工具调用和异常节点。"
        />
      </div>
    </div>
  );
}

function Metric({
  icon,
  label,
  value,
}: {
  icon: ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="metric">
      <span>
        {icon}
        {label}
      </span>
      <strong>{value}</strong>
    </div>
  );
}

function DashboardTile({
  href,
  icon,
  title,
  description,
}: {
  href: string;
  icon: ReactNode;
  title: string;
  description: string;
}) {
  return (
    <Link className="dashboardTile" href={href}>
      <div className="emptyIcon">{icon}</div>
      <div>
        <h4>{title}</h4>
        <p>{description}</p>
      </div>
    </Link>
  );
}

function DashboardEmpty() {
  return (
    <div className="adminEmpty">
      <LayoutDashboard size={26} />
      <span>登录后查看运营概览</span>
    </div>
  );
}
