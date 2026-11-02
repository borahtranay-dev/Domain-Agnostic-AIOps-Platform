"use client";

import React, { useState } from "react";

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
                )}

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
    </header>
  );
}
