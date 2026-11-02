"use client";

import React, { useState } from "react";

interface DemoSimulatorBarProps {
  onSimulate: (scenario: "prometheus" | "github" | "worker") => void;
  onReset: () => void;
  isSimulating?: boolean;
}

export function DemoSimulatorBar({ onSimulate, onReset, isSimulating }: DemoSimulatorBarProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="demo-simulator-wrapper">
      <div className="demo-simulator-bar">
        <div className="demo-brand-col">
          <div className="demo-badge">
            <span className="demo-pulse-dot"></span>
            <span>TEACHER &amp; EVALUATOR DEMO CONTROLS</span>
          </div>
          <p className="demo-help-text">
            Click any button below to trigger a live production failure signal and observe real-time RAG root cause diagnosis &amp; human governance:
          </p>
        </div>

        <div className="demo-actions-col">
          <button
            onClick={() => onSimulate("prometheus")}
            disabled={isSimulating}
            className="demo-btn demo-btn-danger"
            title="Inject real-time Prometheus connection pool exhaustion alert"
          >
            <span className="demo-btn-icon">🔴</span>
            <div className="demo-btn-text">
              <strong>Prometheus Alert</strong>
              <small>DB Pool Starvation (RB-001)</small>
            </div>
          </button>

          <button
            onClick={() => onSimulate("github")}
            disabled={isSimulating}
            className="demo-btn demo-btn-warning"
            title="Inject GitHub Actions deployment readiness probe failure"
          >
            <span className="demo-btn-icon">🟠</span>
            <div className="demo-btn-text">
              <strong>GitHub CI/CD Failure</strong>
              <small>Probe Timeout (RB-006 Rollback)</small>
            </div>
          </button>

          <button
            onClick={() => onSimulate("worker")}
            disabled={isSimulating}
            className="demo-btn demo-btn-purple"
            title="Inject background Redis worker connection timeout"
          >
            <span className="demo-btn-icon">🟡</span>
            <div className="demo-btn-text">
              <strong>Worker Timeout</strong>
              <small>Redis Queue Timeout (RB-007)</small>
            </div>
          </button>

          <button
            onClick={onReset}
            className="demo-btn demo-btn-secondary"
            title="Reset incident list to initial benchmark state"
          >
            <span className="demo-btn-icon">🔄</span>
            <div className="demo-btn-text">
              <strong>Reset State</strong>
              <small>Restore Initial</small>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
