# RFC-001: Enterprise SSO + Audit Log API for Apohara PROBANT

**Status:** Draft (Phase 2 Tier 4)
**Author:** Pablo M. Suarez (with AI co-author note — scaffolded with Claude Sonnet 4.6 assistance)
**Date:** 2026-05-18
**Backlog Item:** US-T4-P

---

## Abstract

This RFC specifies two enterprise-grade capabilities for Apohara PROBANT: identity federation via SAML 2.0 and OpenID Connect (OIDC), and a tamper-evident audit log API designed for SIEM integration. The SSO layer enables enterprise customers to use their existing identity providers (Okta, Azure AD, Auth0, Ping Identity) without exposing credential material to Apohara. The audit log API exposes the existing HMAC-signed SHA-256 ledger through a paginated REST interface with NDJSON export, enabling direct ingestion into Splunk, Datadog, Sumo Logic, and Elastic. Both capabilities are gated behind `APOHARA_ENTERPRISE_MODE=1` and preserve backwards compatibility with the existing BYOK verification flow. This document covers protocol selection rationale, flow design, security considerations, and backwards compatibility guarantees.

---

## 1. Motivation

### 1.1 The BYOK Bottleneck

Apohara PROBANT's current authentication model requires each user to supply a Google Gemini API key at request time (BYOK — Bring Your Own Key). This model is appropriate for individual developers and small teams but creates three blockers for enterprise adoption:

1. **No identity federation.** Enterprise IT departments operate centralized identity providers (IdPs) with enforced MFA, conditional access policies, and automated lifecycle management. They cannot bind access to Apohara PROBANT to their existing IAM governance without SSO support.

2. **No organizational access controls.** The current model has no concept of an `org_id` or tenant boundary. Every user is effectively a peer — there is no admin/viewer role separation, no cross-team audit visibility, and no way to enforce organization-wide policies.

3. **No machine identity.** Enterprises running Apohara as part of a CI/CD pipeline need service accounts with scoped JWT credentials, not human BYOK keys that expire or rotate on individual developer schedules.

### 1.2 Compliance Requirements

Three major compliance frameworks require identity federation for any SaaS tool used by covered organizations:

- **SOC 2 CC6.1 (Logical Access Controls):** Requires that access be limited to authorized users and that access is granted based on a formal provisioning process tied to the organization's identity system. BYOK-only satisfies neither.
- **ISO 27001 A.5.16 (Identity Management) + A.5.17 (Authentication Information):** Requires organizations to manage identity lifecycle including provisioning, modification, and deprovisioning. An external tool that bypasses the organization's IdP cannot be audited for A.5.16 compliance.
- **GDPR Article 32 / CCPA Section 1798.150:** Require "appropriate technical measures" for personal data security, which regulators interpret to include MFA enforcement and centralized access logging. SSO delegation to an MFA-enforcing IdP satisfies both.

### 1.3 SIEM Integration Gap

Apohara PROBANT already maintains a tamper-evident audit ledger: every verdict is HMAC-SHA-256 signed and SHA-256 chain-linked, stored at `~/.apohara-inti/ledger.jsonl`. This ledger is the project's primary forensic artifact and a key differentiator from competitors who lack audit trails entirely.

However, the ledger is currently only queryable via internal helpers or the single-entry `GET /v1/audit/{verdict_id}` endpoint. Enterprise security teams expect:

- **Bulk time-range queries** with ISO 8601 time bounds.
- **Verdict-filtered exports** (e.g., "give me all `blocked` verdicts in the last 30 days").
- **NDJSON streaming** for direct ingestion into Splunk HEC, Datadog Log Management, Sumo Logic, and Elastic Filebeat.
- **Tamper-evidence preserved at API layer** — every returned entry should be verifiable against the original ledger signature.

### 1.4 GDPR / CCPA Retention Requirements

GDPR Article 5(1)(e) requires personal data to be kept "no longer than is necessary." CCPA §1798.100 grants consumers the right to request deletion. Both frameworks require that audit systems support:

- **Time-bounded export** (export data from a specific period for a specific subject).
- **Deletion / scrubbing capability** (not in scope for this RFC but the API surface defined here is the prerequisite).

The audit log API defined in this RFC provides the export capability. Retention enforcement and subject-level deletion are deferred to Phase 3.

---

## 2. Design — SSO

### 2.1 Protocol Selection

Two protocols are specified:

