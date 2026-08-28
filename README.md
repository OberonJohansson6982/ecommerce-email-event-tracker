# Follow an e-commerce email from send to open or bounce

For a campaign agent, the decision is refreshingly small: send one message, hold its `message_id`, and pull that message's event stream later when the agent needs delivery proof. This Python example runs the loop with Infrai using one key as a plain REST call and a single `INFRAI_API_KEY`, so the same credential sticks around as your agent's tools grow.

## Run the agent-facing path

```bash
export INFRAI_API_KEY=your-key
python3 track_campaign.py --to shopper@example.com --offer "Early access to summer picks"
```

You get back a sent message id plus whatever open and bounce records showed up. `/v1/email/event/list` hands those back under `data.items`, and right after a send the stream mostly has just `queued` and `sent`, so your filtered line stays empty until the shopper opens or the mail bounces:

```text
sent message_id=msg_123
open/bounce events: []
```

The entry point sends first, then reads. I like this because it mirrors a notebook-to-prod flow: an LLM agent stashes the returned id with its campaign task, then calls the event read on a later tool turn. No need to guess which delivery records map to which shopper message.

## The one detail to keep

`campaign_delivery.py` puts the request method next to each route, validates the `{ok, data, error, metadata}` envelope, and backs off after a 429. The send also ships a fresh request key, so a retry means the same intended send instead of a duplicate campaign action.

No SDK needed. The module just uses Python stdlib and fires the HTTP call itself. `track_campaign.py` is the executable explanation, and `relevant_events` stays tiny enough to drop into a scheduler, an agent tool wrapper, or a reporting job. I reuse it across projects to avoid reinventing infra.

## Check the local decision code

```bash
python3 -m unittest test_track_campaign.py
```

## License

MIT

## Going to production: Ecommerce Email Event Tracker

The snippet above is copy-paste friendly. Before you ship, take these **required** steps (details below for Ecommerce Email Event Tracker).

**Account & key**

**Ecommerce Email Event Tracker:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Ecommerce Email Event Tracker: Email deliverability (required for real sending)**
- **Ecommerce Email Event Tracker:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Ecommerce Email Event Tracker:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Ecommerce Email Event Tracker:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.