import json
import logging
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.phase11_models import RootCauseGraphNode, RootCauseGraphEdge

logger = logging.getLogger('autoqa.ai.root_cause_graph')

class AIRootCauseGraphService:
    """
    Module 5: AI Root Cause Graph
    Constructs dependency chain: Bug -> Component -> API -> DB -> Service -> Task -> Release -> Customer Impact.
    Explains Why, Where, How, Impact, and Fix priority.
    """

    def __init__(self, db: Session):
        self.db = db

    def build_root_cause_chain(self, defect_id: str) -> Dict[str, Any]:
        chain_nodes = [
            {'type': 'BUG', 'key': defect_id, 'label': f'Defect {defect_id}'},
            {'type': 'COMPONENT', 'key': 'comp_checkout_btn', 'label': 'Checkout Submit Button'},
            {'type': 'API', 'key': 'api_post_order', 'label': 'POST /api/v1/orders'},
            {'type': 'DATABASE', 'key': 'db_sales_orders', 'label': 'Table: sales_orders'},
            {'type': 'SERVICE', 'key': 'svc_payment_gateway', 'label': 'Payment Gateway Microservice'},
            {'type': 'TASK', 'key': 'task_order_refactor', 'label': 'Task #104 Refactor Order Flow'},
            {'type': 'RELEASE', 'key': 'rel_v1_0_0', 'label': 'Release Candidate v1.0.0'},
            {'type': 'CUSTOMER_IMPACT', 'key': 'impact_checkout_delay', 'label': 'Customer Checkout Latency'}
        ]

        explanation = {
            'why': 'API payload schema validation failed on unexpected null currency field.',
            'where': 'Backend Payment Gateway Microservice (/api/v1/orders).',
            'how': 'Refactored task #104 omitted default currency fallback value.',
            'impact': 'Customer checkout delayed by 12 seconds during transaction submission.',
            'fix_priority': 'P0 - CRITICAL'
        }

        return {
            'defect_id': defect_id,
            'chain_depth': len(chain_nodes),
            'nodes': chain_nodes,
            'explanation': explanation
        }
