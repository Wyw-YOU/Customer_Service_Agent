"use client";

import { AlertCircle, CheckCircle2, Clock3, RefreshCw, Route } from "lucide-react";
import { ReactNode, useEffect, useMemo, useState } from "react";

import { AdminShell } from "@/app/admin/components/AdminShell";
import { getTrace, listTraces, ToolLog, TraceRun, TraceStep } from "@/services/api";

const PAGE_SIZE = 20;
const traceStatuses = [
  { label: "全部状态", value: "" },
  { label: "已完成", value: "COMPLETED" },
  { label: "有警告", value: "COMPLETED_WITH_WARNINGS" },
  { label: "运行中", value: "RUNNING" },
];

export default function AdminTracesPage() {
  return (
    <AdminShell
      active="traces"
      eyebrow="Agent 可观测"
      title="Trace"
      description="查看最近的 Agent Run、节点耗时、意图识别和工具执行上下文。"
      requiredRole="ADMIN"
    >
      {({ token, isAuthed, setError }) => (
        <TraceWorkspace token={token} isAuthed={isAuthed} setError={setError} />
      )}
    </AdminShell>
  );
}

function TraceWorkspace({
  token,
  isAuthed,
  setError,
}: {
  token: string;
  isAuthed: boolean;
  setError: (message: string) => void;
}) {
  const [runs, setRuns] = useState<TraceRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<TraceRun | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isAuthed) {
      setRuns([]);
      setSelectedRun(null);
      return;
    }
    void loadRuns(offset);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthed, token, statusFilter, offset]);

  async function loadRuns(nextOffset = offset) {
    if (!token) {
      return;
    }
    setError("");
    setLoading(true);
    try {
      const result = await listTraces(token, {
        status: statusFilter || undefined,
        limit: PAGE_SIZE,
        offset: nextOffset,
      });
      setRuns(result);
      setSelectedRun(result[0] ?? null);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Trace 加载失败");
    } finally {
      setLoading(false);
    }
  }

  async function selectRun(runId: number) {
    setError("");
    try {
      const result = await getTrace(token, runId);
      setSelectedRun(result);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Trace 详情加载失败");
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
    if (runs.length === PAGE_SIZE) {
      setOffset((value) => value + PAGE_SIZE);
    }
  }

  const summary = useMemo(() => {
    const successCount = runs.filter((run) => run.status === "COMPLETED").length;
    const failedCount = runs.filter((run) => run.status !== "COMPLETED").length;
    const avgLatency =
      runs.length === 0
        ? 0
        : Math.round(
            runs.reduce((total, run) => total + (run.latency_ms ?? 0), 0) / Math.max(runs.length, 1),
          );
    return { successCount, failedCount, avgLatency };
  }, [runs]);

  if (!isAuthed) {
    return <AdminEmpty icon={<Route size={28} />} title="登录后查看 Trace" />;
  }

  return (
    <div className="adminGrid">
      <div className="adminMetrics">
        <Metric label="本页 Run" value={String(runs.length)} />
        <Metric label="成功" value={String(summary.successCount)} tone="success" />
        <Metric label="需关注" value={String(summary.failedCount)} tone={summary.failedCount ? "danger" : ""} />
        <Metric label="平均耗时" value={`${summary.avgLatency} ms`} />
      </div>

      <div className="adminToolbar">
        <label className="filterGroup">
          <span>状态</span>
          <select value={statusFilter} onChange={(event) => handleStatusChange(event.target.value)}>
            {traceStatuses.map((status) => (
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
          <button type="button" onClick={goNext} disabled={loading || runs.length < PAGE_SIZE}>
            下一页
          </button>
        </div>
        <button type="button" onClick={() => loadRuns(offset)} disabled={loading}>
          <RefreshCw size={16} />
          {loading ? "刷新中" : "刷新"}
        </button>
      </div>

      <div className="traceLayout">
        <section className="adminList">
          {runs.length === 0 ? (
            <AdminEmpty icon={<Route size={24} />} title="暂无 Trace" />
          ) : (
            runs.map((run) => (
              <button
                key={run.id}
                type="button"
                className={selectedRun?.id === run.id ? "listItem active" : "listItem"}
                onClick={() => selectRun(run.id)}
              >
                <span className="itemTitle">{run.query || `Run #${run.id}`}</span>
                <span className="itemMeta">
                  <StatusBadge status={run.status} />
                  <span>#{run.id}</span>
                  <span>{formatDate(run.created_at)}</span>
                </span>
              </button>
            ))
          )}
        </section>

        <section className="adminDetail">
          {selectedRun ? <TraceDetail run={selectedRun} /> : <AdminEmpty icon={<Route size={24} />} title="选择一个 Run" />}
        </section>
      </div>
    </div>
  );
}

function TraceDetail({ run }: { run: TraceRun }) {
  const steps = run.steps ?? [];
  const toolLogs = run.tool_logs ?? [];

  return (
    <div className="detailStack">
      <div className="detailHeader">
        <div>
          <h4>{run.query || `Run #${run.id}`}</h4>
          <p>
            会话 #{run.conversation_id} · {run.intent ?? "未识别意图"} · {formatDate(run.created_at)}
          </p>
        </div>
        <StatusBadge status={run.status} />
      </div>

      <div className="detailFacts">
        <span>
          <Clock3 size={14} />
          {run.latency_ms ?? 0} ms
        </span>
        <span>confidence {formatConfidence(run.confidence)}</span>
        <span>{steps.length} steps</span>
        <span>{toolLogs.length} tools</span>
      </div>
      {run.error_message ? <div className="traceError">{run.error_message}</div> : null}

      <div className="stepList">
        {steps.length === 0 ? (
          <AdminEmpty icon={<Route size={22} />} title="暂无节点记录" compact />
        ) : (
          steps.map((step) => <TraceStepCard key={step.id} step={step} />)
        )}
      </div>

      <div className="stepList">
        <div className="subsectionTitle">Tool Logs</div>
        {toolLogs.length === 0 ? (
          <AdminEmpty icon={<Route size={22} />} title="暂无工具调用记录" compact />
        ) : (
          toolLogs.map((log) => <ToolLogCard key={log.id} log={log} />)
        )}
      </div>
    </div>
  );
}

function TraceStepCard({ step }: { step: TraceStep }) {
  return (
    <article className="stepCard">
      <div className="stepHeader">
        <strong>{step.node_name}</strong>
        <span>{step.duration_ms ?? 0} ms</span>
      </div>
      {step.error_message ? <div className="traceError inline">{step.error_message}</div> : null}
      <div className="jsonGrid">
        <JsonPanel title="Input" data={step.input_data} />
        <JsonPanel title="Output" data={step.output_data} />
      </div>
    </article>
  );
}

function ToolLogCard({ log }: { log: ToolLog }) {
  return (
    <article className="stepCard">
      <div className="stepHeader">
        <strong>{log.tool_name}</strong>
        <span>
          {log.status} · {log.latency_ms ?? 0} ms
        </span>
      </div>
      {log.error_message ? <div className="traceError inline">{log.error_message}</div> : null}
      <div className="jsonGrid">
        <JsonPanel title="Input" data={log.input_data} />
        <JsonPanel title="Output" data={log.output_data} />
      </div>
    </article>
  );
}

function JsonPanel({ title, data }: { title: string; data?: Record<string, unknown> | null }) {
  return (
    <div className="jsonPanel">
      <span>{title}</span>
      <pre>{data ? JSON.stringify(data, null, 2) : "{}"}</pre>
    </div>
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

function StatusBadge({ status }: { status: string }) {
  const ok = status === "SUCCESS" || status === "COMPLETED" || status === "APPROVED";
  const pending = status === "RUNNING" || status === "PENDING";
  return (
    <span className={`statusBadge ${ok ? "success" : pending ? "pending" : "danger"}`}>
      {ok ? <CheckCircle2 size={13} /> : <AlertCircle size={13} />}
      {status}
    </span>
  );
}

function AdminEmpty({
  icon,
  title,
  compact = false,
}: {
  icon: ReactNode;
  title: string;
  compact?: boolean;
}) {
  return (
    <div className={compact ? "adminEmpty compact" : "adminEmpty"}>
      {icon}
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

function formatConfidence(value?: number | null) {
  if (value === null || value === undefined) {
    return "-";
  }
  return `${Math.round(value * 100)}%`;
}
