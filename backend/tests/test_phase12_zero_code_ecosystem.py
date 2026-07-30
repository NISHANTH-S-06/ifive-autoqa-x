import pytest
from app.services.zero_code_onboarding import ZeroCodeOnboardingService
from app.services.zero_code_test_studio import ZeroCodeTestStudioService
from app.ai.test_generation_v3 import TestGenerationV3Engine, ALL_STRATEGIES
from app.services.autonomous_test_lab import AutonomousTestLabService
from app.ai.test_data_factory import SmartTestDataFactory
from app.ai.root_cause_engine_v2 import RootCauseEngineV2
from app.services.release_war_room import ReleaseWarRoomService
from app.ai.copilot_v4 import ExecutiveCopilotV4
from app.services.plugin_marketplace import PluginMarketplaceService
from app.services.enterprise_integrations import EnterpriseIntegrationsService
from app.services.multi_cloud_platform import MultiCloudPlatformService


def test_zero_code_onboarding_start_session(db):
    service = ZeroCodeOnboardingService(db)
    session = service.start_session(
        company_name='Acme Corp',
        product_name='ERP Suite',
        application_url='https://erp.acme.com',
        auth_type='USERNAME_PASSWORD',
        auth_config={'username': 'admin', 'password': '***'},
        browser_selection='CHROMIUM',
        environment='QA',
    )
    assert session.id is not None
    assert session.validation_status == 'PENDING'
    assert session.company_name == 'Acme Corp'


def test_zero_code_onboarding_validate(db):
    service = ZeroCodeOnboardingService(db)
    session = service.start_session(
        company_name='TestCo', product_name='Portal', application_url='https://portal.test.com',
        auth_type='OTP', auth_config={}, browser_selection='FIREFOX', environment='UAT',
    )
    result = service.validate_connection(session.id)
    assert result['validation_status'] == 'PASSED'
    assert result['validation_results']['all_checks_passed'] is True


def test_zero_code_test_studio_create_flow(db):
    service = ZeroCodeTestStudioService(db)
    flow = service.create_flow(
        project_id=1,
        flow_name='Login Flow',
        flow_type='SCENARIO',
        flow_steps=[{'type': 'CLICK', 'selector': '#submit'}],
    )
    assert flow.id is not None
    assert flow.flow_type == 'SCENARIO'


def test_zero_code_test_studio_step_palette(db):
    service = ZeroCodeTestStudioService(db)
    palette = service.get_available_step_types()
    assert len(palette['actions']) >= 14
    assert len(palette['assertions']) >= 8


def test_test_generation_v3_full_suite():
    engine = TestGenerationV3Engine()
    result = engine.generate_full_suite(1, 'https://app.example.com')
    assert result['total_strategies'] == len(ALL_STRATEGIES)
    assert result['total_tests_generated'] > 0
    assert len(result['strategies']) == len(ALL_STRATEGIES)


def test_test_generation_v3_strategy():
    engine = TestGenerationV3Engine()
    result = engine.generate_strategy(1, 'SECURITY')
    assert result['strategy'] == 'SECURITY'
    assert result['priority'] == 'P0'
    assert len(result['sample_cases']) > 0


def test_autonomous_test_lab_provision(db):
    service = AutonomousTestLabService(db)
    service.provision_workers()
    status = service.get_farm_status()
    assert status['total_workers'] == 9  # one per browser type


def test_autonomous_test_lab_self_heal(db):
    from app.models.phase12_models import TestLabBrowserWorker
    from datetime import datetime
    # Mark one worker as unhealthy
    service = AutonomousTestLabService(db)
    service.provision_workers()
    worker = db.query(TestLabBrowserWorker).first()
    worker.worker_status = 'UNHEALTHY'
    db.commit()
    result = service.self_heal_workers()
    assert result['healed_count'] >= 1


def test_smart_test_data_factory_generate(db):
    factory = SmartTestDataFactory(db)
    result = factory.generate_dataset(1, 'CUSTOMERS', 5)
    assert result['record_count'] == 5
    assert len(result['sample_preview']) <= 3


def test_smart_test_data_factory_masked(db):
    factory = SmartTestDataFactory(db)
    result = factory.generate_dataset(1, 'USERS', 3, masked=True)
    assert result['masked'] is True
    for record in result['sample_preview']:
        assert '**' in str(record.get('email', ''))


def test_root_cause_engine_v2():
    engine = RootCauseEngineV2()
    result = engine.analyze('DEF-200', {})
    assert 'root_cause' in result
    assert result['confidence'] >= 0.9
    assert 'developer_suggestion' in result
    assert 'regression_impact' in result
    assert 'business_impact' in result


def test_release_war_room_metrics(db):
    service = ReleaseWarRoomService(db)
    metrics = service.get_war_room_metrics()
    assert 'deployment_recommendation' in metrics
    assert metrics['deployment_recommendation'] in ('GO', 'CONDITIONAL_GO', 'HOLD')
    assert 'executive_kpis' in metrics
    assert metrics['release_health_score'] >= 0


def test_executive_copilot_v4():
    copilot = ExecutiveCopilotV4()
    result = copilot.process_command('Generate tests for the ERP module')
    assert result['resolved_intent'] == 'GENERATE_TESTS'
    assert result['confidence'] >= 0.95
    result2 = copilot.process_command('Show release status')
    assert result2['resolved_intent'] == 'SHOW_RELEASE_STATUS'
    result3 = copilot.process_command('Generate RCA for login failure')
    assert result3['resolved_intent'] == 'GENERATE_RCA'


def test_plugin_marketplace_seed(db):
    service = PluginMarketplaceService(db)
    packages = service.seed_marketplace()
    assert len(packages) >= 6
    pkg = service.install_package(packages[0]['id'])
    assert pkg['status'] == 'INSTALLED'
    pkg2 = service.uninstall_package(packages[0]['id'])
    assert pkg2['status'] == 'UNINSTALLED'


def test_enterprise_integrations_supported(db):
    service = EnterpriseIntegrationsService(db)
    supported = service.get_supported_integrations()
    assert 'JIRA' in supported
    assert 'SAP' in supported
    assert 'SALESFORCE' in supported
    assert len(supported) >= 18


def test_enterprise_integration_add_and_test(db):
    service = EnterpriseIntegrationsService(db)
    cfg = service.add_integration(
        project_id=1,
        integration_type='JIRA',
        integration_name='Acme Jira',
        config={'base_url': 'https://acme.atlassian.net', 'project_key': 'QA'},
    )
    assert cfg.id is not None
    assert cfg.is_active is True
    test_result = service.test_integration(cfg.id)
    assert test_result['status'] == 'CONNECTION_OK'


def test_multi_cloud_platform_templates():
    service = MultiCloudPlatformService()
    templates = service.get_deployment_templates()
    assert len(templates) == 8
    assert 'KUBERNETES' in templates
    assert 'AWS' in templates
    health = service.get_platform_health('KUBERNETES')
    assert health['status'] == 'HEALTHY'
