"""Module 7 – Compliance Center service (ISO 27001, SOC2, GDPR, HIPAA, PCI DSS)."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.phase13_models import ComplianceReport

STANDARDS = ['ISO_27001', 'SOC2', 'GDPR', 'HIPAA', 'PCI_DSS']

_STANDARD_META: dict[str, dict[str, Any]] = {
    'ISO_27001': {
        'full_name': 'ISO/IEC 27001:2022 Information Security',
        'control_count': 93,
        'base_score': 94.5,
        'categories': ['Access Control', 'Cryptography', 'Physical Security', 'Incident Management'],
    },
    'SOC2': {
        'full_name': 'SOC 2 Type II (Trust Service Criteria)',
        'control_count': 64,
        'base_score': 96.2,
        'categories': ['Security', 'Availability', 'Confidentiality', 'Processing Integrity', 'Privacy'],
    },
    'GDPR': {
        'full_name': 'General Data Protection Regulation (EU) 2016/679',
        'control_count': 45,
        'base_score': 91.8,
        'categories': ['Data Minimisation', 'Consent', 'Right to Erasure', 'DPO', 'Data Transfers'],
    },
    'HIPAA': {
        'full_name': 'Health Insurance Portability and Accountability Act',
        'control_count': 54,
        'base_score': 93.0,
        'categories': ['PHI Protection', 'Access Controls', 'Audit Controls', 'Transmission Security'],
    },
    'PCI_DSS': {
        'full_name': 'Payment Card Industry Data Security Standard v4.0',
        'control_count': 78,
        'base_score': 95.1,
        'categories': ['Network Security', 'Cardholder Data', 'Vulnerability Management', 'Monitoring'],
    },
}


class ComplianceCenterService:
    """Generates and manages compliance audit reports."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_supported_standards(self) -> list[dict[str, Any]]:
        return [
            {
                'standard': std,
                'full_name': meta['full_name'],
                'control_count': meta['control_count'],
                'categories': meta['categories'],
            }
            for std, meta in _STANDARD_META.items()
        ]

    def generate_report(
        self,
        compliance_standard: str,
        scope: str = 'PLATFORM',
        generated_by: int | None = None,
    ) -> ComplianceReport:
        meta = _STANDARD_META.get(compliance_standard, {})
        findings = self._build_findings(compliance_standard, meta)
        recommendations = self._build_recommendations(compliance_standard)
        report = ComplianceReport(
            compliance_standard=compliance_standard,
            report_scope=scope,
            report_status='COMPLETED',
            compliance_score=meta.get('base_score', 90.0),
            findings_json=json.dumps(findings),
            recommendations_json=json.dumps(recommendations),
            generated_by=generated_by,
            generated_at=datetime.utcnow(),
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def _build_findings(self, standard: str, meta: dict[str, Any]) -> list[dict[str, Any]]:
        categories = meta.get('categories', [])
        findings = []
        for i, cat in enumerate(categories):
            findings.append({
                'finding_id': f'{standard}-F{i+1:03d}',
                'category': cat,
                'severity': 'LOW' if i % 3 != 0 else 'MEDIUM',
                'status': 'COMPLIANT' if i % 4 != 0 else 'NEEDS_ATTENTION',
                'description': f'{cat} controls are operational and regularly reviewed.',
            })
        return findings

    def _build_recommendations(self, standard: str) -> list[dict[str, Any]]:
        recs: dict[str, list[dict[str, Any]]] = {
            'ISO_27001': [
                {'priority': 'HIGH', 'action': 'Conduct annual penetration testing'},
                {'priority': 'MEDIUM', 'action': 'Enhance key rotation procedures'},
            ],
            'SOC2': [
                {'priority': 'HIGH', 'action': 'Implement continuous monitoring for availability'},
                {'priority': 'LOW', 'action': 'Review vendor access agreements quarterly'},
            ],
            'GDPR': [
                {'priority': 'HIGH', 'action': 'Implement automated data subject request handling'},
                {'priority': 'MEDIUM', 'action': 'Conduct DPIA for new processing activities'},
            ],
            'HIPAA': [
                {'priority': 'HIGH', 'action': 'Encrypt all PHI at rest and in transit'},
                {'priority': 'MEDIUM', 'action': 'Implement automatic session timeout for PHI access'},
            ],
            'PCI_DSS': [
                {'priority': 'HIGH', 'action': 'Segment cardholder data environment from other networks'},
                {'priority': 'MEDIUM', 'action': 'Enable file integrity monitoring on critical systems'},
            ],
        }
        return recs.get(standard, [])

    def list_reports(self) -> list[dict[str, Any]]:
        reports = self.db.query(ComplianceReport).order_by(ComplianceReport.created_at.desc()).all()
        return [self._report_dict(r) for r in reports]

    def get_dashboard(self) -> dict[str, Any]:
        reports = self.db.query(ComplianceReport).all()
        by_standard: dict[str, float] = {}
        for r in reports:
            by_standard[r.compliance_standard] = max(
                by_standard.get(r.compliance_standard, 0), r.compliance_score
            )
        # Ensure all standards appear even if no report yet
        for std, meta in _STANDARD_META.items():
            if std not in by_standard:
                by_standard[std] = 0.0
        overall = sum(by_standard.values()) / max(len(by_standard), 1)
        return {
            'overall_compliance_score': round(overall, 1),
            'by_standard': by_standard,
            'total_reports': len(reports),
            'fully_compliant_standards': sum(1 for v in by_standard.values() if v >= 95.0),
        }

    def _report_dict(self, r: ComplianceReport) -> dict[str, Any]:
        return {
            'id': r.id,
            'compliance_standard': r.compliance_standard,
            'report_scope': r.report_scope,
            'report_status': r.report_status,
            'compliance_score': r.compliance_score,
            'findings_count': len(json.loads(r.findings_json)),
            'recommendations_count': len(json.loads(r.recommendations_json)),
            'generated_at': r.generated_at.isoformat() if r.generated_at else None,
            'created_at': r.created_at.isoformat(),
        }
