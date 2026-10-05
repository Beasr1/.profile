# Makefile
ZOLA_VERSION=0.23.6
PORT?=1111

# Use zola from PATH if installed, otherwise a pinned copy downloaded into .bin/
ZOLA:=$(shell command -v zola 2>/dev/null || echo .bin/zola)

UNAME_S:=$(shell uname -s)
UNAME_M:=$(shell uname -m)
ifeq ($(UNAME_S),Darwin)
  ZOLA_TARGET=$(if $(filter arm64,$(UNAME_M)),aarch64,x86_64)-apple-darwin
else
  ZOLA_TARGET=$(UNAME_M)-unknown-linux-gnu
endif
ZOLA_URL=https://github.com/getzola/zola/releases/download/v$(ZOLA_VERSION)/zola-v$(ZOLA_VERSION)-$(ZOLA_TARGET).tar.gz

.PHONY: serve drafts build encode clean help

# Live-reloading preview at http://127.0.0.1:$(PORT)
serve: $(ZOLA)
	$(ZOLA) serve --port $(PORT)

# Same, including draft posts
drafts: $(ZOLA)
	$(ZOLA) serve --port $(PORT) --drafts

# Build the static site into public/
build: $(ZOLA)
	$(ZOLA) build

# After editing the bio: regenerate the base64 block, hashes and static/bio.txt for local preview.
# Signing happens in CI with the site key (see .github/workflows/deploy.yml).
encode:
	python3 scripts/sign.py --encode

clean:
	rm -rf public/

.bin/zola:
	@echo "zola not found, downloading v$(ZOLA_VERSION) into .bin/"
	@mkdir -p .bin
	curl -sSL $(ZOLA_URL) | tar -xz -C .bin

.DEFAULT_GOAL := serve

help:
	@echo "Targets:"
	@echo "  serve   - preview at http://127.0.0.1:$(PORT) with live reload (PORT=xxxx to change)"
	@echo "  drafts  - same, including draft posts"
	@echo "  build   - build the site into public/"
	@echo "  encode  - after editing the bio: regenerate the base64 block, hashes and bio.txt"
	@echo "  clean   - remove public/"
