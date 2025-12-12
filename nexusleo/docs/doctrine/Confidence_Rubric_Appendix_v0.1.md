# NexusLEO Confidence Rubric Appendix (v0.1)

**Status:** Authoritative  
**Applies to:** All NexusLEO analytical outputs  
**Effective:** v0.1  
**Last Updated:** 2025-03-XX  

---

## 1. Purpose and Scope

This appendix defines the standardized **confidence assessment rubric** used by the NexusLEO platform.

The purpose of the rubric is to:
- Communicate analytical strength **without asserting truth**
- Enable supervisory, prosecutorial, and judicial review
- Ensure consistency across cases, officers, analysts, and time
- Provide a defensible explanation of *why* a confidence level was assigned

This rubric applies **only to analytical claims generated or organized by NexusLEO**.  
It does **not** assess guilt, intent, legality, or probable cause.

---

## 2. What “Confidence” Means in NexusLEO

In NexusLEO, **confidence is not correctness**.

Confidence expresses:
> *The degree to which a claim is supported by available evidence under a transparent, repeatable analytical method.*

Confidence does **not** mean:
- That the claim is true
- That the evidence is admissible
- That no contrary evidence exists
- That further investigation is unnecessary

---

## 3. Confidence Levels (Standardized)

NexusLEO uses **three confidence levels**, aligned to analytical best practices and compatible with standards such as ICD-203.

### 3.1 HIGH Confidence (🟢 Green)

**Definition:**
A claim is supported by **multiple independent sources or observations**, with no material contradiction identified at the time of assessment.

**Typical characteristics:**
- Evidence originates from **two or more independent sources**
- Sources are not derived from each other
- Consistent descriptions across sources
- No unresolved internal contradiction

**Examples:**
- Two separate interviewees independently describe the same meeting
- Interview + body-worn camera corroborate the same location and time
- Surveillance footage aligns with a documented statement

**What HIGH does *not* mean:**
- That the claim is proven
- That the claim is beyond challenge
- That the claim alone supports enforcement action

---

### 3.2 MODERATE Confidence (🟡 Yellow)

**Definition:**
A claim is supported by **a single source or observation**, or by multiple sources that are not fully independent.

**Typical characteristics:**
- One interview, report, or document
- Multiple mentions trace back to a single origin
- Evidence is clear but uncorroborated
- No known contradiction, but corroboration is limited

**Examples:**
- One witness describes a meeting or relationship
- A single report references a specific location
- An interview statement without independent confirmation

**Interpretive guidance:**
Moderate confidence claims are **analytically useful** but should be treated as **tentative** until corroborated.

---

### 3.3 LOW Confidence (🔴 Red)

**Definition:**
A claim is supported by **ambiguous, incomplete, or weak evidence**, or involves unresolved uncertainty.

**Typical characteristics:**
- Single-token names (e.g., “John,” “Mike”)
- Pronoun-only references
- Conflicting descriptions
- Unclear identity resolution
- Partial or fragmentary statements

**Examples:**
- “He stayed at Ryan’s” without clarity on which Ryan
- A name mentioned without context or corroboration
- Conflicting timelines between sources

**What LOW does *not* mean:**
- That the claim is false
- That the source is unreliable
- That the information should be discarded

Low confidence flags **analytical uncertainty**, not error.

---

## 4. Independence of Evidence (Key Concept)

### 4.1 What Counts as Independent Evidence

Evidence is considered **independent** if it originates from:
- Different individuals
- Different systems or records
- Different collection events
- Different documents not derived from each other

Examples of independence:
- Two separate interviews
- Interview + surveillance footage
- Interview + phone record
- Interview + physical evidence

### 4.2 What Does *Not* Count as Independent

- Repeated retellings of the same statement
- Reports derived from a single original interview
- Officer notes summarizing the same source
- Multiple references to the same document

NexusLEO explicitly tracks source lineage to avoid false corroboration.

---

## 5. Handling Contradictions

When contradictory evidence exists:
- The contradiction is **preserved**
- Confidence is **reduced**
- Both claims remain visible unless explicitly excluded by the user

NexusLEO does not resolve contradictions automatically.  
Contradiction signals **analytical risk**, not failure.

---

## 6. Color Coding (Visual Aid Only)

| Level    | Color      | Meaning                            |
|----------|------------|------------------------------------|
| HIGH     | 🟢 Green   | Strong analytical support          |
| MODERATE | 🟡 Yellow  | Limited or uncorroborated support  |
| LOW      | 🔴 Red     | Ambiguous or uncertain support     |

**Important:**  
Color indicators are **visual aids only**.  
They do not alter the underlying data, evidence, or analysis.

---

## 7. Transparency Requirements (“Show Your Work”)

Every confidence assessment in NexusLEO is accompanied by:

- The evidence items considered
- The number of sources
- The independence evaluation
- Any ambiguity flags
- The rubric version used

This information is available to:
- Investigators
- Supervisors
- Prosecutors
- Defense counsel (via discovery, if applicable)
- Courts

---

## 8. Versioning and Auditability

Each confidence assessment records:
- Rubric version
- Timestamp
- Tool version
- Evidence references
- Analyst or system actor

Changes to the rubric require:
- A version bump
- An updated appendix
- Explicit documentation of changes

Historical confidence assessments remain tied to the rubric version in effect at the time.

---

## 9. Legal and Operational Disclaimer

NexusLEO confidence assessments:
- Do not establish fact
- Do not determine guilt or innocence
- Do not recommend enforcement action
- Do not substitute for investigative judgment

Confidence ratings are **analytical descriptors**, not legal conclusions.

---

## 10. Summary (Plain Language)

In simple terms:

> Green means “supported by more than one independent source.”  
> Yellow means “supported, but not yet corroborated.”  
> Red means “uncertain or ambiguous — proceed carefully.”

The system shows **what the data says**, **why it says it**, and **how strong that support is** — nothing more, nothing less.

---
