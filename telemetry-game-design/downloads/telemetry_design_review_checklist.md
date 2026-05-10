# Telemetry Design Review Checklist

Use this before the event logger is implemented or before the schema is frozen.

## 1. Claim

- What sentence do we want to be able to say after the study?
- Is the claim bounded to a specific task, behavior, or game situation?
- Which broad claims are explicitly off limits?

Avoid claims such as: "The player learned cybersecurity" or "The player was motivated."

## 2. Opportunity

- Does the mission give players a real chance to show the target behavior?
- Can the mission be completed without producing the intended evidence?
- Are hints, failures, retries, and revisions part of the opportunity structure?

## 3. Observable Behavior

- What can be observed without guessing?
- Which event names describe actions rather than interpretations?
- Are the event names controlled in an event dictionary?

Prefer `evidence_linked` over `reasoned_well`.

## 4. Game State

- Is `pre_state` logged?
- Is `post_state` logged?
- Are available actions, support availability, failure states, mission state, and version stored?

## 5. Interpretation

- What does each signal support?
- What does each signal not support?
- What additional evidence would be needed for a stronger claim?

## 6. Privacy and Retention

- Does each field have a purpose?
- Does each field have a privacy tier?
- Is raw text, audio, video, face, gaze, or biometric data truly necessary?
- Are retention and export rules clear before collection?

## 7. Final Pass

- Can a collaborator reconstruct the gameplay context from the log?
- Can a reviewer see the evidence chain from claim to event?
- Can the team explain why every sensitive field is necessary?
