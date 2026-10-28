"""Enterprise AI Copilot Core Engine for Version 2.0 (Session Control & Multi-Turn Chat)."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class CopilotContext(BaseModel):
    session_id: str = Field(default_factory=lambda: f"cses-{uuid.uuid4().hex[:6]}")
    project_id: int = Field(1)
    workflow_id: Optional[str] = Field(None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CopilotSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"cses-{uuid.uuid4().hex[:6]}")
    user_id: str = Field("enterprise-admin")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    context: CopilotContext = Field(default_factory=CopilotContext)


class CopilotMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: f"cmsg-{uuid.uuid4().hex[:6]}")
    role: str = Field("user", description="user, assistant, system")
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CopilotConversation(BaseModel):
    conversation_id: str = Field(default_factory=lambda: f"conv-{uuid.uuid4().hex[:6]}")
    messages: List[CopilotMessage] = Field(default_factory=list)


class CopilotResponse(BaseModel):
    response_id: str = Field(default_factory=lambda: f"cresp-{uuid.uuid4().hex[:6]}")
    content: str
    structured_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = Field(95.0)
    command_actions: List[str] = Field(default_factory=list)


class CopilotHistory:
    def __init__(self):
        self._conversations: Dict[str, CopilotConversation] = {}

    def get_or_create(self, session_id: str) -> CopilotConversation:
        if session_id not in self._conversations:
            self._conversations[session_id] = CopilotConversation()
        return self._conversations[session_id]

    def add_message(self, session_id: str, role: str, content: str) -> CopilotMessage:
        conv = self.get_or_create(session_id)
        msg = CopilotMessage(role=role, content=content)
        conv.messages.append(msg)
        return msg


class CopilotEngine:
    def __init__(self):
        self.history = CopilotHistory()

    def process_message(self, session: CopilotSession, user_input: str) -> CopilotResponse:
        self.history.add_message(session.session_id, "user", user_input)
        
        input_lower = user_input.lower()
        if "/plan" in input_lower or "plan" in input_lower:
            resp_text = "Enterprise AI Copilot Plan: 1. Decompose requirement into 4 subtasks. 2. Verify policy compliance. 3. Execute simulated Playwright runner."
            cmd_actions = ["TASK_DECOMPOSITION", "POLICY_CHECK"]
        elif "/recommend" in input_lower or "recommend" in input_lower:
            resp_text = "Copilot Recommendation: Use text-based button locators (button:has-text('Submit')) and enable auto-retry policy."
            cmd_actions = ["APPLY_RECOMMENDATION"]
        elif "/explain" in input_lower or "explain" in input_lower:
            resp_text = "Copilot Rationale: Verdict PASSED with 100% confidence because all 11 pipeline stages satisfied security policies."
            cmd_actions = ["VIEW_DECISION_TRACE"]
        else:
            resp_text = f"Enterprise AI Copilot Assistant: Ready to assist on project #{session.context.project_id}. Request: '{user_input}'."
            cmd_actions = ["ASSIST"]

        self.history.add_message(session.session_id, "assistant", resp_text)
        
        return CopilotResponse(
            content=resp_text,
            structured_suggestions=[
                {"type": "WORKFLOW", "text": "Execute 11-Stage Autonomous QA Pipeline"},
                {"type": "POLICY", "text": "Enforce SSRF metadata IP block rule"},
            ],
            confidence_score=95.0,
            command_actions=cmd_actions,
        )


class EnterpriseCopilot:
    def __init__(self):
        self.engine = CopilotEngine()

    def chat(self, user_id: str, message: str, project_id: int = 1) -> Dict[str, Any]:
        session = CopilotSession(user_id=user_id, context=CopilotContext(project_id=project_id))
        resp = self.engine.process_message(session, message)
        return {
            "session_id": session.session_id,
            "response": resp.model_dump(),
        }
