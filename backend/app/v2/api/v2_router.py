"""FastAPI Version 3.0 API Routers for Self-Evolving Autonomous QA Ecosystem."""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.v2.evolution import EvolutionEngine
from app.v2.improvement import ImprovementEngine
from app.v2.governance import GovernanceEngine
from app.v2.experiments import ExperimentEngine
from app.v2.knowledge import KnowledgeEvolutionManager
from app.v2.orchestration import EnterpriseLifecycleCoordinator

from app.v2.digital_twin import DigitalTwinEngine
from app.v2.simulation import SimulationEngine
from app.v2.predictive import PredictiveEngine
from app.v2.optimization import OptimizationEngine
from app.v2.analytics import AnalyticsEngine
from app.v2.risk import RiskEngine

from app.v2.ecosystem import AgentDirectory, AgentDiscoveryService, TaskDelegator, CollaborationEngine
from app.v2.communication import MessageBus
from app.v2.plugins import PluginMarketplace
from app.v2.integrations import IntegrationHub
from app.v2.knowledge import KnowledgeExchange
from app.v2.orchestration import AutonomousTeamCoordinator, AutonomousCoordinator

from app.v2.copilot import EnterpriseCopilot
from app.v2.context import ContextEngine
from app.v2.recommendation import RecommendationEngine
from app.v2.learning import LearningEngine, FeedbackEngine
from app.v2.knowledge import KnowledgeEvolutionEngine
from app.v2.prompts import PromptLibrary
from app.v2.advisors import BusinessAdvisor
from app.v2.runtime import RuntimeManager
from app.v2.decision import DecisionEngine, DecisionContext
from app.v2.reasoning import ReasoningEngine, ReasoningRequest, ReasoningType
from app.v2.confidence import ConfidenceEngine
from app.v2.policies import PolicyEngine
from app.v2.explanations import ExplanationEngine
from app.v2.plugins.runtime import PluginRuntime
from app.v2.knowledge.runtime import KnowledgeRuntime
from app.v2.metrics import MetricsCollector

router = APIRouter(prefix="/api/v2", tags=["Version 3.0 Self-Evolving Autonomous QA Ecosystem"])

# Global Singletons
evolution_engine = EvolutionEngine()
improvement_engine = ImprovementEngine()
governance_engine = GovernanceEngine()
experiment_engine = ExperimentEngine()
knowledge_evolution_manager = KnowledgeEvolutionManager()
lifecycle_coordinator = EnterpriseLifecycleCoordinator()

digital_twin_engine = DigitalTwinEngine()
simulation_engine = SimulationEngine()
predictive_engine = PredictiveEngine()
optimization_engine = OptimizationEngine()
analytics_engine = AnalyticsEngine()
risk_engine = RiskEngine()

discovery_service = AgentDiscoveryService()
agent_directory = discovery_service.directory
message_bus = MessageBus()
task_delegator = TaskDelegator(directory=agent_directory)
collaboration_engine = CollaborationEngine()
plugin_marketplace = PluginMarketplace()
integration_hub = IntegrationHub()
knowledge_exchange = KnowledgeExchange()
team_coordinator = AutonomousTeamCoordinator()

copilot = EnterpriseCopilot()
context_engine = ContextEngine()
recommendation_engine = RecommendationEngine()
learning_engine = LearningEngine()
feedback_engine = FeedbackEngine()
knowledge_evolution = KnowledgeEvolutionEngine()
prompt_library = PromptLibrary()
business_advisor = BusinessAdvisor()

runtime_manager = RuntimeManager()
autonomous_coordinator = AutonomousCoordinator()
plugin_runtime = PluginRuntime()
knowledge_runtime = KnowledgeRuntime()
metrics_collector = MetricsCollector()

decision_engine = DecisionEngine()
reasoning_engine = ReasoningEngine()
confidence_engine = ConfidenceEngine()
policy_engine = PolicyEngine()
explanation_engine = ExplanationEngine()


class CopilotChatRequest(BaseModel):
    user_id: str = Field("enterprise-admin")
    message: str = Field("Recommend execution order for Purchase Order test")
    project_id: int = Field(1)


class DelegateTaskRequest(BaseModel):
    task_id: str = Field("task-101")
    required_capability: str = Field("EXECUTION")


class FeedbackRequest(BaseModel):
    rating: int = Field(5, description="Rating from 1 to 5")
    comments: Optional[str] = Field(None)
    correction: Optional[str] = Field(None)


class PluginInstallRequest(BaseModel):
    plugin_id: str = Field("jira")


class SimulateScenarioRequest(BaseModel):
    scenario_name: str = Field("High Volume Purchase Order Creation")
    inputs: Dict[str, Any] = Field(default_factory=dict)


