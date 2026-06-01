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

function getRequiredEnv(name) {
  const value = String(process.env[name] || "").trim();
  return value && value !== '""' ? value : "";
}

function isAuthorized(req) {
  const expectedUser = getRequiredEnv("ADMIN_USERNAME");
  const expectedPassword = getRequiredEnv("ADMIN_PASSWORD");
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
    content: JSON.parse(text)
  };
}

module.exports = async function handler(req, res) {
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
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
    const current = await githubGetContent(token);
    setJson(res, 200, { ok: true, content: current.content });
  } catch (error) {
    setJson(res, 500, { ok: false, error: error.message || "Failed to load content" });
  }
};
