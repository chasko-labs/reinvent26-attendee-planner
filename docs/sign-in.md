# sign in: Builder ID for the Events API

everything that touches your schedule — and every MCP tool call —
runs as you, through Builder ID OAuth with PKCE. one sign-in covers
the cli, the MCP server, and the watcher cron.

## step zero: can this machine run the cli

the cli is stdlib-only: no pip install, no virtualenv. it needs
python 3.10 or newer:

```
python3 --version
# want: Python 3.10.x or newer
```

macs ship no python3: `brew install python` (or python.org), then
re-run the check. then confirm the cli itself loads and report your
sign-in state in one go:

```
cd cli
python3 -m reinvent26 status reinvent2026
```

do this before anything else, on any machine. it never prints secrets.

## how to tell if you are signed in

three answers, each naming the fix:

- `signed in: access token live until ...` — good for the hour shown.
  below it: `schedule readable: N reserved, M favorites` proves the
  sign-in carries your registration.
- `signed in: expired access token refreshed just now` — good; the
  30-day refresh did its job silently.
- `signed out: ...; run python3 -m reinvent26 login` — the refresh is
  dead (older than 30 days or revoked). the schedule line will read
  `schedule unreadable (401): sign in first`. sign in again.

manual check without the command: `stat ~/.config/reinvent26/tokens.json`
shows the last sign-in date. older than 30 days means the refresh is
dead — `status` will confirm it in one line.

## the login in plain english

Builder ID sign-in ends with your browser handing a code to a tiny
web server the cli runs on your own machine at
`http://127.0.0.1:8484/callback` (it tries 8484 through 8489 and
prints the one it got). so the machine that runs `login` must be the
machine whose browser approves it — or be connected to it by a tunnel:

```
ssh -L 8484:localhost:8484 YOUR-AIBOX-SSH-HOST
```

read it as: ssh to your box, and wire port 8484 on your Mac's
localhost to port 8484 on the box's localhost. the callback the box
listens for arrives through that wire. YOUR-AIBOX-SSH-HOST is
whatever you normally ssh to — the same name or address already in
your ssh config. `<aibox>` is a placeholder, never typed literally,
and ssh with no destination always prints usage.

## path 1: hotel laptop, everything local (Vegas)

no tunnel needed. the browser and the callback live on one machine:

```
cd ~/code/chasko-labs/reinvent26-planner/cli
python3 -m reinvent26 login
```

a browser tab opens (or the cli prints a URL — open it). sign in
with Builder ID, approve, back in the terminal:

```
python3 -m reinvent26 status reinvent2026
# signed in: access token live until ...
# schedule readable: N reserved, M favorites
```

tokens land in `~/.config/reinvent26/tokens.json` on that laptop.

## path 2: home powerdesktop does the work, hotel consumes it

this is bryan's setup. the desktop at home runs the watcher cron and
holds the tokens; the hotel laptop holds no credentials at all:

1. from the Mac on the home network, open the tunnel and sign in on
   the box (the login above, run over ssh). tokens stay on the box.
2. the box generates `docs/new-sessions/new-sessions-<date>.md`
   twice daily on its own.
3. at the hotel, read the report and paste its handoff block into
   Meta Muse (`docs/integrations/meta-muse.md`) for planning, or
   into laptop kiro-cli (`docs/integrations/kiro-cli.md`) for live
   seat changes. the report travels; the tokens never leave home.

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
