# 05 — CI/CD Pipeline & Package Setup

**What to build:**
Add GitHub Actions workflow `.github/workflows/ci.yml` and finalize `pyproject.toml` entrypoints for `pip install .`.

**Blocked by:** 04 — CLI Commands Engine

**Status:** ready-for-agent

- [ ] `.github/workflows/ci.yml` runs ruff linter and pytest on every PR.
- [ ] `pip install .` installs `wikify` binary executable in PATH.
