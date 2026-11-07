"use client";

import React, { useState } from "react";
import { changeSuperAdminPassword, changeUserPassword, validatePasswordStrength } from "@/lib/authSecurity";

interface TopNavProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onSimulate: (scenario: "prometheus" | "github" | "worker") => void;
  onReset: () => void;
  isSimulating?: boolean;
  currentUser?: {
    name: string;
    email: string;
    role: "super_admin" | "tenant_sre";
    tenant: string;
  };
  onSignOut?: () => void;
}

export function TopNav({
  searchQuery,
  onSearchChange,
  onSimulate,
  onReset,
  isSimulating,
  currentUser,
  onSignOut,
}: TopNavProps) {
  const [showDemoMenu, setShowDemoMenu] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showAlertPopover, setShowAlertPopover] = useState(false);
  const [showUsersModal, setShowUsersModal] = useState(false);

  // Change Password States
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false);
  const [currentPass, setCurrentPass] = useState("");
  const [newPass, setNewPass] = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [pwError, setPwError] = useState<string | null>(null);
  const [pwSuccess, setPwSuccess] = useState<string | null>(null);

  const handleChangePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPwError(null);
    setPwSuccess(null);

    if (!currentPass || !newPass || !confirmPass) {
      setPwError("Please fill out all password fields.");
      return;
    }

    if (newPass !== confirmPass) {
      setPwError("New password and confirmation password do not match.");
      return;
    }

    if (newPass.length < 8) {
      setPwError("New password must be at least 8 characters long.");
      return;
    }

    if (currentUser?.role === "super_admin") {
      const res = changeSuperAdminPassword(currentPass, newPass);
      if (res.success) {
        setPwSuccess(res.message);
        setCurrentPass("");
        setNewPass("");
        setConfirmPass("");
      } else {
        setPwError(res.message);
      }
    } else {
      const userIdentifier = currentUser?.email || "";
      const res = changeUserPassword(userIdentifier, currentPass, newPass);
      if (res.success) {
        setPwSuccess(res.message);
        setCurrentPass("");
        setNewPass("");
        setConfirmPass("");
      } else {
        setPwError(res.message);
      }
    }
  };

  // Helper to get registered users from localStorage
  const getRegisteredUsers = () => {
    if (typeof window === "undefined") return [];
    try {
      const data = localStorage.getItem("aiops_registered_users");
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  };

  return (
    <header className="topnav-bar">
      {/* Left: Brand title & breadcrumb */}
      <div className="topnav-left">
        <div className="topnav-brand">
          <svg className="brand-svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e4e4e7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          <span className="brand-text">AIOps Autonomous SRE Console</span>
          <span className="brand-badge">Prod v1.0</span>
        </div>
      </div>

      {/* Center: Command Palette Search Bar */}
      <div className="topnav-center">
        <div className="search-bar-wrap">
          <svg className="search-symbol-svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#71717a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            type="text"
            className="search-input-field"
            placeholder="Search incidents, services, traces, runbooks..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
          />
          <kbd className="search-kbd">⌘K</kbd>
        </div>
      </div>

      {/* Right: Quick Demo Controls + User Profile */}
      <div className="topnav-right">
        {/* 1-Click Interactive Demo Simulation Dropdown */}
        <div className="demo-dropdown-wrap">
          <button
            className="btn-demo-trigger"
            onClick={() => setShowDemoMenu(!showDemoMenu)}
            title="Inject Synthetic Telemetry Alerts"
          >
            <span className="pulse-dot-green"></span>
            <span>⚡ Simulate Incident</span>
            <span className="caret-arrow">{showDemoMenu ? "▲" : "▼"}</span>
          </button>

          {showDemoMenu && (
            <div className="demo-popover-card">
              <div className="demo-popover-header">
                <strong>Fault Injection &amp; Telemetry Scenarios</strong>
                <p>Trigger synthetic failure alerts to observe live RAG self-healing:</p>
              </div>
              <div className="demo-popover-list">
                <button
                  onClick={() => {
                    onSimulate("prometheus");
                    setShowDemoMenu(false);
                  }}
                  disabled={isSimulating}
                  className="demo-popover-btn"
                >
                  <span className="btn-bullet red">●</span>
                  <div className="btn-desc">
                    <strong>Prometheus DB Pool Exhaustion</strong>
                    <small>QueuePool saturation &middot; Matches RB-001 Scale</small>
                  </div>
                </button>

                <button
                  onClick={() => {
                    onSimulate("github");
                    setShowDemoMenu(false);
                  }}
                  disabled={isSimulating}
                  className="demo-popover-btn"
                >
                  <span className="btn-bullet orange">●</span>
                  <div className="btn-desc">
                    <strong>GitHub Deployment Failure</strong>
                    <small>Container Probe Timeout &middot; Matches RB-006 Rollback</small>
                  </div>
                </button>

                <button
                  onClick={() => {
                    onSimulate("worker");
                    setShowDemoMenu(false);
                  }}
                  disabled={isSimulating}
                  className="demo-popover-btn"
                >
                  <span className="btn-bullet yellow">●</span>
                  <div className="btn-desc">
                    <strong>Redis Queue Worker Timeout</strong>
                    <small>Consumer dropped &middot; Matches RB-007 Restart</small>
                  </div>
                </button>

                <div className="demo-popover-divider"></div>

                <button
                  onClick={() => {
                    onReset();
                    setShowDemoMenu(false);
                  }}
                  className="demo-popover-btn reset"
                >
                  <span className="btn-bullet blue">🔄</span>
                  <div className="btn-desc">
                    <strong>Reset Benchmark Incidents</strong>
                    <small>Restore clean initial demo state</small>
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Notifications Icon with Interactive Dropdown */}
        <div className="notify-dropdown-wrap" style={{ position: "relative" }}>
          <button
            onClick={() => {
              setShowAlertPopover(!showAlertPopover);
              setShowAuthModal(false);
              setShowDemoMenu(false);
            }}
            className="topnav-icon-btn"
            title="System Alert Notifications"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
            <span className="bell-badge-dot">1</span>
          </button>

          {showAlertPopover && (
            <div className="demo-popover-card" style={{ width: "310px", right: 0 }}>
              <div className="demo-popover-header">
                <strong>Active Telemetry Alerts (1)</strong>
                <p>Real-time Prometheus Alertmanager stream</p>
              </div>
              <div className="demo-popover-list">
                <div className="demo-popover-btn" style={{ cursor: "default" }}>
                  <span className="btn-bullet red">●</span>
                  <div className="btn-desc">
                    <strong style={{ color: "#f87171" }}>CRITICAL: DB Pool Saturation</strong>
                    <small>payment-api &middot; QueuePool limit 10 reached</small>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* SRE User Profile */}
        <div className="profile-dropdown-wrap" style={{ position: "relative" }}>
          <div
            onClick={() => {
              setShowAuthModal(!showAuthModal);
              setShowAlertPopover(false);
              setShowDemoMenu(false);
            }}
            className="topnav-user-profile"
            title="Click to view Role & Tenant Scope"
            style={{ cursor: "pointer" }}
          >
            <div className="avatar-circle">
              {currentUser?.role === "super_admin" ? "SA" : "SR"}
            </div>
            <div className="user-details-col">
              <span className="user-name">{currentUser?.name || "Saurav (Super Admin)"}</span>
              <span className="user-role">{currentUser?.role === "super_admin" ? "Platform Owner" : currentUser?.tenant}</span>
            </div>
            <span className="online-status-dot" title="Authenticated & Active"></span>
          </div>

          {showAuthModal && (
            <div className="demo-popover-card" style={{ width: "300px", right: 0 }}>
              <div className="demo-popover-header">
                <strong>Session Security Context</strong>
                <p>Role-Based Access Control (RBAC) Active</p>
              </div>
              <div className="demo-popover-list">
                <div style={{ padding: "0.4rem 0.2rem", fontSize: "0.74rem", color: "#a1a1aa", lineHeight: 1.5 }}>
                  <div>Account: <strong style={{ color: "#f4f4f5" }}>{currentUser?.email || "admin@platform.io"}</strong></div>
                  <div>Role: <span style={{ color: currentUser?.role === "super_admin" ? "#38bdf8" : "#34d399", fontWeight: 700 }}>{currentUser?.role === "super_admin" ? "Super Admin (Platform Owner)" : "Client SRE Engineer"}</span></div>
                  <div>Tenant Scope: <code style={{ color: "#e4e4e7", background: "#1c1c22", padding: "0.1rem 0.3rem", borderRadius: "3px" }}>{currentUser?.tenant || "Primary Tenant: Acme Corp"}</code></div>
                  <div style={{ marginTop: "0.25rem", fontSize: "0.68rem", color: "#71717a" }}>
                    Status: Strict Tenant Isolation Active &middot; Zero cross-tenant leakage
                  </div>
                </div>

                <div className="demo-popover-divider"></div>

                {currentUser?.role === "super_admin" && (
                  <>
                    <button
                      onClick={() => {
                        setShowUsersModal(true);
                        setShowAuthModal(false);
                      }}
                      className="demo-popover-btn"
                    >
                      <span className="btn-bullet blue">👥</span>
                      <div className="btn-desc">
                        <strong>Registered Users &amp; Projects</strong>
                        <small>Students &amp; devs monitoring their sites</small>
                      </div>
                    </button>
                    <button
                      onClick={() => {
                        alert("Simulated: Platform Ingestion Token: aiops_live_sk_948f21e0b");
                        setShowAuthModal(false);
                      }}
                      className="demo-popover-btn"
                    >
                      <span className="btn-bullet yellow">🔑</span>
                      <div className="btn-desc">
                        <strong>Platform Master API Key</strong>
                        <small>Vendor ingestion root key</small>
                      </div>
                    </button>
                  </>
                )}

                {/* Change Password for All Logged-in Users & Super Admin */}
                <button
                  onClick={() => {
                    setShowChangePasswordModal(true);
                    setShowAuthModal(false);
                    setPwError(null);
                    setPwSuccess(null);
                    setCurrentPass("");
                    setNewPass("");
                    setConfirmPass("");
                  }}
                  className="demo-popover-btn"
                >
                  <span className="btn-bullet blue">🔒</span>
                  <div className="btn-desc">
                    <strong>Change Password</strong>
                    <small>{currentUser?.role === "super_admin" ? "Update master admin password" : "Update your workspace password"}</small>
                  </div>
                </button>

                <button
                  onClick={() => {
                    onSignOut?.();
                    setShowAuthModal(false);
                  }}
                  className="demo-popover-btn reset"
                >
                  <span className="btn-bullet red">⏻</span>
                  <div className="btn-desc">
                    <strong style={{ color: "#f87171" }}>Sign Out</strong>
                    <small>Terminate current authenticated session</small>
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Super Admin Modal: Registered Users & Monitored Sites */}
      {showUsersModal && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          backgroundColor: "rgba(0, 0, 0, 0.75)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 9999,
          backdropFilter: "blur(4px)"
        }}>
          <div style={{
            background: "#0f0f12",
            border: "1px solid #27272e",
            borderRadius: "12px",
            width: "90%",
            maxWidth: "600px",
            padding: "1.5rem",
            boxShadow: "0 20px 50px rgba(0,0,0,0.8)",
            color: "#f4f4f5"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: "1px solid #23232a", paddingBottom: "0.75rem" }}>
              <div>
                <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700, color: "#f8fafc" }}>
                  👑 Platform Super Admin &middot; User Directory
                </h3>
                <p style={{ margin: "0.2rem 0 0 0", fontSize: "0.75rem", color: "#94a3b8" }}>
                  Students &amp; developers actively monitoring projects on your platform
                </p>
              </div>
              <button
                onClick={() => setShowUsersModal(false)}
                style={{
                  background: "#27272e",
                  border: "none",
                  color: "#cbd5e1",
                  borderRadius: "6px",
                  padding: "0.3rem 0.6rem",
                  cursor: "pointer",
                  fontSize: "0.8rem"
                }}
              >
                ✕ Close
              </button>
            </div>

            <div style={{ maxHeight: "350px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "0.6rem" }}>
              {/* Default Mock SRE */}
              <div style={{ background: "#16161a", border: "1px solid #23232a", borderRadius: "8px", padding: "0.75rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <strong style={{ fontSize: "0.85rem", color: "#38bdf8" }}>DevOps SRE (Acme Corp)</strong>
                  <span style={{ fontSize: "0.68rem", background: "#1e293b", color: "#94a3b8", padding: "0.15rem 0.45rem", borderRadius: "4px" }}>Default Tenant</span>
                </div>
                <div style={{ fontSize: "0.74rem", color: "#cbd5e1", marginTop: "0.3rem" }}>
                  Email: <code>sre@acme.com</code> &middot; Scope: Production VPC &amp; Kubernetes Clusters
                </div>
              </div>

              {/* Dynamic Users from LocalStorage */}
              {getRegisteredUsers().length === 0 ? (
                <div style={{ padding: "1.5rem", textAlign: "center", color: "#71717a", fontSize: "0.78rem" }}>
                  No external users registered yet. New students or developers who sign up with their Mobile No. or Email will appear here in real time.
                </div>
              ) : (
                getRegisteredUsers().map((u: any, idx: number) => (
                  <div key={idx} style={{ background: "#16161a", border: "1px solid #27272e", borderRadius: "8px", padding: "0.75rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <strong style={{ fontSize: "0.85rem", color: "#34d399" }}>{u.name}</strong>
                      <span style={{ fontSize: "0.68rem", background: "rgba(16, 185, 129, 0.15)", color: "#34d399", padding: "0.15rem 0.45rem", borderRadius: "4px" }}>Active Workspace</span>
                    </div>
                    <div style={{ fontSize: "0.74rem", color: "#e2e8f0", marginTop: "0.3rem" }}>
                      Contact: <code>{u.mobile || u.email}</code>
                    </div>
                    <div style={{ fontSize: "0.72rem", color: "#94a3b8", marginTop: "0.2rem" }}>
                      Monitored Project: <strong style={{ color: "#f1f5f9" }}>{u.projectWebsite || u.tenant}</strong>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div style={{ marginTop: "1rem", paddingTop: "0.75rem", borderTop: "1px solid #23232a", display: "flex", justifyContent: "space-between", fontSize: "0.7rem", color: "#64748b" }}>
              <span>Total Workspaces: {1 + getRegisteredUsers().length}</span>
              <span>Exclusive Super Admin: Saurav</span>
            </div>
          </div>
        </div>
      )}

      {/* Change Password Modal (For Super Admin and All Tenant Users) */}
      {showChangePasswordModal && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          backgroundColor: "rgba(0, 0, 0, 0.75)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 9999,
          backdropFilter: "blur(4px)"
        }}>
          <div style={{
            background: "#0f0f12",
            border: "1px solid #27272e",
            borderRadius: "12px",
            width: "90%",
            maxWidth: "460px",
            padding: "1.5rem",
            boxShadow: "0 20px 50px rgba(0,0,0,0.8)",
            color: "#f4f4f5"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: "1px solid #23232a", paddingBottom: "0.75rem" }}>
              <div>
                <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700, color: "#f8fafc" }}>
                  🔒 Update Security Password
                </h3>
                <p style={{ margin: "0.2rem 0 0 0", fontSize: "0.75rem", color: "#94a3b8" }}>
                  Account: <strong style={{ color: "#38bdf8" }}>{currentUser?.email || "admin@platform.io"}</strong>
                </p>
              </div>
              <button
                onClick={() => setShowChangePasswordModal(false)}
                style={{
                  background: "#27272e",
                  border: "none",
                  color: "#cbd5e1",
                  borderRadius: "6px",
                  padding: "0.3rem 0.6rem",
                  cursor: "pointer",
                  fontSize: "0.8rem"
                }}
              >
                ✕ Close
              </button>
            </div>

            {pwError && (
              <div style={{ background: "rgba(239, 68, 68, 0.15)", border: "1px solid rgba(239, 68, 68, 0.3)", color: "#fca5a5", padding: "0.6rem 0.8rem", borderRadius: "6px", fontSize: "0.8rem", marginBottom: "1rem" }}>
                {pwError}
              </div>
            )}

            {pwSuccess && (
              <div style={{ background: "rgba(16, 185, 129, 0.15)", border: "1px solid rgba(16, 185, 129, 0.3)", color: "#6ee7b7", padding: "0.6rem 0.8rem", borderRadius: "6px", fontSize: "0.8rem", marginBottom: "1rem" }}>
                {pwSuccess}
              </div>
            )}

            <form onSubmit={handleChangePasswordSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.9rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.78rem", color: "#94a3b8", marginBottom: "0.3rem", fontWeight: 600 }}>
                  Current Password
                </label>
                <input
                  type="password"
                  required
                  placeholder="Enter current password"
                  value={currentPass}
                  onChange={(e) => setCurrentPass(e.target.value)}
                  style={{
                    width: "100%",
                    background: "#18181b",
                    border: "1px solid #27272e",
                    borderRadius: "6px",
                    padding: "0.55rem 0.75rem",
                    color: "#f4f4f5",
                    fontSize: "0.85rem",
                    outline: "none"
                  }}
                />
              </div>

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
                  <label style={{ fontSize: "0.78rem", color: "#94a3b8", fontWeight: 600 }}>
                    New Password
                  </label>
                  <span style={{ fontSize: "0.68rem", color: "#71717a" }}>Enterprise Strong Policy</span>
                </div>
                <input
                  type="password"
                  required
                  placeholder="Enter new strong password"
                  value={newPass}
                  onChange={(e) => setNewPass(e.target.value)}
                  style={{
                    width: "100%",
                    background: "#18181b",
                    border: `1px solid ${newPass.length > 0 ? (validatePasswordStrength(newPass).isValid ? "#22c55e" : "#f59e0b") : "#27272e"}`,
                    borderRadius: "6px",
                    padding: "0.55rem 0.75rem",
                    color: "#f4f4f5",
                    fontSize: "0.85rem",
                    outline: "none"
                  }}
                />

                {/* Real-time Checklist */}
                {newPass.length > 0 && (() => {
                  const s = validatePasswordStrength(newPass);
                  return (
                    <div style={{
                      marginTop: "0.45rem",
                      padding: "0.5rem 0.6rem",
                      background: s.isValid ? "rgba(34, 197, 94, 0.08)" : "#18181b",
                      border: `1px solid ${s.isValid ? "rgba(34, 197, 94, 0.3)" : "#27272e"}`,
                      borderRadius: "6px",
                      fontSize: "0.68rem",
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr",
                      gap: "0.2rem 0.5rem"
                    }}>
                      <span style={{ color: s.hasMinLength ? "#34d399" : "#71717a", display: "flex", alignItems: "center", gap: "4px" }}>
                        {s.hasMinLength ? "✓" : "○"} Min. 8 Characters
                      </span>
                      <span style={{ color: s.hasUpperCase ? "#34d399" : "#71717a", display: "flex", alignItems: "center", gap: "4px" }}>
                        {s.hasUpperCase ? "✓" : "○"} 1 Uppercase (A-Z)
                      </span>
                      <span style={{ color: s.hasLowerCase ? "#34d399" : "#71717a", display: "flex", alignItems: "center", gap: "4px" }}>
                        {s.hasLowerCase ? "✓" : "○"} 1 Lowercase (a-z)
                      </span>
                      <span style={{ color: s.hasNumber ? "#34d399" : "#71717a", display: "flex", alignItems: "center", gap: "4px" }}>
                        {s.hasNumber ? "✓" : "○"} 1 Number (0-9)
                      </span>
                      <span style={{ color: s.hasSpecialChar ? "#34d399" : "#71717a", display: "flex", alignItems: "center", gap: "4px", gridColumn: "span 2" }}>
                        {s.hasSpecialChar ? "✓" : "○"} 1 Special Symbol (!@#$%...)
                      </span>
                    </div>
                  );
                })()}
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.78rem", color: "#94a3b8", marginBottom: "0.3rem", fontWeight: 600 }}>
                  Confirm New Password
                </label>
                <input
                  type="password"
                  required
                  placeholder="Re-enter new password"
                  value={confirmPass}
                  onChange={(e) => setConfirmPass(e.target.value)}
                  style={{
                    width: "100%",
                    background: "#18181b",
                    border: "1px solid #27272e",
                    borderRadius: "6px",
                    padding: "0.55rem 0.75rem",
                    color: "#f4f4f5",
                    fontSize: "0.85rem",
                    outline: "none"
                  }}
                />
              </div>

              <div style={{ display: "flex", gap: "0.6rem", marginTop: "0.5rem" }}>
                <button
                  type="button"
                  onClick={() => setShowChangePasswordModal(false)}
                  style={{
                    flex: 1,
                    background: "#27272e",
                    border: "none",
                    borderRadius: "6px",
                    padding: "0.6rem",
                    color: "#cbd5e1",
                    fontSize: "0.85rem",
                    cursor: "pointer",
                    fontWeight: 600
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    flex: 2,
                    background: "#0284c7",
                    border: "none",
                    borderRadius: "6px",
                    padding: "0.6rem",
                    color: "#ffffff",
                    fontSize: "0.85rem",
                    cursor: "pointer",
                    fontWeight: 600
                  }}
                >
                  Update &amp; Secure Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </header>
  );
}
