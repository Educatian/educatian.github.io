# First-Prompt Templates — Agentic XR

> Open every working session with one of these. They take 10 seconds and save
> half-sessions wasted prompting around a broken MCP tool.

## 1. Generic tool-availability check

```
What custom tools do you have available? Group by MCP server.
```

The agent enumerates registered tools. Read it once; if a tool you expect is
missing, fix the MCP before any other action.

## 2. Unity / Meta MCP check

```
Confirm the Meta MCP Extensions are loaded. List the camera-rig,
interaction-rig, grabbable, and XR simulator tools you can call.
```

Looking for, at minimum:

- `create_camera_rig`
- `open_xr_simulator`
- `create_interaction_rig`
- `add_grabbable`

If any are missing, restart the Meta MCP server before continuing.

## 3. IWSDK / IWER session check

```
Call mcp__iwsdk-dev-mcp__xr_get_session_status and report the result.
```

If it returns a successful connection, the dev server is already running —
do not start another. If it errors, restart with `npm run dev` and retry
before any other action.

## 4. HZDB device check (when working with a connected Quest)

```
Call mcp__hzdb__device_list and mcp__hzdb__device_battery. Confirm the
Quest is connected and not thermally throttled.
```

A throttled or low-battery Quest will give you frame drops that look like
code bugs. Check this first when "the same code" runs at 90 FPS in the
emulator and 30 FPS on device.

## 5. Domain-MCP check (IWSDK)

```
Call mcp__iwsdk-rag-local__list_ecs_components and list_ecs_systems. Confirm
the IWSDK-RAG MCP is indexing the local node_modules.
```

If the lists are empty or stale, the MCP is pointing at an old package
version — re-run its indexer.

## 6. Plan-file context attach

After tool checks, attach the relevant plan files BEFORE the first build
prompt:

```
Read these files into context for the rest of this session:
- docs/pedagogy-charter.md
- docs/mvp-scope.md
- CLAUDE.md
- docs/plans/<current-feature>.md

Confirm each is loaded by summarizing it in one sentence.
```

Compaction will eventually drop them; re-attach when responses start drifting.
