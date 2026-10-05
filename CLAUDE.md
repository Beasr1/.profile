# CLAUDE.md

Personal website built with [Zola](https://www.getzola.org), deployed to GitHub Pages.
Minimal, text-first, themed as a PGP-signed certificate.

## Layout

- `templates/index.html`: home page, hand-written HTML (certificate, base64 signature, decode terminal).
- `templates/base.html`: shared layout. `blog.html` / `post.html`: post list and single post.
- `content/blog/*.md`: posts.
- `static/style.css`: the whole theme. `static/keys.js`: keyboard shortcuts.
- `scripts/sign.py`: re-signs the home page.

## Commands

- `make serve` (live preview), `make drafts`, `make build`, `make sign`.

## Rules

- Keep it simple: plain HTML/CSS, a little JS. The site must work without JavaScript.
- No RSS or feeds, on purpose.
- The "Certificate details" block in `templates/index.html` is locked: don't change it unless asked.
- After editing the decoded intro (`.out` in `index.html`), run `make sign`.
- Avoid `{{`, `{%` and `{#` in hand-written HTML inside templates (Tera syntax).
- Never run `git commit` and never add attribution trailers. Commit style: `type(scope):message`.
