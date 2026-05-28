<!--
Sync Impact Report
Version change: 1.0.0 -> 1.1.0
Modified principles:
- V. Operational Simplicity and Reversibility -> V. Operational Simplicity,
  Reversibility, and Clear Operator Communication
Added sections:
- None
Removed sections:
- None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md
- ✅ .specify/templates/spec-template.md
- ✅ .specify/templates/tasks-template.md
- ✅ .specify/templates/commands/*.md (no files present in this repo)
Follow-up TODOs:
- None
-->
# Naver Search Ops Constitution

## Core Principles

### I. Spec-Driven Delivery
Every material change MUST begin with a feature spec, implementation plan, and
task list that trace back to a concrete user or operator outcome. Work MUST be
organized into independently testable user-story slices with explicit
acceptance scenarios before implementation starts. Rationale: this repository
is a greenfield operational system; ambiguity at the planning layer will become
operational risk later.

### II. Verifiable Increments
Each user story MUST define verification evidence before implementation begins.
Deterministic or business-critical behavior MUST be covered by automated tests;
manual verification is acceptable only when automation is impractical and the
plan records the exact proof steps. A story is not complete until its stated
verification passes and the result is captured in the implementation record.
Rationale: the system affects weekly task assignment, click tracking, and admin
reporting, so regressions must be caught before rollout.

### III. Auditability by Default
Any feature that changes assignments, records tester actions, or exposes admin
reporting MUST define the audit events it produces, the fields captured, and
the operator-visible trail for investigating anomalies. Time-stamped records for
task allocation, search-trigger actions, and admin-visible mutations MUST be
preserved in a form that supports reconciliation. Rationale: the product's core
value depends on trustworthy attribution and history.

### IV. Least-Privilege Data Handling
The system MUST collect only the tester and operator data required to assign
work, attribute activity, and administer the program. Access to identifiable
tester data, exports, and administrative actions MUST be role-scoped; secrets
and credentials MUST never appear in source control, specs, or logs. Rationale:
the product handles operator workflows and tester identifiers, so privacy and
access boundaries must be designed in from the start.

### V. Operational Simplicity, Reversibility, and Clear Operator Communication
Designs MUST prefer the simplest deployable approach that satisfies the current
feature scope, and every stateful or data-shaping change MUST document a
rollback or recovery path. New infrastructure, background processes, or
cross-service dependencies require explicit justification in the plan's
Complexity Tracking section. All user-facing responses and repository-generated
planning artifacts for this project MUST be written in Korean unless the user
explicitly requests another language. Rationale: a small operational team needs
a system and delivery process that can be understood, changed, recovered, and
reviewed without translation ambiguity.

## Delivery Constraints

- Features MUST describe user roles, affected data entities, and failure modes
  in the specification before implementation begins.
- Features that create or modify persistent data MUST state retention,
  reconciliation, and rollback expectations in the plan.
- Features that expose admin analytics or exports MUST specify filters, access
  boundaries, and audit implications before implementation.
- External integrations, automation steps, and scheduled behavior MUST document
  configuration inputs, rate/usage assumptions, and operator override controls.

## Workflow & Quality Gates

- The plan's Constitution Check MUST confirm compliance with all five core
  principles before Phase 0 research is considered complete.
- Task breakdowns MUST include the work needed for verification, audit
  instrumentation, access control, and operational readiness whenever those
  concerns are in scope.
- Pull requests and review summaries MUST call out constitution-impacting
  changes explicitly, especially data model changes, logging changes, new admin
  capabilities, and rollback-sensitive operations.
- Specs, plans, tasks, review summaries, and direct user-facing status updates
  produced for this repository MUST be written in Korean unless the user
  explicitly asks for another language.
- Before release, the implementation record MUST identify what was verified,
  what remains manual, and what operator-facing follow-up is still required.

## Governance

This constitution supersedes conflicting local conventions for planning,
implementation, and review in this repository. Amendments MUST be proposed in a
dedicated change, explain the reason for the governance change, and include any
required template or workflow updates before ratification. Compliance review is
mandatory for every plan, task list, and implementation review; unresolved
constitution violations block approval until corrected or until the
constitution itself is formally amended. Versioning follows semantic rules for
the constitution itself: MAJOR for removed or materially redefined principles,
MINOR for new principles or materially expanded governance, and PATCH for
clarifications that do not change required behavior.

**Version**: 1.1.0 | **Ratified**: 2026-05-28 | **Last Amended**: 2026-05-28