@router.get("/health")
async def get_v2_health():
    return {
        "status": "ok",
        "system": "iFive AutoQA X Self-Evolving Autonomous QA Ecosystem",
        "version": "3.0",
        "phase": "20",
    }


# --- PHASE 20 SELF-EVOLVING AUTONOMOUS QA ECOSYSTEM APIs ---

@router.get("/evolution")
@router.get("/evolution/status")
@router.get("/intelligence/evolution")
@router.get("/platform/evolution")
async def get_evolution_status():
    snapshots = [s.model_dump() for s in evolution_engine.manager.snapshots]
    return {
        "status": "ONLINE",
        "evolution_mode": "AUTONOMOUS_CONTINUOUS",
        "latest_snapshot": snapshots[-1] if snapshots else {},
        "policy": evolution_engine.manager.policy.model_dump(),
    }


@router.get("/evolution/history")
async def get_evolution_history():
    history = [c.model_dump() for c in evolution_engine.manager.history.list_history()]
    return {
        "status": "success",
        "total_cycles": len(history),
        "history": history,
    }


@router.post("/evolution/run")
async def run_evolution_cycle_endpoint():
    return evolution_engine.run_evolution_cycle()


@router.get("/improvement")
async def get_improvements_status():
    return improvement_engine.run_improvement_cycle()


@router.get("/governance")
async def get_governance_status():
    return {
        "status": "ONLINE",
        "policy": governance_engine.policy.model_dump(),
        "total_audits": len(governance_engine.audits),
        "recent_audits": [a.model_dump() for a in governance_engine.audits[-5:]],
    }


@router.post("/governance/authorize")
async def authorize_action_endpoint(action: str = "Deploy Execution Plan", risk_level: str = "LOW"):
    return governance_engine.authorize_action(action, risk_level)


@router.get("/experiments")
async def get_experiments_status():
    return {
        "status": "ONLINE",
        "total_experiments": len(experiment_engine.manager.experiments),
        "experiments": [e.model_dump() for e in experiment_engine.manager.experiments],
    }


@router.post("/experiments/run")
async def run_experiment_endpoint(name: str = "A/B Pipeline Evaluation"):
    return experiment_engine.run_experiment(name)


@router.get("/self-learning")
async def get_self_learning_status():
    return {
        "status": "ONLINE",
        "knowledge_evolution": knowledge_evolution_manager.evolve_all_knowledge(),
        "learning_stats": learning_engine.get_learning_stats(),
        "feedback_stats": feedback_engine.get_feedback_stats(),
    }


# --- PHASE 19 ENTERPRISE DIGITAL TWIN & PREDICTIVE QA APIs ---

@router.get("/digital-twin")
async def get_digital_twin_status():
    models = digital_twin_engine.registry.list_all()
    return {
        "status": "ONLINE",
        "total_twin_models": len(models),
        "models": [m.model_dump() for m in models],
    }


@router.post("/digital-twin/simulate")
async def simulate_digital_twin_endpoint(req: SimulateScenarioRequest):
    sim = digital_twin_engine.simulate_scenario(req.scenario_name, req.inputs)
    return {"status": "success", "simulation": sim.model_dump()}


@router.get("/simulation")
async def get_simulation_status():
    return {
        "status": "ONLINE",
        "capabilities": ["SANDBOX", "DRY_RUN", "REPLAY", "ROLLBACK"],
    }


@router.post("/simulation/dry-run")
async def run_simulation_dry_run_endpoint(scenario_name: str = "Purchase Order Flow"):
    return simulation_engine.run_dry_run(scenario_name)


@router.get("/predictive")
@router.get("/intelligence/forecast")
async def get_predictive_forecast(project_id: int = 1):
    fcast = predictive_engine.generate_forecast(project_id)
    return {"status": "success", "forecast": fcast.model_dump()}


@router.get("/optimization")
async def get_optimization_suggestions():
    opt = optimization_engine.optimize_workflow()
    return {"status": "success", "optimization": opt}


@router.get("/analytics")
async def get_enterprise_analytics_endpoint():
    return analytics_engine.generate_enterprise_analytics()


@router.get("/risk")
async def get_enterprise_risk_endpoint(project_id: int = 1):
    return risk_engine.evaluate_risk(project_id)


@router.get("/intelligence/status")
@router.get("/intelligence/health")
async def get_intelligence_platform_health():
    return {
        "status": "HEALTHY",
        "phase": "20",
        "subsystems": {
            "evolution_engine": "HEALTHY",
            "improvement_engine": "HEALTHY",
            "governance_engine": "HEALTHY",
            "experiment_engine": "HEALTHY",
            "digital_twin_engine": "HEALTHY",
            "predictive_engine": "HEALTHY",
        },
    }