| Protocol | Use Case | Priority |
|---|---|---|
| OIDC (OAuth 2.0 + OpenID Connect Core 1.0) | Modern IdPs: Auth0, Okta, Azure AD (OIDC mode), Cognito, Keycloak | **P0 — this RFC** |
| SAML 2.0 | Legacy enterprise IdPs: on-premise ADFS, legacy Okta configurations, many healthcare and government deployments | P1 — follow-up sprint |

OIDC is implemented first because: (a) all major cloud IdPs support OIDC natively, (b) the library ecosystem (authlib, python-jose) is more ergonomic than XML-based SAML libraries, and (c) OIDC integrates naturally with the existing JWT-based session model.

SAML 2.0 is specified in this RFC and scaffolded in the protocol design sections but the implementation is deferred. The integration point (JIT provisioning, `org_id` mapping, JWT issuance) is identical for both protocols.

SCIM 2.0 (RFC 7644) for automated user lifecycle management (provisioning + deprovisioning) is described in §2.4 but the scaffold is explicitly out of scope for this sprint.

### 2.2 SAML 2.0 SP-Initiated Flow

```
User Browser          Apohara PROBANT (SP)         Enterprise IdP
      |                       |                           |
      |-- GET /v1/sso/login -->|                           |
      |                       |-- build SAMLRequest ------>|
      |<-- HTTP 302 redirect --|   (Base64-encoded XML)     |
      |                                                     |
      |-- POST to IdP SSO URL (with SAMLRequest param) ---->|
      |                                                     |-- validate SP ---|
      |                                                     |-- prompt user    |
      |                                                     |-- MFA (if req'd) |
      |<-- HTTP 302 to /v1/sso/callback?SAMLResponse=... ---|
      |                       |                           |
      |-- POST /v1/sso/callback with SAMLResponse -------->|
      |                       |-- validate XML sig --------|
      |                       |-- extract NameID, attrs ---|
      |                       |-- JIT provision (if new) --|
      |                       |-- issue Apohara JWT --------|
      |<-- HTTP 302 to dashboard (JWT in cookie) ----------|
```

Key SAML parameters:
- **`NameIDFormat`:** `urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress` (preferred) or `persistent`.
- **Attributes requested:** `email`, `given_name`, `family_name`, `groups` (for role mapping).
- **SP EntityID:** `https://api.apohara.dev/saml/metadata`.
- **AssertionConsumerService URL:** `https://api.apohara.dev/v1/sso/callback`.
- **Signature algorithm:** `rsa-sha256` (RSA-SHA1 rejected per NIST SP 800-131A).

### 2.3 OIDC Authorization Code + PKCE Flow

```
User Browser          Apohara PROBANT               Enterprise IdP
      |                       |                           |
      |-- GET /v1/sso/login -->|                           |
      |                       |-- generate code_verifier  |
      |                       |-- generate state cookie   |
      |<-- HTTP 302 to IdP authorization endpoint ---------|
      |                       |                            |
      |-- GET /authorize?response_type=code                |
      |     &client_id=...&redirect_uri=...                |
      |     &scope=openid+profile+email                    |
      |     &state=...&code_challenge=...  --------------->|
      |                                                     |-- authenticate  |
      |                                                     |-- MFA           |
      |<-- HTTP 302 to /v1/sso/callback?code=...&state=... |
      |                       |                            |
      |-- GET /v1/sso/callback?code=...&state=... -------->|
      |                       |-- validate state cookie    |
      |                       |-- POST /token              |
      |                       |   code + code_verifier --> |
      |                       |<-- {access_token,          |
      |                       |     id_token,              |
      |                       |     refresh_token}         |
      |                       |-- validate id_token sig    |
      |                       |-- extract sub, email, orgs |
      |                       |-- JIT provision if new     |
      |                       |-- issue Apohara JWT        |
      |<-- HTTP 302 + Set-Cookie: apohara_jwt=... ---------|
```

PKCE (`code_challenge_method=S256`) is mandatory. This prevents authorization code interception attacks and is required by RFC 9700 for public clients and strongly recommended for confidential clients.

Scopes requested: `openid profile email`. The `acr_values=phr` parameter is included to request phishing-resistant MFA (WebAuthn/FIDO2) from IdPs that support it (Okta, Auth0 with advanced MFA, Azure AD with FIDO2).

### 2.4 JIT Provisioning

Just-in-time provisioning creates an Apohara tenant record on first successful SSO login without requiring pre-population of a user database.

On successful ID token validation or SAML assertion verification:

