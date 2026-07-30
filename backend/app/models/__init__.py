"""Import all models to register SQLAlchemy mappers."""
from app.models.agent_suggestion import AgentSuggestion
from app.models.audit_event import AuditEvent
from app.models.automated_execution import (
    AutomatedRun,
    AutomatedRunCase,
    AutomatedStepResult,
    ExecutionArtifact,
    ExecutionAttempt,
    ExecutionEvent,
    ExecutionJob,
    ExecutionWorker,
)
from app.models.company_task import CompanyTask
from app.models.connection_target import ConnectionTarget, ConnectionTargetVersion
from app.models.defect import Defect, DefectComment, DefectEvidenceLink, DefectHistory, DefectRetest
from app.models.evidence import Evidence
from app.models.external_task_import import ExternalTaskImport
from app.models.operator import Operator
from app.models.operator_session import OperatorSession
from app.models.password_history import PasswordHistory
from app.models.project import Project
from app.models.project_membership import ProjectMember
from app.models.reporting import ReportDefinition, ReportExport
from app.models.test_case import TestCase
from app.models.test_management import (
    ManagedTestCase,
    ManagedTestSuite,
    ManualEvidence,
    ManualStepResult,
    ManualTestRun,
    ManualTestRunCase,
    Tag,
    TestCaseStep,
    TestCaseTag,
    TestCaseVersion,
    TestModule,
    TestProject,
)
from app.models.test_plan import TestPlan, TestPlanVersion, TestScenario, TestStep
from app.models.test_result import TestResult
from app.models.test_run import TestRun
from app.models.test_suite import TestSuite

from app.models.advanced_validation import (
    AccessibilityValidationDefinition,
    AdvancedValidationProfile,
    AdvancedValidationResult,
    AdvancedValidationRun,
    ApiValidationDefinition,
    DatabaseValidationDefinition,
    LocalSchedule,
    PerformanceValidationDefinition,
)
from app.models.visual_regression import (
    VisualBaseline,
    VisualBaselineHistory,
    VisualComparisonRun,
)
from app.models.enterprise_hierarchy import Company, CompanyProduct, CompanyModule
from app.models.discovery import DiscoveryResult
from app.models.phase9_models import (
    AIMemoryRecord,
    AILocatorHistory,
    KnowledgeGraphNode,
    KnowledgeGraphEdge,
    ReleaseReadinessEvaluation,
    NotificationLog,
)
from app.models.phase10_models import (
    AIDigitalQAEngineRecord,
    DigitalTwinEntity,
    ContinuousMonitorAlert,
    PredictiveQualityMetric,
    SelfOptimizationLog,
)
from app.models.phase11_models import (
    AIExperienceRecord,
    PatternDetectionRecord,
    TestEvolutionRecord,
    RootCauseGraphNode,
    RootCauseGraphEdge,
)
from app.models.phase12_models import (
    OnboardingWizardSession,
    ZeroCodeTestStudioFlow,
    TestLabBrowserWorker,
    TestDataFactoryDataset,
    ReleaseWarRoomMetrics,
    PluginMarketplacePackage,
    EnterpriseIntegrationConfig,
)
from app.models.phase13_models import (
    ExecutionWorkerNode,
    ExecutionQueueItem,
    BrowserFarmSession,
    ExecutionStreamEvent,
    ObservabilityMetric,
    EnterpriseAnalyticsSnapshot,
    ReleaseGovernanceStage,
    ReleaseGovernanceApproval,
    ComplianceReport,
    APIHubKey,
    APIHubWebhook,
    MarketplacePlugin,
    DevOpsPipeline,
    CloudRegionConfig,
    SecurityVaultEntry,
    AIOptimizerLog,
    ExecutiveCommandSnapshot,
)
from app.models.phase14_models import (
    EnterpriseBrainRun,
    WorkflowTemplate,
    WorkflowExecution,
    AgentPackage,
    BusinessProcess,
    BusinessRule,
    ReleaseSimulation,
    Incident,
    IncidentTimeline,
    KnowledgeUniverseNode,
    KnowledgeUniverseEdge,
    ExecutiveInsight,
    OptimizationHistory,
    GovernancePolicy,
    ForecastMetric,
    EnterpriseReport,
)
from app.models.phase15_models import (
    SoftwareGraphNode,
    SoftwareGraphEdge,
    ChangeImpactRecord,
    CodeReviewRecord,
    CoverageMetric,
    ReleaseIntelligence,
    DefectCluster,
    EngineeringMetric,
    QualityKnowledge,
    MissionControlSnapshot,
)
from app.models.phase16_models import (
    KnowledgeLakeV2Document,
    RequirementRecord,
    TraceabilityMapping,
    ArchitectureNode,
    ArchitectureEdge,
    CodeQualityViolation,
    ReleaseCertification,
    ObservabilityMetricV2,
    CustomerFeedbackItem,
    DigitalTwinV2Node,
    PolicyRule,
    ExecutiveDecisionRecord,
    SDLCStageExecution,
)

__all__ = [
    'AgentSuggestion',
    'AuditEvent',
    'AutomatedRun',
    'AutomatedRunCase',
    'AutomatedStepResult',
    'ExecutionArtifact',
    'ExecutionAttempt',
    'ExecutionEvent',
    'ExecutionJob',
    'ExecutionWorker',
    'CompanyTask',
    'ConnectionTarget',
    'ConnectionTargetVersion',
    'Defect',
    'DefectComment',
    'DefectEvidenceLink',
    'DefectHistory',
    'DefectRetest',
    'Evidence',
    'ExternalTaskImport',
    'Operator',
    'OperatorSession',
    'PasswordHistory',
    'Project',
    'ProjectMember',
    'ReportDefinition',
    'ReportExport',
    'TestCase',
    'ManagedTestCase',
    'ManagedTestSuite',
    'ManualEvidence',
    'ManualStepResult',
    'ManualTestRun',
    'ManualTestRunCase',
    'Tag',
    'TestCaseStep',
    'TestCaseTag',
    'TestCaseVersion',
    'TestModule',
    'TestPlan',
    'TestPlanVersion',
    'TestProject',
    'TestResult',
    'TestRun',
    'TestScenario',
    'TestStep',
    'TestSuite',
    'AdvancedValidationProfile',
    'ApiValidationDefinition',
    'DatabaseValidationDefinition',
    'AccessibilityValidationDefinition',
    'PerformanceValidationDefinition',
    'AdvancedValidationRun',
    'AdvancedValidationResult',
    'LocalSchedule',
    'VisualBaseline',
    'VisualBaselineHistory',
    'VisualComparisonRun',
]
