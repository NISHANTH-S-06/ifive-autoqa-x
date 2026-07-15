import http.client
import json
import socket
import ssl
from dataclasses import dataclass
from urllib.parse import urljoin

from fastapi import HTTPException

from app.models.connection_target import ConnectionTarget
from app.services.target_policy import resolve_host, validate_same_origin


@dataclass(frozen=True)
class PinnedResponse:
  status_code: int
  headers: dict[str, str]
  body: bytes
  url: str

  @property
  def is_redirect(self) -> bool:
    return self.status_code in {301, 302, 303, 307, 308}

  @property
  def text(self) -> str:
    return self.body.decode('utf-8', errors='replace')


class PinnedTargetSession:
  def __init__(self, target: ConnectionTarget, user_agent: str, timeout_seconds: int, max_response_bytes: int):
    self.target = target
    self.user_agent = user_agent
    self.timeout_seconds = timeout_seconds
    self.max_response_bytes = max_response_bytes
    self.addresses = resolve_host(target.normalized_host, target.normalized_port, target.environment_type)
    self.pinned_address = self.addresses[0]

  def assert_current_resolution(self) -> None:
    current = resolve_host(self.target.normalized_host, self.target.normalized_port, self.target.environment_type)
    if set(current) != set(self.addresses) or self.pinned_address not in current:
      raise HTTPException(status_code=403, detail='DNS rebinding or target address change blocked.')

  def request(self, method: str, path: str, read_body: bool = True) -> PinnedResponse:
    self.assert_current_resolution()
    method = method.upper()
    if method not in {'HEAD', 'GET'}:
      raise HTTPException(status_code=422, detail='Only pinned HEAD and GET requests are allowed.')
    raw_sock = socket.create_connection((self.pinned_address, self.target.normalized_port), timeout=self.timeout_seconds)
    sock = raw_sock
    try:
      if self.target.normalized_scheme == 'https':
        context = ssl.create_default_context()
        if not self.target.tls_verify:
          context.check_hostname = False
          context.verify_mode = ssl.CERT_NONE
        sock = context.wrap_socket(raw_sock, server_hostname=self.target.normalized_host)
      host_header = self.target.normalized_host
      default_port = 443 if self.target.normalized_scheme == 'https' else 80
      if self.target.normalized_port != default_port:
        host_header = f'{host_header}:{self.target.normalized_port}'
      request = (
        f'{method} {path} HTTP/1.1\r\n'
        f'Host: {host_header}\r\n'
        f'User-Agent: {self.user_agent}\r\n'
        'Accept: */*\r\n'
        'Connection: close\r\n'
        '\r\n'
      ).encode('ascii')
      sock.sendall(request)
      response = http.client.HTTPResponse(sock)
      response.begin()
      body = b''
      if method == 'GET' and read_body:
        while len(body) < self.max_response_bytes:
          chunk = response.read(min(8192, self.max_response_bytes - len(body)))
          if not chunk:
            break
          body += chunk
      headers = {key: value for key, value in response.getheaders()}
      return PinnedResponse(response.status, headers, body, f'{self.target.normalized_origin}{path}')
    except ssl.SSLError:
      raise HTTPException(status_code=502, detail='Pinned TLS connection failed.') from None
    except TimeoutError:
      raise HTTPException(status_code=408, detail='Pinned request timed out.') from None
    except OSError:
      raise HTTPException(status_code=502, detail='Pinned connection failed safely.') from None
    finally:
      try:
        sock.close()
      except OSError:
        pass

  def redirect_location(self, response: PinnedResponse) -> str | None:
    for key, value in response.headers.items():
      if key.lower() == 'location':
        absolute = urljoin(response.url, value)
        validate_same_origin(absolute, self.target.normalized_origin)
        self.assert_current_resolution()
        return absolute
    return None

  def audit_metadata(self) -> dict[str, str]:
    return {
      'dns_pinning': 'ENFORCED',
      'pinned_address': self.pinned_address,
      'resolved_addresses': json.dumps(self.addresses, separators=(',', ':')),
    }
