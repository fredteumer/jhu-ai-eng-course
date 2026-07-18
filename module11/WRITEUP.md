# Module 11 — Identity Management and Zero Trust

**Fred Teumer · JHU WebSec**

> 🚧 Working draft. Sections are appended as evidence is captured. Target length 1.5–2.5 pages excluding screenshots.

---

## 1. Environment Summary

The lab stack runs as four containers on a single user-defined Docker bridge network (`proxy-tier`): Nginx Proxy Manager as the reverse proxy and TLS terminator, Authelia as the identity layer, Ghost as the containerized web application, and MySQL as Ghost's datastore. Only the proxy publishes ports to the host (`80`, `81`, `443`); Ghost and Authelia expose their ports only inside the Docker network, which makes the reverse proxy the single ingress path to the application. Three hostnames are served over TLS using self-signed RSA-2048 certificates — `blog.home.local` (public content), `admin.home.local` (administrative access), and `auth.home.local` (the Authelia portal) — each with Force SSL, HTTP/2, and HSTS enabled at the proxy. Multi-factor authentication is provided by Authelia using TOTP, with credentials stored in a local file backend and passwords hashed with argon2id. Before the identity-aware controls were applied, Ghost's administrative interface at `/ghost` was reachable directly through the public blog hostname, meaning the CMS admin panel was served to any unauthenticated visitor who requested that path.

## 2. Initial Exposure and Trust Assumptions

The protected asset is Ghost's administrative interface — the `/ghost` route, which grants full authoring, configuration, and user-management control over the CMS. In the initial configuration, `blog.home.local` was published as a single proxy host forwarding all paths to the Ghost container, so `https://blog.home.local/ghost` returned the admin interface without any authentication challenge. In this lab the exposure was more severe than a visible login form: because Ghost had not yet been initialized, that URL served the unclaimed first-run setup wizard, meaning the first visitor to reach it could claim ownership of the CMS outright, with no credential to guess or steal (Figure 2). The implicit trust assumption was that reaching the application over the network implied authorization to use any of its routes — the blog and its administrative backend occupied a single trust zone distinguished only by URL path. That assumption is precisely what Zero Trust rejects: network reachability is not identity, and a path that happens to be less advertised is not a control. Because policy was applied per-host rather than per-route, the administrative surface inherited the public posture of the content it shared a hostname with.

## 3. Identity and Access Design

The design places the reverse proxy in front of every request and delegates the access decision to Authelia, so no request reaches Ghost without first traversing a policy decision point. Authelia is configured with `default_policy: 'deny'` and an explicit rule set: `auth.home.local` and `blog.home.local` are `bypass` (public content must remain reachable), while `admin.home.local` requires `two_factor`. Enforcement happens through nginx's `auth_request` directive — the `admin.home.local` vhost issues an internal subrequest to Authelia's verify endpoint for every incoming request, and Authelia answers with the policy outcome. When Authelia returns `401`, an `error_page 401 =302` rule redirects the browser to the Authelia portal, appending the originally requested URL as an `rd=` parameter so the user is returned to their destination after authenticating. Authentication itself is two-staged: a username and password validated against a local file backend with argon2id hashing, followed by a TOTP one-time code from a registered device. Route protection for the exposed admin path is handled separately by `ghostBlock.config` on the public blog vhost, which returns `301` for `/ghost` and `/ghost/` to the equivalent path on `admin.home.local` — the route is not blocked, it is relocated behind the enforcement point. That configuration deliberately preserves `location ^~ /ghost/api/` as a direct proxy pass, because the blog's frontend depends on that content API for search and membership features; policy is therefore applied per-route rather than per-host, which is the distinction the original design lacked. One privilege distinction is worth noting explicitly: Authelia and Ghost maintain entirely separate identity stores with no federation between them, so passing Authelia's two-factor challenge grants *reachability* of the admin route, after which Ghost independently authenticates the user against its own credentials.

## 4. Evidence and Observed Behavior

**Figure 1 — `01-blog-public.png`.** The public blog served over HTTPS at `blog.home.local` with no authentication challenge. This confirms the `bypass` policy is working as intended: adding identity controls did not make public content private.

