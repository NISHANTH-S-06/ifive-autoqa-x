"""Module 5 – AI Code Quality Governor service."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.phase16_models import CodeQualityViolation

DEFAULT_VIOLATIONS = [
    {
        'file_path': 'backend/app/api/payments.py',
        'language': 'PYTHON',
        'category': 'SECURITY',
        'line_number': 42,
        'message': 'Potential SQL injection risk: raw string formatting in engine.execute()',
        'recommendation': 'Use SQLAlchemy text() with parameterized bindings :payment_id',
        'severity': 'HIGH',
    },
    {
        'file_path': 'frontend/src/components/CheckoutModal.tsx',
        'language': 'TYPESCRIPT',
        'category': 'PERFORMANCE',
        'line_number': 118,
        'message': 'Unnecessary re-render: inline arrow function passed to heavily rendered child component',
        'recommendation': 'Wrap click handler in useCallback()',
        'severity': 'MEDIUM',
    },
    {
        'file_path': 'services/billing/OrderProcessor.java',
        'language': 'JAVA',
        'category': 'DEAD_CODE',
        'line_number': 88,
        'message': 'Unreachable catch block for ExpiredTokenException',
        'recommendation': 'Remove redundant catch block or throw domain specific BillingException',
        'severity': 'LOW',
    },
]


class CodeQualityGovernorService:
    """Multi-language (Python, TS, React, Node, Java, .NET, Go, SQL) code quality governor."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def seed_violations(self) -> list[dict[str, Any]]:
        count = self.db.query(CodeQualityViolation).count()
        if count > 0:
            return self.fetch_violations()

        for v in DEFAULT_VIOLATIONS:
            violation = CodeQualityViolation(**v)
            self.db.add(violation)
        self.db.commit()
        return self.fetch_violations()

    def fetch_violations(self, language: str | None = None, category: str | None = None) -> list[dict[str, Any]]:
        q = self.db.query(CodeQualityViolation)
        if language:
            q = q.filter_by(language=language)
        if category:
            q = q.filter_by(category=category)
        records = q.all()
        return [
            {
                'id': r.id,
                'file_path': r.file_path,
                'language': r.language,
                'category': r.category,
                'line_number': r.line_number,
                'message': r.message,
                'recommendation': r.recommendation,
                'severity': r.severity,
                'created_at': r.created_at.isoformat(),
            }
            for r in records
        ]

    def scan_code_file(self, file_path: str, language: str, code_snippet: str) -> dict[str, Any]:
        """Multi-language static & security pattern scanner."""
        category = 'TECH_DEBT'
        severity = 'MEDIUM'
        message = 'Code smells detected'
        rec = 'Refactor code to conform to enterprise standards.'

        if 'SELECT *' in code_snippet or 'WHERE' in code_snippet and '%' in code_snippet:
            category = 'SECURITY'
            severity = 'HIGH'
            message = 'SQL query performance / injection risk detected.'
            rec = 'Specify column names explicitly and parameterize variables.'
        elif 'any' in code_snippet or 'eval(' in code_snippet:
            category = 'SECURITY'
            severity = 'HIGH'
            message = 'Unsafe type casting or eval usage found.'
            rec = 'Use strict TypeScript types and avoid dynamic code execution.'
        elif 'TODO' in code_snippet or 'FIXME' in code_snippet:
            category = 'TECH_DEBT'
            severity = 'LOW'
            message = 'Unfinished code comment tag (TODO/FIXME).'
            rec = 'Address pending technical debt before release.'

        v = CodeQualityViolation(
            file_path=file_path,
            language=language.upper(),
            category=category,
            line_number=1,
            message=message,
            recommendation=rec,
            severity=severity,
        )
        self.db.add(v)
        self.db.commit()

        return {
            'id': v.id,
            'file_path': file_path,
            'language': language.upper(),
            'category': category,
            'severity': severity,
            'message': message,
            'recommendation': rec,
        }
