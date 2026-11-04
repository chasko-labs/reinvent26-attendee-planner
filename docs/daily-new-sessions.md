# daily new sessions: watcher runbook

`python -m reinvent26 new-sessions` diffs the live catalog against the
cache, evaluates added sessions with the local model, and writes a dated
report plus a handoff prompt for kiro-cli with the Events MCP server.
read-only against the api: it never reserves, favorites, or writes
personal time. the handoff is the only thing that changes a schedule,
and a person pastes it.

## what it records

- added sessions since the last snapshot (by session id) and removed ones.
  "new" here means newly published or late-added sessions, including
  sessions whose details were held back until AWS announced them.
- live seat availability for each added session (`GetSession` is the only
  call that returns it), bounded by `--max-checks` (default 100).
- local-model evaluation: the added sessions go to the OpenAI-compatible
  endpoint (`--endpoint`, default `http://127.0.0.1:8181/v1`) with your
  tracked topics from `data/reinvent2026/map-config.json`. unknown codes
  are dropped against the added list. when the endpoint is down the
  report still runs on deterministic topic-tag order and says so.
- conflicts against your live schedule and opportunities that fit under
  the venue-gap rules.

## run it

```
cd cli
python3 -m reinvent26 new-sessions reinvent2026 --dry-run   # print, write nothing
python3 -m reinvent26 new-sessions reinvent2026             # write docs/new-sessions/<date>.md
```

first run with no cache records a baseline and reports everything as
added; the second run is the first real diff. an empty live catalog is
treated as an outage (exit 1, cache untouched), never as "all removed".

## cron on rocm-aibox (systemd, twice daily)

the watcher needs your stored token (`python -m reinvent26 login` once;
refresh lasts 30 days, so re-sign-in monthly or the run exits 2). the
local model endpoint is optional; without it the report falls back to
topic tags.

```
# ~/.config/systemd/user/reinvent26-new-sessions.service
[Unit]
Description=reinvent26 new-session watcher

[Service]
Type=oneshot
WorkingDirectory=%h/code/chasko-labs/reinvent26-planner/cli
ExecStart=/usr/bin/timeout 600 /usr/bin/python3 -m reinvent26 new-sessions reinvent2026
```

```
# ~/.config/systemd/user/reinvent26-new-sessions.timer
[Unit]
Description=reinvent26 new-session watcher twice daily

[Timer]
OnCalendar=*-*-* 07,19:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```
systemctl --user daemon-reload
systemctl --user enable --now reinvent26-new-sessions.timer
journalctl --user -u reinvent26-new-sessions -n 20
```

cron alternative:

```
0 7,19 * * * cd ~/code/chasko-labs/reinvent26-planner/cli && timeout 600 python3 -m reinvent26 new-sessions reinvent2026 >> ~/.cache/reinvent26/new-sessions.log 2>&1
```

read `docs/new-sessions/new-sessions-<date>.md`, then paste the handoff
block at the bottom into kiro-cli (setup: `docs/integrations/kiro-cli.md`).
kiro-cli makes the changes through the Events MCP server; the watcher
only ever suggests.
