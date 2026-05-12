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

function listValue(value) {
  if (Array.isArray(value)) return value.filter(Boolean).join(", ");
  return limitText(value, 500);
}

function cutTelegramMessage(text) {
  if (text.length <= 3900) return text;
  return `${text.slice(0, 3900)}\n\n...сообщение обрезано, полный бриф лучше уточнить в переписке.`;
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
  const contact = limitText(body.contact, 100);
  const briefId = limitText(body.briefId, 40);
  const briefMode = limitText(body.briefMode, 40);

  if (!name || !contact) {
    sendJson(res, 400, { ok: false, error: "Name and contact are required" });
    return;
  }

  const submittedAt = new Date().toISOString();
  const text = cutTelegramMessage([
    "Новый бриф с leadcore.by/brief",
    briefId ? `ID брифа: ${briefId}` : "",
    briefMode ? `Режим: ${briefMode === "quick" ? "быстрый" : "полный"}` : "",
    "",
    "Контакты",
    `Имя: ${name}`,
    `Контакт: ${contact}`,
    `Компания/проект: ${limitText(body.company, 160) || "-"}`,
    `Сайт/соцсети: ${limitText(body.projectLink, 240) || "-"}`,
    "",
    "Продукт и рынок",
    `Что продают: ${limitText(body.product, 700) || "-"}`,
    `География: ${limitText(body.geo, 160) || "-"}`,
    `Тип клиента: ${limitText(body.clientType, 120) || "-"}`,
    `Идеальный клиент: ${limitText(body.idealClient, 700) || "-"}`,
    "",
    "Экономика",
    `Средний чек: ${limitText(body.averageCheck, 160) || "-"}`,
    `Маржа/прибыль: ${limitText(body.margin, 160) || "-"}`,
    `Цикл сделки: ${limitText(body.dealCycle, 120) || "-"}`,
    `Допустимая цена лида: ${limitText(body.targetLeadPrice, 160) || "-"}`,
    "",
    "Цель запуска",
    `Главная задача: ${listValue(body.goals) || "-"}`,
    `Что мешает сейчас: ${limitText(body.blockers, 900) || "-"}`,
    "",
    "Оффер и доверие",
    `Сильное предложение: ${limitText(body.offer, 900) || "-"}`,
    `Доказательства доверия: ${limitText(body.proof, 700) || "-"}`,
    `Сомнения клиентов: ${limitText(body.objections, 700) || "-"}`,
    "",
    "Текущий маркетинг",
    `Уже есть: ${listValue(body.assets) || "-"}`,
    `Источники клиентов: ${limitText(body.sources, 700) || "-"}`,
    `Ориентир рекламного бюджета: ${limitText(body.adBudget, 160) || "-"}`,
    "",
    "Финал",
    `Ближайший формат: ${limitText(body.packageName, 160) || "-"}`,
    `Когда стартовать: ${limitText(body.startTime, 120) || "-"}`,
    `Хороший результат: ${limitText(body.successCriteria, 900) || "-"}`,
    "",
    `Страница: ${limitText(body.page, 300) || "-"}`,
    `Время: ${submittedAt}`
  ].join("\n"));

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
