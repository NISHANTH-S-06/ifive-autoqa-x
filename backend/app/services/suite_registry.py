from dataclasses import dataclass


@dataclass(frozen=True)
class AllowedSuite:
  key: str
  test_file: str


ALLOWED_SUITES = {
  'dashboard-smoke': AllowedSuite('dashboard-smoke', 'tests/dashboard/dashboard.spec.ts'),
  'integration-smoke': AllowedSuite('integration-smoke', 'tests/integration/integration-smoke.spec.ts'),
}


def get_allowed_suite(key: str) -> AllowedSuite | None:
  return ALLOWED_SUITES.get(key)
