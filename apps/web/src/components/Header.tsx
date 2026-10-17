"use client";

import React from "react";

export function Header() {
  return (
    <header className="cockpit-header">
      <div className="header-brand">
        <div className="brand-logo">
          <span className="logo-pulse"></span>
          <span className="logo-icon">⚡</span>
        </div>
        <div>
          <div className="brand-title-wrap">
            <h1 className="brand-title">AIOps Autonomous SRE Cockpit</h1>
            <span className="badge-phase">Phase P3 Live</span>
          </div>
          <p className="brand-subtitle">
            Domain-Agnostic Self-Healing Platform &middot; Subsystem: <code className="code-tag">apps/web</code> &middot; Lead: <strong className="text-cyan">Vivek (Frontend)</strong>
          </p>
        </div>
      </div>

      <div className="header-status-group">
        <div className="live-status-pill">
          <span className="live-indicator"></span>
          <span className="live-text">AUTONOMOUS LOOP ACTIVE</span>
        </div>
        <div className="zero-cost-badge">
          <span>Cloud Tier: <strong>$0.00 / Free</strong></span>
        </div>
      </div>
    </header>
  );
}
