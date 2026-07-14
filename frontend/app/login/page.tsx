"use client";

import { Suspense } from "react";

import { LoginExperience } from "@/app/components/LoginExperience";

export default function LoginPage() {
  return (
    <Suspense fallback={<main className="loginPage" />}>
      <LoginExperience variant="user" />
    </Suspense>
  );
}
