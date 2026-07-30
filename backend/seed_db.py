from app.main import app
from app.database import get_db
from app.models.operator import Operator
from app.models.project import TestProject, ProjectMembership
from app.security import get_password_hash
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def create_op(username, role="ADMIN"):
    op = db.query(Operator).filter_by(username=username).first()
    if not op:
        op = Operator(username=username, email=f"{username}@test.com", password_hash=get_password_hash("autoqa2026"), role=role, is_active=True)
        db.add(op)
        db.flush()
    return op

admin = create_op("admin", "ADMIN")
creator = create_op("creator", "TESTER")
approver = create_op("approver", "MANAGER")
viewer = create_op("viewer", "VIEWER")
dev = create_op("dev", "DEVELOPER")
other_proj_user = create_op("other", "TESTER")

p1 = db.query(TestProject).filter_by(project_code="DEMO").first()
if not p1:
    p1 = TestProject(project_code="DEMO", title="Demo ERP", description="Demo", is_active=True)
    db.add(p1)
    db.flush()

p2 = db.query(TestProject).filter_by(project_code="OTHER").first()
if not p2:
    p2 = TestProject(project_code="OTHER", title="Other", description="Other", is_active=True)
    db.add(p2)
    db.flush()

def add_mem(op, proj, role="TESTER"):
    if not db.query(ProjectMembership).filter_by(operator_id=op.id, project_id=proj.id).first():
        db.add(ProjectMembership(operator_id=op.id, project_id=proj.id, project_role=role))

add_mem(admin, p1, "ADMIN")
add_mem(creator, p1, "TESTER")
add_mem(approver, p1, "MANAGER")
add_mem(viewer, p1, "VIEWER")
add_mem(dev, p1, "DEVELOPER")

add_mem(other_proj_user, p2, "TESTER")

db.commit()
print("DB seeded with users.")
