"""Distributed Agent Cluster Manager for Version 3.0 Platform."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ClusterNode(BaseModel):
    node_id: str = Field(default_factory=lambda: f"node-{uuid.uuid4().hex[:6]}")
    hostname: str = Field("cluster-worker-01")
    ip_address: str = Field("10.0.1.15")
    role: str = Field("WORKER", description="LEADER, WORKER")
    status: str = Field("ONLINE", description="ONLINE, BUSY, UNHEALTHY, OFFLINE")
    capacity_slots: int = Field(10)
    active_jobs: int = Field(0)
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentNode(BaseModel):
    agent_id: str
    node_id: str
    capabilities: List[str] = Field(default_factory=list)
    status: str = Field("READY")


class NodeRegistry:
    def __init__(self):
        self._nodes: Dict[str, ClusterNode] = {}

    def register_node(self, node: ClusterNode) -> None:
        self._nodes[node.node_id] = node

    def get_node(self, node_id: str) -> Optional[ClusterNode]:
        return self._nodes.get(node_id)

    def list_nodes(self) -> List[ClusterNode]:
        return list(self._nodes.values())


class HeartbeatManager:
    def process_heartbeat(self, node: ClusterNode) -> None:
        node.last_heartbeat = datetime.now(timezone.utc)
        node.status = "ONLINE"


class LeaderElection:
    def elect_leader(self, nodes: List[ClusterNode]) -> Optional[ClusterNode]:
        online = [n for n in nodes if n.status == "ONLINE"]
        if not online:
            return None
        leader = online[0]
        leader.role = "LEADER"
        for n in online[1:]:
            n.role = "WORKER"
        return leader


class ClusterHealthMonitor:
    def check_health(self, nodes: List[ClusterNode]) -> Dict[str, Any]:
        total = len(nodes)
        online = sum(1 for n in nodes if n.status == "ONLINE")
        return {
            "total_nodes": total,
            "online_nodes": online,
            "cluster_status": "HEALTHY" if online > 0 else "UNHEALTHY",
        }


class ClusterManager:
    def __init__(self):
        self.registry = NodeRegistry()
        self.heartbeat_mgr = HeartbeatManager()
        self.election = LeaderElection()
        self.health_monitor = ClusterHealthMonitor()

        # Seed default cluster nodes
        n1 = ClusterNode(node_id="node-leader-01", hostname="leader-01", role="LEADER")
        n2 = ClusterNode(node_id="node-worker-01", hostname="worker-01", role="WORKER")
        n3 = ClusterNode(node_id="node-worker-02", hostname="worker-02", role="WORKER")
        self.registry.register_node(n1)
        self.registry.register_node(n2)
        self.registry.register_node(n3)

    def get_cluster_overview(self) -> Dict[str, Any]:
        nodes = self.registry.list_nodes()
        leader = self.election.elect_leader(nodes)
        health = self.health_monitor.check_health(nodes)
        return {
            "health": health,
            "leader_node_id": leader.node_id if leader else None,
            "nodes": [n.model_dump() for n in nodes],
        }
