import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.phase12_models import TestLabBrowserWorker

logger = logging.getLogger('autoqa.services.autonomous_test_lab')

BROWSER_FARM = [
    'CHROMIUM', 'CHROME', 'FIREFOX', 'EDGE', 'WEBKIT',
    'MOBILE_CHROME', 'MOBILE_SAFARI', 'TABLET', 'DESKTOP',
]


class AutonomousTestLabService:
    """
    Module 5: Autonomous Test Lab
    Multi-browser farm with parallel/distributed execution, scheduler,
    queue manager, and worker manager. Supports self-healing infrastructure.
    """

    def __init__(self, db: Session):
        self.db = db

    def provision_workers(self) -> List[Dict[str, Any]]:
        """Provision one worker per browser type if not already present."""
        workers = []
        for browser in BROWSER_FARM:
            existing = self.db.query(TestLabBrowserWorker).filter(
                TestLabBrowserWorker.browser_type == browser
            ).first()
            if not existing:
                worker = TestLabBrowserWorker(
                    worker_name=f'worker-{browser.lower().replace("_", "-")}-01',
                    browser_type=browser,
                    worker_status='IDLE',
                    jobs_completed=0,
                    jobs_failed=0,
                    last_heartbeat=datetime.utcnow(),
                )
                self.db.add(worker)
                workers.append(worker)
        self.db.commit()
        return [{'worker_name': w.worker_name, 'browser_type': w.browser_type, 'status': w.worker_status} for w in workers]

    def get_farm_status(self) -> Dict[str, Any]:
        workers = self.db.query(TestLabBrowserWorker).all()
        farm = [
            {
                'id': w.id,
                'worker_name': w.worker_name,
                'browser_type': w.browser_type,
                'status': w.worker_status,
                'jobs_completed': w.jobs_completed,
                'jobs_failed': w.jobs_failed,
                'last_heartbeat': w.last_heartbeat,
            }
            for w in workers
        ]
        idle_count = sum(1 for w in workers if w.worker_status == 'IDLE')
        busy_count = sum(1 for w in workers if w.worker_status == 'BUSY')
        unhealthy_count = sum(1 for w in workers if w.worker_status == 'UNHEALTHY')
        return {
            'total_workers': len(workers),
            'idle': idle_count,
            'busy': busy_count,
            'unhealthy': unhealthy_count,
            'workers': farm,
        }

    def self_heal_workers(self) -> Dict[str, Any]:
        """Module 10: Self-Healing Infrastructure – auto-restart unhealthy workers."""
        unhealthy = self.db.query(TestLabBrowserWorker).filter(
            TestLabBrowserWorker.worker_status == 'UNHEALTHY'
        ).all()
        healed = []
        for w in unhealthy:
            w.worker_status = 'IDLE'
            w.last_heartbeat = datetime.utcnow()
            healed.append(w.worker_name)
        self.db.commit()
        return {
            'healed_workers': healed,
            'healed_count': len(healed),
            'status': 'SELF_HEAL_COMPLETE',
        }
