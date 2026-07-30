from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Company(Base):
    __tablename__ = 'companies'
    __table_args__ = (
        UniqueConstraint('code', name='uq_companies_code'),
        Index('ix_companies_code', 'code'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    code: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    products: Mapped[list['CompanyProduct']] = relationship(back_populates='company', cascade='all, delete-orphan')


class CompanyProduct(Base):
    __tablename__ = 'company_products'
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_company_products_company_code'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    code: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    company: Mapped[Company] = relationship(back_populates='products')
    modules: Mapped[list['CompanyModule']] = relationship(back_populates='product', cascade='all, delete-orphan')


class CompanyModule(Base):
    __tablename__ = 'company_modules'
    __table_args__ = (
        UniqueConstraint('product_id', 'code', name='uq_company_modules_product_code'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('company_products.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    code: Mapped[str] = mapped_column(String(60), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False, default='GENERAL')
    parent_module_id: Mapped[int | None] = mapped_column(ForeignKey('company_modules.id'), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    product: Mapped[CompanyProduct] = relationship(back_populates='modules')
    submodules: Mapped[list['CompanyModule']] = relationship(back_populates='parent_module')
    parent_module: Mapped['CompanyModule | None'] = relationship(back_populates='submodules', remote_side=[id])
