import { normalise } from '../packages/js/src/normalise.js';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Max-Age': '86400',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...CORS },
  });
}

async function readAddress(request, url) {
  if (request.method === 'GET') {
    return url.searchParams.get('address');
  }
  const contentType = request.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    const body = await request.json().catch(() => null);
    return body && typeof body.address === 'string' ? body.address : null;
  }
  if (contentType.includes('application/x-www-form-urlencoded')) {
    const form = await request.formData();
    const v = form.get('address');
    return typeof v === 'string' ? v : null;
  }
  return null;
}

export default {
  async fetch(request) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    const url = new URL(request.url);

    if (url.pathname === '/health') {
      return json({ ok: true });
    }

    if (url.pathname !== '/' && url.pathname !== '/normalise') {
      return json({ error: 'not found' }, 404);
    }

    if (request.method !== 'GET' && request.method !== 'POST') {
      return json({ error: 'method not allowed' }, 405);
    }

    const address = await readAddress(request, url);
    if (!address) {
      return json(
        { error: "missing 'address' (query string for GET, JSON body for POST)" },
        400,
      );
    }

    try {
      return json(normalise(address));
    } catch (err) {
      return json({ error: err.message || String(err) }, 500);
    }
  },
};
