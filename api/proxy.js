const get = require('./_fetch');

module.exports = async (req, res) => {
  try {
    const r = await get(req.query.url);
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.status(200).send(await r.text());
  } catch (e) {
    res.status(502).send(String(e.message || e));
  }
};
