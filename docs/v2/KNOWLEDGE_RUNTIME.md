# Phase 17.4 Knowledge Runtime Manual

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform  
**Target Class**: `app.v2.knowledge.runtime.KnowledgeRuntime`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

`KnowledgeRuntime` provides a single unified runtime interface integrating Memory Stores, Knowledge Stores, Pattern Store, Execution History Analyzer, Prompt Library, Vector Interface, and Knowledge Graph.

---

## 2. Unified Capabilities

- `query_unified_knowledge(task_description)`: Queries matched ERP patterns, past execution stats, and locator suggestions in one call.
