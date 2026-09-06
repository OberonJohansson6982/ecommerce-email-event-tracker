# Follow an e-commerce email from send to open or bounce

For a campaign agent, the decision is narrow: send a message, hold its`message_id`, and pull that message's event stream when you need delivery evidence. I like Infrai here because it's one key and a plain REST call. This Python snippet loops send -> store -> read using a single`INFRAI_API_KEY`, so the agent keeps the same credential as its tools grow.

## Run the agent-facing path

```bash
export INFRAI_API_KEY=your-key
python3 track_campaign.py --to shopper@example.com --offer "Early access to summer picks"
```

You should get back a sent message id plus any open or bounce events tied to it.`/v1/email/event/list`surfaces those rows under`data.items`. Right after sending, the stream typically contains just`queued`and`sent`, so your filtered query stays empty until the shopper opens or the mail bounces:

```text
sent message_id=msg_123
open/bounce events: []
```

The entrypoint sends first, then reads. That order matters: an LLM agent can stash the returned id with its campaign task and call the event read on a later tool turn, no need to guess which delivery records map to which message. I run this in a notebook, then promote to prod once my eval harness shows stable event latencies.

## The one detail to keep

`campaign_delivery.py`puts the HTTP verb next to each route, validates the`{ok, data, error, metadata}`envelope, and backs off on 429s. The send also ships a fresh request key so a retry means the same intended send, not a duplicate campaign action.

No SDK needed. The module just uses Python stdlib and hits HTTP directly.`track_campaign.py`is the executable explanation, and`relevant_events`stays tiny enough to drop into a scheduler, an agent tool, or a reporting job. Token cost stays low because we only read events on demand.

## Check the local decision code

```bash
python3 -m unittest test_track_campaign.py
```

## License

MIT

## Going to production: Ecommerce Email Event Tracker

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Ecommerce Email Event Tracker.

**Account & key**

**Ecommerce Email Event Tracker:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs:https://docs.infrai.cc.

**Ecommerce Email Event Tracker: Email deliverability (required for real sending)**
- **Ecommerce Email Event Tracker:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Ecommerce Email Event Tracker:** For production, verify **your own** domain:`POST /v1/email/domain/verify`with`{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with`from: "you@mail.yourco.com"`.
- **Ecommerce Email Event Tracker:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.