"""Module 10 – Enterprise DevOps integration service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase13_models import DevOpsPipeline

CI_TOOLS = [
    'GITHUB', 'GITLAB', 'AZURE_DEVOPS', 'BITBUCKET',
    'JENKINS', 'CIRCLECI', 'TEAMCITY', 'ARGOCD',
    'KUBERNETES', 'DOCKER', 'TERRAFORM',
]

_TOOL_META: dict[str, dict[str, str]] = {
    'GITHUB': {'icon': 'github', 'docs': 'https://docs.github.com/actions'},
    'GITLAB': {'icon': 'gitlab', 'docs': 'https://docs.gitlab.com/ee/ci/'},
    'AZURE_DEVOPS': {'icon': 'azure', 'docs': 'https://docs.microsoft.com/azure/devops/pipelines'},
    'BITBUCKET': {'icon': 'bitbucket', 'docs': 'https://support.atlassian.com/bitbucket-cloud/docs/get-started-with-bitbucket-pipelines'},
    'JENKINS': {'icon': 'jenkins', 'docs': 'https://www.jenkins.io/doc/'},
    'CIRCLECI': {'icon': 'circleci', 'docs': 'https://circleci.com/docs/'},
    'TEAMCITY': {'icon': 'teamcity', 'docs': 'https://www.jetbrains.com/teamcity/'},
    'ARGOCD': {'icon': 'argocd', 'docs': 'https://argo-cd.readthedocs.io/'},
    'KUBERNETES': {'icon': 'kubernetes', 'docs': 'https://kubernetes.io/docs/'},
    'DOCKER': {'icon': 'docker', 'docs': 'https://docs.docker.com/'},
    'TERRAFORM': {'icon': 'terraform', 'docs': 'https://developer.hashicorp.com/terraform/docs'},
}


class EnterpriseDevOpsService:
    """Manages CI/CD pipeline integrations for all supported DevOps tools."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_pipelines(self, project_id: int | None = None) -> list[dict[str, Any]]:
        q = self.db.query(DevOpsPipeline)
        if project_id:
            q = q.filter_by(project_id=project_id)
        pipelines = q.order_by(DevOpsPipeline.created_at.desc()).all()
        return [self._pipeline_dict(p) for p in pipelines]

    def create_pipeline(
        self,
        pipeline_name: str,
        ci_tool: str,
        repo_url: str = '',
        branch: str = 'main',
        project_id: int | None = None,
        config: dict[str, Any] | None = None,
    ) -> DevOpsPipeline:
        pipeline = DevOpsPipeline(
            project_id=project_id,
            pipeline_name=pipeline_name,
            ci_tool=ci_tool,
            repo_url=repo_url,
            branch=branch,
            config_json=json.dumps(config or {}),
            pipeline_status='IDLE',
        )
        self.db.add(pipeline)
        self.db.commit()
        self.db.refresh(pipeline)
        return pipeline

    def get_pipeline_status(self, pipeline_id: int) -> dict[str, Any]:
        pipeline = self.db.query(DevOpsPipeline).filter_by(id=pipeline_id).first()
        if not pipeline:
            return {'error': 'Pipeline not found'}
        return {
            **self._pipeline_dict(pipeline),
            'meta': _TOOL_META.get(pipeline.ci_tool, {}),
        }

    def trigger_pipeline(self, pipeline_id: int) -> dict[str, Any]:
        pipeline = self.db.query(DevOpsPipeline).filter_by(id=pipeline_id).first()
        if not pipeline:
            return {'error': 'Pipeline not found'}
        pipeline.pipeline_status = 'RUNNING'
        pipeline.last_triggered_at = datetime.utcnow()
        self.db.commit()
        return {
            'pipeline_id': pipeline_id,
            'status': 'RUNNING',
            'triggered_at': pipeline.last_triggered_at.isoformat(),
        }

    def complete_pipeline(self, pipeline_id: int, success: bool = True, duration_ms: int = 0) -> dict[str, Any]:
        pipeline = self.db.query(DevOpsPipeline).filter_by(id=pipeline_id).first()
        if not pipeline:
            return {'error': 'Pipeline not found'}
        pipeline.pipeline_status = 'SUCCESS' if success else 'FAILED'
        pipeline.last_run_duration_ms = duration_ms
        self.db.commit()
        return {'pipeline_id': pipeline_id, 'status': pipeline.pipeline_status}

    def get_supported_tools(self) -> list[dict[str, Any]]:
        return [
            {
                'ci_tool': tool,
                'icon': meta['icon'],
                'documentation_url': meta['docs'],
                'connected': self.db.query(DevOpsPipeline).filter_by(ci_tool=tool).count() > 0,
            }
            for tool, meta in _TOOL_META.items()
        ]

    def delete_pipeline(self, pipeline_id: int) -> dict[str, Any]:
        pipeline = self.db.query(DevOpsPipeline).filter_by(id=pipeline_id).first()
        if not pipeline:
            return {'error': 'Pipeline not found'}
        self.db.delete(pipeline)
        self.db.commit()
        return {'id': pipeline_id, 'status': 'DELETED'}

    def _pipeline_dict(self, p: DevOpsPipeline) -> dict[str, Any]:
        return {
            'id': p.id,
            'pipeline_name': p.pipeline_name,
            'ci_tool': p.ci_tool,
            'repo_url': p.repo_url,
            'branch': p.branch,
            'pipeline_status': p.pipeline_status,
            'is_active': p.is_active,
            'config': json.loads(p.config_json),
            'last_triggered_at': p.last_triggered_at.isoformat() if p.last_triggered_at else None,
            'last_run_duration_ms': p.last_run_duration_ms,
            'created_at': p.created_at.isoformat(),
        }
