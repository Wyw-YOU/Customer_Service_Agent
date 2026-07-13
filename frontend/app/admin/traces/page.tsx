"use client";

import { AlertCircle, CheckCircle2, Clock3, RefreshCw, Route } from "lucide-react";
import { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import { AdminShell } from "@/app/admin/components/AdminShell";
import { getTrace, listTraces, TraceRun, TraceStep } from "@/services/api";

export default function AdminTracesPage() {
  return (
    <AdminShell
      active="traces"
      eyebrow="Agent 可观测"
      title="Trace"
      description="查看最近的 Agent Run、节点耗时、意图识别和工具执行上下文。"
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
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isAuthed) {
      setRuns([]);
      setSelectedRun(null);
      return;
    }
    void loadRuns();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthed, token]);

  async function loadRuns() {
    if (!token) {
      return;
    }
    setError("");
    setLoading(true);
    try {
      const result = await listTraces(token);
      setRuns(result);
      if (result.length > 0) {
        setSelectedRun(result[0]);
      } else {
        setSelectedRun(null);
      }
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
        <Metric label="Run 数" value={String(runs.length)} />
        <Metric label="成功" value={String(summary.successCount)} tone="success" />
        <Metric label="需关注" value={String(summary.failedCount)} tone={summary.failedCount ? "danger" : ""} />
        <Metric label="平均耗时" value={`${summary.avgLatency} ms`} />
      </div>

      <div className="adminToolbar">
        <button type="button" onClick={loadRuns} disabled={loading}>
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
        <span>{run.steps.length} steps</span>
      </div>

      <div className="stepList">
        {run.steps.length === 0 ? (
          <AdminEmpty icon={<Route size={22} />} title="暂无节点记录" compact />
        ) : (
          run.steps.map((step) => <TraceStepCard key={step.id} step={step} />)
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
      <div className="jsonGrid">
        <JsonPanel title="Input" data={step.input_data} />
        <JsonPanel title="Output" data={step.output_data} />
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
