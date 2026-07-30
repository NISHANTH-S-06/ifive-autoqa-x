from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List, Optional

from app.auth import AuthContext, get_auth_context, require_csrf
from app.database import get_db
from app.models.enterprise_hierarchy import Company, CompanyProduct, CompanyModule

router = APIRouter(tags=['enterprise'], dependencies=[Depends(get_auth_context)])


class CompanyCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class CompanyRead(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    company_id: int
    name: str
    code: str
    description: Optional[str] = None

class ProductRead(BaseModel):
    id: int
    company_id: int
    name: str
    code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class ModuleCreate(BaseModel):
    product_id: int
    name: str
    code: str
    category: str = 'GENERAL'
    parent_module_id: Optional[int] = None
    description: Optional[str] = None

class ModuleRead(BaseModel):
    id: int
    product_id: int
    name: str
    code: str
    category: str
    parent_module_id: Optional[int] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


@router.get('/enterprise/companies', response_model=List[CompanyRead])
def list_companies(db: Session = Depends(get_db)):
    return list(db.scalars(select(Company).order_by(Company.name)))

@router.post('/enterprise/companies', response_model=CompanyRead, status_code=201)
def create_company(payload: CompanyCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
    if context.operator.role not in {'ADMIN', 'SUPER_ADMIN'}:
        raise HTTPException(status_code=403, detail='Super Admin permission required.')
    company = Company(name=payload.name.strip(), code=payload.code.strip().upper(), description=payload.description)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get('/enterprise/products', response_model=List[ProductRead])
def list_products(company_id: Optional[int] = None, db: Session = Depends(get_db)):
    stmt = select(CompanyProduct)
    if company_id:
        stmt = stmt.where(CompanyProduct.company_id == company_id)
    return list(db.scalars(stmt.order_by(CompanyProduct.name)))

@router.post('/enterprise/products', response_model=ProductRead, status_code=201)
def create_product(payload: ProductCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
    if context.operator.role not in {'ADMIN', 'SUPER_ADMIN'}:
        raise HTTPException(status_code=403, detail='Super Admin permission required.')
    product = CompanyProduct(company_id=payload.company_id, name=payload.name.strip(), code=payload.code.strip().upper(), description=payload.description)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get('/enterprise/modules', response_model=List[ModuleRead])
def list_modules(product_id: Optional[int] = None, db: Session = Depends(get_db)):
    stmt = select(CompanyModule)
    if product_id:
        stmt = stmt.where(CompanyModule.product_id == product_id)
    return list(db.scalars(stmt.order_by(CompanyModule.name)))

@router.post('/enterprise/modules', response_model=ModuleRead, status_code=201)
def create_module(payload: ModuleCreate, context: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)):
    if context.operator.role not in {'ADMIN', 'SUPER_ADMIN'}:
        raise HTTPException(status_code=403, detail='Super Admin permission required.')
    mod = CompanyModule(product_id=payload.product_id, name=payload.name.strip(), code=payload.code.strip().upper(), category=payload.category, parent_module_id=payload.parent_module_id, description=payload.description)
    db.add(mod)
    db.commit()
    db.refresh(mod)
    return mod
