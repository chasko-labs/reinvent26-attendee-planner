# sign in: Builder ID for the Events API

everything that touches your schedule — and every MCP tool call —
runs as you, through Builder ID OAuth with PKCE. one sign-in covers
the cli, the MCP server, and the watcher cron.

## how to tell if you are signed in

```
cd cli
python3 -m reinvent26 status reinvent2026
```

three answers, each naming the fix:

- `signed in: access token live until ...` — good for the hour shown.
  below it: `schedule readable: N reserved, M favorites` proves the
  sign-in carries your registration.
- `signed in: expired access token refreshed just now` — good; the
  30-day refresh did its job silently.
- `signed out: ...; run python -m reinvent26 login` — the refresh is
  dead (older than 30 days or revoked). the schedule line will read
  `schedule unreadable (401): sign in first`. sign in again.

manual check without the command: `stat ~/.config/reinvent26/tokens.json`
shows the last sign-in date. older than 30 days means the refresh is
dead — `status` will confirm it in one line.

## sign in from your Mac (do this once)

the callback lands on the machine that runs `login`, so run it on the
box and approve in your Mac browser:

```
ssh -L 8484:localhost:8484 <aibox>
cd ~/code/chasko-labs/reinvent26-planner/cli
python3 -m reinvent26 login
```

copy the printed URL into your Mac browser, sign in with Builder ID,
approve. back in the terminal:

```
python3 -m reinvent26 status reinvent2026
# signed in: access token live until ...
# schedule readable: N reserved, M favorites
exit
```

tokens land in `~/.config/reinvent26/tokens.json` on the box
(access: 60 minutes, refresh: 30 days). the login tries ports
8484 through 8489 and prints the one it got, so if 8484 is busy
forward the printed port instead.

## lifetimes

| token   | lasts   | renews                   |
| ------- | ------- | ------------------------ |
| access  | 60 min  | silently, on any command |
| refresh | 30 days | never — sign in again    |

when a command fails with 401 it already tried one silent refresh;
a second 401 means the refresh is dead, not that you should retry.

## what the errors mean

- `401 sign in first` — no usable token. `status`, then `login`.
- `403` — signed in fine, but this Builder ID is not registered for
  the event. signing in again changes nothing; register on the
  re:Invent site.
- `409` — the operation is closed on the API side right now, not a
  bad request. retry later.
- `429` — quota spent; the cli already honored one Retry-After.
  wait before retrying.
