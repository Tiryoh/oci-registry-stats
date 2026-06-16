# Roadmap

This project currently focuses on collecting repository/package-level download
counts that can run unattended from GitHub Actions.

## Phase 1: Stable Scheduled Collection

- [x] Collect Docker Hub repository-level total pulls.
- [x] Collect GHCR package-level total downloads from the public package page.
- [x] Store per-target JSONL snapshots.
- [x] Generate `data/latest.json`.
- [x] Generate `data/latest.csv`.
- [x] Generate Shields.io-compatible badge JSON files.
- [x] Compute weekly and monthly values from historical snapshots when enough
      history exists.
- [x] Keep the command-line interface thin for GitHub Actions usage.

## Phase 2: Optional Tag-Level Metrics

- [ ] Decide whether tag-level metrics are worth the extra operational
      complexity.
- [ ] Add GHCR tag-level collection behind an explicit config option.
- [ ] Use a `read:packages` GitHub token to resolve moving GHCR tags through the
      GitHub Packages API.
- [ ] Consider a fallback mode where fixed GHCR version IDs are configured
      manually for known tags.
- [ ] Clearly document that GHCR moving tag metrics are for the currently
      referenced package version, not the lifetime total for the tag name.
- [ ] Add tests for GHCR tag version resolution and moving-tag behavior.

## Phase 3: Docker Hub Analytics

- [ ] Investigate Docker Hub DVP/DSOS Analytics access for this repository.
- [ ] Add a Docker Hub analytics collector if tag/digest CSV or API access is
      available.
- [ ] Support weekly and monthly Docker Hub tag-level downloads from analytics
      exports.
- [ ] Preserve the current public API collector as the default for normal Docker
      Hub repositories.

## Phase 4: Reporting Improvements

- [ ] Add a generated static HTML dashboard from `data/latest.json`.
- [ ] Add optional Prometheus metrics output.
- [ ] Add parser failure diagnostics that can save sanitized debug HTML when
      explicitly enabled.
- [ ] Consider a SQLite backend if JSONL snapshot files become too large.
