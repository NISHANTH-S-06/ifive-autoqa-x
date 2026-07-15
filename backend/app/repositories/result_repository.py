from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.test_result import TestResult


class ResultRepository:
  def __init__(self, db: Session):
    self.db = db

  def list_by_run(self, run_id: int) -> list[TestResult]:
    return list(self.db.scalars(select(TestResult).where(TestResult.test_run_id == run_id).order_by(TestResult.id)))

  def evidence_by_run(self, run_id: int) -> list[Evidence]:
    return list(self.db.scalars(select(Evidence).where(Evidence.test_run_id == run_id).order_by(Evidence.id)))

  def get_evidence(self, run_id: int, evidence_id: int) -> Evidence | None:
    return self.db.scalar(select(Evidence).where(Evidence.id == evidence_id, Evidence.test_run_id == run_id))

  def replace_results(self, run_id: int, results: list[dict]) -> list[TestResult]:
    records = [TestResult(test_run_id=run_id, **result) for result in results]
    self.db.add_all(records)
    self.db.flush()
    return records

  def add_evidence(self, run_id: int, items: list[dict]) -> list[Evidence]:
    records = [Evidence(test_run_id=run_id, **item) for item in items]
    self.db.add_all(records)
    self.db.flush()
    return records
