"""Cloud Provider Abstraction for AWS, Azure, GCP, and On-Premise Runtimes."""
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class CloudProviderInfo(BaseModel):
    provider_name: str
    region: str = Field("us-east-1")
    status: str = Field("READY")


class CloudProvider:
    def get_info(self) -> CloudProviderInfo:
        raise NotImplementedError


class AWSCloudProvider(CloudProvider):
    def get_info(self) -> CloudProviderInfo:
        return CloudProviderInfo(provider_name="AWS (Amazon Web Services)", region="us-east-1")


class AzureCloudProvider(CloudProvider):
    def get_info(self) -> CloudProviderInfo:
        return CloudProviderInfo(provider_name="Azure (Microsoft Cloud)", region="eastus")


class GCPCloudProvider(CloudProvider):
    def get_info(self) -> CloudProviderInfo:
        return CloudProviderInfo(provider_name="GCP (Google Cloud Platform)", region="us-central1")


class OnPremCloudProvider(CloudProvider):
    def get_info(self) -> CloudProviderInfo:
        return CloudProviderInfo(provider_name="On-Premise Enterprise Datacenter", region="datacenter-01")


class MultiCloudManager:
    def __init__(self):
        self.providers: Dict[str, CloudProvider] = {
            "aws": AWSCloudProvider(),
            "azure": AzureCloudProvider(),
            "gcp": GCPCloudProvider(),
            "on_prem": OnPremCloudProvider(),
        }

    def list_supported_providers(self) -> List[Dict[str, Any]]:
        return [p.get_info().model_dump() for p in self.providers.values()]
