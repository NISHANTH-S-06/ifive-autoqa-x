"""Module 8 – Enterprise API Hub service."""
from __future__ import annotations

import hashlib
import json
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase13_models import APIHubKey, APIHubWebhook

SDK_LANGUAGES = ['PYTHON', 'JAVA', 'NODE', 'CSHARP', 'GO']


class APIHubService:
    """Enterprise API Hub – key management, webhooks, rate limiting, SDK info."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── API Keys ──────────────────────────────────────────────────────────────

    def create_key(
        self,
        key_name: str,
        sdk_type: str = 'REST',
        rate_limit_rpm: int = 1000,
        permissions: list[str] | None = None,
        created_by: int | None = None,
        expires_days: int | None = None,
    ) -> dict[str, Any]:
        raw_key = f'aqx_{secrets.token_urlsafe(32)}'
        prefix = raw_key[:12]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        expires_at = (datetime.utcnow() + timedelta(days=expires_days)) if expires_days else None
        key = APIHubKey(
            key_name=key_name,
            key_prefix=prefix,
            key_hash=key_hash,
            sdk_type=sdk_type,
            rate_limit_rpm=rate_limit_rpm,
            permissions_json=json.dumps(permissions or ['READ']),
            created_by=created_by,
            expires_at=expires_at,
        )
        self.db.add(key)
        self.db.commit()
        self.db.refresh(key)
        return {
            'id': key.id,
            'key_name': key.key_name,
            'key_prefix': key.key_prefix,
            'raw_key': raw_key,  # Shown only once
            'sdk_type': key.sdk_type,
            'rate_limit_rpm': key.rate_limit_rpm,
            'permissions': json.loads(key.permissions_json),
            'expires_at': key.expires_at.isoformat() if key.expires_at else None,
        }

    def list_keys(self, created_by: int | None = None) -> list[dict[str, Any]]:
        q = self.db.query(APIHubKey)
        if created_by:
            q = q.filter_by(created_by=created_by)
        keys = q.order_by(APIHubKey.created_at.desc()).all()
        return [
            {
                'id': k.id,
                'key_name': k.key_name,
                'key_prefix': k.key_prefix + '...',
                'sdk_type': k.sdk_type,
                'key_status': k.key_status,
                'rate_limit_rpm': k.rate_limit_rpm,
                'permissions': json.loads(k.permissions_json),
                'last_used_at': k.last_used_at.isoformat() if k.last_used_at else None,
                'expires_at': k.expires_at.isoformat() if k.expires_at else None,
                'created_at': k.created_at.isoformat(),
            }
            for k in keys
        ]

    def revoke_key(self, key_id: int) -> dict[str, Any]:
        key = self.db.query(APIHubKey).filter_by(id=key_id).first()
        if not key:
            return {'error': 'Key not found'}
        key.key_status = 'REVOKED'
        self.db.commit()
        return {'id': key_id, 'status': 'REVOKED'}

    def verify_key(self, raw_key: str) -> dict[str, Any]:
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key = self.db.query(APIHubKey).filter_by(key_hash=key_hash, key_status='ACTIVE').first()
        if not key:
            return {'valid': False, 'error': 'Invalid or revoked key'}
        key.last_used_at = datetime.utcnow()
        self.db.commit()
        return {
            'valid': True,
            'key_name': key.key_name,
            'rate_limit_rpm': key.rate_limit_rpm,
            'permissions': json.loads(key.permissions_json),
        }

    # ── Webhooks ──────────────────────────────────────────────────────────────

    def register_webhook(
        self,
        webhook_name: str,
        target_url: str,
        event_types: list[str] | None = None,
    ) -> dict[str, Any]:
        secret = secrets.token_hex(32)
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        hook = APIHubWebhook(
            webhook_name=webhook_name,
            target_url=target_url,
            event_types_json=json.dumps(event_types or ['ALL']),
            secret_hash=secret_hash,
        )
        self.db.add(hook)
        self.db.commit()
        self.db.refresh(hook)
        return {
            'id': hook.id,
            'webhook_name': hook.webhook_name,
            'target_url': hook.target_url,
            'signing_secret': secret,  # Shown once
            'event_types': json.loads(hook.event_types_json),
        }

    def list_webhooks(self) -> list[dict[str, Any]]:
        hooks = self.db.query(APIHubWebhook).order_by(APIHubWebhook.created_at.desc()).all()
        return [
            {
                'id': h.id,
                'webhook_name': h.webhook_name,
                'target_url': h.target_url,
                'event_types': json.loads(h.event_types_json),
                'is_active': h.is_active,
                'delivery_count': h.delivery_count,
                'failure_count': h.failure_count,
                'created_at': h.created_at.isoformat(),
            }
            for h in hooks
        ]

    def delete_webhook(self, webhook_id: int) -> dict[str, Any]:
        hook = self.db.query(APIHubWebhook).filter_by(id=webhook_id).first()
        if not hook:
            return {'error': 'Webhook not found'}
        self.db.delete(hook)
        self.db.commit()
        return {'id': webhook_id, 'status': 'DELETED'}

    # ── SDK Info ──────────────────────────────────────────────────────────────

    def get_sdk_info(self) -> list[dict[str, Any]]:
        return [
            {
                'language': lang,
                'package_name': f'autoqa-sdk-{lang.lower()}',
                'version': '1.0.0',
                'install_command': self._install_cmd(lang),
                'documentation_url': f'https://docs.autoqa.io/sdk/{lang.lower()}',
                'example_snippet': self._example_snippet(lang),
            }
            for lang in SDK_LANGUAGES
        ]

    def _install_cmd(self, lang: str) -> str:
        cmds = {
            'PYTHON': 'pip install autoqa-sdk',
            'JAVA': 'maven: com.autoqa:autoqa-sdk:1.0.0',
            'NODE': 'npm install @autoqa/sdk',
            'CSHARP': 'dotnet add package AutoQA.SDK',
            'GO': 'go get github.com/autoqa/sdk-go',
        }
        return cmds.get(lang, 'See documentation')

    def _example_snippet(self, lang: str) -> str:
        snippets = {
            'PYTHON': 'from autoqa import Client\nclient = Client(api_key="aqx_...")\nresult = client.runs.list()',
            'JAVA': 'AutoQAClient client = new AutoQAClient("aqx_...");\nList<Run> runs = client.runs().list();',
            'NODE': 'const autoqa = require("@autoqa/sdk");\nconst client = new autoqa.Client("aqx_...");\nconst runs = await client.runs.list();',
            'CSHARP': 'var client = new AutoQAClient("aqx_...");\nvar runs = await client.Runs.ListAsync();',
            'GO': 'client := autoqa.NewClient("aqx_...")\nruns, err := client.Runs.List(ctx)',
        }
        return snippets.get(lang, '')
