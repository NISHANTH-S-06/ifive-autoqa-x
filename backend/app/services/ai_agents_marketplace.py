"""Module 3 – Enterprise AI Agents Marketplace service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase14_models import AgentPackage

DEFAULT_AGENTS = [
    {'agent_name': 'Security Sentinel Agent', 'agent_key': 'sec_sentinel', 'agent_category': 'SECURITY', 'version': '1.2.0', 'description': 'Automated SAST/DAST security scanning & vulnerability checks.', 'permissions': ['NETWORK', 'INSPECT_DOM', 'VAULT_READ']},
    {'agent_name': 'A11y Accessibility Guardian', 'agent_key': 'a11y_guardian', 'agent_category': 'ACCESSIBILITY', 'version': '2.0.1', 'description': 'WCAG 2.1 AA/AAA accessibility compliance auditing agent.', 'permissions': ['INSPECT_DOM', 'SCREENSHOT']},
    {'agent_name': 'SAP ERP Transaction Agent', 'agent_key': 'sap_erp_agent', 'agent_category': 'SAP', 'version': '1.0.0', 'description': 'Specialized agent for SAP S/4HANA GUI & Fiori transactional testing.', 'permissions': ['API_CALL', 'EXECUTE_STEPS']},
    {'agent_name': 'Salesforce CRM Agent', 'agent_key': 'sfdc_agent', 'agent_category': 'CRM', 'version': '1.5.0', 'description': 'Salesforce Object & Lightning component test validation agent.', 'permissions': ['API_CALL', 'EXECUTE_STEPS']},
    {'agent_name': 'Finance & Ledger Validator', 'agent_key': 'finance_validator', 'agent_category': 'FINANCE', 'version': '1.1.0', 'description': 'Financial balance sheet, invoicing & double-entry ledger validator.', 'permissions': ['DATABASE_READ', 'ASSERT_EQUALS']},
    {'agent_name': 'High-Load Performance Agent', 'agent_key': 'perf_load_agent', 'agent_category': 'PERFORMANCE', 'version': '2.2.0', 'description': 'Distributed load simulation & response latency agent.', 'permissions': ['NETWORK_STRESS', 'METRICS_WRITE']},
    {'agent_name': 'Multi-Browser Swarm Agent', 'agent_key': 'browser_swarm', 'agent_category': 'BROWSER', 'version': '3.0.0', 'description': 'Cross-browser swarm coordination & visual snapshot agent.', 'permissions': ['BROWSER_FARM', 'SCREENSHOT']},
    {'agent_name': 'Database Consistency Agent', 'agent_key': 'db_consistency', 'agent_category': 'DATABASE', 'version': '1.0.4', 'description': 'Database transaction integrity & migration verification agent.', 'permissions': ['DATABASE_READ', 'SCHEMA_CHECK']},
    {'agent_name': 'REST & GraphQL API Agent', 'agent_key': 'api_sentinel', 'agent_category': 'API', 'version': '2.1.0', 'description': 'Contract testing & schema validation agent for REST/GraphQL APIs.', 'permissions': ['API_CALL', 'SCHEMA_CHECK']},
    {'agent_name': 'HIPAA & GDPR Compliance Agent', 'agent_key': 'compliance_guardian', 'agent_category': 'COMPLIANCE', 'version': '1.3.0', 'description': 'Data masking, PII protection & regulatory compliance auditor.', 'permissions': ['DATA_MASK', 'AUDIT_WRITE']},
]


class AIAgentsMarketplaceService:
    """Manages custom AI agent packages (installation, permissions, updates, health)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_agents(self) -> list[dict[str, Any]]:
        existing = self.db.query(AgentPackage).count()
        if existing > 0:
            return self.list_agents()
        for a in DEFAULT_AGENTS:
            pkg = AgentPackage(
                agent_name=a['agent_name'],
                agent_key=a['agent_key'],
                agent_category=a['agent_category'],
                version=a['version'],
                description=a['description'],
                permissions_json=json.dumps(a['permissions']),
            )
            self.db.add(pkg)
        self.db.commit()
        return self.list_agents()

    def list_agents(self, category: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(AgentPackage)
        if category:
            q = q.filter_by(agent_category=category)
        agents = q.order_by(AgentPackage.agent_name).all()
        return [self._agent_dict(a) for a in agents]

    def install_agent(self, agent_id: int) -> dict[str, Any]:
        agent = self.db.query(AgentPackage).filter_by(id=agent_id).first()
        if not agent:
            return {'error': 'Agent not found'}
        agent.install_status = 'INSTALLED'
        agent.health_status = 'HEALTHY'
        agent.installed_at = datetime.utcnow()
        self.db.commit()
        return self._agent_dict(agent)

    def update_agent(self, agent_id: int) -> dict[str, Any]:
        agent = self.db.query(AgentPackage).filter_by(id=agent_id).first()
        if not agent:
            return {'error': 'Agent not found'}
        parts = agent.version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        agent.version = '.'.join(parts)
        agent.install_status = 'INSTALLED'
        self.db.commit()
        return self._agent_dict(agent)

    def uninstall_agent(self, agent_id: int) -> dict[str, Any]:
        agent = self.db.query(AgentPackage).filter_by(id=agent_id).first()
        if not agent:
            return {'error': 'Agent not found'}
        agent.install_status = 'AVAILABLE'
        agent.installed_at = None
        self.db.commit()
        return self._agent_dict(agent)

    def _agent_dict(self, a: AgentPackage) -> dict[str, Any]:
        return {
            'id': a.id,
            'agent_name': a.agent_name,
            'agent_key': a.agent_key,
            'agent_category': a.agent_category,
            'version': a.version,
            'description': a.description,
            'install_status': a.install_status,
            'health_status': a.health_status,
            'permissions': json.loads(a.permissions_json),
            'installed_at': a.installed_at.isoformat() if a.installed_at else None,
        }
