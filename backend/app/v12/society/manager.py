"""Global AI Society Module — Version 12.0 Autonomous Digital Civilization Platform.

Implements:
  - CommunityManager      : Manages AI agent guilds, specialized communities & membership
  - CollaborationNetwork  : Manages inter-community communication graph & task delegation channels
  - AgentSociety          : Top-level coordinator for the Global AI Society & agent interaction graph
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class AgentProfile(BaseModel):
    agent_id: str = Field(default_factory=lambda: f"agent-{uuid.uuid4().hex[:8]}")
    name: str
    role: str = Field("AUTONOMOUS_SPECIALIST")  # ARCHITECT | CODE_GEN | TESTER | SECURITY | GUARDIAN
    community_id: str
    reputation_score: float = Field(0.98, ge=0.0, le=1.0)
    status: str = Field("ACTIVE")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

class AICommunity(BaseModel):
    community_id: str = Field(default_factory=lambda: f"comm-{uuid.uuid4().hex[:8]}")
    name: str
    specialization: str
    member_count: int = Field(0)
    lead_agent_id: Optional[str] = None
    status: str = Field("ACTIVE")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

class InterCommunityLink(BaseModel):
    link_id: str = Field(default_factory=lambda: f"link-{uuid.uuid4().hex[:8]}")
    source_community_id: str
    target_community_id: str
    collaboration_topic: str
    bandwidth_capacity: float = Field(100.0)  # Mbps / channel capacity
    status: str = Field("ESTABLISHED")

# ---------------------------------------------------------------------------
# Community Manager
# ---------------------------------------------------------------------------

class CommunityManager:
    """Manages specialized AI guilds, agent memberships, and community roles."""

    def __init__(self) -> None:
        self._communities: Dict[str, AICommunity] = {}
        self._agents: Dict[str, AgentProfile] = {}

        # Pre-seed specialized AI guilds
        c1 = self.create_community("Universal Engineering Guild", "SOFTWARE_ENGINEERING")
        c2 = self.create_community("Global Quality & Testing Guild", "QA_AUTOMATION")
        c3 = self.create_community("Zero-Trust Security Guild", "SECURITY_AUDIT")
        c4 = self.create_community("Autonomous Governance Guild", "GOVERNANCE")

        # Register lead agents
        self.register_agent("Sentinel Prime", "ARCHITECT", c1.community_id)
        self.register_agent("TestMaster AI", "TESTER", c2.community_id)
        self.register_agent("Aegis Shield", "SECURITY", c3.community_id)
        self.register_agent("Lex AI", "GUARDIAN", c4.community_id)

    def create_community(self, name: str, specialization: str) -> AICommunity:
        comm = AICommunity(name=name, specialization=specialization)
        self._communities[comm.community_id] = comm
        return comm

    def register_agent(self, name: str, role: str, community_id: str) -> AgentProfile:
        agent = AgentProfile(name=name, role=role, community_id=community_id)
        self._agents[agent.agent_id] = agent
        if community_id in self._communities:
            self._communities[community_id].member_count += 1
            if not self._communities[community_id].lead_agent_id:
                self._communities[community_id].lead_agent_id = agent.agent_id
        return agent

    def get_community(self, community_id: str) -> Optional[AICommunity]:
        return self._communities.get(community_id)

    def list_communities(self) -> List[AICommunity]:
        return list(self._communities.values())

    def list_agents(self, community_id: Optional[str] = None) -> List[AgentProfile]:
        if community_id:
            return [a for a in self._agents.values() if a.community_id == community_id]
        return list(self._agents.values())

# ---------------------------------------------------------------------------
# Collaboration Network
# ---------------------------------------------------------------------------

class CollaborationNetwork:
    """Manages inter-community communication topology and collaboration channels."""

    def __init__(self) -> None:
        self._links: Dict[str, InterCommunityLink] = {}

    def establish_link(
        self, source_community_id: str, target_community_id: str, collaboration_topic: str
    ) -> InterCommunityLink:
        link = InterCommunityLink(
            source_community_id=source_community_id,
            target_community_id=target_community_id,
            collaboration_topic=collaboration_topic,
        )
        self._links[link.link_id] = link
        return link

    def list_links(self) -> List[InterCommunityLink]:
        return list(self._links.values())

    def get_network_topology(self) -> Dict[str, Any]:
        return {
            "total_inter_community_links": len(self._links),
            "topology_type": "HIGHLY_CONNECTED_FEDERATED_GRAPH",
            "cross_guild_bandwidth_utilization_pct": 18.5,
        }

# ---------------------------------------------------------------------------
# Agent Society
# ---------------------------------------------------------------------------

class AgentSociety:
    """Top-level coordinator for the Global AI Society."""

    def __init__(self) -> None:
        self.community_manager = CommunityManager()
        self.collaboration_network = CollaborationNetwork()

        # Establish default inter-guild links
        comms = self.community_manager.list_communities()
        if len(comms) >= 2:
            self.collaboration_network.establish_link(comms[0].community_id, comms[1].community_id, "Automated QA Verification")
            self.collaboration_network.establish_link(comms[1].community_id, comms[2].community_id, "Security Audit Pipeline")

    def get_society_summary(self) -> Dict[str, Any]:
        comms = self.community_manager.list_communities()
        agents = self.community_manager.list_agents()
        return {
            "total_communities": len(comms),
            "registered_lead_agents": len(agents),
            "society_status": "FLOURISHING",
            "collaboration_graph": self.collaboration_network.get_network_topology(),
            "avg_agent_reputation": round(sum(a.reputation_score for a in agents) / max(len(agents), 1), 4),
        }
