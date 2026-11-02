"use client";

import React, { useState } from "react";
import { Incident } from "../types";

interface IncidentStreamColumnProps {
  incidents: Incident[];
  selectedId: string;
  onSelect: (id: string) => void;
  searchFilter?: string;
}

export function IncidentStreamColumn({
  incidents,
  selectedId,
  onSelect,
  searchFilter = "",
}: IncidentStreamColumnProps) {
  const [filterSeverity, setFilterSeverity] = useState<string>("all");

  const filtered = incidents.filter((inc) => {
    if (filterSeverity !== "all" && inc.severity !== filterSeverity) return false;
    if (searchFilter.trim() !== "") {
      const q = searchFilter.toLowerCase();
      const matchTitle = inc.title.toLowerCase().includes(q);
      const matchId = inc.id.toLowerCase().includes(q);
      const matchService = (inc.service_id || "").toLowerCase().includes(q);
      if (!matchTitle && !matchId && !matchService) return false;
    }
    return true;
  });

  return (
    <div className="stream-col-container">
      {/* Stream Column Header */}
      <div className="stream-col-header">
        <div className="stream-header-top">
          <h2 className="stream-heading">Incident Stream List</h2>
          <button className="btn-more-options" title="Options">•••</button>
        </div>
        <div className="stream-active-summary">
          <span className="summary-text">
            Active Incidents ({filtered.length})
          </span>
          <span className="summary-caret">▼</span>
        </div>

        {/* Quick filter pills */}
        <div className="stream-filter-pills">
          <button
            onClick={() => setFilterSeverity("all")}
            className={`filter-pill ${filterSeverity === "all" ? "active" : ""}`}
          >
            All
          </button>
          <button
            onClick={() => setFilterSeverity("critical")}
            className={`filter-pill pill-critical ${filterSeverity === "critical" ? "active" : ""}`}
          >
            Critical
          </button>
          <button
            onClick={() => setFilterSeverity("high")}
            className={`filter-pill pill-high ${filterSeverity === "high" ? "active" : ""}`}
          >
            High
          </button>
          <button
            onClick={() => setFilterSeverity("medium")}
            className={`filter-pill pill-medium ${filterSeverity === "medium" ? "active" : ""}`}
          >
            Medium
          </button>
        </div>
      </div>

      {/* Scrollable Incident Stream */}
      <div className="stream-items-list">
        {filtered.map((inc) => {
          const isSelected = inc.id === selectedId;
          const isCritical = inc.severity === "critical";
          const isWarning = inc.severity === "high" || inc.severity === "medium";
          const dateObj = new Date(inc.opened_at);
          const timeStr = isNaN(dateObj.getTime())
            ? "10:15 AM"
            : `${(dateObj.getUTCHours() % 12 || 12).toString().padStart(2, "0")}:${dateObj.getUTCMinutes().toString().padStart(2, "0")} ${dateObj.getUTCHours() >= 12 ? "PM" : "AM"}`;

          return (
            <div
              key={inc.id}
              onClick={() => onSelect(inc.id)}
              className={`stream-item-card ${isSelected ? "item-selected" : ""} ${
                isCritical ? "border-critical" : isWarning ? "border-warning" : "border-info"
              }`}
            >
              {/* Top Row: Time, Service, and Opened Time */}
              <div className="item-meta-row" suppressHydrationWarning>
                <span className="item-time-prefix" suppressHydrationWarning>{timeStr}</span>
                <span className="item-service-name">{inc.service_id || "core-service"}</span>
                <span className="item-time-right" suppressHydrationWarning>
                  {timeStr}
                </span>
              </div>

              {/* Second Row: Severity Tag & Service Badge */}
              <div className="item-badge-row">
                <span
                  className={`severity-badge ${
                    isCritical ? "sev-critical" : isWarning ? "sev-warning" : "sev-low"
                  }`}
                >
                  {inc.severity.toUpperCase()}
                </span>
                <span className="item-service-inline">{inc.service_id || "system"}</span>
              </div>

              {/* Third Row: Incident Title / Summary */}
              <div className="item-title-row">
                <p className="item-title-text">{inc.title}</p>
              </div>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="stream-empty-state">
            <span className="empty-icon">🔍</span>
            <p>No active incidents found.</p>
          </div>
        )}
      </div>
    </div>
  );
}
