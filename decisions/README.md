# VECA-2075 — Decision Register

This file records consequential project decisions that narrow the research space, select a methodology or materially affect interpretation. It is a compact current register; create separate decision records later if an item needs deeper history.

A decision is not evidence about future Australia. Decisions govern **how VECA investigates** the problem.

## Active decisions

| ID | Date | Decision | Rationale / consequence | Revisit when |
|---|---|---|---|---|
| DEC-001 | 2026-09 | Use ~10 million additional residents as the initial forcing scenario, not a forecast. | Large enough to force meaningful spatial choices without pretending VECA knows the 2075 population. | Population scenarios become central to sensitivity testing. |
| DEC-002 | 2026-09 | Base geographic scope is eastern Australia from SEQ to Melbourne, including plausible inland regions; South Australia excluded initially. | Keeps first model bounded while allowing inland alternatives. | Run later `EXP-SA-001` if Adelaide/SA may materially improve system architecture. |
| DEC-003 | 2026-09 | Settlement before transport. | Prevents HSR, motorway or current corridor assumptions from defining future settlement geography. | Durable doctrine; change only with explicit project-level reconsideration. |
| DEC-004 | 2026-09 | EXP-001 maps the inherited system before candidate cities or settlement ranking. | Establishes common evidence surface and reduces confirmation bias. | EXP-001/EXP-002 evidence is mature enough for candidate discovery. |
| DEC-005 | 2026-09 | Current population receives little direct weight in future settlement potential. | Otherwise analysis simply rediscovers Brisbane/Sydney/Melbourne. Existing population remains relevant to inherited services/capital. | During later scoring design and sensitivity testing. |
| DEC-006 | 2026-09 | Separate evidence, inference and hypothesis. | Repetition must not convert speculation into fact. | Durable research-control decision. |
| DEC-007 | 2026-09 | Keep infrastructure status classes distinct; proposed/planned must not be merged with committed/built. | Avoids overstating inherited capital and political intent. | Durable unless taxonomy needs refinement. |
| DEC-008 | 2026-09 | Organise new repository work domain-first: `domains/<domain>/research`, `data/raw`, `data/derived`. | Research and data for the same subject should remain discoverable together. | Legacy workflow-dependent migration is complete. |
| DEC-009 | 2026-09 | Do not force migration by duplicating large files. | Automated migration was blocked by workflow-update permissions; reproducibility is more important than cosmetic layout. | Workflow permissions/strategy allow safe migration. |
| DEC-010 | 2026-09 | Treat government plans as evidence of intent/path dependency, not as VECA truth. | Current plans partly create the growth/infrastructure outcomes they forecast. | Durable; later scenarios may deliberately compare with current-government baseline. |
| DEC-011 | 2026-09 | Add Future Capital Optionality as an explicit analytical family. | Future public capital differs by flexibility: sunk, committed, planned, renewal, growth-triggered and preserved optionality. This allows alternative settlement cost to be compared with spending that would occur anyway. | Refine classes when whole-system cost modelling begins. |
| DEC-012 | 2026-09 | EXP-002 uses staged physical/resource gates, not a single settlement score. | Prevents hidden weighting from predetermining candidate regions. First output is a survival map with disagreements visible. | After candidate evidence is mature and sensitivity analysis is designed. |
| DEC-013 | 2026-09 | Use future 2050/2070 climate/hazard evidence where possible. | 2075 settlement cannot be screened using present climate alone. | Refine scenario/time slices as better projections are selected. |
| DEC-014 | 2026-09 | Analyse water as a functional engineering system, not a nearby-dam/river variable. | Storage, yield, groundwater, treatment, transfers, desalination/recycling and augmentation have different meanings. | Durable; later economics will add marginal augmentation cost. |
| DEC-015 | 2026-09 | Energy capacity fields remain distinct. | Generation MW, storage MW/MWh, connection capacity and transfer capability are not interchangeable. | Durable. |
| DEC-016 | 2026-09 | Universities, VET/trade colleges and schools have different settlement roles. | Universities can shape population/economy; VET supports workforce scalability; schools are primarily growth-triggered service infrastructure. | Later human-capital methodology may formalise dimensions. |
| DEC-017 | 2026-09 | Existing layered-map POC is an evidence view, not the analytical model. | Underlying entities retain provenance/status/time/scenario semantics; map rendering must not become source of truth. | When production spatial architecture is selected. |
| DEC-018 | 2026-09 | Pause Regional Anchor Cluster join/weighting work. | The concept is useful, but physical EXP-002 survival screening should mature before cluster weighting risks biasing candidate discovery. | Resume explicitly after survival-map evidence is credible. |
| DEC-019 | 2026-09 | Do not use a composite cluster/settlement weight yet. | Node importance should later expose scale, reach, scarcity, replacement cost, scalability, strategic coupling and lock-in/optionality separately; sensitivity testing must precede composite ranking. | Stage 10 scenario comparison/optimisation, or explicit earlier methodological experiment. |
| DEC-020 | 2026-09 | `domains/government-intent/` is canonical; `domains/government_intent/` is legacy. | Duplicate naming emerged during rapid research. New work must not deepen the split. | Consolidate legacy files safely, then remove legacy directory. |

## Pinned future-stage decisions

These are sequencing decisions, not completed work:

- Candidate regions emerge **after** the physical/resource survival screen.
- Attractiveness and voluntary migration are tested before assuming people/businesses will move.
- AI/automation is a stress-test family, not a forecast.
- Alternative settlement systems are constructed before VECA transport architecture.
- Transport is derived from settlement/trip/freight systems; door-to-door access and capacity matter more than CBD-to-CBD headline time.
- Whole-system economics compares alternatives against the counterfactual cost of accommodating the same population under current/default growth, not against zero.
- Composite weighting, if used, must be sensitivity-tested.

## Decision-record standard

When adding a consequential decision, record:
- decision and date;
- evidence/context available;
- alternatives considered;
- rationale;
- uncertainty/risks;
- what would cause reconsideration.

Do not use this register to turn a working hypothesis into a factual conclusion.