import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import urllib.error
import urllib.request

from app.config import PROJECT_ROOT


class QuietStaticHandler(SimpleHTTPRequestHandler):
  def log_message(self, *_args) -> None:
    return

  def end_headers(self) -> None:
    if not self.path.startswith('/api/'):
      self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
      self.send_header('Pragma', 'no-cache')
      self.send_header('Expires', '0')
    super().end_headers()

  def _proxy_api(self):
    backend_port = os.getenv('BACKEND_PORT', '8300')
    target_url = f"http://127.0.0.1:{backend_port}{self.path}"

    content_length = int(self.headers.get('Content-Length', 0))
    body = self.rfile.read(content_length) if content_length > 0 else None

    req_headers = {k: v for k, v in self.headers.items() if k.lower() != 'host'}
    req = urllib.request.Request(target_url, data=body, headers=req_headers, method=self.command)

    try:
      with urllib.request.urlopen(req) as resp:
        self.send_response(resp.status)
        for k, v in resp.headers.items():
          if k.lower() not in ('transfer-encoding', 'content-length'):
            self.send_header(k, v)
        resp_data = resp.read()
        self.send_header('Content-Length', str(len(resp_data)))
        self.end_headers()
        self.wfile.write(resp_data)
    except urllib.error.HTTPError as e:
      self.send_response(e.code)
      for k, v in e.headers.items():
        if k.lower() not in ('transfer-encoding', 'content-length'):
          self.send_header(k, v)
      resp_data = e.read()
      self.send_header('Content-Length', str(len(resp_data)))
      self.end_headers()
      self.wfile.write(resp_data)
    except Exception as e:
      self.send_response(502)
      self.send_header('Content-Type', 'application/json')
      self.end_headers()
      self.wfile.write(f'{{"detail": "Backend proxy error: {str(e)}"}}'.encode('utf-8'))

  def do_GET(self):
    if self.path.startswith('/api/'):
      self._proxy_api()
      return
    path = self.translate_path(self.path)
    if not os.path.exists(path) and not self.path.startswith('/assets/'):
      self.path = '/index.html'
    super().do_GET()

  def do_POST(self):
    if self.path.startswith('/api/'):
      self._proxy_api()
    else:
      self.send_error(501, "Unsupported method ('POST')")

  def do_PATCH(self):
    if self.path.startswith('/api/'):
      self._proxy_api()
    else:
      self.send_error(501, "Unsupported method ('PATCH')")

  def do_DELETE(self):
    if self.path.startswith('/api/'):
      self._proxy_api()
    else:
      self.send_error(501, "Unsupported method ('DELETE')")

  def do_PUT(self):
    if self.path.startswith('/api/'):
      self._proxy_api()
    else:
      self.send_error(501, "Unsupported method ('PUT')")


def run() -> None:
  parser = argparse.ArgumentParser(description='Serve the built AutoQA frontend on loopback with API proxying.')
  default_port = int(os.getenv('FRONTEND_PORT', '3300'))
  parser.add_argument('--port', type=int, default=default_port)

  parser.add_argument('--root', required=True)
  parser.add_argument('--runtime-marker', required=True)
  args = parser.parse_args()
  root = Path(args.root).resolve()
  expected = (PROJECT_ROOT / 'frontend' / 'dist').resolve()
  if Path(args.runtime_marker).resolve() != PROJECT_ROOT.resolve() or root != expected or not (root / 'index.html').is_file():
    raise SystemExit('Static server root or runtime marker is invalid.')
  if not 1024 <= args.port <= 65535:
    raise SystemExit('Static server port is outside the allowed local range.')
  server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(QuietStaticHandler, directory=str(root)))
  try:
    server.serve_forever(poll_interval=0.5)
  except KeyboardInterrupt:
    pass
  finally:
    server.server_close()


if __name__ == '__main__':
  run()

