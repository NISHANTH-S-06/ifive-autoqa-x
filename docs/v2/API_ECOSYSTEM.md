# Phase 18 FastAPI Multi-Agent Ecosystem API Guide

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform (Version 2.1)  
**Target Router**: `backend/app/v2/api/v2_router.py`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

This guide documents the Version 2.1 REST API endpoints implemented in Phase 18 under `/api/v2/ecosystem/*`, `/api/v2/plugins/*`, and `/api/v2/integrations/*`.

---

## 2. API Endpoints Reference

| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/api/v2/ecosystem/health` | Ecosystem health & message bus status |
| **GET** | `/api/v2/ecosystem/agents` | Registered multi-agent list |
| **GET** | `/api/v2/ecosystem/discovery` | Capability-based agent discovery |
| **GET** | `/api/v2/ecosystem/messages` | Message bus execution history |
| **POST** | `/api/v2/ecosystem/tasks` | Task delegation & workload assignment |
| **GET** | `/api/v2/ecosystem/collaboration` | Multi-agent collaborative planning |
| **GET** | `/api/v2/plugins/catalog` | Plugin Marketplace catalog |
| **POST** | `/api/v2/plugins/install` | Plugin installation & activation |
| **GET** | `/api/v2/plugins/status` | Installed plugin runtime status |
| **GET** | `/api/v2/integrations` | Integration Hub connectors status |
| **POST** | `/api/v2/integrations/sync` | External system data synchronization |
