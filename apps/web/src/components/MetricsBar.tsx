"use client";

import React from "react";

interface MetricsBarProps {
  activeCount: number;
  criticalCount: number;
  resolvedCount: number;
}

export function MetricsBar({ activeCount, criticalCount, resolvedCount }: MetricsBarProps) {
  return (
    <div className="metrics-grid">
      {/* Metric 1 */}
      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-label">ACTIVE INCIDENTS</span>
          <span className="metric-icon alert-icon">🚨</span>
        </div>
        <div className="metric-value-wrap">
          <span className="metric-value">{activeCount}</span>
          <span className="metric-badge badge-rose">{criticalCount} Critical</span>
        </div>
        <div className="metric-subtext">Autonomous Telemetry Ingested</div>
      </div>

      {/* Metric 2 */}
      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-label">AVG SELF-HEAL MTTR</span>
          <span className="metric-icon timer-icon">⏱️</span>
        </div>
        <div className="metric-value-wrap">
          <span className="metric-value text-emerald">84s</span>
          <span className="metric-badge badge-emerald">-98% vs Manual</span>
        </div>
        <div className="metric-subtext">Target: &lt;90s (Human Manual: 3.5 hrs)</div>
      </div>

      {/* Metric 3 */}
      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-label">AI RAG CONFIDENCE</span>
          <span className="metric-icon brain-icon">🧠</span>
        </div>
        <div className="metric-value-wrap">
          <span className="metric-value text-cyan">94.2%</span>
          <span className="metric-badge badge-cyan">Zero Hallucination</span>
        </div>
        <div className="metric-subtext">Grounded in Runbooks &amp; Traces</div>
      </div>

      {/* Metric 4 */}
      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-label">HUMAN GOVERNANCE</span>
          <span className="metric-icon shield-icon">🛡️</span>
        </div>
        <div className="metric-value-wrap">
          <span className="metric-value text-purple">100%</span>
          <span className="metric-badge badge-purple">{resolvedCount} Approved</span>
        </div>
        <div className="metric-subtext">Consequential Fixes Verified</div>
      </div>
    </div>
  );
}
