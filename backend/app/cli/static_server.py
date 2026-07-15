import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from app.config import PROJECT_ROOT


class QuietStaticHandler(SimpleHTTPRequestHandler):
  def log_message(self, *_args) -> None:
    return


def run() -> None:
  parser = argparse.ArgumentParser(description='Serve the built AutoQA frontend on loopback without request logging.')
  parser.add_argument('--port', type=int, default=5173)
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
