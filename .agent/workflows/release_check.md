---
description: Checklist to ensure version integrity during releases.
---

# Release Safety Check

Run this checklist BEFORE notifying the user of a new release.

## 1. Version Synchronization
- [ ] Check `src/navidrome_mcp_server.py`: `__version__` match target?
- [ ] Check `pyproject.toml`: `version` match target?
- [ ] Check `docs/roadmap/changelog.md`: Entry exists for this version?

## 2. Public Surface
- [ ] Check `navidrome://info` (in `server.py`): Does it need updates?
- [ ] Check `README.md`: Do new features require doc updates?

## 3. Operations
// turbo
- `grep -r "__version__" src/`
// turbo
- `grep -r "version =" pyproject.toml`
