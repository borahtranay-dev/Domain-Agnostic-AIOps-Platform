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
          <h2>Enterprise Cloud Service Topology</h2>
          <p>Real-time microservice dependency graph, latency telemetry, and cluster connectivity</p>
        </div>
        <div className="topology-header-badges">
          <span className="topology-net-badge">VPC: production-us-east-1</span>
          <span className="topology-cluster-badge">Kubernetes v1.30</span>
        </div>
      </div>

      <div className="topology-grid">
        {Object.entries(statuses).map(([key, svc]) => {
          const isOk = svc.status === "connected";
          const isDegraded = svc.status === "degraded";
          const isErr = svc.status === "error";

          return (
            <div
              key={key}
              className={`svc-card ${
                isOk ? "svc-card-ok" : isDegraded ? "svc-card-degraded" : "svc-card-err"
              }`}
            >
              <div className="svc-header">
                <div className="svc-title-row">
                  <span
                    className={`svc-dot ${
                      isOk ? "dot-ok" : isDegraded ? "dot-degraded" : "dot-err"
                    }`}
                  ></span>
                  <div>
                    <h3 className="svc-name">{svc.name}</h3>
                    <span className="svc-role-text">{svc.role}</span>
                  </div>
                </div>
                <span className={`svc-tier-badge ${svc.tier.includes("Tier-0") ? "tier-0" : ""}`}>
                  {svc.tier}
                </span>
              </div>

              {/* Service Telemetry KPI Strip */}
              <div className="svc-metrics-strip">
                <div className="svc-kpi">
                  <span className="kpi-micro-label">LATENCY (p99)</span>
                  <strong className={`kpi-micro-val ${isDegraded ? "text-amber" : "text-emerald"}`}>
                    {svc.latency}
                  </strong>
                </div>
                <div className="svc-kpi">
                  <span className="kpi-micro-label">UPTIME</span>
                  <strong className="kpi-micro-val text-slate">{svc.uptime}</strong>
                </div>
                <div className="svc-kpi">
                  <span className="kpi-micro-label">THROUGHPUT</span>
                  <strong className="kpi-micro-val text-slate">{svc.throughput}</strong>
                </div>
              </div>

              <div className="svc-body">
                <div className="svc-field">
                  <span className="field-label">Engine:</span>
                  <span className="field-val">{svc.technology}</span>
                </div>
                <div className="svc-field">
                  <span className="field-label">Health:</span>
                  <span
                    className={`status-text ${
                      isOk ? "text-emerald" : isDegraded ? "text-amber" : "text-rose"
                    }`}
                  >
                    {isOk ? "HEALTHY" : isDegraded ? "DEGRADED (INCIDENT)" : "OFFLINE"}
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
