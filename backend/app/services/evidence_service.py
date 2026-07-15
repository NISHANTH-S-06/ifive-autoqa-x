EVIDENCE_TYPES = {'screenshot', 'trace', 'video', 'console', 'network'}


def normalize_evidence_type(evidence_type: str) -> str:
  normalized = evidence_type.strip().lower()
  if normalized not in EVIDENCE_TYPES:
    raise ValueError(f'Unsupported evidence type: {evidence_type}')
  return normalized

