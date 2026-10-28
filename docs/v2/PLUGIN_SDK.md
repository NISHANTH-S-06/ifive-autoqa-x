# Version 2.0 Enterprise Plugin SDK Documentation

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform  
**Target Package**: `backend/app/v2/plugins/`  
**Date**: 2026-08-03  

---

## 1. Overview

The Plugin SDK provides an enterprise integration layer supporting third-party and custom connectors for Jira, Azure DevOps, GitHub, GitLab, Slack, Teams, Email, SAP, and Salesforce.

---

## 2. Core SDK Abstractions

- `PluginManifest`: Defines plugin metadata, supported target system, event triggers, and permission scopes.
- `PluginContext`: Carries event name, event payload, and connection parameters to plugin handlers.
- `PluginResult`: Output wrapper carrying plugin ID, status (`SUCCESS`/`FAILED`), data, and error messages.
- `PluginBase`: Abstract base class specifying `initialize()`, `handle_event()`, `health_check()`.
- `PluginRegistry`: Thread-safe registry for registering and looking up plugin instances.
- `PluginManager`: Dispatches platform events to all matching active plugins.
