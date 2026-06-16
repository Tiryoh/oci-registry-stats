from __future__ import annotations

import time

import httpx

from registry_stats.models import CollectionConfig


class HttpClient:
    def __init__(self, config: CollectionConfig, headers: dict[str, str] | None = None) -> None:
        base_headers = {"User-Agent": config.user_agent}
        if headers:
            base_headers.update(headers)
        self._client = httpx.Client(timeout=config.timeout_seconds, headers=base_headers)
        self._retry_count = config.retry_count
        self._backoff = config.retry_backoff_seconds

    def close(self) -> None:
        self._client.close()

    def get_json(self, url: str, headers: dict[str, str] | None = None) -> dict:
        response = self._request("GET", url, headers=headers)
        return response.json()

    def get_text(self, url: str, headers: dict[str, str] | None = None) -> str:
        response = self._request("GET", url, headers=headers)
        return response.text

    def post_json(self, url: str, json: dict) -> dict:
        response = self._request("POST", url, json=json)
        return response.json()

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self._retry_count + 1):
            try:
                response = self._client.request(method, url, **kwargs)
                if response.status_code < 400:
                    return response
                last_error = httpx.HTTPStatusError(
                    f"{method} {url} returned {response.status_code}",
                    request=response.request,
                    response=response,
                )
            except httpx.HTTPError as exc:
                last_error = exc
            if attempt < self._retry_count:
                time.sleep(self._backoff * (attempt + 1))
        assert last_error is not None
        raise last_error
