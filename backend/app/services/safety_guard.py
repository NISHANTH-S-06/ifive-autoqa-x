from app.security import validate_action, validate_environment


def assert_safe_execution(environment: str, requested_actions: list[str]) -> None:
  validate_environment(environment)
  for action in requested_actions:
    validate_action(action)

