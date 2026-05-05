function sendJson(res, statusCode, payload) {
  res.statusCode = statusCode;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "s-maxage=300, stale-while-revalidate=600");
  res.end(JSON.stringify(payload));
}

module.exports = function handler(req, res) {
  if (req.method !== "GET") {
    sendJson(res, 405, { ok: false, error: "Method not allowed" });
    return;
  }

  sendJson(res, 200, {
    ok: true,
    yandexMetrikaId: process.env.YANDEX_METRIKA_ID || "",
    ga4Id: process.env.GA4_ID || ""
  });
};
