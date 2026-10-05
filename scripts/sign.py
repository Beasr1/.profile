#!/usr/bin/env python3
"""Encode and verify the home page's signed bio.

The bio is the text of the <p> tags inside <div class="out"> in templates/index.html,
joined with spaces and stripped of HTML. That exact byte string is the signed message.

  sign.py --encode   regenerate everything derived from the bio:
                       - static/bio.txt (the signed bytes, served at /bio.txt)
                       - the base64 BEGIN MESSAGE block (64-char lines) and its CRC-24 (=xxxx)
                       - the same block in the terminal's re-encode screen
                       - the "decoding / encoding N bytes" log lines and the short SHA-256s
                       - the invisible copy of the bio that sizes the terminal on small screens
  sign.py --check    verify static/bio.txt.sig (an SSH signature, `ssh-keygen -Y sign -n file`)
                     against static/allowed_signers, make sure bio.txt matches the page, and
                     stamp the verified key fingerprint and the signature itself into the page. Exits 1 on any mismatch,
                     so CI refuses to deploy a bio that isn't signed.

`make encode` runs --encode locally. CI runs --encode, signs bio.txt with the site key
(the SITE_SIGNING_KEY repo secret), then --check, before every deploy.
"""

import base64
import hashlib
import html
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = ROOT / "templates" / "index.html"
BIO = ROOT / "static" / "bio.txt"
SIG = ROOT / "static" / "bio.txt.sig"
SIGNERS = ROOT / "static" / "allowed_signers"
PRINCIPAL = "ishaan"
NAMESPACE = "file"


def crc24(data):
    # OpenPGP armor checksum (RFC 4880, section 6.1)
    crc = 0xB704CE
    for byte in data:
        crc ^= byte << 16
        for _ in range(8):
            crc <<= 1
            if crc & 0x1000000:
                crc ^= 0x1864CFB
    return crc & 0xFFFFFF


def plaintext(page):
    out = re.search(r'<div class="out">(.*?)</div>', page, re.S).group(1)
    paragraphs = re.findall(r"<p>(.*?)</p>", out, re.S)
    text = " ".join(re.sub(r"<[^>]+>", "", p).strip() for p in paragraphs)
    return html.unescape(text).encode()


def encode():
    page = HOME.read_text()
    msg = plaintext(page)

    body = textwrap.wrap(base64.b64encode(msg).decode(), 64)
    checksum = "=" + base64.b64encode(crc24(msg).to_bytes(3, "big")).decode()
    armor = "-----BEGIN MESSAGE-----<br>" + "<br>".join(body + [checksum]) + "<br>-----END MESSAGE-----"
    page, n = re.subn(
        r'(<p class="armor" aria-hidden="true">)-----BEGIN MESSAGE-----<br>.*?<br>-----END MESSAGE-----',
        lambda m: m.group(1) + armor, page, flags=re.S)
    assert n == 1, "signature block not found"

    # the same block, printed by the terminal's re-encode screen
    page, n = re.subn(r'<p class="enc">.*?</p>', '<p class="enc">' + armor + "</p>", page, flags=re.S)
    assert n == 1, "re-encode block not found"

    page = re.sub(r"checksum =\S+ ", f"checksum {checksum} ", page)
    page = re.sub(r"(de|en)coding \d+ bytes", lambda m: f"{m.group(1)}coding {len(msg)} bytes", page)

    digest = hashlib.sha256(msg).hexdigest()
    page = re.sub(r"\b[0-9a-f]{8}…[0-9a-f]{8}\b", f"{digest[:8]}…{digest[-8:]}", page)

    # invisible copy of the bio that sizes the terminal while decoded (links flattened to text)
    out = re.search(r'<div class="out">(.*?)</div>', page, re.S).group(1)
    copy = re.sub(r"<a [^>]*>(.*?)</a>", r"\1", out)
    page, n = re.subn(r'(<div class="out sz">).*?(</div>)', lambda m: m.group(1) + copy + m.group(2), page, flags=re.S)
    assert n == 1, "sizer block not found"

    HOME.write_text(page)
    BIO.write_bytes(msg)
    print(f"encoded {len(msg)} bytes, sha256 {digest}, checksum {checksum} -> {BIO.relative_to(ROOT)}")


def check():
    page = HOME.read_text()
    msg = plaintext(page)

    if not BIO.exists() or BIO.read_bytes() != msg:
        sys.exit("bio.txt doesn't match the bio on the page: run `make sign`")
    if not SIG.exists():
        sys.exit("bio.txt isn't signed yet: run `make sign`")

    result = subprocess.run(
        ["ssh-keygen", "-Y", "verify", "-f", str(SIGNERS), "-I", PRINCIPAL, "-n", NAMESPACE, "-s", str(SIG)],
        input=msg, capture_output=True)
    output = (result.stdout + result.stderr).decode().strip()
    if result.returncode != 0:
        sys.exit(f"signature does NOT verify: {output}\nrun `make sign`")

    # e.g. Good "file" signature for ishaan with ED25519 key SHA256:xZG+...
    m = re.search(r"with (\S+) key (SHA256:\S+)", output)
    algo, fingerprint = m.group(1), m.group(2)
    stamped = re.sub(r'<span class="fp">[^<]*</span>', f'<span class="fp">{algo} key {fingerprint}</span>', page)
    # print the real signature in the terminal (armor lines joined with <br>)
    sig = "<br>".join(html.escape(line) for line in SIG.read_text().strip().splitlines())
    stamped, n = re.subn(r'<p class="sshsig">.*?</p>', lambda _: f'<p class="sshsig">{sig}</p>', stamped, flags=re.S)
    assert n == 1, "signature block (sshsig) not found"
    if stamped != page:
        HOME.write_text(stamped)
    print(output)


if __name__ == "__main__":
    if sys.argv[1:] == ["--encode"]:
        encode()
    elif sys.argv[1:] == ["--check"]:
        check()
    else:
        sys.exit(__doc__)
