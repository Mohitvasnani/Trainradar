# TrainRadar scale-up: architecture redesign

Status: draft, for discussion. Written before any code changes.

## Why the current architecture can't just be pointed at a bigger bounding box

The dissertation build is a **pull, single-process, in-memory** design:

- `services/state.py` loads one OSM rail graph (76k nodes, Liverpool–Leeds corridor) into a Python global at process start, once.
- Every `/api/trains` request fetches fresh data from the RTT REST API, does the leg-selection and interpolation work inline, and returns. Nothing is precomputed or persisted.
- The only "cache" is in-process dicts with TTLs (`services/cache.py`). Restarting the process throws it all away.
- There's one thing to run: `python server.py`, for as long as a terminal stays open on your laptop.

None of that survives contact with national scale, for three separate reasons, not one:

1. **RTT is pull, Network Rail Open Data is push.** TD/TM arrive continuously over a persistent STOMP connection. There's no "request" to make — something has to stay connected 24/7 and process a message stream. Flask's request/response model has nowhere to put that.
2. **The reference-data chain is new and three hops longer.** RTT already hands you a CRS code per calling point. TD gives you a *berth* code. Getting from a berth to a lat/lon is: `TD berth → SMART (berth → STANOX) → CORPUS (STANOX → TIPLOC/CRS) → NaPTAN (TIPLOC/CRS → lat/lon)`. That's a lookup pipeline that doesn't exist in the codebase at all yet.
3. **National OSM graph is a different object than a 76k-node corridor.** GB rail is denser and the Overpass round-trip is already "several minutes" for one corridor at `simplify=False`. Loading one graph into one process's memory and routing on it synchronously won't hold at this scale, independent of the feed question.

So this isn't "swap the HTTP client," it's a move from one process doing everything on demand, to a small pipeline of processes that each own one job and hand off through a shared store.

## Target shape

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Network Rail     │     │  Ingestion worker │     │                  │
│ Open Data        │ STOMP│  (long-running,  │     │   State store    │
│ (TD + TM feeds)  ├─────▶│  always-on)       ├────▶│  (shared, not    │
│                  │     │  - STOMP client   │ write│   in-process)    │
└─────────────────┘     │  - berth→lat/lon  │     │                  │
                         │    resolution      │     └────────┬─────────┘
┌─────────────────┐     │  - leg/estimate    │              │ read
│ CORPUS / SMART /  │     │    pipeline        │              │
│ NaPTAN (static,   ├────▶│    (existing       │     ┌────────▼─────────┐
│ periodic refresh) │     │    estimate.py     │     │   API process    │
└─────────────────┘     │    logic, reused)  │     │  (Flask/FastAPI,  │
                         └──────────────────┘     │   thin, read-only)│
                                                    └────────┬─────────┘
                                                             │ HTTP
                                                    ┌────────▼─────────┐
                                                    │     Frontend      │
                                                    └──────────────────┘