**Figure 2 — `02-ghost-exposed-BEFORE.png`.** Ghost's unclaimed setup wizard reachable at `https://blog.home.local/ghost/#/setup` before `ghostBlock.config` was applied. This is the exposure in its most severe form — not a login prompt, but an open offer of CMS ownership to any unauthenticated visitor.

**Figure 3 — `routes-BEFORE.log` / `routes-AFTER.log`.** Status codes for the same four routes before and after the restriction. `blog.home.local/ghost/` changes from `200` (admin panel served) to `301` (redirected to the protected host), while `blog.home.local/` remains `200` throughout — the control closed the administrative path without affecting public content.

**Figure 4 — `03-admin-redirect.png`.** Requesting `admin.home.local/ghost/` without a session yields the Authelia sign-in portal rather than Ghost. The `rd=` parameter in the address bar shows the original destination being preserved for post-authentication return.

**Figure 5 — `03-admin-redirect_2.png`.** Authelia reporting that the requested resource requires two-factor authentication and that no device is yet registered. This is the authorization decision surfacing to the user: first-factor success alone does not satisfy the `two_factor` policy on this route.

**Figure 6 — `authelia-OTP.png`.** Authelia's notification record for the one-time code, retrieved via `docker exec authelia cat /config/notification.txt`. Beyond delivering the code, it records the originating IP (`172.22.0.1`), the account it was issued to, and a revocation link — accounting and containment, not merely authentication.

**Figure 7 — `authelia-2FA-success.png`.** Confirmation that the TOTP credential was enrolled. Note the credential reads *"Never used"*, distinguishing enrollment from exercise.

**Figure 8 — `04-mfa-totp_2.png`.** The TOTP challenge presented on the way to `admin.home.local/ghost/`, with the `rd=` destination still intact. This is the second factor being exercised, not merely registered.

**Figure 9 — `05-admin-success.png`.** Ghost's administrative dashboard at `admin.home.local/ghost/#/analytics` after completing both Authelia's two-factor challenge and Ghost's own login. Successful access to the intended route through the full control chain.

**Figure 10 — `redirect-chain-AFTER.log`.** The complete post-restriction chain for a request to the formerly exposed URL: `blog.home.local/ghost` → `301` → `admin.home.local/ghost/` → `302` → `auth.home.local/?rd=…` → `200`. The request is handed from the public host to the protected host to the identity layer, with the original destination carried through both hops.

**Figures 11 and 12 — the same request, two outcomes.** Both figures show a request to `blog.home.local/ghost` after the restriction was applied; the only variable is whether the client presents an established identity.

**Figure 11 — `06-ghost-blocked-AFTER.png` (denied).** Requested from a private browser window with no session. The address bar shows the request has been carried to `auth.home.local/?rd=https%3A%2F%2Fadmin.home.local%2Fghost%2F` — relocated to the protected host, then handed to the identity layer, with the original destination preserved for return.

**Figure 12 — `07-authorized-passthrough.png` (allowed).** The identical URL requested from a session that had already satisfied both Authelia's two-factor challenge and Ghost's login. The address bar shows `admin.home.local/ghost/#/analytics`: the redirect still occurred, but no challenge was raised because the identity requirement was already met.

Read together, these two figures show that the control discriminates on **identity**, not on path. The routing behavior is identical in both cases — the request is relocated to the protected host either way — and only the presence of a verified session determines whether the user is challenged or admitted. A path-based block would have produced the same result for both clients.

## 5. AAA and CI4A Analysis

