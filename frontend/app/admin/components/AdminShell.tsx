"use client";

import { Bot } from "lucide-react";
import { ReactNode } from "react";

import { AppShell, AppShellState } from "@/app/components/AppShell";

type AdminShellProps = {
  active: "traces" | "approvals";
  eyebrow: string;
  title: string;
  description: string;
  children: (state: AppShellState) => ReactNode;
};

export function AdminShell({ active, eyebrow, title, description, children }: AdminShellProps) {
  return (
    <AppShell
      active={active}
      eyebrow={eyebrow}
      title={title}
      requiredRole="CUSTOMER_SERVICE"
      sidebarExtra={
        <div className="consoleHint">
          <Bot size={17} />
          <span>Trace 用于排障，Approval 用于处理售后审批。</span>
        </div>
      }
    >
      {(state) => (
        <section className="adminPage">
          <div className="adminPageHeader">
            <div>
              <h3>{title}</h3>
              <p>{description}</p>
            </div>
          </div>
          {children(state)}
        </section>
      )}
    </AppShell>
  );
}
