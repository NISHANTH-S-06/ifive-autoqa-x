import logging
from typing import Dict, Any

logger = logging.getLogger('autoqa.ai.execution_intelligence')

EXEC_ACTIONS = [
    'CONTINUE', 'RETRY', 'HEAL_LOCATOR', 'REFRESH', 'RE_LOGIN',
    'SKIP', 'ROLLBACK', 'RESTART_BROWSER', 'CHANGE_BROWSER',
    'REDUCE_TIMEOUT', 'INCREASE_TIMEOUT', 'PARALLELIZE',
    'SERIALIZE', 'PAUSE', 'RESUME', 'ABORT'
]

class AIExecutionIntelligence:
    """
    Module 4: AI Execution Intelligence
    Continuously decides runtime step actions based on execution confidence scores.
    """

    def evaluate_step_execution(self, step_context: Dict[str, Any]) -> Dict[str, Any]:
        error_msg = step_context.get('error_message', '').lower()
        retry_count = step_context.get('retry_count', 0)
        confidence = step_context.get('confidence_score', 0.90)

        if not error_msg:
            action = 'CONTINUE'
            reason = 'Step executed cleanly without errors.'
        elif 'timeout' in error_msg and retry_count == 0:
            action = 'INCREASE_TIMEOUT'
            reason = 'DOM element render delayed; dynamically scaling timeout duration.'
        elif 'element not found' in error_msg or 'selector' in error_msg:
            action = 'HEAL_LOCATOR'
            reason = 'Selector DOM drift detected; triggering AI locator healing engine.'
        elif '401' in error_msg or 'session expired' in error_msg:
            action = 'RE_LOGIN'
            reason = 'Session token invalidated during run; executing automatic auth re-login.'
        elif retry_count > 2:
            action = 'ABORT'
            reason = 'Exceeded retry threshold; aborting step execution to avoid cascading failures.'
        else:
            action = 'RETRY'
            reason = 'Transient execution failure detected; re-attempting step.'

        return {
            'recommended_action': action,
            'reason': reason,
            'confidence_score': confidence,
            'allowed_actions': EXEC_ACTIONS
        }
