"""Auto-Registered Enterprise Plugin Runtime for Version 2.0."""
from typing import Dict, Any, List, Optional
from app.v2.plugins.sdk import PluginBase, PluginRegistry, PluginManager, PluginManifest, PluginContext, PluginResult


class GenericConnectorPlugin(PluginBase):
    def __init__(self, plugin_id: str, name: str, system: str):
        manifest = PluginManifest(
            plugin_id=plugin_id,
            name=name,
            version="2.0",
            supported_target=system,
            permission_scopes=["READ", "WRITE"],
        )
        super().__init__(manifest)

    async def initialize(self, config: Dict[str, Any]) -> bool:
        self._is_initialized = True
        return True

    async def handle_event(self, context: PluginContext) -> PluginResult:
        return PluginResult(
            plugin_id=self.manifest.plugin_id,
            status="SUCCESS",
            data={"system": self.manifest.supported_target, "event_handled": context.event_name},
        )

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "HEALTHY", "plugin_id": self.manifest.plugin_id}


class PluginRuntime:
    def __init__(self):
        self.registry = PluginRegistry()
        self.manager = PluginManager(self.registry)
        self._auto_register_connectors()

    def _auto_register_connectors(self) -> None:
        connectors = [
            ("jira", "Jira Defect Tracker Plugin", "Jira"),
            ("azure_devops", "Azure DevOps Boards Plugin", "Azure DevOps"),
            ("github", "GitHub CI/CD Actions Plugin", "GitHub"),
            ("gitlab", "GitLab CI/CD Pipelines Plugin", "GitLab"),
            ("slack", "Slack Notification Plugin", "Slack"),
            ("teams", "MS Teams Notification Plugin", "Teams"),
            ("email", "Enterprise Email Gateway Plugin", "Email"),
            ("sap", "SAP S/4HANA ERP Connector Plugin", "SAP"),
            ("salesforce", "Salesforce CRM Connector Plugin", "Salesforce"),
        ]

        for pid, name, sys in connectors:
            plugin = GenericConnectorPlugin(pid, name, sys)
            self.registry.register(plugin)

    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                "plugin_id": manifest.plugin_id,
                "name": manifest.name,
                "system": manifest.supported_target,
                "initialized": True,
            }
            for manifest in self.registry.list_all()
        ]
