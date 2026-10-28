"""Unified Knowledge Runtime Interface for Version 2.0."""
from typing import Dict, Any, List, Optional
from app.v2.memory import AgentMemory, SessionMemory, WorkflowMemory, ExecutionMemory
from app.v2.knowledge.reasoning import PatternMatcher, KnowledgeQueryEngine, ExecutionHistoryAnalyzer, SuggestionEngine


class KnowledgeRuntime:
    def __init__(self):
        self.agent_memory = AgentMemory("knowledge_runtime")
        self.session_memory = SessionMemory("knowledge_session")
        self.execution_memory = ExecutionMemory()
        
        self.query_engine = KnowledgeQueryEngine()
        self.pattern_matcher = PatternMatcher()
        self.history_analyzer = ExecutionHistoryAnalyzer()
        self.suggestion_engine = SuggestionEngine()

    def query_unified_knowledge(self, task_description: str) -> Dict[str, Any]:
        """Query unified knowledge interface combining patterns, memory, and history."""
        pattern_res = self.query_engine.query_knowledge(task_description)
        history_stats = self.history_analyzer.analyze_history(self.execution_memory.list_runs())
        
        return {
            "status": "success",
            "task_description": task_description,
            "matched_pattern": pattern_res,
            "history_statistics": history_stats,
            "suggestions": self.suggestion_engine.generate_suggestions({"failure_type": "none"}),
        }
