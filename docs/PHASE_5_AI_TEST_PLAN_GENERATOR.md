# Phase 5: AI Test Plan Generator

## Overview

The AI Test Plan Generator is a core capability of iFive AutoQA X, designed to convert raw functional requirements (imported from the Mock Task Portal) into structured, executable test plans.

## Workflow

1. **Analyze Task**: When a user triggers "Generate AI Test Plan" for a task in DRAFT status, the backend calls the local AI provider.
2. **AI Provider**: The AI provider analyzes the task description, acceptance criteria, and expected results to identify required test scenarios (Primary, Negative, Boundary, Regression).
3. **Draft Plan Generation**: A `TestPlan` is created in `DRAFT` status containing multiple `TestScenario`s, each with sequenced `TestStep`s.
4. **Validation**: The AI provider may return a `422 Unprocessable Entity` with `missing_information` if the task description lacks sufficient detail to generate a safe plan.

## Architecture

- **API**: `POST /api/task-imports/{id}/generate-plan`
- **Models**: `TestPlan`, `TestPlanVersion`, `TestScenario`, `TestStep`
- **Services**: `test_plan_service.py`, `task_analysis_service.py`
- **AI Integration**: The `local_provider.py` contains deterministic mocks for predefined tasks (e.g. `EMPLOYEE_CREATE`, `STOCK_COUNT`) to ensure consistent acceptance testing.

## Database Models

- `TestPlan`: Central entity linking `ExternalTaskImport` to test versions. Tracks approval status.
- `TestPlanVersion`: Immutable snapshots of the plan for audit and execution purposes.
- `TestScenario`: Groups of sequential actions designed to validate a specific business case.
- `TestStep`: The granular action (e.g., `NAVIGATE`, `CLICK`, `FILL`, `ASSERT_TEXT`) and locator/value payload.

## Future Enhancements

- Integration with external LLM providers (e.g., Gemini, GPT-4) when real AI mode is enabled.
- Adaptive selector generation using visual DOM analysis.
