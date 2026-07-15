import base64
import hashlib
import hmac
import re
import secrets

ITERATIONS = 600_000
COMMON = {
  'password', 'password123', 'password123!', 'changeme', 'changeme123!', 'admin',
  'admin123456!', 'welcome', 'welcome123!', 'letmein', 'qwerty123!', 'temporary123!',
}


def normalize_username(username: str) -> str:
  normalized = username.strip().lower()
  if not re.fullmatch(r'[a-z0-9][a-z0-9._-]{2,79}', normalized):
    raise ValueError('Username must be 3-80 characters using letters, numbers, dot, underscore, or hyphen.')
  return normalized


def _display_name_tokens(display_name: str | None) -> set[str]:
  if not display_name: return set()
  compact = re.sub(r'[^a-z0-9]', '', display_name.lower())
  tokens = {item for item in re.split(r'[^a-z0-9]+', display_name.lower()) if len(item) >= 3}
  if len(compact) >= 3: tokens.add(compact)
  return tokens


def _is_sequential_number(value: str) -> bool:
  if not value.isdigit() or len(value) < 4: return False
  ascending = '01234567890123456789'
  descending = '98765432109876543210'
  return value in ascending or value in descending


def password_policy_errors(password: str, username: str, display_name: str | None = None) -> list[str]:
  errors: list[str] = []
  normalized_username = normalize_username(username)
  lowered = password.lower()
  if len(password) < 12: errors.append('Password must be at least 12 characters.')
  if not re.search(r'[A-Z]', password): errors.append('Password must include an uppercase letter.')
  if not re.search(r'[a-z]', password): errors.append('Password must include a lowercase letter.')
  if not re.search(r'\d', password): errors.append('Password must include a number.')
  if not re.search(r'[^A-Za-z0-9]', password): errors.append('Password must include a special character.')
  if normalized_username and normalized_username in lowered: errors.append('Password must not contain the username.')
  if any(token in lowered for token in _display_name_tokens(display_name)): errors.append('Password must not contain the display name.')
  if lowered in COMMON or any(common in lowered for common in COMMON): errors.append('Common placeholder passwords are not allowed.')
  if len(password) >= 4 and re.fullmatch(r'(.)\1+', password): errors.append('Repeated-character passwords are not allowed.')
  if _is_sequential_number(password): errors.append('Sequential-number passwords are not allowed.')
  return errors


def validate_password(password: str, username: str, display_name: str | None = None) -> None:
  errors = password_policy_errors(password, username, display_name)
  if errors:
    raise ValueError(' '.join(errors))


def hash_password(password: str) -> str:
  salt = secrets.token_bytes(16)
  digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, ITERATIONS)
  return f'pbkdf2_sha256${ITERATIONS}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}'


def verify_password(password: str, encoded: str) -> bool:
  try:
    algorithm, iterations, salt, expected = encoded.split('$', 3)
    if algorithm != 'pbkdf2_sha256': return False
    actual = hashlib.pbkdf2_hmac('sha256', password.encode(), base64.urlsafe_b64decode(salt), int(iterations))
    return hmac.compare_digest(actual, base64.urlsafe_b64decode(expected))
  except (ValueError, TypeError):
    return False


def hash_secret(value: str) -> str:
  return hashlib.sha256(value.encode()).hexdigest()
