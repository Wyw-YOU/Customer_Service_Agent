"use client";

import { RefreshCw, ShieldCheck, UserRound, Users } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { AdminShell } from "@/app/admin/components/AdminShell";
import { UserSummary, listUsers } from "@/services/api";

const PAGE_SIZE = 20;
const roleFilters = [
  { label: "全部角色", value: "" },
  { label: "普通用户", value: "USER" },
  { label: "客服", value: "CUSTOMER_SERVICE" },
  { label: "管理员", value: "ADMIN" },
];

export default function UsersPage() {
  return (
    <AdminShell
      active="users"
      eyebrow="账号管理"
      title="客服管理"
      description="查看用户、客服和管理员账号，为后续禁用、重置密码、分配角色做准备。"
      requiredRole="ADMIN"
    >
      {({ token, isAuthed, setError }) => (
        <UsersWorkspace token={token} isAuthed={isAuthed} setError={setError} />
      )}
    </AdminShell>
  );
}

function UsersWorkspace({
  token,
  isAuthed,
  setError,
}: {
  token: string;
  isAuthed: boolean;
  setError: (message: string) => void;
}) {
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [roleFilter, setRoleFilter] = useState("");
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isAuthed) {
      setUsers([]);
      return;
    }
    void loadUsers(offset);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthed, token, roleFilter, offset]);

  async function loadUsers(nextOffset = offset) {
    if (!token) {
      return;
    }
    setError("");
    setLoading(true);
    try {
      const result = await listUsers(token, {
        role: roleFilter || undefined,
        limit: PAGE_SIZE,
        offset: nextOffset,
      });
      setUsers(result);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "账号列表加载失败");
    } finally {
      setLoading(false);
    }
  }

  const summary = useMemo(() => {
    return {
      active: users.filter((item) => item.is_active).length,
      customerService: users.filter((item) => item.role === "CUSTOMER_SERVICE").length,
      admins: users.filter((item) => item.role === "ADMIN").length,
    };
  }, [users]);

  if (!isAuthed) {
    return <UsersEmpty title="登录后查看账号" />;
  }

  return (
    <div className="adminGrid">
      <div className="adminMetrics">
        <Metric label="本页账号" value={String(users.length)} />
        <Metric label="启用中" value={String(summary.active)} tone="success" />
        <Metric label="客服" value={String(summary.customerService)} />
        <Metric label="管理员" value={String(summary.admins)} />
      </div>

      <div className="adminToolbar">
        <label className="filterGroup">
          <span>角色</span>
          <select
            value={roleFilter}
            onChange={(event) => {
              setRoleFilter(event.target.value);
              setOffset(0);
            }}
          >
            {roleFilters.map((role) => (
              <option key={role.value || "all"} value={role.value}>
                {role.label}
              </option>
            ))}
          </select>
        </label>
        <div className="pager">
          <button type="button" onClick={() => setOffset((value) => Math.max(value - PAGE_SIZE, 0))} disabled={loading || offset === 0}>
            上一页
          </button>
          <span>{Math.floor(offset / PAGE_SIZE) + 1}</span>
          <button type="button" onClick={() => setOffset((value) => value + PAGE_SIZE)} disabled={loading || users.length < PAGE_SIZE}>
            下一页
          </button>
        </div>
        <button type="button" onClick={() => loadUsers(offset)} disabled={loading}>
          <RefreshCw size={16} />
          {loading ? "刷新中" : "刷新"}
        </button>
      </div>

      <section className="userTable">
        <div className="userHeader">
          <span>账号</span>
          <span>角色</span>
          <span>联系方式</span>
          <span>状态</span>
          <span>创建时间</span>
        </div>
        {users.length === 0 ? (
          <UsersEmpty title="暂无账号" />
        ) : (
          users.map((user) => <UserRow key={user.id} user={user} />)
        )}
      </section>
    </div>
  );
}

function UserRow({ user }: { user: UserSummary }) {
  return (
    <article className="userRow">
      <div className="userIdentity">
        <div className="conversationAvatar">{user.username.slice(0, 1).toUpperCase()}</div>
        <div>
          <strong>{user.username}</strong>
          <span>#{user.id}</span>
        </div>
      </div>
      <RoleBadge role={user.role} />
      <div>
        <strong>{user.email || "-"}</strong>
        <span>{user.phone || "-"}</span>
      </div>
      <span className={`statusBadge ${user.is_active ? "success" : "danger"}`}>
        {user.is_active ? "ACTIVE" : "DISABLED"}
      </span>
      <span className="mutedText">{formatDate(user.created_at)}</span>
    </article>
  );
}

function RoleBadge({ role }: { role: string }) {
  const admin = role === "ADMIN";
  const service = role === "CUSTOMER_SERVICE";
  return (
    <span className={`statusBadge ${admin ? "danger" : service ? "pending" : "success"}`}>
      {admin ? <ShieldCheck size={13} /> : service ? <Users size={13} /> : <UserRound size={13} />}
      {role}
    </span>
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

function UsersEmpty({ title }: { title: string }) {
  return (
    <div className="adminEmpty">
      <Users size={26} />
      <span>{title}</span>
    </div>
  );
}

function formatDate(value?: string | null) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(value));
}
