"""Module 4 – AI Business Process Understanding service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase14_models import BusinessProcess, BusinessRule

DOMAIN_TYPES = [
    'HRMS', 'PAYROLL', 'RECRUITMENT', 'CRM', 'SALES',
    'INVENTORY', 'MANUFACTURING', 'FINANCE', 'PROCUREMENT',
    'HEALTHCARE', 'INSURANCE', 'BANKING', 'EDUCATION', 'ERP',
]

DEFAULT_PROCESSES = [
    {
        'process_name': 'Global Employee Onboarding & Payroll Sync',
        'domain_type': 'HRMS',
        'risk_score': 88.5,
        'is_critical_path': True,
        'flow_graph': {
            'nodes': ['Create Employee', 'Assign Benefits', 'Configure Tax Profile', 'Run Initial Payroll', 'Issue Bank Transfer'],
            'edges': [('Create Employee', 'Assign Benefits'), ('Assign Benefits', 'Configure Tax Profile'), ('Configure Tax Profile', 'Run Initial Payroll'), ('Run Initial Payroll', 'Issue Bank Transfer')],
        },
        'rules': [
            {'rule_name': 'Tax ID Validation', 'rule_condition': 'employee.tax_id IS NOT NULL', 'severity': 'CRITICAL'},
            {'rule_name': 'Double Payroll Check', 'rule_condition': 'payroll.run_count == 1', 'severity': 'HIGH'},
        ]
    },
    {
        'process_name': 'Order-to-Cash Enterprise Flow',
        'domain_type': 'ERP',
        'risk_score': 94.0,
        'is_critical_path': True,
        'flow_graph': {
            'nodes': ['Receive PO', 'Check Inventory', 'Generate Invoice', 'Ship Goods', 'Reconcile Payment'],
            'edges': [('Receive PO', 'Check Inventory'), ('Check Inventory', 'Generate Invoice'), ('Generate Invoice', 'Ship Goods'), ('Ship Goods', 'Reconcile Payment')],
        },
        'rules': [
            {'rule_name': 'Credit Limit Enforcement', 'rule_condition': 'customer.credit_used <= customer.credit_limit', 'severity': 'CRITICAL'},
            {'rule_name': 'Inventory Lock', 'rule_condition': 'inventory.quantity >= order.quantity', 'severity': 'HIGH'},
        ]
    },
    {
        'process_name': 'Core Banking Wire Transfer & KYC',
        'domain_type': 'BANKING',
        'risk_score': 98.2,
        'is_critical_path': True,
        'flow_graph': {
            'nodes': ['KYC Verification', 'AML Screen', 'Debit Account', 'Credit Beneficiary', 'Audit Log'],
            'edges': [('KYC Verification', 'AML Screen'), ('AML Screen', 'Debit Account'), ('Debit Account', 'Credit Beneficiary'), ('Credit Beneficiary', 'Audit Log')],
        },
        'rules': [
            {'rule_name': 'AML Blacklist Check', 'rule_condition': 'beneficiary NOT IN aml_watchlist', 'severity': 'CRITICAL'},
            {'rule_name': 'Sufficient Balance', 'rule_condition': 'account.balance >= transfer.amount', 'severity': 'CRITICAL'},
        ]
    }
]


class BusinessProcessCenterService:
    """Manages industry-specific business process flow graphs and critical rules."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_processes(self) -> list[dict[str, Any]]:
        existing = self.db.query(BusinessProcess).count()
        if existing > 0:
            return self.list_processes()

        for dp in DEFAULT_PROCESSES:
            bp = BusinessProcess(
                process_name=dp['process_name'],
                domain_type=dp['domain_type'],
                risk_score=dp['risk_score'],
                is_critical_path=dp['is_critical_path'],
                flow_graph_json=json.dumps(dp['flow_graph']),
            )
            self.db.add(bp)
            self.db.flush()

            for r in dp['rules']:
                rule = BusinessRule(
                    process_id=bp.id,
                    rule_name=r['rule_name'],
                    rule_condition=r['rule_condition'],
                    severity=r['severity'],
                )
                self.db.add(rule)

        self.db.commit()
        return self.list_processes()

    def list_processes(self, domain_type: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(BusinessProcess)
        if domain_type:
            q = q.filter_by(domain_type=domain_type)
        processes = q.order_by(BusinessProcess.risk_score.desc()).all()
        return [self._process_dict(p) for p in processes]

    def create_process(
        self,
        process_name: str,
        domain_type: str,
        risk_score: float = 50.0,
        is_critical_path: bool = True,
        flow_graph: dict[str, Any] | None = None,
        project_id: int | None = None,
    ) -> dict[str, Any]:
        bp = BusinessProcess(
            project_id=project_id,
            process_name=process_name,
            domain_type=domain_type,
            risk_score=risk_score,
            is_critical_path=is_critical_path,
            flow_graph_json=json.dumps(flow_graph or {}),
        )
        self.db.add(bp)
        self.db.commit()
        self.db.refresh(bp)
        return self._process_dict(bp)

    def _process_dict(self, p: BusinessProcess) -> dict[str, Any]:
        rules = self.db.query(BusinessRule).filter_by(process_id=p.id).all()
        return {
            'id': p.id,
            'process_name': p.process_name,
            'domain_type': p.domain_type,
            'risk_score': p.risk_score,
            'is_critical_path': p.is_critical_path,
            'flow_graph': json.loads(p.flow_graph_json),
            'rules': [
                {
                    'id': r.id,
                    'rule_name': r.rule_name,
                    'rule_condition': r.rule_condition,
                    'severity': r.severity,
                    'is_active': r.is_active,
                }
                for r in rules
            ],
            'created_at': p.created_at.isoformat(),
        }
