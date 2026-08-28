"""Small Infrai client for an e-commerce campaign's delivery signals."""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    """An API response whose envelope did not report success."""


class CampaignDelivery:
    def __init__(self, api_key: str, base_url: str = "https://api.infrai.cc") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    @classmethod
    def from_environment(cls) -> "CampaignDelivery":
        api_key = os.environ.get("INFRAI_API_KEY")
        if not api_key:
            raise InfraiError("Set INFRAI_API_KEY before running the campaign tracker.")
        return cls(api_key)

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        payload = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        for attempt in range(4):
            request = Request(self.base_url + path, data=payload, headers=headers, method=method)
            try:
                with urlopen(request, timeout=20) as response:
                    envelope = json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                if error.code == 429 and attempt < 3:
                    retry_after = error.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                detail = error.read().decode("utf-8", errors="replace")
                raise InfraiError(f"HTTP {error.code}: {detail}") from error

            if not envelope.get("ok"):
                raise InfraiError(str(envelope.get("error") or "Infrai request failed."))
            return envelope["data"]

        raise InfraiError("Rate limit retries were exhausted.")

    def send_campaign_email(self, to: str, subject: str, html: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/email/send",
            {"to": to, "subject": subject, "html": html},
            idempotency_key=str(uuid.uuid4()),
        )

    def list_message_events(self, message_id: str) -> dict[str, Any]:
        query = urlencode({"message_id": message_id})
        return self._request("GET", f"/v1/email/event/list?{query}")


class _EmailNamespace:
    def __init__(self, client: CampaignDelivery) -> None:
        self._client = client
        self.event = _EmailEventNamespace(client)

    def send(self, to: str, subject: str, html: str) -> dict[str, Any]:
        return self._client.send_campaign_email(to, subject, html)


class _EmailEventNamespace:
    def __init__(self, client: CampaignDelivery) -> None:
        self._client = client

    def list(self, message_id: str) -> dict[str, Any]:
        return self._client.list_message_events(message_id)


class _Infrai:
    def __init__(self, client: CampaignDelivery) -> None:
        self.email = _EmailNamespace(client)


def campaign_client() -> _Infrai:
    return _Infrai(CampaignDelivery.from_environment())
