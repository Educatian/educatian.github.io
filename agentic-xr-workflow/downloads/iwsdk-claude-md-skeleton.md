# IWSDK Project — CLAUDE.md Skeleton

> Drop this at the root of a new IWSDK project. Edit the project-name and
> module sections. The pitfall list and performance budget are stack-level
> facts; do not edit those without reason.

## Project: <NAME>

One paragraph: what this project is, who it is for, what it is NOT.

Anti-scope: list 3–5 things explicitly out of scope. Update when scope shifts.

## Stack

- Framework: `@iwsdk/core` 0.3.x
- ECS: `elics` (via IWSDK)
- 3D: `super-three` (Meta-maintained Three.js fork; bundled with IWSDK)
- Spatial UI: `@pmndrs/uikit` + UIKitML
- Manipulation: `@pmndrs/handle` + `@pmndrs/pointer-events`
- Reactivity: `@preact/signals-core`
- Build: Vite 7 + `@iwsdk/vite-plugin-dev`
- Telemetry: IndexedDB + NDJSON export

## Performance budget

- VR targets 72–90 FPS = 11–14 ms per frame.
- No object allocation in `update()`.
- Allocate Vector3 / Quaternion as class properties in `init()`; reuse.
- For hot reads/writes, use `entity.getVectorView(Component, 'field')` to
  get a TypedArray slice — zero allocations.

## Pitfalls (top causes of bugs)

1. **`locomotion: true` without `LocomotionEnvironment`** → player falls
   through the floor. Add `LocomotionEnvironment` to the floor entity OR use
   physics colliders.
2. **Importing Three from `'three'`** → duplicate Three.js instances and
   subtle bugs. ALWAYS `import { Vector3, Mesh } from '@iwsdk/core'`.
3. **`scene.add(mesh)`** → bypasses ECS, no Transform component, no level
   lifecycle. Use `world.createTransformEntity(mesh, parent)`.
4. **Manual `Raycaster`** → no BVH acceleration, doesn't work in XR. Add
   `Interactable` component; query `Hovered` / `Pressed` from a system.
5. **Polling `entity.hasComponent()` in `update()`** → use
   `queries.x.subscribe('qualify', ...)` once instead.
6. **`signal.value` in `update()` loops** → adds subscription overhead per
   frame. Use `signal.peek()` for hot-path reads.
7. **Raw `GLTFLoader`** → bypasses DRACO/KTX2 setup, no caching. Declare in
   `AssetManifest` → `AssetManager.getGLTF('id')`.
8. **Environment components on arbitrary entities** → silently ignored.
   Must go on `world.activeLevel.value`. After property change, set
   `_needsUpdate: true`.
9. **`entity.destroy()` for GPU objects** → leaks GPU memory. Use
   `entity.dispose()` for objects with geometry / material / texture.
10. **`ScreenSpace` with numbers** → expects CSS strings:
    `{ width: '400px', top: '20px' }`.
11. **No native multiplayer.** Collaborative experiences require custom
    networking (Colyseus + LiveKit is one valid combination).

## Sub-skills

- `/iwsdk-planner` — feature planning + best practices
- `/iwsdk-grab` — One/Two-hand grab interactions
- `/iwsdk-ray` — DistanceGrabbable + Interactable
- `/iwsdk-ui` — UIKitML panels + ScreenSpace
- `/iwsdk-debug` — frame-by-frame ECS pause / step / snapshot / diff
- `/iwsdk-physics` — PhysicsBody + PhysicsShape

## Testing workflow

1. `npx tsc --noEmit` — type check first.
2. `mcp__iwsdk-dev-mcp__xr_get_session_status` — do not start another dev
   server if one is already running.
3. If not connected: `npm run dev`.
4. Open `https://localhost:8081/`.
5. `xr_accept_session` to enter XR.
6. Test interactions with controller / hand MCP tools.

## Quest-on-network testing

Quest browser → `https://<dev-pc-lan-ip>:8081/` → accept self-signed cert →
"Enter VR". If LAN is blocked (corporate Wi-Fi, client isolation), use
`chrome://inspect/#devices` USB port-forwarding.

## Modules / sections

[Project-specific. Document each module / scene with its scope, components,
and telemetry contract.]
