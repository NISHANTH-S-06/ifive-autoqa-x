import logging
from typing import Dict, Any, List

from app.ai.agents.agent_registry import AgentRegistry

logger = logging.getLogger('autoqa.ai.agents.orchestrator')

class AgentOrchestrator:
    """
    Master Agent Orchestrator:
    Coordinates multi-agent workflows, state transitions, and inter-agent messages.
    """

    def __init__(self):
        self.registry = AgentRegistry()

    def run_pipeline(self, pipeline_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Executing AI Multi-Agent pipeline: %s", pipeline_name)
        results = {}

        if pipeline_name == 'FULL_AUTONOMOUS_QA':
            # 1. Task Parsing
            task_res = self.registry.get_agent('task').execute(payload)
            results['task'] = task_res

            # 2. Context Building
            context_res = self.registry.get_agent('context').execute(payload)
            results['context'] = context_res

            # 3. Discovery & Module Mapping
            disc_res = self.registry.get_agent('discovery').execute(payload)
            results['discovery'] = disc_res

            # 4. Recommendation Generation
            rec_res = self.registry.get_agent('recommendation').execute(disc_res)
            results['recommendations'] = rec_res

            # 5. Planning
            plan_res = self.registry.get_agent('planning').execute({
                'context_data': context_res,
                'steps': payload.get('steps', []),
                'expected_flow': payload.get('expected_flow', ''),
                'acceptance_criteria': payload.get('acceptance_criteria', '')
            })
            results['planning'] = plan_res

            # 6. Learning & Memory Update
            learn_res = self.registry.get_agent('learning').execute(results)
            results['learning'] = learn_res

            # 7. Release Readiness Evaluation
            release_res = self.registry.get_agent('release').execute(results)
            results['release_verdict'] = release_res

        else:
            # Single agent fallback
            agent = self.registry.get_agent(pipeline_name)
            results[pipeline_name] = agent.execute(payload)

        return {
            'pipeline': pipeline_name,
            'status': 'SUCCESS',
            'agent_results': results
        }
