# Muse (claude.ai web app) with the AWS Events MCP server

checked 2026-11-05 against [Anthropic's connector docs](https://claude.com/docs/claude-science/custom-connectors)
(not end-to-end tested here; confirming needs a registered Builder ID).

the Muse web app, desktop app, and mobile apps connect to remote MCP
servers as custom connectors. the Events server is remote HTTPS with
OAuth, so it fits: no localhost tunneling, because Anthropic's cloud —
not your machine — connects to it.

## add the connector

1. open settings, then connectors (customize, then connectors on some plans).
2. add a custom connector: name it `awsevents`, server URL
   `https://api.awsevents.com/mcp`.
3. advanced settings cover transport (Streamable HTTP) and OAuth client
   settings. for the shared public client, the client id is
   `7vmom55m1qstvq8i71ph127bfq` with scopes
   `openid email events/access`
   ([AWS docs](https://docs.aws.amazon.com/events/latest/devguide/mcp-server.html)).
4. sign in with your Builder ID in the browser when prompted.

limits, as of late 2026: custom connectors exist on Free (one connector),
Pro, Max, Team, and Enterprise. on Team and Enterprise an owner adds it
under organization settings and members enable it. Claude Desktop shares
the same connector list.

## confirm it works

ask Muse to list events. you should get `reinvent2026` back. then ask
for your schedule: favorites and reservations prove the sign-in carries
the `events/access` scope and your re:Invent registration.

caveats: the connector has no local-callback step, so headless machines
are not an issue here — but the Builder ID sign-in still happens in your
browser. write operations (reserve, favorite, personal time) run as you;
keep the per-session-result discipline from `docs/api-field-notes.md`:
a 200 never means every session succeeded, and `GetSchedule` confirms.
