"""Version 2.0 Typed Configuration System."""
from pydantic import BaseModel, Field
from app.v2.config.constants import V2_VERSION, PHASE_MARKER
from app.v2.config.feature_flags import FeatureFlags


class AgentSettings(BaseModel):
    default_timeout_sec: float = Field(60.0, description="Default agent execution timeout")
    max_retries: int = Field(3, description="Maximum agent retry attempts")
    enable_memory_persistence: bool = Field(True, description="Persist agent memory across runs")


class PluginSettings(BaseModel):
    sandbox_enabled: bool = Field(True, description="Execute plugins in isolated sandbox")
    max_plugins_loaded: int = Field(50, description="Maximum plugins allowed in registry")


class KnowledgeSettings(BaseModel):
    vector_dimension: int = Field(1536, description="Embedding vector dimension")
    max_graph_depth: int = Field(5, description="Knowledge graph traversal depth limit")


class EventSettings(BaseModel):
    store_limit: int = Field(1000, description="In-memory event store record limit")
    async_dispatch: bool = Field(True, description="Dispatch events asynchronously")


class V2Settings(BaseModel):
    version: str = Field(V2_VERSION, description="Version 2.0 version string")
    phase: str = Field(PHASE_MARKER, description="Phase marker")
    features: FeatureFlags = Field(default_factory=FeatureFlags)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    plugin: PluginSettings = Field(default_factory=PluginSettings)
    knowledge: KnowledgeSettings = Field(default_factory=KnowledgeSettings)
    event: EventSettings = Field(default_factory=EventSettings)


# Singleton instance
v2_settings = V2Settings()
