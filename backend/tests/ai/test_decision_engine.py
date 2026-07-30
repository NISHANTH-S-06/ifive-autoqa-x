from app.ai.decision_engine import AIDecisionEngine
from app.ai.schemas import ExecutionFailure

def test_decision_engine_heal():
    engine = AIDecisionEngine()
    failure = ExecutionFailure(
        step_number=1,
        action="CLICK",
        selector="#submit-btn",
        error_message="TimeoutError: waiting for selector '#submit-btn' failed"
    )
    decision = engine.decide_next_action(failure)
    
    assert decision["decision"] == "HEAL"
    assert decision["confidence_score"] == 90

def test_decision_engine_abort():
    engine = AIDecisionEngine()
    failure = ExecutionFailure(
        step_number=2,
        action="ASSERT_VISIBLE",
        error_message="AssertionError: expected 'Dashboard' but got 'Login'"
    )
    decision = engine.decide_next_action(failure)
    
    assert decision["decision"] == "ABORT"
    assert decision["confidence_score"] == 95
