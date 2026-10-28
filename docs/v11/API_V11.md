# Version 11.0 REST API Reference
## Autonomous Enterprise Intelligence Network

**Base URL:** `/api/v11`  
**Version:** 11.0  
**Phase:** 29  
**Router:** `app/v11/api/v11_router.py`

---

## Endpoint Summary

### Platform & Health

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/api/v11/platform/status` | Returns v11 platform status |
| GET | `/api/v11/platform/health` | Platform health check |
| GET | `/api/v11/health` | Health alias |
| GET | `/api/v11/dashboard` | Unified v11 network dashboard |

---

### Enterprise Network

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/api/v11/network` | Network summary & statistics |
| GET | `/api/v11/network/topology` | Returns network mesh topology |
| GET | `/api/v11/network/nodes` | Lists connected organization nodes |
| POST | `/api/v11/network/nodes/connect` | Connects a new organization node |
| POST | `/api/v11/network/nodes/disconnect` | Disconnects an organization node |
| POST | `/api/v11/network/exchange` | Exchanges privacy-preserving intelligence |
| GET | `/api/v11/network/exchange/history` | Retrieves exchange packet history |

---

### Cross-Enterprise Collaboration

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/api/v11/collaboration` | Collaboration hub summary |
| GET | `/api/v11/collaboration/workflows` | Lists shared workflows |
| POST | `/api/v11/collaboration/workflows/share` | Shares a new cross-org workflow |
| POST | `/api/v11/collaboration/workflows/execute` | Executes a shared workflow |
| GET | `/api/v11/collaboration/knowledge` | Lists shared knowledge items |
| POST | `/api/v11/collaboration/knowledge/publish` | Publishes anonymised knowledge |
| POST | `/api/v11/collaboration/knowledge/search` | Searches shared knowledge base |
| GET | `/api/v11/collaboration/sessions` | Lists active collaboration sessions |
| POST | `/api/v11/collaboration/sessions/create` | Creates a new collaboration session |

---

### Distributed Intelligence

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/api/v11/distributed` | Distributed intelligence summary |
| GET | `/api/v11/distributed/memory` | Global memory stats |
| POST | `/api/v11/distributed/memory/store` | Stores a record in global memory |
| POST | `/api/v11/distributed/memory/recall` | Recalls records from global memory |
| POST | `/api/v11/distributed/reasoning/federated` | Executes federated multi-node reasoning |
| POST | `/api/v11/distributed/decision` | Orchestrates a multi-party distributed decision |

---

### Autonomous Coordination

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/api/v11/coordination` | Autonomous coordination summary |
| GET | `/api/v11/coordination/health` | Coordination health report |
| GET | `/api/v11/coordination/resources` | Lists multi-tenant resource allocations |
| POST | `/api/v11/coordination/resources/allocate` | Allocates resources to an organization |
| POST | `/api/v11/coordination/resources/rebalance` | Rebalances network resource pools |
| POST | `/api/v11/coordination/network/optimize` | Optimises routing latency between orgs |
| GET | `/api/v11/coordination/network/optimization-stats` | Returns latency & compression stats |

---

*Generated: 2026-08-04 | iFive AutoQA X Phase 29 — Version 11.0*
