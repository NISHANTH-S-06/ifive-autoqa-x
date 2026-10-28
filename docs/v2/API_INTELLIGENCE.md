# Phase 19 FastAPI Intelligence API Guide

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform (Version 2.1)  
**Target Router**: `backend/app/v2/api/v2_router.py`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

This guide documents the Version 2.1 REST API endpoints implemented in Phase 19 under `/api/v2/digital-twin`, `/simulation`, `/predictive`, `/optimization`, `/analytics`, `/risk`, and `/intelligence/*`.

---

## 2. API Endpoints Reference

| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/api/v2/digital-twin` | Digital Twin models & status |
| **POST** | `/api/v2/digital-twin/simulate` | Execute scenario simulation on Digital Twin |
| **GET** | `/api/v2/simulation` | Simulation engine status & capabilities |
| **POST** | `/api/v2/simulation/dry-run` | Run dry-run execution scenario |
| **GET** | `/api/v2/predictive` | Failure & quality forecasting |
| **GET** | `/api/v2/intelligence/forecast` | Release confidence forecast |
| **GET** | `/api/v2/optimization` | Workflow & resource optimization suggestions |
| **GET** | `/api/v2/analytics` | Enterprise analytics, KPIs & readiness score |
| **GET** | `/api/v2/risk` | Enterprise multi-factor risk assessment |
| **GET** | `/api/v2/intelligence/health` | Intelligence platform health check |
