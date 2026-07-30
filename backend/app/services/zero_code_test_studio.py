import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.phase12_models import ZeroCodeTestStudioFlow

logger = logging.getLogger('autoqa.services.zero_code_test_studio')

FLOW_TYPES = [
    'SCENARIO', 'VISUAL_ASSERTION', 'API', 'DB_VALIDATION', 'BUSINESS_RULE',
    'DRAG_DROP', 'FLOW_BUILDER', 'VALIDATION_BUILDER', 'DATA_BUILDER',
]


class ZeroCodeTestStudioService:
    """
    Module 3: Zero-Code Test Studio
    Enables Drag & Drop Visual Test Builder, Flow Builder, Scenario Builder,
    Validation Builder, Test Data Builder, API Builder, DB Validation Builder,
    Visual Assertion Builder, Business Rule Builder. No scripting required.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_flow(
        self,
        project_id: int,
        flow_name: str,
        flow_type: str,
        flow_steps: List[Dict[str, Any]],
        created_by: Optional[int] = None,
    ) -> ZeroCodeTestStudioFlow:
        flow = ZeroCodeTestStudioFlow(
            project_id=project_id,
            flow_name=flow_name,
            flow_type=flow_type.upper(),
            flow_definition_json=json.dumps(flow_steps),
            is_active=True,
            created_by=created_by,
        )
        self.db.add(flow)
        self.db.commit()
        self.db.refresh(flow)
        return flow

    def list_flows(self, project_id: int) -> List[Dict[str, Any]]:
        flows = self.db.query(ZeroCodeTestStudioFlow).filter(
            ZeroCodeTestStudioFlow.project_id == project_id
        ).all()
        return [
            {
                'id': f.id,
                'flow_name': f.flow_name,
                'flow_type': f.flow_type,
                'step_count': len(json.loads(f.flow_definition_json or '[]')),
                'is_active': f.is_active,
                'created_at': f.created_at,
            }
            for f in flows
        ]

    def get_available_step_types(self) -> Dict[str, Any]:
        """Return the full palette of zero-code step types."""
        return {
            'actions': [
                'CLICK', 'DOUBLE_CLICK', 'RIGHT_CLICK', 'TYPE', 'CLEAR',
                'SELECT_OPTION', 'CHECK', 'UNCHECK', 'HOVER', 'SCROLL',
                'DRAG_AND_DROP', 'UPLOAD_FILE', 'PRESS_KEY', 'WAIT',
            ],
            'assertions': [
                'ASSERT_TEXT', 'ASSERT_VISIBLE', 'ASSERT_HIDDEN',
                'ASSERT_URL', 'ASSERT_TITLE', 'ASSERT_COUNT',
                'ASSERT_ATTRIBUTE', 'VISUAL_BASELINE_MATCH',
            ],
            'data_operations': [
                'DB_QUERY', 'DB_ASSERT', 'API_CALL', 'API_ASSERT',
                'SET_VARIABLE', 'USE_TEST_DATA', 'MASK_SENSITIVE_FIELD',
            ],
            'flow_controls': [
                'IF_CONDITION', 'ELSE_BRANCH', 'LOOP_UNTIL', 'RETRY_ON_FAIL',
                'PARALLEL_BRANCH', 'WAIT_FOR_ELEMENT', 'WAIT_FOR_API',
            ],
        }
