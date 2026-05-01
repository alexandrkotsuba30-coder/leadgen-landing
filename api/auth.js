module.exports = async function handler(req, res) {
  const clientId = process.env.GITHUB_OAUTH_CLIENT_ID;
  const siteUrl = process.env.SITE_URL || "https://www.reklama-test.by";

  if (!clientId) {
    res.statusCode = 500;
    res.end("Missing GITHUB_OAUTH_CLIENT_ID");
    return;
  }

  const state = Math.random().toString(36).slice(2);
  const redirectUri = `${siteUrl}/api/callback`;
  const authUrl =
    "https://github.com/login/oauth/authorize" +
    `?client_id=${encodeURIComponent(clientId)}` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}` +
    `&scope=${encodeURIComponent("repo")}` +
    `&state=${encodeURIComponent(state)}`;

  res.statusCode = 302;
  res.setHeader("Location", authUrl);
  res.end();
};
