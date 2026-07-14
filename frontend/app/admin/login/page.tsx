"use client";

import { Suspense } from "react";

import { LoginExperience } from "@/app/components/LoginExperience";

export default function AdminLoginPage() {
  return (
    <Suspense fallback={<main className="loginPage adminLoginPage" />}>
      <LoginExperience variant="admin" />
    </Suspense>
  );
}
