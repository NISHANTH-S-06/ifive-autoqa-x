import hashlib
import json
from datetime import datetime
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.models.external_task_import import ExternalTaskImport
from app.models.test_plan import TestPlan, TestPlanVersion, TestScenario, TestStep
from app.schemas.test_plan import TestPlanUpdate, TestPlanReject
from app.services.task_analysis_service import analyze_imported_task

def _generate_hash(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def generate_plan_for_task(db: DBSession, task_import_id: int, creator_id: int) -> TestPlan:
    task = db.get(ExternalTaskImport, task_import_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task.import_status not in ["DRAFT", "NEED_CLARITY"]:
        raise HTTPException(status_code=400, detail="Can only generate plans for tasks in DRAFT or NEED_CLARITY status")
        
    # See if plan already exists
    plan = db.query(TestPlan).filter_by(external_task_import_id=task_import_id).first()
    
    # 1. Ask AI for analysis
    ai_response = analyze_imported_task(task.title, task.description or "", task.acceptance_criteria or "")
    # Check total size of AI output
    if len(ai_response.model_dump_json()) > 50000:
        raise HTTPException(status_code=422, detail="Oversized AI output detected")

    allowed_actions = {"CLICK", "FILL", "NAVIGATE", "ASSERT_TEXT", "ASSERT_VISIBLE", "ASSERT_VALUE", "ASSERT_URL", "SELECT", "CHECK", "UNCHECK", "READ_TEXT", "SCREENSHOT"}
    
    for sc in ai_response.scenarios:
        for st in sc.steps:
            if st.action not in allowed_actions:
                msg = f"unsupported action: {st.action}"
                if msg not in ai_response.missing_information:
                    ai_response.missing_information.append(msg)

            val = (st.value or "").lower()
            sel = (st.selector or "").lower()
            pth = (st.path or "").lower()
            exp = (st.expected_result or "").lower()

            # Check external URLs and unsafe path traversal
            if st.path and (st.path.startswith("http://") or st.path.startswith("https://") or "://" in st.path):
                raise HTTPException(status_code=422, detail="External URLs are not allowed")
            if st.path and (".." in st.path or "\\" in st.path):
                raise HTTPException(status_code=422, detail="Path outside approved mapping detected")

            # Check code / command injection
            code_keywords = ['javascript:', '<script', 'eval(', 'exec(', 'os.system', 'subprocess', 'bash', 'powershell', 'import ', 'require(']
            if any(p in val or p in sel or p in pth or p in exp for p in code_keywords):
                raise HTTPException(status_code=422, detail="Unsafe JavaScript or shell command detected in AI output")

            # Check raw secrets
            secret_keywords = ['password123', 'secret_token', 'bearer_', 'pass=', 'token=', 'autoqa_session']
            if any(p in val for p in secret_keywords):
                raise HTTPException(status_code=422, detail="Raw secret detected in AI output")

            # Check PASS/FAIL instructions
            if exp in ["pass", "fail", "blocked", "mark pass", "result: pass", "result: fail"]:
                raise HTTPException(status_code=422, detail="AI output cannot contain raw PASS/FAIL decisions")

    # Missing information gate
    if ai_response.missing_information:
        task.import_status = "NEED_CLARITY"
        task.callback_error = "AI found missing information: " + "; ".join(ai_response.missing_information)
        db.commit()
        if not plan:
            plan = TestPlan(
                project_id=task.project_id,
                external_task_import_id=task.id,
                source_task_id=task.source_task_id,
                source_revision=task.source_revision,
                plan_code=f"PLAN-{task.source_task_id}",
                title=ai_response.plan_title,
                status="DRAFT",
                created_by=creator_id
            )
            db.add(plan)
            db.commit()
        raise HTTPException(status_code=422, detail={"missing_information": ai_response.missing_information})

    # If no missing info, proceed with plan generation
    if not plan:
        plan = TestPlan(
            project_id=task.project_id,
            external_task_import_id=task.id,
            source_task_id=task.source_task_id,
            source_revision=task.source_revision,
            plan_code=f"PLAN-{task.source_task_id}",
            title=ai_response.plan_title,
            status="DRAFT",
            created_by=creator_id
        )
        db.add(plan)
        db.flush()
        
    # Freeze version
    version_num = plan.current_version + (1 if plan.versions else 0)
    
    snapshot_data = ai_response.model_dump_json()
    
    version = TestPlanVersion(
        test_plan_id=plan.id,
        version_number=version_num,
        source_revision=task.source_revision,
        provider="LocalAI",
        model="heuristic-v1",
        plan_hash=_generate_hash(snapshot_data),
        created_by=creator_id,
        immutable_snapshot_json=snapshot_data
    )
    db.add(version)
    db.flush()
    
    # Build scenarios
    for s_idx, ai_scenario in enumerate(ai_response.scenarios):
        scenario = TestScenario(
            test_plan_version_id=version.id,
            scenario_type=ai_scenario.scenario_type,
            title=ai_scenario.title,
            description=ai_scenario.description,
            priority=ai_scenario.priority,
            risk=ai_scenario.risk,
            enabled=ai_scenario.enabled,
            mandatory=ai_scenario.mandatory,
            order_index=s_idx
        )
        db.add(scenario)
        db.flush()
        
        for step in ai_scenario.steps:
            db.add(TestStep(
                scenario_id=scenario.id,
                step_order=step.step_number,
                action=step.action,
                locator_json=step.selector,
                input_value_reference=step.value,
                expected_value=step.expected_result,
            ))
            
    plan.current_version = version_num
    task.import_status = "IN_REVIEW"
    db.commit()
    db.refresh(plan)
    
    return plan

def get_plan_by_import_id(db: DBSession, import_id: int) -> Optional[TestPlan]:
    return db.query(TestPlan).filter_by(external_task_import_id=import_id).first()

def get_plan(db: DBSession, plan_id: int) -> TestPlan:
    plan = db.get(TestPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="TestPlan not found")
    return plan

def update_plan(db: DBSession, plan_id: int, updates: TestPlanUpdate, operator_id: int) -> TestPlan:
    plan = get_plan(db, plan_id)
    if plan.status not in ["DRAFT", "IN_REVIEW", "APPROVED"]:
        raise HTTPException(status_code=400, detail="Cannot edit a rejected plan")
    if plan.status == "APPROVED":
        plan.status = "DRAFT"
        plan.execution_enabled = False
        
    if updates.scenarios is not None:
        mandatory_scenarios = [s for s in updates.scenarios if s.scenario_type == 'PRIMARY']
        if not mandatory_scenarios:
            raise HTTPException(status_code=400, detail="Cannot remove all mandatory scenarios")
        code_keywords = ['javascript:', '<script', 'eval(', 'exec(', 'os.system', 'subprocess', 'bash', 'powershell', 'import ', 'require(']
        secret_keywords = ['password', 'secret', 'token', 'password123', 'secret_token', 'bearer_', 'autoqa_session']
        for sc in updates.scenarios:
            for st in sc.steps:
                if st.action not in ["CLICK", "FILL", "NAVIGATE", "ASSERT_TEXT", "ASSERT_VISIBLE", "ASSERT_VALUE", "ASSERT_URL", "SELECT", "CHECK", "UNCHECK", "READ_TEXT", "SCREENSHOT"]:
                    raise HTTPException(status_code=400, detail=f"Unsupported action: {st.action}")
                val = (st.input_value_reference or "").lower()
                sel = (st.locator_json or "").lower()
                exp = (st.expected_value or "").lower()
                if any(p in val or p in sel or p in exp for p in code_keywords):
                    raise HTTPException(status_code=400, detail="Unsafe JavaScript or shell command detected in input")
                if any(p in val or p in sel or p in exp for p in secret_keywords):
                    raise HTTPException(status_code=400, detail="Secrets cannot be stored in plain text")

        
    if updates.title is not None:
        plan.title = updates.title
    if updates.optional_regression_enabled is not None:
        plan.optional_regression_enabled = updates.optional_regression_enabled
        
    if updates.scenarios is not None:
        # Create a new version if we modify scenarios
        # Only if the hash is different
        snapshot_data = updates.model_dump_json(exclude_unset=True)
        new_hash = _generate_hash(snapshot_data)
        
        last_version = db.query(TestPlanVersion).filter_by(test_plan_id=plan.id).order_by(TestPlanVersion.version_number.desc()).first()
        if last_version and last_version.plan_hash == new_hash:
            # Hash unchanged, do not bump version
            version_num = plan.current_version
            version = last_version
            # But we should still update plan fields if they changed (title etc handled below)
            # We don't overwrite scenarios since they didn't change
            should_create_version = False
        else:
            version_num = plan.current_version + 1
            version = TestPlanVersion(
                test_plan_id=plan.id,
                version_number=version_num,
                source_revision=plan.source_revision,
                plan_hash=new_hash,
                created_by=operator_id,
                immutable_snapshot_json=snapshot_data
            )
            db.add(version)
            db.flush()
            should_create_version = True
        
        if should_create_version:
            for s_idx, s_data in enumerate(updates.scenarios):
                scenario = TestScenario(
                    test_plan_version_id=version.id,
                    scenario_type=s_data.scenario_type,
                    title=s_data.title,
                    description=s_data.description,
                    priority=s_data.priority,
                    risk=s_data.risk,
                    enabled=s_data.enabled,
                    mandatory=s_data.mandatory,
                    order_index=s_idx
                )
                db.add(scenario)
                db.flush()
                for st_idx, st_data in enumerate(s_data.steps):
                    db.add(TestStep(
                        scenario_id=scenario.id,
                        step_order=st_data.step_order,
                        action=st_data.action,
                        locator_json=st_data.locator_json,
                        input_value_reference=st_data.input_value_reference,
                        expected_value=st_data.expected_value,
                        timeout_ms=st_data.timeout_ms,
                        continue_on_failure=st_data.continue_on_failure,
                        metadata_json=st_data.metadata_json
                    ))
            plan.current_version = version_num
        
    db.commit()
    db.refresh(plan)
    return plan

def submit_plan(db: DBSession, plan_id: int, operator_id: int) -> TestPlan:
    plan = get_plan(db, plan_id)
    if plan.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Plan must be in DRAFT status to submit")
    plan.status = "IN_REVIEW"
    plan.submitted_by = operator_id
    plan.submitted_at = datetime.utcnow()
    db.commit()
    db.refresh(plan)
    return plan

def approve_plan(db: DBSession, plan_id: int, operator_id: int) -> TestPlan:
    plan = get_plan(db, plan_id)
    if plan.status != "IN_REVIEW":
        raise HTTPException(status_code=400, detail="Plan must be IN_REVIEW to approve")
        
    task = db.get(ExternalTaskImport, plan.external_task_import_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if plan.created_by == operator_id:
        raise HTTPException(status_code=403, detail="Developers cannot approve their own generated test plans")
        
    # Block developer who owns source task
    # We will assume Operator.username is used for task.assigned_developer
    from app.models.operator import Operator
    operator = db.get(Operator, operator_id)
    if operator and operator.username == task.assigned_developer:
        raise HTTPException(status_code=403, detail="Developers cannot approve test plans for their own tasks")
        
    plan.status = "APPROVED"
    plan.approved_by = operator_id
    plan.approved_at = datetime.utcnow()
    plan.approved_version_number = plan.current_version
    plan.execution_enabled = True
    
    # Also update the task import
    task = db.get(ExternalTaskImport, plan.external_task_import_id)
    if task:
        task.import_status = "APPROVED"
        task.approved_by = "operator"
        task.approved_at = datetime.utcnow()
        
    db.commit()
    db.refresh(plan)
    return plan

def reject_plan(db: DBSession, plan_id: int, payload: TestPlanReject, operator_id: int) -> TestPlan:
    plan = get_plan(db, plan_id)
    if plan.status != "IN_REVIEW":
        raise HTTPException(status_code=400, detail="Plan must be IN_REVIEW to reject")
        
    if not payload.reason or not payload.reason.strip():
        raise HTTPException(status_code=400, detail="Rejection requires a non-empty reason")
        
    plan.status = "REJECTED"
    plan.rejected_by = operator_id
    plan.rejected_at = datetime.utcnow()
    plan.rejection_reason = payload.reason
    plan.execution_enabled = False
    
    task = db.get(ExternalTaskImport, plan.external_task_import_id)
    if task:
        task.import_status = "DRAFT" # Goes back to draft for fixing
        
    db.commit()
    db.refresh(plan)
    return plan
