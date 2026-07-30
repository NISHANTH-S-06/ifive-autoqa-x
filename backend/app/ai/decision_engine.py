from typing import Dict, Any
from app.ai.schemas import ExecutionFailure, DecisionResponse

class AIDecisionEngine:
    """
    Analyzes execution results, handles unexpected UI states, and decides on the next actions dynamically.
    """
    def __init__(self):
        pass

    def decide_next_action(self, failure_data: ExecutionFailure) -> Dict[str, Any]:
        """
        Evaluate the failure and decide whether to HEAL, ABORT, or CONTINUE.
        """
        error_msg = failure_data.error_message.lower()
        
        # Determine if the error is related to element location (candidate for healing)
        is_locator_error = any(kw in error_msg for kw in [
            'timeout', 
            'waiting for selector', 
            'element not found',
            'no node found',
            'not visible'
        ])
        
        # Determine if it's a hard assertion failure (likely a true bug)
        is_assertion_error = any(kw in error_msg for kw in [
            'expected',
            'assertion',
            'status 500',
            'network error'
        ])

        if is_locator_error and failure_data.selector:
            decision = "HEAL"
            reason = "Element locator failed or timed out. Attempting self-healing to find new selector."
            score = 90
        elif is_assertion_error:
            decision = "ABORT"
            reason = "A critical assertion or network error occurred. This is likely a true application bug."
            score = 95
        else:
            # Fallback or unknown errors might just abort
            decision = "ABORT"
            reason = "Unknown error type that cannot be healed."
            score = 70
            
        response = DecisionResponse(
            decision=decision,
            reason=reason,
            confidence_score=score
        )
        return response.model_dump()
