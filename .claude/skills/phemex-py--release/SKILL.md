---
name: phemex-py--release
description: "Release workflow for phemex-py: version bump, changelog update, commit, tag, push, build, and publish to PyPI. Use when the user asks to bump the version, cut a release, publish a new version, or invoke /phemex-py--release."
---

# Release Workflow

Bump version, update changelog, commit, tag, push, build, and publish.

## Version Locations

Update the version string in all four places:

1. `pyproject.toml` — `version = "X.Y.Z"`
2. `src/phemex_py/__init__.py` — `__version__ = "X.Y.Z"`
3. `CHANGELOG.md` — add new section at top
4. `uv.lock` — run `uv lock` to sync automatically

## Steps

1. **Read current state** — check `pyproject.toml`, `__init__.py`, `CHANGELOG.md`, and recent `git log --oneline` to understand what changed since the last release.

2. **Bump version** — edit `pyproject.toml` and `src/phemex_py/__init__.py` with the new version.

3. **Update CHANGELOG.md** — add a new `## X.Y.Z (YYYY-MM-DD)` section above the previous release. Summarize changes from commits since the last tag using conventional changelog sections (`### Added`, `### Fixed`, `### Changed`, `### Breaking Changes`) as appropriate.

4. **Sync lock file** — run `uv lock`.

5. **Commit** — stage all changed files and commit:
   ```
   chore: bump version to X.Y.Z and update changelog
   ```

6. **Tag and push** — `git tag vX.Y.Z && git push origin main --tags`

7. **Build** — `just build`

8. **Publish** — `just publish`
