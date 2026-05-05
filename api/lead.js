async function readJsonBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  if (typeof req.body === "string") return JSON.parse(req.body || "{}");

  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString("utf8");
  return JSON.parse(raw || "{}");
}

function sendJson(res, statusCode, payload) {
  res.statusCode = statusCode;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(payload));
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    sendJson(res, 405, { ok: false, error: "Method not allowed" });
    return;
  }

  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  const threadId = process.env.TELEGRAM_THREAD_ID;

  if (!token || !chatId) {
    sendJson(res, 500, { ok: false, error: "Telegram bot is not configured" });
    return;
  }

  let body;
  try {
    body = await readJsonBody(req);
  } catch (error) {
    sendJson(res, 400, { ok: false, error: "Invalid JSON body" });
    return;
  }

  const name = String(body.name || "").trim();
  const contact = String(body.contact || "").trim();
  const packageName = String(body.packageName || "Не выбрал").trim();
  const niche = String(body.niche || "").trim();
  const page = String(body.page || "").trim();

  if (!name || !contact) {
    sendJson(res, 400, { ok: false, error: "Name and contact are required" });
    return;
  }

  const text = [
    "Новая заявка с reklama-test.by",
    "",
    `Имя: ${name}`,
    `Контакт: ${contact}`,
    `Пакет: ${packageName}`,
    `Ниша/задача: ${niche || "-"}`,
    `Страница: ${page || "-"}`
  ].join("\n");

  const telegramPayload = {
    chat_id: chatId,
    text,
    disable_web_page_preview: true
  };

  if (threadId) telegramPayload.message_thread_id = Number(threadId);

  const telegramResp = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(telegramPayload)
  });

  if (!telegramResp.ok) {
    sendJson(res, 502, { ok: false, error: "Telegram delivery failed" });
    return;
  }

  sendJson(res, 200, { ok: true });
};
