# Microsoft Copilot with the AWS Events MCP server

checked 2026-11-05. the honest summary first: the consumer Copilot app
(copilot.microsoft.com, Windows app, phone app) cannot add a custom MCP
server as of October 2026 — it connects to a fixed list (Outlook, OneDrive,
Gmail) and nothing else. the routes below are the ones that can reach
the Events server.

## route 1: Copilot Studio agent (maker route)

[Copilot Studio supports MCP servers](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent)
as agent actions through the connector infrastructure:

1. in Copilot Studio, open your agent, select add an action, and search
   for your MCP server (or build a
   [custom connector in Power Apps](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent)
   pointing at `https://api.awsevents.com/mcp` with OAuth).
2. sign in with Builder ID when the connector prompts; requested scopes
   are `openid email events/access`.
3. test with list events, then your schedule, before any reserve or
   favorite action.

this needs a Copilot Studio maker license and suits a team agent better
than a personal planner.

## route 2: GitHub Copilot in VS Code (developer route)

GitHub Copilot (Microsoft's programmer assistant, distinct from the
consumer app) speaks MCP from VS Code's MCP support. add the Events
server to your VS Code MCP config as a remote HTTP server at
`https://api.awsevents.com/mcp`, then run Copilot Chat against it and
sign in with Builder ID on first call. check the current VS Code MCP
docs for the exact config shape — it moves faster than this page.

## route 3: Microsoft 365 admin (org route)

Microsoft 365 Copilot supports admin-registered
[custom federated connectors](https://learn.microsoft.com/en-us/microsoft-365/copilot/connectors/set-up-custom-federated-connectors)
backed by an MCP server. this is an administrator operation (Global or
AI admin role), not a personal setup; the base URL is the same
`https://api.awsevents.com/mcp`.

## what not to try

the consumer Copilot chat box: no custom connections exist there, so the
Events server cannot be added. if that changes, it will show up as a
connectors or integrations list in the app settings.
