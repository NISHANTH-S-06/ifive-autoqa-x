"""Enterprise Plugin Marketplace for Version 2.1."""
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.v2.plugins.sdk import PluginManifest, PluginRegistry
from app.v2.plugins.runtime import GenericConnectorPlugin


class PluginMarketplaceItem(BaseModel):
    plugin_id: str
    name: str
    system: str
    version: str = Field("2.1.0")
    author: str = Field("iFive Platform Engineering")
    status: str = Field("AVAILABLE", description="AVAILABLE, INSTALLED, ACTIVE, INACTIVE")
    downloads: int = Field(120)
    rating: float = Field(4.9)


class PluginCatalog:
    def __init__(self):
        self._items: Dict[str, PluginMarketplaceItem] = {
            "jira": PluginMarketplaceItem(plugin_id="jira", name="Jira Defect Tracker Plugin", system="Jira", status="INSTALLED"),
            "azure_devops": PluginMarketplaceItem(plugin_id="azure_devops", name="Azure DevOps Boards Plugin", system="Azure DevOps", status="INSTALLED"),
            "github": PluginMarketplaceItem(plugin_id="github", name="GitHub CI/CD Actions Plugin", system="GitHub", status="INSTALLED"),
            "gitlab": PluginMarketplaceItem(plugin_id="gitlab", name="GitLab CI/CD Pipelines Plugin", system="GitLab", status="INSTALLED"),
            "slack": PluginMarketplaceItem(plugin_id="slack", name="Slack Notification Plugin", system="Slack", status="INSTALLED"),
            "teams": PluginMarketplaceItem(plugin_id="teams", name="MS Teams Notification Plugin", system="Teams", status="INSTALLED"),
            "email": PluginMarketplaceItem(plugin_id="email", name="Enterprise Email Gateway Plugin", system="Email", status="INSTALLED"),
            "sap": PluginMarketplaceItem(plugin_id="sap", name="SAP S/4HANA ERP Connector Plugin", system="SAP", status="INSTALLED"),
            "salesforce": PluginMarketplaceItem(plugin_id="salesforce", name="Salesforce CRM Connector Plugin", system="Salesforce", status="INSTALLED"),
            "service_now": PluginMarketplaceItem(plugin_id="service_now", name="ServiceNow ITSM Plugin", system="ServiceNow", status="AVAILABLE"),
        }

    def list_all(self) -> List[PluginMarketplaceItem]:
        return list(self._items.values())

    def get(self, plugin_id: str) -> Optional[PluginMarketplaceItem]:
        return self._items.get(plugin_id)


class PluginValidator:
    def validate_manifest(self, manifest: PluginManifest) -> bool:
        return bool(manifest.plugin_id and manifest.name and manifest.supported_target)


class PluginInstaller:
    def __init__(self, registry: Optional[PluginRegistry] = None):
        self.registry = registry or PluginRegistry()
        self.validator = PluginValidator()

    def install_plugin(self, plugin_id: str, name: str, system: str) -> bool:
        plugin = GenericConnectorPlugin(plugin_id, name, system)
        if self.validator.validate_manifest(plugin.manifest):
            self.registry.register(plugin)
            return True
        return False


class PluginMarketplace:
    def __init__(self):
        self.catalog = PluginCatalog()
        self.installer = PluginInstaller()

    def list_catalog(self) -> List[Dict[str, Any]]:
        return [item.model_dump() for item in self.catalog.list_all()]

    def install(self, plugin_id: str) -> Dict[str, Any]:
        item = self.catalog.get(plugin_id)
        if not item:
            return {"status": "FAILED", "error": f"Plugin '{plugin_id}' not found in catalog"}
        
        success = self.installer.install_plugin(item.plugin_id, item.name, item.system)
        if success:
            item.status = "INSTALLED"
            return {"status": "SUCCESS", "message": f"Plugin '{item.name}' installed successfully"}
        return {"status": "FAILED", "error": "Plugin validation failed"}
