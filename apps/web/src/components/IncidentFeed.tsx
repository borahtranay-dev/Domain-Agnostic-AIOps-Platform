"use client";

import React, { useState } from "react";
import { Incident } from "../types";

interface IncidentFeedProps {
  incidents: Incident[];
  selectedId: string;
  onSelect: (id: string) => void;
}

export function IncidentFeed({ incidents, selectedId, onSelect }: IncidentFeedProps) {
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filtered = incidents.filter((inc) => {
    if (severityFilter !== "all" && inc.severity !== severityFilter) return false;
    if (statusFilter !== "all" && inc.status !== statusFilter) return false;
    if (searchTerm.trim() !== "") {
      const q = searchTerm.toLowerCase();
      const matchTitle = inc.title.toLowerCase().includes(q);
      const matchId = inc.id.toLowerCase().includes(q);
      const matchService = (inc.service_id || "").toLowerCase().includes(q);
      if (!matchTitle && !matchId && !matchService) return false;
    }
    return true;
  });

  return (
    <div className="incident-feed-card">
      <div className="feed-header">
        <div className="feed-title-wrap">
          <h2 className="feed-title">Real-Time Incident Stream</h2>
          <span className="feed-count-pill">{filtered.length} active</span>
        </div>

        {/* Search input for instant teacher demonstration */}
        <div className="feed-search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="feed-search-input"
            placeholder="Search service, ID, error..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <button 
              className="search-clear-btn" 
              onClick={() => setSearchTerm("")}
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="feed-filters">
          <select 
            className="filter-select"
            value={severityFilter} 
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="all">All Severities</option>
            <option value="critical">🔴 Critical</option>
            <option value="high">🟠 High</option>
            <option value="medium">🟡 Medium</option>
            <option value="low">🟢 Low</option>
          </select>

          <select 
            className="filter-select"
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Statuses</option>
            <option value="awaiting_approval">⏳ Awaiting Approval</option>
            <option value="diagnosing">🧠 Diagnosing</option>
            <option value="open">📡 Open</option>
            <option value="resolved">✅ Resolved</option>
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
                  ⚡ {inc.event_ids.length} Events
                </span>
              </div>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="feed-empty">
            <span className="empty-feed-icon">🔍</span>
            <p>No incidents match the search criteria.</p>
            <button 
              className="btn-reset-filters"
              onClick={() => {
                setSearchTerm("");
                setSeverityFilter("all");
                setStatusFilter("all");
              }}
            >
              Reset Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
