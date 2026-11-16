#!/usr/bin/env node
'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const HOST = '127.0.0.1';
const PORT = 3000;
const WEB_ROOT = path.resolve(__dirname, 'web');
const REAL_ROOT = fs.realpathSync(WEB_ROOT);

const TOKEN_FROM_ENV = Boolean(process.env.MEGA_DASHBOARD_TOKEN);
const TOKEN = process.env.MEGA_DASHBOARD_TOKEN || crypto.randomBytes(32).toString('hex');
const TOKEN_HASH = crypto.createHash('sha256').update(TOKEN).digest();

function sendJson(res, status, data, extraHeaders) {
  res.writeHead(status, Object.assign({
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store'
  }, extraHeaders || {}));
  res.end(JSON.stringify(data));
}

// Compara hashes SHA-256 (sempre 32 bytes), entao timingSafeEqual nunca recebe tamanhos diferentes.
function isAuthorized(req) {
  const auth = req.headers.authorization || '';
  const match = auth.match(/^Bearer\s+(.+)$/i);
  if (!match) return false;
  const candidateHash = crypto.createHash('sha256').update(match[1].trim()).digest();
  return crypto.timingSafeEqual(candidateHash, TOKEN_HASH);
}

function resolveStaticPath(pathname) {
  let decoded;
  try {
    decoded = decodeURIComponent(pathname);
  } catch (error) {
    return null;
  }
  if (decoded.includes('\0')) return null;
  const requested = decoded === '/' ? '/index.html' : decoded;
  const filePath = path.resolve(WEB_ROOT, '.' + requested);
  if (!filePath.startsWith(WEB_ROOT + path.sep)) return null;
  return filePath;
}

function safeFileRead(filePath) {
  try {
    const real = fs.realpathSync(filePath);
    if (!real.startsWith(REAL_ROOT + path.sep)) return null;
    if (!fs.statSync(real).isFile()) return null;
    return fs.readFileSync(real);
  } catch (error) {
    return null;
  }
}

function getContentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const map = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.ico': 'image/x-icon'
  };
  return map[ext] || 'application/octet-stream';
}

const server = http.createServer((req, res) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'SAMEORIGIN');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader('Content-Security-Policy', "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self';");

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    return sendJson(res, 405, { error: 'Method Not Allowed' }, { Allow: 'GET, HEAD' });
  }

  let url;
  try {
    url = new URL(req.url, `http://${HOST}:${PORT}`);
  } catch (error) {
    return sendJson(res, 400, { error: 'Bad Request' });
  }

  // API: exige Bearer token. Nao existe rota que devolva o token.
  if (url.pathname.startsWith('/api/')) {
    if (!isAuthorized(req)) {
      return sendJson(res, 401, { error: 'Unauthorized', message: 'Token Bearer invalido ou ausente.' }, {
        'WWW-Authenticate': 'Bearer realm="mega-code-4"'
      });
    }

    if (url.pathname === '/api/health') {
      // Sem verificacao real dos servicos MCP: o estado e "unknown", nunca "ON".
      return sendJson(res, 200, {
        status: 'ok',
        service: 'MEGA-CODE-4',
        host: HOST,
        model: 'unknown',
        mcp: {
          hexstrike: 'unknown',
          cyberstrike: 'unknown'
        },
        timestamp: new Date().toISOString()
      });
    }

    return sendJson(res, 404, { error: 'Not Found' });
  }

  // Arquivos estaticos do dashboard (sem segredos). O token so e exigido na API.
  const filePath = resolveStaticPath(url.pathname);
  if (!filePath) {
    res.writeHead(403);
    return res.end('Forbidden');
  }

  const data = safeFileRead(filePath);
  if (!data) {
    res.writeHead(404);
    return res.end('Not Found');
  }

  res.writeHead(200, { 'Content-Type': getContentType(filePath), 'Cache-Control': 'no-store' });
  res.end(req.method === 'HEAD' ? undefined : data);
});

server.listen(PORT, HOST, () => {
  console.log(`[MEGA-CODE-4] Dashboard em http://${HOST}:${PORT}`);
  if (TOKEN_FROM_ENV) {
    console.log('[MEGA-CODE-4] Usando o token definido em MEGA_DASHBOARD_TOKEN (nao exibido).');
  } else {
    console.log(`[MEGA-CODE-4] Bearer Token (valido so nesta execucao): ${TOKEN}`);
  }
});

process.on('SIGINT', () => server.close(() => process.exit(0)));
process.on('SIGTERM', () => server.close(() => process.exit(0)));
