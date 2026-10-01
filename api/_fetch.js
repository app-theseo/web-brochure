const net = require('net');
const dns = require('dns').promises;

// Refuse les adresses locales/privées (anti-SSRF).
function isPrivate(ip) {
  if (net.isIPv6(ip)) return /^(::1|fc|fd|fe80)/i.test(ip) || ip === '::';
  const [a, b] = ip.split('.').map(Number);
  return a === 10 || a === 127 || a === 0 || (a === 169 && b === 254) ||
    (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168);
}

module.exports = async function get(raw) {
  const u = new URL(raw);
  if (!/^https?:$/.test(u.protocol)) throw new Error('URL invalide');
  const { address } = await dns.lookup(u.hostname);
  if (isPrivate(address)) throw new Error('Adresse refusée');
  const r = await fetch(u, {
    headers: { 'User-Agent': 'Mozilla/5.0 (compatible; BrochureMVP/1.0)', 'Accept-Language': 'fr,en;q=0.8' },
    redirect: 'follow',
    signal: AbortSignal.timeout(15000),
  });
  if (!r.ok) throw new Error('HTTP ' + r.status);
  return r;
};
