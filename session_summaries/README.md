# VECA-2075 — Multi-Agent Session Summary and Reconciliation Protocol

**Status:** active coordination process  
**Introduced:** 10 September 2026  
**Purpose:** recover, reconcile and consolidate work performed across parallel VECA agent chats without losing discoveries, duplicating work, or mistaking historical agent claims for current repository truth.

## Why this process exists

VECA has now been advanced through multiple parallel agent sessions. Some sessions changed project infrastructure, some produced datasets or ingestion tooling, some performed research, and some changed maps, assurance controls or analytical framing.

That creates three risks:

1. **Lost discoveries** — useful conclusions, caveats or next-step ideas may exist only in a chat and never have reached the repository.
2. **Duplicate or conflicting work** — two agents may have researched or implemented the same area differently.
3. **False completion** — an agent may correctly report that it produced something at the time, while later work replaced, moved, deprecated or invalidated it.

The solution is a two-stage process:

> **Stage A — each agent records what it did and learned.**  
> **Stage B — a reconciliation pass checks those claims against current `main` and produces one canonical project state.**

A session summary is therefore **evidence about the history of the project, not automatically the current truth of the project**.

---

## Instructions for every agent

Create one Markdown file in:

`session_summaries/`

Use a descriptive name such as:

`agent-map-poc-and-spatial-serving.md`  
`agent-energy-ingestion-and-assurance.md`  
`agent-exp002-climate-screening.md`

Do not overwrite another agent's summary.

Before writing it, inspect the **current repository**, especially:

1. `README.md`
2. `AGENTS.md`
3. `PROJECT_STATUS_AND_ROADMAP.md`
4. `assurance/README.md` if your work touched data, sources or maps
5. the domains/experiments you worked on
6. relevant current files on `main`

The purpose is to distinguish what you originally did from what still exists now.

## Required summary structure

Use these headings.

### 1. Session identity and scope

State:
- the broad purpose of your session/chat;
- the main domains, experiments or infrastructure touched;
- approximate time/order in the project if known;
- whether your work was research, implementation, data ingestion, mapping, project architecture, QA/assurance, or mixed.

### 2. What I actually did

Describe concrete work performed, not intentions.

For repository work, identify the important files/directories, PRs or commits where practical. Do not provide an exhaustive commit log unless it adds value.

Separate:
- files/datasets created;
- files/datasets modified;
- tooling/workflows introduced;
- research/findings added;
- project/process decisions introduced.

### 3. Important discoveries and reasoning outcomes

Record discoveries that mattered to VECA even if they did not become code or data.

Classify each important item where practical as:
- **Evidence** — sourced factual finding;
- **Inference** — conclusion drawn from evidence;
- **Hypothesis / idea** — proposed direction still needing testing;
- **Methodological lesson** — something learned about how VECA should research/build the system.

This section is especially important for preventing chat-only insights from disappearing.

### 4. Current repository status of my work

Inspect current `main` and classify your major outputs:

- `present_current` — still present and appears current;
- `present_but_evolved` — still present but materially changed by later work;
- `superseded` — replaced by a newer implementation/dataset/document;
- `legacy` — intentionally retained but no longer canonical;
- `missing_from_main` — work discussed/done in the session but not found on current `main`;
- `uncertain` — cannot confidently determine current status.

Where something is missing, say whether it is likely:
- never committed;
- committed on another branch only;
- removed later;
- absorbed into another artefact;
- unknown.

Do **not** recreate missing work during this summary task unless explicitly asked. Surface it for reconciliation.

### 5. Incomplete work / backlog I left behind

List work that was started but incomplete, deliberately deferred, blocked, or merely proposed.

Distinguish:
- required follow-up;
- optional enrichment;
- speculative future idea;
- obsolete follow-up that later work has already solved.

### 6. Potential overlaps or conflicts with other agents

Identify areas where another agent may reasonably have touched the same:
- dataset;
- source family;
- map layer;
- extractor/workflow;
- taxonomy/schema;
- README/status document;
- analytical method;
- candidate-region research.

Do not attempt to resolve the conflict unless it is obvious. Describe what needs comparison.

### 7. Things that should be promoted to canonical project knowledge

List any finding, decision, warning, reusable method or source family that is important enough that it should eventually live in one of:
- `PROJECT_STATUS_AND_ROADMAP.md`;
- `decisions/`;
- doctrine;
- a domain findings document;
- `assurance/`;
- an experiment README/findings file;
- the active backlog.

