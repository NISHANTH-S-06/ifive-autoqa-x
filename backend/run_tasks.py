import time
from app.database import SessionLocal
from app.models.company_task import CompanyTask
from app.models.operator import Operator
from app.models.automated_execution import AutomatedRun, ExecutionJob
from app.services.company_task_autoqa import trigger_autoqa_for_task

db = SessionLocal()
admin = db.query(Operator).filter_by(username='admin').first()
task_ids = [6, 7, 11]

# Clean any stale running jobs
db.query(ExecutionJob).filter_by(status='RUNNING').update({'status': 'FAILED'})
db.query(AutomatedRun).filter_by(status='RUNNING').update({'status': 'FAILED'})
db.commit()

for tid in task_ids:
    t = db.get(CompanyTask, tid)
    if not t:
        continue
    t.target_url = 'http://127.0.0.1:5175'
    t.expected_flow = 'Home -> Employees -> Product List'
    t.status = 'TESTING_L2'
    t.retest_count = 0
    db.commit()
    
    run = trigger_autoqa_for_task(db, t, admin.id)
    print(f'Triggered Task #{tid} -> Run #{run.id}')
    time.sleep(15)
    db.refresh(t)
    print(f'Task #{tid} STATUS: {t.status} | RESULT: {t.autoqa_result}')

db.close()
