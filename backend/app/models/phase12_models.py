import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class OnboardingWizardSession(Base):
    __tablename__ = 'onboarding_wizard_sessions'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    company_name = Column(String(200), nullable=False)
    product_name = Column(String(200), nullable=False)
    application_url = Column(String(500), nullable=False)
    auth_type = Column(String(60), nullable=False)  # USERNAME_PASSWORD, OTP, GOOGLE, MICROSOFT, SSO, BEARER_TOKEN, COOKIE, MANUAL
    auth_config_json = Column(Text, nullable=False, default='{}')
    browser_selection = Column(String(60), nullable=False, default='CHROMIUM')
    environment = Column(String(30), nullable=False, default='QA')  # DEV, QA, UAT, PRODUCTION
    validation_status = Column(String(30), nullable=False, default='PENDING')  # PENDING, VALIDATING, PASSED, FAILED
    validation_results_json = Column(Text, nullable=False, default='{}')
    current_step = Column(Integer, nullable=False, default=1)
    created_by = Column(Integer, ForeignKey('operators.id'), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class ZeroCodeTestStudioFlow(Base):
    __tablename__ = 'zero_code_test_studio_flows'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    flow_name = Column(String(200), nullable=False)
    flow_type = Column(String(60), nullable=False)  # SCENARIO, VISUAL_ASSERTION, API, DB_VALIDATION, BUSINESS_RULE
    flow_definition_json = Column(Text, nullable=False, default='[]')
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(Integer, ForeignKey('operators.id'), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TestLabBrowserWorker(Base):
    __tablename__ = 'test_lab_browser_workers'

    id = Column(Integer, primary_key=True)
    worker_name = Column(String(100), nullable=False)
    browser_type = Column(String(60), nullable=False)  # CHROMIUM, CHROME, FIREFOX, EDGE, WEBKIT, MOBILE_CHROME, MOBILE_SAFARI, TABLET, DESKTOP
    worker_status = Column(String(30), nullable=False, default='IDLE')  # IDLE, BUSY, UNHEALTHY, RESTARTING
    current_job_id = Column(String(100), nullable=True)
    jobs_completed = Column(Integer, nullable=False, default=0)
    jobs_failed = Column(Integer, nullable=False, default=0)
    last_heartbeat = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TestDataFactoryDataset(Base):
    __tablename__ = 'test_data_factory_datasets'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    dataset_name = Column(String(200), nullable=False)
    data_category = Column(String(60), nullable=False)  # CUSTOMERS, PRODUCTS, INVOICES, ORDERS, USERS, ROLES, PERMISSIONS, RANDOM, BOUNDARY, NEGATIVE, SYNTHETIC
    record_count = Column(Integer, nullable=False, default=0)
    is_masked = Column(Boolean, nullable=False, default=False)
    dataset_json = Column(Text, nullable=False, default='[]')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class ReleaseWarRoomMetrics(Base):
    __tablename__ = 'release_war_room_metrics'

    id = Column(Integer, primary_key=True)
    snapshot_label = Column(String(100), nullable=False)
    total_projects = Column(Integer, nullable=False, default=0)
    total_companies = Column(Integer, nullable=False, default=0)
    running_executions = Column(Integer, nullable=False, default=0)
    overall_risk_score = Column(Float, nullable=False, default=0.0)
    overall_coverage_pct = Column(Float, nullable=False, default=0.0)
    open_critical_defects = Column(Integer, nullable=False, default=0)
    release_health_score = Column(Float, nullable=False, default=0.0)
    deployment_recommendation = Column(String(30), nullable=False, default='HOLD')  # GO, HOLD, ROLLBACK
    metrics_json = Column(Text, nullable=False, default='{}')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class PluginMarketplacePackage(Base):
    __tablename__ = 'plugin_marketplace_packages'

    id = Column(Integer, primary_key=True)
    package_name = Column(String(150), nullable=False)
    package_version = Column(String(30), nullable=False)
    plugin_type = Column(String(60), nullable=False)  # VALIDATOR, AI_AGENT, REPORT, BROWSER_ACTION, INTEGRATION, EXTENSION
    author = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    is_installed = Column(Boolean, nullable=False, default=False)
    config_schema_json = Column(Text, nullable=False, default='{}')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class EnterpriseIntegrationConfig(Base):
    __tablename__ = 'enterprise_integration_configs'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    integration_type = Column(String(60), nullable=False)  # JIRA, AZURE_DEVOPS, GITHUB, GITLAB, SLACK, TEAMS, EMAIL, WEBHOOK, SERVICENOW, SAP, SALESFORCE, ERP, CRM, HRMS
    integration_name = Column(String(150), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    config_json = Column(Text, nullable=False, default='{}')
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
