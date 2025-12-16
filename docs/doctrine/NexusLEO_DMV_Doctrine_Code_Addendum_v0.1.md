# NexusLEO DMV Doctrine Code Addendum v0.1

**Document Type:** Doctrine-to-Code Addendum (Non-Authoritative)
**System:** NexusLEO
**Version:** v0.1
**Status:** Draft
**Last Updated:** 2025-12-16

## Doctrine → Code Intent
This addendum binds DMV procedural doctrine to NexusLEO implementation intent.
It constrains behavior so guidance remains neutral, documentation-first, and non-legal.

## Allowed AI Behaviors

### Procedural reminders
Allowed behavior includes neutral reminders framed as procedural considerations.
These reminders emphasize documentation quality and consistent organization.

### Documentation prompts
Allowed behavior includes prompts that request commonly documented fields, such as time, location, parties, and source attribution.
Prompts are framed as missing-information prompts rather than directives.

### Information completeness checks
Allowed behavior includes deterministic completeness checks based on existing case data.
Outputs may indicate that a commonly documented element appears absent from the current record.

## Forbidden AI Behaviors

### Prescriptive guidance
Forbidden behavior includes any prescriptive guidance that directs outcomes or action choices.

### Enforcement actions
Forbidden behavior includes guidance that selects or directs enforcement actions.

### Legal conclusions
Forbidden behavior includes legal conclusions, legal threshold language, and statutory interpretation.

## Mapping to Endpoint

### GET /cases/{case_id}/guidance (PR7)
This endpoint is constrained to deterministic procedural considerations derived from existing case data.
It emphasizes documentation completeness, consistent identifiers, and neutral organization.

## Enforcement Rule
If code conflicts with doctrine, doctrine prevails.

## Versioning Rule
Only bump doctrine version when scope or behavior changes.
