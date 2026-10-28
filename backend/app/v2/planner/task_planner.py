"""Task Planner and Dependency Resolver for Version 2.0."""
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class TaskNode(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task-{uuid.uuid4().hex[:6]}")
    name: str
    priority: int = Field(1, description="Priority rank (lower = higher priority)")
    estimated_cost_ms: float = Field(15.0, description="Estimated execution cost in milliseconds")
    dependencies: List[str] = Field(default_factory=list, description="IDs of prerequisite tasks")


class TaskGraph:
    def __init__(self, nodes: Optional[List[TaskNode]] = None):
        self._nodes: Dict[str, TaskNode] = {n.task_id: n for n in (nodes or [])}

    def add_node(self, node: TaskNode) -> None:
        self._nodes[node.task_id] = node

    def get_node(self, task_id: str) -> Optional[TaskNode]:
        return self._nodes.get(task_id)

    def list_nodes(self) -> List[TaskNode]:
        return list(self._nodes.values())


class DependencyResolver:
    def resolve_topological_order(self, graph: TaskGraph) -> List[TaskNode]:
        nodes = graph.list_nodes()
        visited = set()
        order: List[TaskNode] = []

        def visit(node: TaskNode):
            if node.task_id not in visited:
                visited.add(node.task_id)
                for dep_id in node.dependencies:
                    dep_node = graph.get_node(dep_id)
                    if dep_node and dep_node.task_id not in visited:
                        visit(dep_node)
                order.append(node)

        for n in nodes:
            visit(n)

        return order


class PriorityResolver:
    def sort_by_priority(self, tasks: List[TaskNode]) -> List[TaskNode]:
        return sorted(tasks, key=lambda t: (t.priority, t.estimated_cost_ms))


class ExecutionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"plan-{uuid.uuid4().hex[:6]}")
    ordered_tasks: List[TaskNode] = Field(default_factory=list)
    total_estimated_cost_ms: float = Field(0.0)
    dependency_levels: List[List[str]] = Field(default_factory=list)


class TaskPlanner:
    def __init__(self):
        self.dep_resolver = DependencyResolver()
        self.prio_resolver = PriorityResolver()

    def split_work(self, requirement: str) -> List[TaskNode]:
        """Split requirement into structured task nodes."""
        return [
            TaskNode(task_id="t-nav", name="Navigate to Application Target", priority=1, estimated_cost_ms=10.0),
            TaskNode(task_id="t-auth", name="Authenticate Operator Session", priority=2, estimated_cost_ms=15.0, dependencies=["t-nav"]),
            TaskNode(task_id="t-fill", name="Fill Form Fields & Validate Constraints", priority=3, estimated_cost_ms=20.0, dependencies=["t-auth"]),
            TaskNode(task_id="t-submit", name="Submit Record & Confirm State Persistence", priority=4, estimated_cost_ms=15.0, dependencies=["t-fill"]),
        ]

    def create_optimized_plan(self, nodes: List[TaskNode]) -> ExecutionPlan:
        graph = TaskGraph(nodes)
        topo_ordered = self.dep_resolver.resolve_topological_order(graph)
        prio_ordered = self.prio_resolver.sort_by_priority(topo_ordered)

        total_cost = sum(t.estimated_cost_ms for t in prio_ordered)
        dep_levels = [[t.task_id] for t in prio_ordered]

        return ExecutionPlan(
            ordered_tasks=prio_ordered,
            total_estimated_cost_ms=total_cost,
            dependency_levels=dep_levels,
        )
