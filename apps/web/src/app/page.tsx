"use client";

import React, { useState } from "react";
import { LoginScreen } from "../components/LoginScreen";
import {
  Incident,
  Evidence,
  Diagnosis,
  RemediationPlan,
} from "../types";
import {
  INITIAL_INCIDENTS,
  INITIAL_EVIDENCE,
  INITIAL_DIAGNOSES,
  INITIAL_REMEDIATION_PLANS,
} from "../lib/mockData";

export default function CleanDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [currentUser, setCurrentUser] = useState<{
    name: string;
    email: string;
    role: "super_admin" | "tenant_sre";
    tenant: string;
  }>({
    name: "Saurav (Super Admin)",
    email: "admin@platform.io",
    role: "super_admin",
    tenant: "Global Infrastructure (All Clusters)",
  });

  // User-Specific Theme State (Default: light)
  const [theme, setTheme] = useState<"light" | "dark">("light");

  // Load user's personal theme preference upon login
  const handleUserLogin = (user: {
    name: string;
    email: string;
    role: "super_admin" | "tenant_sre";
    tenant: string;
  }) => {
    setCurrentUser(user);
    setIsAuthenticated(true);

    try {
      // Look up this specific user's saved theme preference
      const savedUserTheme = localStorage.getItem(`aiops_theme_${user.email.toLowerCase()}`) as "light" | "dark" | null;
      if (savedUserTheme === "dark" || savedUserTheme === "light") {
        setTheme(savedUserTheme);
      } else {
        setTheme("light"); // Default is light mode
      }
    } catch {
      setTheme("light");
    }

    showToast(`✓ Welcome, ${user.name}`);
  };

  // Toggle theme inside dashboard and save specifically to this user's account
  const toggleTheme = () => {
    const nextTheme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);

    if (currentUser && currentUser.email) {
      try {
        localStorage.setItem(`aiops_theme_${currentUser.email.toLowerCase()}`, nextTheme);
      } catch (e) {
        console.error("Failed to save user theme preference", e);
      }
    }
  };

  const isDark = theme === "dark";

  // Color theme tokens for dashboard
  const colors = {
    bg: isDark ? "#09090b" : "#f8fafc",
    cardBg: isDark ? "#121215" : "#ffffff",
    cardBorder: isDark ? "#27272a" : "#e2e8f0",
    headerBg: isDark ? "#121215" : "#ffffff",
    headerBorder: isDark ? "#27272a" : "#e2e8f0",
    textPrimary: isDark ? "#f4f4f5" : "#0f172a",
    textSecondary: isDark ? "#a1a1aa" : "#475569",
    textMuted: isDark ? "#71717a" : "#94a3b8",
    inputBg: isDark ? "#18181b" : "#ffffff",
    inputBorder: isDark ? "#27272a" : "#cbd5e1",
    subtleBoxBg: isDark ? "#18181b" : "#f8fafc",
    subtleBoxBorder: isDark ? "#23232a" : "#e2e8f0",
    activeItemBg: isDark ? "#1c1c22" : "#f1f5f9",
    codeBg: isDark ? "#0d0d10" : "#f1f5f9",
    shadow: isDark ? "0 10px 25px rgba(0,0,0,0.5)" : "0 2px 8px rgba(0,0,0,0.04)",
  };

  const [activeTab, setActiveTab] = useState<"incidents" | "services">("incidents");
  const [incidents, setIncidents] = useState<Incident[]>(INITIAL_INCIDENTS);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>("INC-8921");
  const [evidenceMap] = useState<Record<string, Evidence[]>>(INITIAL_EVIDENCE);
  const [diagnosesMap] = useState<Record<string, Diagnosis>>(INITIAL_DIAGNOSES);
  const [plansMap, setPlansMap] = useState<Record<string, RemediationPlan>>(INITIAL_REMEDIATION_PLANS);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [showUsersModal, setShowUsersModal] = useState(false);

  // Simple Monitored Services List
  const servicesList = [
    { name: "API Gateway & Ingress", status: "Healthy", latency: "14ms", uptime: "99.99%", desc: "Reverse proxy & public router" },
    { name: "Auth & Identity Engine", status: "Healthy", latency: "8ms", uptime: "99.98%", desc: "OAuth 2.0 & JWT verification" },
    { name: "PostgreSQL Primary Cluster", status: "Needs Attention", latency: "42ms", uptime: "99.90%", desc: "Connection pool saturation detected" },
    { name: "Redis Cache & Event Broker", status: "Healthy", latency: "1.2ms", uptime: "100%", desc: "Queue broker & session cache" },
    { name: "AI Self-Healing Engine", status: "Active", latency: "850ms", uptime: "99.95%", desc: "DeepSeek-R1 runbook diagnostic brain" },
  ];

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const getRegisteredUsers = () => {
    if (typeof window === "undefined") return [];
    try {
      const data = localStorage.getItem("aiops_registered_users");
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  };

  // Simulate new incident
  const handleSimulateAlert = () => {
    setIsSimulating(true);
    showToast("⚡ Simulating incoming Prometheus alert...");
    setTimeout(() => {
      const newId = `INC-${Math.floor(1000 + Math.random() * 9000)}`;
      const newInc: Incident = {
        id: newId,
        title: "Redis Memory Saturation Warning",
        service_id: "redis-cluster",
        severity: "high",
        status: "open",
        opened_at: new Date().toISOString(),
        event_ids: [`EVT-${newId}`],
      };
      setIncidents((prev) => [newInc, ...prev]);
      setSelectedIncidentId(newId);
      setIsSimulating(false);
      showToast(`✓ New alert received: ${newId} (Redis Warning)`);
    }, 800);
  };

  // Approve remediation
  const handleApprove = async (incidentId: string) => {
    setIncidents((prev) =>
      prev.map((inc) => (inc.id === incidentId ? { ...inc, status: "executing" } : inc))
    );
    showToast("Applying AI remediation fix...");

    setTimeout(() => {
      setIncidents((prev) =>
        prev.map((inc) =>
          inc.id === incidentId
            ? { ...inc, status: "resolved", resolved_at: new Date().toISOString() }
            : inc
        )
      );
      setPlansMap((prev) => {
        if (!prev[incidentId]) return prev;
        return {
          ...prev,
          [incidentId]: { ...prev[incidentId], status: "completed" },
        };
      });
      showToast(`✅ Fixed & Verified! Incident ${incidentId} successfully resolved.`);
    }, 1200);
  };

  // Reject remediation
  const handleReject = (incidentId: string) => {
    setIncidents((prev) =>
      prev.map((inc) => (inc.id === incidentId ? { ...inc, status: "open" } : inc))
    );
    showToast(`❌ Remediation rejected for ${incidentId}. Kept in open state.`);
  };

  const selectedIncident = incidents.find((i) => i.id === selectedIncidentId) || incidents[0];
  const currentDiagnosis = selectedIncident ? diagnosesMap[selectedIncident.id] : undefined;
  const currentPlan = selectedIncident ? plansMap[selectedIncident.id] : undefined;
  const currentEvidence = selectedIncident ? evidenceMap[selectedIncident.id] || [] : [];

  const filteredIncidents = incidents.filter(
    (inc) =>
      inc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (inc.service_id || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const activeCount = incidents.filter((i) => i.status !== "resolved").length;
  const resolvedCount = incidents.filter((i) => i.status === "resolved").length;

  // Clean Login Screen Gate (No theme switcher before login)
  if (!isAuthenticated) {
    return (
      <LoginScreen onLogin={handleUserLogin} />
    );
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: colors.bg,
      color: colors.textPrimary,
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
      display: "flex",
      flexDirection: "column",
      transition: "background 0.2s ease, color 0.2s ease",
    }}>
      {/* Toast Notification */}
      {toastMessage && (
        <div style={{
          position: "fixed",
          top: "20px",
          right: "20px",
          background: isDark ? "#18181b" : "#ffffff",
          border: `1px solid ${colors.cardBorder}`,
          color: colors.textPrimary,
          padding: "0.75rem 1.25rem",
          borderRadius: "8px",
          boxShadow: isDark ? "0 10px 25px rgba(0,0,0,0.5)" : "0 10px 25px rgba(0,0,0,0.1)",
          fontSize: "0.85rem",
          fontWeight: 500,
          zIndex: 9999,
          display: "flex",
          alignItems: "center",
          gap: "8px"
        }}>
          <span>{toastMessage}</span>
        </div>
      )}

      {/* 1. CLEAN TOP NAVBAR */}
      <header style={{
        background: colors.headerBg,
        borderBottom: `1px solid ${colors.headerBorder}`,
        padding: "0.85rem 1.75rem",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        boxShadow: isDark ? "none" : "0 1px 3px rgba(0,0,0,0.02)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1.25rem" }}>
          {/* Logo */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <div style={{
              width: "32px",
              height: "32px",
              background: "#2563eb",
              borderRadius: "6px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 800,
              color: "#ffffff",
              fontSize: "1rem"
            }}>
              A
            </div>
            <div>
              <span style={{ fontWeight: 700, fontSize: "1rem", letterSpacing: "-0.01em", color: colors.textPrimary }}>AIOps Platform</span>
              <span style={{ fontSize: "0.7rem", color: colors.textMuted, marginLeft: "0.5rem" }}>Self-Healing SRE</span>
            </div>
          </div>

          {/* Simple Tab Nav */}
          <nav style={{ display: "flex", gap: "0.5rem", marginLeft: "1.5rem" }}>
            <button
              onClick={() => setActiveTab("incidents")}
              style={{
                background: activeTab === "incidents" ? (isDark ? "#27272a" : "#f1f5f9") : "transparent",
                color: activeTab === "incidents" ? colors.textPrimary : colors.textSecondary,
                border: "none",
                padding: "0.45rem 0.9rem",
                borderRadius: "6px",
                fontSize: "0.85rem",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Incidents &amp; Alerts ({activeCount})
            </button>
            <button
              onClick={() => setActiveTab("services")}
              style={{
                background: activeTab === "services" ? (isDark ? "#27272a" : "#f1f5f9") : "transparent",
                color: activeTab === "services" ? colors.textPrimary : colors.textSecondary,
                border: "none",
                padding: "0.45rem 0.9rem",
                borderRadius: "6px",
                fontSize: "0.85rem",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Monitored Services ({servicesList.length})
            </button>
          </nav>
        </div>

        {/* Right Nav Actions */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.85rem" }}>
          {/* USER-SPECIFIC THEME SWITCHER (Top Right in Dashboard) */}
          <button
            onClick={toggleTheme}
            style={{
              background: colors.cardBg,
              border: `1px solid ${colors.cardBorder}`,
              color: colors.textPrimary,
              padding: "0.42rem 0.8rem",
              borderRadius: "6px",
              fontSize: "0.78rem",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "5px",
            }}
            title="Toggle Light / Dark Mode for your account"
          >
            <span>{isDark ? "☀️ Light Mode" : "🌙 Dark Mode"}</span>
          </button>

          {/* Simulate Issue Button */}
          <button
            onClick={handleSimulateAlert}
            disabled={isSimulating}
            style={{
              background: isDark ? "#18181b" : "#f8fafc",
              border: `1px solid ${colors.cardBorder}`,
              color: colors.textPrimary,
              padding: "0.42rem 0.8rem",
              borderRadius: "6px",
              fontSize: "0.8rem",
              fontWeight: 500,
              cursor: isSimulating ? "not-allowed" : "pointer",
            }}
          >
            {isSimulating ? "Simulating..." : "⚡ Simulate Alert"}
          </button>

          {/* Super Admin User Directory */}
          {currentUser.role === "super_admin" && (
            <button
              onClick={() => setShowUsersModal(true)}
              style={{
                background: isDark ? "#1e1b4b" : "#e0e7ff",
                border: isDark ? "1px solid #3730a3" : "1px solid #c7d2fe",
                color: isDark ? "#a5b4fc" : "#4338ca",
                padding: "0.42rem 0.8rem",
                borderRadius: "6px",
                fontSize: "0.8rem",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              👥 Registered Users
            </button>
          )}

          {/* User Info & Sign Out */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", borderLeft: `1px solid ${colors.cardBorder}`, paddingLeft: "0.85rem" }}>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: "0.82rem", fontWeight: 600, color: colors.textPrimary }}>{currentUser.name}</div>
              <div style={{ fontSize: "0.7rem", color: currentUser.role === "super_admin" ? "#0284c7" : colors.textSecondary }}>
                {currentUser.role === "super_admin" ? "Platform Super Admin" : currentUser.tenant}
              </div>
            </div>
            <button
              onClick={() => {
                setIsAuthenticated(false);
                setTheme("light"); // reset view to standard light gateway
                showToast("Signed out successfully.");
              }}
              style={{
                background: isDark ? "#27272a" : "#fee2e2",
                border: "none",
                color: isDark ? "#f87171" : "#dc2626",
                padding: "0.4rem 0.75rem",
                borderRadius: "6px",
                fontSize: "0.78rem",
                fontWeight: 600,
                cursor: "pointer",
              }}
              title="Sign Out"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* 2. TOP METRIC CARDS */}
      <div style={{ maxWidth: "1280px", width: "100%", margin: "0 auto", padding: "1.5rem 1.75rem 0 1.75rem" }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "1rem",
        }}>
          <div style={{ background: colors.cardBg, border: `1px solid ${colors.cardBorder}`, borderRadius: "8px", padding: "1.1rem 1.25rem", boxShadow: colors.shadow }}>
            <div style={{ fontSize: "0.75rem", color: colors.textSecondary, fontWeight: 500 }}>System Health</div>
            <div style={{ fontSize: "1.35rem", fontWeight: 700, color: activeCount > 0 ? "#d97706" : "#16a34a", marginTop: "0.3rem" }}>
              {activeCount > 0 ? "Degraded (1 Issue)" : "100% Operational"}
            </div>
            <div style={{ fontSize: "0.72rem", color: colors.textMuted, marginTop: "0.2rem" }}>Target: &lt; 200ms latency</div>
          </div>

          <div style={{ background: colors.cardBg, border: `1px solid ${colors.cardBorder}`, borderRadius: "8px", padding: "1.1rem 1.25rem", boxShadow: colors.shadow }}>
            <div style={{ fontSize: "0.75rem", color: colors.textSecondary, fontWeight: 500 }}>Active Issues</div>
            <div style={{ fontSize: "1.35rem", fontWeight: 700, color: activeCount > 0 ? "#dc2626" : "#16a34a", marginTop: "0.3rem" }}>
              {activeCount}
            </div>
            <div style={{ fontSize: "0.72rem", color: colors.textMuted, marginTop: "0.2rem" }}>{resolvedCount} resolved automatically</div>
          </div>

          <div style={{ background: colors.cardBg, border: `1px solid ${colors.cardBorder}`, borderRadius: "8px", padding: "1.1rem 1.25rem", boxShadow: colors.shadow }}>
            <div style={{ fontSize: "0.75rem", color: colors.textSecondary, fontWeight: 500 }}>AI Diagnosis Engine</div>
            <div style={{ fontSize: "1.35rem", fontWeight: 700, color: "#0284c7", marginTop: "0.3rem" }}>
              DeepSeek-R1 Active
            </div>
            <div style={{ fontSize: "0.72rem", color: colors.textMuted, marginTop: "0.2rem" }}>Runbook matching &amp; auto-PR generation</div>
          </div>

          <div style={{ background: colors.cardBg, border: `1px solid ${colors.cardBorder}`, borderRadius: "8px", padding: "1.1rem 1.25rem", boxShadow: colors.shadow }}>
            <div style={{ fontSize: "0.75rem", color: colors.textSecondary, fontWeight: 500 }}>Human SRE Approval Gate</div>
            <div style={{ fontSize: "1.35rem", fontWeight: 700, color: "#7c3aed", marginTop: "0.3rem" }}>
              Rule 15 Enforced
            </div>
            <div style={{ fontSize: "0.72rem", color: colors.textMuted, marginTop: "0.2rem" }}>No blind auto-executions</div>
          </div>
        </div>
      </div>

      {/* 3. MAIN CONTENT: CLEAN INCIDENTS VIEW */}
      {activeTab === "incidents" && (
        <div style={{ maxWidth: "1280px", width: "100%", margin: "0 auto", padding: "1.5rem 1.75rem", flex: 1 }}>
          <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: "1.5rem", alignItems: "start" }}>
            
            {/* LEFT COLUMN: Clean List of Incidents */}
            <div style={{ background: colors.cardBg, border: `1px solid ${colors.cardBorder}`, borderRadius: "8px", overflow: "hidden", boxShadow: colors.shadow }}>
              {/* Search Header */}
              <div style={{ padding: "0.85rem 1rem", borderBottom: `1px solid ${colors.cardBorder}` }}>
                <input
                  type="text"
                  placeholder="Search issues by name or service..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    width: "100%",
                    background: colors.inputBg,
                    border: `1px solid ${colors.inputBorder}`,
                    borderRadius: "6px",
                    padding: "0.5rem 0.75rem",
                    color: colors.textPrimary,
                    fontSize: "0.8rem",
                    outline: "none",
                  }}
                />
              </div>

              {/* Incident Items */}
              <div style={{ maxHeight: "600px", overflowY: "auto" }}>
                {filteredIncidents.length === 0 ? (
                  <div style={{ padding: "2rem 1rem", textAlign: "center", color: colors.textMuted, fontSize: "0.82rem" }}>
                    No matching incidents found.
                  </div>
                ) : (
                  filteredIncidents.map((inc) => {
                    const isSelected = inc.id === selectedIncidentId;
                    const isResolved = inc.status === "resolved";
                    const isExecuting = inc.status === "executing";

                    return (
                      <div
                        key={inc.id}
                        onClick={() => setSelectedIncidentId(inc.id)}
                        style={{
                          padding: "1rem",
                          borderBottom: `1px solid ${colors.cardBorder}`,
                          background: isSelected ? colors.activeItemBg : "transparent",
                          cursor: "pointer",
                          borderLeft: isSelected ? "3px solid #2563eb" : "3px solid transparent",
                          transition: "background 0.15s ease",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                          <span style={{ fontSize: "0.72rem", color: colors.textSecondary, fontWeight: 600 }}>{inc.id}</span>
                          <span style={{
                            fontSize: "0.68rem",
                            padding: "0.15rem 0.5rem",
                            borderRadius: "4px",
                            fontWeight: 700,
                            textTransform: "uppercase",
                            background: isResolved ? (isDark ? "rgba(16, 185, 129, 0.15)" : "#dcfce7") : inc.severity === "critical" ? (isDark ? "rgba(239, 68, 68, 0.15)" : "#fee2e2") : (isDark ? "rgba(245, 158, 11, 0.15)" : "#fef3c7"),
                            color: isResolved ? "#16a34a" : inc.severity === "critical" ? "#dc2626" : "#d97706",
                          }}>
                            {isResolved ? "RESOLVED" : isExecuting ? "FIXING..." : inc.severity}
                          </span>
                        </div>

                        <div style={{ fontSize: "0.85rem", fontWeight: 600, color: colors.textPrimary, marginBottom: "0.25rem", lineHeight: 1.3 }}>
                          {inc.title}
                        </div>

                        <div style={{ fontSize: "0.72rem", color: colors.textMuted }}>
                          Service: <span style={{ color: colors.textSecondary }}>{inc.service_id}</span>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* RIGHT COLUMN: Clean Detail & Action Panel */}
            {selectedIncident ? (
              <div style={{ background: colors.cardBg, border: `1px solid ${colors.cardBorder}`, borderRadius: "8px", padding: "1.75rem", boxShadow: colors.shadow }}>
                
                {/* Header Section */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", borderBottom: `1px solid ${colors.cardBorder}`, paddingBottom: "1.25rem" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.4rem" }}>
                      <span style={{ fontSize: "0.8rem", color: colors.textSecondary, fontWeight: 700 }}>{selectedIncident.id}</span>
                      <span style={{
                        fontSize: "0.7rem",
                        padding: "0.15rem 0.5rem",
                        borderRadius: "4px",
                        fontWeight: 700,
                        textTransform: "uppercase",
                        background: selectedIncident.status === "resolved" ? (isDark ? "rgba(16, 185, 129, 0.15)" : "#dcfce7") : (isDark ? "rgba(239, 68, 68, 0.15)" : "#fee2e2"),
                        color: selectedIncident.status === "resolved" ? "#16a34a" : "#dc2626",
                      }}>
                        {selectedIncident.status.toUpperCase()}
                      </span>
                    </div>
                    <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: colors.textPrimary, margin: 0 }}>
                      {selectedIncident.title}
                    </h2>
                    <p style={{ fontSize: "0.82rem", color: colors.textSecondary, margin: "0.4rem 0 0 0" }}>
                      Target Component: <code style={{ color: colors.textPrimary, background: colors.subtleBoxBg, padding: "0.15rem 0.4rem", borderRadius: "4px", border: `1px solid ${colors.subtleBoxBorder}` }}>{selectedIncident.service_id}</code>
                    </p>
                  </div>

                  {/* Status Indicator */}
                  {selectedIncident.status === "resolved" && (
                    <div style={{
                      background: isDark ? "rgba(16, 185, 129, 0.1)" : "#dcfce7",
                      border: isDark ? "1px solid rgba(16, 185, 129, 0.3)" : "1px solid #86efac",
                      color: "#16a34a",
                      padding: "0.5rem 0.9rem",
                      borderRadius: "6px",
                      fontSize: "0.8rem",
                      fontWeight: 600,
                    }}>
                      ✓ Issue Fixed &amp; Verified
                    </div>
                  )}
                </div>

                {/* 1. What Happened? */}
                <div style={{ marginTop: "1.25rem" }}>
                  <h4 style={{ fontSize: "0.85rem", color: colors.textPrimary, margin: "0 0 0.4rem 0", textTransform: "uppercase", letterSpacing: "0.03em" }}>
                    1. Problem Description
                  </h4>
                  <p style={{ fontSize: "0.85rem", color: colors.textSecondary, lineHeight: 1.5, margin: 0, background: colors.subtleBoxBg, padding: "0.85rem 1rem", borderRadius: "6px", border: `1px solid ${colors.subtleBoxBorder}` }}>
                    {(selectedIncident as any).description || "Active threshold alert received from telemetry ingestion. Service degraded under saturated connection limits."}
                  </p>
                </div>

                {/* 2. AI Root Cause Diagnosis */}
                <div style={{ marginTop: "1.25rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                    <h4 style={{ fontSize: "0.85rem", color: colors.textPrimary, margin: 0, textTransform: "uppercase", letterSpacing: "0.03em" }}>
                      2. AI Diagnosis (DeepSeek-R1 Runbook)
                    </h4>
                    <span style={{ fontSize: "0.75rem", color: "#0284c7", fontWeight: 600 }}>
                      Confidence: {currentDiagnosis?.confidence ? `${(currentDiagnosis.confidence * 100).toFixed(0)}%` : "96%"}
                    </span>
                  </div>

                  <div style={{ background: colors.subtleBoxBg, border: `1px solid ${colors.subtleBoxBorder}`, borderRadius: "6px", padding: "0.85rem 1rem" }}>
                    <div style={{ fontSize: "0.85rem", color: colors.textPrimary, fontWeight: 600, marginBottom: "0.3rem" }}>
                      {currentDiagnosis?.probable_root_cause || "PostgreSQL connection pool exhausted due to unclosed worker connection leaks."}
                    </div>
                    <div style={{ fontSize: "0.78rem", color: colors.textSecondary, lineHeight: 1.4 }}>
                      Matched Runbook: <code>{(currentDiagnosis as any)?.matched_runbooks?.[0] || "RB-001 (Database Pool Saturation Recovery)"}</code>
                    </div>
                  </div>
                </div>

                {/* 3. Recommended Remediation & Approval Action */}
                <div style={{ marginTop: "1.5rem", borderTop: `1px solid ${colors.cardBorder}`, paddingTop: "1.25rem" }}>
                  <h4 style={{ fontSize: "0.85rem", color: colors.textPrimary, margin: "0 0 0.6rem 0", textTransform: "uppercase", letterSpacing: "0.03em" }}>
                    3. Recommended Solution &amp; Action
                  </h4>

                  <div style={{ background: colors.subtleBoxBg, border: `1px solid ${colors.subtleBoxBorder}`, borderRadius: "6px", padding: "1rem", marginBottom: "1rem" }}>
                    <div style={{ fontSize: "0.85rem", color: colors.textPrimary, fontWeight: 600, marginBottom: "0.4rem" }}>
                      Action Plan: {currentPlan?.rationale || "Auto-generate GitHub Pull Request to increase pool limit and restart idle worker sessions."}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: colors.textSecondary }}>
                      Safe Execution: Will create branch <code>fix/db-pool-saturation-inc-8921</code> and PR on GitHub without breaking production.
                    </div>
                  </div>

                  {/* Action Buttons */}
                  {selectedIncident.status !== "resolved" ? (
                    <div style={{ display: "flex", gap: "0.75rem" }}>
                      <button
                        onClick={() => handleApprove(selectedIncident.id)}
                        disabled={selectedIncident.status === "executing"}
                        style={{
                          background: "#16a34a",
                          color: "#ffffff",
                          border: "none",
                          padding: "0.65rem 1.4rem",
                          borderRadius: "6px",
                          fontSize: "0.85rem",
                          fontWeight: 700,
                          cursor: selectedIncident.status === "executing" ? "not-allowed" : "pointer",
                          display: "flex",
                          alignItems: "center",
                          gap: "6px"
                        }}
                      >
                        {selectedIncident.status === "executing" ? "Executing..." : "✓ Approve & Execute Fix (Generate GitHub PR)"}
                      </button>

                      <button
                        onClick={() => handleReject(selectedIncident.id)}
                        style={{
                          background: isDark ? "#27272a" : "#f1f5f9",
                          color: colors.textSecondary,
                          border: `1px solid ${colors.cardBorder}`,
                          padding: "0.65rem 1rem",
                          borderRadius: "6px",
                          fontSize: "0.85rem",
                          fontWeight: 600,
                          cursor: "pointer",
                        }}
                      >
                        Reject Fix
                      </button>
                    </div>
                  ) : (
                    <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                      <a
                        href="https://github.com/borahtranay-dev/Domain-Agnostic-AIOps-Platform/pull/421"
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          background: "#2563eb",
                          color: "#ffffff",
                          textDecoration: "none",
                          padding: "0.55rem 1rem",
                          borderRadius: "6px",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "6px"
                        }}
                      >
                        <span>View GitHub Pull Request #421 &rarr;</span>
                      </a>
                      <span style={{ fontSize: "0.75rem", color: colors.textMuted }}>
                        PR created &amp; verified by Telemetry Verification Engine
                      </span>
                    </div>
                  )}
                </div>

                {/* 4. Evidence Logs */}
                {currentEvidence.length > 0 && (
                  <div style={{ marginTop: "1.5rem", borderTop: `1px solid ${colors.cardBorder}`, paddingTop: "1.25rem" }}>
                    <div style={{ fontSize: "0.8rem", color: colors.textSecondary, fontWeight: 600, marginBottom: "0.5rem" }}>
                      Telemetry Logs ({currentEvidence.length} records)
                    </div>
                    <div style={{ background: colors.codeBg, border: `1px solid ${colors.subtleBoxBorder}`, borderRadius: "6px", padding: "0.75rem", maxHeight: "150px", overflowY: "auto" }}>
                      {currentEvidence.map((ev) => (
                        <div key={ev.id} style={{ fontSize: "0.72rem", color: colors.textPrimary, fontFamily: "monospace", marginBottom: "0.3rem" }}>
                          <span style={{ color: "#0284c7" }}>[{ev.source}]</span> {ev.content}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ background: colors.cardBg, border: `1px solid ${colors.cardBorder}`, borderRadius: "8px", padding: "3rem", textAlign: "center", color: colors.textMuted }}>
                Select an incident from the list to view details and execute actions.
              </div>
            )}
          </div>
        </div>
      )}

      {/* 4. MONITORED SERVICES TAB */}
      {activeTab === "services" && (
        <div style={{ maxWidth: "1280px", width: "100%", margin: "0 auto", padding: "1.5rem 1.75rem", flex: 1 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1rem" }}>
            {servicesList.map((svc, idx) => (
              <div key={idx} style={{ background: colors.cardBg, border: `1px solid ${colors.cardBorder}`, borderRadius: "8px", padding: "1.25rem", boxShadow: colors.shadow }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                  <strong style={{ fontSize: "0.95rem", color: colors.textPrimary }}>{svc.name}</strong>
                  <span style={{
                    fontSize: "0.68rem",
                    padding: "0.15rem 0.5rem",
                    borderRadius: "4px",
                    fontWeight: 700,
                    background: svc.status === "Healthy" ? (isDark ? "rgba(16, 185, 129, 0.15)" : "#dcfce7") : svc.status === "Active" ? (isDark ? "rgba(37, 99, 235, 0.15)" : "#dbeafe") : (isDark ? "rgba(245, 158, 11, 0.15)" : "#fef3c7"),
                    color: svc.status === "Healthy" ? "#16a34a" : svc.status === "Active" ? "#2563eb" : "#d97706",
                  }}>
                    {svc.status}
                  </span>
                </div>
                <div style={{ fontSize: "0.78rem", color: colors.textSecondary, marginBottom: "0.75rem" }}>{svc.desc}</div>
                <div style={{ display: "flex", gap: "1rem", fontSize: "0.72rem", color: colors.textMuted, borderTop: `1px solid ${colors.cardBorder}`, paddingTop: "0.6rem" }}>
                  <span>Latency: <strong style={{ color: colors.textPrimary }}>{svc.latency}</strong></span>
                  <span>Uptime: <strong style={{ color: colors.textPrimary }}>{svc.uptime}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SUPER ADMIN MODAL: Registered Users Directory */}
      {showUsersModal && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          background: "rgba(0, 0, 0, 0.6)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 9999,
        }}>
          <div style={{
            background: colors.cardBg,
            border: `1px solid ${colors.cardBorder}`,
            borderRadius: "8px",
            width: "90%",
            maxWidth: "560px",
            padding: "1.5rem",
            color: colors.textPrimary,
            boxShadow: isDark ? "0 20px 40px rgba(0,0,0,0.8)" : "0 20px 40px rgba(0,0,0,0.15)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: `1px solid ${colors.cardBorder}`, paddingBottom: "0.75rem" }}>
              <div>
                <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 700 }}>
                  👥 Platform Registered Users &amp; Projects
                </h3>
                <p style={{ margin: "0.2rem 0 0 0", fontSize: "0.75rem", color: colors.textSecondary }}>
                  Students &amp; developers actively monitoring websites on your platform
                </p>
              </div>
              <button
                onClick={() => setShowUsersModal(false)}
                style={{ background: isDark ? "#27272a" : "#e2e8f0", border: "none", color: colors.textPrimary, borderRadius: "4px", padding: "0.3rem 0.6rem", cursor: "pointer", fontSize: "0.8rem" }}
              >
                ✕ Close
              </button>
            </div>

            <div style={{ maxHeight: "300px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <div style={{ background: colors.subtleBoxBg, border: `1px solid ${colors.subtleBoxBorder}`, borderRadius: "6px", padding: "0.75rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <strong style={{ fontSize: "0.85rem", color: "#0284c7" }}>DevOps SRE (Acme Corp)</strong>
                  <span style={{ fontSize: "0.68rem", color: colors.textMuted }}>Default Tenant</span>
                </div>
                <div style={{ fontSize: "0.75rem", color: colors.textSecondary, marginTop: "0.2rem" }}>Contact: sre@acme.com</div>
              </div>

              {getRegisteredUsers().length === 0 ? (
                <div style={{ padding: "1.5rem", textAlign: "center", color: colors.textMuted, fontSize: "0.78rem" }}>
                  No external users registered yet.
                </div>
              ) : (
                getRegisteredUsers().map((u: any, idx: number) => (
                  <div key={idx} style={{ background: colors.subtleBoxBg, border: `1px solid ${colors.subtleBoxBorder}`, borderRadius: "6px", padding: "0.75rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <strong style={{ fontSize: "0.85rem", color: "#16a34a" }}>{u.name}</strong>
                      <span style={{ fontSize: "0.68rem", color: "#16a34a" }}>Active</span>
                    </div>
                    <div style={{ fontSize: "0.75rem", color: colors.textSecondary, marginTop: "0.2rem" }}>
                      Contact: <code>{u.mobile || u.email}</code>
                    </div>
                    <div style={{ fontSize: "0.72rem", color: colors.textMuted, marginTop: "0.2rem" }}>
                      Monitored Project: <strong style={{ color: colors.textPrimary }}>{u.projectWebsite || u.tenant}</strong>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div style={{ marginTop: "1rem", paddingTop: "0.75rem", borderTop: `1px solid ${colors.cardBorder}`, textAlign: "right" }}>
              <button
                onClick={() => setShowUsersModal(false)}
                style={{ background: "#2563eb", color: "#ffffff", border: "none", borderRadius: "4px", padding: "0.45rem 0.9rem", fontSize: "0.8rem", cursor: "pointer", fontWeight: 600 }}
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
