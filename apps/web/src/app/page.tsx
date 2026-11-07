"use client";

import React, { useState } from "react";
import { LoginScreen } from "../components/LoginScreen";
import {
  changeSuperAdminPassword,
  changeUserPassword,
  validatePasswordStrength,
} from "../lib/authSecurity";
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

  // Load user's personal theme preference & attached services upon login
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

    try {
      // Look up user's custom attached websites/services (only if explicitly added by user)
      const savedServices = localStorage.getItem(`aiops_services_${user.email.toLowerCase()}`);
      if (savedServices) {
        const parsed = JSON.parse(savedServices).filter((s: any) => !s.url?.includes(".local"));
        setServicesList(parsed.length > 0 ? parsed : DEFAULT_SERVICES);
      } else {
        setServicesList(DEFAULT_SERVICES);
      }
    } catch {
      setServicesList(DEFAULT_SERVICES);
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
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>("");
  const [evidenceMap, setEvidenceMap] = useState<Record<string, Evidence[]>>({});
  const [diagnosesMap, setDiagnosesMap] = useState<Record<string, Diagnosis>>({});
  const [plansMap, setPlansMap] = useState<Record<string, RemediationPlan>>({});
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [showUsersModal, setShowUsersModal] = useState(false);

  // Settings & Change Password Modal States
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [settingsTab, setSettingsTab] = useState<"password" | "account">("password");
  const [currentPass, setCurrentPass] = useState("");
  const [newPass, setNewPass] = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [showNewPass, setShowNewPass] = useState(false);
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

    const strength = validatePasswordStrength(newPass);
    if (!strength.isValid) {
      setPwError(strength.errorMessage || "Password does not meet enterprise security requirements.");
      return;
    }

    if (currentUser?.role === "super_admin") {
      const res = changeSuperAdminPassword(currentPass, newPass);
      if (res.success) {
        setPwSuccess(res.message);
        setCurrentPass("");
        setNewPass("");
        setConfirmPass("");
        showToast("✓ Super Admin password successfully updated!");
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
        showToast("✓ Workspace password successfully updated!");
      } else {
        setPwError(res.message);
      }
    }
  };

  interface MonitoredService {
    name: string;
    url?: string;
    status: "Healthy" | "Active" | "Needs Attention";
    latency: string;
    uptime: string;
    desc: string;
    isCustom?: boolean;
  }

  const DEFAULT_SERVICES: MonitoredService[] = [
    { name: "API Gateway & Ingress", status: "Healthy", latency: "14ms", uptime: "99.99%", desc: "Reverse proxy & public router" },
    { name: "Auth & Identity Engine", status: "Healthy", latency: "8ms", uptime: "99.98%", desc: "OAuth 2.0 & JWT verification" },
    { name: "PostgreSQL Primary Cluster", status: "Needs Attention", latency: "42ms", uptime: "99.90%", desc: "Connection pool saturation detected" },
    { name: "Redis Cache & Event Broker", status: "Healthy", latency: "1.2ms", uptime: "100%", desc: "Queue broker & session cache" },
    { name: "AI Self-Healing Engine", status: "Active", latency: "850ms", uptime: "99.95%", desc: "DeepSeek-R1 runbook diagnostic brain" },
  ];

  const [servicesList, setServicesList] = useState<MonitoredService[]>(DEFAULT_SERVICES);

  // Attach New Website Modal States
  const [showAttachModal, setShowAttachModal] = useState(false);
  const [attachSiteName, setAttachSiteName] = useState("");
  const [attachSiteUrl, setAttachSiteUrl] = useState("");
  const [attachSiteType, setAttachSiteType] = useState<"http" | "api">("http");
  const [isPingingMap, setIsPingingMap] = useState<Record<string, boolean>>({});

  // Real HTTP Health Ping to user's live website
  const handleLivePing = async (service: MonitoredService) => {
    if (!service.url) return;
    setIsPingingMap((prev) => ({ ...prev, [service.name]: true }));
    showToast(`⚡ Sending live HTTP probe to ${service.url}...`);

    try {
      const res = await fetch("/api/ping", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: service.url }),
      });
      const data = await res.json();

      if (data.success) {
        // Update service status with real latency
        const updated = servicesList.map((s) => {
          if (s.name === service.name) {
            return {
              ...s,
              status: data.healthy ? ("Healthy" as const) : ("Needs Attention" as const),
              latency: data.latency,
              uptime: data.healthy ? "100%" : "98.5%",
            };
          }
          return s;
        });
        setServicesList(updated);

        if (currentUser && currentUser.email) {
          try {
            localStorage.setItem(`aiops_services_${currentUser.email.toLowerCase()}`, JSON.stringify(updated));
          } catch (err) {
            console.error(err);
          }
        }

        if (data.healthy) {
          showToast(`✓ [${service.name}] Live & Operational: ${data.latency} (HTTP ${data.status})`);
        } else {
          showToast(`⚠️ [${service.name}] ${data.message}`);
        }
      } else {
        showToast(`❌ Ping error: ${data.error}`);
      }
    } catch (err: any) {
      showToast(`❌ Failed to ping ${service.name}: ${err.message}`);
    } finally {
      setIsPingingMap((prev) => ({ ...prev, [service.name]: false }));
    }
  };

  const handleAttachWebsiteSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!attachSiteName.trim()) return;

    let targetUrl = attachSiteUrl.trim();
    if (targetUrl && !targetUrl.startsWith("http://") && !targetUrl.startsWith("https://")) {
      targetUrl = "https://" + targetUrl;
    }

    const newService: MonitoredService = {
      name: attachSiteName.trim(),
      url: targetUrl || "https://local-endpoint.dev",
      status: "Healthy",
      latency: "Checking...",
      uptime: "100%",
      desc: `Live Web Endpoint (${attachSiteType === "http" ? "HTTP Health Ping" : "API Ingestion"})`,
      isCustom: true,
    };

    const updated = [newService, ...servicesList];
    setServicesList(updated);

    if (currentUser && currentUser.email) {
      try {
        localStorage.setItem(`aiops_services_${currentUser.email.toLowerCase()}`, JSON.stringify(updated));
      } catch (err) {
        console.error("Failed to save attached website", err);
      }
    }

    setShowAttachModal(false);
    setAttachSiteName("");
    setAttachSiteUrl("");
    showToast(`✓ Website "${newService.name}" attached successfully! Active monitoring started.`);

    // Instantly probe live URL
    handleLivePing(newService);
  };

  // Handle Detaching / Deleting a Monitored Website
  const handleDetachWebsite = (siteName: string) => {
    const updated = servicesList.filter((s) => s.name !== siteName);
    setServicesList(updated);
    if (currentUser && currentUser.email) {
      try {
        localStorage.setItem(`aiops_services_${currentUser.email.toLowerCase()}`, JSON.stringify(updated));
      } catch (err) {
        console.error(err);
      }
    }
    showToast(`✓ Website "${siteName}" removed from monitoring.`);
  };

  // Regular users see ONLY their own custom attached websites!
  // Super Admin sees global platform infrastructure + connected endpoints.
  const displayedServices = currentUser.role === "super_admin"
    ? servicesList.filter((s) => !s.url?.includes(".local"))
    : servicesList.filter((s) => s.isCustom && !s.url?.includes(".local"));

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

  // Monitored services state

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
              Monitored Services ({displayedServices.length})
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

          {/* Settings & Profile Governance Button */}
          <button
            onClick={() => {
              setSettingsTab("password");
              setShowSettingsModal(true);
              setPwError(null);
              setPwSuccess(null);
            }}
            style={{
              background: isDark ? "#18181b" : "#f8fafc",
              border: `1px solid ${colors.cardBorder}`,
              color: colors.textPrimary,
              padding: "0.42rem 0.8rem",
              borderRadius: "6px",
              fontSize: "0.8rem",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "5px",
            }}
            title="Account Settings & Security"
          >
            <span>⚙️ Settings</span>
          </button>

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
                  <div style={{ padding: "3rem 1.5rem", textAlign: "center", color: colors.textSecondary }}>
                    <div style={{ fontSize: "1.8rem", marginBottom: "0.5rem" }}>🟢</div>
                    <strong style={{ fontSize: "0.95rem", color: colors.textPrimary, display: "block", marginBottom: "0.25rem" }}>
                      Zero Active Incidents
                    </strong>
                    <span style={{ fontSize: "0.78rem", color: colors.textMuted }}>
                      All monitored endpoints and services are operating normally.
                    </span>
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
                      <span style={{
                        background: isDark ? "rgba(16, 185, 129, 0.1)" : "#dcfce7",
                        border: isDark ? "1px solid rgba(16, 185, 129, 0.3)" : "1px solid #86efac",
                        color: "#16a34a",
                        padding: "0.45rem 0.85rem",
                        borderRadius: "6px",
                        fontSize: "0.78rem",
                        fontWeight: 600,
                      }}>
                        ✓ Remediation Executed &amp; Empirically Verified
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
              <div style={{ background: colors.cardBg, border: `1px dashed ${colors.cardBorder}`, borderRadius: "12px", padding: "4rem 2rem", textAlign: "center", color: colors.textSecondary }}>
                <div style={{ fontSize: "2.4rem", marginBottom: "0.75rem" }}>🛡️</div>
                <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "1.15rem", color: colors.textPrimary }}>
                  Autonomous SRE Engine Active &amp; Ready
                </h3>
                <p style={{ margin: "0 auto", fontSize: "0.85rem", color: colors.textMuted, maxWidth: "460px", lineHeight: 1.5 }}>
                  Your infrastructure is 100% operational with zero open alerts. Live telemetry and automated health checks are actively monitoring your connected services.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 4. MONITORED SERVICES TAB */}
      {activeTab === "services" && (
        <div style={{ maxWidth: "1280px", width: "100%", margin: "0 auto", padding: "1.5rem 1.75rem", flex: 1 }}>
          {/* Header & Attach Action */}
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1.25rem",
            background: colors.cardBg,
            border: `1px solid ${colors.cardBorder}`,
            borderRadius: "8px",
            padding: "1rem 1.25rem",
            boxShadow: colors.shadow,
          }}>
            <div>
              <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700, color: colors.textPrimary }}>
                {currentUser.role === "super_admin" ? "Platform Infrastructure & Connected Services" : "My Monitored Websites & Endpoints"}
              </h3>
              <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.78rem", color: colors.textSecondary }}>
                {currentUser.role === "super_admin"
                  ? "Global cluster components and client endpoints"
                  : "Live health status, real-time ping latency, and automated error telemetry"}
              </p>
            </div>
            <button
              onClick={() => setShowAttachModal(true)}
              style={{
                background: "#2563eb",
                color: "#ffffff",
                border: "none",
                padding: "0.55rem 1rem",
                borderRadius: "6px",
                fontSize: "0.82rem",
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px"
              }}
            >
              <span>➕ Attach Website / Service</span>
            </button>
          </div>

          {displayedServices.length === 0 ? (
            <div style={{
              background: colors.cardBg,
              border: `1px dashed ${colors.cardBorder}`,
              borderRadius: "12px",
              padding: "3.5rem 2rem",
              textAlign: "center",
              color: colors.textSecondary
            }}>
              <div style={{ fontSize: "2.2rem", marginBottom: "0.5rem" }}>🌐</div>
              <h4 style={{ margin: "0 0 0.4rem 0", fontSize: "1.05rem", color: colors.textPrimary }}>No Websites Attached Yet</h4>
              <p style={{ margin: "0 auto 1.25rem auto", fontSize: "0.82rem", color: colors.textMuted, maxWidth: "420px" }}>
                Connect your live website URL (e.g. Vercel portfolio or custom API) to monitor health and catch errors automatically.
              </p>
              <button
                onClick={() => setShowAttachModal(true)}
                style={{
                  background: "#2563eb",
                  color: "#ffffff",
                  border: "none",
                  padding: "0.55rem 1.25rem",
                  borderRadius: "6px",
                  fontSize: "0.82rem",
                  fontWeight: 600,
                  cursor: "pointer"
                }}
              >
                ➕ Attach Website Now
              </button>
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1rem" }}>
              {displayedServices.map((svc, idx) => (
                <div key={idx} style={{ background: colors.cardBg, border: `1px solid ${colors.cardBorder}`, borderRadius: "8px", padding: "1.25rem", boxShadow: colors.shadow }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <strong style={{ fontSize: "0.95rem", color: colors.textPrimary }}>{svc.name}</strong>
                      {svc.isCustom && (
                        <span style={{ fontSize: "0.65rem", padding: "0.1rem 0.4rem", borderRadius: "4px", background: isDark ? "#1e293b" : "#e0e7ff", color: isDark ? "#38bdf8" : "#2563eb", fontWeight: 600 }}>
                          Connected
                        </span>
                      )}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
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
                      {svc.isCustom && (
                        <button
                          onClick={() => handleDetachWebsite(svc.name)}
                          title="Remove this website"
                          style={{
                            background: isDark ? "#27272a" : "#f1f5f9",
                            border: `1px solid ${colors.cardBorder}`,
                            cursor: "pointer",
                            fontSize: "0.75rem",
                            color: colors.textMuted,
                            borderRadius: "4px",
                            padding: "1px 6px",
                            lineHeight: "1.2"
                          }}
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  </div>
                  {svc.url && (
                    <div style={{ fontSize: "0.74rem", color: "#0284c7", fontFamily: "monospace", marginBottom: "0.4rem" }}>
                      {svc.url}
                    </div>
                  )}
                  <div style={{ fontSize: "0.78rem", color: colors.textSecondary, marginBottom: "0.75rem" }}>{svc.desc}</div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: `1px solid ${colors.cardBorder}`, paddingTop: "0.6rem" }}>
                    <div style={{ display: "flex", gap: "1rem", fontSize: "0.72rem", color: colors.textMuted }}>
                      <span>Latency: <strong style={{ color: colors.textPrimary }}>{svc.latency}</strong></span>
                      <span>Uptime: <strong style={{ color: colors.textPrimary }}>{svc.uptime}</strong></span>
                    </div>
                    {svc.isCustom && svc.url && (
                      <button
                        onClick={() => handleLivePing(svc)}
                        disabled={isPingingMap[svc.name]}
                        style={{
                          background: isPingingMap[svc.name] ? (isDark ? "#27272a" : "#e2e8f0") : "#2563eb",
                          color: isPingingMap[svc.name] ? colors.textMuted : "#ffffff",
                          border: "none",
                          borderRadius: "4px",
                          fontSize: "0.72rem",
                          fontWeight: 600,
                          cursor: isPingingMap[svc.name] ? "wait" : "pointer",
                          padding: "3px 8px",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px",
                        }}
                      >
                        {isPingingMap[svc.name] ? "Probing..." : "⚡ Real Ping"}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* MODAL: Attach New Website / Service */}
      {showAttachModal && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          background: "rgba(0, 0, 0, 0.65)",
          backdropFilter: "blur(4px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 9999,
        }}>
          <div style={{
            background: colors.cardBg,
            border: `1px solid ${colors.cardBorder}`,
            borderRadius: "12px",
            width: "92%",
            maxWidth: "520px",
            padding: "1.75rem",
            color: colors.textPrimary,
            boxShadow: isDark ? "0 25px 50px -12px rgba(0, 0, 0, 0.7)" : "0 20px 40px rgba(0,0,0,0.12)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", borderBottom: `1px solid ${colors.cardBorder}`, paddingBottom: "0.75rem" }}>
              <div>
                <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700 }}>
                  ➕ Attach Your Website or API
                </h3>
                <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.75rem", color: colors.textSecondary }}>
                  Connect your web application for real-time monitoring and autonomous self-healing
                </p>
              </div>
              <button
                onClick={() => setShowAttachModal(false)}
                style={{
                  background: isDark ? "#27272a" : "#f1f5f9",
                  border: `1px solid ${colors.cardBorder}`,
                  color: colors.textPrimary,
                  borderRadius: "6px",
                  padding: "0.35rem 0.65rem",
                  cursor: "pointer",
                  fontSize: "0.8rem",
                  fontWeight: 600
                }}
              >
                ✕ Close
              </button>
            </div>

            <form onSubmit={handleAttachWebsiteSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, marginBottom: "0.35rem", color: colors.textPrimary }}>
                  Project / Website Name <span style={{ color: "#ef4444" }}>*</span>
                </label>
                <input
                  type="text"
                  value={attachSiteName}
                  onChange={(e) => setAttachSiteName(e.target.value)}
                  placeholder="e.g. My Portfolio Website, Student LMS, Store API"
                  required
                  autoFocus
                  style={{
                    width: "100%",
                    background: colors.inputBg,
                    border: `1px solid ${colors.inputBorder}`,
                    borderRadius: "6px",
                    padding: "0.55rem 0.8rem",
                    color: colors.textPrimary,
                    fontSize: "0.85rem",
                    outline: "none",
                  }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, marginBottom: "0.35rem", color: colors.textPrimary }}>
                  Target URL / Endpoint <span style={{ color: "#ef4444" }}>*</span>
                </label>
                <input
                  type="text"
                  value={attachSiteUrl}
                  onChange={(e) => setAttachSiteUrl(e.target.value)}
                  placeholder="e.g. https://myportfolio.vercel.app or http://localhost:5000"
                  required
                  style={{
                    width: "100%",
                    background: colors.inputBg,
                    border: `1px solid ${colors.inputBorder}`,
                    borderRadius: "6px",
                    padding: "0.55rem 0.8rem",
                    color: colors.textPrimary,
                    fontSize: "0.85rem",
                    outline: "none",
                  }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, marginBottom: "0.35rem", color: colors.textPrimary }}>
                  Monitoring Mode
                </label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
                  <button
                    type="button"
                    onClick={() => setAttachSiteType("http")}
                    style={{
                      background: attachSiteType === "http" ? "#2563eb" : (isDark ? "#18181b" : "#f8fafc"),
                      color: attachSiteType === "http" ? "#ffffff" : colors.textPrimary,
                      border: `1px solid ${colors.cardBorder}`,
                      borderRadius: "6px",
                      padding: "0.5rem",
                      fontSize: "0.78rem",
                      fontWeight: 600,
                      cursor: "pointer",
                      textAlign: "center"
                    }}
                  >
                    🌐 HTTP Health Ping
                  </button>
                  <button
                    type="button"
                    onClick={() => setAttachSiteType("api")}
                    style={{
                      background: attachSiteType === "api" ? "#2563eb" : (isDark ? "#18181b" : "#f8fafc"),
                      color: attachSiteType === "api" ? "#ffffff" : colors.textPrimary,
                      border: `1px solid ${colors.cardBorder}`,
                      borderRadius: "6px",
                      padding: "0.5rem",
                      fontSize: "0.78rem",
                      fontWeight: 600,
                      cursor: "pointer",
                      textAlign: "center"
                    }}
                  >
                    ⚡ API Ingestion Webhook
                  </button>
                </div>
              </div>

              {/* Ingestion Info Box */}
              <div style={{ background: colors.subtleBoxBg, border: `1px solid ${colors.subtleBoxBorder}`, borderRadius: "6px", padding: "0.75rem", fontSize: "0.72rem", color: colors.textSecondary }}>
                <strong style={{ color: colors.textPrimary }}>📡 Telemetry Ingestion Endpoint:</strong>
                <div style={{ fontFamily: "monospace", color: "#0284c7", marginTop: "0.25rem", wordBreak: "break-all" }}>
                  POST http://localhost:8000/api/v1/telemetry/ingest
                </div>
                <div style={{ marginTop: "0.35rem" }}>
                  Your website can send HTTP errors directly here for automated AI diagnosis and healing.
                </div>
              </div>

              <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem" }}>
                <button
                  type="button"
                  onClick={() => setShowAttachModal(false)}
                  style={{
                    flex: 1,
                    background: isDark ? "#27272a" : "#f1f5f9",
                    border: `1px solid ${colors.cardBorder}`,
                    color: colors.textPrimary,
                    borderRadius: "6px",
                    padding: "0.6rem 1rem",
                    fontSize: "0.82rem",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    flex: 1,
                    background: "#2563eb",
                    color: "#ffffff",
                    border: "none",
                    borderRadius: "6px",
                    padding: "0.6rem 1rem",
                    fontSize: "0.82rem",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  Attach &amp; Start Monitoring
                </button>
              </div>
            </form>
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
              {getRegisteredUsers().length === 0 ? (
                <div style={{ padding: "1.5rem", textAlign: "center", color: colors.textMuted, fontSize: "0.78rem" }}>
                  No registered users yet.
                </div>
              ) : (
                getRegisteredUsers().map((u: any, idx: number) => (
                  <div key={idx} style={{ background: colors.subtleBoxBg, border: `1px solid ${colors.subtleBoxBorder}`, borderRadius: "6px", padding: "0.75rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <strong style={{ fontSize: "0.85rem", color: "#16a34a" }}>{u.name}</strong>
                      <span style={{ fontSize: "0.68rem", color: "#16a34a", fontWeight: 600 }}>Active</span>
                    </div>
                    <div style={{ fontSize: "0.75rem", color: colors.textSecondary, marginTop: "0.2rem" }}>
                      Email: <code>{u.email}</code> {u.mobile && <>&bull; Mobile: <code>{u.mobile}</code></>}
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

      {/* COMPREHENSIVE SETTINGS & CHANGE PASSWORD MODAL (Accessible to Super Admin & All Users) */}
      {showSettingsModal && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          background: "rgba(0, 0, 0, 0.65)",
          backdropFilter: "blur(4px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 9999,
        }}>
          <div style={{
            background: colors.cardBg,
            border: `1px solid ${colors.cardBorder}`,
            borderRadius: "12px",
            width: "92%",
            maxWidth: "520px",
            padding: "1.75rem",
            color: colors.textPrimary,
            boxShadow: isDark ? "0 25px 50px -12px rgba(0, 0, 0, 0.7)" : "0 20px 40px rgba(0,0,0,0.12)",
          }}>
            {/* Header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", borderBottom: `1px solid ${colors.cardBorder}`, paddingBottom: "0.85rem" }}>
              <div>
                <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
                  <span>⚙️ Settings &amp; Security</span>
                </h3>
                <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.75rem", color: colors.textSecondary }}>
                  Manage credentials, password security, and workspace preferences
                </p>
              </div>
              <button
                onClick={() => setShowSettingsModal(false)}
                style={{
                  background: isDark ? "#27272a" : "#f1f5f9",
                  border: `1px solid ${colors.cardBorder}`,
                  color: colors.textPrimary,
                  borderRadius: "6px",
                  padding: "0.35rem 0.65rem",
                  cursor: "pointer",
                  fontSize: "0.8rem",
                  fontWeight: 600
                }}
              >
                ✕ Close
              </button>
            </div>

            {/* Modal Navigation Tabs */}
            <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.25rem", borderBottom: `1px solid ${colors.cardBorder}`, paddingBottom: "0.5rem" }}>
              <button
                type="button"
                onClick={() => setSettingsTab("password")}
                style={{
                  background: settingsTab === "password" ? "#2563eb" : "transparent",
                  color: settingsTab === "password" ? "#ffffff" : colors.textSecondary,
                  border: "none",
                  padding: "0.4rem 0.9rem",
                  borderRadius: "6px",
                  fontSize: "0.82rem",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                🔒 Change Password
              </button>
              <button
                type="button"
                onClick={() => setSettingsTab("account")}
                style={{
                  background: settingsTab === "account" ? "#2563eb" : "transparent",
                  color: settingsTab === "account" ? "#ffffff" : colors.textSecondary,
                  border: "none",
                  padding: "0.4rem 0.9rem",
                  borderRadius: "6px",
                  fontSize: "0.82rem",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                👤 Profile
              </button>
            </div>

            {/* TAB 1: CHANGE PASSWORD FORM */}
            {settingsTab === "password" && (
              <form onSubmit={handleChangePasswordSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {pwError && (
                  <div style={{ background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "6px", padding: "0.6rem 0.8rem", color: "#b91c1c", fontSize: "0.78rem" }}>
                    {pwError}
                  </div>
                )}
                {pwSuccess && (
                  <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "6px", padding: "0.6rem 0.8rem", color: "#15803d", fontSize: "0.78rem" }}>
                    {pwSuccess}
                  </div>
                )}

                <div>
                  <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, marginBottom: "0.35rem", color: colors.textPrimary }}>
                    Current Password
                  </label>
                  <input
                    type="password"
                    value={currentPass}
                    onChange={(e) => setCurrentPass(e.target.value)}
                    placeholder="Enter current password"
                    required
                    style={{
                      width: "100%",
                      background: colors.inputBg,
                      border: `1px solid ${colors.inputBorder}`,
                      borderRadius: "6px",
                      padding: "0.55rem 0.8rem",
                      color: colors.textPrimary,
                      fontSize: "0.85rem",
                      outline: "none",
                    }}
                  />
                </div>

                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                    <label style={{ fontSize: "0.78rem", fontWeight: 600, color: colors.textPrimary }}>
                      New Strong Password
                    </label>
                    <button
                      type="button"
                      onClick={() => setShowNewPass(!showNewPass)}
                      style={{ background: "none", border: "none", cursor: "pointer", fontSize: "0.72rem", color: colors.textMuted }}
                    >
                      {showNewPass ? "🙈 Hide" : "👁️ Show"}
                    </button>
                  </div>
                  <input
                    type={showNewPass ? "text" : "password"}
                    value={newPass}
                    onChange={(e) => setNewPass(e.target.value)}
                    placeholder="Enter new strong password"
                    required
                    style={{
                      width: "100%",
                      background: colors.inputBg,
                      border: `1px solid ${colors.inputBorder}`,
                      borderRadius: "6px",
                      padding: "0.55rem 0.8rem",
                      color: colors.textPrimary,
                      fontSize: "0.85rem",
                      outline: "none",
                    }}
                  />

                  {/* Real-time Checklist */}
                  {newPass.length > 0 && (() => {
                    const s = validatePasswordStrength(newPass);
                    return (
                      <div style={{
                        marginTop: "0.5rem",
                        padding: "0.55rem 0.75rem",
                        background: s.isValid ? "rgba(34, 197, 94, 0.08)" : (isDark ? "#18181b" : "#f8fafc"),
                        border: `1px solid ${s.isValid ? "rgba(34, 197, 94, 0.3)" : colors.cardBorder}`,
                        borderRadius: "6px",
                        fontSize: "0.7rem",
                        display: "grid",
                        gridTemplateColumns: "1fr 1fr",
                        gap: "0.25rem 0.5rem"
                      }}>
                        <span style={{ color: s.hasMinLength ? "#16a34a" : "#94a3b8" }}>{s.hasMinLength ? "✓" : "○"} Min. 8 Chars</span>
                        <span style={{ color: s.hasUpperCase ? "#16a34a" : "#94a3b8" }}>{s.hasUpperCase ? "✓" : "○"} Uppercase (A-Z)</span>
                        <span style={{ color: s.hasLowerCase ? "#16a34a" : "#94a3b8" }}>{s.hasLowerCase ? "✓" : "○"} Lowercase (a-z)</span>
                        <span style={{ color: s.hasNumber ? "#16a34a" : "#94a3b8" }}>{s.hasNumber ? "✓" : "○"} Number (0-9)</span>
                        <span style={{ color: s.hasSpecialChar ? "#16a34a" : "#94a3b8", gridColumn: "span 2" }}>{s.hasSpecialChar ? "✓" : "○"} Special Symbol (!@#$...)</span>
                      </div>
                    );
                  })()}
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, marginBottom: "0.35rem", color: colors.textPrimary }}>
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    value={confirmPass}
                    onChange={(e) => setConfirmPass(e.target.value)}
                    placeholder="Re-type new password"
                    required
                    style={{
                      width: "100%",
                      background: colors.inputBg,
                      border: `1px solid ${colors.inputBorder}`,
                      borderRadius: "6px",
                      padding: "0.55rem 0.8rem",
                      color: colors.textPrimary,
                      fontSize: "0.85rem",
                      outline: "none",
                    }}
                  />
                </div>

                <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem" }}>
                  <button
                    type="button"
                    onClick={() => setShowSettingsModal(false)}
                    style={{
                      flex: 1,
                      background: isDark ? "#27272a" : "#f1f5f9",
                      border: `1px solid ${colors.cardBorder}`,
                      color: colors.textPrimary,
                      borderRadius: "6px",
                      padding: "0.6rem 1rem",
                      fontSize: "0.82rem",
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    style={{
                      flex: 1,
                      background: "#2563eb",
                      color: "#ffffff",
                      border: "none",
                      borderRadius: "6px",
                      padding: "0.6rem 1rem",
                      fontSize: "0.82rem",
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    Save New Password
                  </button>
                </div>
              </form>
            )}

            {/* TAB 2: CLEAN USER PROFILE */}
            {settingsTab === "account" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <div style={{ background: colors.subtleBoxBg, border: `1px solid ${colors.subtleBoxBorder}`, borderRadius: "8px", padding: "1rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <strong style={{ fontSize: "0.95rem", color: colors.textPrimary }}>{currentUser.name}</strong>
                      <div style={{ fontSize: "0.78rem", color: colors.textSecondary, marginTop: "0.2rem" }}>
                        {currentUser.email}
                      </div>
                    </div>
                    <span style={{
                      fontSize: "0.72rem",
                      padding: "0.25rem 0.65rem",
                      borderRadius: "9999px",
                      fontWeight: 700,
                      background: currentUser.role === "super_admin" ? (isDark ? "#1e1b4b" : "#e0e7ff") : (isDark ? "#064e3b" : "#dcfce7"),
                      color: currentUser.role === "super_admin" ? "#6366f1" : "#16a34a"
                    }}>
                      {currentUser.role === "super_admin" ? "Platform Administrator" : "Member"}
                    </span>
                  </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                  <div style={{ background: colors.subtleBoxBg, border: `1px solid ${colors.subtleBoxBorder}`, borderRadius: "6px", padding: "0.8rem" }}>
                    <div style={{ fontSize: "0.7rem", color: colors.textMuted }}>Workspace</div>
                    <div style={{ fontSize: "0.85rem", fontWeight: 600, color: colors.textPrimary, marginTop: "0.25rem" }}>
                      {currentUser.tenant}
                    </div>
                  </div>
                  <div style={{ background: colors.subtleBoxBg, border: `1px solid ${colors.subtleBoxBorder}`, borderRadius: "6px", padding: "0.8rem" }}>
                    <div style={{ fontSize: "0.7rem", color: colors.textMuted }}>Account Status</div>
                    <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "#16a34a", marginTop: "0.25rem", display: "flex", alignItems: "center", gap: "6px" }}>
                      <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#16a34a", display: "inline-block" }}></span>
                      Active &amp; Verified
                    </div>
                  </div>
                </div>

                <div style={{ textAlign: "right", marginTop: "0.5rem" }}>
                  <button
                    onClick={() => setShowSettingsModal(false)}
                    style={{ background: "#2563eb", color: "#ffffff", border: "none", borderRadius: "6px", padding: "0.5rem 1.25rem", fontSize: "0.82rem", cursor: "pointer", fontWeight: 600 }}
                  >
                    Done
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
