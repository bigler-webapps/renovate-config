# Renovate configuration

Shared Renovate presets for Bigler Webapps repositories.

- `default`: organisation-wide defaults.
- `auto-merge`: opt-in auto-merge rules for eligible updates.
- `library`: range handling for shared libraries.

Use `library` only in a repository that publishes a package other repositories depend on, where a declared range is a promise to consumers. It makes Renovate widen the range instead of raising its floor. Apps pin dependencies exactly and must not extend this preset.
