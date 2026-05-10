# Privacy and Retention Checklist

Use this before collecting telemetry from a highly interactive digital learning environment.

## Data Minimization

- Do we need raw text, audio, video, face, gaze, or sensor data for the claim?
- Can derived features answer the research question instead of raw media?
- Are free-text fields necessary, or can students select structured rationales?

## Identity and Linkage

- Are player IDs pseudonymous in the exported dataset?
- Is the roster mapping stored outside the public analysis folder?
- Can collaborators analyze the data without names, emails, or student IDs?

## Consent and Notice

- Does consent explain interaction traces and any multimodal capture?
- Are optional modalities, such as camera, audio, gaze, pose, hand/controller path, or biometrics, clearly separated from basic event logging?
- Does the participant know what will be retained and for how long?

## Security and Retention

- Where are raw logs stored?
- Who can access raw logs, media files, and ID mapping tables?
- What is the deletion or archive date?
- Can public examples be synthetic or heavily de-identified?

## Reporting

- Does the dashboard avoid diagnosing learners from telemetry alone?
- Are uncertainty and limitations visible?
- Are small-N results described as exploratory?
