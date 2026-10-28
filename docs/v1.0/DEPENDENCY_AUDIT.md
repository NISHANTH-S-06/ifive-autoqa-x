# DEPENDENCY_AUDIT.md — iFive AutoQA X (live 26-router / 19-page product)

## Backend (`backend/requirements.txt`)

All 9 pinned packages verified by direct import-count scan of `app/` and `tests/`:

| Package | References found | Status |
| --- | --- | --- |
| fastapi | 121 | USED |
| uvicorn | 0 direct imports (CLI-only: `python -m uvicorn app.main:app`) | USED (correct — no import needed) |
| sqlalchemy | 318 | USED |
| alembic | 9 | USED |
| pydantic | 56 | USED |
| pytest | 29 | USED (dev/test) |
| httpx | 4 | USED |
| Pillow | 2 | USED (screenshot validation) |
| python-multipart | 0 direct imports, but 36 `UploadFile`/`Form`/`File` usages across API routes | USED (required transitively by FastAPI for multipart parsing) |

**Result: zero unused, zero duplicate, zero obviously-vulnerable pinned packages.**
Not checked in this pass: CVE database lookup against exact pinned versions
(would need network access to PyPI advisory data — flagging as a follow-up,
not fabricating a clean bill of health for something not actually checked).

## Frontend (`frontend/package.json`)

| Package | Status |
| --- | --- |
| react, react-dom | USED (core) |
| lucide-react | USED (icons throughout Sidebar/TopHeader/CommandPalette/pages) |
| framer-motion | USED (added this session for Command Palette + Dashboard micro-interactions) |
| @types/node, @types/react, @types/react-dom | USED (TypeScript types, dev) |
| @vitejs/plugin-react, vite | USED (build tooling) |
| typescript | USED |

**Result: zero unused packages.** `npm audit` → 0 vulnerabilities (fixed one
transitive `postcss` path-traversal advisory via `npm audit fix` earlier this
session).

## Not audited in this pass

`mock-task-portal/backend`, `mock-task-portal/frontend`, `demo-product/backend`,
`demo-product/frontend` each have their own `requirements.txt`/`package.json` —
not yet scanned. These are separate PoC applications, lower priority than the
main product for this sprint.
