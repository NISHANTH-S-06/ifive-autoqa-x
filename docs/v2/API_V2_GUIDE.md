# Phase 17.2 FastAPI Version 2.0 API Guide

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform  
**Target Router**: `backend/app/v2/api/v2_router.py`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

This guide documents the Version 2.0 REST API endpoints implemented in Phase 17.2 under `/api/v2/*`.

---

## 2. API Endpoints Reference

| HTTP Method | Endpoint | Description | Payload / Response |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/v2/health` | Platform & Phase 17.2 health status | `{"status":"ok", "phase":"17.2"}` |
| **GET** | `/api/v2/agents` | List registered AI agents | `{"total_agents":6, "registered_agent_ids":[...]}` |
| **GET** | `/api/v2/orchestrator/status` | Get Orchestrator status | `{"status":"ONLINE", "orchestrator_ready":true}` |
| **POST** | `/api/v2/orchestrator/execute` | Trigger autonomous QA pipeline | Input: `{"project_id":1, "task_description":"..."}` |
| **POST** | `/api/v2/workflows/execute` | Execute workflow endpoint | Input: `{"project_id":1, "task_description":"..."}` |
| **GET** | `/api/v2/reports` | Get quality execution reports | List of structured JSON reports |