**Authentication** improved from absent to two-factor on the administrative path: the admin route previously required no credential at all, and now requires a password verified against an argon2id hash plus a TOTP code from an enrolled device. **Authorization** moved from implicit to explicit — Authelia's `default_policy: 'deny'` means a domain not named in the rule set is refused rather than permitted, inverting the original posture where anything reachable was allowed. **Accounting** improved but remains partial: the proxy logs every request with its authorization outcome and Authelia records identity events with source IP and revocation links (Figure 6), yet these logs are per-component, are not aggregated, and Ghost's own application-level actions are not correlated with the Authelia identity that was used to reach them, so an audit cannot fully reconstruct who did what inside the CMS. **Confidentiality** is served by TLS on all three hostnames with Force SSL and HSTS preventing downgrade to cleartext, though the certificates are self-signed, so traffic is encrypted without any third-party assurance of server identity — encryption without trust anchoring. **Integrity** benefits from HSTS and HTTP/2 at the transport layer, but the design weakens integrity of request metadata: the admin vhost rewrites both `Host` and `Origin` to `blog.home.local` before proxying, so Ghost receives deliberately falsified information about how it was reached and cannot make its own trust decisions from those headers. **Accountability and Assurance** are the weakest legs — access is tied to a single named `admin` account with no role separation, there is no device posture assessment, and authorization is evaluated once at request time rather than continuously, so a session that was legitimate when established remains valid regardless of any change in the client's state.

## 6. Residual Risk and Improvement

**Risk 1 — the forward-auth pattern returns a redirect to API requests, so session expiry fails silently.** After the Authelia session lapsed, Ghost's admin interface submitted credentials as an XHR to `/ghost/api/admin/session`; Authelia correctly returned `401`, but `error_page 401 =302` converted that denial into a redirect to an HTML login page. The single-page application cannot follow a login redirect, so it displayed only "There was a problem on the server" and retried once per second indefinitely — behavior confirmed in the proxy access logs, where the `302` on the admin host and the corresponding CORS preflight to the auth host repeat in lockstep. This matters because the control failed *closed*, which is correct, but *misleadingly*, which is not: the only evidence that an identity session had expired existed in proxy logs that neither the user nor the application could see, which is an accounting and diagnosability gap in the security control itself. The improvement is to branch on request type at the proxy — return a bare `401` for `/ghost/api/` paths so the application can prompt for re-authentication, and reserve the `302` redirect for navigation requests; Authelia's newer `/api/authz/*` endpoints are designed around this distinction and would be the cleaner long-term fix.

**Risk 2 — the admin path depends on header rewriting rather than genuine identity-aware routing.** Because `admin.home.local` proxies to a Ghost instance configured to believe it serves `blog.home.local`, the design only functions if the proxy successfully misrepresents the request's origin to the application; the initial configuration spoofed `Host` but not `Origin`, and admin login failed outright until `Origin` was rewritten as well. This matters because the control's correctness rests on the application never independently verifying how it was reached — an assumption that already broke once when Ghost added an origin check, and that will break again with any further validation upstream, producing a security-relevant failure as a side effect of a routine version bump. The improvement is to give the application first-class knowledge of its administrative origin rather than concealing it: Ghost supports a distinct `admin__url` setting for exactly this topology, which would let the proxy forward accurate headers and allow Ghost's own origin validation to function as a defense rather than an obstacle to work around.

