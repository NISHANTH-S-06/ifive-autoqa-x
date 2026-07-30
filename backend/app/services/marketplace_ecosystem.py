"""Module 9 – Marketplace Ecosystem service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase13_models import MarketplacePlugin

SEED_PLUGINS = [
    {
        'plugin_name': 'AI Visual Validator Pro',
        'plugin_version': '2.1.0',
        'plugin_category': 'VALIDATOR',
        'author': 'AutoQA Labs',
        'description': 'Advanced AI-powered visual regression validation with heatmap analysis.',
        'rating': 4.8,
        'install_count': 1240,
        'manifest_json': {'entry_point': 'validators/visual_pro.py', 'permissions': ['SCREENSHOT', 'BASELINE']},
    },
    {
        'plugin_name': 'Autonomous API Sentinel',
        'plugin_version': '1.5.3',
        'plugin_category': 'AI_AGENT',
        'author': 'QA Innovations Inc.',
        'description': 'AI agent that autonomously monitors and validates API contracts.',
        'rating': 4.7,
        'install_count': 890,
        'manifest_json': {'entry_point': 'agents/api_sentinel.py', 'permissions': ['API_CALL', 'REPORT']},
    },
    {
        'plugin_name': 'Enterprise PDF Report Suite',
        'plugin_version': '3.0.1',
        'plugin_category': 'REPORT',
        'author': 'ReportCraft',
        'description': 'Generate branded executive PDF reports with charts and KPIs.',
        'rating': 4.6,
        'install_count': 2100,
        'manifest_json': {'entry_point': 'reports/pdf_suite.py', 'permissions': ['READ_RUNS', 'EXPORT']},
    },
    {
        'plugin_name': 'Dark Nebula UI Theme',
        'plugin_version': '1.0.0',
        'plugin_category': 'THEME',
        'author': 'UI Studio',
        'description': 'Professional dark nebula theme for the AutoQA dashboard.',
        'rating': 4.5,
        'install_count': 560,
        'manifest_json': {'css_variables': {'--bg-app': '#050a14', '--color-primary': '#6366f1'}},
    },
    {
        'plugin_name': 'Salesforce Test Connector',
        'plugin_version': '1.2.0',
        'plugin_category': 'CONNECTOR',
        'author': 'SFX Connect',
        'description': 'Native Salesforce CRM integration for syncing defects and test results.',
        'rating': 4.4,
        'install_count': 430,
        'manifest_json': {'entry_point': 'connectors/salesforce.py', 'permissions': ['DEFECTS', 'WEBHOOK']},
    },
    {
        'plugin_name': 'Playwright Smart Executor',
        'plugin_version': '2.0.0',
        'plugin_category': 'EXECUTOR',
        'author': 'AutoQA Labs',
        'description': 'Enhanced Playwright executor with auto-retry, healing, and parallel scaling.',
        'rating': 4.9,
        'install_count': 3200,
        'manifest_json': {'entry_point': 'executors/playwright_smart.py', 'permissions': ['EXECUTE', 'WORKER']},
    },
    {
        'plugin_name': 'Accessibility Guardian',
        'plugin_version': '1.1.0',
        'plugin_category': 'EXTENSION',
        'author': 'A11y Labs',
        'description': 'WCAG 2.1 AA/AAA automated accessibility compliance checking extension.',
        'rating': 4.7,
        'install_count': 780,
        'manifest_json': {'entry_point': 'extensions/a11y_guardian.py', 'permissions': ['SCREENSHOT', 'REPORT']},
    },
    {
        'plugin_name': 'SAP S/4HANA Connector',
        'plugin_version': '1.0.2',
        'plugin_category': 'CONNECTOR',
        'author': 'ERP Connectors GmbH',
        'description': 'Native SAP S/4HANA integration for enterprise ERP test automation.',
        'rating': 4.3,
        'install_count': 210,
        'manifest_json': {'entry_point': 'connectors/sap.py', 'permissions': ['DEFECTS', 'TASKS']},
    },
]

CATEGORIES = ['PLUGIN', 'AI_AGENT', 'REPORT', 'THEME', 'CONNECTOR', 'VALIDATOR', 'EXECUTOR', 'EXTENSION']


class MarketplaceEcosystemService:
    """Enterprise plugin marketplace management."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_marketplace(self) -> list[dict[str, Any]]:
        existing = self.db.query(MarketplacePlugin).count()
        if existing > 0:
            return self.list_plugins()
        for p in SEED_PLUGINS:
            plugin = MarketplacePlugin(
                plugin_name=p['plugin_name'],
                plugin_version=p['plugin_version'],
                plugin_category=p['plugin_category'],
                author=p['author'],
                description=p['description'],
                rating=p['rating'],
                install_count=p['install_count'],
                manifest_json=json.dumps(p['manifest_json']),
            )
            self.db.add(plugin)
        self.db.commit()
        return self.list_plugins()

    def list_plugins(self, category: str | None = None, search: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(MarketplacePlugin)
        if category:
            q = q.filter_by(plugin_category=category)
        plugins = q.order_by(MarketplacePlugin.install_count.desc()).all()
        if search:
            plugins = [p for p in plugins if search.lower() in p.plugin_name.lower() or search.lower() in p.description.lower()]
        return [self._plugin_dict(p) for p in plugins]

    def install_plugin(self, plugin_id: int) -> dict[str, Any]:
        plugin = self.db.query(MarketplacePlugin).filter_by(id=plugin_id).first()
        if not plugin:
            return {'error': 'Plugin not found'}
        plugin.install_status = 'INSTALLED'
        plugin.install_count += 1
        self.db.commit()
        return {'id': plugin_id, 'plugin_name': plugin.plugin_name, 'status': 'INSTALLED'}

    def uninstall_plugin(self, plugin_id: int) -> dict[str, Any]:
        plugin = self.db.query(MarketplacePlugin).filter_by(id=plugin_id).first()
        if not plugin:
            return {'error': 'Plugin not found'}
        plugin.install_status = 'AVAILABLE'
        self.db.commit()
        return {'id': plugin_id, 'plugin_name': plugin.plugin_name, 'status': 'UNINSTALLED'}

    def get_categories(self) -> list[dict[str, Any]]:
        plugins = self.db.query(MarketplacePlugin).all()
        by_cat: dict[str, int] = {}
        for p in plugins:
            by_cat[p.plugin_category] = by_cat.get(p.plugin_category, 0) + 1
        return [{'category': c, 'count': by_cat.get(c, 0)} for c in CATEGORIES]

    def _plugin_dict(self, p: MarketplacePlugin) -> dict[str, Any]:
        return {
            'id': p.id,
            'plugin_name': p.plugin_name,
            'plugin_version': p.plugin_version,
            'plugin_category': p.plugin_category,
            'author': p.author,
            'description': p.description,
            'install_status': p.install_status,
            'install_count': p.install_count,
            'rating': p.rating,
            'manifest': json.loads(p.manifest_json),
        }
