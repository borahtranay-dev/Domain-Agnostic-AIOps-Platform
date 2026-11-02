"use client";

import React from "react";
import { Incident, IncidentStatus } from "../types";

interface IncidentWorkspaceColumnProps {
  incident?: Incident;
  onAcknowledge?: () => void;
  onViewLogs?: () => void;
}

export function IncidentWorkspaceColumn({
  incident,
  onAcknowledge,
  onViewLogs,
}: IncidentWorkspaceColumnProps) {
  if (!incident) {
    return (
      <div className="workspace-empty-state">
        <span className="empty-icon-lg">🔍</span>
        <h3>Select an incident from the stream</h3>
        <p>Telemetry metrics, 5-step pipeline stepper, and latency charts will appear here.</p>
      </div>
    );
  }

  const isResolved = incident.status === "resolved";
  const isAwaitingApproval = incident.status === "awaiting_approval";
  const isExecuting = incident.status === "executing";
  const isDiagnosing = incident.status === "diagnosing";

  // Determine active step index (1-based)
  let activeStep = 3; // Default investigating
  if (incident.status === "open") activeStep = 1;
  else if (isDiagnosing) activeStep = 3;
  else if (isAwaitingApproval) activeStep = 4;
  else if (isExecuting) activeStep = 4;
  else if (isResolved) activeStep = 5;

  return (
    <div className="workspace-col-container">
      {/* Workspace Top Header */}
      <div className="workspace-header">
        <div className="workspace-title-group">
          <div className="workspace-tag-row">
            <span className={`badge-severity sev-${incident.severity}`}>
              {incident.severity.toUpperCase()}
            </span>
            <span className="workspace-service-tag">
              {incident.service_id || "auth-service"}
            </span>
          </div>
          <h1 className="workspace-main-title">
            <span className="title-sev-prefix">[{incident.severity.toUpperCase()}]</span>{" "}
            {incident.title}
          </h1>
        </div>

        {/* On-Call Incident Response Team */}
        <div className="team-avatar-stack" title="Active SRE Incident Response Team">
          <div className="avatar-chip chip-1" title="Primary On-Call SRE (Active Commander)">PC</div>
          <div className="avatar-chip chip-2" title="Secondary On-Call (Infrastructure)">SO</div>
          <div className="avatar-chip chip-3" title="AI Subsystem Escalator">AI</div>
          <span className="avatar-more" title="2 Subscribed Responders">+2</span>
        </div>
      </div>

      {/* Card 1: 5-Step Pipeline Stepper */}
      <div className="workspace-card pipeline-card">
        <div className="card-header-row">
          <div>
            <h2 className="card-title">5-Step Pipeline Stepper</h2>
            <p className="card-subtitle">
              AUTONOMOUS AIOPS ENGINE &middot; Status:{" "}
              <strong className="status-highlight">
                {incident.status.replace("_", " ")}
              </strong>
            </p>
          </div>
          <div className="card-actions-group">
            <button
              onClick={onAcknowledge}
              className="btn-workspace-action"
              title="Acknowledge this incident alert"
            >
              Acknowledge
            </button>
            <button
              onClick={onViewLogs}
              className="btn-workspace-action"
              title="Inspect raw log evidence"
            >
              View Logs
            </button>
          </div>
        </div>

        {/* Vertical 5-Step Sequence */}
        <div className="stepper-vertical-list">
          {/* Step 1 */}
          <div className={`step-item ${activeStep > 1 ? "step-completed" : activeStep === 1 ? "step-active" : "step-pending"}`}>
            <div className="step-circle">1</div>
            <div className="step-content">
              <span className="step-name">Detected (Prometheus Alertmanager)</span>
              <span className="step-time">10:15 AM</span>
            </div>
          </div>

          {/* Step 2 */}
          <div className={`step-item ${activeStep > 2 ? "step-completed" : activeStep === 2 ? "step-active" : "step-pending"}`}>
            <div className="step-circle">2</div>
            <div className="step-content">
              <span className="step-name">Acknowledged (10m Temporal Correlator)</span>
              <span className="step-time">10:18 AM</span>
            </div>
          </div>

          {/* Step 3 */}
          <div className={`step-item ${activeStep > 3 ? "step-completed" : activeStep === 3 ? "step-active" : "step-pending"}`}>
            <div className="step-circle green">3</div>
            <div className="step-content">
              <span className="step-name font-bold">
                Investigating (AI Root Cause Analysis){" "}
                {activeStep === 3 && <span className="active-tag">[ACTIVE]</span>}
              </span>
              <span className="step-status-badge">
                {activeStep > 3 ? "COMPLETED" : "[ACTIVE]"}
              </span>
            </div>
          </div>

          {/* Step 4 */}
          <div className={`step-item ${activeStep > 4 ? "step-completed" : activeStep === 4 ? "step-active" : "step-pending"}`}>
            <div className="step-circle">4</div>
            <div className="step-content">
              <span className="step-name">
                Mitigating (Action Plan Drafted){" "}
                {activeStep === 4 && <span className="active-tag-amber">[HUMAN APPROVAL REQUIRED]</span>}
              </span>
              <span className="step-time">{activeStep >= 4 ? "10:22 AM" : "Pending"}</span>
            </div>
          </div>

          {/* Step 5 */}
          <div className={`step-item ${activeStep === 5 ? "step-completed" : "step-pending"}`}>
            <div className="step-circle green">5</div>
            <div className="step-content">
              <span className="step-name">Resolved (Verified Autonomous Health)</span>
              <span className="step-time">{isResolved ? "10:25 AM" : "Pending"}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Card 2: Telemetry Metrics & Sparkline Graph */}
      <div className="workspace-card telemetry-card">
        {/* Metric KPI Chips Row */}
        <div className="telemetry-kpi-row">
          <div className="kpi-box">
            <span className="kpi-label">Latency</span>
            <div className="kpi-value-row">
              <strong className="kpi-value text-emerald">156ms</strong>
              <span className="kpi-delta text-emerald">(+120%)</span>
            </div>
          </div>

          <div className="kpi-box">
            <span className="kpi-label">Errors</span>
            <div className="kpi-value-row">
              <strong className="kpi-value text-rose">5.2%</strong>
              <span className="kpi-delta text-rose">(+4.8%)</span>
            </div>
          </div>

          <div className="kpi-box">
            <span className="kpi-label">Traffic</span>
            <div className="kpi-value-row">
              <strong className="kpi-value text-slate">890 RPM</strong>
              <span className="kpi-delta text-dim">&plusmn;1.2%</span>
            </div>
          </div>
        </div>

        {/* Latency Spike vs Baseline Graph */}
        <div className="telemetry-chart-wrap">
          <div className="chart-header">
            <span className="chart-title">Latency Spike vs Baseline</span>
          </div>

          {/* SVG Sparkline Area Chart */}
          <div className="chart-svg-container">
            <svg viewBox="0 0 500 130" className="chart-svg" preserveAspectRatio="none">
              <defs>
                {/* Red Spike Area Gradient */}
                <linearGradient id="spikeGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity="0.45" />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity="0.0" />
                </linearGradient>
                {/* White Baseline Area Gradient */}
                <linearGradient id="baseGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#94a3b8" stopOpacity="0.18" />
                  <stop offset="100%" stopColor="#94a3b8" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Grid Lines */}
              <line x1="40" y1="20" x2="490" y2="20" stroke="#1f2937" strokeDasharray="3 3" />
              <line x1="40" y1="50" x2="490" y2="50" stroke="#1f2937" strokeDasharray="3 3" />
              <line x1="40" y1="80" x2="490" y2="80" stroke="#1f2937" strokeDasharray="3 3" />
              <line x1="40" y1="110" x2="490" y2="110" stroke="#1f2937" />

              {/* Y Axis Labels */}
              <text x="10" y="24" fill="#64748b" fontSize="9">100</text>
              <text x="10" y="54" fill="#64748b" fontSize="9">60</text>
              <text x="10" y="84" fill="#64748b" fontSize="9">30</text>
              <text x="10" y="114" fill="#64748b" fontSize="9">0</text>

              {/* Baseline Area & Line */}
              <path
                d="M 40 95 Q 80 85, 120 90 T 200 88 T 280 85 T 360 88 T 440 90 L 490 89 L 490 110 L 40 110 Z"
                fill="url(#baseGrad)"
              />
              <path
                d="M 40 95 Q 80 85, 120 90 T 200 88 T 280 85 T 360 88 T 440 90 L 490 89"
                fill="none"
                stroke="#94a3b8"
                strokeWidth="1.5"
                strokeDasharray="2 2"
              />

              {/* Anomaly Red Latency Spike Area & Line */}
              <path
                d="M 40 90 Q 90 75, 140 85 T 220 70 L 260 20 L 280 75 Q 320 80, 380 85 T 490 90 L 490 110 L 40 110 Z"
                fill="url(#spikeGrad)"
              />
              <path
                d="M 40 90 Q 90 75, 140 85 T 220 70 L 260 20 L 280 75 Q 320 80, 380 85 T 490 90"
                fill="none"
                stroke="#ef4444"
                strokeWidth="2.5"
              />

              {/* Peak Circle Indicator */}
              <circle cx="260" cy="20" r="4.5" fill="#ef4444" stroke="#ffffff" strokeWidth="2" />
            </svg>
          </div>

          {/* X Axis Time Labels */}
          <div className="chart-x-ticks">
            <span>10:00</span>
            <span>10:10</span>
            <span>10:20</span>
            <span>10:30</span>
            <span>10:40</span>
          </div>

          {/* Legend */}
          <div className="chart-legend">
            <span className="legend-item">
              <span className="legend-dot red">●</span> Latency Spike
            </span>
            <span className="legend-item">
              <span className="legend-line white">—</span> Baseline
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
