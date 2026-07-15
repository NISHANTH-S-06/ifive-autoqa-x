from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedResult:
  test_name: str
  status: str
  duration_ms: int
  error_message: str | None = None


def parse_playwright_summary(raw_results: list[dict]) -> list[ParsedResult]:
  return [
    ParsedResult(
      test_name=str(item.get('title', 'unknown test')),
      status=str(item.get('status', 'unknown')),
      duration_ms=int(item.get('duration', 0)),
      error_message=item.get('error'),
    )
    for item in raw_results
  ]

