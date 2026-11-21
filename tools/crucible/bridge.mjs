// Tiny HTTP bridge: keeps one crucible-mcp session alive, lets shell scripts call tools.
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { createServer } from 'node:http';
import { writeFileSync } from 'node:fs';
const D = process.env.CRU_DIR || process.cwd();
const transport = new StdioClientTransport({
  command: process.execPath,
  args: [`${D}/node_modules/@codepawlhq/crucible/bin/crucible-mcp.mjs`, '--backend', process.env.CRU_BACKEND || 'cpu',
    '--memory', process.env.CRU_MEM || '1024', '--browser', process.env.CRU_BROWSER || '/opt/pw-browsers/chromium',
    '--assets', `${D}/assets`, '--jobs', `${D}/jobs`, '--audio', `${D}/audio`, '--ffmpeg', '/usr/bin/ffmpeg'],
  stderr: 'inherit',
});
const client = new Client({ name: 'reel-bridge', version: '1.0.0' });
await client.connect(transport);
let n = 0;
createServer(async (req, res) => {
  let body = ''; for await (const c of req) body += c;
  try {
    if (req.url === '/tools') { const t = await client.listTools(); res.end(JSON.stringify(t.tools.map(x => x.name))); return; }
    const { name, args, img } = JSON.parse(body);
    const r = await client.callTool({ name, arguments: args || {} }, undefined, { timeout: 600000 });
    const out = [];
    for (const c of r.content || []) {
      if (c.type === 'image') { const p = img || `${D}/out/img-${++n}.png`; writeFileSync(p, Buffer.from(c.data, 'base64')); out.push({ image: p }); }
      else out.push(c.text ?? c);
    }
    res.end(JSON.stringify({ isError: r.isError, out }, null, 1));
  } catch (e) { res.statusCode = 500; res.end(String(e?.stack || e)); }
}).listen(7777, '127.0.0.1', () => console.error('bridge on 7777'));