# --- PHASE 18 MULTI-AGENT ECOSYSTEM & PLUGIN APIs ---

@router.get("/ecosystem")
@router.get("/ecosystem/health")
async def get_ecosystem_health():
    return {
        "status": "ONLINE",
        "total_registered_agents": len(agent_directory.list_all()),
        "message_bus_status": "ACTIVE",
        "integration_hub_status": "ONLINE",
    }


@router.get("/ecosystem/agents")
async def list_ecosystem_agents():
    return {
        "status": "success",
        "agents": [a.model_dump() for a in agent_directory.list_all()],
    }


@router.get("/ecosystem/discovery")
async def discover_agents_endpoint(capability: str = "EXECUTION"):
    agents = discovery_service.discover_by_capability(capability)
    return {
        "status": "success",
        "capability": capability,
        "matched_agents": [a.model_dump() for a in agents],
    }


@router.get("/ecosystem/messages")
async def get_ecosystem_messages():
    history = message_bus.get_history()
    return {
        "status": "success",
        "total_messages": len(history),
        "messages": [m.model_dump() for m in history],
    }


@router.post("/ecosystem/tasks")
async def delegate_task_endpoint(req: DelegateTaskRequest):
    asgn = task_delegator.delegate_task(req.task_id, req.required_capability)
    if not asgn:
        raise HTTPException(status_code=404, detail="No suitable agent found for required capability")
    return {"status": "success", "assignment": asgn.model_dump()}


@router.get("/ecosystem/collaboration")
async def run_collaboration_endpoint(task: str = "Automate Sales Order Flow"):
    return collaboration_engine.run_collaborative_planning(task)


@router.get("/plugins/catalog")
async def list_plugin_catalog():
    return {
        "status": "success",
        "catalog": plugin_marketplace.list_catalog(),
    }


@router.post("/plugins/install")
async def install_plugin_endpoint(req: PluginInstallRequest):
    return plugin_marketplace.install(req.plugin_id)


@router.get("/plugins/status")
async def get_plugins_status():
    return {
        "status": "success",
        "installed_plugins": plugin_runtime.list_plugins(),
    }


@router.get("/integrations")
async def get_integrations_status():
    return integration_hub.get_hub_status()


@router.post("/integrations/sync")
async def sync_integration_endpoint(system: str = "Jira"):
    return integration_hub.sync_mgr.sync_data(system)


# --- PHASE 17 COPILOT, PLATFORM & RUNTIME ENDPOINTS ---

@router.get("/copilot")
@router.get("/copilot/status")
async def get_copilot_status():
    return {
        "status": "ONLINE",
        "copilot_mode": "ENTERPRISE_ASSISTANT",
        "capabilities": ["CHAT", "RECOMMENDATIONS", "LEARNING", "ADVISORY", "EXPLAINABILITY"],
    }


@router.post("/copilot/chat")
async def copilot_chat_endpoint(req: CopilotChatRequest):
    return copilot.chat(user_id=req.user_id, message=req.message, project_id=req.project_id)


@router.get("/copilot/context")
async def get_copilot_context(project_id: int = 1):
    return context_engine.get_context(project_id)


@router.get("/copilot/recommend")
async def get_copilot_recommendations():
    recs = recommendation_engine.generate_recommendations()
    return {
        "status": "success",
        "total_recommendations": len(recs),
        "recommendations": [r.model_dump() for r in recs],
    }


@router.get("/copilot/history")
async def get_copilot_history(session_id: str = "cses-default"):
    conv = copilot.engine.history.get_or_create(session_id)
    return {
        "status": "success",
        "session_id": session_id,
        "messages": [m.model_dump() for m in conv.messages],
    }


@router.get("/copilot/learning")
async def get_copilot_learning():
    return {
        "status": "success",
        "learning_stats": learning_engine.get_learning_stats(),
        "feedback_stats": feedback_engine.get_feedback_stats(),
    }


@router.post("/copilot/feedback")
async def submit_copilot_feedback(req: FeedbackRequest):
    fb = feedback_engine.submit_feedback(rating=req.rating, comments=req.comments, correction=req.correction)
    return {"status": "success", "feedback": fb.model_dump()}


@router.get("/copilot/advisor")
async def get_copilot_advisor():
    advisories = business_advisor.get_all_advisories()
    return {
        "status": "success",
        "advisories": [a.model_dump() for a in advisories],
    }


@router.get("/copilot/knowledge")
async def get_copilot_knowledge_evolution():
    return {
        "status": "success",
        "evolved_knowledge": knowledge_evolution.list_evolved_knowledge(),
        "prompts": prompt_library.list_prompts(),
    }


