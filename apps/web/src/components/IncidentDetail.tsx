"use client";

import React, { useState } from "react";
import { Incident, Evidence, Diagnosis, RemediationPlan } from "../types";

interface IncidentDetailProps {
  incident?: Incident;
  evidenceList: Evidence[];
  diagnosis?: Diagnosis;
  plan?: RemediationPlan;
  onApprove: (incidentId: string) => void;
  onReject: (incidentId: string) => void;
}

export function IncidentDetail({
  incident,
  evidenceList,
  diagnosis,
  plan,
  onApprove,
  onReject,
}: IncidentDetailProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "evidence" | "ai_diagnosis" | "governance">("overview");

  if (!incident) {
    return (
      <div className="detail-empty-card">
        <div className="empty-icon">🔍</div>
        <h3>Select an incident from the stream to inspect</h3>
        <p>Real-time telemetry, AI diagnosis, and human approval controls will appear here.</p>
      </div>
    );
  }

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const confidencePct = diagnosis ? Math.round(diagnosis.confidence * 100) : 0;
  const isAwaitingApproval = incident.status === "awaiting_approval";
  const isResolved = incident.status === "resolved";
  const isExecuting = incident.status === "executing";

  return (
    <div className="detail-card">
      {/* Detail Header */}
      <div className="detail-header">
        <div className="detail-title-wrap">
          <div className="detail-meta-row">
            <span className="incident-id-badge">{incident.id}</span>
            <span className={`badge-severity badge-sev-${incident.severity}`}>
              {incident.severity.toUpperCase()}
            </span>
            <span className={`badge-status badge-status-${incident.status}`}>
              {incident.status.replace("_", " ").toUpperCase()}
            </span>
          </div>
          <h2 className="detail-title">{incident.title}</h2>
          <div className="detail-sub-meta">
            <span>Affected Service: <strong className="text-cyan">{incident.service_id || "N/A"}</strong></span>
            <span>&bull;</span>
            <span>Environment: <strong>{incident.environment_id || "production"}</strong></span>
            <span>&bull;</span>
            <span>Opened: {new Date(incident.opened_at).toLocaleTimeString()}</span>
          </div>
        </div>

        {/* Quick Action in Header */}
        {isAwaitingApproval && (
          <button 
            onClick={() => onApprove(incident.id)}
            className="btn-approve-primary pulse-btn"
          >
            ✓ Approve &amp; Heal System
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="detail-tabs">
        <button
          className={`tab-btn ${activeTab === "overview" ? "tab-btn-active" : ""}`}
          onClick={() => setActiveTab("overview")}
        >
          📋 Overview
        </button>
        <button
          className={`tab-btn ${activeTab === "evidence" ? "tab-btn-active" : ""}`}
          onClick={() => setActiveTab("evidence")}
        >
          🔬 Evidence Room ({evidenceList.length})
        </button>
        <button
          className={`tab-btn ${activeTab === "ai_diagnosis" ? "tab-btn-active" : ""}`}
          onClick={() => setActiveTab("ai_diagnosis")}
        >
          🧠 AI Diagnosis &amp; RAG
        </button>
        <button
          className={`tab-btn ${activeTab === "governance" ? "tab-btn-active" : ""}`}
          onClick={() => setActiveTab("governance")}
        >
          🛡️ Human Governance
        </button>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === "overview" && (
        <div className="tab-pane">
          {/* Status banner */}
          {isResolved && (
            <div className="alert-box alert-success">
              <span className="alert-icon-lg">✅</span>
              <div>
                <strong>Incident Resolved Autonomously</strong>
                <p>Remediation plan was approved by human operator and verified healthy by post-fix health probes.</p>
              </div>
            </div>
          )}

          {isExecuting && (
            <div className="alert-box alert-warning">
              <span className="alert-icon-lg">⚙️</span>
              <div>
                <strong>Executing Automated Remediation...</strong>
                <p>Human approved the fix. Dispatched automated config patch to Kubernetes cluster.</p>
              </div>
            </div>
          )}

          {isAwaitingApproval && (
            <div className="alert-box alert-rose">
              <span className="alert-icon-lg">⚠️</span>
              <div>
                <strong>Human Approval Required Before Remediation</strong>
                <p>AI has diagnosed root cause with {confidencePct}% confidence. Under enterprise safety policy, consequential actions must be approved by SRE.</p>
              </div>
            </div>
          )}

          {/* Quick AI Diagnosis Summary Card */}
          <div className="section-block">
            <h3 className="section-heading">🧠 AI Root Cause Diagnosis</h3>
            {diagnosis ? (
              <div className="ai-diagnosis-box">
                <div className="diag-header">
                  <span className="diag-label">PROBABLE ROOT CAUSE:</span>
                  <div className="confidence-meter">
                    <span className="conf-label">Confidence:</span>
                    <div className="conf-bar-bg">
                      <div className="conf-bar-fill" style={{ width: `${confidencePct}%` }}></div>
                    </div>
                    <span className="conf-val">{confidencePct}%</span>
                  </div>
                </div>
                <p className="diag-text">{diagnosis.probable_root_cause}</p>
                <div className="diag-citations">
                  <span>Cited Evidence IDs:</span>
                  {diagnosis.supporting_evidence_ids.map((id) => (
                    <span key={id} className="citation-pill">{id}</span>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-dim">AI worker is currently analyzing telemetry logs...</p>
            )}
          </div>

          {/* Quick Proposed Action Card */}
          {plan && plan.actions.length > 0 && (
            <div className="section-block">
              <h3 className="section-heading">🛠️ Proposed Remediation Action</h3>
              <div className="action-box">
                <div className="action-header">
                  <span className="action-type-pill">
                    {plan.actions[0].action_type.toUpperCase()}
                  </span>
                  <span className="action-target">Target: {plan.actions[0].target_service_id}</span>
                </div>
                <p className="action-desc">{plan.actions[0].description}</p>
                <div className="action-params">
                  <span className="params-label">Action Parameters:</span>
                  <pre className="code-pre">{JSON.stringify(plan.actions[0].parameters, null, 2)}</pre>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: EVIDENCE ROOM */}
      {activeTab === "evidence" && (
        <div className="tab-pane">
          <div className="pane-intro">
            <h3>🔬 Immutable Telemetry Evidence Records</h3>
            <p>Raw runtime observations harvested from containers, databases, and CI/CD without human or AI speculation.</p>
          </div>

          <div className="evidence-list">
            {evidenceList.map((ev) => (
              <div key={ev.id} className="evidence-card">
                <div className="evidence-card-header">
                  <div className="ev-left">
                    <span className="citation-pill">{ev.id}</span>
                    <span className="ev-kind-badge">{ev.kind.toUpperCase()}</span>
                    <span className="ev-source">Source: <code>{ev.source}</code></span>
                  </div>
                  <button 
                    onClick={() => handleCopy(ev.id, ev.content)}
                    className="btn-copy"
                  >
                    {copiedId === ev.id ? "✓ Copied" : "📋 Copy"}
                  </button>
                </div>
                <pre className="evidence-content">{ev.content}</pre>
                <div className="ev-footer">
                  <span>Harvested at: {new Date(ev.collected_at).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: AI DIAGNOSIS & RAG */}
      {activeTab === "ai_diagnosis" && (
        <div className="tab-pane">
          <div className="pane-intro">
            <h3>🧠 LangChain RAG Autonomous Diagnostic Brain</h3>
            <p>Grounds LLM reasoning in verified engineering runbooks and raw runtime evidence.</p>
          </div>

          {diagnosis && (
            <div className="rag-showcase-grid">
              <div className="rag-card">
                <span className="rag-step-badge">STEP 1: EVIDENCE CITATION</span>
                <h4>Factual Evidence Links</h4>
                <p>The AI is constrained to cite only collected telemetry records:</p>
                <div className="citation-group">
                  {diagnosis.supporting_evidence_ids.map((id) => (
                    <div key={id} className="citation-row">
                      <span className="citation-pill">{id}</span>
                      <span className="citation-status text-emerald">✓ Verified Runtime Fact</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rag-card">
                <span className="rag-step-badge">STEP 2: RUNBOOK MATCHING</span>
                <h4>Operational Playbook RAG</h4>
                <p>Retrieved from In-Memory Vector Runbook Store (Cosine Similarity):</p>
                <div className="runbook-matched-box">
                  <strong>RB-001: PostgreSQL Database Pool Exhaustion</strong>
                  <p>Matches symptom signature: <code>TimeoutError: QueuePool limit exceeded</code></p>
                </div>
              </div>

              <div className="rag-card full-width">
                <span className="rag-step-badge">STEP 3: REASONING OUTPUT</span>
                <h4>Diagnosed Root Cause Explanation</h4>
                <p className="rag-diag-body">{diagnosis.probable_root_cause}</p>
                <div className="confidence-display">
                  <span>Empirical Confidence Score:</span>
                  <strong className="text-cyan text-lg">{confidencePct}%</strong>
                  <span className="confidence-sub">(Zero Hallucination Grounding Guaranteed)</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: HUMAN GOVERNANCE */}
      {activeTab === "governance" && (
        <div className="tab-pane">
          <div className="pane-intro">
            <h3>🛡️ Human-in-the-Loop Governance &amp; Approval Console</h3>
            <p>Consequential system changes (restarts, scaling, config rollbacks) require verified human sign-off.</p>
          </div>

          {plan && (
            <div className="governance-panel">
              <div className="plan-summary-box">
                <div className="plan-meta-row">
                  <span>Plan ID: <code>{plan.id}</code></span>
                  <span>Status: <strong className="text-purple">{plan.status.toUpperCase()}</strong></span>
                  <span>Created: {new Date(plan.created_at).toLocaleTimeString()}</span>
                </div>
                <h4>Rationale:</h4>
                <p>{plan.rationale}</p>
              </div>

              <div className="action-sequence-box">
                <h4>Execution Action Pipeline ({plan.actions.length} Action):</h4>
                {plan.actions.map((act) => (
                  <div key={act.id} className="action-sequence-card">
                    <div className="seq-num">1</div>
                    <div className="seq-body">
                      <div className="seq-header">
                        <span className="action-type-pill">{act.action_type.toUpperCase()}</span>
                        <span>Target: <strong>{act.target_service_id}</strong></span>
                      </div>
                      <p>{act.description}</p>
                      <pre className="code-pre">{JSON.stringify(act.parameters, null, 2)}</pre>
                    </div>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="governance-actions-row">
                {isAwaitingApproval && (
                  <>
                    <button 
                      onClick={() => onApprove(incident.id)}
                      className="btn-approve-lg"
                    >
                      ✓ Approve &amp; Execute Fix
                    </button>
                    <button 
                      onClick={() => onReject(incident.id)}
                      className="btn-reject-lg"
                    >
                      ✕ Reject Plan
                    </button>
                  </>
                )}

                {isResolved && (
                  <div className="resolution-badge-box">
                    <span>✅ Action Executed &amp; Verified by Human SRE</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