1. Extract the `sub` claim (OIDC) or `NameID` (SAML) as the canonical IdP subject identifier.
2. Look up `tenant_id` by `(idp_issuer, sub)` in the tenant store (SQLite-backed, schema in `billing/tenant_model.py`).
3. If not found: call `create_tenant(org_name, plan="enterprise")` → generates `org_id` and HMAC key.
4. Map `sub` → `org_id` in the `sso_identities` table (schema added in follow-up migration).
5. Extract role from IdP group claims (e.g., Okta group `apohara-admin` → `role=admin`; default: `role=viewer`).
6. Issue Apohara JWT (see §2.5) with `sub`, `org_id`, `role`.

SCIM 2.0 (RFC 7644) handles pre-provisioning and deprovisioning in environments that require it. When an SCIM `DELETE /Users/{id}` event arrives, the corresponding `org_id` is suspended and any active JWTs for that `sub` are added to the revocation blocklist. SCIM implementation is deferred to Phase 3.

### 2.5 JWT Issuance and Session Management

Post-SSO, Apohara issues its own short-lived JWT. This decouples the Apohara session from the IdP session, enabling:

- Short TTL (15 minutes) without forcing re-auth at the IdP on every API call.
- Role/permission claims embedded in the token for stateless authorization at each endpoint.
- Revocation via a lightweight blocklist (Redis or in-process LRU) without modifying the IdP session.

**JWT Claims:**

| Claim | Type | Description |
|---|---|---|
| `sub` | string | IdP subject identifier (email or opaque ID) |
| `org_id` | string | Apohara tenant UUID |
| `role` | string | `"admin"` \| `"super_admin"` \| `"viewer"` |
| `iat` | integer | Issued-at (Unix timestamp) |
| `exp` | integer | Expiry (iat + 900 seconds = 15 minutes) |
| `iss` | string | `"https://api.apohara.dev"` |
| `jti` | string | Unique token ID (16 random bytes, hex-encoded) — for revocation |

**Algorithm:** HS256 with `APOHARA_JWT_SECRET` (min 32 bytes). In production, migrate to RS256 with a rotating keypair to enable public key verification by downstream services without sharing the signing secret.

**Session storage:** Stateless JWT only — no server-side session store for the happy path. Revocation uses a blocklist keyed by `jti`. The blocklist is ephemeral (process-scoped in the PoC); production uses Redis with TTL equal to the token's remaining lifetime.

**Refresh:** OIDC: use the refresh_token from the IdP's token response to obtain a new id_token without re-authentication. SAML: re-initiate SP-initiated flow (SAML has no refresh_token concept). Refresh window: 7 days for both protocols (matching the IdP session lifetime for most enterprise configurations).

---

## 3. Design — Audit Log API

### 3.1 Query Endpoint

```
GET /v1/admin/audit
```

**Authentication:** Apohara JWT (see §4) in `Authorization: Bearer <token>` header or `apohara_jwt` cookie.

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `since` | ISO 8601 string | Lower time bound (inclusive). Example: `2026-05-01T00:00:00Z` |
| `until` | ISO 8601 string | Upper time bound (inclusive). Example: `2026-05-18T23:59:59Z` |
| `verdict_filter` | string | One of `verified`, `risky`, `blocked`. Returns only matching entries |
| `tenant_id` | string | Filter to a specific tenant. Only accessible to `super_admin` role |
| `cursor` | string | Opaque pagination cursor (base64url-encoded `signed_hash` of last-seen entry) |
| `limit` | integer | Page size. Default: 50. Max: 500 |

**Response Schema:**

```json
{
  "entries": [
    {
      "verdict": "verified",
      "signed_hash": "ab12cd...",
      "prev_hash": "00000...",
      "signature": "hmac-hex...",
      "ts": 1747612800.123,
      "tenant_id": "org-uuid",
      "attackers": [...],
      "memory_isolation": {...},
      "latency_ms": 1842.5,
      "cost_estimate_usd": 0.000312
    }
  ],
  "next_cursor": "base64url-encoded-signed-hash-or-null",
  "total_returned": 50
}
```

**Tamper-evidence at API layer:** Before returning any entry, the server re-derives the `signed_hash` and `signature` from the raw payload. If either fails to match, the entry is excluded and an `audit_integrity_error` metric is incremented. This catches in-place tampering of the ledger file between write and read. (Full chain verification via `VerdictVault.verify_chain()` is too expensive per-request; it runs as a scheduled background job.)