```

Three processes instead of one, each with one job:

### 1. Ingestion worker (new)

- Holds the STOMP connection to Network Rail Open Data. Durable subscription, heartbeats, exponential backoff on reconnect — all called out explicitly in Network Rail's own usage guidance, not optional extras.
- Subscribes to **TD** (berth-level, national, up to 6,000 msg/min) as the primary position signal. **TM** (up to 600 msg/min) is the better source for scheduled-vs-actual timing/lateness, which TD doesn't carry — worth bringing in alongside TD rather than instead of it, since the dissertation's error-evaluation work leaned on exactly that lateness data.
- Runs the berth → STANOX → TIPLOC/CRS → lat/lon resolution per incoming message, using locally cached CORPUS/SMART/NaPTAN snapshots (refreshed periodically, not per-message).
- Reuses the existing estimation pipeline (`route_leg`, `track_builder`, `estimate`) to turn resolved positions into map coordinates, but triggered by incoming feed events instead of by an incoming HTTP request.
- Writes current state out. Never serves HTTP. This is the only process that needs to be "always on" in the strict sense — if it drops, positions go stale; if the API process drops, it just means the map doesn't load for a minute.

### 2. State store (new — this is the actual architectural gap today)

There currently isn't one; `last_good` is a Python list living in one process's memory. Once ingestion and API are separate processes, something durable and concurrent-safe has to sit between them. Candidates, roughly in order of "least new infrastructure to learn":

- **SQLite with WAL mode** — one file, no server to run, but a single writer at a time; fine for current-position snapshots (ingestion is the only writer), thin for anything wanting concurrent writes later.
- **Postgres** — a real server process, handles concurrent access cleanly, natural fit if the dissertation's evaluation-style queries ("show me error by leg duration") ever want to run against live history instead of CSVs. More infra to run.
- **Redis** — built for exactly "one process writes current state fast, many processes read it fast," nothing to query with SQL. Weakest fit if history/analytics matters later.

This is a genuine open decision, not something to default silently — flagged below.

### 3. API process (reshaped, not new)

- Flask (or FastAPI, if moving anyway) keeps the same endpoint shapes (`/api/trains`, `/api/journey/<uid>/<date>`, etc.) so the frontend barely notices the change.
- The difference: handlers become reads against the state store, not RTT calls plus inline computation. `/api/trains` goes from "make a live API call and compute" to "read the last row ingestion wrote." This is also what removes the RTT rate-limit ceiling from the serving path entirely — the API never calls RTT or Network Rail directly.
- Can scale horizontally (multiple instances behind a load balancer) precisely because it no longer holds any unique in-memory state — that was impossible in the current design, where the graph and `last_good` live in one process.

## The national-graph question, separately from the feed question

Even without touching the feed, "Liverpool–Leeds corridor" to "all of GB" is its own scaling problem:

- Re-running the current `osm_graph.py` Overpass query at GB scale will be slow and may hit Overpall's own usage limits; it's worth checking whether Network Rail or ORR publish a maintained national rail geometry layer directly, rather than re-deriving one from OSM each time.
- `simplify=False, retain_all=True` was a deliberate, documented choice for correctness at corridor scale (keeps disconnected fragments visible rather than silently wrong). At national scale, decide once whether that policy still holds everywhere or needs per-region exceptions, rather than rediscovering it as a bug later.
- Loading the whole national graph into every process that touches it (today: one process, one load) stops making sense once there's an ingestion worker and a scalable API tier. Worth deciding whether the graph lives in the state store too (so it's loaded once and read by whichever process needs it) or stays a per-process load from a cached file.

## Deployment, which the current design never had to think about

"Two terminals on a laptop" assumed a human was there to start it and nothing had to survive being closed. An always-on STOMP connection needs:

- A host that's actually always on — a small VPS, a cloud free-tier VM, or a home machine (e.g. something always-on you already run) left running, as opposed to your dev laptop.
- The ingestion worker running as a managed process (systemd unit, Docker container with a restart policy) so a crash reconnects instead of silently going stale.
- The API process can live on the same host or be deployed separately/scaled independently, since it holds no state of its own anymore.

## Open decisions — these are yours to make, not mine to default

1. **State store technology.** SQLite / Postgres / Redis, per the trade-offs above.
2. **TD only, or TD + TM?** TD alone gives national position coverage; TM adds the lateness/timing data the dissertation's evaluation relied on. Leaning TD+TM, but it's more ingestion complexity for a benefit you may or may not want to carry into v2.
3. **Hosting target for the always-on worker.** VPS, cloud free tier, or a home machine.
4. **Geographic rollout.** All of GB in one step, or stage it (e.g. corridor → one region → national) so each layer of the redesign gets proven before the next.
5. **Does RTT stay in the picture at all** (e.g. as a cross-check or a gap-filler), or does Network Rail Open Data fully replace it?

## Suggested first milestone

Smallest slice that proves the new shape end-to-end without committing to the open decisions above: a standalone ingestion script that holds a STOMP connection, subscribes to TD for the *existing* corridor only, resolves one berth to a lat/lon using a hand-fetched CORPUS/SMART snapshot, and prints it. No state store, no API changes yet — just proof that the push side of this works before any infrastructure is built around it.
