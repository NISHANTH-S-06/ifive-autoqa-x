"""Enterprise Plugin SDK Framework for Version 2.0 (SDK Only, Zero Third-Party API Calls)."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field


class PluginManifest(BaseModel):
    plugin_id: str = Field(..., description="Unique plugin ID (e.g. 'org.ifive.jira')")
    name: str = Field(..., description="Human-readable plugin name")
    version: str = Field("1.0.0", description="Plugin semver string")
    description: Optional[str] = Field(None, description="Plugin description")
    supported_target: str = Field(..., description="Target system: Jira, AzureDevOps, GitHub, GitLab, Slack, Teams, Email, SAP, Salesforce")
    supported_events: List[str] = Field(default_factory=list, description="Events handled by this plugin")
    permissions: List[str] = Field(default_factory=list, description="Scope permissions requested")


class PluginContext(BaseModel):
    event_name: str = Field(..., description="Event name triggering plugin")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload data")
    config: Dict[str, Any] = Field(default_factory=dict, description="Plugin configuration")


class PluginResult(BaseModel):
    plugin_id: str = Field(..., description="Plugin identifier")
    status: str = Field("SUCCESS", description="Result status: SUCCESS, FAILED, SKIPPED")
    data: Dict[str, Any] = Field(default_factory=dict, description="Plugin processing output data")
    error: Optional[str] = Field(None, description="Error message if failed")


class PluginBase(ABC):
    def __init__(self, manifest: PluginManifest):
        self.manifest = manifest
        self.is_enabled = True

    @property
    def plugin_id(self) -> str:
        return self.manifest.plugin_id

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin connection parameters."""
        pass

    @abstractmethod
    async def handle_event(self, context: PluginContext) -> PluginResult:
        """Process event payload asynchronously."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check target system connectivity."""
        pass


class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, PluginBase] = {}

    def register(self, plugin: PluginBase) -> None:
        self._plugins[plugin.plugin_id] = plugin

    def unregister(self, plugin_id: str) -> Optional[PluginBase]:
        return self._plugins.pop(plugin_id, None)

    def get(self, plugin_id: str) -> Optional[PluginBase]:
        return self._plugins.get(plugin_id)

    def list_all(self) -> List[PluginManifest]:
        return [p.manifest for p in self._plugins.values()]


class PluginLoader:
    @staticmethod
    def instantiate_plugin(plugin_cls: Type[PluginBase], manifest: PluginManifest) -> PluginBase:
        return plugin_cls(manifest)


class PluginManager:
    def __init__(self, registry: Optional[PluginRegistry] = None):
        self.registry = registry or PluginRegistry()

    async def dispatch_event(self, event_name: str, payload: Dict[str, Any]) -> List[PluginResult]:
        results: List[PluginResult] = []
        for manifest in self.registry.list_all():
            plugin = self.registry.get(manifest.plugin_id)
            if plugin and plugin.is_enabled and event_name in manifest.supported_events:
                ctx = PluginContext(event_name=event_name, payload=payload)
                try:
                    res = await plugin.handle_event(ctx)
                    results.append(res)
                except Exception as ex:
                    results.append(
                        PluginResult(
                            plugin_id=plugin.plugin_id,
                            status="FAILED",
                            error=str(ex),
                        )
                    )
        return results
