# ECS Debug Cheatsheet — IWER

> Frame-by-frame debugging vocabulary for IWSDK projects. Use these when a
> bug happens in 11–14 ms and reading the console after the fact gives you
> nothing useful.

## Pre-flight

```
mcp__iwsdk-dev-mcp__xr_get_session_status
```

Confirms IWER is connected. If not, start `npm run dev` and retry.

## Pause / step / resume

```
ecs_pause                 # freeze ECS updates (renderer keeps running)
ecs_step count=1          # advance one frame
ecs_step count=5 delta=16 # advance 5 frames at fixed 16 ms each
ecs_resume                # back to real-time
```

Renderer keeps painting while ECS is paused, so you can move your head and
look at the frozen state from different angles.

## Snapshot / diff

```
ecs_snapshot label="before"
# trigger the action you want to inspect
ecs_snapshot label="after"
ecs_diff from="before" to="after"
```

Diff reports field-level changes per entity per component. Up to 2 snapshots
held at a time — capture-trigger-capture-diff is the standard cycle.

## Find entities

```
ecs_list_components                        # what components exist
ecs_list_systems                           # what systems exist
ecs_find_entities components=["Snappable"] # entities with a component
ecs_find_entities namePattern="^led_"      # entities by name regex
ecs_query_entity index=N                   # read all fields of entity N
```

The entity index is stable for the life of the entity; use it for repeated
queries.

## Isolate a system

```
ecs_list_systems
ecs_toggle_system name="CircuitEvalSystem" enabled=false
# reproduce the bug — does it still happen?
ecs_toggle_system name="CircuitEvalSystem" enabled=true
```

Bisect by toggling suspect systems one at a time.

## Combine with scene introspection

```
scene_get_hierarchy
scene_get_object_transform name="led_red"
```

Object UUIDs and entity indices map back to each other; useful when the
visual ground truth disagrees with the ECS state.

## Combine with screenshots

```
browser_screenshot
```

Pair with snapshots: `screenshot → snapshot → step → screenshot → snapshot`
gives you a per-frame visual + state record.

## Set a component field on a live entity

```
ecs_set_component index=42 component="Transform" field="position" value=[0,1,-1]
```

For verifying that the bug is in the system, not the component value.

## Frame-by-frame physics debug template

```
1. ecs_pause
2. xr_set_transform device="rightHand" pos=[...] rot=[...]
3. ecs_snapshot label="before"
4. xr_set_select_value hand="right" value=1.0    # press trigger
5. ecs_step count=1
6. ecs_snapshot label="after"
7. ecs_diff from="before" to="after"
8. browser_screenshot
9. (read result; iterate)
10. ecs_resume
```

This is the standard recipe for "why did the snap fire (or not fire) on
this frame" type bugs.
