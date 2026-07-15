from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ResultStatus(str, Enum):
  PASSED = 'PASSED'
  FAILED = 'FAILED'
  SKIPPED = 'SKIPPED'
  TIMED_OUT = 'TIMED_OUT'


class EvidenceType(str, Enum):
  HTML_REPORT = 'HTML_REPORT'
  JSON_RESULT = 'JSON_RESULT'
  SCREENSHOT = 'SCREENSHOT'
  TRACE = 'TRACE'
  VIDEO = 'VIDEO'
  STDOUT = 'STDOUT'
  STDERR = 'STDERR'


class TestResultRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  test_run_id: int
  test_name: str
  test_file: str
  status: ResultStatus
  duration_seconds: float
  error_message: str | None
  created_at: datetime


class EvidenceRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  test_run_id: int
  test_result_id: int | None
  evidence_type: EvidenceType
  relative_path: str
  file_size_bytes: int
  created_at: datetime
