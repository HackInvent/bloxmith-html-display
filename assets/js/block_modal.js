(function () {
  "use strict";

  const registry = (window.CWBlockUiBlocks = window.CWBlockUiBlocks || {});

  /**
   * Read the HTML payload currently displayed by the modal preview source.
   *
   * @param {HTMLElement} root - Mounted HTML Display modal root.
   * @returns {string} Raw HTML text to preview.
   */
  function previewSource(root) {
    const source = root.querySelector("[data-html-display-preview-source]");
    if (source instanceof HTMLTextAreaElement) {
      return source.value;
    }
    return source?.textContent || "";
  }

  /**
   * Build the standalone preview document shown in a new browser tab.
   *
   * @param {string} html - User-provided HTML fragment or document.
   * @param {boolean} allowScripts - Whether scripts should be allowed in the preview.
   * @returns {string} Full HTML document when scripts are blocked, otherwise the raw HTML.
   */
  function previewDocument(html, allowScripts) {
    const content = String(html || "");
    if (allowScripts) {
      return content;
    }
    return [
      "<!doctype html>",
      '<html><head><meta charset="utf-8">',
      '<meta http-equiv="Content-Security-Policy" content="script-src \'none\'; object-src \'none\'; base-uri \'none\'">',
      "<title>HTML Display Preview</title></head><body>",
      content,
      "</body></html>",
    ].join("");
  }

  /**
   * Open the current HTML payload in a temporary browser tab.
   *
   * @param {HTMLElement} root - Mounted HTML Display modal root.
   * @param {object} api - Generic block UI API used for log messages.
   */
  function openPreview(root, api) {
    const html = previewSource(root);
    if (!html.trim()) {
      api.log?.("[html-display] Aucun HTML a visualiser.");
      return;
    }
    const allowScripts = root.dataset.htmlDisplayAllowScripts === "true";
    const blob = new Blob([previewDocument(html, allowScripts)], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const opened = window.open(url, "_blank", "noopener");
    window.setTimeout(() => URL.revokeObjectURL(url), 30000);
    if (!opened) {
      api.log?.("[html-display] Ouverture du rendu HTML bloquee par le navigateur.");
    }
  }

  registry.html_display = {
    /**
     * Bind the preview action without changing persistence behavior.
     *
     * @param {HTMLElement} root - Mounted HTML Display modal root.
     * @param {object} api - Generic block UI API.
     */
    mount(root, api) {
      root.addEventListener("click", (event) => {
        const button = event.target.closest("[data-html-display-open-preview]");
        if (!button) {
          return;
        }
        event.preventDefault();
        openPreview(root, api || {});
      });
    },
  };
})();
