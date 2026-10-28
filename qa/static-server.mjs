import { createServer } from 'node:http';
import { createReadStream, existsSync, statSync } from 'node:fs';
import { extname, join, normalize, resolve } from 'node:path';

const root = resolve('../frontend/dist');
const port = Number(process.env.FRONTEND_PORT ?? process.env.AUTOQA_STATIC_PORT ?? 3300);

const host = '127.0.0.1';
const types = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.ico', 'image/x-icon'],
  ['.png', 'image/png'],
]);

function safePath(url) {
  const requested = normalize(decodeURIComponent(new URL(url, `http://${host}:${port}`).pathname)).replace(/^([/\\])+/, '');
  const candidate = resolve(join(root, requested));
  if (!candidate.startsWith(root)) return join(root, 'index.html');
  if (existsSync(candidate) && statSync(candidate).isFile()) return candidate;
  return join(root, 'index.html');
}

createServer((request, response) => {
  const path = safePath(request.url ?? '/');
  response.setHeader('Content-Type', types.get(extname(path)) ?? 'application/octet-stream');
  createReadStream(path).pipe(response);
}).listen(port, host, () => {
  console.log(`Static server listening on http://${host}:${port}`);
});
