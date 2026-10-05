#!/usr/bin/env python3
"""Re-sign templates/index.html after editing the intro.

The plaintext is the text of the <p> tags inside <div class="out"> (the decoded intro),
joined with spaces and stripped of HTML. From it this regenerates:
  - the base64 body of the BEGIN SIGNATURE block (64-char lines) and its CRC-24 (=xxxx)
  - the "decoding N bytes" log line
  - every "fef2939e…12db600e"-style short SHA-256 (footer strip + terminal line)
"""

import base64
import hashlib
import html
import re
import textwrap
from pathlib import Path

HOME = Path(__file__).resolve().parent.parent / "templates" / "index.html"


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


def main():
    page = HOME.read_text()
    msg = plaintext(page)

    body = textwrap.wrap(base64.b64encode(msg).decode(), 64)
    checksum = "=" + base64.b64encode(crc24(msg).to_bytes(3, "big")).decode()
    armor = "-----BEGIN SIGNATURE-----<br>" + "<br>".join(body + [checksum]) + "<br>-----END SIGNATURE-----"
    page, n = re.subn(r"-----BEGIN SIGNATURE-----<br>.*?<br>-----END SIGNATURE-----", armor, page, flags=re.S)
    assert n == 1, "signature block not found"

    page = re.sub(r"checksum =\S+ ", f"checksum {checksum} ", page)
    page = re.sub(r"decoding \d+ bytes", f"decoding {len(msg)} bytes", page)

    digest = hashlib.sha256(msg).hexdigest()
    page = re.sub(r"\b[0-9a-f]{8}…[0-9a-f]{8}\b", f"{digest[:8]}…{digest[-8:]}", page)

    HOME.write_text(page)
    print(f"signed {len(msg)} bytes, sha256 {digest}, checksum {checksum}")


if __name__ == "__main__":
    main()
