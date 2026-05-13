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

function maskPhone(phone) {
  const normalized = String(phone || "").trim();
  if (normalized.length <= 5) return normalized;
  return `${normalized.slice(0, 3)}***${normalized.slice(-2)}`;
}

function isValidPhone(value) {
  const digits = String(value || "").replace(/\D/g, "");
  return digits.length >= 9 && digits.length <= 15;
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

  const phone = limitText(body.phone, 40);
  const name = limitText(body.name, 80);
  const telegram = limitText(body.telegram, 80);
  const consent = Boolean(body.consent);
  const sourcePage = limitText(body.page, 300);
  const utmSource = limitText(body.utmSource, 120);
  const utmMedium = limitText(body.utmMedium, 120);
  const utmCampaign = limitText(body.utmCampaign, 120);
  const utmTerm = limitText(body.utmTerm, 120);
  const utmContent = limitText(body.utmContent, 120);
  const gclid = limitText(body.gclid, 120);
  const yclid = limitText(body.yclid, 120);

  if (!phone || !isValidPhone(phone)) {
    sendJson(res, 400, { ok: false, error: "Valid phone is required" });
    return;
  }

  if (!consent) {
    sendJson(res, 400, { ok: false, error: "Consent is required" });
    return;
  }

  const forwardedFor = limitText(req.headers["x-forwarded-for"], 120);
  const userAgent = limitText(req.headers["user-agent"], 260);
  const submittedAt = new Date().toISOString();

  const text = [
    "Новый PDF-лид с leadcore.by/pdf",
    "",
    `Телефон: ${phone}`,
    `Имя: ${name || "-"}`,
    `Telegram: ${telegram || "-"}`,
    `Согласие: ${consent ? "да" : "нет"}`,
    "",
    "UTM и клики",
    `utm_source: ${utmSource || "-"}`,
    `utm_medium: ${utmMedium || "-"}`,
    `utm_campaign: ${utmCampaign || "-"}`,
    `utm_term: ${utmTerm || "-"}`,
    `utm_content: ${utmContent || "-"}`,
    `gclid: ${gclid || "-"}`,
    `yclid: ${yclid || "-"}`,
    "",
    `Страница: ${sourcePage || "-"}`,
    `IP (x-forwarded-for): ${forwardedFor || "-"}`,
    `User-Agent: ${userAgent || "-"}`,
    `Время: ${submittedAt}`
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
    sendJson(res, 502, {
      ok: false,
      error: "Telegram delivery failed",
      debugPhone: maskPhone(phone)
    });
    return;
  }

  sendJson(res, 200, { ok: true });
};