**Cursor design:** The cursor is the base64url encoding of the `signed_hash` of the last entry on the current page. On the next request, the server scans the ledger from the beginning, skipping entries until it finds the hash matching the cursor, then serves the next `limit` entries. This is O(N) per page in the worst case; for ledgers with millions of entries, a production implementation should maintain a B-tree index on `signed_hash` + `ts`. The O(N) scan is acceptable for Phase 2 (ledger sizes expected in the low thousands).

### 3.2 NDJSON Export Endpoint

```
GET /v1/admin/audit/export.ndjson?since=<ISO8601>&until=<ISO8601>
```

Returns a streaming NDJSON (newline-delimited JSON) response, one ledger entry per line. This format is directly ingestible by:

- **Splunk HEC** (`curl -H "Authorization: Splunk <token>" --data-binary @export.ndjson https://splunk-host/services/collector`)
- **Datadog Log Management** (`datadog-agent log tail` or direct API POST with `Content-Type: application/x-ndjson`)
- **Sumo Logic** (HTTP Source accepts NDJSON)
- **Elastic Filebeat** (`filebeat.inputs` with `type: log` parsing NDJSON)

Response headers:
```
Content-Type: application/x-ndjson
Content-Disposition: attachment; filename="apohara-audit-<since>-<until>.ndjson"
Transfer-Encoding: chunked
```

No pagination cursor needed — the export is a single streaming response bounded by `since`/`until`.

### 3.3 WebSocket Streaming (Future — Phase 3)

A real-time audit stream endpoint is planned:

```
WSS /v1/admin/audit/stream
```

This would emit new ledger entries in real time as they are appended, enabling push-based SIEM integration without polling. This is out of scope for this RFC and is deferred to Phase 3.

---

## 4. Authentication and RBAC

### 4.1 JWT-Based Admin Authentication

Every request to `/v1/admin/*` must carry a valid Apohara JWT (see §2.5). The JWT is verified per the following procedure:

1. Extract token from `Authorization: Bearer <token>` or `apohara_jwt` cookie.
2. Verify HS256 signature against `APOHARA_JWT_SECRET`.
3. Verify `exp` > current time (reject expired tokens).
4. Verify `iss` == `"https://api.apohara.dev"`.
5. Verify required claims present: `sub`, `org_id`, `role`, `jti`.
6. Check `jti` not in revocation blocklist.
7. Extract `org_id` and `role` for downstream authorization.

In FastAPI, steps 1–7 would be implemented as a `Depends()` dependency, injecting `(org_id, role)` into the endpoint handler. The PoC scaffold in `main.py` exposes these as query parameters for development convenience; production deployment must replace query parameters with the `Depends()` pattern.

### 4.2 Role-Based Access Control

| Role | Scope |
|---|---|
| `viewer` | Read own tenant's audit entries. Cannot use `tenant_id` cross-tenant query param. Cannot call export endpoint. |
| `admin` | Read + export own tenant's audit entries. Can filter by all parameters except cross-tenant `tenant_id`. |
| `super_admin` | Read + export all tenants. Can use `tenant_id` param to query any tenant. Required for `GET /v1/admin/audit?tenant_id=<other-org>`. |

Role is embedded in the JWT `role` claim. Role assignment happens at JIT provisioning time based on IdP group membership. Role elevation requires a `super_admin` to update the tenant record — there is no self-elevation path.

---

## 5. Security Considerations

### 5.1 Token Rotation and TTL

The 15-minute JWT TTL limits the window of credential theft exploitation. Combined with:

- OIDC refresh tokens valid for 7 days (rotated on each use — one-time use refresh tokens per RFC 6749 §10.4 recommendation).
- Refresh token storage in an `HttpOnly; Secure; SameSite=Strict` cookie to prevent JavaScript access.
- `jti` revocation blocklist for immediate logout scenarios (employee termination, suspected compromise).

The effective attack window for a stolen JWT is at most 15 minutes without access to the refresh token.

### 5.2 MFA Enforcement

MFA is delegated to the IdP via:

- **OIDC:** `acr_values=phr` in the authorization request signals the IdP to require phishing-resistant MFA (WebAuthn/FIDO2). If the IdP does not support `phr`, fall back to `acr_values=mfa` (any second factor). Apohara validates the `acr` claim in the returned ID token.
- **SAML:** `<samlp:RequestedAuthnContext>` element with `AuthnContextClassRef` set to `urn:oasis:names:tc:SAML:2.0:ac:classes:MobileTwoFactorContract` (or stronger). IdP assertion must include matching `AuthnStatement/AuthnContext`.

