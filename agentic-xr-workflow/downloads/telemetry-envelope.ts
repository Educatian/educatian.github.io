// telemetry-envelope.ts
// Public-safe XR telemetry event envelope.
// Adapt event_type strings and payload fields to your project; keep the
// envelope shape stable so analysis pipelines don't break across studies.

export interface Pose {
  pos: [number, number, number];          // world position (m)
  rot: [number, number, number, number];  // quaternion [x, y, z, w]
}

export interface TelemetryEvent {
  // -------- envelope (every event has these) --------
  event_id: string;          // UUID v7 — time-ordered, sortable
  session_id: string;        // UUID per VR session (random per session)
  participant_id: string;    // anonymized; mapping kept outside telemetry
  room_id?: string;          // collaborative-mode only
  event_type: string;        // see catalog below
  timestamp_ms: number;      // client wall-clock (ms since epoch)
  frame_time_ms: number;     // ms since session start (monotonic)

  // -------- spatial context (optional) --------
  head_pose?: Pose;
  hand_l_pose?: Pose;
  hand_r_pose?: Pose;

  // -------- event-specific payload --------
  payload: Record<string, unknown>;
}

// ---------- example event catalog ----------
// Project-specific; this is the catalog Virtual Makerspace uses for its
// breadboard module. Replace with your own.

export type EventType =
  | "session_start"
  | "session_end"
  | "grab_start"
  | "grab_end"
  | "socket_connect"
  | "socket_disconnect"
  | "circuit_state_change"
  | "circuit_closed_success"
  | "gaze_dwell"
  | "step_advance"
  | "ui_interaction"
  | "error_recovery";

// Helper: emit through your project's TelemetrySystem (which buffers to
// IndexedDB or streams to a server depending on phase).
export function buildEvent(
  type: EventType,
  payload: Record<string, unknown>,
  context: {
    sessionId: string;
    participantId: string;
    sessionStartMs: number;
    roomId?: string;
    headPose?: Pose;
    handLPose?: Pose;
    handRPose?: Pose;
  }
): TelemetryEvent {
  return {
    event_id: crypto.randomUUID(),         // upgrade to UUID v7 in prod
    session_id: context.sessionId,
    participant_id: context.participantId,
    room_id: context.roomId,
    event_type: type,
    timestamp_ms: Date.now(),
    frame_time_ms: performance.now() - context.sessionStartMs,
    head_pose: context.headPose,
    hand_l_pose: context.handLPose,
    hand_r_pose: context.handRPose,
    payload,
  };
}

// ---------- export shape ----------
// One event per line, NDJSON. Gzip at session_end if size warrants.
//
//   {"event_id":"...","session_id":"...","event_type":"grab_start",...}
//   {"event_id":"...","session_id":"...","event_type":"socket_connect",...}
//   ...
//
// Anonymization: participant_id is a random per-session UUID by default.
// Mapping to real identifiers (if any) is kept in an encrypted lookup
// owned by the researcher, never in telemetry files.
