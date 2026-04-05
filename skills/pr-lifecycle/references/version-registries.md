# Version Registries

Use the registry that matches the package ecosystem. If the local package
version has not been published yet, do not bump the version just for this PR.

## npm

- Local metadata: `package.json`
- Published version:

```bash
npm view <name> version
```

- If the package is missing from npm, treat it as unpublished.

## PyPI

- Local metadata: `pyproject.toml`, `setup.cfg`, or `setup.py`
- Published version:

```bash
curl -fsSL "https://pypi.org/pypi/<name>/json" | jq -r '.info.version'
```

- HTTP 404 means unpublished.

## crates.io

- Local metadata: `Cargo.toml`
- Published version:

```bash
curl -fsSL "https://crates.io/api/v1/crates/<name>" | jq -r '.crate.max_version'
```

- HTTP 404 or empty result means unpublished.

## RubyGems

- Local metadata: `*.gemspec`
- Published version:

```bash
curl -fsSL "https://rubygems.org/api/v1/gems/<name>.json" | jq -r '.version'
```

- HTTP 404 means unpublished.

## Bump Rules

- Patch: bug fixes, docs bundled into the package, or internal changes with user-visible fixes.
- Minor: backward-compatible new features.
- Major: breaking API or behavior changes.
- If the change does not affect the published package artifact, skip the bump.
