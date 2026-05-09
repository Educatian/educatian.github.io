# ECD Evidence Map Template for Educational Game Telemetry

## 1. Learning Claim

What do you want to say?

Example: Players used evidence to justify a cybersecurity decision.

## 2. Construct or Competency

What underlying capability is being inferred?

Example: Evidence-based reasoning.

## 3. Game Situation

Which task gives the player an opportunity to show it?

Example: A mystery board where players inspect artifacts and connect evidence to a resolution.

## 4. Observable Behaviors

What can be observed without guessing?

- Evidence inspected
- Evidence linked to claim
- Claim revised after new evidence
- Resolution submitted

## 5. Event Records Needed

Which telemetry events must exist?

- `evidence_inspected`
- `evidence_linked`
- `claim_revised`
- `resolution_submitted`

## 6. Derived Features

What will be calculated later?

- Number of relevant evidence items inspected before resolution
- Sequence position of first relevant evidence
- Number of claim revisions
- Evidence-to-claim coverage score

## 7. Safe Interpretation

What can be said conservatively?

Example: Players who inspected and connected relevant evidence before submission showed stronger evidence-use patterns in this game task.

## 8. Claims to Avoid

- The game proved reasoning ability.
- Clicks measured understanding directly.
- Students learned cybersecurity because they completed the case.
