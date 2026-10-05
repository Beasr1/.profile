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
    const box = document.getElementById("decode");
    if (!box) {
      location.href = home + "#decode";
      return;
    }
    box.checked = !box.checked;
    followTerminal();
    box.closest(".signature").scrollIntoView({ behavior: "smooth", block: "center" });
  }

  // The terminal keeps the newest line at the bottom (CSS), but if someone scrolled up to read,
  // jump back down when the session continues, so the decode / re-encode is always in view.
  // (The screen is a reversed column, so scrollTop 0 is the bottom.)
  // A fixed 250ms ease-out glide (not the browser's "smooth", whose duration grows with the
  // distance), so it always lands before the re-encode starts typing at 0.3s.
  function followTerminal() {
    const screen = document.querySelector(".screen");
    if (!screen || screen.scrollTop === 0) return;
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      screen.scrollTop = 0;
      return;
    }
    const from = screen.scrollTop;
    const start = performance.now();
    const step = (now) => {
      const t = Math.min((now - start) / 250, 1);
      screen.scrollTop = from * Math.pow(1 - t, 3);
      if (t < 1) requestAnimationFrame(step);
      else screen.scrollTop = 0;
    };
    requestAnimationFrame(step);
  }
  document.getElementById("decode")?.addEventListener("change", followTerminal);

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
    const box = document.getElementById("decode");
    if (box) box.checked = true;
  }

  // enable the terminal's close animation only once the page has settled (see style.css)
  const ready = () => requestAnimationFrame(() => document.documentElement.classList.add("ready"));
  if (document.readyState === "complete") ready();
  else addEventListener("load", ready);

  addEventListener("keydown", (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const t = e.target;
    const typing = (t.tagName === "INPUT" && t.type !== "checkbox") || t.tagName === "TEXTAREA" || t.isContentEditable;
    if (typing) return;
    const hit = shortcuts.find((s) => s.key === e.key || s.key === e.key.toLowerCase());
    if (hit) {
      e.preventDefault();
      hit.run();
    }
  });
})();
