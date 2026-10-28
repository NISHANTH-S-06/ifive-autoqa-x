# Version 9.0 REST API Reference
## Universal Autonomous Software & Digital Ecosystem Platform

**Base URL:** `/api/v9`  
**Version:** 9.0  
**Phase:** 27  
**Router:** `app/v9/api/v9_router.py`

---

## Platform Endpoints

### GET /api/v9/platform/status

Returns platform operational status.

**Response:**

```json
{
  "status": "ok",
  "system": "iFive AutoQA X Universal Autonomous Software & Digital Ecosystem Platform",
  "version": "9.0",
  "phase": "27",
  "maturity": "UNIVERSAL_AUTONOMOUS"
}
```

### GET /api/v9/platform/health

Alias for `/api/v9/platform/status`.

### GET /api/v9/health

Health check alias.

---

## Software Intelligence Endpoints

### GET /api/v9/software/capabilities

Returns list of supported languages and frameworks.

**Response:**

```json
{
  "supported_languages": ["Python", "Java", "C#", "Go", "Rust", "Node.js", "TypeScript", "JavaScript"],
  "supported_frameworks": ["FastAPI", "Django", "Flask", "Spring Boot", ".NET", "..."],
  "analysis_modes": ["Static Analysis", "Dependency Graph", "Architecture Classification", "..."]
}
```

### POST /api/v9/software/analyse

Analyses a repository and returns a full intelligence profile.

**Request Body:**

```json
{
  "repo_name": "enterprise-erp",
  "source_sample": "from fastapi import FastAPI",
  "manifest": "fastapi==0.100\npydantic==2.0"
}
```

**Response:**

```json
{
  "status": "success",
  "profile": {
    "repo_id": "repo-abc123",
    "name": "enterprise-erp",
    "primary_language": "Python",
    "detected_frameworks": ["FastAPI"],
    "quality_score": 98.5,
    "maintainability_index": 97.2
  }
}
```

### POST /api/v9/software/generate

Generates a full application scaffold from a specification.

**Request Body:**

```json
{
  "name": "OrderService",
  "language": "Python",
  "framework": "FastAPI",
  "api_style": "REST",
  "entities": ["Order", "Customer"]
}
```

**Response:**

```json
{
  "status": "success",
  "artifact": {
    "artifact_id": "art-xyz789",
    "files_generated": ["main.py", "models/order.py", "..."],
    "lines_of_code": 2250,
    "test_cases_generated": 12,
    "quality_score": 99.2,
    "generation_status": "SUCCESS"
  }
}
```

### GET /api/v9/software/generation/styles

Returns supported API generation styles.

**Response:**

```json
{"supported_styles": ["REST", "GraphQL", "gRPC", "Event-Driven", "Serverless"]}
```

---

## Runtime Endpoints

### GET /api/v9/runtime

Returns runtime platform summary.

**Response:**

```json
{
  "registered_environments": 4,
  "supported_targets": ["Local", "Docker", "Kubernetes", "Serverless", "Multi-Cloud", "Edge"],
  "active_workloads": 10,
  "global_uptime_pct": 99.9999,
  "zero_rpo_dr": true
}
```

### POST /api/v9/runtime/deploy

Deploys a workload to the target runtime environment.

**Request Body:**

```json
{
  "name": "PaymentService",
  "replicas": 5,
  "runtime_target": "Kubernetes"
}
```

**Response:**

```json
{
  "status": "success",
  "deployment": {
    "workload_id": "wl-abc123",
    "status": "RUNNING",
    "scheduled_on": "kubernetes-node-9a1b",
    "latency_ms": 12.5,
    "throughput_rps": 15000.0
  }
}
```

---

## Integration Endpoints

### GET /api/v9/integrations

Returns integration platform summary.

### POST /api/v9/integrations/sync

Synchronises data between enterprise systems.

**Request Body:**

