# UNVERIFIED_MODULES.md

Per Step 5 rules: a router is listed here only because no literal frontend-service string matched any of its real endpoint paths (see `BACKEND_INVENTORY.md`). Before any 'potentially unused' language, each was checked for internal backend cross-references: mentions of the module name in any other backend `.py` file, **excluding** `main.py` itself (since every module is trivially imported there for registration — that is not evidence of actual use, just evidence it's mounted, which is already known). None are classified as unused, dead, or orphaned.

Total UNVERIFIED-status routers: **74**

| Router (module) | Internal backend references (excluding main.py, own api/ file) | Classification |
|---|---|---|
| health | backend\app\auth.py, backend\app\migration_safety.py, backend\app\ai\copilot.py, backend\app\ai\copilot_v4.py (+16 more) | Needs Manual Review (internal backend reference found) |
| results | backend\app\migration_metadata.py, backend\app\ai\copilot_v4.py, backend\app\ai\decision_engine.py, backend\app\ai\agents\orchestrator.py (+20 more) | Needs Manual Review (internal backend reference found) |
| agents | backend\app\ai\copilot.py, backend\app\ai\agents\agent_registry.py, backend\app\ai\agents\base_agent.py, backend\app\ai\agents\orchestrator.py (+2 more) | Needs Manual Review (internal backend reference found) |
| task_imports | none found | Needs Manual Review (no reference found by any static method) |
| advanced_validation | backend\app\api\local_schedules.py, backend\app\api\system.py, backend\app\models\__init__.py, backend\app\scheduling\local_schedule_service.py (+4 more) | Needs Manual Review (internal backend reference found) |
| local_schedules | backend\app\models\advanced_validation.py | Needs Manual Review (internal backend reference found) |
| ai | backend\app\ai\autonomous_exploration.py, backend\app\ai\base.py, backend\app\ai\bug_analyzer.py, backend\app\ai\business_impact_engine.py (+55 more) | Needs Manual Review (internal backend reference found) |
| enterprise | backend\app\ai\digital_twin.py, backend\app\ai\recommendation_engine.py, backend\app\ai\strategy_generator.py, backend\app\ai\test_data_factory.py (+14 more) | Needs Manual Review (internal backend reference found) |
| discovery | backend\app\migration_metadata.py, backend\app\ai\agents\agent_registry.py, backend\app\ai\agents\orchestrator.py, backend\app\api\dashboard.py (+2 more) | Needs Manual Review (internal backend reference found) |
| copilot | backend\app\ai\copilot.py, backend\app\api\integrations.py | Needs Manual Review (internal backend reference found) |
| release_readiness | backend\app\api\release_command_center.py, backend\app\services\executive_advisor.py, backend\app\services\executive_command_center.py, backend\app\services\release_readiness.py (+1 more) | Needs Manual Review (internal backend reference found) |
| autonomous_regression | backend\app\services\autonomous_regression.py | Needs Manual Review (internal backend reference found) |
| knowledge_graph | backend\app\ai\knowledge_graph.py | Needs Manual Review (internal backend reference found) |
| digital_qa | none found | Needs Manual Review (no reference found by any static method) |
| digital_twin | backend\app\ai\digital_twin.py | Needs Manual Review (internal backend reference found) |
| continuous_monitoring | backend\app\services\continuous_monitoring.py | Needs Manual Review (internal backend reference found) |
| predictive_quality | backend\app\ai\predictive_quality.py | Needs Manual Review (internal backend reference found) |
| multi_reports | none found | Needs Manual Review (no reference found by any static method) |
| experience_memory | backend\app\ai\experience_memory.py | Needs Manual Review (internal backend reference found) |
| pattern_recognition | backend\app\ai\pattern_recognition.py | Needs Manual Review (internal backend reference found) |
| test_evolution | backend\app\ai\test_evolution.py | Needs Manual Review (internal backend reference found) |
| root_cause_graph | backend\app\ai\root_cause_graph.py | Needs Manual Review (internal backend reference found) |
| release_command_center | none found | Needs Manual Review (no reference found by any static method) |
| autonomous_monitoring_v2 | backend\app\services\autonomous_monitoring_v2.py | Needs Manual Review (internal backend reference found) |
| onboarding | backend\app\ai\copilot_v4.py | Needs Manual Review (internal backend reference found) |
| test_studio | none found | Needs Manual Review (no reference found by any static method) |
| test_lab | none found | Needs Manual Review (no reference found by any static method) |
| data_factory | none found | Needs Manual Review (no reference found by any static method) |
| war_room | none found | Needs Manual Review (no reference found by any static method) |
| plugin_marketplace | backend\app\services\plugin_marketplace.py | Needs Manual Review (internal backend reference found) |
| integrations | backend\app\services\enterprise_devops.py | Needs Manual Review (internal backend reference found) |
| distributed_execution | none found | Needs Manual Review (no reference found by any static method) |
| cloud_browser_farm | none found | Needs Manual Review (no reference found by any static method) |
| execution_stream | none found | Needs Manual Review (no reference found by any static method) |
| observability | backend\app\api\observability_ai.py, backend\app\models\phase16_models.py, backend\app\services\observability_platform.py, backend\app\services\production_observability_ai.py | Needs Manual Review (internal backend reference found) |
| enterprise_analytics | none found | Needs Manual Review (no reference found by any static method) |
| release_governance | none found | Needs Manual Review (no reference found by any static method) |
| compliance_center | none found | Needs Manual Review (no reference found by any static method) |
| api_hub | none found | Needs Manual Review (no reference found by any static method) |
| marketplace_ecosystem | none found | Needs Manual Review (no reference found by any static method) |
| enterprise_devops | none found | Needs Manual Review (no reference found by any static method) |
| multi_region_cloud | none found | Needs Manual Review (no reference found by any static method) |
| enterprise_security_center | none found | Needs Manual Review (no reference found by any static method) |
| ai_optimizer | none found | Needs Manual Review (no reference found by any static method) |
| executive_command_center | none found | Needs Manual Review (no reference found by any static method) |
| enterprise_brain | none found | Needs Manual Review (no reference found by any static method) |
| workflows | backend\app\ai\agents\orchestrator.py | Needs Manual Review (internal backend reference found) |
| business_process | none found | Needs Manual Review (no reference found by any static method) |
| incidents | backend\app\models\phase14_models.py, backend\app\services\incident_commander.py, backend\app\services\plugin_marketplace.py | Needs Manual Review (internal backend reference found) |
| governance | backend\app\api\release_governance.py, backend\app\services\release_governance.py | Needs Manual Review (internal backend reference found) |
| forecast | backend\app\ai\copilot_v4.py, backend\app\api\predictive_quality.py, backend\app\api\release_command_center.py | Needs Manual Review (internal backend reference found) |
| executive_advisor | none found | Needs Manual Review (no reference found by any static method) |
| knowledge_universe | none found | Needs Manual Review (no reference found by any static method) |
| report_factory | none found | Needs Manual Review (no reference found by any static method) |
| optimization_v2 | none found | Needs Manual Review (no reference found by any static method) |
| software_graph | none found | Needs Manual Review (no reference found by any static method) |
| change_impact | none found | Needs Manual Review (no reference found by any static method) |
| code_review | none found | Needs Manual Review (no reference found by any static method) |
| coverage | backend\app\ai\copilot.py, backend\app\ai\copilot_v4.py, backend\app\ai\risk_engine.py, backend\app\models\phase15_models.py (+8 more) | Needs Manual Review (internal backend reference found) |
| release_intelligence | none found | Needs Manual Review (no reference found by any static method) |
| defects_hub | none found | Needs Manual Review (no reference found by any static method) |
| engineering | none found | Needs Manual Review (no reference found by any static method) |
| knowledge_lake | none found | Needs Manual Review (no reference found by any static method) |
| mission_control | none found | Needs Manual Review (no reference found by any static method) |
| knowledge_lake_v2 | none found | Needs Manual Review (no reference found by any static method) |
| requirements | backend\app\ai\local_provider.py, backend\app\ai\prompt_registry.py, backend\app\ai\schemas.py, backend\app\api\knowledge_lake_v2.py (+1 more) | Needs Manual Review (internal backend reference found) |
| traceability | backend\app\api\defects.py, backend\app\api\knowledge_lake_v2.py, backend\app\api\reports.py, backend\app\models\phase16_models.py (+3 more) | Needs Manual Review (internal backend reference found) |
| architecture | backend\app\ai\copilot.py, backend\app\api\knowledge_lake_v2.py, backend\app\services\architecture_intelligence.py | Needs Manual Review (internal backend reference found) |
| code_quality | none found | Needs Manual Review (no reference found by any static method) |
| release_certification | none found | Needs Manual Review (no reference found by any static method) |
| observability_ai | none found | Needs Manual Review (no reference found by any static method) |
| customer_intelligence | none found | Needs Manual Review (no reference found by any static method) |
| policies | backend\app\api\governance.py, backend\app\models\phase14_models.py, backend\app\services\enterprise_policy_engine.py, backend\app\services\governance_center.py | Needs Manual Review (internal backend reference found) |
| sdlc_orchestrator | none found | Needs Manual Review (no reference found by any static method) |

## Summary
- With internal backend references found (excluding main.py): 33
- No references found by any static method (frontend service strings OR other backend files OR main.py): 41

## Explicit note per Final Rule
No module above is classified as unused, dead, or orphaned. Dynamic URL construction, scheduled/background jobs, external API-doc consumers, and test-only usage are all possibilities not ruled out by static search. Each row requires human decision or deeper manual trace before any cleanup action.
