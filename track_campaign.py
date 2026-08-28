"""Send one campaign message, then report the opening and bounce trail."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from typing import Any

from campaign_delivery import campaign_client


def message_events(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Pull the event records out of an /v1/email/event/list data payload."""
    return payload.get("items", [])


def relevant_events(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [event for event in events if event.get("type") in {"open", "bounce"}]


def main() -> None:
    parser = argparse.ArgumentParser(description="Track one e-commerce campaign email.")
    parser.add_argument("--to", required=True, help="Recipient address")
    parser.add_argument("--offer", required=True, help="Offer text for the campaign")
    args = parser.parse_args()

    infrai = campaign_client()
    sent = infrai.email.send(
        to=args.to,
        subject=f"Your store update: {args.offer}",
        html=f"<h1>{args.offer}</h1><p>Visit the store when you are ready.</p>",
    )
    message_id = sent["message_id"]
    events = infrai.email.event.list(message_id=message_id)
    signals = relevant_events(message_events(events))

    print(f"sent message_id={message_id}")
    print(f"open/bounce events: {signals}")


if __name__ == "__main__":
    main()
