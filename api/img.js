const get = require('./_fetch');

module.exports = async (req, res) => {
  try {
    const r = await get(req.query.url);
    const type = r.headers.get('content-type') || '';
    if (!type.startsWith('image/')) throw new Error('Pas une image');
    res.setHeader('Content-Type', type);
    res.setHeader('Cache-Control', 'public, max-age=3600');
    res.status(200).send(Buffer.from(await r.arrayBuffer()));
  } catch (e) {
    res.status(502).send(String(e.message || e));
  }
};
