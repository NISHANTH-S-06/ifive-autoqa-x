"""Prompt Intelligence Framework for Version 2.0 (Reusable Enterprise Prompts)."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class PromptVersion(BaseModel):
    prompt_id: str = Field(default_factory=lambda: f"prm-{uuid.uuid4().hex[:6]}")
    name: str
    version: str = Field("1.0.0")
    template_str: str
    variables: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromptBuilder:
    def render(self, prompt_version: PromptVersion, values: Dict[str, Any]) -> str:
        res = prompt_version.template_str
        for var in prompt_version.variables:
            val = str(values.get(var, f"{{{var}}}"))
            res = res.replace(f"{{{var}}}", val)
        return res


class PromptLibrary:
    def __init__(self):
        self._prompts: Dict[str, PromptVersion] = {
            "task_breakdown": PromptVersion(
                name="Task Breakdown Prompt",
                template_str="Decompose requirement '{requirement}' into structured subtasks for project #{project_id}.",
                variables=["requirement", "project_id"],
            ),
            "decision_evaluation": PromptVersion(
                name="Decision Evaluation Prompt",
                template_str="Evaluate options '{options}' against policy '{policy_name}'.",
                variables=["options", "policy_name"],
            ),
        }
        self.builder = PromptBuilder()

    def get_prompt(self, name: str) -> Optional[PromptVersion]:
        return self._prompts.get(name)

    def render_prompt(self, name: str, values: Dict[str, Any]) -> str:
        prm = self.get_prompt(name)
        if not prm:
            return f"Prompt '{name}' not found."
        return self.builder.render(prm, values)

    def list_prompts(self) -> List[Dict[str, Any]]:
        return [p.model_dump() for p in self._prompts.values()]
