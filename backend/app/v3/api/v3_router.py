"""FastAPI Version 3.0 API Routers for Distributed Enterprise QA Operating System."""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.v3.cluster import ClusterManager
from app.v3.scheduler import JobScheduler
from app.v3.execution import ExecutionFabric
from app.v3.observability import ObservabilityPlatform
from app.v3.kubernetes import KubernetesManager
from app.v3.storage import StorageManager
from app.v3.security import SecurityPlatform
from app.v3.cloud import MultiCloudManager

router = APIRouter(prefix="/api/v3", tags=["Version 3.0 Distributed Enterprise QA Operating System"])

# Global Singletons
cluster_manager = ClusterManager()
job_scheduler = JobScheduler()
execution_fabric = ExecutionFabric()
observability_platform = ObservabilityPlatform()
kubernetes_manager = KubernetesManager()
storage_manager = StorageManager()
security_platform = SecurityPlatform()
cloud_manager = MultiCloudManager()


class SubmitJobRequest(BaseModel):
    task_name: str = Field("Execute Distributed ERP Regression Suite")
    priority: int = Field(1)


class StoreArtifactRequest(BaseModel):
    artifact_type: str = Field("SCREENSHOT")
    path: str = Field("/storage/v3/screenshots/po_created.png")
    size_bytes: int = Field(4096)


@router.get("/health")
async def get_v3_health():
    return {
        "status": "ok",
        "system": "iFive AutoQA X Distributed Enterprise QA Operating System",
        "version": "3.1",
        "phase": "21",
    }


@router.get("/cluster")
async def get_cluster_status():
    return cluster_manager.get_cluster_overview()


@router.get("/scheduler")
async def get_scheduler_status():
    return job_scheduler.get_queue_status()


@router.post("/scheduler/submit")
async def submit_scheduled_job(req: SubmitJobRequest):
    job = job_scheduler.submit_job(req.task_name, req.priority)
    return {"status": "success", "job": job.model_dump()}


@router.post("/scheduler/execute-next")
async def execute_next_scheduled_job():
    res = job_scheduler.execute_next_job()
    if not res:
        return {"status": "empty", "message": "No jobs in queue"}
    return res


@router.get("/runtime")
@router.get("/kubernetes")
async def get_kubernetes_runtime_status():
    return kubernetes_manager.get_k8s_runtime_overview()


@router.get("/execution")
async def get_execution_fabric_status():
    return {
        "status": "ONLINE",
        "browser_pool": execution_fabric.browser_pool.get_pool_status(),
    }


@router.post("/execution/run-suite")
async def run_suite_on_fabric(suite_name: str = "Purchasing Flow", test_cases: List[str] = ["TC-01", "TC-02", "TC-03"]):
    return execution_fabric.run_distributed_test_suite(suite_name, test_cases)


@router.get("/observability")
async def get_observability_status():
    return observability_platform.get_observability_summary()


@router.get("/storage")
async def get_storage_status():
    return {
        "status": "ONLINE",
        "total_artifacts": len(storage_manager.list_artifacts()),
        "artifacts": [a.model_dump() for a in storage_manager.list_artifacts()],
    }


@router.post("/storage/artifact")
async def store_artifact_endpoint(req: StoreArtifactRequest):
    art = storage_manager.store_artifact(req.artifact_type, req.path, req.size_bytes)
    return {"status": "success", "stored_artifact": art.model_dump()}


@router.get("/security")
async def get_security_status():
    return security_platform.get_security_summary()


@router.get("/cloud")
async def get_cloud_providers():
    return {
        "status": "ONLINE",
        "providers": cloud_manager.list_supported_providers(),
    }


@router.get("/dashboard")
async def get_dashboard_backend_metrics():
    return {
        "cluster": cluster_manager.get_cluster_overview(),
        "scheduler": job_scheduler.get_queue_status(),
        "execution_fabric": execution_fabric.browser_pool.get_pool_status(),
        "observability": observability_platform.get_observability_summary(),
        "kubernetes": kubernetes_manager.get_k8s_runtime_overview(),
        "security": security_platform.get_security_summary(),
    }
