# Module 8 — TLS / PKI / Certificates Lab 🎓🔒

A pinned OpenSSL sandbox in Docker for the JHU WebSec TLS/PKI assignment, replacing the VirtualBox image. Everything runs in a container; **nothing is installed on your host.**

## Use

```bash
./setup.sh                      # build + start, verifies the OpenSSL version
docker compose exec pki bash    # <- your sandbox shell; run assignment commands here
./teardown.sh                   # remove container + built image (KEEPS your keys)
```

## Why this is safe to substitute for the VM

Every step of this assignment is the OpenSSL CLI. Nothing calls a kernel feature, a GUI, or anything else VirtualBox provides — the VM exists only to guarantee everyone has a known-good OpenSSL. A pinned base image does that more precisely.

`ubuntu:24.04` + `apt-get install openssl` resolves to **OpenSSL 3.0.13 30 Jan 2024**, which is byte-for-byte the build in the PDF's Figure 1. Verified working in-container: symmetric encrypt/decrypt, `genrsa 1024`, `rsa -des3`, `rsa -pubout`, `pkeyutl` encrypt/decrypt, the 116-byte overflow demo, and the Part 3.5 CSR + self-signed certificate.

**The bind mount is a genuine upgrade over the VM.** The PDF says twice to keep the generated files — "especially the `cert.pem` file" — because module 9 reuses them. They land in `./artifacts/` on the host and `teardown.sh` leaves them alone, so there's no VM disk to preserve or accidentally clobber.

## Known gap: `hostnamectl`

Part 1 asks for `hostnamectl`, which needs systemd/dbus and does not work in a container. **It is not on the grading rubric** (see the table below — Part 1 scores zero points), so this is cosmetic. Options:

```bash
docker compose exec pki uname -a           # kernel + arch
docker compose exec pki cat /etc/os-release  # distro identity
hostnamectl                                # or just run it on your Arch host
```

## Mapping to the grading rubric

| Rubric item | Value | Where |
| --- | :---: | --- |
| Symmetric Encryption Part 2 — `openssl enc` encrypt + decrypt | 20 | container |
| Asymmetric Encryption Part 3 — keys, `pkeyutl`, CSR, self-signed cert | 20 | container |
| Interact with fellow students via PKI, post plain text results | 50 | **MS Teams** |
| Professional presentation, spelling/grammar at master's level | 10 | the Google Doc |
| **Total** | **100** | |

Note that Part 1 (`hostnamectl` / `openssl version` / `openssl ciphers`) carries no points despite being listed as a deliverable, and that **half the grade lives in Teams**, not in the write-up.

## Screenshots to capture

Annotate each snip with a one-line description of what it demonstrates — the PDF asks for this explicitly, and it feeds the 10-point presentation score. Quality of annotation over quantity of snips.

**Part 2 (20 pts)** — `openssl enc -aes-256-cbc -pbkdf2` in both directions, showing the round-trip recovers the plaintext.

**Part 3 (20 pts)** — `genrsa`, `cat key.pem`, `rsa -text -noout`, `rsa -des3`, `rsa -pubout`, `pkeyutl -encrypt`, `pkeyutl -decrypt`, plus the >116-byte failure, and the Part 3.5 `req` / `x509 -req` / `x509 -text` sequence.

**Part 4 (50 pts)** — graded in Teams, but screenshot your side of it for the doc.

## ⚠️ Before starting Part 4

The PDF names **three different Teams channels** for the same workflow: "Module 02 Assignment" (4.A), "Module 01 Assignment" (4.B.2.iii), and "Module 2 Assignment" (4.B.3.ii). It's a recycled document. Confirm the live channel with the instructor before posting — this is 50 of the 100 points.

## Notes

- `artifacts/` is gitignored. Private keys don't belong in a repo even when they're throwaway 1024-bit classroom keys, and the bind mount persists them for module 9 regardless of whether git tracks them.
- The container runs as your uid/gid (exported by `setup.sh`), so `key.pem` lands on the host owned by you rather than root — bind mounts don't remap ownership. The uid-1000 default also lands on ubuntu:24.04's stock `ubuntu` user, so the prompt reads `ubuntu@pki_lab` rather than `I have no name!`. If your uid isn't 1000 the lab still works, it just prints the uglier prompt.
- 1024-bit RSA and 3DES are both obsolete for real use. The assignment specifies them deliberately — 1024-bit keeps the 116-byte padding limit small enough to demonstrate, and both still work in OpenSSL 3.0.13's default provider.
