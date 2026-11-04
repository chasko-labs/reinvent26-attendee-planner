# reinvent26-attendee-planner

python cli for re:invent 2026 session discovery, planning, and seat booking via the public Events API.

## install

```bash
pip install -e .
```

## sign in

```bash
python -m reinvent26 login
```

opens a browser for Builder ID sign-in (PKCE s256, loopback callback). tokens are stored in the OS keychain or `~/.config/reinvent26/tokens.json`.

## quick start

```bash
# list events
python -m reinvent26 events

# pull the full catalog, cached
python -m reinvent26 sessions reinvent2026

# rank by topic keywords
python -m reinvent26 shortlist reinvent2026 --topics agents,mcp --level 3

# show schedule with clashes
python -m reinvent26 schedule reinvent2026

# list free windows
python -m reinvent26 slots reinvent2026 --window 2026-12-01T13:00:00,2026-12-01T16:00:00

# book open seats into free windows
python -m reinvent26 fill --dry-run   # preview
python -m reinvent26 fill             # book
```

## commands

| command              | description                                               |
| -------------------- | --------------------------------------------------------- |
| `login`              | sign in with Builder ID (PKCE, loopback callback)         |
| `events`             | list current/upcoming events                              |
| `sessions`           | list catalog pages until no nextToken                     |
| `shortlist`          | rank sessions by topic keywords                           |
| `schedule`           | show schedule plus double bookings                        |
| `slots`              | list sessions fitting free windows with no clash          |
| `favorite`           | favorite up to 10 session ids per call                    |
| `block`              | create a personal-time block                              |
| `reblock`            | replace every field of a personal-time block              |
| `unblock`            | delete a personal-time block                              |
| `remove-favorite`    | remove one favorite                                       |
| `cancel-reservation` | cancel one reservation                                    |
| `stack-pick`         | stack-aware shortlist from live resources                 |
| `rank`               | rank cached catalog via local model                       |
| `ingest`             | load curated sessions into cache                          |
| `reserve`            | reserve seats                                             |
| `fill`               | book open seats into free windows of the live schedule    |
| `interest`           | write full-but-interesting page with presenters to follow |
| `map`                | build event map and launch ledger from catalog            |

## events mcp

the same api is available as the aws events mcp server at
`https://api.awsevents.com/mcp` (streamable http) for ai assistants and
agents. we do not ship our own mcp server; the cli above is the scriptable
interface and the mcp server is the interactive one. both follow the rules
in [skills/awsevents-muse/SKILL.md](skills/awsevents-muse/SKILL.md).

getting up and running:

1. sign in with your Builder ID. the oauth flow uses pkce with a loopback
   callback, so sign-in lands on `127.0.0.1:8484` on your own machine.
   headless host: forward the port from a machine with a browser first
   (`ssh -L 8484:localhost:8484 <host>`), then `python -m reinvent26 login`
   on the host. tokens live 60 minutes (access) and 30 days (refresh).
2. every mcp tool call needs sign-in, including catalog reads. that differs
   from rest, where public `ListEvents` needs no token.
3. walk the catalog the cheap way: `ListSessions` with
   `includeAbstracts=false`, follow `nextToken` until absent (a short page
   is not the last page), shortlist locally, then `GetSession` for
   abstracts and `seatAvailability` on the shortlist only.
4. favorites record interest, they do not reserve seats. reserve 1-10 ids
   per call. http 200 on a batch never means every session succeeded:
   inspect each per-session result, then confirm with `GetSchedule`.
5. on an unknown write outcome (timeout, 500, 503) never blind-resend.
   read the schedule, compare with intent, submit only what remains.
   404 on cancel or remove means already absent: complete.

full call order and live state: [docs/mcp-approach.md](docs/mcp-approach.md).
field notes and enums: [docs/api-field-notes.md](docs/api-field-notes.md).

## architecture

```
cli/reinvent26/
  __main__.py     # entry point
  cli.py          # argparse scaffolding, 18 subcommands
  api.py          # Events API client (stdlib only)
  auth.py         # Builder ID OAuth with PKCE, keychain/file storage
  cache.py        # .cache/<eventId>/ caching layer
  mapper.py       # topic tagging, venue travel gaps, exclusion rules
  rank.py         # session ranking by format, topic, duration
  schedule.py     # schedule normalization, clash detection
  seats.py        # seat availability sweeping
  fill.py         # book open seats into free windows
  interest.py     # full-but-interesting page generator
  inventory.py    # catalog dump to json for debugging
  seeds.py        # re:invent 2026 topic/venue defaults
  seeds.json      # curated session count targets
data/reinvent2026/
  *.json          # curated session lists by lens
  map-config.json # venue gaps, format weights, topic weights, exclusions
demo/
  demo_public.py           # public api demo
  sessions-sample.json     # sample ListSessions response
  schedule-sample.json     # sample GetSchedule response
docs/
  api-field-notes.md       # api calls, enums, lessons learned
  data-schema.md           # session schema and ingest layout
  event-map.md             # venue map with travel times
  launch-ledger.md         # session launch order and notes
  mcp-approach.md          # mcp vs cli sign-in patterns
  local-models.md          # local model setup for rank command
  samples/                 # api response shapes
tests/
  *_test.py                # pytest unit tests
skills/
  awsevents-muse/
    SKILL.md               # MCP skill definition
rust/
  catalog-filter/          # optional rust filter for fast catalog scan
```

## data files

curated session lists live in `data/reinvent2026/*.json`. each file groups sessions by interest lens. the schema is documented in `docs/data-schema.md`.

## tests

```bash
python -m pytest -q
```

## contributing gate

enable the pre-push hook once per clone:

```bash
git config core.hooksPath .githooks
```

pre-push runs secret-shape scan, compile, pytest, and the offline demo. all must pass before pushing.

## docs

- [docs/competition-ledger.md](docs/competition-ledger.md) — rival hackathon entries, steal-or-skip verdicts, ranked gaps
- [docs/hallway-windows.md](docs/hallway-windows.md) — breakfast, lunch, dinner, and morning/midday/evening meetup slots
- [docs/mcp-approach.md](docs/mcp-approach.md) — mcp vs cli sign-in patterns and live schedule state
- [docs/event-map.md](docs/event-map.md) — venue map with travel times
- [docs/launch-ledger.md](docs/launch-ledger.md) — sessions signaling new launches
- [docs/daily-fill.md](docs/daily-fill.md) — seat-filling runbook
- [docs/api-field-notes.md](docs/api-field-notes.md) — api calls, enums, lessons learned

## license

MIT
