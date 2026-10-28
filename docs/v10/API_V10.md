# Version 10.0 REST API Reference
## Artificial General Enterprise Intelligence (AGEI)

**Base URL:** `/api/v10`  
**Version:** 10.0  
**Phase:** 28  
**Router:** `app/v10/api/v10_router.py`

---

## Platform Endpoints

### GET /api/v10/platform/status

Returns AGEI platform status.

**Response:**

```json
{
  "status": "ok",
  "system": "iFive AutoQA X — Artificial General Enterprise Intelligence (AGEI)",
  "version": "10.0",
  "phase": "28",
  "maturity": "ARTIFICIAL_GENERAL_ENTERPRISE_INTELLIGENCE",
  "codename": "UNIVERSAL_MIND"
}
```

### GET /api/v10/platform/health

Alias for `/api/v10/platform/status`.

### GET /api/v10/health

Health check alias.

### GET /api/v10/dashboard

Returns the unified AGEI global dashboard.

---

## AGEI Core Endpoints

### GET /api/v10/agei

Returns full AGEI platform summary.

### POST /api/v10/agei/think

Executes one AGEI cognitive cycle (recall → reason → store).

**Request:**

```json
{
  "prompt": "How to reduce global API latency below 10ms?",
  "reasoning_mode": "Causal",
  "store_result": true
}
```

### GET /api/v10/agei/profile

Returns the current AGEI Intelligence Profile.

---

## Memory Endpoints

### GET /api/v10/memory

Returns memory store statistics.

### POST /api/v10/memory/store

Stores a knowledge record.

**Request:**

```json
{
  "domain": "ENGINEERING",
  "context": "latency_targets",
  "content": "P99 global latency target is 10ms",
  "importance": 0.95,
  "tags": ["latency", "slo"]
}
```

### POST /api/v10/memory/recall

Recalls knowledge records by domain or tags.

**Request:**

```json
{"domain": "ENGINEERING", "tags": ["latency"], "top_k": 10}
```

### POST /api/v10/memory/consolidate

Consolidates the memory store and returns domain statistics.

---

## Goal Endpoints

### GET /api/v10/goals

Lists all enterprise goals. Accepts optional `state` and `domain` query params.

### GET /api/v10/goals/summary

Returns goal distribution and progress summary.

### POST /api/v10/goals/create

Creates a new enterprise goal.

**Request:**

```json
{"title": "Achieve AGEI Core Stability", "domain": "ENGINEERING", "priority": 10, "target_kpi": "99.9999% uptime"}
```

### POST /api/v10/goals/progress

Updates goal progress percentage.

**Request:**

```json
{"goal_id": "goal-abc123", "progress_pct": 75.0}
```

---

## Reasoning Endpoints

### GET /api/v10/reasoning/capabilities

Returns supported reasoning modes and configuration.

### POST /api/v10/reasoning/reason

Executes single-mode reasoning.

**Request:**

```json
{"premise": "Memory utilisation >78% causes latency spikes", "mode": "Causal"}
```

### POST /api/v10/reasoning/multi

Executes multi-mode reasoning consensus.

**Request:**

```json
{"premise": "Global throughput optimisation", "modes": ["Deductive", "Causal", "Probabilistic"]}
```

---

## Strategic Intelligence Endpoints

### GET /api/v10/strategic

Returns strategic intelligence hub summary.

### POST /api/v10/strategic/plan

Creates a strategic plan.

**Request:**

```json
{"objective": "Global AI market leadership", "horizon_months": 12, "domain": "PLATFORM"}
```

### GET /api/v10/strategic/roadmap

Returns quarterly roadmap. Accepts `horizon_months` query param.

### POST /api/v10/strategic/decide

Makes a long-term decision.

**Request:**

```json
{"context": "Adopt federated AI architecture", "horizon_months": 24, "domain": "STRATEGIC"}
```

### POST /api/v10/strategic/scenarios

Returns scenario comparison (Conservative / Balanced / Aggressive).

### POST /api/v10/strategic/synthesise

Synthesises multi-domain intelligence.

**Request:**

```json
{"premise": "Improve engineering velocity", "domains": ["ENGINEERING", "AI", "BUSINESS"]}
```

### GET /api/v10/strategic/domain-health

