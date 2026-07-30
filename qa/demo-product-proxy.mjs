/**
 * demo-product-proxy.mjs
 * Serves the demo-product frontend (dist/) on port 5175 with API proxy to port 8002.
 * Run from D:\AUTO_QA_TESTING\demo-product\frontend:
 *   node ..\..\qa\demo-product-proxy.mjs
 */

import { createServer } from 'node:http';
import { createReadStream, existsSync, statSync } from 'node:fs';
import { extname, join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { request as httpRequest } from 'node:http';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
const FRONTEND_DIST = resolve(__dirname, '../demo-product/frontend/dist');
const PORT = 5175;
const HOST = '127.0.0.1';
const API_TARGET_HOST = '127.0.0.1';
const API_TARGET_PORT = 8002;

const MIME = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.js',   'text/javascript; charset=utf-8'],
  ['.mjs',  'text/javascript; charset=utf-8'],
  ['.css',  'text/css; charset=utf-8'],
  ['.svg',  'image/svg+xml'],
  ['.ico',  'image/x-icon'],
  ['.png',  'image/png'],
  ['.json', 'application/json'],
  ['.woff', 'font/woff'],
  ['.woff2','font/woff2'],
]);

function safeStaticPath(url) {
  const requested = normalize(decodeURIComponent(new URL(url, `http://${HOST}:${PORT}`).pathname)).replace(/^([/\\])+/, '');
  const candidate = resolve(join(FRONTEND_DIST, requested));
  if (!candidate.startsWith(FRONTEND_DIST)) return join(FRONTEND_DIST, 'index.html');
  if (existsSync(candidate) && statSync(candidate).isFile()) return candidate;
  return join(FRONTEND_DIST, 'index.html');
}

function proxyApiRequest(req, res) {
  const options = {
    hostname: API_TARGET_HOST,
    port: API_TARGET_PORT,
    path: req.url,
    method: req.method,
    headers: {
      ...req.headers,
      host: `${API_TARGET_HOST}:${API_TARGET_PORT}`,
    },
  };

  const proxyReq = httpRequest(options, (proxyRes) => {
    // Forward CORS and other headers from backend, but replace Access-Control-Allow-Origin
    const forwardHeaders = { ...proxyRes.headers };
    forwardHeaders['access-control-allow-origin'] = `http://${HOST}:${PORT}`;
    forwardHeaders['access-control-allow-credentials'] = 'true';
    res.writeHead(proxyRes.statusCode || 200, forwardHeaders);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', (err) => {
    console.error(`Proxy error: ${err.message}`);
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ detail: 'Demo product API proxy error.' }));
  });

  req.pipe(proxyReq);
}

const server = createServer((req, res) => {
  const url = req.url || '/';

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': `http://${HOST}:${PORT}`,
      'Access-Control-Allow-Methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type,Authorization',
      'Access-Control-Allow-Credentials': 'true',
    });
    res.end();
    return;
  }

  // Proxy /api/* to demo product backend
  if (url.startsWith('/api/') || url === '/api') {
    proxyApiRequest(req, res);
    return;
  }

  // Serve static files from dist
  const filePath = safeStaticPath(url);
  const mime = MIME.get(extname(filePath)) ?? 'application/octet-stream';
  res.setHeader('Content-Type', mime);
  createReadStream(filePath).pipe(res);
});

server.listen(PORT, HOST, () => {
  console.log(`Demo product proxy server listening on http://${HOST}:${PORT}`);
  console.log(`  Static files: ${FRONTEND_DIST}`);
  console.log(`  API proxy: /api/* -> http://${API_TARGET_HOST}:${API_TARGET_PORT}`);
});
