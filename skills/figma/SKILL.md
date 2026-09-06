---
name: figma
description: Retrieve Figma design context, screenshots, assets, or setup guidance. Route production code implementation to figma-implement-design.
---

## Intent and applicability

Retrieve design context, screenshots and assets, or diagnose Figma access. For a
production implementation request, route once to `figma-implement-design`, which
owns code translation and visual validation; do not execute two competing flows.

## Inputs and local bindings

Resolve the exact supplied file/node/variant and existing connection. For setup
or debugging, read [references/figma-mcp-config.md](references/figma-mcp-config.md).
A link identifies the requested node; it is not authorization for client setup.

## Non-goals

Retrieval does not select production edits or connection installation. Necessary
metadata inspection and bounded retrieval recovery remain autonomous.

## Must not

Do not invent missing design context, expose credentials, or claim visual parity
from a retrieval alone. Do not register/authenticate/restart a client without the
required existing authority; continue independent preparation where possible.

## Interaction and authority

Reuse the user's node selection and valid connection/setup decisions. Ask only
for a materially ambiguous node or unresolved access/configuration action.

## Procedure

1. Fetch `get_design_context` for the selected node.
2. On oversized/truncated context, use `get_metadata`, then fetch needed nodes.
3. Fetch `get_screenshot` for the relevant variant when visual context is needed
   or the result is being handed to implementation.
4. Retrieve actual supplied assets. Pass context identity, screenshots, tokens,
   assets and coverage limits to the implementation skill when selected.

### Asset handling
- The Figma MCP Server provides an assets endpoint which can serve image and SVG assets.
- IMPORTANT: If the Figma MCP Server returns a localhost source for an image or an SVG, use that image or SVG source directly.
- IMPORTANT: DO NOT import/add new icon packages, all the assets should be in the Figma payload.
- IMPORTANT: do NOT use or create placeholders if a localhost source is provided.

### Link-based prompting
- The server is link-based: copy the Figma frame/layer link and give that URL to the MCP client when asking for implementation help.
- The client cannot browse the URL but extracts the node ID from the link; always ensure the link points to the exact node/variant you want.

## References
- `references/figma-mcp-config.md` — setup, verification, troubleshooting, and link-based usage reminders.
- `references/figma-tools-and-prompts.md` — tool catalog and prompt patterns for selecting frameworks/components and fetching metadata.

## Completion and evidence

Return the requested context/assets and their node identity, with failed or
unavailable coverage explicit. Retrieval success does not prove the implemented
UI's fidelity or behavior.
