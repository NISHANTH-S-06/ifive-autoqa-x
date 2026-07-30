import ipaddress
import json
import re
import socket
from dataclasses import dataclass
from urllib.parse import urlsplit

from fastapi import HTTPException

from app.config import settings

ALLOWED_SCHEMES = {'http', 'https'}
BLOCKED_METADATA_HOSTS = {'metadata.google.internal', 'metadata', 'instance-data', '169.254.169.254'}
TARGET_KEY_PATTERN = re.compile(r'^[A-Z0-9][A-Z0-9._-]{1,59}$')
HOST_OBFUSCATION_PATTERN = re.compile(r'^(0x[0-9a-f]+|\d+)$', re.I)
SENSITIVE_PATTERN = re.compile(r'(?i)(password|token|secret|authorization|cookie|csrf|bearer)')


@dataclass(frozen=True)
class NormalizedTarget:
  scheme: str
  host: str
  port: int
  origin: str
  base_url: str


def normalize_target_key(value: str) -> str:
  normalized = value.strip().upper()
  if not TARGET_KEY_PATTERN.fullmatch(normalized) or SENSITIVE_PATTERN.search(normalized):
    raise HTTPException(status_code=422, detail='Target key must use letters, numbers, dot, underscore, or hyphen.')
  return normalized


def _has_control(value: str) -> bool:
  return any(ord(ch) < 32 or ord(ch) == 127 for ch in value)


def _normalize_host(raw_host: str | None) -> str:
  if not raw_host:
    raise HTTPException(status_code=422, detail='Target URL host is required.')
  if '%' in raw_host:
    raise HTTPException(status_code=422, detail='IPv6 zone identifiers and encoded host confusion are blocked.')
  host = raw_host.strip().rstrip('.').lower()
  if not host:
    raise HTTPException(status_code=422, detail='Target URL host is required.')
  if HOST_OBFUSCATION_PATTERN.fullmatch(host):
    raise HTTPException(status_code=422, detail='Obfuscated IP hostnames are blocked.')
  if re.search(r'(^|\.)(0[0-9]+)(\.|$)', host):
    raise HTTPException(status_code=422, detail='Octal-looking IP hostnames are blocked.')
  try:
    ipaddress.ip_address(host)
    return host
  except ValueError:
    pass
  try:
    ascii_host = host.encode('idna').decode('ascii')
  except UnicodeError:
    raise HTTPException(status_code=422, detail='Target URL host cannot be normalized safely.') from None
  if not re.fullmatch(r'[a-z0-9.-]{1,255}', ascii_host) or '..' in ascii_host:
    raise HTTPException(status_code=422, detail='Target URL host contains unsupported characters.')
  return ascii_host


def normalize_url(value: str) -> NormalizedTarget:
  raw = value.strip()
  if len(raw) > 1000:
    raise HTTPException(status_code=422, detail='Target URL is too long.')
  if _has_control(raw):
    raise HTTPException(status_code=422, detail='Target URL contains control characters.')
  if raw.startswith(('//', '\\\\')) or re.match(r'^[A-Za-z]:[\\/]', raw):
    raise HTTPException(status_code=422, detail='Target URL must be an absolute http or https URL.')
  parsed = urlsplit(raw)
  scheme = parsed.scheme.lower()
  if scheme not in ALLOWED_SCHEMES:
    raise HTTPException(status_code=422, detail='Only http and https target URLs are allowed.')
  if parsed.username or parsed.password:
    raise HTTPException(status_code=422, detail='Embedded credentials are not allowed in target URLs.')
  if parsed.fragment:
    raise HTTPException(status_code=422, detail='URL fragments are not allowed.')
  if parsed.query:
    raise HTTPException(status_code=422, detail='Base target URL must not include a query string.')
  try:
    port = parsed.port or (443 if scheme == 'https' else 80)
  except ValueError:
    raise HTTPException(status_code=422, detail='Target URL port is invalid.') from None
  if not 1 <= port <= 65535:
    raise HTTPException(status_code=422, detail='Target URL port is invalid.')
  host = _normalize_host(parsed.hostname)
  origin = f'{scheme}://{host}' if port == (443 if scheme == 'https' else 80) else f'{scheme}://{host}:{port}'
  path = parsed.path or '/'
  if path != '/' and (path.startswith('//') or '\\' in path or '..' in path):
    raise HTTPException(status_code=422, detail='Base target path is not allowed.')
  return NormalizedTarget(scheme=scheme, host=host, port=port, origin=origin, base_url=origin)


