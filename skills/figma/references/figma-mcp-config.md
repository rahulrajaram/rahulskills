# Figma MCP config reference

Use an existing working Figma connection. A request to inspect or implement a design does not by itself authorize registering a server, changing client features or credential storage, authenticating an account, or restarting the client. Reuse authorization already given for those actions; ask only for any material action that remains unauthorized.

## Diagnose before changing configuration

- Distinguish a missing connection from an invalid node, file-access denial, authentication failure, or transient service error. Do not replace a working configuration because one request failed.
- Inspect only the relevant non-secret settings and the client's tool availability. Do not dump credential-bearing configuration or environment variables.
- If setup is needed, prepare the concrete server/configuration change and explain any login or restart it requires. Continue independent repository inspection or other authorized preparation while that boundary is unresolved; do not invent missing design context.
- After an authorized change, check tool availability and a relevant read call. A non-empty credential variable alone does not establish authentication or file access.

## Authorized setup options

Confirm the installed client's supported commands with `codex mcp add --help` and `codex mcp login --help`. For a selected OAuth setup, add the server only if it is missing, then authenticate as needed:

```bash
codex mcp add figma --url https://mcp.figma.com/mcp
codex mcp login figma
```

Do not change feature flags or force a restart from an old example. Follow the actual client's reload/login requirements; if a user action is still required, preserve the completed preparation and identify the remaining step.

For an existing or explicitly selected bearer-token setup, reference the environment variable rather than embedding its value in `~/.codex/config.toml`:

```toml
[mcp_servers.figma]
url = "https://mcp.figma.com/mcp"
bearer_token_env_var = "FIGMA_OAUTH_TOKEN"
```

Preserve existing required headers and organization settings; do not assume a region or overwrite another authentication method. Use the client's OAuth flow or the user's existing approved credential-provisioning method. Do not ask for a token in chat or put its value in a shell command, diagnostic output, or generated report. Changes to persistent credential storage are separate from checking the connection.

## Check credential presence without disclosure

For bearer-token configuration, run this in the environment that launches the client. The expansion returns a literal presence marker, never the token:

```bash
if [ "${FIGMA_OAUTH_TOKEN:+set}" = set ]; then
  printf '%s\n' 'FIGMA_OAUTH_TOKEN is set'
else
  printf '%s\n' 'FIGMA_OAUTH_TOKEN is missing'
fi
```

A variable set in an unrelated shell may not be available to the running client. Resolve that launch-environment difference through the approved setup path, without printing or copying the credential into the conversation.

## Usage reminders
- The server is link-based: copy the Figma frame or layer link, then ask the MCP client to implement that URL. The client will extract the node ID from the link (it does not browse the page).
- If output feels generic, restate the project-specific rules from the main skill and ensure you follow the required flow (get_design_context → get_metadata if needed → get_screenshot).
