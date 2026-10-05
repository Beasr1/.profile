// Keyboard shortcuts. Progressive enhancement: the site works the same without this file.
// Links opt in with data-key="x" (and optional data-label); see templates/base.html.
(() => {
  "use strict";

  const shortcuts = [];

  for (const link of document.querySelectorAll("a[data-key]")) {
    const key = link.dataset.key;
    shortcuts.push({
      key,
      label: link.dataset.label || link.textContent.trim(),
      run: () => link.click(),
    });
    // show a [x] badge on nav links
    if (link.closest("nav")) link.insertAdjacentHTML("afterbegin", `<kbd>${key}</kbd>`);
  }

  const home = document.querySelector("a[data-key='h']")?.href || "/";

  shortcuts.push(
    { key: "d", label: "decode / re-encode signature", run: toggleDecode },
    { key: "j", label: "scroll down", run: () => scrollBy({ top: 120, behavior: "smooth" }) },
    { key: "k", label: "scroll up", run: () => scrollBy({ top: -120, behavior: "smooth" }) },
    { key: "?", label: "show / hide this help", run: toggleHelp },
  );

  function toggleDecode() {
    const details = document.querySelector(".decode");
    if (!details) {
      location.href = home + "#decode";
      return;
    }
    details.open = !details.open;
    details.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  let help;
  function toggleHelp() {
    if (!help) {
      help = document.createElement("dialog");
      help.className = "keys-help";
      help.innerHTML =
        "<p class=\"keys-title\">$ man ishaan</p><dl>" +
        shortcuts.map((s) => `<dt><kbd>${s.key}</kbd></dt><dd>${s.label}</dd>`).join("") +
        "<dt><kbd>esc</kbd></dt><dd>close</dd></dl>";
      help.addEventListener("click", (e) => { if (e.target === help) help.close(); });
      document.body.append(help);
    }
    help.open ? help.close() : help.showModal();
  }

  // a "?" hint at the end of the nav, only when JS is on
  document.querySelector("nav")?.insertAdjacentHTML("beforeend", "<span class=\"keys-hint\"><kbd>?</kbd></span>");

  // landing on /#decode (e.g. pressing d on another page) opens the signature
  if (location.hash === "#decode") {
    const details = document.querySelector(".decode");
    if (details) details.open = true;
  }

  addEventListener("keydown", (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const tag = e.target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || e.target.isContentEditable) return;
    const hit = shortcuts.find((s) => s.key === e.key || s.key === e.key.toLowerCase());
    if (hit) {
      e.preventDefault();
      hit.run();
    }
  });
})();
