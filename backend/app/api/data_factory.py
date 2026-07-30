from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import AuthContext, get_auth_context
from app.database import get_db
from app.ai.test_data_factory import SmartTestDataFactory

router = APIRouter(prefix='/data-factory', tags=['test-data-factory'], dependencies=[Depends(get_auth_context)])


@router.post('/generate', summary='Generate Synthetic Enterprise Dataset')
def generate_dataset(
    project_id: int = Query(1),
    category: str = Query('CUSTOMERS'),
    record_count: int = Query(10),
    masked: bool = Query(False),
    context: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    factory = SmartTestDataFactory(db)
    return factory.generate_dataset(project_id, category, record_count, masked)


@router.get('/categories', summary='List Available Data Categories')
def get_categories(context: AuthContext = Depends(get_auth_context)):
    return {
        'categories': [
            'CUSTOMERS', 'PRODUCTS', 'INVOICES', 'ORDERS', 'USERS',
            'ROLES', 'PERMISSIONS', 'RANDOM', 'BOUNDARY', 'NEGATIVE', 'SYNTHETIC',
        ]
    }
