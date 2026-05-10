# Research Question Fit Audit Checklist

Use this before analysis, dashboard design, or AI-assisted modeling.

## 1. Name The Intended Claim

- What does the draft RQ ask for: describe, compare, associate, predict, sequence, explain, measure, evaluate, generalize, or integrate?
- What finding sentence would you like to write if the result works?
- Which words in that sentence create the strongest evidence burden: caused, improved, measured, explained, predicted, representative, or generalized?

## 2. Inspect The Data Shape

- What is one row: learner, attempt, event, message, session, artifact, class, school, or time window?
- Are IDs stable across files?
- Are observations nested inside learners, teams, classes, schools, tasks, or time?
- Are timestamps, turn numbers, event order, or pre/post timing available when the question implies process or change?
- Are missingness, exclusions, attrition, and impossible values visible?

## 3. Check Design Support

- Is there an intervention, comparison, baseline, assignment rule, or repeated observation?
- Was assignment randomized, matched, quasi-experimental, observational, or convenience-based?
- Does the outcome occur after the predictor/intervention?
- Could selection, maturation, history, testing, contamination, or attrition explain the pattern?

## 4. Check Measurement Support

- What construct is each variable supposed to represent?
- Is the variable directly observed, self-reported, coded, inferred, detected, or proxied?
- Are reliability, coder agreement, scoring rules, or validation evidence available?
- Would the same indicator mean the same thing in another task, platform, population, or language?

## 5. Match Method To Claim

- Does the analysis-ready table preserve the evidence needed by the RQ?
- Does the method answer the question verb, or only create an impressive output?
- Are covariates justified by design/theory rather than added after result shopping?
- For prediction, is there held-out validation and no leakage?
- For sequence/process, is event order preserved?
- For qualitative explanation, are excerpts, memos, and rival interpretations linked to claims?

## 6. Rewrite The RQ If Needed

- Current unsupported RQ:
- Nearest defensible RQ with current data:
- Safe finding sentence:
- Claims to avoid:
- Additional evidence needed for the stronger future claim:

## 7. Reviewer Readiness

- Can a reviewer see the chain from data shape to claim wording?
- Are limitations written as claim boundaries, not generic apologies?
- Are stronger claims explicitly marked as future design needs?
- Are citations/reporting standards used to support the warrant, not decorate the reference list?
