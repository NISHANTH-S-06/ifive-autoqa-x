# iFive AutoQA — Full End-to-End Video Demo Script

Status: Local Stage 1-14 release. Persistent ADMIN and real non-production iFive
target acceptance remain manual, pending prerequisites (see Scene 51).

## How authentication works in this script

Two different auth approaches are used, and this script keeps them separate:

- **Scripted/CI verification** (already run in this session) uses the Playwright
  mocked-auth fixture `qa/fixtures/authenticated.fixture.ts`, which fabricates an
  in-memory ADMIN session for the browser only. It never creates a real operator,
  never touches the real database, and never involves a real password.

- **Human-recorded video** needs a real logged-in operator on screen for each of
  the four roles. The mocked fixture only covers one role (ADMIN) inside automated
  tests, so it cannot be reused for a role-differentiated recording. A persistent
  ADMIN and several old demo accounts already exist in the configured database
  (discovered during this audit) — this script does **not** use them, name them,
  or touch them. Instead, Scene 7 has the authorized presenter create four
  **temporary** operators with `scripts\create_local_operator.ps1` (private,
  off-screen password entry), and Scene 52 deactivates them again afterward from
  Local Administration. No password is ever shown on screen.

## Roles used

VIEWER, TESTER, APPROVER, ADMIN — the exact operator roles defined in
`frontend/src/types/auth.ts` and enforced end-to-end by the backend.

## Product under test

iFive AutoQA itself (the local dashboard), using LOCAL mock targets only. No real
iFive ERP/HRMS/CRM/IIoT/Integration URL is opened, searched for, or referenced.

---

## Chapter 1 — Introduction, Architecture, Startup

| # | Role | Screen / Command | Action & Data | Expected Result | Voice-over (English) | Presenter Note (Tanglish) | Security Note | Duration |
| --- | ------ | ------------------- | ---------------- | ------------------ | ------------------------ | ----------------------------- | ---------------- | ---------- |
| 1 | Presenter | Slide / terminal | Introduce iFive AutoQA as a local-first QA platform for iFive products. | Title slide shown. | "This is iFive AutoQA, a local-first quality engineering platform. Everything you see today runs on this machine only." | "Intro slide caption panni, project name sollunga." | No real target or credential is shown at this stage. | 0:30 |
| 2 | Presenter | `ARCHITECTURE.md` / diagram | Summarize stack: React+Vite+TypeScript frontend, FastAPI+Python backend, SQLite, Playwright Test for QA. | Architecture diagram shown. | "The stack is React on the frontend, FastAPI on the backend, and SQLite for storage, with Playwright driving automated checks." | "Architecture diagram screen la vச்சு summary பண்ணுங்க." | Mention that AI assistance is design material only in this release; no AI runtime is installed. | 0:45 |
| 3 | Presenter | PowerShell | `cd D:\AUTO_QA_TESTING` then `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_migrations.ps1` | Console prints migration success, no errors. | "First we apply local database migrations." | "Command run pannala, screen la scroll pannunga, password ethuvum illa." | No credentials required; script only runs local schema migrations. | 0:30 |
| 4 | Presenter | PowerShell | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_local_system.ps1` | Backend, frontend, and one local worker start; script rejects duplicate/occupied ports. | "This single script starts the backend, frontend, and the local execution worker together." | "Start pannunga, terminal output kaamikkanum." | Script binds to loopback only; no public interface. | 0:45 |
| 5 | Presenter | PowerShell + browser | `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify_health.ps1`; open `http://127.0.0.1:8000/health`, `http://127.0.0.1:8000/docs`, `http://127.0.0.1:5173` | Console prints backend status, database ready, migrations current, worker heartbeat, queued jobs, Chromium availability. Browser loads dashboard login screen. | "Health check confirms backend, database, worker, and Chromium are all ready." | "Health script run pannitu, browser la frontend open pannunga." | Health output is sanitized: booleans and counts only, no secrets. | 1:00 |

## Chapter 2 — Authentication, Roles, Security

| # | Role | Screen | Action & Data | Expected Result | Voice-over | Presenter Note (Tanglish) | Security Note | Duration |
| --- | ------ | -------- | ---------------- | ------------------ | ------------- | ----------------------------- | ---------------- | ---------- |
| 6 | Presenter | Login screen (`App.tsx`) | Explain "Local Operator Login" form: Username, Password, Sign In button. No default credentials exist. | Login form shown, empty fields. | "There are no default accounts in AutoQA. Every operator is created explicitly and privately." | "Login screen kaamichu, default password illa nu sollunga." | Never type a real password on camera; this scene shows the empty form only. | 0:30 |
| 7 | ADMIN (presenter, off-screen) | PowerShell | Pause recording. Run `scripts\create_local_operator.ps1` four times to privately create four **temporary** demo operators: one ADMIN, one TESTER, one APPROVER, one VIEWER. Resume recording after. | Four temporary operators exist locally; none of their usernames/passwords appear on screen or in this document. | "Off camera, we created four temporary operators — one for each role — using the official interactive bootstrap script." | "Idha recording la kaatamatom — pause pannitu private ah operator create pannunga." | Password entry is fully off-screen; this is the only supported way to create a persistent operator. | 1:00 |
| 8 | ADMIN | Local Administration (`#administration`) | Log in as the temporary ADMIN. Open Local Administration. Point out Operators panel, "Create Operator" form, Audit Log, "Verify Audit Integrity" button, Operator Security table (Reset / Sessions / Revoke). | Security summary grid shows Active Operators, Locked Operators, Password Change Required, Active Sessions, Failed Logins, Audit Integrity: Valid. | "As ADMIN, this is the security control center — operator management and an append-only audit chain." | "ADMIN login aiduchu, security summary numbers sollunga." | Do not open the temporary ADMIN's own row detail beyond what is needed; no password/hash is ever shown. | 1:00 |
| 9 | TESTER | Header / role badge | Log out, log in as the temporary TESTER. Point out role badge in header reads "TESTER". Show Test Management, Connection Targets, Automated Runs, Defects nav items are visible but Local Administration is not. | TESTER sees authoring/execution tools but no Local Administration section. | "TESTER can author and execute tests but cannot manage operators." | "TESTER role badge kaamikkanum, admin panel illa nu sollunga." | Role boundary enforced both in UI and by the backend API. | 0:45 |
| 10 | APPROVER | Header / role badge | Log out, log in as the temporary APPROVER. Point out role badge reads "APPROVER". | APPROVER sees review/approval controls across Test Management, Connection Targets, Automated Runs, Defects. | "APPROVER reviews and approves work created by others — never their own." | "Approver login, role badge screen la காட்டுங்க." | Creator-approver separation applies even to ADMIN-created records. | 0:45 |
| 11 | VIEWER | Header / role badge | Log out, log in as the temporary VIEWER. Point out role badge reads "VIEWER". | VIEWER sees read-only views; create/approve/execute/edit/delete controls are absent or disabled. | "VIEWER is read-only across the whole platform." | "Viewer login, edit button illama irukanum nu kaamikkunga." | Confirms least-privilege role is enforced; full check happens in Scene 50. | 0:45 |
