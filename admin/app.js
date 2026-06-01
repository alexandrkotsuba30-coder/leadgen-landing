(function () {
  const loginForm = document.getElementById("loginForm");
  const loginStatus = document.getElementById("loginStatus");
  const editorShell = document.getElementById("editorShell");
  const editorStatus = document.getElementById("editorStatus");
  const reloadButton = document.getElementById("reloadButton");
  const saveButton = document.getElementById("saveButton");

  const state = {
    authHeader: "",
    content: null
  };

  const fields = {
    seoTitle: document.getElementById("seoTitle"),
    seoDescription: document.getElementById("seoDescription"),
    brandName: document.getElementById("brandName"),
    heroBadge: document.getElementById("heroBadge"),
    heroTitle: document.getElementById("heroTitle"),
    heroSubtitle: document.getElementById("heroSubtitle"),
    heroPrimaryCta: document.getElementById("heroPrimaryCta"),
    heroSecondaryCta: document.getElementById("heroSecondaryCta"),
    leadFormTitle: document.getElementById("leadFormTitle"),
    leadFormSubtitle: document.getElementById("leadFormSubtitle"),
    leadFormButton: document.getElementById("leadFormButton"),
    telegramLabel: document.getElementById("telegramLabel"),
    telegramUrl: document.getElementById("telegramUrl"),
    phoneLabel: document.getElementById("phoneLabel"),
    phoneUrl: document.getElementById("phoneUrl")
  };

  function setStatus(node, message, tone) {
    node.textContent = message || "";
    node.className = "status" + (tone ? " " + tone : "");
  }

  function setAuthenticated(isAuthenticated) {
    document.body.classList.toggle("is-authenticated", Boolean(isAuthenticated));
    editorShell.classList.toggle("is-hidden", !isAuthenticated);
  }

  function buildAuthHeader(username, password) {
    return "Basic " + btoa(username + ":" + password);
  }

  function toStringValue(value) {
    return typeof value === "string" ? value : "";
  }

  function applyContent(content) {
    fields.seoTitle.value = toStringValue(content?.seo?.title);
    fields.seoDescription.value = toStringValue(content?.seo?.description);
    fields.brandName.value = toStringValue(content?.brand?.name);
    fields.heroBadge.value = toStringValue(content?.hero?.badge);
    fields.heroTitle.value = toStringValue(content?.hero?.title);
    fields.heroSubtitle.value = toStringValue(content?.hero?.subtitle);
    fields.heroPrimaryCta.value = toStringValue(content?.hero?.primaryCta);
    fields.heroSecondaryCta.value = toStringValue(content?.hero?.secondaryCta);
    fields.leadFormTitle.value = toStringValue(content?.leadForm?.title);
    fields.leadFormSubtitle.value = toStringValue(content?.leadForm?.subtitle);
    fields.leadFormButton.value = toStringValue(content?.leadForm?.button);
    fields.telegramLabel.value = toStringValue(content?.contacts?.telegramLabel);
    fields.telegramUrl.value = toStringValue(content?.contacts?.telegramUrl);
    fields.phoneLabel.value = toStringValue(content?.contacts?.phoneLabel);
    fields.phoneUrl.value = toStringValue(content?.contacts?.phoneUrl);
  }

  function collectContent() {
    return {
      seo: {
        title: fields.seoTitle.value.trim(),
        description: fields.seoDescription.value.trim()
      },
      brand: {
        name: fields.brandName.value.trim()
      },
      hero: {
        badge: fields.heroBadge.value.trim(),
        title: fields.heroTitle.value.trim(),
        subtitle: fields.heroSubtitle.value.trim(),
        primaryCta: fields.heroPrimaryCta.value.trim(),
        secondaryCta: fields.heroSecondaryCta.value.trim()
      },
      leadForm: {
        title: fields.leadFormTitle.value.trim(),
        subtitle: fields.leadFormSubtitle.value.trim(),
        button: fields.leadFormButton.value.trim()
      },
      contacts: {
        telegramLabel: fields.telegramLabel.value.trim(),
        telegramUrl: fields.telegramUrl.value.trim(),
        phoneLabel: fields.phoneLabel.value.trim(),
        phoneUrl: fields.phoneUrl.value.trim()
      }
    };
  }

  async function authedFetch(url, options) {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: state.authHeader,
        ...(options && options.headers ? options.headers : {})
      }
    });

    const payload = await response.json().catch(function () {
      return {};
    });

    if (!response.ok) {
      throw new Error(payload.error || "Request failed");
    }

    return payload;
  }

  async function loadContent() {
    setStatus(editorStatus, "Загружаю текущий контент...", "");
    const payload = await authedFetch("/api/admin-content", { method: "GET" });
    state.content = payload.content || {};
    applyContent(state.content);
    setAuthenticated(true);
    setStatus(editorStatus, "Контент загружен.", "success");
  }

  loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
      setStatus(loginStatus, "Введите логин и пароль.", "error");
      return;
    }

    state.authHeader = buildAuthHeader(username, password);
    setStatus(loginStatus, "Проверяю доступ...", "");

    try {
      await loadContent();
      setStatus(loginStatus, "Доступ подтвержден.", "success");
      document.getElementById("password").value = "";
    } catch (error) {
      setAuthenticated(false);
      setStatus(loginStatus, error.message || "Не удалось войти.", "error");
      setStatus(editorStatus, "", "");
    }
  });

  reloadButton.addEventListener("click", async function () {
    try {
      await loadContent();
    } catch (error) {
      setStatus(editorStatus, error.message || "Не удалось обновить контент.", "error");
    }
  });

  saveButton.addEventListener("click", async function () {
    try {
      saveButton.disabled = true;
      setStatus(editorStatus, "Сохраняю изменения в GitHub...", "");
      const payload = await authedFetch("/api/admin-save", {
        method: "POST",
        body: JSON.stringify({ content: collectContent() })
      });
      state.content = payload.content || collectContent();
      applyContent(state.content);
      setStatus(
        editorStatus,
        payload.unchanged
          ? "Изменений не было."
          : "Готово. Контент сохранен.",
        "success"
      );
    } catch (error) {
      setStatus(editorStatus, error.message || "Не удалось сохранить изменения.", "error");
    } finally {
      saveButton.disabled = false;
    }
  });

  setAuthenticated(false);
})();
