import json
import random
import string
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.phase12_models import TestDataFactoryDataset

logger = logging.getLogger('autoqa.ai.test_data_factory')


class SmartTestDataFactory:
    """
    Module 6: Smart Test Data Factory
    AI-generates synthetic enterprise datasets: Customers, Products, Invoices,
    Orders, Users, Roles, Permissions, Random, Boundary, Negative,
    Sensitive Masked Data, and Synthetic Enterprise Datasets.
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_dataset(
        self,
        project_id: int,
        category: str,
        record_count: int = 10,
        masked: bool = False,
    ) -> Dict[str, Any]:
        category = category.upper()
        records = self._generate_records(category, record_count, masked)

        dataset = TestDataFactoryDataset(
            project_id=project_id,
            dataset_name=f'{category.title()} Dataset ({record_count} records)',
            data_category=category,
            record_count=len(records),
            is_masked=masked,
            dataset_json=json.dumps(records),
        )
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)

        return {
            'dataset_id': dataset.id,
            'category': category,
            'record_count': len(records),
            'masked': masked,
            'sample_preview': records[:3],
        }

    def _generate_records(self, category: str, count: int, masked: bool) -> List[Dict[str, Any]]:
        generators = {
            'CUSTOMERS': self._gen_customer,
            'PRODUCTS': self._gen_product,
            'INVOICES': self._gen_invoice,
            'ORDERS': self._gen_order,
            'USERS': self._gen_user,
            'ROLES': self._gen_role,
            'PERMISSIONS': self._gen_permission,
            'BOUNDARY': self._gen_boundary,
            'NEGATIVE': self._gen_negative,
            'RANDOM': self._gen_random,
            'SYNTHETIC': self._gen_synthetic,
        }
        gen_fn = generators.get(category, self._gen_random)
        records = [gen_fn(i, masked) for i in range(1, count + 1)]
        return records

    def _mask(self, value: str) -> str:
        if len(value) <= 4:
            return '****'
        return value[:2] + '*' * (len(value) - 4) + value[-2:]

    def _gen_customer(self, i: int, masked: bool) -> Dict:
        email = f'customer{i}@enterprise.com'
        phone = f'+1-555-{random.randint(1000, 9999)}'
        return {
            'id': i,
            'name': f'Enterprise Customer {i}',
            'email': self._mask(email) if masked else email,
            'phone': self._mask(phone) if masked else phone,
            'tier': random.choice(['GOLD', 'SILVER', 'PLATINUM']),
            'country': random.choice(['US', 'UK', 'SG', 'IN', 'AU']),
        }

    def _gen_product(self, i: int, masked: bool) -> Dict:
        return {
            'id': i,
            'sku': f'SKU-{i:05d}',
            'name': f'Enterprise Product {i}',
            'price': round(random.uniform(9.99, 9999.99), 2),
            'stock': random.randint(0, 10000),
            'category': random.choice(['Hardware', 'Software', 'Service']),
        }

    def _gen_invoice(self, i: int, masked: bool) -> Dict:
        return {
            'id': i,
            'invoice_number': f'INV-{i:07d}',
            'amount': round(random.uniform(100, 50000), 2),
            'currency': 'USD',
            'status': random.choice(['PAID', 'PENDING', 'OVERDUE']),
            'due_date': f'2026-0{random.randint(1,9)}-{random.randint(10,28)}',
        }

    def _gen_order(self, i: int, masked: bool) -> Dict:
        return {
            'id': i,
            'order_number': f'ORD-{i:07d}',
            'customer_id': random.randint(1, 100),
            'total_amount': round(random.uniform(50, 20000), 2),
            'status': random.choice(['PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']),
        }

    def _gen_user(self, i: int, masked: bool) -> Dict:
        email = f'user{i}@corp.com'
        return {
            'id': i,
            'username': f'user_{i:04d}',
            'email': self._mask(email) if masked else email,
            'role': random.choice(['ADMIN', 'MANAGER', 'ANALYST', 'VIEWER']),
            'is_active': random.choice([True, False]),
        }

    def _gen_role(self, i: int, masked: bool) -> Dict:
        roles = ['SUPER_ADMIN', 'PROJECT_MANAGER', 'DEVELOPER', 'TESTER', 'VIEWER', 'AUDITOR']
        return {'id': i, 'role_name': roles[i % len(roles)], 'permission_count': random.randint(5, 50)}

    def _gen_permission(self, i: int, masked: bool) -> Dict:
        actions = ['READ', 'WRITE', 'DELETE', 'EXECUTE', 'APPROVE', 'EXPORT']
        resources = ['PROJECTS', 'TESTS', 'REPORTS', 'USERS', 'SETTINGS', 'INTEGRATIONS']
        return {'id': i, 'action': random.choice(actions), 'resource': random.choice(resources), 'granted': True}

    def _gen_boundary(self, i: int, masked: bool) -> Dict:
        return {
            'id': i,
            'field': f'field_{i}',
            'min_value': 0,
            'max_value': 2147483647,
            'below_min': -1,
            'above_max': 2147483648,
            'exact_min': 0,
            'exact_max': 2147483647,
        }

    def _gen_negative(self, i: int, masked: bool) -> Dict:
        negatives = [
            'NULL', '""', 'undefined', '<script>alert(1)</script>',
            "'; DROP TABLE users; --", '../../../etc/passwd',
            'A' * 5001, '-9999999999',
        ]
        return {'id': i, 'test_input': negatives[i % len(negatives)], 'expected_behavior': 'VALIDATION_ERROR'}

    def _gen_random(self, i: int, masked: bool) -> Dict:
        return {
            'id': i,
            'random_string': ''.join(random.choices(string.ascii_letters, k=16)),
            'random_int': random.randint(-100000, 100000),
            'random_float': round(random.uniform(-1000.0, 1000.0), 4),
            'random_bool': random.choice([True, False]),
        }

    def _gen_synthetic(self, i: int, masked: bool) -> Dict:
        return {
            'id': i,
            'entity': f'SyntheticEntity_{i:04d}',
            'department': random.choice(['Finance', 'HR', 'Sales', 'Engineering', 'Marketing']),
            'annual_revenue': round(random.uniform(100000, 10000000), 2),
            'employee_count': random.randint(10, 5000),
            'region': random.choice(['APAC', 'EMEA', 'AMERICAS']),
        }
