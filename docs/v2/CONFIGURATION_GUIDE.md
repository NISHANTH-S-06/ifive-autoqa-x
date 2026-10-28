# Version 2.0 Typed Configuration Guide

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform  
**Target Package**: `backend/app/v2/config/`  
**Date**: 2026-08-03  

---

## 1. Overview

Version 2.0 configuration uses strongly-typed Pydantic settings models. Zero hardcoded secrets or environment variables exist in codebase.

---

## 2. Configuration Subsystems

- `constants.py`: Holds system constants (`V2_VERSION = "2.0"`, `PHASE_MARKER = "17.1"`).
- `feature_flags.py`: Feature flag toggles (`enable_v2_platform`, `enable_ai_agent_framework`, `enable_plugin_sdk`, `enable_knowledge_graph`, etc.).
- `settings.py`: Centralized `V2Settings` singleton containing `AgentSettings`, `PluginSettings`, `KnowledgeSettings`, `EventSettings`.
