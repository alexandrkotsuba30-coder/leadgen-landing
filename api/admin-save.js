const crypto = require("node:crypto");

const REPO = "alexandrkotsuba30-coder/leadgen-landing";
const BRANCH = "main";
const CONTENT_PATH = "content/site.json";

function setJson(res, statusCode, payload) {
  res.statusCode = statusCode;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(payload));
}

function timingSafeEqual(a, b) {
  const left = Buffer.from(String(a || ""), "utf8");
  const right = Buffer.from(String(b || ""), "utf8");
  if (left.length !== right.length) return false;
  return crypto.timingSafeEqual(left, right);
}

function isAuthorized(req) {
  const expectedUser = process.env.ADMIN_USERNAME || "alex";
  const expectedPassword = process.env.ADMIN_PASSWORD || "alex321";
  const header = req.headers.authorization || "";

  if (!expectedUser || !expectedPassword || !header.startsWith("Basic ")) {
    return false;
  }

  const decoded = Buffer.from(header.slice(6), "base64").toString("utf8");
  const separatorIndex = decoded.indexOf(":");
  if (separatorIndex === -1) return false;

  const user = decoded.slice(0, separatorIndex);
  const password = decoded.slice(separatorIndex + 1);

  return timingSafeEqual(user, expectedUser) && timingSafeEqual(password, expectedPassword);
}

function normalizeContent(content) {
  return {
    seo: {
      title: String(content?.seo?.title || ""),
      description: String(content?.seo?.description || "")
    },
    brand: {
      name: String(content?.brand?.name || "")
    },
    hero: {
      badge: String(content?.hero?.badge || ""),
      title: String(content?.hero?.title || ""),
      subtitle: String(content?.hero?.subtitle || ""),
      primaryCta: String(content?.hero?.primaryCta || ""),
      secondaryCta: String(content?.hero?.secondaryCta || "")
    },
    leadForm: {
      title: String(content?.leadForm?.title || ""),
      subtitle: String(content?.leadForm?.subtitle || ""),
      button: String(content?.leadForm?.button || "")
    },
    contacts: {
      telegramLabel: String(content?.contacts?.telegramLabel || ""),
      telegramUrl: String(content?.contacts?.telegramUrl || ""),
      phoneLabel: String(content?.contacts?.phoneLabel || ""),
      phoneUrl: String(content?.contacts?.phoneUrl || "")
    }
  };
}

async function githubGetContent(token) {
  const response = await fetch(
    `https://api.github.com/repos/${REPO}/contents/${CONTENT_PATH}?ref=${encodeURIComponent(BRANCH)}`,
    {
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${token}`,
        "User-Agent": "LeadCore-Admin"
      }
    }
  );

  const payload = await response.json().catch(function () {
    return {};
  });

  if (!response.ok) {
    throw new Error(payload.message || "GitHub content fetch failed");
  }

  const text = Buffer.from(String(payload.content || "").replace(/\n/g, ""), "base64").toString("utf8");
  return {
    sha: payload.sha,
    text,
    content: JSON.parse(text)
  };
}

async function githubSaveContent(token, sha, text) {
  const response = await fetch(`https://api.github.com/repos/${REPO}/contents/${CONTENT_PATH}`, {
    method: "PUT",
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "User-Agent": "LeadCore-Admin"
    },
    body: JSON.stringify({
      message: `Update LeadCore site content (${new Date().toISOString()})`,
      content: Buffer.from(text, "utf8").toString("base64"),
      branch: BRANCH,
      sha
    })
  });

  const payload = await response.json().catch(function () {
    return {};
  });

  if (!response.ok) {
    throw new Error(payload.message || "GitHub save failed");
  }
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    setJson(res, 405, { ok: false, error: "Method not allowed" });
    return;
  }

  if (!isAuthorized(req)) {
    res.setHeader("WWW-Authenticate", 'Basic realm="LeadCore Admin"');
    setJson(res, 401, { ok: false, error: "Unauthorized" });
    return;
  }

  const token = process.env.GITHUB_TOKEN || "";
  if (!token) {
    setJson(res, 500, { ok: false, error: "GITHUB_TOKEN is missing in Vercel env" });
    return;
  }

  try {
    const incoming = normalizeContent(req.body && req.body.content);
    const current = await githubGetContent(token);
    const nextText = JSON.stringify(incoming, null, 2) + "\n";

    if (current.text === nextText) {
      setJson(res, 200, { ok: true, unchanged: true, content: incoming });
      return;
    }

    await githubSaveContent(token, current.sha, nextText);
    setJson(res, 200, { ok: true, unchanged: false, content: incoming });
  } catch (error) {
    setJson(res, 500, { ok: false, error: error.message || "Failed to save content" });
  }
};
