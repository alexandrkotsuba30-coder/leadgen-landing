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

function limitText(value, maxLength) {
  return String(value || "").trim().slice(0, maxLength);
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

  const spamTrap = String(body.website || "").trim();
  if (spamTrap) {
    sendJson(res, 200, { ok: true });
    return;
  }

  const name = limitText(body.name, 80);
  const contact = limitText(body.contact, 80);
  const packageName = limitText(body.packageName || "Не выбрал", 120);
  const niche = limitText(body.niche, 1000);
  const page = limitText(body.page, 300);
  const source = limitText(body.source, 80);
  const utmSource = limitText(body.utm_source, 160);
  const utmMedium = limitText(body.utm_medium, 160);
  const utmCampaign = limitText(body.utm_campaign, 180);
  const utmContent = limitText(body.utm_content, 180);
  const utmTerm = limitText(body.utm_term, 180);

  if (!name || !contact) {
    sendJson(res, 400, { ok: false, error: "Name and contact are required" });
    return;
  }

  if (name.length < 2 || contact.length < 3) {
    sendJson(res, 400, { ok: false, error: "Lead fields are too short" });
    return;
  }

  const text = [
    "Новая заявка с leadcore.by",
    "",
    `Имя: ${name}`,
    `Контакт: ${contact}`,
    `Пакет: ${packageName}`,
    `Ниша/задача: ${niche || "-"}`,
    `Страница: ${page || "-"}`,
    `Источник: ${source || "-"}`,
    "",
    `utm_source: ${utmSource || "-"}`,
    `utm_medium: ${utmMedium || "-"}`,
    `utm_campaign: ${utmCampaign || "-"}`,
    `utm_content: ${utmContent || "-"}`,
    `utm_term: ${utmTerm || "-"}`
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
