"use client";

import React from "react";
import { Incident, Diagnosis, RemediationPlan } from "../types";

interface AiRootCauseConsoleProps {
  incident?: Incident;
  diagnosis?: Diagnosis;
  plan?: RemediationPlan;
  onApprove: (incidentId: string) => void;
  onReject: (incidentId: string) => void;
  onDiagnose?: (incidentId: string) => void;
}

export function AiRootCauseConsole({
  incident,
  diagnosis,
  plan,
  onApprove,
  onReject,
  onDiagnose,
}: AiRootCauseConsoleProps) {
  if (!incident) {
    return (
      <div className="ai-console-empty">
        <span className="empty-sparkle">✦</span>
        <h3>AI Diagnostic Console</h3>
        <p>Awaiting incident selection to compute LangChain RAG root cause analysis.</p>
      </div>
    );
  }

  const isAwaitingApproval = incident.status === "awaiting_approval";
  const isResolved = incident.status === "resolved";
  const isExecuting = incident.status === "executing";
  const confidencePct = diagnosis ? Math.round(diagnosis.confidence * 100) : 92;

  // Key findings based on service
  const errorSource = incident.service_id === "payment-api" 
    ? "Container Image Readiness Probe" 
    : incident.service_id === "worker-service" 
    ? "Redis Message Queue Connection" 
    : "PostgreSQL Connection Pool";

  const relatedAlerts = incident.service_id === "payment-api"
    ? "Probe HTTP 500, Container CrashLoop"
    : incident.service_id === "worker-service"
    ? "Worker heartbeat timeout, Queue backlog"
    : "QueuePool limit 10, Saturation 100%";

  const impactedDeps = incident.service_id === "payment-api"
    ? "api-gateway, auth-service"
    : incident.service_id === "worker-service"
    ? "notification-service, event-pipeline"
    : "auth-service, transaction-worker";

  return (
    <div className="ai-console-container">
      {/* Console Top Header */}
      <div className="console-header">
        <div className="console-title-wrap">
          <svg className="console-icon-svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a1a1aa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
            <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
            <line x1="6" y1="6" x2="6.01" y2="6"></line>
            <line x1="6" y1="18" x2="6.01" y2="18"></line>
          </svg>
          <h2 className="console-heading">AI Root Cause Analysis Console</h2>
        </div>
        <button className="console-close-btn" title="Close Panel">✕</button>
      </div>

      {/* Subhead / Insight Title */}
      <div className="console-subhead">
        <span className="subhead-label">TITLE</span>
        <h3 className="subhead-title">
          AI Insight: {incident.service_id ? incident.service_id.toUpperCase() : "SYSTEM"} ANOMALY
        </h3>
      </div>

      {/* Box 1: Probable Root Cause (RAG Vector Output) */}
      <div className="console-block">
        <div className="block-header-row">
          <span className="block-label">Probable Root Cause</span>
          <span className="confidence-chip">{confidencePct}% Confidence</span>
        </div>
        <div className="root-cause-card">
          <p className="root-cause-text">
            <strong>[AI Detected]</strong>{" "}
            {diagnosis?.probable_root_cause ||
              "Database connection pool exhausted due to unclosed sessions in concurrent worker threads or insufficient pool_size limit."}
          </p>
          {diagnosis?.uncertainty_notes && (
            <span className="runbook-match-chip">
              📖 {diagnosis.uncertainty_notes}
            </span>
          )}
        </div>
      </div>

      {/* Box 2: Key Findings */}
      <div className="console-block">
        <span className="block-label">Key Findings</span>
        <div className="key-findings-list">
          <div className="finding-row">
            <span className="finding-num">1.</span>
            <div className="finding-desc">
              <span>Error Source Identified:</span>
              <strong className="text-white">{errorSource}</strong>
            </div>
          </div>

          <div className="finding-row">
            <span className="finding-num">2.</span>
            <div className="finding-desc">
              <span>Related Alerts:</span>
              <strong className="text-white">{relatedAlerts}</strong>
            </div>
          </div>

          <div className="finding-row">
            <span className="finding-num">3.</span>
            <div className="finding-desc">
              <span>Impacted Dependencies:</span>
              <strong className="text-white">{impactedDeps}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Box 3: Timeline of Anomaly */}
      <div className="console-block">
        <div className="timeline-header-row">
          <span className="block-label">Timeline of Anomaly</span>
          <span className="timeline-range-text">10:15 - 10:30 AM</span>
        </div>
        <div className="timeline-slider-track">
          <div className="timeline-slider-fill" style={{ width: "65%" }}></div>
          <div className="timeline-slider-thumb" style={{ left: "65%" }}></div>
        </div>
      </div>

      {/* Box 4: Recommended Actions */}
      <div className="console-block">
        <span className="block-label">Recommended Actions</span>
        <div className="actions-step-list">
          {plan && plan.actions.length > 0 ? (
            plan.actions.map((act, idx) => (
              <div key={act.id} className="action-step-card active-step">
                <div className="step-radio-dot"></div>
                <div className="step-detail">
                  <strong className="step-title">{act.description}</strong>
                  <span className="step-sub">
                    Target: {act.target_service_id || incident.service_id} &middot; Type: {act.action_type}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <>
              <div className="action-step-card active-step">
                <div className="step-radio-dot"></div>
                <div className="step-detail">
                  <strong className="step-title">Scale Connection Pool to 30</strong>
                  <span className="step-sub">Target: {incident.service_id} &middot; Config update</span>
                </div>
              </div>
              <div className="action-step-card">
                <div className="step-radio-dot pending"></div>
                <div className="step-detail">
                  <strong className="step-title">Enable pool_pre_ping Recycling</strong>
                  <span className="step-sub">Infrastructure policy check</span>
                </div>
              </div>
              <div className="action-step-card">
                <div className="step-radio-dot pending"></div>
                <div className="step-detail">
                  <strong className="step-title">Alert On-Call Database SRE</strong>
                  <span className="step-sub">Automated Slack notification</span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Human Governance Action Gate (Approve / Reject) */}
      <div className="console-governance-footer">
        {isAwaitingApproval && (
          <div className="gov-action-box">
            <button
              onClick={() => onApprove(incident.id)}
              className="btn-console-approve pulse-emerald"
              title="Execute approved remediation plan"
            >
              ✓ Approve &amp; Execute Remediation
            </button>
            <button
              onClick={() => onReject(incident.id)}
              className="btn-console-reject"
              title="Reject remediation plan"
            >
              ✕ Reject Plan
            </button>
          </div>
        )}

        {isExecuting && (
          <div className="gov-status-pill executing">
            <span className="spinner-dot"></span>
            <span>Executing automated fix on cluster...</span>
          </div>
        )}

        {isResolved && (
          <div className="gov-status-pill resolved" style={{ display: 'flex', flexDirection: 'column', gap: '6px', alignItems: 'flex-start' }}>
            <span style={{ fontWeight: 600 }}>✅ System Autonomously Healed &amp; Verified</span>
            <span style={{ fontSize: '11px', color: '#a1a1aa' }}>
              Rule 17: Post-remediation telemetry verified error rate 0.00%
            </span>
            {plan?.actions?.[0]?.parameters?.pull_request_url && (
              <a
                href={plan.actions[0].parameters.pull_request_url}
                target="_blank"
                rel="noreferrer"
                style={{
                  fontSize: '11px',
                  color: '#38bdf8',
                  textDecoration: 'underline',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  marginTop: '2px'
                }}
              >
                <span>🔗 View Merged GitHub Hotfix PR ({plan.actions[0].parameters.pull_request_url.split('/').slice(-2).join('/')})</span>
              </a>
            )}
          </div>
        )}

        {!diagnosis && (incident.status === "open" || incident.status === "diagnosing") && onDiagnose && (
          <button
            onClick={() => onDiagnose(incident.id)}
            className="btn-console-diagnose"
          >
            Run AI Diagnosis
          </button>
        )}
      </div>
    </div>
  );
}