This is the explicit recovery mechanism for valuable chat knowledge that may not yet be represented canonically.

### 8. Suggested reconciliation checks

Give the later reconciliation agent specific checks that would confirm your work, for example:
- compare dataset row counts against manifest;
- inspect PR #N;
- search for an older duplicate CSV;
- compare two schema versions;
- verify a map layer is generated from the canonical dataset;
- check whether a proposed backlog item is already done by another session.

### 9. Compact handover

Finish with no more than roughly 10 bullets covering:
- strongest completed contributions;
- strongest discoveries;
- biggest unresolved issue;
- biggest suspected overlap;
- what you would do next if this were still your active task.

---

## What not to do

During the summary pass:

- Do not claim the repo is complete because your session completed its assigned task.
- Do not silently update project doctrine or status to match your recollection.
- Do not delete apparent duplicates.
- Do not re-run large ingestions simply to prove they once worked.
- Do not turn hypotheses into established findings.
- Do not assume your old paths are still canonical.
- Do not assume an old PR/commit still represents the latest implementation.

The purpose is **recovery and reconciliation first, cleanup second**.

---

# Stage B — cross-session reconciliation

After the session summaries exist, perform a dedicated reconciliation pass.

## Reconciliation outputs

The reconciliation pass should produce:

1. **Current-state matrix** — each claimed deliverable mapped to current repo artefact/status.
2. **Discovery recovery list** — useful findings/ideas absent from canonical docs.
3. **Duplicate/overlap register** — competing datasets, schemas, tools, map layers or analyses requiring comparison.
4. **Missing-work register** — material session outputs not found on `main`.
5. **Superseded/legacy register** — old artefacts that should be clearly marked or eventually retired.
6. **Canonical backlog** — one deduplicated list of remaining work.
7. **Canonical status update** — only after reconciliation, update `PROJECT_STATUS_AND_ROADMAP.md`, README/status docs and decisions where warranted.

## Recommended reconciliation table

Use a table with fields similar to:

| Claimed contribution | Session | Current artefact | Repo status | Assurance/status confidence | Overlap | Action |
|---|---|---|---|---|---|---|
| Example dataset | energy agent | `domains/...csv` | present_current | verified | none | retain |
| Earlier map layer | map agent | `maps/poc-002/...` | superseded | n/a | POC-003 | document lineage |
| Research insight | first agent | none | missing_from_canonical_docs | medium | none | promote to findings |

The key distinction is between **repository existence**, **current canonical status**, **data assurance**, and **analytical validity**.

---

# Improvements to the multi-agent workflow after reconciliation

This exercise should be a one-time recovery pass, but the underlying problem should not recur.

## 1. Require a session closeout for substantial agent work

For any task spanning substantial research, implementation or multiple commits, the agent should update/create its session summary before finishing. The summary can be short if the task is narrow.

## 2. Give each parallel agent an explicit ownership boundary

Every task should name:
- owned domain/region/output;
- files/registers the agent may edit;
- files it should avoid because another agent owns them;
- completion test;
- required assurance checks.

This reduces README/register collisions and duplicate source ingestion.

## 3. Separate work completion from canonical integration

An agent may complete a bounded task without being authorised to rewrite the global roadmap. Global synthesis/status should be updated by a coordination/reconciliation pass after parallel work lands.

## 4. Record discoveries as first-class outputs

A successful research session should not only produce CSVs. It should also produce a concise findings/limitations record. Otherwise the project accumulates data but loses the reasoning that made the data valuable.

## 5. Use stable IDs for work packages where useful

For larger parallel waves, assign IDs such as:

`WAVE-EXP002-CLIMATE-01`  
`WAVE-ENERGY-DNSP-02`

and include the ID in the session summary, PR and relevant manifest/findings note. This makes later provenance from task -> PR -> dataset -> findings much easier to reconstruct.

## 6. Treat `main` + assurance as the implementation truth, and session summaries as history/context

Where a summary and current repository disagree, do not automatically trust either. Inspect commits, provenance, assurance state and current consumers. Reconciliation is an evidence task too.

---

## First example

The original foundation/research agent summary is:

`session_summaries/agent-001-foundation-research-and-handover.md`

Use its structure as a worked example, but describe your own session rather than copying its conclusions.
