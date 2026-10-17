/**
 * Frontend Type Definitions matching Phase P2 Shared Contracts.
 * 
 * Owner: Vivek (Frontend Lead)
 * Phase: P3 (Component Construction - Developer Cockpit)
 */

export type Severity = "low" | "medium" | "high" | "critical";

export type IncidentStatus = 
  | "open"
  | "diagnosing"
  | "awaiting_approval"
  | "executing"
  | "verifying"
  | "resolved"
  | "closed";

export type EvidenceKind = 
  | "log"
  | "stack_trace"
  | "commit"
  | "pipeline_info"
  | "configuration"
  | "metric"
  | "documentation"
  | "knowledge_base";

export type ActionType = 
  | "pull_request"
  | "rollback"
  | "container_restart"
  | "config_update"
  | "scale_service";

export type PlanStatus = 
  | "drafted"
  | "approved"
  | "rejected"
  | "executing"
  | "completed"
  | "failed";

export interface Incident {
  id: string;
  title: string;
  status: IncidentStatus;
  severity: Severity;
  service_id?: string;
  environment_id?: string;
  pipeline_id?: string;
  event_ids: string[];
  opened_at: string;
  resolved_at?: string;
}

export interface Evidence {
  id: string;
  incident_id: string;
  kind: EvidenceKind;
  source: string;
  content: string;
  reference?: string;
  collected_at: string;
}

export interface Diagnosis {
  id: string;
  incident_id: string;
  probable_root_cause: string;
  confidence: number;
  supporting_evidence_ids: string[];
  contradicting_evidence_ids: string[];
}

export interface RemediationAction {
  id: string;
  plan_id: string;
  action_type: ActionType;
  description: string;
  target_service_id?: string;
  parameters: Record<string, any>;
  order: number;
}

export interface RemediationPlan {
  id: string;
  incident_id: string;
  diagnosis_id: string;
  status: PlanStatus;
  rationale: string;
  actions: RemediationAction[];
  created_at: string;
}

export interface ServiceTopologyStatus {
  name: string;
  subsystem: string;
  owner: string;
  technology: string;
  status: "connected" | "checking" | "error";
  details: string;
}
