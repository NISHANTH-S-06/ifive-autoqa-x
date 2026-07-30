"""Module 2 – Autonomous Workflow Composer service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase14_models import WorkflowExecution, WorkflowTemplate

DEFAULT_TEMPLATES = [
    {
        'template_name': 'Autonomous Full QA Pipeline',
        'category': 'QA_PIPELINE',
        'description': 'End-to-end QA flow: Discover → Analyze → Generate → Approve → Execute → Heal → Visual Diff → Release',
        'graph_definition': {
            'nodes': [
                {'id': 'step-1', 'label': 'Discover Application Topology', 'type': 'ACTION'},
                {'id': 'step-2', 'label': 'Analyze Risk & Business Flow', 'type': 'ACTION'},
                {'id': 'step-3', 'label': 'Generate Test Suite V3', 'type': 'ACTION'},
                {'id': 'step-4', 'label': 'Release Governance Approval', 'type': 'CONDITION'},
                {'id': 'step-5', 'label': 'Execute Parallel Runs in Lab', 'type': 'ACTION'},
                {'id': 'step-6', 'label': 'AI Self-Healing & Locator Fix', 'type': 'ACTION'},
                {'id': 'step-7', 'label': 'Visual Regression Check', 'type': 'ACTION'},
                {'id': 'step-8', 'label': 'Incident & Defect Routing', 'type': 'BRANCH'},
            ],
            'edges': [
                {'source': 'step-1', 'target': 'step-2'},
                {'source': 'step-2', 'target': 'step-3'},
                {'source': 'step-3', 'target': 'step-4'},
                {'source': 'step-4', 'target': 'step-5'},
                {'source': 'step-5', 'target': 'step-6'},
                {'source': 'step-6', 'target': 'step-7'},
                {'source': 'step-7', 'target': 'step-8'},
            ]
        }
    },
    {
        'template_name': 'Continuous Regression & Healing Loop',
        'category': 'REGRESSION',
        'description': 'Automated regression execution loop with auto-retry and locator healing.',
        'graph_definition': {
            'nodes': [
                {'id': 'reg-1', 'label': 'Fetch Priority Queue Jobs', 'type': 'ACTION'},
                {'id': 'reg-2', 'label': 'Run Browser Farm Pool', 'type': 'LOOP'},
                {'id': 'reg-3', 'label': 'Auto-Heal Broken Locators', 'type': 'ACTION'},
                {'id': 'reg-4', 'label': 'Publish Analytics Snapshot', 'type': 'ACTION'},
            ],
            'edges': [
                {'source': 'reg-1', 'target': 'reg-2'},
                {'source': 'reg-2', 'target': 'reg-3'},
                {'source': 'reg-3', 'target': 'reg-4'},
            ]
        }
    }
]


class WorkflowComposerService:
    """Manages visual QA workflow templates and executions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_templates(self) -> list[dict[str, Any]]:
        existing = self.db.query(WorkflowTemplate).count()
        if existing > 0:
            return self.list_templates()
        for t in DEFAULT_TEMPLATES:
            tpl = WorkflowTemplate(
                template_name=t['template_name'],
                category=t['category'],
                description=t['description'],
                graph_definition_json=json.dumps(t['graph_definition']),
            )
            self.db.add(tpl)
        self.db.commit()
        return self.list_templates()

    def list_templates(self) -> list[dict[str, Any]]:
        templates = self.db.query(WorkflowTemplate).filter_by(is_active=True).all()
        return [
            {
                'id': t.id,
                'template_name': t.template_name,
                'category': t.category,
                'description': t.description,
                'graph_definition': json.loads(t.graph_definition_json),
                'created_at': t.created_at.isoformat(),
            }
            for t in templates
        ]

    def create_template(
        self,
        template_name: str,
        category: str = 'QA_PIPELINE',
        description: str = '',
        graph_definition: dict[str, Any] | None = None,
        created_by: int | None = None,
    ) -> WorkflowTemplate:
        tpl = WorkflowTemplate(
            template_name=template_name,
            category=category,
            description=description,
            graph_definition_json=json.dumps(graph_definition or {}),
            created_by=created_by,
        )
        self.db.add(tpl)
        self.db.commit()
        self.db.refresh(tpl)
        return tpl

    def execute_workflow(self, template_id: int, execution_name: str) -> dict[str, Any]:
        template = self.db.query(WorkflowTemplate).filter_by(id=template_id).first()
        if not template:
            return {'error': 'Template not found'}

        graph = json.loads(template.graph_definition_json)
        nodes = graph.get('nodes', [])
        first_step = nodes[0]['id'] if nodes else None

        execution = WorkflowExecution(
            template_id=template_id,
            execution_name=execution_name,
            execution_status='RUNNING',
            current_step_id=first_step,
            state_json=json.dumps({'completed_steps': [], 'current_step_index': 0}),
            execution_log_json=json.dumps([{'timestamp': datetime.utcnow().isoformat(), 'message': f'Started workflow: {execution_name}'}]),
            started_at=datetime.utcnow(),
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        return {
            'id': execution.id,
            'execution_name': execution.execution_name,
            'execution_status': execution.execution_status,
            'current_step_id': execution.current_step_id,
            'started_at': execution.started_at.isoformat(),
        }

    def list_executions(self, limit: int = 20) -> list[dict[str, Any]]:
        executions = self.db.query(WorkflowExecution).order_by(WorkflowExecution.created_at.desc()).limit(limit).all()
        return [
            {
                'id': e.id,
                'template_id': e.template_id,
                'execution_name': e.execution_name,
                'execution_status': e.execution_status,
                'current_step_id': e.current_step_id,
                'state': json.loads(e.state_json),
                'started_at': e.started_at.isoformat() if e.started_at else None,
                'completed_at': e.completed_at.isoformat() if e.completed_at else None,
            }
            for e in executions
        ]
