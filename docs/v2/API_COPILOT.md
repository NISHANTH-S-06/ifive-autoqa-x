# Phase 17.5 FastAPI Enterprise AI Copilot API Guide

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform  
**Target Router**: `backend/app/v2/api/v2_router.py`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

This guide documents the Version 2.0 REST API endpoints implemented in Phase 17.5 under `/api/v2/copilot/*`.

---

## 2. API Endpoints Reference

| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/api/v2/copilot/status` | Enterprise Copilot online status & capabilities |
| **POST** | `/api/v2/copilot/chat` | Multi-turn conversational copilot assistant |
| **GET** | `/api/v2/copilot/context` | Multi-dimensional project & workflow context |
| **GET** | `/api/v2/copilot/recommend` | 8-category recommendations list |
| **GET** | `/api/v2/copilot/history` | Multi-turn chat message history |
| **GET** | `/api/v2/copilot/learning` | Pattern learning and feedback statistics |
| **POST** | `/api/v2/copilot/feedback` | User rating (1-5) and correction submission |
| **GET** | `/api/v2/copilot/advisor` | Executive advisory recommendations |
| **GET** | `/api/v2/copilot/knowledge` | Knowledge pattern evolution list |
