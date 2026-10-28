# Software Intelligence Engine
## Version 9.0 — Universal Autonomous Software & Digital Ecosystem Platform

---

## Overview

The **Universal Software Intelligence Engine** is the core analytical subsystem of Version 9.0. It provides deep, cross-language software understanding, from repository profiling and language detection through dependency resolution to architecture classification.

---

## Components

### UniversalSoftwareEngine

Top-level orchestrator that coordinates all software intelligence sub-systems.

```python
from app.v9.software_intelligence import UniversalSoftwareEngine

engine = UniversalSoftwareEngine()
profile = engine.profile_repository(
    repo_name="enterprise-erp",
    source_sample="from fastapi import FastAPI",
    manifest="fastapi==0.100\npydantic==2.0"
)
```

### LanguageAnalyzer

Detects and profiles programming languages within a repository.

**Supported Languages:**

- Python
- Java
- C# (.NET)
- Go
- Rust
- Node.js / TypeScript / JavaScript

### Detection Strategy:

| Language | Detection Signal |
| ---------- | ---------------- |
| Java | `import java` prefix |
| C# | `using System` namespace |
| Go | `package main` declaration |
| Rust | `fn main()` entry point |
| Node.js | `require(` / npm references |
| Python | Default fallback + FastAPI/Django signals |

### FrameworkDetector

Identifies software frameworks via source-code signature scanning.

### Supported Frameworks:

| Framework | Detection Signatures |
| ----------- | --------------------- |
| FastAPI | `from fastapi`, `FastAPI(` |
| Django | `django.db`, `INSTALLED_APPS` |
| Spring Boot | `@SpringBootApplication`, `springframework` |
| React | `import React`, `from 'react'` |
| Angular | `@NgModule`, `@Component` |
| Vue | `createApp`, `defineComponent` |
| .NET | `Microsoft.AspNetCore`, `IServiceCollection` |

### DependencyResolver

Resolves and validates project dependencies from manifest files.

**Supported Ecosystems:**

- `pip` (requirements.txt, pyproject.toml)
- `maven` (pom.xml)
- `npm` / `yarn` (package.json)
- `gradle` (build.gradle)
- `cargo` (Cargo.toml)
- `go.mod`

### Output (DependencyGraph):

| Field | Description |
| ------- | ------------- |
| `total_dependencies` | Total dependency count |
| `direct` | Direct dependencies |
| `transitive` | Transitive/indirect dependencies |
| `vulnerable` | Known CVEs |
| `outdated` | Packages with newer versions |
| `dependency_health_score` | 0–100% health rating |

### ArchitectureClassifier

Classifies software architecture patterns from code hints and file structure.

### Detected Patterns:

| Pattern | Keyword Signal |
| --------- | --------------- |
| Microservices | `microservices`, `service mesh` |
| Monolith | `monolith`, `modular monolith` |
| Event-Driven | `event`, `message broker`, `queue` |
| Serverless | `serverless`, `lambda`, `function` |
| Layered N-Tier | `layered`, `presentation/business/data` |
| CQRS | `cqrs`, `command query` |
| Hexagonal | `hexagonal`, `ports-and-adapters` |

### RepositoryProfiler

Produces a holistic profile of the entire repository.

### Profile fields:

| Field | Type | Description |
| ------- | ------ | ------------- |
| `repo_id` | str | Unique repository identifier |
| `name` | str | Repository name |
| `primary_language` | str | Dominant language |
| `detected_languages` | List[str] | All identified languages |
| `detected_frameworks` | List[str] | All identified frameworks |
| `architecture` | ArchitectureProfile | Pattern + bounded contexts |
| `dependencies` | DependencyGraph | Dependency health graph |
| `quality_score` | float | 0–100 quality rating |
| `maintainability_index` | float | 0–100 maintainability rating |

---

## REST API Endpoints

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/api/v9/software/capabilities` | List supported languages and frameworks |
| POST | `/api/v9/software/analyse` | Analyse a repository and return full profile |
| POST | `/api/v9/software/generate` | Generate code for a given spec |
| GET | `/api/v9/software/generation/styles` | List supported API generation styles |

---

## Module Location

```text
backend/app/v9/software_intelligence/
├── __init__.py      ← Package exports
└── engine.py        ← All classes and models
```

---

*Generated: 2026-08-04 | iFive AutoQA X Phase 27 — Version 9.0*