Returns health status for all monitored domains.

---

## Learning Endpoints

### GET /api/v10/learning

Returns enterprise learning summary.

### POST /api/v10/learning/cycle

Runs one continuous learning cycle.

**Request:**

```json
{"domain": "AI", "data_points": 50000}
```

### POST /api/v10/learning/full-cycle

Runs a complete integrated learning cycle: learn → evolve → discover.

### POST /api/v10/learning/evolve

Evolves the knowledge graph.

**Request:**

```json
{"trigger": "NEW_DOMAIN_DATA", "evolution_type": "INCREMENTAL", "new_triples": 500}
```

### POST /api/v10/learning/discover

Discovers patterns in the enterprise data.

**Request:**

```json
{"domain": "ENGINEERING", "min_significance": 0.99, "top_k": 10}
```

### GET /api/v10/learning/patterns

Returns pattern library statistics.

---

## Coordination Endpoints

### GET /api/v10/coordination

Returns autonomous coordination hub summary.

### GET /api/v10/coordination/modules

Lists all registered AI modules. Accepts optional `health` filter.

### GET /api/v10/coordination/report

Returns full coordination report.

### POST /api/v10/coordination/delegate

Delegates a task to the best-matching module.

**Request:**

```json
{"name": "AnalyseCodeQuality", "required_capability": "code_analysis", "priority": 8}
```

### POST /api/v10/coordination/delegate-batch

Delegates multiple tasks in one call.

### POST /api/v10/coordination/optimise

Applies a specific optimisation action.

**Request:**

```json
{"target": "execution_fabric"}
```

### POST /api/v10/coordination/auto-optimise

Applies all 5 optimisation rules automatically.

### POST /api/v10/coordination/full-cycle

Executes one full coordination cycle (coordinate → optimise).

---

## Complete Endpoint Index

| Method | Endpoint | Domain |
| -------- | ---------- | -------- |
| GET | /api/v10/platform/status | Platform |
| GET | /api/v10/platform/health | Platform |
| GET | /api/v10/health | Platform |
| GET | /api/v10/dashboard | Platform |
| GET | /api/v10/agei | AGEI Core |
| POST | /api/v10/agei/think | AGEI Core |
| GET | /api/v10/agei/profile | AGEI Core |
| GET | /api/v10/memory | Memory |
| POST | /api/v10/memory/store | Memory |
| POST | /api/v10/memory/recall | Memory |
| POST | /api/v10/memory/consolidate | Memory |
| GET | /api/v10/goals | Goals |
| GET | /api/v10/goals/summary | Goals |
| POST | /api/v10/goals/create | Goals |
| POST | /api/v10/goals/progress | Goals |
| GET | /api/v10/reasoning/capabilities | Reasoning |
| POST | /api/v10/reasoning/reason | Reasoning |
| POST | /api/v10/reasoning/multi | Reasoning |
| GET | /api/v10/strategic | Strategic |
| POST | /api/v10/strategic/plan | Strategic |
| GET | /api/v10/strategic/roadmap | Strategic |
| POST | /api/v10/strategic/decide | Strategic |
| POST | /api/v10/strategic/scenarios | Strategic |
| POST | /api/v10/strategic/synthesise | Strategic |
| GET | /api/v10/strategic/domain-health | Strategic |
| GET | /api/v10/learning | Learning |
| POST | /api/v10/learning/cycle | Learning |
| POST | /api/v10/learning/full-cycle | Learning |
| POST | /api/v10/learning/evolve | Learning |
| POST | /api/v10/learning/discover | Learning |
| GET | /api/v10/learning/patterns | Learning |
| GET | /api/v10/coordination | Coordination |
| GET | /api/v10/coordination/modules | Coordination |
| GET | /api/v10/coordination/report | Coordination |
| POST | /api/v10/coordination/delegate | Coordination |
| POST | /api/v10/coordination/delegate-batch | Coordination |
| POST | /api/v10/coordination/optimise | Coordination |
| POST | /api/v10/coordination/auto-optimise | Coordination |
| POST | /api/v10/coordination/full-cycle | Coordination |

### Total Endpoints: 39

---

*Generated: 2026-08-04 | iFive AutoQA X Phase 28 — Version 10.0*
