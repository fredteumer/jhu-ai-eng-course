# Module 8 — TLS / PKI / Certificates lab
#
# ubuntu:24.04 is not an arbitrary choice: `apt-get install openssl` on this
# release yields OpenSSL 3.0.13 30 Jan 2024 — the exact build shown in the
# assignment PDF's screenshots. Pinning the base image pins the OpenSSL version,
# so every command and every banner matches the guide verbatim.
FROM ubuntu:24.04

RUN apt-get update \
 && apt-get install -y --no-install-recommends openssl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /lab
