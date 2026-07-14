"use client";

import { AlertCircle, CheckCircle2, ClipboardCheck, RefreshCw, XCircle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { AdminShell } from "@/app/admin/components/AdminShell";
import { ApprovalTask, approveTask, listApprovals, rejectTask } from "@/services/api";

const PAGE_SIZE = 20;
const approvalStatuses = [
  { label: "全部状态", value: "" },
  { label: "待处理", value: "PENDING" },
  { label: "已通过", value: "APPROVED" },
  { label: "已拒绝", value: "REJECTED" },
];

export default function AdminApprovalsPage() {
  return (
    <AdminShell
      active="approvals"
      eyebrow="售后审批"
      title="Approval"
      description="处理退款审批任务，已处理任务会自动禁用操作。"
    >
      {({ token, isAuthed, setError }) => (
        <ApprovalWorkspace token={token} isAuthed={isAuthed} setError={setError} />
      )}
    </AdminShell>
  );
}

function ApprovalWorkspace({
  token,
  isAuthed,
  setError,
}: {
  token: string;
  isAuthed: boolean;
  setError: (message: string) => void;
}) {
  const [tasks, setTasks] = useState<ApprovalTask[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [comments, setComments] = useState<Record<number, string>>({});

  useEffect(() => {
    if (!isAuthed) {
      setTasks([]);
      return;
    }
    void loadApprovals(offset);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthed, token, statusFilter, offset]);

  async function loadApprovals(nextOffset = offset) {
    if (!token) {
      return;
    }
    setError("");
    setLoading(true);
    try {
      const result = await listApprovals(token, {
        status: statusFilter || undefined,
        limit: PAGE_SIZE,
        offset: nextOffset,
      });
      setTasks(result);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "审批任务加载失败");
    } finally {
      setLoading(false);
    }
  }

  async function handleAction(taskId: number, action: "approve" | "reject") {
    setError("");
    setProcessingId(taskId);
    try {
      if (action === "approve") {
        await approveTask(token, taskId, comments[taskId]);
      } else {
        await rejectTask(token, taskId, comments[taskId]);
      }
      await loadApprovals(offset);
      setComments((items) => ({ ...items, [taskId]: "" }));
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "审批操作失败");
    } finally {
      setProcessingId(null);
    }
  }

  function handleStatusChange(value: string) {
    setStatusFilter(value);
    setOffset(0);
  }

  function goPrev() {
    setOffset((value) => Math.max(value - PAGE_SIZE, 0));
  }

  function goNext() {
    if (tasks.length === PAGE_SIZE) {
      setOffset((value) => value + PAGE_SIZE);
    }
  }

  const summary = useMemo(() => {
    const pending = tasks.filter((task) => task.status === "PENDING").length;
    const approved = tasks.filter((task) => task.status === "APPROVED").length;
    const rejected = tasks.filter((task) => task.status === "REJECTED").length;
    return { pending, approved, rejected };
  }, [tasks]);

  if (!isAuthed) {
    return <AdminEmpty title="登录后查看审批任务" />;
  }

  return (
    <div className="adminGrid">
      <div className="adminMetrics">
        <Metric label="本页待处理" value={String(summary.pending)} tone={summary.pending ? "danger" : ""} />
        <Metric label="本页已通过" value={String(summary.approved)} tone="success" />
        <Metric label="本页已拒绝" value={String(summary.rejected)} />
        <Metric label="本页任务" value={String(tasks.length)} />
      </div>

      <div className="adminToolbar">
        <label className="filterGroup">
          <span>状态</span>
          <select value={statusFilter} onChange={(event) => handleStatusChange(event.target.value)}>
            {approvalStatuses.map((status) => (
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
          <button type="button" onClick={goNext} disabled={loading || tasks.length < PAGE_SIZE}>
            下一页
          </button>
        </div>
        <button type="button" onClick={() => loadApprovals(offset)} disabled={loading}>
          <RefreshCw size={16} />
          {loading ? "刷新中" : "刷新"}
        </button>
      </div>

      <section className="approvalTable">
        <div className="approvalHeader">
          <span>任务</span>
          <span>退款信息</span>
          <span>风险</span>
          <span>状态</span>
          <span>备注</span>
          <span>操作</span>
        </div>
        {tasks.length === 0 ? (
          <AdminEmpty title="暂无审批任务" />
        ) : (
          tasks.map((task) => (
            <ApprovalRow
              key={task.id}
              task={task}
              processing={processingId === task.id}
              comment={comments[task.id] ?? ""}
              onCommentChange={(value) => setComments((items) => ({ ...items, [task.id]: value }))}
              onAction={handleAction}
            />
          ))
        )}
      </section>
    </div>
  );
}

function ApprovalRow({
  task,
  processing,
  comment,
  onCommentChange,
  onAction,
}: {
  task: ApprovalTask;
  processing: boolean;
  comment: string;
  onCommentChange: (value: string) => void;
  onAction: (taskId: number, action: "approve" | "reject") => void;
}) {
  const disabled = task.status !== "PENDING" || processing;
  return (
    <article className="approvalRow">
      <div>
        <strong>#{task.id}</strong>
        <span>
          {task.type} · {formatDate(task.created_at)}
        </span>
        <span>申请人：{task.username ?? "-"}</span>
      </div>
      <div>
        <strong>{task.order_no ?? `订单 #${task.order_id ?? "-"}`}</strong>
        <span>金额：{formatMoney(task.refund_amount)}</span>
        <span>原因：{task.refund_reason ?? "-"}</span>
      </div>
      <RiskBadge risk={task.risk_level} />
      <StatusBadge status={task.status} />
      {task.status === "PENDING" ? (
        <textarea
          className="approvalComment"
          value={comment}
          onChange={(event) => onCommentChange(event.target.value)}
          placeholder="处理备注"
          rows={2}
        />
      ) : (
        <span className="mutedText">
          {task.comment || "无备注"}
          {task.operator_username ? ` · ${task.operator_username}` : ""}
        </span>
      )}
      <div className="approvalActions">
        <button type="button" disabled={disabled} onClick={() => onAction(task.id, "approve")}>
          <CheckCircle2 size={15} />
          通过
        </button>
        <button
          className="dangerButton"
          type="button"
          disabled={disabled}
          onClick={() => onAction(task.id, "reject")}
        >
          <XCircle size={15} />
          拒绝
        </button>
      </div>
    </article>
  );
}

function RiskBadge({ risk }: { risk: string }) {
  return <span className={`riskBadge ${risk.toLowerCase()}`}>{risk}</span>;
}

function StatusBadge({ status }: { status: string }) {
  const ok = status === "APPROVED";
  const pending = status === "PENDING";
  return (
    <span className={`statusBadge ${ok ? "success" : pending ? "pending" : "danger"}`}>
      {ok ? <CheckCircle2 size={13} /> : <AlertCircle size={13} />}
      {status}
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

function AdminEmpty({ title }: { title: string }) {
  return (
    <div className="adminEmpty">
      <ClipboardCheck size={26} />
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

function formatMoney(value?: number | null) {
  if (value === null || value === undefined) {
    return "-";
  }
  return new Intl.NumberFormat("zh-CN", {
    style: "currency",
    currency: "CNY",
    maximumFractionDigits: 2,
  }).format(value);
}
