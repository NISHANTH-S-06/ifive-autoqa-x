import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

@patch("app.connectors.mock_task_portal.MockTaskPortalConnector.health_check", return_value=True)
@patch("app.connectors.mock_task_portal.MockTaskPortalConnector.fetch_testing_l2_tasks", return_value=[
    {
        "source_task_id": "123",
        "source_revision": 1,
        "status": "TESTING_L2",
        "project_name": "Demo ERP",
        "module_name": "HR",
        "title": "Create Employee",
        "description": "Test creation with role admin and permission edit",
    },
    {
        "source_task_id": "456",
        "source_revision": 1,
        "status": "TESTING_L2",
        "project_name": "Demo ERP",
        "module_name": "HR",
        "title": "Generic form without expected result",
        "description": "Test generic",
    }
])
@patch("app.connectors.mock_task_portal.MockTaskPortalConnector.send_qa_result", return_value=True)
def test_test_plan_acceptance_hardening(mock_send, mock_fetch, mock_health, client: TestClient):
    # Setup - Sync tasks
    res = client.post("/api/task-imports/sync")
    assert res.status_code == 200

    # 1. Missing Information Gate
    res = client.get("/api/task-imports")
    imports = res.json()
    generic_task = next(t for t in imports if t["source_task_id"] == "456")
    
    res = client.post(f"/api/task-imports/{generic_task['id']}/generate-plan")
    assert res.status_code == 422
    assert "missing_information" in res.json()["detail"]
    assert "missing target route" in "".join(res.json()["detail"]["missing_information"])
    
    # Check that task status is now NEED_CLARITY
    res = client.get(f"/api/task-imports/{generic_task['id']}")
    assert res.json()["import_status"] == "NEED_CLARITY"

    # 2. Employee Task - Happy path and Approval Hardening
    employee_task = next(t for t in imports if t["source_task_id"] == "123")
    res = client.post(f"/api/task-imports/{employee_task['id']}/generate-plan")
    if res.status_code != 200:
        print("GENERATE PLAN FAILED WITH:", res.json())
    assert res.status_code == 200
    plan = res.json()
    plan_id = plan["id"]
    
    # Edit the plan - try to remove all mandatory scenarios (should fail)
    res = client.patch(f"/api/test-plans/{plan_id}", json={"scenarios": [{"scenario_type": "REGRESSION", "title": "Regr", "steps": []}]})
    assert res.status_code == 400
    assert "Cannot remove all mandatory scenarios" in res.json()["detail"]
    
    # Edit the plan - try to add secret (should fail)
    res = client.patch(f"/api/test-plans/{plan_id}", json={"scenarios": [{"scenario_type": "PRIMARY", "title": "Pri", "steps": [{"step_order": 1, "action": "FILL", "input_value_reference": "my secret_token"}]}]})
    assert res.status_code == 400
    assert "Secrets cannot be stored in plain text" in res.json()["detail"]
    
    # Submit the plan
    res = client.post(f"/api/test-plans/{plan_id}/submit")
    assert res.status_code == 200
    
    # Try to approve the plan (self-approval block)
    res = client.post(f"/api/test-plans/{plan_id}/approve")
    assert res.status_code == 403
    assert "Developers cannot approve their own generated test plans" in res.json()["detail"]
    
    # Reject the plan without reason (should fail)
    res = client.post(f"/api/test-plans/{plan_id}/reject", json={"reason": ""})
    assert res.status_code == 400
    assert "Rejection requires a non-empty reason" in res.json()["detail"]
    
    # Reject the plan properly
    res = client.post(f"/api/test-plans/{plan_id}/reject", json={"reason": "Need fix"})
    assert res.status_code == 200
    assert res.json()["status"] == "REJECTED"
    
    # Task import status should be back to DRAFT
    res = client.get(f"/api/task-imports/{employee_task['id']}")
    assert res.json()["import_status"] == "DRAFT"

@patch("app.connectors.mock_task_portal.MockTaskPortalConnector.health_check", return_value=True)
@patch("app.connectors.mock_task_portal.MockTaskPortalConnector.fetch_testing_l2_tasks", return_value=[
    {
        "source_task_id": "999",
        "source_revision": 1,
        "status": "TESTING_L2",
        "project_name": "Demo ERP",
        "module_name": "HR",
        "title": "Create Employee",
        "description": "Test creation with role admin and permission edit",
        "acceptance_criteria": "Should be immutable"
    }
])
@patch("app.connectors.mock_task_portal.MockTaskPortalConnector.send_qa_result", return_value=True)
def test_test_plan_immutability_and_execution(mock_send, mock_fetch, mock_health, client: TestClient):
    # Setup - Sync tasks
    res = client.post("/api/task-imports/sync")
    assert res.status_code == 200

    res = client.get("/api/task-imports")
    imports = res.json()
    task = next(t for t in imports if t["source_task_id"] == "999")
    
    # Generate Plan
    res = client.post(f"/api/task-imports/{task['id']}/generate-plan")
    if res.status_code != 200:
        print("GENERATE FAILED:", res.json())
    assert res.status_code == 200
    plan = res.json()
    plan_id = plan["id"]
    
    # Submit Plan
    res = client.post(f"/api/test-plans/{plan_id}/submit")
    assert res.status_code == 200
    
    # Approve Plan (We need to bypass self-approval check for the test, let's mock it or just assume the endpoint allows it if we bypass auth check. Actually, self-approval is blocked in the API: `if plan.created_by == operator_id: raise HTTPException`.
    # Let's mock the get_operator dependency for the approve call
    from fastapi import Depends
    from app.auth import get_auth_context
    from app.auth import AuthContext
    from app.models.operator import Operator


    op2 = Operator(id=2, username="approver", display_name="Approver", role="ADMIN", is_active=True)
    from sqlalchemy.orm import Session
    from app.database import get_db
    def override_get_auth_context(db: Session = Depends(get_db)):
        from app.models.operator_session import OperatorSession
        from app.models.project_membership import ProjectMember
        import datetime
        
        # Ensure operator is member of project
        if not db.query(ProjectMember).filter_by(project_id=task['project_id'], operator_id=op2.id).first():
            db.add(ProjectMember(project_id=task['project_id'], operator_id=op2.id, role="APPROVER", status="ACTIVE"))
            db.commit()
            
        mock_session = OperatorSession(id="mock", operator_id=op2.id, operator=op2, ip_address="127.0.0.1", password_version_at_login=1, expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=1))
        return AuthContext(operator=op2, session=mock_session)
        
    original_override = client.app.dependency_overrides.get(get_auth_context)
    client.app.dependency_overrides[get_auth_context] = override_get_auth_context
    
    res = client.post(f"/api/test-plans/{plan_id}/approve")
    if res.status_code != 200:
        print("APPROVE FAILED:", res.text)
    assert res.status_code == 200
    assert res.json()["status"] == "APPROVED"
    assert res.json()["approved_version_number"] is not None
    
    if original_override:
        client.app.dependency_overrides[get_auth_context] = original_override
    else:
        del client.app.dependency_overrides[get_auth_context]
    
    # Patch plan (should revert to DRAFT)
    res = client.patch(f"/api/test-plans/{plan_id}", json={"title": "New Title"})
    assert res.status_code == 200
    assert res.json()["status"] == "DRAFT"
    
    # Now it's DRAFT again. Execution should be prevented if we try to execute.
    res = client.post(f"/api/task-imports/{task['id']}/run")
    # Actually execute-callback requires APPROVED plan
    assert res.status_code == 409
    assert "TestPlan must be APPROVED before execution" in res.json()["detail"]

