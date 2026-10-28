# Phase 17.4 Event Runtime Integration Manual

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform  
**Target Package**: `backend/app/v2/events/`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

The Event Runtime automatically connects the in-memory `EventBus` to publish events across all platform engines: `DecisionEngine`, `WorkflowEngine`, `KnowledgeRuntime`, and `PluginRuntime`.

---

## 2. Event Dispatching

- `publish_platform_event(source_engine, event_type, payload)`: Standardized event dispatching with source metadata.
- `EventStore`: Logs event history in-memory for audit and compliance.
