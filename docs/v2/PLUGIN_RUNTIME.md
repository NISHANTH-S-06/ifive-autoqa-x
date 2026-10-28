# Phase 17.4 Plugin Runtime Manual

**Platform**: iFive AutoQA X Enterprise AI Engineering Platform  
**Target Class**: `app.v2.plugins.runtime.PluginRuntime`  
**Date**: 2026-08-03  

---

## 1. Executive Summary

`PluginRuntime` connects the Enterprise Plugin SDK and automatically registers 9 enterprise connectors on startup:

1. **Jira** (Defect Tracker)
2. **Azure DevOps** (Boards & Pipelines)
3. **GitHub** (Actions CI/CD)
4. **GitLab** (Pipelines CI/CD)
5. **Slack** (ChatOps Notifications)
6. **Teams** (Collaboration Gateway)
7. **Email** (Enterprise Gateway)
8. **SAP** (S/4HANA ERP Connector)
9. **Salesforce** (CRM Connector)
