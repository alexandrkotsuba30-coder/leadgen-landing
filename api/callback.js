function renderResultPage(payloadScript) {
  return `<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Auth</title></head>
  <body>
    <script>
      ${payloadScript}
    </script>
  </body>
</html>`;
}

module.exports = async function handler(req, res) {
  const clientId = process.env.GITHUB_OAUTH_CLIENT_ID;
  const clientSecret = process.env.GITHUB_OAUTH_CLIENT_SECRET;
  const siteUrl = process.env.SITE_URL || "https://www.reklama-test.by";

  if (!clientId || !clientSecret) {
    res.statusCode = 500;
    res.end("Missing GitHub OAuth env vars");
    return;
  }

  const { code, state, error, error_description: errorDescription } = req.query || {};
  if (error) {
    const html = renderResultPage(`
      window.opener && window.opener.postMessage("authorization:github:error:${errorDescription || error}", "*");
      window.close();
    `);
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.end(html);
    return;
  }

  if (!code) {
    res.statusCode = 400;
    res.end("Missing OAuth code");
    return;
  }

  const tokenResp = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      client_id: clientId,
      client_secret: clientSecret,
      code,
      state,
      redirect_uri: `${siteUrl}/api/callback`
    })
  });

  const tokenData = await tokenResp.json();
  if (!tokenResp.ok || tokenData.error || !tokenData.access_token) {
    const err = tokenData.error_description || tokenData.error || "OAuth token exchange failed";
    const html = renderResultPage(`
      window.opener && window.opener.postMessage("authorization:github:error:${err}", "*");
      window.close();
    `);
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.end(html);
    return;
  }

  const payload = JSON.stringify({
    token: tokenData.access_token,
    provider: "github"
  });

  const html = renderResultPage(`
    window.opener && window.opener.postMessage("authorizing:github", "*");
    window.opener && window.opener.postMessage("authorization:github:success:${payload}", "*");
    window.close();
  `);
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.end(html);
};
