# Phase 5: Approval Workflow

## Overview
The iFive AutoQA X platform mandates strict human-in-the-loop oversight. AI-generated test plans must never be executed automatically against production or staging environments without explicit human approval.

## The Approval Gate
1. **DRAFT**: AI generates the plan. The assigned developer or tester can edit scenarios, fix locators, and tweak expected results in the `TestPlanEditor`.
2. **IN_REVIEW**: When the user clicks "Submit for Approval," the plan transitions to `IN_REVIEW`.
3. **APPROVED / REJECTED**: Another authorized user (usually the assigned tester or QA lead) reviews the plan in the `TestPlanApproval` modal.
    - **Approve**: Marks the plan as `APPROVED` and unlocks execution capability.
    - **Reject**: Marks the plan as `REJECTED`, requiring a mandatory rejection reason (e.g., "Missing edge cases for null input"). The plan can then be reverted to DRAFT or revised.

## Security Controls
- **Self-Approval Block**: A user cannot approve a test plan they submitted. The system enforces segregation of duties (`403 Forbidden` if `current_operator_id == plan.submitted_by`).
- **Immutable Execution Versions**: When a plan is executed via `automated_execution.py`, it references a specific `TestPlanVersion` (`version_number` and `immutable_snapshot_json`), ensuring that any post-approval edits do not retroactively alter the audit trail of what was actually run.
