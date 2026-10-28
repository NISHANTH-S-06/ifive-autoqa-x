# Version 2.0 Testing Guide Documentation

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform  
**Target Package**: `backend/app/v2/tests/`  
**Date**: 2026-08-03  

---

## 1. Overview

Version 2.0 introduces a modular unit test suite located in `backend/app/v2/tests/`. All tests validate framework components, DI containers, event buses, agent factories, and plugin registries without external infrastructure dependencies.

---

## 2. Test Execution Command

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest app/v2/tests/test_v2_foundation.py
```

---

## 3. Test Coverage Summary

- **Agent Framework**: Tests `BaseAgent`, `AgentRegistry`, `AgentFactory` execution & context passing.
- **Event Framework**: Tests `EventBus` subscriptions, in-memory `EventStore` logging, async event publication.
- **Plugin SDK**: Tests `PluginManager` event dispatching, `PluginRegistry` registration, `PluginManifest` validation.
- **Configuration Engine**: Tests `V2Settings` singleton, default feature flags, and constants.
- **Dependency Injection**: Tests `Container` singleton/factory registrations, `ServiceLocator` resolution.
- **Logging & Error Framework**: Tests `LoggerFactory` instance creation and custom `AgentException` / `PluginException` codes.