*(Noted as a deliberate tradeoff rather than a finding: Ghost's own email-based staff verification was disabled via `security__staffDeviceVerification=false` because the lab has no SMTP transport and the code could never be delivered. This leaves Authelia as the sole MFA control on the admin path, concentrating rather than layering the protection.)*

## 7. Focused Analysis Question

**Q3 — What happens after the `/ghost` restriction is applied, and why does that matter from a Zero Trust perspective?**

After `ghostBlock.config` is applied, a request to `blog.home.local/ghost` no longer receives the admin interface; it receives a `301` to `admin.home.local/ghost/`, which in turn returns a `302` to the Authelia portal, where the user must satisfy both password and TOTP before being returned to the original destination (Figure 10). The significant detail is that the route was not blocked — it was relocated behind the enforcement point, and the `rd=` parameter carries the user's original destination through both hops so that legitimate access still succeeds. Figures 11 and 12 make this concrete: the same URL requested with and without an established session produces identical routing but opposite outcomes, so what changed is not the reachability of the path but the requirement that a verified identity accompany the request. This matters because Zero Trust is not about denying paths but about ensuring no path reaches a protected asset without traversing a policy decision point: the same resource remains available to the same authorized user, but the request now arrives with a verified identity attached rather than on the strength of network reachability alone. The change also demonstrates that policy must be evaluated per-route rather than per-host, since the fix deliberately leaves `/ghost/api/` publicly proxied so the blog's frontend continues to work — the trust boundary is drawn around the administrative function, not around the hostname that happens to serve it.

---

# Lab Notes (working — not part of submission)

Verified facts captured during setup, so the report describes what actually ran.

## Stack as deployed

| Component | Image | Role | Network exposure |
|:--|:--|:--|:--|
| Nginx Proxy Manager | `jc21/nginx-proxy-manager:latest` | Reverse proxy, TLS termination, forward-auth enforcement point | host `:80`, `:81`, `:443` |
| Authelia | `authelia/authelia:latest` (**v4.39.20**) | Identity layer — authn + TOTP 2FA + policy decision point | `9091`, internal only |
| Ghost | `ghost:latest` | Containerized CMS, the protected application | `2368`, internal only |
| MySQL | `mysql:8.0` | Ghost datastore | `3306`, internal only |

All containers share the user-defined bridge network `proxy-tier`. Only NPM publishes ports to the host — Ghost and Authelia are **not** directly reachable from the host, so the proxy is the sole ingress path.

## Authelia policy table (`configuration.yml`)

`default_policy: deny`, with:

| Domain | Policy |
|:--|:--|
| `auth.home.local` | `bypass` |
| `blog.home.local` | `bypass` |
| `admin.home.local` | `two_factor` |

**This asymmetry is the core of the assignment.** Ghost serves its admin panel at `/ghost` on *whatever* vhost reaches it. Because `blog.home.local` is `bypass`, `blog.home.local/ghost` reaches the admin panel without ever consulting the policy table. The identity layer is not bypassed by an attack — it is simply never invoked on that path.

`ghostBlock.config` does **not** authenticate `/ghost`. It returns `301` to `admin.home.local`, which *is* `two_factor`. The fix is not "block the route", it is "force the route through the enforcement point." Worth being precise about this in §3 and §7 — it is the distinction the rubric is looking for.

## Pre-flight verification (before NPM configuration)

Authelia booted standalone against the patched config and probed directly. Policy table confirmed enforcing:

```
$ curl -s -o /dev/null -w '%{http_code}' \
    -H 'X-Original-URL: https://blog.home.local/'  http://127.0.0.1:9099/api/verify
200                                   # bypass policy — request allowed

$ curl -s -o /dev/null -w '%{http_code}' \
    -H 'X-Original-URL: https://admin.home.local/ghost/' http://127.0.0.1:9099/api/verify
401                                   # two_factor policy — unauthenticated request denied
```

The `401` is what `admin_adv.config` catches via `error_page 401 =302` to redirect to the auth portal. Note: `/api/verify` is legacy in 4.39 but **confirmed working** — the scaffold needs no modification.

Post-compose, the same check from inside the proxy network also returns `401`, confirming NPM can reach the identity layer over `proxy-tier`.

## Config changes made to the scaffold

All shipped placeholder secrets were replaced before first run — the scaffold ships with `a_very_long_random_string_must_be_here_32_chars`-style values and `root_password` / `ghost_password` for MySQL:

- `identity_validation.reset_password.jwt_secret` → unique 32-byte random
- `storage.encryption_key` → unique 32-byte random
- `session.secret` → unique 32-byte random
- MySQL root + ghost passwords → unique randoms
- `users_database.yml` password → argon2id hash of the lab password (stock hash replaced)

⚠️ These live in cleartext in the compose file and config — fine for a local lab, and a legitimate §6 residual-risk candidate (secrets-at-rest / no secrets manager).

## Certificates

Self-signed, 10-year, RSA-2048, in `lab/IDZT/certs/` (gitignored — contains private keys):

| File | CN |
|:--|:--|
| `auth.crt` / `auth.key` | `auth.home.local` |
| `blog.crt` / `blog.key` | `blog.home.local` |
| `admin.crt` / `admin.key` | `admin.home.local` |

Browser will warn on these — expected, and worth one honest sentence in the report: TLS still provides confidentiality in transit, but the self-signed trust anchor means no third-party identity assurance for the server. That gap is a defensible §5 Assurance point.

## Credentials (lab only)

| Layer | Identity | Credential |
|:--|:--|:--|
| Authelia (route gate) | `admin` / `admin@home.local` | `jhu` + TOTP |
| Ghost (application) | `admin@example.com` | `supernatural` |
| NPM (proxy admin) | *(set at first login)* | — |

**Three separate identity stores, no federation between them.** Passing Authelia's 2FA does not log you into Ghost — Ghost still presents its own login. The identity layer gates *reachability* of the route; the application authenticates *independently* behind it. Good §3 material, and the lack of SSO/federation is a strong §6 residual risk: revoking the Authelia account does not revoke Ghost access, so an attacker with Ghost credentials who reaches the route another way is still authenticated.

## Observed route behavior — before vs. after

Captured with `curl` at both states. Full logs in `evidence/routes-BEFORE.log`, `routes-AFTER.log`, `redirect-chain-AFTER.log`.

| Route | Before `ghostBlock` | After `ghostBlock` |
|:--|:--|:--|
| `blog.home.local/` | 200 | 200 (unchanged — blog stays public) |
| `blog.home.local/ghost` | — | 301 → `admin.home.local/ghost/` |
| `blog.home.local/ghost/` | **200 — admin panel served** | **301 → `admin.home.local/ghost/`** |
| `blog.home.local/ghost/api/` | — | 404 *from Ghost* (proxied, not redirected — carve-out intact) |
| `admin.home.local/` | 301 → `/ghost/` | 301 → `/ghost/` |
| `admin.home.local/ghost/` | 302 → auth portal | 302 → auth portal |

Full chain after the fix:

```
blog.home.local/ghost
  → 301  https://admin.home.local/ghost/          (ghostBlock -> protected vhost)
  → 302  https://auth.home.local/?rd=https://admin.home.local/ghost/   (forward-auth -> identity layer)
  → 200  Authelia portal
```

**The key observation for §7:** the route is not blocked, it is *relocated behind the enforcement point*. The `rd=` parameter survives both hops, so after successful 2FA the user is returned to the originally requested resource. A deny would have been simpler; this is better, because it preserves function while making identity non-optional. Zero Trust here is not "deny the path" but "no path reaches the asset without traversing a policy decision point."

Also note the `/ghost/api/` carve-out: the fix distinguishes the **admin UI** (must be gated) from the **public content API** (must stay reachable for blog search/members). Blanket-blocking `/ghost*` would have broken the blog. Policy is per-route, not per-host.

## Scaffold defects encountered (both required fixes)

Two failures hit during setup that the provided scaffold does not account for. Both are worth reporting — they were found by running the thing, not by reading about it.

### 1. Ghost rejects admin login: "Request made from incorrect origin"

**Symptom:** After passing Authelia 2FA, Ghost's own login returned `Request made from incorrect origin. Expected 'https://blog.home.local' received 'https://admin.home.local'.`

**Cause:** The scaffold's `admin_adv.config` routes admin traffic over a *different hostname* than Ghost believes it serves, and maintains that illusion by rewriting `Host` to `blog.home.local` (the block literally commented `# --- Ghost Identity Spoofing ---`). Current Ghost also validates the browser's `Origin` header against its configured `url`. `Origin` passed through untouched, so the check failed.

**Fix applied:** added `proxy_set_header Origin https://blog.home.local;` alongside the existing `Host` spoof.

**Why this matters for the report (§3/§6):** the architecture is fragile *by construction*. It depends on the proxy successfully lying to the application about its own identity, and it broke the moment Ghost added one additional origin check. It will break again on the next one. The proper design gives the application first-class knowledge of its admin origin — Ghost natively supports `admin__url` for exactly this — rather than requiring header rewriting to paper over a hostname mismatch. **Header spoofing is not identity-aware routing; it is a workaround that happens to produce the same result until it doesn't.** Strong residual-risk candidate with a concrete, realistic improvement.

### 2. Ghost admin login dead-ends: "Failed to send email"

**Symptom:** With the origin issue resolved, login failed at `Failed to send email. Please check your site configuration and try again.`

**Cause:** Modern Ghost enforces its own email-based staff device verification. The stack has no SMTP configured, so the code can never be delivered and login cannot complete.

**Fix applied:** `security__staffDeviceVerification=false` in the Ghost service environment, container recreated.

⚠️ **Report this honestly — it is a lab concession, not a hardening step.** Disabling it removes the *application's* second factor, leaving Authelia as the sole MFA control on the admin path. That is defensible here (Authelia's MFA is the subject of the assignment, and standing up mail infrastructure to satisfy a redundant second factor is out of scope) but it does concentrate risk: with app-layer MFA off, anyone who reaches Ghost's login having bypassed the proxy — see the direct-container-access risk — faces only a single password. Good §6 material precisely *because* it is a tradeoff rather than a clean win.

