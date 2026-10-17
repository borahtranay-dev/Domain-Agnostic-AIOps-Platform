"use client";

import React, { useState } from "react";
import { Incident, Severity, IncidentStatus } from "../types";

interface IncidentFeedProps {
  incidents: Incident[];
  selectedId: string;
  onSelect: (id: string) => void;
}

export function IncidentFeed({ incidents, selectedId, onSelect }: IncidentFeedProps) {
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filtered = incidents.filter((inc) => {
    if (severityFilter !== "all" && inc.severity !== severityFilter) return false;
    if (statusFilter !== "all" && inc.status !== statusFilter) return false;
    return true;
  });

  return (
    <div className="incident-feed-card">
      <div className="feed-header">
        <div>
          <h2 className="feed-title">Real-Time Incident Stream</h2>
          <p className="feed-subtitle">{filtered.length} correlated failure signals active</p>
        </div>

        {/* Filters */}
        <div className="feed-filters">
          <select 
            className="filter-select"
            value={severityFilter} 
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select 
            className="filter-select"
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Statuses</option>
            <option value="awaiting_approval">Awaiting Approval</option>
            <option value="diagnosing">Diagnosing</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      <div className="feed-list">
        {filtered.map((inc) => {
          const isSelected = inc.id === selectedId;
          const severityClass = `badge-sev-${inc.severity}`;
          const statusClass = `badge-status-${inc.status}`;

          return (
            <div
              key={inc.id}
              onClick={() => onSelect(inc.id)}
              className={`feed-item ${isSelected ? "feed-item-selected" : ""}`}
            >
              <div className="feed-item-header">
                <span className={`badge-severity ${severityClass}`}>
                  {inc.severity.toUpperCase()}
                </span>
                <span className={`badge-status ${statusClass}`}>
                  {inc.status.replace("_", " ").toUpperCase()}
                </span>
                <span className="feed-item-time" suppressHydrationWarning>
                  {new Date(inc.opened_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>

              <h3 className="feed-item-title">{inc.title}</h3>

              <div className="feed-item-footer">
                <span className="service-tag">
                  📦 {inc.service_id || "global"}
                </span>
                <span className="env-tag">
                  🌐 {inc.environment_id || "prod"}
                </span>
                <span className="events-count">
                  ⚡ {inc.event_ids.length} Telemetry Events
                </span>
              </div>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="feed-empty">
            <p>No incidents match the selected filter criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
}
