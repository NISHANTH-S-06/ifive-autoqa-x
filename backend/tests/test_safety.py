import pytest

from app.security import SafetyViolation, validate_action, validate_environment


def test_validate_environment_allows_qa():
  validate_environment('qa')


def test_validate_environment_blocks_production():
  with pytest.raises(SafetyViolation, match='Production test execution is disabled'):
    validate_environment('production')


def test_validate_action_blocks_payment_execution():
  with pytest.raises(SafetyViolation):
    validate_action('payment_execution')
