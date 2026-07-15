from app.config import settings


class SafetyViolation(ValueError):
  pass


def validate_environment(environment: str) -> None:
  normalized = environment.strip().lower()
  if normalized == 'production':
    raise SafetyViolation('Production test execution is disabled.')
  if normalized not in settings.allowed_environments:
    raise SafetyViolation(f'Environment is not allowed for AutoQA execution: {environment}')


def validate_action(action: str) -> None:
  normalized = action.strip().lower()
  if settings.safe_mode and normalized in settings.blocked_actions:
    raise SafetyViolation(f'Action is blocked by AutoQA safety policy: {action}')
