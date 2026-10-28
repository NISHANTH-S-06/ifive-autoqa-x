# AUTO QA - Port Configuration Matrix

Standardized port assignments for the **AUTO QA** application within the multi-project ecosystem.

## System Port Allocations

| System Name | Backend Port | Frontend Port | Health Check Endpoint | Status |
|---|---|---|---|---|
| **OCR** | 8000 | 3000 | `/health` | Active |
| **AGENT ALINE X** | 8100 | 3100 | `/api/health` | Active |
| **MCP** | 8200 | 3200 | `/api/health` | Active |
| **AUTO QA** | **8300** | **3300** | `/api/health` | **Active (This System)** |

---

## AUTO QA Specific Endpoints

| Component | Target URL | Protocol | Port | Path | Description |
|---|---|---|---|---|---|
| **Backend REST API** | `http://127.0.0.1:8300` | HTTP | 8300 | `/` | Core FastAPI application |
| **Health Check Endpoint** | `http://127.0.0.1:8300` | HTTP | 8300 | `/api/health` | Returns HTTP 200 health status JSON |
| **API Documentation** | `http://127.0.0.1:8300` | HTTP | 8300 | `/docs` | Swagger OpenAPI documentation |
| **Frontend Web App** | `http://127.0.0.1:3300` | HTTP | 3300 | `/` | Vite React Single Page Application |

---

## Environment Variables

Port configuration is driven by standard environment variables in `.env`:

```ini
BACKEND_PORT=8300
FRONTEND_PORT=3300
AUTOQA_FRONTEND_URL=http://127.0.0.1:3300
VITE_API_BASE_URL=http://127.0.0.1:8300
```

---

## Service Management Commands

Launch and manage services using PowerShell scripts in the root directory:

- **Start Services**: `.\start.ps1`
- **Stop Services**: `.\stop.ps1`
- **Restart Services**: `.\restart.ps1`
- **Health Check**: `.\health_check.ps1`
