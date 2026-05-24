# APP_FINDINGS.md — renovate-config

Generated 2026-05-24 from a deep-security audit (sec_reviewer agent pass).
Cross-reference: `webapp-management/SECURITY_FINDINGS.md` (central tracking).

Already addressed:
- S33 (SHA-pinning of `actions/checkout` + `actions/setup-python` in `apply-rulesets.yml` — commit `0ca3f2f`)

---

## P3 — Tracking

### S181 — RENOVATE-NEW-automerge-no-infra-restriction — `auto-merge.json` allows infra-update auto-merge
**Severity:** P3
**File:** `auto-merge.json:8`
**Confidence:** medium
**Issue:** The preset enables `automerge: true` for all minor, patch, pin, and digest updates. The preset is opt-in (currently not extended by `webapp-management` or any tenant — `default.json` doesn't include it), but its mere existence + lack of any restriction on managers/types means it's one `"extends"` line away from auto-merging Docker image digests, Tailscale binaries, Traefik composes, or `actions/checkout` SHA bumps in infra repos.
**Repro:** A tenant adds `"extends": ["github>bigler-webapps/renovate-config:auto-merge"]`. A patch update to a Django package, Docker image, or GitHub Action is auto-merged with no human review.
**Fix:** Add `matchManagers` exclusion list to the auto-merge preset:
```json
"matchManagers": {
  "exclude": ["dockerfile", "docker-compose", "github-actions", "terraform"]
}
```
Document explicitly that `webapp-management` and `workflow-templates` must NOT extend this preset.

---

## Residual risks / lower-confidence

- Preset is currently safe because no repo extends it. The risk surfaces only if a future tenant or maintainer opts in.
