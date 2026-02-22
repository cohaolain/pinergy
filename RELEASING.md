# CI/CD and releasing

GitHub Actions runs on every push and pull request to `main`:

- **Unit tests** always run.
- **Integration tests** run on push to `main`, using credentials from repository secrets (so the real API is exercised in CI).

To enable integration tests in CI, add these **Actions repository secrets** (Settings → Secrets and variables → Actions):

- `PINERGY_EMAIL` – account email
- `PINERGY_PASSWORD` – account password  

If these are not set, integration tests are skipped.

## Releasing to PyPI

Pushing a tag `v*` (e.g. `v0.1.0`) runs the test job then publishes the package to PyPI.

1. Bump `version` in `pyproject.toml`.
2. Commit, push to `main`, then create and push a tag:
   ```bash
   git tag v0.1.0 && git push origin v0.1.0
   ```
3. Add an **Actions repository secret** **`PYPI_API_TOKEN`** with a PyPI API token ([create one](https://pypi.org/manage/account/token/)). You can use an environment and environment secrets instead if you want branch/tag restrictions.
