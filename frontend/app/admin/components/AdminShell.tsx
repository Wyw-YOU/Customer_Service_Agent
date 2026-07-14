"use client";

import { Bot } from "lucide-react";
import { ReactNode } from "react";

import { AppShell, AppShellState } from "@/app/components/AppShell";

type AdminShellProps = {
  active: "dashboard" | "service" | "traces" | "approvals" | "users";
  eyebrow: string;
  title: string;
  description: string;
  requiredRole?: "CUSTOMER_SERVICE" | "ADMIN";
  children: (state: AppShellState) => ReactNode;
};

export function AdminShell({
  active,
  eyebrow,
  title,
  description,
  requiredRole = "CUSTOMER_SERVICE",
  children,
}: AdminShellProps) {
  return (
    <AppShell
      active={active}
      eyebrow={eyebrow}
      title={title}
      requiredRole={requiredRole}
      sidebarExtra={
        <div className="consoleHint">
          <Bot size={17} />
          <span>客服处理用户会话和售后审批；管理员负责运营概览、客服管理和链路监控。</span>
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
