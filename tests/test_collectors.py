from datetime import datetime, timezone

from registry_stats.collectors.dockerhub import collect_dockerhub_repository
from registry_stats.models import TargetConfig


class FakeClient:
    def get_json(self, url, headers=None):
        return {
            "namespace": "example",
            "name": "image",
            "pull_count": 123456,
            "star_count": 12,
            "last_updated": "2026-06-01T00:00:00Z",
        }


def test_collect_dockerhub_repository() -> None:
    target = TargetConfig(
        id="dockerhub_image",
        registry="dockerhub",
        scope="repository",
        namespace="example",
        repository="image",
    )

    result = collect_dockerhub_repository(
        target,
        FakeClient(),  # type: ignore[arg-type]
        datetime(2026, 6, 15, tzinfo=timezone.utc),
    )

    assert result.snapshot.metrics.total_downloads == 123456
    assert result.snapshot.methods["total_downloads"] == "dockerhub_repository_api"