def validate_environment(environment: str) -> str:
  env = environment.strip().upper()
  if env == 'PRODUCTION':
    raise HTTPException(status_code=403, detail='Production targets are blocked in Stage 9.')
  if env not in {'LOCAL', 'DEVELOPMENT', 'QA', 'STAGING'}:
    raise HTTPException(status_code=422, detail='Unsupported target environment.')
  return env


def validate_tls_policy(environment: str, scheme: str, tls_verify: bool) -> None:
  if scheme == 'https' and not tls_verify and environment not in {'LOCAL', 'DEVELOPMENT'}:
    raise HTTPException(status_code=422, detail='TLS verification can only be disabled for LOCAL or DEVELOPMENT targets.')


def validate_probe_paths(values: list[str]) -> list[str]:
  limit = getattr(settings, 'target_max_probe_paths', 10)
  max_length = getattr(settings, 'target_max_probe_path_length', 500)
  if not values:
    raise HTTPException(status_code=422, detail='At least one probe path is required.')
  if len(values) > limit:
    raise HTTPException(status_code=422, detail='Too many probe paths.')
  normalized: list[str] = []
  seen: set[str] = set()
  for value in values:
    path = value.strip()
    if len(path) > max_length:
      raise HTTPException(status_code=422, detail='Probe path is too long.')
    if _has_control(path) or '\x00' in path:
      raise HTTPException(status_code=422, detail='Probe path contains control characters.')
    if not path.startswith('/'):
      raise HTTPException(status_code=422, detail='Probe path must start with /.')
    if path.startswith('//') or '://' in path or '\\' in path or '..' in path:
      raise HTTPException(status_code=422, detail='Probe path must not contain a host, traversal, or backslash.')
    if '?' in path or '#' in path:
      raise HTTPException(status_code=422, detail='Probe path query strings and fragments are not allowed.')
    if path not in seen:
      normalized.append(path)
      seen.add(path)
  return normalized


def probe_paths_json(values: list[str]) -> str:
  return json.dumps(validate_probe_paths(values), separators=(',', ':'), ensure_ascii=True)


def load_probe_paths(value: str) -> list[str]:
  try:
    parsed = json.loads(value)
  except json.JSONDecodeError:
    return []
  return parsed if isinstance(parsed, list) and all(isinstance(item, str) for item in parsed) else []


def is_address_allowed(address: str, environment: str, host: str) -> bool:
  lowered_host = host.lower()
  if lowered_host in BLOCKED_METADATA_HOSTS:
    return False
  try:
    ip = ipaddress.ip_address(address)
  except ValueError:
    return False
  if ip.is_loopback:
    return environment == 'LOCAL' and lowered_host in {'localhost', '127.0.0.1', '::1'} | ({address} if address in {'127.0.0.1', '::1'} else set())
  if ip.is_unspecified or ip.is_multicast or ip.is_link_local or ip.is_reserved:
    return False
  if ip.version == 4 and address == '255.255.255.255':
    return False
  return True


def resolve_host(host: str, port: int, environment: str) -> list[str]:
  try:
    records = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
  except socket.gaierror:
    raise HTTPException(status_code=502, detail='Target host could not be resolved.') from None
  addresses = sorted({item[4][0] for item in records})
  if not addresses:
    raise HTTPException(status_code=502, detail='Target host could not be resolved.')
  blocked = [address for address in addresses if not is_address_allowed(address, environment, host)]
  if blocked:
    raise HTTPException(status_code=403, detail='Target resolved to a blocked address range.')
  return addresses


def check_probe_allowed(probe_path: str, allowed_paths: list[str]) -> str:
  normalized = validate_probe_paths([probe_path])[0]
  if normalized not in allowed_paths:
    raise HTTPException(status_code=403, detail='Probe path is not approved for this target.')
  return normalized


def validate_same_origin(url: str, expected_origin: str) -> str:
  normalized = normalize_url(url)
  if normalized.origin != expected_origin:
    raise HTTPException(status_code=403, detail='Redirect target origin is not approved.')
  return normalized.origin
