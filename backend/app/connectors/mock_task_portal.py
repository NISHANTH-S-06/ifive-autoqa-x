"""Mock Task Portal Connector implementation."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
import httpx

from app.connectors.base import BaseTaskConnector


class MockTaskPortalConnector(BaseTaskConnector):
    """Connector implementation for local Mock Task Portal (port 8001)."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        self.base_url = (
            base_url
            or os.environ.get('MOCK_TASK_PORTAL_BASE_URL', 'http://localhost:8001')
        ).rstrip('/')
        self.enabled = (
            os.environ.get('MOCK_TASK_PORTAL_ENABLED', 'true').lower() == 'true'
        )
        self.timeout = int(
            timeout_seconds
            or os.environ.get('MOCK_TASK_PORTAL_TIMEOUT_SECONDS', '10')
        )

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def health_check(self) -> bool:
        if not self.enabled:
            return False
        try:
            with self._client() as client:
                resp = client.get('/api/health')
                return resp.status_code == 200
        except Exception:
            return False

    def fetch_testing_l2_tasks(self) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            with self._client() as client:
                resp = client.get('/api/tasks', params={'status': 'TESTING_L2'})
                resp.raise_for_status()
                return resp.json()
        except Exception as err:
            raise RuntimeError(f'Failed to fetch TESTING_L2 tasks from Mock Task Portal: {err}') from err

    def fetch_task(self, source_task_id: str | int) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        try:
            with self._client() as client:
                resp = client.get(f'/api/tasks/{source_task_id}')
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return resp.json()
        except Exception as err:
            raise RuntimeError(f'Failed to fetch task {source_task_id} from Mock Task Portal: {err}') from err

    def send_qa_result(
        self,
        source_task_id: str | int,
        source_revision: int,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send QA result callback to Mock Task Portal.

        Callback payload format:
        {
          "source_system": "MOCK_TASK_PORTAL",
          "source_task_id": str,
          "source_revision": int,
          "autoqa_run_id": str,
          "qa_result": "PASS" | "FAIL" | "BLOCKED",
          "task_status": "QA_PASSED" | "REWORK" | "NEED_CLARITY" | "HOLD",
          "summary": str,
          "severity": str | None,
          "report_url": str | None,
          "completed_at": str (ISO)
        }
        """
        if not self.enabled:
            raise RuntimeError('Mock Task Portal connector is disabled.')

        # First record QA result if present
        qa_result = payload.get('qa_result')
        summary = payload.get('summary', '')

        with self._client() as client:
            # 1. Record QA result on portal
            if qa_result in {'PASS', 'FAIL', 'BLOCKED'}:
                qa_resp = client.post(
                    f'/api/tasks/{source_task_id}/qa-result',
                    json={'result': qa_result, 'reason': summary},
                )
                qa_resp.raise_for_status()

            # 2. If status needs explicit transition (e.g. REWORK)
            target_status = payload.get('task_status')
            if target_status and target_status not in {'QA_PASSED', 'QA_FAILED'}:
                status_resp = client.patch(
                    f'/api/tasks/{source_task_id}/status',
                    json={'new_status': target_status, 'reason': summary},
                )
                if status_resp.status_code == 200:
                    return status_resp.json()

            # Fetch updated task
            task_resp = client.get(f'/api/tasks/{source_task_id}')
            task_resp.raise_for_status()
            return task_resp.json()
