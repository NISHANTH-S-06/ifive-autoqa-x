from app.ai.validation_planner import ValidationPlanner

def test_validation_planner_navigate_click():
    planner = ValidationPlanner()
    context = {"url": "https://example.com"}
    steps = [
        {"step_number": 1, "action": "NAVIGATE"},
        {"step_number": 2, "action": "CLICK", "selector": "a.product-link"}
    ]
    
    plan = planner.plan_validations(context, steps, "", "Must meet accessibility")
    
    assert plan["plan_title"] == "Dynamic Execution Plan"
    assert len(plan["steps"]) == 2
    
    # Check NAVIGATE step
    assert plan["steps"][0]["step_number"] == 1
    validations_1 = plan["steps"][0]["validations"]
    assert "URL Validation" in validations_1
    assert "HTTP 200" in validations_1
    assert "Screenshot Capture" in validations_1
    assert "Accessibility Validation" in validations_1
    
    # Check CLICK step
    assert plan["steps"][1]["step_number"] == 2
    validations_2 = plan["steps"][1]["validations"]
    assert "Element Visible" in validations_2
    assert "Element Clickable" in validations_2
    assert "URL Changed" in validations_2
    assert "Accessibility Validation" in validations_2

def test_validation_planner_fill():
    planner = ValidationPlanner()
    steps = [
        {"step_number": 1, "action": "FILL", "selector": "input#name"}
    ]
    
    plan = planner.plan_validations({}, steps, "", "Performance testing required")
    validations = plan["steps"][0]["validations"]
    
    assert "Element Visible" in validations
    assert "Element Enabled" in validations
    assert "Text Validation" in validations
    assert "Performance Validation" not in validations # Performance only added to NAVIGATE/CLICK in our rules
