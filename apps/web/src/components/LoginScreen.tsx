"use client";

import React, { useState } from "react";

interface LoginScreenProps {
  onLogin: (user: {
    name: string;
    email: string;
    role: "super_admin" | "tenant_sre";
    tenant: string;
  }) => void;
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    const cleanEmail = email.trim().toLowerCase();

    // Verify authentication credentials
    if (cleanEmail === "admin@platform.io" && password === "admin123") {
      onLogin({
        name: "Saurav (Super Admin)",
        email: "admin@platform.io",
        role: "super_admin",
        tenant: "Global Infrastructure (All Clusters)",
      });
    } else if (cleanEmail === "sre@acme.com" && password === "acme123") {
      onLogin({
        name: "DevOps Engineer (Client)",
        email: "sre@acme.com",
        role: "tenant_sre",
        tenant: "Acme Corp (Production VPC)",
      });
    } else {
      setErrorMsg("Invalid email or password. Please verify your credentials and try again.");
    }
  };

  return (
    <div className="login-page-container">
      <div className="login-card">
        {/* Brand Header */}
        <div className="login-header">
          <div className="login-logo-circle">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f1f5f9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
              <polyline points="2 17 12 22 22 17"></polyline>
              <polyline points="2 12 12 17 22 12"></polyline>
            </svg>
          </div>
          <h1 className="login-title">AIOps Autonomous Platform</h1>
          <p className="login-subtitle">
            Enterprise Observability &amp; Self-Healing SRE Cockpit
          </p>
          <span className="login-env-pill">SaaS Multi-Tenant Gateway &middot; v1.0</span>
        </div>

        {/* Error Notification */}
        {errorMsg && (
          <div className="login-error-banner">
            <span>⚠️ {errorMsg}</span>
          </div>
        )}

        {/* Credentials Form */}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label">
              <span>Work Email / Username</span>
            </label>
            <input
              type="text"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="form-input"
              placeholder="name@company.com"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span>Password</span>
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="form-input"
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" className="btn-login-submit">
            Sign In to Developer Cockpit &rarr;
          </button>
        </form>

        {/* Security & Compliance Footer */}
        <div className="login-footer">
          <p>🔒 End-to-End Encrypted &middot; SOC-2 Type II Certified &middot; Domain-Agnostic Core</p>
        </div>
      </div>
    </div>
  );
}
