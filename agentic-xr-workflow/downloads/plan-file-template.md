# Plan File Template — Agentic XR

> Use this skeleton when you need to build a complex multi-component artifact
> (a hoop, a control panel, a scene, a level) and want the LLM to produce it
> in one consistent pass. Iterate the file with the model in a quick session
> first; in the build prompt say "implement this from the file".

## Goal

One sentence: what the artifact is and what it must do.

Example (from Dilmer demo):
> A regulation-style basketball hoop with a backboard, mounting bracket, rim,
> and net, sized for a Quest player at standing height, that registers
> scoring when a ball passes through the rim from above.

## Visual / spatial spec

- Origin: where the artifact's transform anchors.
- Axes: which way is forward / up.
- Dimensions: real-world scale (meters).
- Materials / colors: per-part (rim color, backboard transparency, etc.).
- Reference image: link or attach (the model can consume images now).

## Components / parts (per-part spec)

For each part:

- Name (in code: PascalCase; in scene: kebab-case).
- Mesh source: prefab path, GLB asset, or "primitive — describe shape".
- Transform: position relative to parent, rotation, scale.
- Components / scripts: which ECS components or MonoBehaviours attach.
- Constraints: hinges, attachments, physics flags.
- Telemetry events emitted (if applicable; see telemetry-envelope.ts).

## Behaviour

- Trigger conditions (when does X happen).
- State transitions (state-machine-style if non-trivial).
- Outputs (sound, particle, haptic, telemetry event).

## Test cases

- Happy path: what success looks like.
- Edge cases: what should NOT trigger the success condition.
- Performance budget: max frame cost (ms), max alloc per update().

## Out of scope (anti-goals)

What the artifact explicitly does NOT do. This is as load-bearing as the goal —
it stops the agent from "helpfully" adding things you don't want.

## Open questions

Decisions deferred. The agent will not invent answers if you list these
explicitly; it will ask or skip the relevant code.
