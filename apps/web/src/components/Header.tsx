"use client";

import React, { useState, useEffect } from "react";

export function Header() {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [showUserMenu, setShowUserMenu] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("aiops-theme") as "light" | "dark" | null;
    if (saved) {
      setTheme(saved);
      document.documentElement.setAttribute("data-theme", saved);
    } else {
      document.documentElement.setAttribute("data-theme", "light");
    }
  }, []);

  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("aiops-theme", next);
  };

  return (
    <header className="cockpit-header">
      <div className="header-brand">
        <div className="brand-logo skeuo-convex">
          <span className="logo-icon">⚡</span>
        </div>
        <div>
          <div className="brand-title-wrap">
            <h1 className="brand-title">AIOps Operations Console</h1>
            <span className="badge-prod skeuo-pill">Production v1.0</span>
          </div>
          <p className="brand-subtitle">
            Infrastructure Observability &amp; Automated Remediation &middot; Cluster: <strong className="text-highlight">prod-primary</strong> &middot; Region: <span className="text-highlight">us-east-1</span>
          </p>
        </div>
      </div>

      <div className="header-status-group">
        {/* Real-Time Operational Status */}
        <div className="live-status-pill skeuo-inset">
          <span className="live-indicator"></span>
          <span className="live-text">MONITORING ACTIVE</span>
        </div>

        {/* Theme Toggle Button (3D Skeuo Pill) */}
        <button 
          onClick={toggleTheme} 
          className="theme-toggle-btn skeuo-button"
          title={`Switch to ${theme === "light" ? "Dark" : "Light"} theme`}
          aria-label="Toggle Theme"
        >
          {theme === "light" ? (
            <>
              <span className="theme-icon">🌙</span>
              <span className="theme-label">Dark</span>
            </>
          ) : (
            <>
              <span className="theme-icon">☀️</span>
              <span className="theme-label">Light</span>
            </>
          )}
        </button>

        {/* User Profile / Login Session Widget */}
        <div className="user-profile-wrapper">
          <button 
            className="user-profile-btn skeuo-button"
            onClick={() => setShowUserMenu(!showUserMenu)}
            title="Logged-in User Account"
          >
            <div className="user-avatar-initials">SS</div>
            <div className="user-meta-col">
              <span className="user-name-text">Saurav (Admin)</span>
              <span className="user-role-badge">Tier-1 SRE</span>
            </div>
            <span className="user-dropdown-caret">{showUserMenu ? "▲" : "▼"}</span>
          </button>

          {/* Interactive User Session Dropdown */}
          {showUserMenu && (
            <div className="user-dropdown-menu skeuo-card">
              <div className="dropdown-user-header">
                <div className="dropdown-avatar">SS</div>
                <div>
                  <strong>Saurav Sharma</strong>
                  <div className="dropdown-email">saurav@domain-agnostic.io</div>
                </div>
              </div>
              <div className="dropdown-divider"></div>
              <div className="dropdown-detail-row">
                <span>Account Role:</span>
                <span className="dropdown-badge-accent">Super Admin (RBAC: Tier-1)</span>
              </div>
              <div className="dropdown-detail-row">
                <span>Auth Session:</span>
                <span className="dropdown-badge-green">● Active (JWT Verified)</span>
              </div>
              <div className="dropdown-detail-row">
                <span>Tenant Scope:</span>
                <code>global-all-clusters</code>
              </div>
              <div className="dropdown-divider"></div>
              <div className="dropdown-actions-row">
                <button 
                  className="dropdown-btn-switch skeuo-button"
                  onClick={() => alert("Simulated: Switched tenant context to tenant-01.")}
                >
                  Switch Tenant
                </button>
                <button 
                  className="dropdown-btn-logout skeuo-button"
                  onClick={() => alert("Session logout simulated.")}
                >
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
