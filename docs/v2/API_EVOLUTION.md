# Phase 20 FastAPI Evolution API Guide

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform (Version 3.0)  
**Target Router**: `backend/app/v2/api/v2_router.py`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

This guide documents the Version 3.0 REST API endpoints implemented in Phase 20 under `/api/v2/evolution`, `/evolution/history`, `/evolution/status`, `/improvement`, `/governance`, `/experiments`, `/self-learning`, `/intelligence/evolution`, and `/platform/evolution`.

---

## 2. API Endpoints Reference

| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/api/v2/evolution/status` | Evolution engine status & active snapshots |
| **GET** | `/api/v2/evolution/history` | Historical evolution cycles list |
| **POST** | `/api/v2/evolution/run` | Execute self-evolution cycle |
| **GET** | `/api/v2/improvement` | Autonomous improvement suggestions & scores |
| **GET** | `/api/v2/governance` | Governance policy & audit log history |
| **POST** | `/api/v2/governance/authorize` | Mandatory governance action authorization |
| **GET** | `/api/v2/experiments` | Experiment engine status & active A/B tests |
| **POST** | `/api/v2/experiments/run` | Execute A/B test experiment |
| **GET** | `/api/v2/self-learning` | Self-learning stats & evolved knowledge |
