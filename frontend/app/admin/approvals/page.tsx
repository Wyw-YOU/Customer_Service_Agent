"use client";

import { AlertCircle, CheckCircle2, ClipboardCheck, RefreshCw, XCircle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { AdminShell } from "@/app/admin/components/AdminShell";
import { ApprovalTask, approveTask, listApprovals, rejectTask } from "@/services/api";

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
  const [loading, setLoading] = useState(false);
  const [processingId, setProcessingId] = useState<number | null>(null);

  useEffect(() => {
    if (!isAuthed) {
      setTasks([]);
      return;
    }
    void loadApprovals();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthed, token]);

  async function loadApprovals() {
    if (!token) {
      return;
    }
    setError("");
    setLoading(true);
    try {
      const result = await listApprovals(token);
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
        await approveTask(token, taskId);
      } else {
        await rejectTask(token, taskId);
      }
      await loadApprovals();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "审批操作失败");
    } finally {
      setProcessingId(null);
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
        <Metric label="待处理" value={String(summary.pending)} tone={summary.pending ? "danger" : ""} />
        <Metric label="已通过" value={String(summary.approved)} tone="success" />
        <Metric label="已拒绝" value={String(summary.rejected)} />
        <Metric label="总任务" value={String(tasks.length)} />
      </div>

      <div className="adminToolbar">
        <button type="button" onClick={loadApprovals} disabled={loading}>
          <RefreshCw size={16} />
          {loading ? "刷新中" : "刷新"}
        </button>
      </div>

      <section className="approvalTable">
        <div className="approvalHeader">
          <span>任务</span>
          <span>风险</span>
          <span>状态</span>
          <span>创建时间</span>
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
  onAction,
}: {
  task: ApprovalTask;
  processing: boolean;
  onAction: (taskId: number, action: "approve" | "reject") => void;
}) {
  const disabled = task.status !== "PENDING" || processing;
  return (
    <article className="approvalRow">
      <div>
        <strong>#{task.id}</strong>
        <span>
          {task.type} · refund #{task.target_id}
        </span>
      </div>
      <RiskBadge risk={task.risk_level} />
      <StatusBadge status={task.status} />
      <span className="mutedText">{formatDate(task.created_at)}</span>
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
