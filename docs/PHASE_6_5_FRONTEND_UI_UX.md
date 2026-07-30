# Phase 6.5 — Frontend UI/UX Integration and Visual Upgrade

## Architectural Overview

Phase 6.5 delivers a modern enterprise SaaS dashboard experience for the AutoQA platform. The application is styled with Vanilla CSS tokens, HSL color management, dark and light theme switching, glassmorphism surface treatments, compact readable data tables, status badges, and interactive step execution timelines.

No backend API services were rewritten, modified, or bypassed. Every single module page connects directly to the real existing AutoQA REST API endpoints, preserving strict RBAC authorization, cryptographic audit verification, project context isolation, and deterministic Playwright execution engine workflows.

---

## Design Tokens & Theme Engine

### 1. Palette & Theme Modes
- **Light Theme**: Soft `#f8fafc` background with crisp `#ffffff` surface cards, elevated shadows, and `#0f172a` primary text.
- **Dark Theme**: Deep `#0b0f17` background with `#131b2e` surface cards, dark borders (`#24304f`), and high-contrast `#f1f5f9` text.
- **Persistence**: Theme selection persists across browser refreshes via `localStorage.getItem('autoqa_theme')` and automatically respects system OS preferences (`prefers-color-scheme`).

### 2. Status Design System
The status badge system provides clear visual feedback across 11 standardized status tokens:

| Status Code | Visual Style | Icon | Semantic Meaning |
| :--- | :--- | :--- | :--- |
| `DRAFT` | Slate / Neutral Pill | `FileText` | Editable draft artifact |
| `IN_REVIEW` | Amber / Yellow Pill | `Clock` | Submitted awaiting peer approval |
| `APPROVED` | Emerald / Green Pill | `CheckCircle2` | Immutable approved state |
| `REJECTED` | Rose / Red Pill | `XCircle` | Rejected with mandatory reason |
| `NEED_CLARITY` | Purple / Violet Pill | `HelpCircle` | Blocked due to missing info |
| `QUEUED` | Sky / Blue Pill | `Layers` | Enqueued for worker execution |
| `RUNNING` | Cyan / Pulse Pill | `PlayCircle` | Currently executing on worker |
| `PASS` | Success Green Pill | `Check` | Deterministic 100% verification |
| `FAIL` | Danger Red Pill | `XCircle` | Execution error or assertion failure |
| `BLOCKED` | Orange / Amber Pill | `AlertCircle` | Blocked by missing dependency |
| `PASS_WITH_WARNINGS` | Chartreuse / Yellow Pill | `AlertTriangle` | Passed with non-critical warnings |

---

## Layout Architecture (`AppShell`)

```
+-----------------------------------------------------------------------------------+
|  BRAND (i5)  |  PROJECT SELECTOR  | STAGE: LOCAL | SEARCH (Ctrl+K) | THEME | USER |
+-----------------------------------------------------------------------------------+
| SIDEBAR      | BREADCRUMB: AutoQA > Dashboard                                     |
|              | PAGE TITLE: QA Platform Dashboard                                  |
| [x] Dashboard|--------------------------------------------------------------------+
| [ ] Task Imp | [ KPI Stat Card ]  [ KPI Stat Card ]  [ KPI Stat Card ] ...        |
| [ ] TestPlan |--------------------------------------------------------------------+
| [ ] ApprQueue|                                                                    |
| [ ] Auto Runs| +----------------------------------+ +---------------------------+ |
| [ ] Adv Valid| | Execution Readiness & Metrics    | | System Health Cards       | |
| [ ] Evidence | +----------------------------------+ +---------------------------+ |
| [ ] Defects  |                                                                    |
| [ ] Reports  | +----------------------------------+ +---------------------------+ |
| [ ] Schedules| | Recent Automated Runs            | | Recent Defects            | |
| [ ] Projects | +----------------------------------+ +---------------------------+ |
| [ ] Audit Log|                                                                    |
| [ ] Settings |                                                                    |
+-----------------------------------------------------------------------------------+
```

### Main Layout Components
1. **`AppShell.tsx`**: Top-level application shell enclosing sidebar navigation, top header, page content viewport, and global toast container.
2. **`Sidebar.tsx`**: Collapsible left sidebar providing navigation to all 13 module pages with active route indicators and attention badges.
3. **`TopHeader.tsx`**: Fixed top header with active project switcher (`/api/test-projects`), environment indicator, global search bar, notification drawer, theme toggle, and user menu.
4. **`PageHeader.tsx`**: Page-level breadcrumb path, title, description, and action button bar.

---

## 13 Core Module Pages

1. **Dashboard (`DashboardPage.tsx`)**: Real-time KPI stat cards, readiness metrics, system health monitors, recent automated runs, and open defect trackers.
2. **Task Imports (`TaskImportsPage.tsx`)**: Backlog requirements sync, AI plan generation trigger, requirement analysis, and task detail drawer.
3. **Test Plans (`TestPlansPage.tsx`)**: Multi-scenario test plan editor (Primary, Negative, Edge, Regression), step reorder controls, locator target editor, and version history.
4. **Approval Queue (`ApprovalQueuePage.tsx`)**: Peer review queue enforcing developer self-approval protection rules and mandatory rejection reason dialogs.
5. **Automated Runs (`AutomatedRunsPage.tsx`)**: Live step timelines, UI/API/DB validation result breakdowns, console/network logs, and execution artifact downloads.
6. **Advanced Validation (`AdvancedValidationPage.tsx`)**: Configuration profiles for API validation, read-only DB query checks, accessibility WCAG rules, and performance thresholds.
7. **Evidence Repository (`EvidencePage.tsx`)**: Central gallery for screenshots, trace ZIPs, DOM snapshots, and video recordings with lightbox preview modals.
8. **Defects (`DefectsPage.tsx`)**: Defect lifecycle tracker, fingerprint deduplication, evidence linkage, and automated retest trigger.
9. **Reports (`ReportsPage.tsx`)**: Management reports, HTML report preview modal, PDF/CSV export downloads, and cryptographic hash verification.
10. **Local Schedules (`LocalSchedulesPage.tsx`)**: Automated cron schedules, frequency controls, browser targets, and execution history.
11. **Projects (`ProjectsPage.tsx`)**: Multi-tenant test project context isolation, access project mapping, and archive controls.
12. **Audit Logs (`AuditLogsPage.tsx`)**: Cryptographic audit event ledger and SHA-256 hash chain integrity verification tool.
13. **Settings (`SettingsPage.tsx`)**: Operator administration, RBAC role management, session revocation, connection targets, and system health backups.

---

## Verification & Acceptability

- **TypeScript Compilation**: `npm run build` completed with zero type errors.
- **Playwright Test Suite**: `npx playwright test tests/phase6-5-ui-acceptance.spec.ts --project=chromium` executed with 5/5 tests passing in 4.4s.
