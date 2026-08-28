import unittest

from track_campaign import message_events, relevant_events


class EventPayloadTest(unittest.TestCase):
    def test_reads_the_items_key_returned_by_the_event_list_route(self) -> None:
        payload = {
            "items": [{"type": "sent"}, {"type": "open"}],
            "next_cursor": None,
            "count": 2,
        }
        self.assertEqual(relevant_events(message_events(payload)), [{"type": "open"}])

    def test_missing_items_is_an_empty_stream(self) -> None:
        self.assertEqual(message_events({"count": 0}), [])


class RelevantEventsTest(unittest.TestCase):
    def test_keeps_only_opens_and_bounces(self) -> None:
        events = [{"type": "delivered"}, {"type": "open"}, {"type": "bounce"}]
        self.assertEqual(relevant_events(events), [{"type": "open"}, {"type": "bounce"}])


if __name__ == "__main__":
    unittest.main()
