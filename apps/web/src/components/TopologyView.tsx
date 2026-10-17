"use client";

import React from "react";
import { ServiceTopologyStatus } from "../types";

interface TopologyViewProps {
  statuses: Record<string, ServiceTopologyStatus>;
}

export function TopologyView({ statuses }: TopologyViewProps) {
  return (
    <div className="topology-card">
      <div className="topology-header">
        <div>
          <h2>Autonomous Cloud Service Topology</h2>
          <p>Live health and inter-service connectivity across all 6 containerized microservices</p>
        </div>
        <span className="topology-net-badge">Network: aiops-network (Bridge)</span>
      </div>

      <div className="topology-grid">
        {Object.entries(statuses).map(([key, svc]) => {
          const isOk = svc.status === "connected";
          const isErr = svc.status === "error";

          return (
            <div key={key} className={`svc-card ${isOk ? "svc-card-ok" : isErr ? "svc-card-err" : "svc-card-checking"}`}>
              <div className="svc-header">
                <div className="svc-title-row">
                  <span className={`svc-dot ${isOk ? "dot-ok" : isErr ? "dot-err" : "dot-checking"}`}></span>
                  <h3 className="svc-name">{svc.name}</h3>
                </div>
                <span className="svc-owner-badge">{svc.owner}</span>
              </div>

              <div className="svc-body">
                <div className="svc-field">
                  <span className="field-label">Subsystem:</span>
                  <code className="field-code">{svc.subsystem}</code>
                </div>
                <div className="svc-field">
                  <span className="field-label">Tech Stack:</span>
                  <span className="field-val">{svc.technology}</span>
                </div>
                <div className="svc-field">
                  <span className="field-label">Status:</span>
                  <span className={`status-text ${isOk ? "text-emerald" : isErr ? "text-rose" : "text-amber"}`}>
                    {svc.status.toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="svc-footer">
                <span className="svc-details">{svc.details}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
