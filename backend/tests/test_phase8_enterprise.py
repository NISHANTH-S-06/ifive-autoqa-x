import pytest
from app.models.enterprise_hierarchy import Company, CompanyProduct, CompanyModule
from app.models.discovery import DiscoveryResult
from app.ai.website_discovery import WebsiteDiscoveryEngine
from app.ai.recommendation_engine import AIRecommendationEngine
from app.ai.bug_analyzer import AIBugAnalyzer


def test_enterprise_hierarchy_creation(db):
    company = Company(name="iFive Technology", code="IFIVE_TEST", description="Enterprise Tech")
    db.add(company)
    db.commit()
    db.refresh(company)

    assert company.id is not None
    assert company.code == "IFIVE_TEST"

    product = CompanyProduct(company_id=company.id, name="iFive ERP", code="ERP_TEST")
    db.add(product)
    db.commit()
    db.refresh(product)

    assert product.id is not None
    assert product.company_id == company.id

    module = CompanyModule(product_id=product.id, name="HRMS Module", code="HRMS_TEST", category="HRMS")
    db.add(module)
    db.commit()
    db.refresh(module)

    assert module.id is not None
    assert module.product_id == product.id


def test_ai_website_discovery_engine():
    engine = WebsiteDiscoveryEngine()
    sample_scan = {
        'title': 'Test ERP Portal',
        'url': 'https://erp.example.com',
        'menus': [{'text': 'Sales Order', 'href': '/sales'}],
        'links': [{'text': 'HRMS Attendance', 'href': '/hrms'}],
        'buttons': [{'text': 'Submit Invoice'}],
        'forms': [{'id': 'form_1'}],
        'tables': [{'id': 'table_1'}]
    }

    res = engine.discover(sample_scan)
    assert res['status'] == 'discovery_complete'
    assert 'module_tree' in res
    assert 'flow_graph' in res
    assert res['flow_graph']['total_nodes'] >= 2


def test_ai_recommendation_engine():
    engine = AIRecommendationEngine()
    discovery_res = {
        'title': 'Demo App',
        'url': 'https://demo.example.com',
        'module_tree': {
            'modules': [{'module_name': 'Sales'}, {'module_name': 'HRMS'}]
        }
    }

    recs = engine.generate_recommendations(discovery_res)
    assert len(recs) >= 12
    categories = {r['category'] for r in recs}
    assert 'SMOKE' in categories
    assert 'CRITICAL_PATH' in categories
    assert 'SECURITY' in categories
    assert 'ACCESSIBILITY' in categories
    assert 'VISUAL_REGRESSION' in categories


def test_ai_bug_analyzer_fingerprint():
    analyzer = AIBugAnalyzer()
    failure_ctx = {
        'error_message': 'Element button.submit not visible',
        'module': 'Sales',
        'url': 'https://example.com/sales'
    }

    res = analyzer.analyze_failure(failure_ctx)
    assert 'fingerprint' in res
    assert len(res['fingerprint']) == 64
    assert res['category'] == 'DOM_INTERACTION'
    assert 'auto_bug' in res
