import time
from app.database import SessionLocal
from app.models.company_task import CompanyTask
from app.models.operator import Operator
from app.models.automated_execution import AutomatedRun, ExecutionJob
from app.services.company_task_autoqa import trigger_autoqa_for_task

db = SessionLocal()
admin = db.query(Operator).filter_by(username='admin').first()

db.query(ExecutionJob).filter_by(status='RUNNING').update({'status': 'FAILED'})
db.query(AutomatedRun).filter_by(status='RUNNING').update({'status': 'FAILED'})
db.commit()

# Task 1
t1 = db.get(CompanyTask, 1)
if t1:
    t1.target_url = 'https://ifive.in/'
    t1.expected_flow = 'Home -> Contact Us -> Request Demo'
    t1.status = 'TESTING_L2'
    db.commit()
    r1 = trigger_autoqa_for_task(db, t1, admin.id)
    print(f'Triggered Task #1 -> Run #{r1.id}')
    time.sleep(15)
    db.refresh(t1)
    print(f'Task #1 STATUS: {t1.status} | RESULT: {t1.autoqa_result}')

# Task 10
t10 = db.get(CompanyTask, 10)
if t10:
    t10.target_url = 'https://i5infotech.in/amsak/public/soorder'
    t10.expected_flow = 'Home -> Sign In'
    t10.status = 'TESTING_L2'
    db.commit()
    r10 = trigger_autoqa_for_task(db, t10, admin.id)
    print(f'Triggered Task #10 -> Run #{r10.id}')
    time.sleep(15)
    db.refresh(t10)
    print(f'Task #10 STATUS: {t10.status} | RESULT: {t10.autoqa_result}')

db.close()