If the IdP returns a token/assertion without the requested authentication context, the callback handler rejects the session and redirects to an error page explaining the MFA requirement.

### 5.3 Replay Attack Resistance

Three layers:

1. **JWT `exp` claim (15 minutes):** Tokens expire quickly. A replayed token is invalid after 900 seconds regardless of `jti` state.
2. **JWT `jti` (unique token ID):** Every issued JWT has a unique `jti`. On logout, the `jti` is added to the revocation blocklist with TTL equal to the remaining lifetime of that token. An attacker replaying a valid but logged-out token will hit the blocklist.
3. **OIDC state parameter + PKCE:** The `state` parameter is a per-request random nonce stored in a `HttpOnly` cookie. The callback handler validates `state` before accepting the authorization code. `code_challenge` (PKCE) additionally binds the code to the session that initiated the flow, preventing code interception by a malicious redirect URI.

### 5.4 Cross-Tenant Data Leakage Prevention

The audit log API enforces tenant isolation at two layers:

1. **JWT claim enforcement:** The `org_id` extracted from the verified JWT is used as the mandatory tenant filter for `admin` and `viewer` roles. The `tenant_id` query parameter is ignored for non-`super_admin` roles — the code always uses `requester_org_id` from the JWT, not the user-supplied parameter.
2. **No SQL joins across tenants:** The current ledger implementation uses a flat JSONL file with per-entry `tenant_id` filtering. There are no join queries that could accidentally expose cross-tenant data through ORM misconfiguration.

When the ledger migrates to a relational store, all queries must include `WHERE tenant_id = :requester_org_id` (parameterized) and the `super_admin` path must be explicitly branched — no implicit "if no filter provided, return all" default.

### 5.5 HMAC Re-derivation Before Serving

Every audit entry returned by the API is re-verified server-side by re-deriving its `signed_hash` and `signature` from the stored payload using the same `VerdictVault` logic used at write time. This catches:

- Direct editing of the `ledger.jsonl` file (payload tampered → hash mismatch).
- `signed_hash` field replacement without corresponding payload change (hash mismatch on re-derivation).
- HMAC field replacement (signature mismatch).

Tampered entries are excluded from API responses and trigger an `audit_integrity_violation` metric (Prometheus counter). Full chain verification (scanning all entries in sequence to verify `prev_hash` linkage) runs as a scheduled background job every 6 hours, not inline with API requests.

### 5.6 Rate Limiting

Per-organization call quotas are already implemented in `billing/tenant_model.py` (`check_quota`). The audit log endpoints participate in the same quota system — a tenant on the `free` plan (100 calls/month) cannot use audit log API calls to exhaust the quota of other tenants. Enterprise plans have higher or unlimited quotas. Rate limiting is enforced before ledger reads to prevent CPU exhaustion via rapid cursor-pagination requests against a large ledger.

---

## 6. Backwards Compatibility

### 6.1 Existing Flows Preserved

All existing endpoints are unaffected by this RFC:

- `POST /v1/verify` — BYOK + 9-vendor adversarial ensemble + INV-15. No change.
- `POST /v1/demo_verify` — Demo mode with server-side key. No change.
- `GET /v1/audit/{verdict_id}` — Single-entry lookup. No change.
- `GET /v1/audit/recent` — Recent entries (admin-key gated). No change.
- `POST /v1/verify_stream` — SSE streaming. No change.

### 6.2 Enterprise Mode Gate

All new SSO and audit log API endpoints are registered only when `APOHARA_ENTERPRISE_MODE=1` is set in the environment. The default is off, so:

- Existing deployments are unaffected.
- Self-hosted installations without enterprise licensing do not expose enterprise endpoints.
- The FastAPI app size and startup time are unaffected when enterprise mode is off.

This is implemented as a top-level `if` block in `main.py` that conditionally imports `enterprise.audit_api` and registers the endpoint handler. The `enterprise/` package exists in the codebase but is not imported in the hot path.

### 6.3 Migration Path for Existing BYOK Users

Existing users with personal API keys can claim a tenant identity post-SSO:

1. User authenticates via SSO for the first time → JIT provisioning creates `org_id = "org-new-uuid"`.
2. An admin associates the new `org_id` with the user's existing BYOK-linked `tenant_id` via a migration endpoint (implementation deferred to Phase 3).
3. Historical ledger entries written with the old `tenant_id` are tagged in the tenant mapping table so audit queries that use the new SSO-issued `org_id` still surface them.

