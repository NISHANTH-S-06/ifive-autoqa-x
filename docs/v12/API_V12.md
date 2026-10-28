# Version 12.0 REST API Reference
## Autonomous Digital Civilization Platform

**Base URL:** `/api/v12`  
**Version:** 12.0  
**Phase:** 30  
**Router:** `app/v12/api/v12_router.py`

---

## Endpoint Index

### Platform & Health

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/api/v12/platform/status` | Returns platform status & roadmap completion |
| GET | `/api/v12/platform/health` | Platform health check |
| GET | `/api/v12/health` | Health alias |
| GET | `/api/v12/dashboard` | Unified v12 civilization dashboard |

---

### Digital Civilization Core

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/api/v12/civilization` | Civilization core summary |
| GET | `/api/v12/civilization/status` | Returns civilization status & era |
| GET | `/api/v12/civilization/policies` | Lists constitutional policies |
| POST | `/api/v12/civilization/policies/propose` | Proposes a new governance policy |
| GET | `/api/v12/civilization/audit` | Audits governance compliance |
| GET | `/api/v12/civilization/epoch` | Returns current civilization epoch |
| POST | `/api/v12/civilization/epoch/advance` | Advances civilization to next epoch |

---

### Global AI Society

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/api/v12/society` | Society summary |
| GET | `/api/v12/society/communities` | Lists AI agent communities/guilds |
| POST | `/api/v12/society/communities/create` | Creates a new AI community |
| GET | `/api/v12/society/agents` | Lists registered AI agents |
| POST | `/api/v12/society/agents/register` | Registers an AI agent to a community |
| GET | `/api/v12/society/links` | Lists inter-community links |
| POST | `/api/v12/society/links/establish` | Establishes an inter-community link |

---

### Autonomous Economy

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/api/v12/economy` | Digital economy summary |
| GET | `/api/v12/economy/listings` | Lists resource exchange listings |
| POST | `/api/v12/economy/listings/create` | Creates a resource listing |
| POST | `/api/v12/economy/trade` | Executes a resource trade |
| GET | `/api/v12/economy/transactions` | Trade transaction history |
| POST | `/api/v12/economy/contribute` | Records value contribution |
| GET | `/api/v12/economy/value-stats` | Value engine metrics |

---

### Global Coordination

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/api/v12/coordination` | Planetary coordination summary |
| GET | `/api/v12/coordination/telemetry` | Returns planetary telemetry |
| GET | `/api/v12/coordination/incidents` | Lists crisis incidents |
| POST | `/api/v12/coordination/incidents/trigger` | Triggers crisis mitigation |
| GET | `/api/v12/coordination/tasks` | Lists scheduled global tasks |
| POST | `/api/v12/coordination/tasks/schedule` | Schedules a planetary task |
| POST | `/api/v12/coordination/tasks/execute` | Executes scheduled tasks |

---

*Generated: 2026-08-04 | iFive AutoQA X Phase 30 — Version 12.0*
