+++
title = "verify"
description = "Check the signature on my bio yourself."
template = "page.html"
+++

The bio on the home page is actually signed, with this site's Ed25519 SSH signing key, on every
deploy. No need to take the green stamp's word for it.

## check the signature

```sh
curl -fsSO https://beasr.dev/bio.txt -O https://beasr.dev/bio.txt.sig -O https://beasr.dev/allowed_signers
ssh-keygen -Y verify -f allowed_signers -I ishaan -n file -s bio.txt.sig < bio.txt
```

You should get `Good "file" signature for ishaan with ED25519 key SHA256:…`. Change one byte of
`bio.txt` and it fails.

## don't trust this site for the key

`allowed_signers` comes from this site, so compare it with the signing key registered on my
GitHub account, [@Beasr1](https://github.com/Beasr1):

```sh
curl -fsS https://api.github.com/users/Beasr1/ssh_signing_keys | grep '"key"'
cut -d' ' -f3- allowed_signers
```

Same key, two places.

## re-derive the block

The `BEGIN MESSAGE` block is just `bio.txt` in base64, and the footer hash is its SHA-256:

```sh
base64 < bio.txt | fold -w 64
shasum -a 256 bio.txt
```
