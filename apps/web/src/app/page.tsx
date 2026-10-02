"use client";

import React, { useState, useEffect } from "react";

interface ServiceStatus {
  name: string;
  subsystem: string;
  owner: string;
  technology: string;
  status: "connected" | "checking" | "error";
  details: string;
}

export default function Home() {
  const [statuses, setStatuses] = useState<Record<string, ServiceStatus>>({
    api: {
      name: "Core API",
      subsystem: "apps/api",
      owner: "Taranay (Backend)",
      technology: "Python 3.12 + FastAPI",
      status: "checking",
      details: "Probing /health...",
    },
    database: {
      name: "PostgreSQL Database",
      subsystem: "infrastructure/db",
      owner: "Taranay & Saurav",
      technology: "PostgreSQL 16",
      status: "checking",
      details: "Awaiting API probe...",
    },
    redis: {
      name: "Queue & Cache (Redis)",
      subsystem: "infrastructure/redis",
      owner: "Taranay & Saurav",
      technology: "Redis 7",
      status: "checking",
      details: "Awaiting API probe...",
    },
    worker: {
      name: "Background Worker",
      subsystem: "apps/worker",
      owner: "Taranay (Backend)",
      technology: "Python 3.12 + RQ",
      status: "checking",
      details: "Listening on queue aiops-default",
    },
    aiWorker: {
      name: "AI Diagnosis Subsystem",
      subsystem: "apps/ai-worker",
      owner: "Rudra (AI / RAG)",
      technology: "FastAPI + LangChain",
      status: "checking",
      details: "Probing AI worker...",
    },
    web: {
      name: "Developer Cockpit",
      subsystem: "apps/web",
      owner: "Vivek (Frontend)",
      technology: "Next.js + TypeScript",
      status: "connected",
      details: "Web application shell active",
    },
  });

  const [lastCheck, setLastCheck] = useState<string>("Checking now...");

  const checkConnectivity = async () => {
    setLastCheck(new Date().toLocaleTimeString());

    // 1. Probe API /health and /ready
    try {
      const apiRes = await fetch("http://localhost:8000/api/v1/system-status", {
        cache: "no-store",
      });
      if (apiRes.ok) {
        const data = await apiRes.json();
        setStatuses((prev) => ({
          ...prev,
          api: {
            ...prev.api,
            status: "connected",
            details: `Online v${data.version || "0.1.0"}`,
          },
          database: {
            ...prev.database,
            status: data.dependencies?.postgresql?.connected ? "connected" : "error",
            details: data.dependencies?.postgresql?.details || "Connected",
          },
          redis: {
            ...prev.redis,
            status: data.dependencies?.redis?.connected ? "connected" : "error",
            details: data.dependencies?.redis?.details || "Connected",
          },
          worker: {
            ...prev.worker,
            status: data.dependencies?.redis?.connected ? "connected" : "error",
            details: data.dependencies?.redis?.connected
              ? "Queue connectivity active"
              : "Redis unavailable",
          },
        }));
      } else {
        throw new Error(`API returned HTTP ${apiRes.status}`);
      }
    } catch (err: any) {
      setStatuses((prev) => ({
        ...prev,
        api: { ...prev.api, status: "error", details: err.message || "Failed to reach API" },
        database: { ...prev.database, status: "error", details: "Unreachable (via API)" },
        redis: { ...prev.redis, status: "error", details: "Unreachable (via API)" },
        worker: { ...prev.worker, status: "error", details: "Worker dependency check failed" },
      }));
    }

    // 2. Probe AI-Worker /health
    try {
      const aiRes = await fetch("http://localhost:8001/health", {
        cache: "no-store",
      });
      if (aiRes.ok) {
        const aiData = await aiRes.json();
        setStatuses((prev) => ({
          ...prev,
          aiWorker: {
            ...prev.aiWorker,
            status: "connected",
            details: `Online (LangChain: ${aiData.langchain_available ? "Ready" : "Missing"})`,
          },
        }));
      } else {
        throw new Error(`AI Worker returned HTTP ${aiRes.status}`);
      }
    } catch (err: any) {
      setStatuses((prev) => ({
        ...prev,
        aiWorker: {
          ...prev.aiWorker,
          status: "error",
          details: err.message || "Failed to reach AI Worker",
        },
      }));
    }
  };

  useEffect(() => {
    checkConnectivity();
    const interval = setInterval(checkConnectivity, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div className="brand-section">
          <div className="brand-logo">
            <svg
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M13 10V3L4 14h7v7l9-11h-7z"
              ></path>
            </svg>
          </div>
          <div>
            <h1 className="brand-title">AIOps Developer Cockpit</h1>
            <p className="brand-subtitle">Domain-Agnostic Self-Healing Platform</p>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <button className="btn-refresh" onClick={checkConnectivity} id="btn-refresh-status">
            <svg
              style={{ width: "16px", height: "16px" }}
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              ></path>
            </svg>
            Refresh Status
          </button>
          <div className="phase-pill">
            <div className="pulse-dot"></div>
            <span>Phase P1: Technical Foundation</span>
          </div>
        </div>
      </header>

      {/* Hero Banner */}
      <section className="hero-banner">
        <h2 className="hero-title">Technical Foundation & Subsystem Health</h2>
        <p className="hero-description">
          This Developer Cockpit serves as the operational inspection surface for the AIOps platform.
          The core architecture is strictly domain-agnostic, reasoning over generic operational
          signals (Pipelines, Deployments, Incidents, Evidence, Remediation Plans, Approvals, and
          Verifications) while isolating e-commerce reference logic behind the adapter boundary.
        </p>
      </section>

      {/* Connectivity & Service Status Grid */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
        <h2 className="section-heading">Subsystem Connectivity & Health</h2>
        <span style={{ fontSize: "0.82rem", color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
          Last checked: {lastCheck}
        </span>
      </div>

      <div className="cards-grid">
        {Object.entries(statuses).map(([key, svc]) => (
          <div className="cockpit-card" key={key} id={`card-status-${key}`}>
            <div className="card-header">
              <div className="card-title-group">
                <h3>{svc.name}</h3>
                <div className="card-role">{svc.subsystem}</div>
              </div>
              <span
                className={`badge ${
                  svc.status === "connected"
                    ? "badge-connected"
                    : svc.status === "checking"
                    ? "badge-checking"
                    : "badge-error"
                }`}
              >
                {svc.status.toUpperCase()}
              </span>
            </div>

            <div className="card-detail-item">
              <span className="card-detail-label">Subsystem Lead</span>
              <span className="card-detail-val">{svc.owner}</span>
            </div>
            <div className="card-detail-item">
              <span className="card-detail-label">Tech Stack</span>
              <span className="card-detail-val">{svc.technology}</span>
            </div>
            <div className="card-detail-item">
              <span className="card-detail-label">Status Details</span>
              <span className="card-detail-val">{svc.details}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Architectural Flow Representation */}
      <div className="arch-banner">
        <div style={{ fontWeight: 600, color: "var(--text-main)", marginBottom: "0.5rem" }}>
          Authoritative Self-Healing Remediation Chain (P0-P1 Baseline)
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
          Operational execution chain enforcing bounded autonomy and evidence-grounded human governance:
        </p>
        <div className="arch-chain">
          <div className="arch-node">Event</div>
          <span className="arch-arrow">→</span>
          <div className="arch-node">Incident</div>
          <span className="arch-arrow">→</span>
          <div className="arch-node">Evidence</div>
          <span className="arch-arrow">→</span>
          <div className="arch-node">RAG Diagnosis</div>
          <span className="arch-arrow">→</span>
          <div className="arch-node">Remediation Plan</div>
          <span className="arch-arrow">→</span>
          <div className="arch-node" style={{ borderColor: "var(--accent-amber)", color: "var(--accent-amber)" }}>
            Human Approval
          </div>
          <span className="arch-arrow">→</span>
          <div className="arch-node">Adapter Execution</div>
          <span className="arch-arrow">→</span>
          <div className="arch-node" style={{ borderColor: "var(--accent-emerald)", color: "var(--accent-emerald)" }}>
            Verification
          </div>
        </div>
      </div>
    </div>
  );
}
