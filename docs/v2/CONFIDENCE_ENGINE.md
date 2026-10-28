# Phase 17.3 Confidence Scoring Engine Manual

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform  
**Target Package**: `backend/app/v2/confidence/`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

The `ConfidenceEngine` calculates 0–100 numerical confidence scores accompanied by explainable rationale for execution runs, task plans, decisions, and overall workflows.

---

## 2. Confidence Metrics

- `compute_execution_confidence()`: Evaluates step pass ratios.
- `compute_planning_confidence()`: Evaluates subtask structure completeness.
- `compute_decision_confidence()`: Evaluates rule match score weights.
- `compute_workflow_confidence()`: Evaluates overall workflow status.
