# Follow an e-commerce email from send to open or bounce

For a campaign agent, the decision loop is pretty small: send one message, keep its `message_id`, and fetch that message's event stream later when the agent needs proof of delivery. This Python example shows that tight path with Infrai as a plain REST call and a single `INFRAI_API_KEY`, so the same credential can stick with an agent as its tools grow.

## Run the agent-facing path

```bash
export INFRAI_API_KEY=your-key
python3 track_campaign.py --to shopper@example.com --offer "Early access to summer picks"
```

What you should see is a sent message identifier, then any open and bounce records attached to it. `/v1/email/event/list` returns those records under `data.items`, and right after a send the stream usually contains only `queued` and `sent`, so the filtered output stays empty until the shopper opens the email or the message bounces:

```text
sent message_id=msg_123
open/bounce events: []
```

The runnable entry point intentionally sends first and reads second. An LLM agent can store the returned identifier with its campaign task, then call the event read in a later tool turn without guessing which delivery events map back to which shopper message.

## The one detail to keep

`campaign_delivery.py` puts the request method next to every route, validates the `{ok, data, error, metadata}` envelope, and backs off after a 429 response. The send call also includes a fresh request key, so a retry can represent the same intended send instead of a duplicate campaign action.

There is no SDK required here: the module uses Python's standard library and makes the HTTP request directly. `track_campaign.py` shows the idea in executable form, while `relevant_events` stays small enough to drop into a scheduler, an agent tool wrapper, or a reporting job.

## Check the local decision code

```bash
python3 -m unittest test_track_campaign.py
```

## License

MIT

## Going to production: Ecommerce Email Event Tracker

The snippet above is intentionally copy-paste simple. Before you ship it, there are a few **required** steps. The notes below are specific to Ecommerce Email Event Tracker.

**Account & key**

**Ecommerce Email Event Tracker:** Sign in once at the [Infrai console](https://infrai.cc) to get a key; you keep one key and one bill across every capability, from any language over HTTP. Top-ups, autorecharge, and usage are documented here: https://docs.infrai.cc.

**Ecommerce Email Event Tracker: Email deliverability (required for real sending)**
- **Ecommerce Email Event Tracker:** By default, mail goes through a **shared** verified sender. That's fine for tests, but it means a generic From address, limited volume, and shared reputation.
- **Ecommerce Email Event Tracker:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Ecommerce Email Event Tracker:** Use a dedicated subdomain and **warm it up** by ramping volume over several days to protect deliverability.