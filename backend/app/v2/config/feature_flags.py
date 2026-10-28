"""Version 2.0 Feature Flags Configuration."""
from pydantic import BaseModel, Field

class FeatureFlags(BaseModel):
    enable_v2_platform: bool = Field(True, description="Enable Version 2.0 AI Engineering Platform")
    enable_ai_agent_framework: bool = Field(True, description="Enable autonomous multi-agent framework")
    enable_plugin_sdk: bool = Field(True, description="Enable enterprise plugin SDK & connectors")
    enable_knowledge_graph: bool = Field(True, description="Enable enterprise knowledge graph")
    enable_self_healing: bool = Field(True, description="Enable DOM selector self-healing interceptor")
    enable_predictive_quality: bool = Field(True, description="Enable predictive release quality forecasting")
