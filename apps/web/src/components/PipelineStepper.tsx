"use client";

import React from "react";
import { IncidentStatus } from "../types";

interface PipelineStepperProps {
  status: IncidentStatus;
}

interface StepItem {
  key: string;
  label: string;
  sublabel: string;
  icon: string;
}

export function PipelineStepper({ status }: PipelineStepperProps) {
  const steps: StepItem[] = [
    { key: "open", label: "Alert Ingested", sublabel: "Webhook telemetry", icon: "📡" },
    { key: "correlated", label: "Correlated", sublabel: "10m sliding window", icon: "🔗" },
    { key: "diagnosing", label: "RAG Diagnosis", sublabel: "Vector runbook match", icon: "🧠" },
    { key: "awaiting_approval", label: "Human Gate", sublabel: "SRE safety review", icon: "🛡️" },
    { key: "resolved", label: "Auto-Healed", sublabel: "Verified healthy", icon: "✅" },
  ];

  // Helper to determine status of each step
  const getStepState = (stepKey: string): "completed" | "current" | "pending" => {
    if (status === "resolved" || status === "closed") {
      return "completed";
    }

    if (status === "executing" || status === "verifying") {
      if (stepKey === "resolved") return "current";
      return "completed";
    }

    if (status === "awaiting_approval") {
      if (stepKey === "awaiting_approval") return "current";
      if (stepKey === "resolved") return "pending";
      return "completed";
    }

    if (status === "diagnosing") {
      if (stepKey === "open" || stepKey === "correlated") return "completed";
      if (stepKey === "diagnosing") return "current";
      return "pending";
    }

    // Default open
    if (stepKey === "open") return "current";
    return "pending";
  };

  return (
    <div className="pipeline-stepper-container">
      <div className="stepper-title-row">
        <span className="stepper-caption">⚡ Autonomous SRE Remediation Pipeline</span>
        <span className="stepper-current-pill">
          Current State: <strong>{status.replace("_", " ").toUpperCase()}</strong>
        </span>
      </div>

      <div className="stepper-track">
        {steps.map((step, idx) => {
          const state = getStepState(step.key);
          const isLast = idx === steps.length - 1;

          return (
            <React.Fragment key={step.key}>
              <div className={`stepper-node stepper-node-${state}`}>
                <div className="stepper-circle">
                  {state === "completed" ? "✓" : step.icon}
                </div>
                <div className="stepper-label-group">
                  <span className="stepper-step-title">{step.label}</span>
                  <span className="stepper-step-sub">{step.sublabel}</span>
                </div>
              </div>
              {!isLast && (
                <div className={`stepper-connector stepper-conn-${state === "completed" ? "completed" : "pending"}`} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
