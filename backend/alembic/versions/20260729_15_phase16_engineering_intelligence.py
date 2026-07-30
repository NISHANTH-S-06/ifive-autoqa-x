"""Phase 16 – Enterprise Autonomous Software Engineering Intelligence Platform (ASEIP) migration.

Revision ID: 20260729_15_phase16_engineering_intelligence
Revises: 20260729_14_phase15_quality_intelligence
Create Date: 2026-07-29 12:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '20260729_15_phase16_engineering_intelligence'
down_revision: Union[str, None] = '20260729_14_phase15_quality_intelligence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. knowledge_lake_v2_documents
    op.create_table(
        'knowledge_lake_v2_documents',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('source_type', sa.String(length=60), nullable=False),
        sa.Column('title', sa.String(length=250), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('vector_embedding_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('hybrid_search_tags_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_kl_v2_source_type', 'knowledge_lake_v2_documents', ['source_type'])

    # 2. requirement_records
    op.create_table(
        'requirement_records',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('requirement_code', sa.String(length=100), nullable=False, unique=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('requirement_type', sa.String(length=60), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('acceptance_criteria_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('is_ambiguous', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_conflicting', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('analysis_notes', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_requirement_type', 'requirement_records', ['requirement_type'])

    # 3. traceability_mappings
    op.create_table(
        'traceability_mappings',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('requirement_code', sa.String(length=100), nullable=False),
        sa.Column('user_story_key', sa.String(length=100), nullable=False),
        sa.Column('design_doc_ref', sa.String(length=200), nullable=False),
        sa.Column('api_endpoint', sa.String(length=200), nullable=False),
        sa.Column('db_table', sa.String(length=100), nullable=False),
        sa.Column('ui_page', sa.String(length=150), nullable=False),
        sa.Column('test_scenario', sa.String(length=200), nullable=False),
        sa.Column('evidence_url', sa.String(length=300), nullable=False),
        sa.Column('defect_key', sa.String(length=100), nullable=True),
        sa.Column('release_version', sa.String(length=60), nullable=False),
        sa.Column('is_coverage_complete', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_traceability_req', 'traceability_mappings', ['requirement_code'])

    # 4. architecture_nodes
    op.create_table(
        'architecture_nodes',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('node_key', sa.String(length=150), nullable=False, unique=True),
        sa.Column('label', sa.String(length=200), nullable=False),
        sa.Column('node_type', sa.String(length=60), nullable=False),
        sa.Column('is_bottleneck', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('attributes_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_arch_nodes_type', 'architecture_nodes', ['node_type'])

    # 5. architecture_edges
    op.create_table(
        'architecture_edges',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('source_node_id', sa.Integer(), sa.ForeignKey('architecture_nodes.id'), nullable=False),
        sa.Column('target_node_id', sa.Integer(), sa.ForeignKey('architecture_nodes.id'), nullable=False),
        sa.Column('call_protocol', sa.String(length=40), nullable=False, server_default='HTTP_REST'),
        sa.Column('latency_p95_ms', sa.Float(), nullable=False, server_default='12.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # 6. code_quality_violations
    op.create_table(
        'code_quality_violations',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('file_path', sa.String(length=300), nullable=False),
        sa.Column('language', sa.String(length=40), nullable=False),
        sa.Column('category', sa.String(length=60), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('recommendation', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=30), nullable=False, server_default='MEDIUM'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_cq_lang', 'code_quality_violations', ['language'])
    op.create_index('ix_cq_category', 'code_quality_violations', ['category'])

    # 7. release_certifications
    op.create_table(
        'release_certifications',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('release_version', sa.String(length=60), nullable=False),
        sa.Column('certification_status', sa.String(length=40), nullable=False, server_default='CERTIFIED'),
        sa.Column('overall_quality_score', sa.Float(), nullable=False),
        sa.Column('qa_score', sa.Float(), nullable=False),
        sa.Column('security_score', sa.Float(), nullable=False),
        sa.Column('performance_score', sa.Float(), nullable=False),
        sa.Column('accessibility_score', sa.Float(), nullable=False),
        sa.Column('compliance_score', sa.Float(), nullable=False),
        sa.Column('business_rules_score', sa.Float(), nullable=False),
        sa.Column('report_summary', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_release_cert_version', 'release_certifications', ['release_version'])

    # 8. observability_metrics_v2
    op.create_table(
        'observability_metrics_v2',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('error_rate_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('latency_p99_ms', sa.Float(), nullable=False, server_default='45.0'),
        sa.Column('predicted_incident_risk', sa.Float(), nullable=False, server_default='0.05'),
        sa.Column('prediction_summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('metrics_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_obs_v2_service', 'observability_metrics_v2', ['service_name'])

    # 9. customer_feedback_items
    op.create_table(
        'customer_feedback_items',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('source_type', sa.String(length=60), nullable=False),
        sa.Column('headline', sa.String(length=200), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=False, server_default='0.8'),
        sa.Column('nps_score', sa.Integer(), nullable=True),
        sa.Column('correlated_bug_key', sa.String(length=100), nullable=True),
        sa.Column('assigned_developer', sa.String(length=100), nullable=True),
        sa.Column('release_version', sa.String(length=60), nullable=True),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # 10. digital_twin_v2_nodes
    op.create_table(
        'digital_twin_v2_nodes',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('twin_key', sa.String(length=150), nullable=False, unique=True),
        sa.Column('entity_name', sa.String(length=200), nullable=False),
        sa.Column('entity_type', sa.String(length=60), nullable=False),
        sa.Column('health_status', sa.String(length=30), nullable=False, server_default='HEALTHY'),
        sa.Column('live_state_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('last_synced_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # 11. policy_rules
    op.create_table(
        'policy_rules',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('rule_name', sa.String(length=150), nullable=False),
        sa.Column('policy_category', sa.String(length=60), nullable=False),
        sa.Column('rule_condition', sa.Text(), nullable=False),
        sa.Column('action_on_violation', sa.String(length=60), nullable=False, server_default='BLOCK_RELEASE'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_policy_cat', 'policy_rules', ['policy_category'])

    # 12. executive_decision_records
    op.create_table(
        'executive_decision_records',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('decision_type', sa.String(length=60), nullable=False),
        sa.Column('recommendation_summary', sa.Text(), nullable=False),
        sa.Column('reasoning_explanation', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.92'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # 13. sdlc_stage_executions
    op.create_table(
        'sdlc_stage_executions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('stage_name', sa.String(length=60), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='COMPLETED'),
        sa.Column('scheduled_actions_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('execution_notes', sa.Text(), nullable=False, server_default=''),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('sdlc_stage_executions')
    op.drop_table('executive_decision_records')
    op.drop_table('policy_rules')
    op.drop_table('digital_twin_v2_nodes')
    op.drop_table('customer_feedback_items')
    op.drop_table('observability_metrics_v2')
    op.drop_table('release_certifications')
    op.drop_table('code_quality_violations')
    op.drop_table('architecture_edges')
    op.drop_table('architecture_nodes')
    op.drop_table('traceability_mappings')
    op.drop_table('requirement_records')
    op.drop_table('knowledge_lake_v2_documents')
