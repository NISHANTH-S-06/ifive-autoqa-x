"""Multi-Agent Collaboration, Voting & Consensus Manager for Version 2.0."""
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AgentVote(BaseModel):
    vote_id: str = Field(default_factory=lambda: f"vote-{uuid.uuid4().hex[:6]}")
    agent_id: str
    option_id: str
    vote_weight: float = Field(1.0, description="Agent voting weight")
    rationale: str = Field("", description="Reason for vote")


class ConsensusResult(BaseModel):
    consensus_id: str = Field(default_factory=lambda: f"con-{uuid.uuid4().hex[:6]}")
    winning_option_id: Optional[str] = Field(None)
    consensus_reached: bool = Field(False)
    vote_summary: Dict[str, float] = Field(default_factory=dict)
    escalated_to_admin: bool = Field(False)
    conflict_detected: bool = Field(False)


class ConflictResolver:
    def resolve_tie(self, votes: List[AgentVote], priority_overrides: Dict[str, float]) -> str:

        totals: Dict[str, float] = {}
        for v in votes:
            agent_weight = priority_overrides.get(v.agent_id, v.vote_weight)
            totals[v.option_id] = totals.get(v.option_id, 0.0) + agent_weight

        sorted_options = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        return sorted_options[0][0] if sorted_options else ""


class ConsensusManager:
    def __init__(self, threshold: float = 0.50):
        self.threshold = threshold
        self.conflict_resolver = ConflictResolver()

    def evaluate_consensus(
        self,
        votes: List[AgentVote],
        priority_overrides: Optional[Dict[str, float]] = None,
    ) -> ConsensusResult:
        if not votes:
            return ConsensusResult(consensus_reached=False, escalated_to_admin=True)

        overrides = priority_overrides or {}
        totals: Dict[str, float] = {}
        total_weight = 0.0

        for v in votes:
            w = overrides.get(v.agent_id, v.vote_weight)
            totals[v.option_id] = totals.get(v.option_id, 0.0) + w
            total_weight += w

        if total_weight == 0:
            return ConsensusResult(consensus_reached=False, escalated_to_admin=True)

        winning_option = max(totals, key=totals.get)
        winning_weight = totals[winning_option]
        ratio = winning_weight / total_weight

        consensus_reached = ratio >= self.threshold
        conflict_detected = len(totals) > 1 and ratio < 0.60

        return ConsensusResult(
            winning_option_id=winning_option,
            consensus_reached=consensus_reached,
            vote_summary=totals,
            escalated_to_admin=not consensus_reached,
            conflict_detected=conflict_detected,
        )


class CollaborationManager:
    def __init__(self):
        self.consensus_manager = ConsensusManager()

    def run_collaboration_session(
        self,
        agents_votes: List[AgentVote],
        priority_overrides: Optional[Dict[str, float]] = None,
    ) -> ConsensusResult:
        return self.consensus_manager.evaluate_consensus(agents_votes, priority_overrides)
