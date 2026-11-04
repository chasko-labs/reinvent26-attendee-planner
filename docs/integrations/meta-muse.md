# Meta Muse with the AWS Events MCP server

Muse takes remote MCP servers as custom connectors. the Events
server is remote HTTPS, so add it by URL:

1. open a Muse chat, add a custom connector, paste
   `https://api.awsevents.com/mcp`.
2. client ID: `7vmom55m1qstvq8i71ph127bfq`, scopes
   `openid email events/access` (the shared public client from the
   AWS docs — no secret exists for it).

sign-in runs as Muse's secure OAuth flow and lands on a hosted
callback. AWS matches the callback in full and publishes no hosted
redirect for this server — sign-in listens on loopback ports
8484–8489 only. expect AWS to reject the hosted callback at the
sign-in step.

## the setup that works

authenticated work happens on a machine you own; Muse plans from
the output:

1. home powerdesktop holds the tokens and runs the watcher cron
   (`docs/sign-in.md` path 2, `docs/daily-new-sessions.md`).
2. it writes `docs/new-sessions/new-sessions-<date>.md` twice daily.
3. at the hotel, paste the report into Muse. it plans from real
   seats, conflicts, and launch signals with nothing to connect.
4. live seat changes still need a loopback-capable client on your
   laptop: paste the report's handoff block into kiro-cli
   (`docs/integrations/kiro-cli.md`) and it books through the
   Events MCP server right there.

verify the connector any time by asking Muse to list events:
`reinvent2026` comes back only when sign-in actually succeeded.
