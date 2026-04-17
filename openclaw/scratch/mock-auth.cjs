const http = require('http');

const server = http.createServer((req, res) => {
  let body = '';
  req.on('data', chunk => { body += chunk; });
  req.on('end', () => {
    console.log(`[MOCK] Request: ${req.method} ${req.url}`);
    console.log(`[MOCK] Headers: ${JSON.stringify(req.headers, null, 2)}`);
    console.log(`[MOCK] Body: ${body}`);
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
  
  if (req.url.includes('loadCodeAssist')) {
    res.end(JSON.stringify({
      enabled: true,
      user_type: 'INTERNAL',
      features: ['FLASH3', 'OCR', 'AGENT', 'GSD'],
      config: {
        enable_thinking: true,
        max_tokens: 8192
      }
    }));
  } else if (req.url.includes('fetchUserInfo')) {
    res.end(JSON.stringify({
      user: {
        email: 'local@antigravity.mock',
        name: 'Local Developer',
        is_google_internal: true,
        id: '12345'
      },
      auth_token: 'mock-valid-token-12345'
    }));
  } else if (req.url.includes('fetchAdminControls')) {
    res.end(JSON.stringify({
      allowed: true
    }));
  } else {
    res.end(JSON.stringify({ status: 'OK', token: 'mock-token' }));
  }
  });
});

const PORT = 18788;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`Mock Auth Server running on http://0.0.0.0:${PORT}`);
});