### 3. Forward-auth returns a redirect to API calls — SPA breaks on session expiry ⭐

**Symptom:** After a period of inactivity, Ghost admin login failed with the opaque message *"There was a problem on the server."* and the browser retried once per second indefinitely. No errors appeared in Ghost's log, because the request never reached Ghost.

**Diagnosis, from NPM access logs at matching timestamps:**

```
proxy-host-2 (admin):  POST /ghost/api/admin/session          -> 302   (repeating, 1/sec)
proxy-host-3 (auth):   OPTIONS /?rd=...admin/session          -> 200   (repeating, 1/sec)
```

Sequence:

1. Ghost's Ember admin submits credentials as an **XHR** to `/ghost/api/admin/session`
2. `auth_request` consults Authelia → `401`, session lapsed (`inactivity: '5m'`)
3. `error_page 401 =302` rewrites the failure into **a redirect to the login portal**
4. The browser attempts to follow it cross-origin → CORS preflight `OPTIONS` to `auth.home.local`
5. Ember receives an HTML login page where it expected JSON → generic failure, infinite retry

**This is the most interesting finding in the lab and should anchor §6.** The forward-auth pattern converts an authentication failure into a *redirect*. That is correct for browser **navigation** — the user sees a login page — but wrong for **API** requests. A single-page application cannot follow a login redirect; it needs a `401` with a JSON body so it can prompt for re-authentication. As built, session expiry produces an unintelligible error and a retry storm rather than a re-auth prompt.