Until the migration endpoint exists, historical entries are accessible via the existing `GET /v1/audit/{verdict_id}` endpoint (not tenant-filtered) by any caller with the `signed_hash`.

---

## 7. Alternatives Considered

### 7.1 API Key Only (Rejected)

The simplest extension would be to issue per-organization API keys and require them on admin endpoints. This was rejected because:

- **No identity federation:** API keys do not bind to a specific human identity, making MFA enforcement impossible.
- **No lifecycle automation:** Deprovisioning requires explicit key revocation. If a departing employee retains their API key, access persists until manual intervention.
- **No compliance evidence:** SOC 2 auditors expect to see IdP-integration evidence, not a list of static secrets.

API keys remain appropriate for machine-to-machine access (CI/CD pipelines). The recommended pattern is: SSO for human access, API keys for service accounts — both supported in this RFC.

### 7.2 Managed SSO Providers (Auth0, Clerk, WorkOS) — Deferred

Auth0, Clerk, and WorkOS provide managed SSO-as-a-service that would eliminate implementation complexity. WorkOS in particular is designed for B2B SaaS SAML/OIDC integration and handles the enterprise IdP compatibility matrix.

This option was deferred — not rejected — for the following reasons:

- **External dependency:** Managed SSO adds a mandatory third-party in the authentication critical path. An outage or pricing change at the SSO provider blocks all enterprise logins.
- **Cost at scale:** WorkOS charges per MAU at enterprise plans. For a product with many enterprise users, the per-seat cost may exceed the value delivered.
- **Data residency:** Some enterprise customers (healthcare, financial services, EU GDPR-sensitive deployments) require that authentication flows not pass through US-hosted third-party infrastructure. A self-hosted OIDC integration avoids this.

WorkOS or Auth0 integration remains the recommended path if Phase 3 enterprise adoption accelerates faster than the self-hosted SSO implementation can mature. The interface contracts defined in this RFC (JIT provisioning, JWT issuance, audit log API) are provider-agnostic and would remain unchanged whether the SSO layer is self-hosted or delegated to a managed provider.

### 7.3 mTLS Instead of JWT (Rejected)

Mutual TLS would provide strong client authentication without bearer token management. It was rejected for the admin API because:

- **Browser incompatibility:** The Apohara PROBANT admin UI runs in a browser. Browser-side mTLS requires client certificates distributed to end users via OS certificate stores, which is operationally complex and fragile (certificate rotation, cross-browser behavior, corporate proxy interference).
- **Tooling friction:** Splunk, Datadog, and Elastic export integrations would all require custom certificate configuration per integration, compared to a simple `Authorization: Bearer <token>` header.

mTLS remains appropriate for internal service-to-service communication (e.g., the Guard ML subprocess calling the PROBANT backend, or a future dedicated audit microservice calling the ledger reader). For those cases, it is the preferred option.

---

## 8. References

- OASIS Security Services (SAML 2.0) Technical Committee. *Assertions and Protocols for the OASIS Security Assertion Markup Language (SAML) V2.0*. OASIS Standard, March 2005. [https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf](https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf)
- Hardt, D. (Ed.). *The OAuth 2.0 Authorization Framework*. RFC 6749. IETF, October 2012. [https://www.rfc-editor.org/rfc/rfc6749](https://www.rfc-editor.org/rfc/rfc6749)
- Jones, M., Bradley, J., Sakimura, N. *JSON Web Token (JWT)*. RFC 7519. IETF, May 2015. [https://www.rfc-editor.org/rfc/rfc7519](https://www.rfc-editor.org/rfc/rfc7519)
- Sakimura, N., Bradley, J., Jones, M., de Medeiros, B., Mortimore, C. *OpenID Connect Core 1.0*. OpenID Foundation, November 2014. [https://openid.net/specs/openid-connect-core-1_0.html](https://openid.net/specs/openid-connect-core-1_0.html)
- Hunt, P., Grizzle, K., Wahlstroem, E., Mortimore, C. *System for Cross-domain Identity Management: Protocol (SCIM 2.0)*. RFC 7644. IETF, September 2015. [https://www.rfc-editor.org/rfc/rfc7644](https://www.rfc-editor.org/rfc/rfc7644)
- Lodderstedt, T. (Ed.), Campbell, B., Tokio, N., Tschofenig, H. *OAuth 2.0 Security Best Current Practice*. RFC 9700. IETF, January 2025. [https://www.rfc-editor.org/rfc/rfc9700](https://www.rfc-editor.org/rfc/rfc9700)
