# Phase 22 FastAPI Version 4.0 REST API Guide

**Platform**: iFive AutoQA X Autonomous Software Engineering Platform (Version 4.0)  
**Target Router**: `backend/app/v4/api/v4_router.py`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

This guide documents the Version 4.0 REST API endpoints implemented in Phase 22 under `/api/v4/*`.

---

## 2. API Endpoints Reference

| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/api/v4/system/status` | Autonomous Software Engineering platform status |
| **GET** | `/api/v4/code` | Multi-language source code analysis & graph maps |
| **POST** | `/api/v4/review` | Security, complexity, & quality code review |
| **POST** | `/api/v4/refactor` | Safe code refactoring & import optimization |
| **POST** | `/api/v4/repair` | 5-stage autonomous bug repair pipeline |
| **POST** | `/api/v4/generator` | Generate full-stack feature (backend, frontend, test, docs) |
| **GET** | `/api/v4/testing` | Generate Pytest, Playwright, & API test suites |
| **GET** | `/api/v4/architecture` | Architecture health report & pattern detection |
| **GET** | `/api/v4/documentation` | System documentation & sequence diagrams |
| **GET** | `/api/v4/git` | Git pull requests & merge advisor status |
| **POST** | `/api/v4/git/pr` | Create automated semantic pull request |
| **GET** | `/api/v4/copilot` | Developer copilot coding suggestions |
| **GET** | `/api/v4/metrics` | Software engineering productivity & quality metrics |