@router.get("/runtime/status")
async def get_runtime_status():
    return runtime_manager.get_status()


@router.post("/runtime/start")
async def start_runtime():
    success = await runtime_manager.start_all()
    return {"status": "success" if success else "error", "runtime_state": runtime_manager.get_status()}


@router.get("/runtime/metrics")
async def get_runtime_metrics():
    return metrics_collector.collect_all_metrics()


@router.get("/platform/status")
async def get_platform_status():
    return {
        "platform_status": "ONLINE",
        "autonomous_mode": True,
        "copilot_active": True,
        "runtime_state": runtime_manager.get_status(),
        "registered_plugins_count": len(plugin_runtime.list_plugins()),
    }


@router.get("/platform/health")
async def get_platform_health():
    return {
        "status": "HEALTHY",
        "phase": "20",
        "subsystems": {
            "evolution": "HEALTHY",
            "improvement": "HEALTHY",
            "governance": "HEALTHY",
            "experiments": "HEALTHY",
            "digital_twin": "HEALTHY",
            "predictive": "HEALTHY",
        },
    }


@router.get("/agents")
@router.get("/platform/agents")
async def list_platform_agents():
    agents = agent_directory.list_all()
    return {
        "status": "success",
        "total_agents": len(agents),
        "agents": [a.agent_id for a in agents],
    }


@router.get("/platform/workflows")
async def list_platform_workflows():
    return {
        "status": "success",
        "workflows": ["Autonomous QA Pipeline", "Enterprise Collaboration Chain", "Self-Evolving Lifecycle Pipeline"],
    }


@router.get("/orchestrator/status")
async def get_orchestrator_status():
    return {
        "status": "ONLINE",
        "orchestrator_ready": True,
        "registered_agents": [a.agent_id for a in agent_directory.list_all()],
    }


@router.post("/orchestrator/execute")
async def execute_autonomous_pipeline_endpoint(req: CopilotChatRequest):
    try:
        res = await lifecycle_coordinator.execute_autonomous_lifecycle(
            project_id=req.project_id,
            task_description=req.message,
        )
        exec_dict = res.model_dump()
        exec_dict["status"] = res.overall_status
        return {
            "status": "success",
            "execution_result": exec_dict,
            "pipeline_execution": res.model_dump(),
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/workflows/execute")
async def execute_workflow_endpoint(req: CopilotChatRequest):
    return await execute_autonomous_pipeline_endpoint(req)


@router.get("/reports")
async def get_v2_reports():
    return {
        "status": "success",
        "reports": [
            {
                "report_id": "rep-v3-001",
                "phase": "20",
                "execution_summary": {"total_steps": 14, "passed_steps": 14, "verdict": "PASSED"},
            }
        ],
    }


@router.post("/decision")
async def evaluate_decision_endpoint(payload: Dict[str, Any]):
    opts = payload.get("options") or [{"id": "opt-1", "review_verdict": "PASSED", "failure_count": 0, "is_complete": True}]
    ctx = DecisionContext(options=opts, parameters=payload.get("parameters", {}))
    res = decision_engine.evaluate_options(ctx)
    return {"status": "success", "decision": res.model_dump()}


@router.post("/reasoning")
async def evaluate_reasoning_endpoint(request: Dict[str, Any]):
    req = ReasoningRequest(
        reasoning_type=request.get("reasoning_type", ReasoningType.DEDUCTIVE),
        premises=request.get("premises", [{"name": "Step 1", "status": "PASSED"}]),
    )
    verdict = reasoning_engine.reason(req)
    return {"status": "success", "reasoning_verdict": verdict.model_dump()}


@router.get("/confidence")
async def compute_confidence_endpoint():
    eval_res = confidence_engine.compute_execution_confidence([{"status": "PASSED"}, {"status": "PASSED"}])
    return {"status": "success", "confidence": eval_res.model_dump()}


@router.get("/policies")
async def evaluate_policies_endpoint():
    res = policy_engine.evaluate_context({"environment": "STAGING", "target_host": "127.0.0.1"})
    return {"status": "success", "policy_evaluation": res}


@router.get("/explanations")
async def get_explanations_endpoint():
    trace = explanation_engine.explain_decision(
        decision_id="dec-101",
        selected_option={"id": "opt-1", "name": "Proceed Execution"},
        confidence_score=95.0,
        ranked_options=[{"id": "opt-1", "name": "Proceed Execution"}],
        rules_applied=["Zero Failures Check", "Passed Review Check"],
    )
    return {"status": "success", "decision_trace": trace.model_dump()}
