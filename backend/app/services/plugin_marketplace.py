import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.phase12_models import PluginMarketplacePackage

logger = logging.getLogger('autoqa.services.plugin_marketplace')

SAMPLE_PLUGINS = [
    {
        'package_name': 'autoqa-jira-sync',
        'package_version': '2.1.0',
        'plugin_type': 'INTEGRATION',
        'author': 'iFive Enterprise',
        'description': 'Bi-directional Jira synchronization: Auto-create/update Jira issues from AutoQA defects.',
    },
    {
        'package_name': 'autoqa-slack-notifier',
        'package_version': '1.4.0',
        'plugin_type': 'INTEGRATION',
        'author': 'iFive Enterprise',
        'description': 'Real-time Slack notifications for test failures, release verdicts, and AI recommendations.',
    },
    {
        'package_name': 'autoqa-ai-validator-security',
        'package_version': '3.0.1',
        'plugin_type': 'VALIDATOR',
        'author': 'iFive Security Labs',
        'description': 'Advanced OWASP Top 10 security validation agent for enterprise applications.',
    },
    {
        'package_name': 'autoqa-custom-pdf-report',
        'package_version': '1.2.3',
        'plugin_type': 'REPORT',
        'author': 'Community',
        'description': 'Customizable branded PDF executive report with company logo and branding.',
    },
    {
        'package_name': 'autoqa-sap-connector',
        'package_version': '1.0.0',
        'plugin_type': 'INTEGRATION',
        'author': 'iFive Enterprise',
        'description': 'SAP ERP module connector for automated business rule validation and DB assertion.',
    },
    {
        'package_name': 'autoqa-servicenow-defects',
        'package_version': '1.1.0',
        'plugin_type': 'INTEGRATION',
        'author': 'iFive Enterprise',
        'description': 'Auto-raise ServiceNow incidents from critical test failures.',
    },
]


class PluginMarketplaceService:
    """
    Module 12: Plugin Marketplace
    Plugin SDK for: Custom Validators, Custom AI Agents, Custom Reports,
    Custom Browser Actions, Custom Integrations, Company Extensions, Version Management.
    """

    def __init__(self, db: Session):
        self.db = db

    def seed_marketplace(self) -> List[Dict[str, Any]]:
        """Seed the marketplace with built-in plugins if empty."""
        existing = self.db.query(PluginMarketplacePackage).count()
        if existing > 0:
            return self.list_packages()

        for plugin in SAMPLE_PLUGINS:
            pkg = PluginMarketplacePackage(
                package_name=plugin['package_name'],
                package_version=plugin['package_version'],
                plugin_type=plugin['plugin_type'],
                author=plugin['author'],
                description=plugin['description'],
                is_installed=False,
                config_schema_json='{}',
            )
            self.db.add(pkg)
        self.db.commit()
        return self.list_packages()

    def list_packages(self) -> List[Dict[str, Any]]:
        packages = self.db.query(PluginMarketplacePackage).all()
        return [
            {
                'id': p.id,
                'package_name': p.package_name,
                'version': p.package_version,
                'plugin_type': p.plugin_type,
                'author': p.author,
                'description': p.description,
                'is_installed': p.is_installed,
            }
            for p in packages
        ]

    def install_package(self, package_id: int) -> Dict[str, Any]:
        pkg = self.db.get(PluginMarketplacePackage, package_id)
        if not pkg:
            return {'error': 'Package not found'}
        pkg.is_installed = True
        self.db.commit()
        return {'package_name': pkg.package_name, 'status': 'INSTALLED'}

    def uninstall_package(self, package_id: int) -> Dict[str, Any]:
        pkg = self.db.get(PluginMarketplacePackage, package_id)
        if not pkg:
            return {'error': 'Package not found'}
        pkg.is_installed = False
        self.db.commit()
        return {'package_name': pkg.package_name, 'status': 'UNINSTALLED'}
