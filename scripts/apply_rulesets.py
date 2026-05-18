#!/usr/bin/env python3
"""Apply branch rulesets defined in rulesets/*.json to repos listed in repos.yml.

Idempotent: looks up existing rulesets by name; PATCH if exists, POST if not.

Requires env var GITHUB_TOKEN with `Administration: write` on each target repo.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests
import yaml

API = "https://api.github.com"
ROOT = Path(__file__).resolve().parent.parent
RULESETS_DIR = ROOT / "rulesets"
REPOS_FILE = RULESETS_DIR / "repos.yml"


def load_ruleset(name: str) -> dict:
    path = RULESETS_DIR / f"{name}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_repos() -> list[dict]:
    with REPOS_FILE.open(encoding="utf-8") as f:
        return yaml.safe_load(f)["repos"] or []


def gh_session(token: str) -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    return s


def find_existing(session: requests.Session, slug: str, name: str) -> int | None:
    r = session.get(f"{API}/repos/{slug}/rulesets", timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    for rs in r.json():
        if rs.get("name") == name:
            return rs["id"]
    return None


def apply(session: requests.Session, slug: str, ruleset: dict) -> None:
    name = ruleset["name"]
    existing_id = find_existing(session, slug, name)
    if existing_id is None:
        r = session.post(f"{API}/repos/{slug}/rulesets", json=ruleset, timeout=30)
        action = "created"
    else:
        # PUT replaces, target field not accepted on update — strip it.
        body = {k: v for k, v in ruleset.items() if k != "target"}
        r = session.put(
            f"{API}/repos/{slug}/rulesets/{existing_id}", json=body, timeout=30
        )
        action = "updated"
    if r.status_code >= 400:
        print(f"  ERROR {slug} {name}: {r.status_code} {r.text}", file=sys.stderr)
        r.raise_for_status()
    print(f"  {action}: {slug}#{name}")


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN env var is required.", file=sys.stderr)
        return 2

    repos = load_repos()
    if not repos:
        print("No repos configured in repos.yml.")
        return 0

    session = gh_session(token)
    errors = 0
    for entry in repos:
        slug = entry["slug"]
        names = entry.get("rulesets", [])
        print(f"{slug}: {', '.join(names) or '(none)'}")
        for name in names:
            try:
                ruleset = load_ruleset(name)
                apply(session, slug, ruleset)
            except requests.HTTPError as exc:
                errors += 1
                print(f"  failed: {exc}", file=sys.stderr)
            except FileNotFoundError:
                errors += 1
                print(f"  unknown ruleset: {name}", file=sys.stderr)
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
