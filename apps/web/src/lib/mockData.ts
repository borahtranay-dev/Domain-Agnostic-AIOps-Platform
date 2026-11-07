import { Incident, Evidence, Diagnosis, RemediationPlan } from "../types";

export const INITIAL_INCIDENTS: Incident[] = [
  {
    id: "INC-8921",
    title: "Critical Service Outage: Database Connection Pool Exhausted",
    severity: "critical",
    status: "awaiting_approval",
    service_id: "payment-api",
    environment_id: "production",
    pipeline_id: "pipe-release-v2.1",
    event_ids: ["EVT-101", "EVT-102"],
    opened_at: "2026-11-02T10:15:00.000Z",
  },
  {
    id: "INC-8922",
    title: "High Severity: Background Task Worker OOMKilled (Exit Code 137)",
    severity: "high",
    status: "diagnosing",
    service_id: "worker-queue",
    environment_id: "staging",
    pipeline_id: "pipe-nightly-build",
    event_ids: ["EVT-201"],
    opened_at: "2026-11-02T09:45:00.000Z",
  },
  {
    id: "INC-8923",
    title: "Configuration Drift: Missing Runtime Environment Variable REDIS_URL",
    severity: "medium",
    status: "resolved",
    service_id: "api-gateway",
    environment_id: "production",
    event_ids: ["EVT-301"],
    opened_at: "2026-11-02T08:30:00.000Z",
    resolved_at: "2026-11-02T08:45:00.000Z",
  },
];

export const INITIAL_EVIDENCE: Record<string, Evidence[]> = {
  "INC-8921": [
    {
      id: "EVD-101",
      incident_id: "INC-8921",
      kind: "stack_trace",
      source: "fastapi-service.log",
      content: `sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 20 reached, connection timed out, timeout 30.00 (Background worker pool exhausted at 2026-10-17T09:45:00Z)`,
      collected_at: "2026-11-02T10:16:00.000Z",
    },
    {
      id: "EVD-102",
      incident_id: "INC-8921",
      kind: "metric",
      source: "prometheus-telemetry",
      content: `database_active_connections{db="postgres_aiops"} = 30.0 (Saturation: 100%, Waiting threads: 14)`,
      collected_at: "2026-11-02T10:17:00.000Z",
    },
  ],
  "INC-8922": [
    {
      id: "EVD-201",
      incident_id: "INC-8922",
      kind: "log",
      source: "docker-daemon",
      content: `Container worker-queue-1 exceeded memory reservation 512MiB. Process terminated by kernel with SIGKILL (Exit code 137 OOMKilled).`,
      collected_at: "2026-11-02T09:46:00.000Z",
    },
  ],
  "INC-8923": [
    {
      id: "EVD-301",
      incident_id: "INC-8923",
      kind: "configuration",
      source: "k8s-pod-manifest",
      content: `KeyError: 'REDIS_URL' required by settings.py but missing from deployment environment map.`,
      collected_at: "2026-11-02T08:31:00.000Z",
    },
  ],
};

export const INITIAL_DIAGNOSES: Record<string, Diagnosis> = {
  "INC-8921": {
    id: "DIAG-101",
    incident_id: "INC-8921",
    probable_root_cause: "PostgreSQL connection pool exhausted due to unclosed sessions in concurrent worker threads under high webhook volume. Saturated at 30 connections.",
    confidence: 0.94,
    supporting_evidence_ids: ["EVD-101", "EVD-102"],
    contradicting_evidence_ids: [],
  },
  "INC-8922": {
    id: "DIAG-201",
    incident_id: "INC-8922",
    probable_root_cause: "Process memory consumption surpassed container cgroup limits (512MiB) due to uncollected memory in heavy batch processing.",
    confidence: 0.91,
    supporting_evidence_ids: ["EVD-201"],
    contradicting_evidence_ids: [],
  },
  "INC-8923": {
    id: "DIAG-301",
    incident_id: "INC-8923",
    probable_root_cause: "Container failed to boot because REDIS_URL was missing from environment secrets manifest.",
    confidence: 0.98,
    supporting_evidence_ids: ["EVD-301"],
    contradicting_evidence_ids: [],
  },
};

export const INITIAL_REMEDIATION_PLANS: Record<string, RemediationPlan> = {
  "INC-8921": {
    id: "PLAN-101",
    incident_id: "INC-8921",
    diagnosis_id: "DIAG-101",
    status: "drafted",
    rationale: "Grounded on Runbook RB-001 (PostgreSQL Connection Pool Exhaustion) with 94% confidence. Scaled pool size and enabled auto-ping recycling.",
    created_at: "2026-11-02T10:18:00.000Z",
    actions: [
      {
        id: "ACT-101",
        plan_id: "PLAN-101",
        action_type: "config_update",
        description: "Scale connection pool to pool_size=20, max_overflow=30, and enable pool_pre_ping=true",
        target_service_id: "payment-api",
        parameters: { pool_size: 20, max_overflow: 30, pool_pre_ping: true },
        order: 1,
      },
    ],
  },
  "INC-8922": {
    id: "PLAN-201",
    incident_id: "INC-8922",
    diagnosis_id: "DIAG-201",
    status: "drafted",
    rationale: "Grounded on Runbook RB-002 (Container OOMKilled). Initiating graceful container restart with 15s grace period.",
    created_at: "2026-11-02T09:47:00.000Z",
    actions: [
      {
        id: "ACT-201",
        plan_id: "PLAN-201",
        action_type: "container_restart",
        description: "Gracefully restart worker container and recycle orphaned worker processes",
        target_service_id: "worker-queue",
        parameters: { service: "worker-queue", grace_period_seconds: 15 },
        order: 1,
      },
    ],
  },
};
