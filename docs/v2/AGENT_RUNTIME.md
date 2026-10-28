# Phase 17.4 Agent Runtime Architecture Manual

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform  
**Target Class**: `app.v2.runtime.manager.AgentRuntime`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

`AgentRuntime` encapsulates active agent execution states (`STOPPED`, `STARTING`, `RUNNING`, `PAUSED`, `ERROR`), execution performance metrics, error counters, and async lifecycle methods.

---

## 2. Agent Instances Managed

- `PlannerAgent`: Task decomposition and subtask planning.
- `ExecutionAgent`: Simulated Playwright action runner.
- `ReviewAgent`: Execution completeness review.
- `HealingAgent`: Self-healing selector inspection.
- `ReportingAgent`: Quality reporting and JSON generation.
- `CoordinatorAgent`: Workflow coordination.
