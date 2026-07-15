# Installation

Stage 14 installation, configuration, migration, lifecycle, backup, restore, retention, packaging, troubleshooting, and known-limitations are documented in [LOCAL_RELEASE_OPERATIONS.md](LOCAL_RELEASE_OPERATIONS.md).

No account is created automatically. After dependencies and migrations are ready, an authorized person may explicitly run:

```powershell
.\scripts\create_local_operator.ps1
```

The command prompts interactively, never prints or writes a plaintext password, rejects a second active ADMIN, and forces first-login password rotation.