```json
{
  "source": "SAP",
  "target": "Salesforce",
  "record_count": 5000
}
```

---

## Ecosystem Endpoints

### GET /api/v9/ecosystem

Returns digital ecosystem summary.

### GET /api/v9/ecosystem/services

Discovers services in the ecosystem. Accepts optional `query` parameter.

---

## Knowledge Endpoints

### GET /api/v9/knowledge

Returns Knowledge Universe summary.

### POST /api/v9/knowledge/query

Queries the knowledge graph.

**Request Body:**

```json
{"subject": "FastAPI"}
```

**Response:**

```json
{
  "status": "success",
  "triples": [{"subject": "FastAPI", "predicate": "IS_FRAMEWORK_FOR", "obj": "Python", "confidence": 0.98}],
  "reasoning": {"inferred_conclusions": [...], "reasoning_confidence": 0.96}
}
```

---

## Decision Endpoints

### GET /api/v9/decision

Returns AI Decision Platform summary.

### POST /api/v9/decision/decide

Makes an AI-driven decision.

**Request Body:**

```json
{
  "domain": "TECHNICAL",
  "objective": "Optimise API response time"
}
```

### GET /api/v9/decision/strategy

Returns a strategic plan for an objective. Accepts `objective` query parameter.

---

## Execution Endpoints

### GET /api/v9/execution

Returns Execution Fabric summary.

### POST /api/v9/execution/submit

Submits a task for distributed execution.

**Request Body:**

```json
{
  "name": "DataProcessingTask",
  "priority": 8
}
```

---

## Observability Endpoints

### GET /api/v9/observability

Returns the full observability dashboard.

### GET /api/v9/observability/metrics

Returns aggregated enterprise metrics.

### GET /api/v9/observability/traces

Returns distributed trace summary.

---

## Global Dashboard

### GET /api/v9/dashboard

Returns the unified global dashboard combining all platform domains.

**Response:**

```json
{
  "platform": "iFive AutoQA X v9.0 Universal Autonomous Software & Digital Ecosystem",
  "software_intelligence": {...},
  "runtime": {...},
  "integrations": {...},
  "ecosystem": {...},
  "knowledge": {...},
  "decision": {...},
  "execution": {...},
  "observability": {...},
  "overall_health": "GREEN",
  "ai_maturity_score": 99.7,
  "platform_maturity_level": "UNIVERSAL_AUTONOMOUS"
}
```

---

## Endpoint Summary

| Method | Endpoint | Domain |
| -------- | ---------- | -------- |
| GET | /api/v9/platform/status | Platform |
| GET | /api/v9/platform/health | Platform |
| GET | /api/v9/health | Platform |
| GET | /api/v9/dashboard | Platform |
| GET | /api/v9/software/capabilities | Software |
| POST | /api/v9/software/analyse | Software |
| POST | /api/v9/software/generate | Software / CodeGen |
| GET | /api/v9/software/generation/styles | CodeGen |
| GET | /api/v9/runtime | Runtime |
| POST | /api/v9/runtime/deploy | Runtime |
| GET | /api/v9/integrations | Integrations |
| POST | /api/v9/integrations/sync | Integrations |
| GET | /api/v9/ecosystem | Ecosystem |
| GET | /api/v9/ecosystem/services | Ecosystem |
| GET | /api/v9/knowledge | Knowledge |
| POST | /api/v9/knowledge/query | Knowledge |
| GET | /api/v9/decision | Decision |
| POST | /api/v9/decision/decide | Decision |
| GET | /api/v9/decision/strategy | Decision |
| GET | /api/v9/execution | Execution |
| POST | /api/v9/execution/submit | Execution |
| GET | /api/v9/observability | Observability |
| GET | /api/v9/observability/metrics | Observability |
| GET | /api/v9/observability/traces | Observability |

### Total Endpoints: 24

---

*Generated: 2026-08-04 | iFive AutoQA X Phase 27 — Version 9.0*
