# Phase 21 FastAPI Version 3.0 REST API Guide

**Platform**: iFive AutoQA X Distributed Enterprise QA Operating System (Version 3.1)  
**Target Router**: `backend/app/v3/api/v3_router.py`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

This guide documents the Version 3.0 REST API endpoints implemented in Phase 21 under `/api/v3/*`.

---

## 2. API Endpoints Reference

| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/api/v3/health` | Distributed platform health check |
| **GET** | `/api/v3/cluster` | Multi-node cluster overview & leader status |
| **GET** | `/api/v3/scheduler` | Distributed queue status & dead-letter queue count |
| **POST** | `/api/v3/scheduler/submit` | Submit high-priority job to distributed queue |
| **POST** | `/api/v3/scheduler/execute-next` | Execute next queued job from worker pool |
| **GET** | `/api/v3/runtime` | Kubernetes pod deployment status & recommended replicas |
| **GET** | `/api/v3/execution` | Browser pool status & active Playwright instances |
| **POST** | `/api/v3/execution/run-suite` | Execute partitioned test suite on execution fabric |
| **GET** | `/api/v3/storage` | Distributed artifact repository list |
| **POST** | `/api/v3/storage/artifact` | Store screenshot/trace artifact in repository |
| **GET** | `/api/v3/security` | Zero trust security summary & TLS certificate status |
| **GET** | `/api/v3/cloud` | Multi-cloud provider support list (AWS/Azure/GCP/OnPrem) |
| **GET** | `/api/v3/dashboard` | Dashboard backend aggregated telemetry |
