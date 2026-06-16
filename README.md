# OCI Registry Stats

Collect Docker Hub and GHCR download statistics on a daily schedule and publish
JSON, CSV, and Shields.io endpoint files under `data/`.

## Badges

Total downloads:

[![Docker Hub pulls](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FTiryoh%2Foci-registry-stats%2Fmain%2Fdata%2Fshields%2Fdockerhub_ros2_desktop_vnc_total.json)](https://hub.docker.com/r/tiryoh/ros2-desktop-vnc)
[![GHCR downloads](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FTiryoh%2Foci-registry-stats%2Fmain%2Fdata%2Fshields%2Fghcr_ros2_desktop_vnc_package_total.json)](https://github.com/Tiryoh/docker-ros2-desktop-vnc/pkgs/container/ros2-desktop-vnc)

Weekly and monthly badges are generated from committed daily snapshots. They
show `unknown` until enough history exists.

```markdown
[![Docker Hub pulls](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FTiryoh%2Foci-registry-stats%2Fmain%2Fdata%2Fshields%2Fdockerhub_ros2_desktop_vnc_total.json)](https://hub.docker.com/r/tiryoh/ros2-desktop-vnc)
[![GHCR downloads](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FTiryoh%2Foci-registry-stats%2Fmain%2Fdata%2Fshields%2Fghcr_ros2_desktop_vnc_package_total.json)](https://github.com/Tiryoh/docker-ros2-desktop-vnc/pkgs/container/ros2-desktop-vnc)
```

## Local Run

```bash
uv run registry-stats --config registry-stats.yaml
```

The command writes:

- `data/snapshots/*.jsonl`
- `data/latest.json`
- `data/latest.csv`
- `data/shields/*.json`

## References

This project was created with reference to
[actionstore/ghcr-stats](https://github.com/actionstore/ghcr-stats).
