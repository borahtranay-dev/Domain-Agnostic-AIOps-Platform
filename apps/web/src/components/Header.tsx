"use client";

import React, { useState, useEffect } from "react";

export function Header() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

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
        <div className="brand-logo">
          <span className="logo-icon">⚡</span>
        </div>
        <div>
          <div className="brand-title-wrap">
            <h1 className="brand-title">AIOps Operations Console</h1>
            <span className="badge-prod">Production v1.0</span>
          </div>
          <p className="brand-subtitle">
            Infrastructure Observability &amp; Automated Incident Remediation &middot; Cluster: <strong className="text-highlight">prod-primary</strong> &middot; Region: <span className="text-highlight">us-east-1</span>
          </p>
        </div>
      </div>

      <div className="header-status-group">
        <div className="live-status-pill">
          <span className="live-indicator"></span>
          <span className="live-text">MONITORING ACTIVE</span>
        </div>

        {/* Theme Toggle Button */}
        <button 
          onClick={toggleTheme} 
          className="theme-toggle-btn"
          title={`Switch to ${theme === "light" ? "Dark" : "Light"} theme`}
          aria-label="Toggle Theme"
        >
          {theme === "light" ? (
            <>
              <span className="theme-icon">🌙</span>
              <span className="theme-label">Dark Mode</span>
            </>
          ) : (
            <>
              <span className="theme-icon">☀️</span>
              <span className="theme-label">Light Mode</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
}
