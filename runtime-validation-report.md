# Runtime Validation Report

**Generated**: 2026-11-13T20:17:46-05:00
**Target**: `C:\Users\sant1\Downloads\EmpleoWeb`
**Commit validated**: `2163e88f6c02622a2729534d831ebfdeaee19aeb`
**Integration commit**: `e213327`

## Summary

| Step | Status | Exit Code | Details |
|---|---|---:|---|
| Initial repository checks | PASS | 0 | Clean `integration/r1-02c`; HEAD matches the documented R1-02D commit |
| Locked dependency installation | PASS | 0 | `npm ci`; 36 packages installed, 0 vulnerabilities |
| CSS compilation | PASS | 0 | Tailwind CSS CLI 4.3.3; byte-for-byte unchanged output |
| Python integration suite | PASS | 0 | 57 tests passed |
| Catalog and candidate validation | PASS | 0 | Schema 2 snapshot and 0-candidate inbox validated |
| JavaScript and UI checks | PASS | 0 | `app.js`, `canvas.js`, and catalog UI checks passed |
| Playwright browser validation | PASS | 0 | 8/8 tests passed across Chromium desktop and mobile |
| Pages artifact generation | PASS | 0 | Exact five-file artifact generated and validated |
| Artifact reproducibility | PASS | 0 | Second generation matched file set and SHA-256 hashes |
| Remote GitHub Actions | UNVERIFIED | N/A | No push or remote dispatch was performed |

**Overall**: PARTIAL — local validation and the remote `validate` job are green;
the first Pages deployment attempt failed in `Deploy Pages`.

## Environment

- Node.js: `v24.22.2`
- npm: `11.19.1`
- Python: `3.13.3`
- Docker: unavailable; no infrastructure tier is required by this static site
- Playwright Chromium: installation command succeeded
- Browser tier: primary Playwright validation used

## Test Evidence

### Commands

```text
npm ci
npm run build:css
python -m unittest discover -s tests -v
python scripts/build_catalog.py --check
python scripts/validate_catalog.py
python scripts/validate_candidates.py data/candidates/inbox.example.json
node --check app.js
node --check canvas.js
node tests/catalog_ui.test.cjs
npx playwright install --with-deps chromium
npm run test:e2e
python scripts/pages_artifact.py --output <temporary-directory>
```

### Results

- `npm ci` did not modify `package-lock.json`; no new dependency was added.
- `npm run build:css` preserved `styles.css` SHA-256
  `AB0088064235C30BDF1D6DC1E79DC230CFFA89703DFB75FE61F2E4DCB0C121FA`.
- Source CSS files remained unchanged during compilation.
- Python suite: 57 passed.
- Catalog validator: 5 demonstration records, 0 active real opportunities.
- Candidate validator: 0 candidates.
- E2E: 8 passed, 0 failed, 0 skipped; desktop and mobile projects.
- Playwright's `webServer` started `python server.py` and reached
  `http://127.0.0.1:4173/`.

The validator warnings concern the intentionally historical/demo catalog
records and an unclassified mode; they are expected and do not change the
published active-opportunity count.

## Pages Artifact

The official generator produced exactly:

```text
index.html
app.js
canvas.js
styles.css
data/opportunities.json
```

SHA-256:

| File | SHA-256 |
|---|---|
| `index.html` | `AC3048752DA438690632C95B9A6DB9454F87E657C521DB68818D9D23E0A03CBB` |
| `app.js` | `C25DA1EA6EC24BDC1A5179367705A7180D661B76A31B5C9BE64D284FB96D47B9` |
| `canvas.js` | `E353C7F800E0CF75AAA34306724D0D19FE1303A4D2AF21FF31D4B52A9C631610` |
| `styles.css` | `AB0088064235C30BDF1D6DC1E79DC230CFFA89703DFB75FE61F2E4DCB0C121FA` |
| `data/opportunities.json` | `13F91B9090B2377F0E8B770D7F513EF767CE9904A4B2EBB72D56F868BBF80B05` |

The artifact validator confirmed local resource references, the `/WebRutaSistemas/`
subpath contract, Schema 2, snapshot identity, and the absence of runtime CDN,
absolute asset, or `/api/opportunities` dependencies. A second artifact
generation matched the complete file set and all hashes.

## CI

The workflow at `.github/workflows/refresh-catalog.yml` has
`workflow_dispatch`, uses `npm ci`, compiles CSS before validation and
packaging, separates `validate` from `publish`, and grants Pages permissions
only to the publish job. The inspected remote workflow is active.

The branch `integration/r1-02c` was pushed to `main` with a fast-forward from
`20d2002` to `9bb6b397c04fc1f096a8a4d2e0214f06b7922704`. No force push was
used and `main` history was not rewritten.

Run `43603777615` (`#13`) validated the exact SHA
`9bb6b397c04fc1f096a8a4d2e0214f06b7922704`:

- `validate`: **success**; checkout, Node/Python setup, CSS compilation,
  57-test suite, catalog validators, JavaScript checks, UI checks and E2E all
  passed.
- `publish`: **failure** only at `Deploy Pages`; artifact generation,
  `configure-pages`, and `Upload Pages artifact` succeeded. The deployment
  action reported: `No artifacts named "github-pages" were found for this
  workflow run`.

The failure is confined to the GitHub Pages deployment service/action metadata
lookup after artifact upload. No local source, catalog, workflow, permission,
or dependency change was made to mask it. The prior remote run `43144107491`
(`#12`) on `20d2002` remains historical and is not used as evidence for this
release.

## Issues Found

| Severity | Description | Decision |
|---|---|---|
| Informational | Docker is unavailable | No impact; the project is a static site and has no infrastructure tier |
| Blocking | Pages deployment metadata lookup failed in run `43603777615` | Retry the official workflow before declaring publication complete |

No source or catalog correction was required. Seed and snapshot were not
modified.

## Next Step

Retry the official workflow against `9bb6b397` without changing the artifact or
permissions. Only after a successful `publish` job should R1-04 be completed;
R1-05 remains reserved for remote resource and content verification.