**Why it matters:** it is an availability and diagnosability failure in the security control itself. An operator seeing only "problem on the server" has no indication that the cause is an expired identity session — the accounting trail lives in the proxy logs, not anywhere the user or the application can see. That is a genuine gap in the **Accounting/Assurance** leg of CI4A: the control failed *closed* (good) but *silently and misleadingly* (bad).

**Recommended improvement:** branch on request type at the proxy — return a bare `401` for `/ghost/api/` paths and reserve the `302` redirect for navigation requests. Nginx can distinguish these via `$http_accept` or `$http_x_requested_with`. Authelia's newer `/api/authz/*` endpoints are designed with this distinction in mind and would be the cleaner long-term fix.

**Mitigation applied for capture purposes:** `session.inactivity` raised `5m` → `30m`. ⚠️ Note honestly in the report that this reduces the frequency of the symptom but does **not** fix the defect — the redirect-on-XHR behavior is unchanged, it simply triggers less often. The short timeout was never the bug.

## Host footprint (for teardown)

Single change outside Docker and this repo — `/etc/hosts`:

```
127.0.0.1  auth.home.local  blog.home.local  admin.home.local
```

Teardown: delete that line · `docker compose down -v` · `sudo rm -rf lab/IDZT/{ghost,mysql,nginx-proxy-manager,certs}`

## Known-benign noise

Ghost logs `getaddrinfo ENOTFOUND blog.home.local` from its ActivityPub module — it resolves its own public hostname from inside the container, where the host's `/etc/hosts` does not apply. Unrelated to the identity controls. Do not chase.
