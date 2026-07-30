from app.ai.self_healing import SelfHealingEngine
from app.ai.schemas import ExecutionFailure

def test_self_healing_exact_text():
    engine = SelfHealingEngine()
    
    current_dom = {
        "buttons": [
            {"tag": "button", "text": "Submit", "id": "new-submit-id"},
            {"tag": "button", "text": "Cancel"}
        ]
    }
    
    failure = ExecutionFailure(
        step_number=1,
        action="CLICK",
        selector="button:has-text(\"Submit\")",
        error_message="TimeoutError",
        current_dom=current_dom
    )
    
    result = engine.heal_test_step(failure)
    
    assert result["success"] is True
    assert result["strategy_used"] == "EXACT_TEXT_MATCH"
    assert result["healed_selector"] == "#new-submit-id"

def test_self_healing_partial_id():
    engine = SelfHealingEngine()
    
    current_dom = {
        "inputs": [
            {"tag": "input", "id": "username-v2-field"}
        ]
    }
    
    failure = ExecutionFailure(
        step_number=1,
        action="FILL",
        selector="#username",
        error_message="TimeoutError",
        current_dom=current_dom
    )
    
    result = engine.heal_test_step(failure)
    
    assert result["success"] is True
    assert result["strategy_used"] == "PARTIAL_ID_MATCH"
    assert result["healed_selector"] == "#username-v2-field"
