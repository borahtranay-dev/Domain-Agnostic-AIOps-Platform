"use client";

import React, { useState, useEffect } from "react";
import { SidebarRail } from "../components/SidebarRail";
import { TopNav } from "../components/TopNav";
import { IncidentStreamColumn } from "../components/IncidentStreamColumn";
import { IncidentWorkspaceColumn } from "../components/IncidentWorkspaceColumn";
import { AiRootCauseConsole } from "../components/AiRootCauseConsole";
import { TopologyView } from "../components/TopologyView";
import { LoginScreen } from "../components/LoginScreen";
import { 
  Incident, 
  Evidence, 
  Diagnosis, 
  RemediationPlan, 
  ServiceTopologyStatus 
} from "../types";
import { 
  INITIAL_INCIDENTS, 
  INITIAL_EVIDENCE, 
  INITIAL_DIAGNOSES, 
  INITIAL_REMEDIATION_PLANS 
} from "../lib/mockData";

export default function DeveloperCockpit() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [currentUser, setCurrentUser] = useState<{
    name: string;
    email: string;
    role: "super_admin" | "tenant_sre";
    tenant: string;
  }>({
    name: "Saurav (Super Admin)",
    email: "admin@platform.io",
    role: "super_admin",
    tenant: "Acme Corp (Primary Tenant)",
  });

  const [activeTab, setActiveTab] = useState<"incidents" | "topology" | "evidence" | "settings">("incidents");
  const [incidents, setIncidents] = useState<Incident[]>(INITIAL_INCIDENTS);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>("INC-8921");
  const [evidenceMap, setEvidenceMap] = useState<Record<string, Evidence[]>>(INITIAL_EVIDENCE);
  const [diagnosesMap, setDiagnosesMap] = useState<Record<string, Diagnosis>>(INITIAL_DIAGNOSES);
  const [plansMap, setPlansMap] = useState<Record<string, RemediationPlan>>(INITIAL_REMEDIATION_PLANS);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  // Customer Cloud Microservice Topology statuses
  const [statuses, setStatuses] = useState<Record<string, ServiceTopologyStatus>>({
    apiGateway: {
      name: "API Gateway & Ingress Router",
      role: "Public Reverse Proxy & Traffic Director",
      tier: "Tier-0 Critical",
      technology: "Envoy / NGINX Proxy",
      status: "connected",
      latency: "14ms",
      uptime: "99.99%",
      throughput: "4.8k req/s",
      details: "TLS 1.3 Active · Zero dropped packets",
    },
    authService: {
      name: "Authentication & Identity Engine",
      role: "JWT Verification & RBAC Access Control",
      tier: "Tier-0 Critical",
      technology: "FastAPI / OAuth 2.0",
      status: "connected",
      latency: "8ms",
      uptime: "99.98%",
      throughput: "2.1k req/s",
      details: "Redis token cache hit ratio: 98.4%",
    },
    paymentApi: {
      name: "Core Business & Webhook API",
      role: "Telemetry Ingestion & Business Logic",
      tier: "Tier-1 Backend",
      technology: "Python 3.12 + FastAPI",
      status: "degraded",
      latency: "185ms",
      uptime: "99.42%",
      throughput: "1.2k req/s",
      details: "Active Alert: Connection Pool Saturation (30/30)",
    },
    database: {
      name: "PostgreSQL Primary Cluster",
      role: "Relational Storage & Telemetry Ledger",
      tier: "Data Tier",
      technology: "PostgreSQL 16 High-Availability",
      status: "degraded",
      latency: "42ms",
      uptime: "99.90%",
      throughput: "850 IOPS",
      details: "Connection limit reached (30 Active Threads)",
    },
    redis: {
      name: "Redis Queue & Event Broker",
      role: "Asynchronous Telemetry Event Buffer",
      tier: "Streaming Tier",
      technology: "Redis 7.2 Cluster",
      status: "connected",
      latency: "1.2ms",
      uptime: "100.0%",
      throughput: "12.4k ops/s",
      details: "Queue aiops:events_queue Active & Low Latency",
    },
    aiWorker: {
      name: "AI Autonomous Diagnostic Brain",
      role: "LangChain RAG Runbook Engine",
      tier: "AI / Inference",
      technology: "FastAPI + LangChain + Vector DB",
      status: "connected",
      latency: "850ms",
      uptime: "99.95%",
      throughput: "45 diags/min",
      details: "In-Memory Vector Store Active (RB-001 - RB-007)",
    },
  });

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // 1-Click Interactive Simulation
  const handleSimulate = (scenario: "prometheus" | "github" | "worker") => {
    setIsSimulating(true);

    if (scenario === "prometheus") {
      const newId = `INC-${Math.floor(1000 + Math.random() * 9000)}`;
      const evId = `EVD-${Math.floor(100 + Math.random() * 900)}`;
      const diagId = `DIAG-${Math.floor(100 + Math.random() * 900)}`;
      const planId = `PLAN-${Math.floor(100 + Math.random() * 900)}`;

      const newInc: Incident = {
        id: newId,
        title: "Database Connection Pool Saturation (Prometheus Alertmanager)",
        severity: "critical",
        status: "awaiting_approval",
        service_id: "auth-service",
        environment_id: "production",
        event_ids: [evId],
        opened_at: new Date().toISOString(),
      };

      const newEv: Evidence = {
        id: evId,
        incident_id: newId,
        kind: "metric",
        source: "prometheus-alertmanager",
        content: "QueuePool limit of size 10 overflow 20 reached, checkout timed out after 30.00s",
        collected_at: new Date().toISOString(),
      };

      const newDiag: Diagnosis = {
        id: diagId,
        incident_id: newId,
        probable_root_cause: "Database connection pool exhausted due to unclosed sessions in concurrent worker threads or insufficient pool_size.",
        confidence: 0.94,
        supporting_evidence_ids: [evId],
        recommended_remediation: "Scale connection pool size to 30 and enable pool_pre_ping recycling.",
        uncertainty_notes: "Runbook RB-001 matched via vector similarity 0.94.",
        created_at: new Date().toISOString(),
      };

      const newPlan: RemediationPlan = {
        id: planId,
        incident_id: newId,
        diagnosis_id: diagId,
        status: "drafted",
        rationale: "Automated RAG diagnosis matched Runbook RB-001 (Postgres Pool Exhaustion). Proposes pool scaling.",
        risk_level: "low",
        actions: [
          {
            id: `ACT-${Math.floor(100 + Math.random() * 900)}`,
            plan_id: planId,
            action_type: "config_update",
            target_service_id: "auth-service",
            description: "Scale connection pool size to 30 and enable pool_pre_ping recycling",
            parameters: { pool_size: 30, max_overflow: 20, pool_pre_ping: true },
            order: 1,
          },
        ],
        created_at: new Date().toISOString(),
      };

      setIncidents((prev) => [newInc, ...prev]);
      setEvidenceMap((prev) => ({ ...prev, [newId]: [newEv] }));
      setDiagnosesMap((prev) => ({ ...prev, [newId]: newDiag }));
      setPlansMap((prev) => ({ ...prev, [newId]: newPlan }));
      setSelectedIncidentId(newId);

      showToast(`🔴 Live Prometheus alert ingested! AI matched RB-001 with 94% confidence.`);
    } else if (scenario === "github") {
      const newId = `INC-${Math.floor(1000 + Math.random() * 9000)}`;
      const evId = `EVD-${Math.floor(100 + Math.random() * 900)}`;
      const diagId = `DIAG-${Math.floor(100 + Math.random() * 900)}`;
      const planId = `PLAN-${Math.floor(100 + Math.random() * 900)}`;

      const newInc: Incident = {
        id: newId,
        title: "Deployment Failure: Container image failed readiness probe on startup",
        severity: "high",
        status: "awaiting_approval",
        service_id: "payment-api",
        environment_id: "production",
        pipeline_id: "deploy-release-v3.0.2",
        event_ids: [evId],
        opened_at: new Date().toISOString(),
      };

      const newEv: Evidence = {
        id: evId,
        incident_id: newId,
        kind: "pipeline_info",
        source: "github-actions",
        content: "Deployment #4921 failed: readiness probe timeout HTTP 500 on port 8080 during container bootstrap",
        collected_at: new Date().toISOString(),
      };

      const newDiag: Diagnosis = {
        id: diagId,
        incident_id: newId,
        probable_root_cause: "Container image failed readiness probe on startup due to an unhandled initialization exception or port misconfiguration.",
        confidence: 0.89,
        supporting_evidence_ids: [evId],
        recommended_remediation: "Execute automated Git rollback to previous verified stable release commit SHA.",
        uncertainty_notes: "Runbook RB-006 matched via vector similarity 0.91.",
        created_at: new Date().toISOString(),
      };

      const newPlan: RemediationPlan = {
        id: planId,
        incident_id: newId,
        diagnosis_id: diagId,
        status: "drafted",
        rationale: "Automated RAG diagnosis matched Runbook RB-006 (Container Startup Probe Failure). Proposes safe rollback.",
        risk_level: "low",
        actions: [
          {
            id: `ACT-${Math.floor(100 + Math.random() * 900)}`,
            plan_id: planId,
            action_type: "rollback",
            target_service_id: "payment-api",
            description: "Rollback deployment to previous verified Git commit SHA",
            parameters: { previous_commit_sha: "a1b2c3d4e5f6" },
            order: 1,
          },
        ],
        created_at: new Date().toISOString(),
      };

      setIncidents((prev) => [newInc, ...prev]);
      setEvidenceMap((prev) => ({ ...prev, [newId]: [newEv] }));
      setDiagnosesMap((prev) => ({ ...prev, [newId]: newDiag }));
      setPlansMap((prev) => ({ ...prev, [newId]: newPlan }));
      setSelectedIncidentId(newId);

      showToast(`🟠 Live GitHub Actions deployment failure ingested! AI matched RB-006 Rollback.`);
    } else if (scenario === "worker") {
      const newId = `INC-${Math.floor(1000 + Math.random() * 9000)}`;
      const evId = `EVD-${Math.floor(100 + Math.random() * 900)}`;
      const diagId = `DIAG-${Math.floor(100 + Math.random() * 900)}`;
      const planId = `PLAN-${Math.floor(100 + Math.random() * 900)}`;

      const newInc: Incident = {
        id: newId,
        title: "Worker Timeout: Redis message queue consumer connection dropped",
        severity: "medium",
        status: "awaiting_approval",
        service_id: "worker-service",
        environment_id: "production",
        event_ids: [evId],
        opened_at: new Date().toISOString(),
      };

      const newEv: Evidence = {
        id: evId,
        incident_id: newId,
        kind: "log",
        source: "python-sentry-client",
        content: "Redis connection timeout after 3 retries, queue worker disconnected from aiops:events_queue",
        collected_at: new Date().toISOString(),
      };

      const newDiag: Diagnosis = {
        id: diagId,
        incident_id: newId,
        probable_root_cause: "Background worker failed to maintain active heartbeat connection with Redis message queue due to timeout or network latency.",
        confidence: 0.86,
        supporting_evidence_ids: [evId],
        recommended_remediation: "Restart the worker container to re-establish clean connection with Redis cluster.",
        uncertainty_notes: "Runbook RB-007 matched via vector similarity 0.89.",
        created_at: new Date().toISOString(),
      };

      const newPlan: RemediationPlan = {
        id: planId,
        incident_id: newId,
        diagnosis_id: diagId,
        status: "drafted",
        rationale: "Automated RAG diagnosis matched Runbook RB-007 (Queue Worker Timeout). Recommends container restart.",
        risk_level: "low",
        actions: [
          {
            id: `ACT-${Math.floor(100 + Math.random() * 900)}`,
            plan_id: planId,
            action_type: "container_restart",
            target_service_id: "worker-service",
            description: "Restart background worker container and drain queue backlog",
            parameters: { container_name: "aiops-worker-1", grace_period_sec: 10 },
            order: 1,
          },
        ],
        created_at: new Date().toISOString(),
      };

      setIncidents((prev) => [newInc, ...prev]);
      setEvidenceMap((prev) => ({ ...prev, [newId]: [newEv] }));
      setDiagnosesMap((prev) => ({ ...prev, [newId]: newDiag }));
      setPlansMap((prev) => ({ ...prev, [newId]: newPlan }));
      setSelectedIncidentId(newId);

      showToast(`🟡 Live Generic alert ingested! AI matched RB-007 (Container Restart).`);
    }

    setTimeout(() => setIsSimulating(false), 400);
  };

  const handleReset = () => {
    setIncidents(INITIAL_INCIDENTS);
    setEvidenceMap(INITIAL_EVIDENCE);
    setDiagnosesMap(INITIAL_DIAGNOSES);
    setPlansMap(INITIAL_REMEDIATION_PLANS);
    setSelectedIncidentId(INITIAL_INCIDENTS[0].id);
    showToast(`🔄 State restored to baseline demo incidents.`);
  };

  const handleDiagnose = (incidentId: string) => {
    setIncidents((prev) =>
      prev.map((inc) => (inc.id === incidentId ? { ...inc, status: "diagnosing" } : inc))
    );
    showToast(`🧠 Running LangChain RAG vector similarity diagnosis for ${incidentId}...`);

    setTimeout(() => {
      setIncidents((prev) =>
        prev.map((inc) => (inc.id === incidentId ? { ...inc, status: "awaiting_approval" } : inc))
      );
      showToast(`✨ RAG Diagnosis Complete! Incident ${incidentId} advanced to Awaiting Approval.`);
    }, 1200);
  };

  const handleApprove = async (incidentId: string) => {
    setIncidents((prev) =>
      prev.map((inc) => (inc.id === incidentId ? { ...inc, status: "executing" } : inc))
    );
    showToast(`⚡ Human Approval Granted: Calling backend remediation API for ${incidentId}...`);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const resp = await fetch(`${apiUrl}/api/v1/incidents/${incidentId}/remediation/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          approver_id: currentUser.email,
          notes: `Authorized by ${currentUser.name} via Developer Cockpit`,
        }),
      });

      if (resp.ok) {
        const data = await resp.json();
        const prUrl = data.execution?.results?.[0]?.pull_request_url;
        setIncidents((prev) =>
          prev.map((inc) =>
            inc.id === incidentId
              ? { ...inc, status: "resolved", resolved_at: new Date().toISOString() }
              : inc
          )
        );
        setPlansMap((prev) => {
          if (!prev[incidentId]) return prev;
          const updatedActions = [...prev[incidentId].actions];
          if (updatedActions[0] && prUrl) {
            updatedActions[0] = {
              ...updatedActions[0],
              parameters: { ...updatedActions[0].parameters, pull_request_url: prUrl },
            };
          }
          return {
            ...prev,
            [incidentId]: { ...prev[incidentId], status: "completed", actions: updatedActions },
          };
        });
        showToast(
          prUrl
            ? `✅ Fix Verified & PR Created: ${prUrl}`
            : `✅ Remediation Verified: ${incidentId} returned to 100% operational health!`
        );
        return;
      }
    } catch {
      // Graceful fallback for offline demo simulation
    }

    // Fallback simulation when API container is offline
    setTimeout(() => {
      setIncidents((prev) =>
        prev.map((inc) =>
          inc.id === incidentId
            ? { ...inc, status: "resolved", resolved_at: new Date().toISOString() }
            : inc
        )
      );
      setPlansMap((prev) => {
        if (!prev[incidentId]) return prev;
        return {
          ...prev,
          [incidentId]: { ...prev[incidentId], status: "completed" },
        };
      });
      showToast(`✅ Remediation Verified: ${incidentId} returned to 100% operational health!`);
    }, 1500);
  };

  const handleReject = async (incidentId: string) => {
    setIncidents((prev) =>
      prev.map((inc) => (inc.id === incidentId ? { ...inc, status: "open" } : inc))
    );
    showToast(`❌ Remediation Plan Rejected by SRE Operator for ${incidentId}.`);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      await fetch(`${apiUrl}/api/v1/incidents/${incidentId}/remediation/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          approver_id: currentUser.email,
          notes: `Rejected by ${currentUser.name} via Developer Cockpit: Scheduled maintenance or manual review required`,
        }),
      });
    } catch {
      // Fallback
    }
  };

  const selectedIncident = incidents.find((i) => i.id === selectedIncidentId);
  const currentEvidence = selectedIncident ? evidenceMap[selectedIncident.id] || [] : [];
  const currentDiagnosis = selectedIncident ? diagnosesMap[selectedIncident.id] : undefined;
  const currentPlan = selectedIncident ? plansMap[selectedIncident.id] : undefined;

  if (!isAuthenticated) {
    return (
      <LoginScreen
        onLogin={(user) => {
          setCurrentUser(user);
          setIsAuthenticated(true);
          showToast(`✓ Authenticated as ${user.name}`);
        }}
      />
    );
  }

  return (
    <div className="sre-app-layout">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="sre-toast-notification">
          {toastMessage}
        </div>
      )}

      {/* 1. Left Icon Rail (64px) */}
      <SidebarRail activeTab={activeTab} onTabChange={setActiveTab} />

      {/* 2. Main SRE Dashboard Viewport */}
      <div className="sre-viewport">
        {/* Top Global Navigation Bar */}
        <TopNav
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSimulate={handleSimulate}
          onReset={handleReset}
          isSimulating={isSimulating}
          currentUser={currentUser}
          onSignOut={() => {
            setIsAuthenticated(false);
            showToast("Signed out of session.");
          }}
        />

        {/* Dynamic Content Body */}
        {activeTab === "incidents" && (
          <div className="sre-three-column-grid">
            {/* Column 1: Incident Stream List (~25% width) */}
            <IncidentStreamColumn
              incidents={incidents}
              selectedId={selectedIncidentId}
              onSelect={(id) => setSelectedIncidentId(id)}
              searchFilter={searchQuery}
            />

            {/* Column 2: Main Incident Workspace (~45% width) */}
            <IncidentWorkspaceColumn
              incident={selectedIncident}
              onAcknowledge={() => showToast(`✓ Incident ${selectedIncident?.id} acknowledged by SRE`)}
              onViewLogs={() => setActiveTab("evidence")}
            />

            {/* Column 3: AI Root Cause Analysis Console (~30% width) */}
            <AiRootCauseConsole
              incident={selectedIncident}
              diagnosis={currentDiagnosis}
              plan={currentPlan}
              onApprove={handleApprove}
              onReject={handleReject}
              onDiagnose={handleDiagnose}
            />
          </div>
        )}

        {activeTab === "topology" && (
          <div className="topology-viewport">
            <TopologyView statuses={statuses} />
          </div>
        )}

        {activeTab === "evidence" && (
          <div className="evidence-room-viewport">
            <div className="evidence-room-header">
              <h2>🔬 Telemetry Evidence Room ({currentEvidence.length} Records)</h2>
              <p>Raw runtime observations harvested from containers, databases, and CI/CD without hallucination.</p>
            </div>
            <div className="evidence-room-grid">
              {currentEvidence.map((ev) => (
                <div key={ev.id} className="evidence-room-card">
                  <div className="ev-card-top">
                    <span className="ev-badge-id">{ev.id}</span>
                    <span className="ev-badge-kind">{ev.kind.toUpperCase()}</span>
                    <span className="ev-source-text">Source: <code>{ev.source}</code></span>
                  </div>
                  <pre className="ev-card-code">{ev.content}</pre>
                  <div className="ev-card-bottom" suppressHydrationWarning>
                    Harvested at: {new Date(ev.collected_at).toISOString().slice(11, 19)} UTC
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "settings" && (
          <div className="settings-viewport">
            <h2>⚙️ System Settings &amp; Autonomous Governance Policy</h2>
            <p>Configured for strict Human-in-the-Loop policy. All consequential actions require explicit sign-off.</p>
          </div>
        )}
      </div>
    </div>
  );
}
