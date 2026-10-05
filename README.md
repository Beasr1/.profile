# .profile

Personal website of Ishaan Dubey ([@Beasr1](https://github.com/Beasr1)). Themed as a PGP-signed
certificate. Built with [Zola](https://www.getzola.org) (a single-binary static site generator
written in Rust) and served as plain static files.

## Layout

```
config.toml              site settings (base_url, title)
content/
  _index.md              home section (content lives in templates/index.html)
  blog/_index.md         blog section settings
  blog/*.md              posts (Markdown + TOML front matter)
templates/
  base.html              shared layout: head, header + nav, footer
  index.html             the home page (hand-written HTML: certificate, signature, terminal)
  blog.html              post list
  post.html              single post
static/
  style.css              the whole theme
  keys.js                keyboard shortcuts (h, b, g, d, j, k, ?); optional, site works without it
scripts/sign.py          re-signs the home page (see below)
.github/workflows/       builds and deploys to GitHub Pages on push to main
```

## Run it

```sh
make serve       # http://127.0.0.1:1111, live reload
make drafts      # same, including draft posts
make build       # static site in public/
```

Install Zola with `brew install zola` or `cargo install --locked zola`. If it isn't on your PATH,
the Makefile downloads the pinned release into `.bin/` (gitignored) automatically.

## Write a post

Add `content/blog/my-post.md`:

```toml
+++
title = "my post"
date = 2026-10-05
description = "one line for search results and link previews"
+++

Markdown here.
```

It shows up at `/blog/my-post/` and in the blog list. There's no RSS feed on purpose: posts live
on the site only. Add `draft = true` to keep it unpublished.

## Deploy (GitHub Pages)

1. Push this repo to `github.com/Beasr1/.profile` on branch `main`.
2. Repo **Settings → Pages → Source: GitHub Actions**.
3. Every push to `main` builds and publishes to `https://beasr1.github.io/.profile/` (until a custom domain is set).

For your own domain later: set `base_url` in `config.toml`, add the domain under Settings → Pages,
and point DNS at GitHub. Or copy `public/` to any server (nginx, etc.).

## The signature is real (ish)

The `BEGIN SIGNATURE` block on the home page is the decoded intro (the `.out` paragraphs in
`templates/index.html`), base64-encoded and wrapped at 64 chars. The `=xxxx` line is its OpenPGP
CRC-24 checksum, and the `sha256 …` in the footer strip is the SHA-256 of the same text. The
decode terminal shows all of them. After editing the intro, run:

```sh
make sign
```
