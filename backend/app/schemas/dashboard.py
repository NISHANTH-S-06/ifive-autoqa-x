from pydantic import BaseModel

from app.schemas.test_run import TestRunRead


class DashboardSummary(BaseModel):
  total_projects: int
  active_projects: int
  total_runs: int
  passed_runs: int
  failed_runs: int
  queued_runs: int
  running_runs: int
  pass_rate: float
  total_tests: int
  average_duration_seconds: float
  recent_runs: list[TestRunRead]
