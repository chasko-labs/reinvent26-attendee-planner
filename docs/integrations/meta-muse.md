# Meta Muse with the AWS Events MCP server

Muse is Meta's AI assistant. it connects to outside tools through custom
connectors, which use the Model Context Protocol. there is no add-server
form: ask Muse in chat to build the connector and hand it the public
HTTPS URL. the Events server is public HTTPS with OAuth, so it qualifies.

## add the connector

1. open a Muse chat and ask it to connect a custom MCP connector, with
   the URL:
   `https://api.awsevents.com/mcp`
2. Muse writes the client on its own side, tests the tools, and saves
   the result as a reusable skill.
3. sign in with your Builder ID when prompted (scopes
   `openid email events/access`).

Muse runs in Meta's cloud, so it only reaches public servers — no
localhost tunneling needed on your side. your sign-in still happens in
your browser.

## confirm it works

ask Muse to list events (`reinvent2026` comes back), then ask for your
schedule: your favorites and reservations prove the sign-in carries the
registration. work from the handoff block at the bottom of
`docs/new-sessions/new-sessions-<date>.md` the same way
`docs/integrations/kiro-cli.md` describes.
