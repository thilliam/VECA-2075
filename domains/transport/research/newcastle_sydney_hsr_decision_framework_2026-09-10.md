# Newcastle–Sydney HSR — reverse engineering the decision framework

**Research date:** 10 September 2026  
**Domain:** transport  
**Purpose:** document how HSRA appears to have selected the current Newcastle–Sydney HSR concept, including station-locality screening, alignment selection, demand modelling and mode-shift assumptions.  
**Status:** evidence-led reconstruction. Explicitly separate published evidence from VECA inference. This does not authorise a preferred VECA HSR route.

## Executive finding

The current HSR concept was not selected by comparing only one Newcastle–Sydney alignment. Infrastructure Australia's Stage 3 evaluation says HSRA used a four-stage options process:

1. **Alternative and Deferral** — strategic merit test of 10 non-HSR/rail/non-rail alternatives.
2. **Station Locality** — long list of **26 station locations**, qualitatively scored against Network and Project objectives; 13 survived.
3. **Alignment scenarios** — 13 short-listed station options assembled into **18 alignment options**, screened using catchment/accessibility, demand and land use, strategic technical analysis, preliminary rail operations, strategic costings and qualitative factors; six survived.
4. **Project options analysis** — a three-stage multi-criteria analysis (MCA), including quantitative MCA and rapid economic appraisal, selected the preferred staged solution: Option 1 (Sydney Central) first, extended toward Option 3 (Western Sydney International).

This is enough to reconstruct the *shape* of their decision process, but not yet every criterion weight or every rejected option. The detailed business-case appendices and model outputs are therefore high-value evidence targets.

---

## 1. Sydney target: Sydney Central station, not a generic CBD centroid

### Evidence

Infrastructure Australia repeatedly describes the preferred Stage 1B anchor as **Sydney Central** and the selected station structure as Broadmeadow, Lake Macquarie, Central Coast and Sydney Central, followed later by Parramatta and Western Sydney International.

IA also says the options process selected **Option 1 (Central)** as the first operational endpoint and staged it toward **Option 3 (Western Sydney International)**.

HSRA's public-facing wording is sometimes broader — “central Sydney” — but the evaluated business-case solution is specifically **Sydney Central station**.

### VECA interpretation

The model should therefore not be assumed to use an abstract Sydney CBD centroid as the HSR terminal. The physical HSR endpoint in the preferred concept is Central. However, demand/accessibility modelling almost certainly operates at travel-zone level rather than treating all Sydney demand as trips to the station itself. The critical question is therefore:

> Did HSRA select Central because it optimised network-wide generalised accessibility to Sydney destinations, or because Sydney CBD demand was given disproportionate weight?

The 2013 Phase 2 study provides historical precedent: Central was preferred among Sydney station options despite higher capital cost because that study found it had the highest accessibility to Sydney destinations, was closest to the main demand centre and generated stronger net benefits. We must not assume HSRA 2024 simply inherited that conclusion, but the continuity is important to test.

---

## 2. Central is an unusually strong interchange point in the current network

Transport for NSW's current station information shows Central directly connects:

- suburban rail lines including T1, T2, T3, T4, T8 and T9;
- Intercity and Regional services;
- Sydney Metro M1;
- L1, L2 and L3 light rail;
- extensive bus/coach connections;
- direct Airport Line train services.

This means Central is not merely “at the southern edge of the CBD”; it is the broadest multimodal rail interchange in Sydney.

### Important counterpoint

Central is not necessarily the best destination for every CBD-bound passenger. Town Hall, Wynyard and Martin Place are closer to large portions of the commercial core. Martin Place now has both Metro and T4 rail. The HSR decision therefore depends heavily on whether transfer penalties and onward-access times are correctly represented.

A VECA replication should calculate total door-to-door accessibility from each candidate HSR station, not compare station-to-station running times alone.

---

## 3. Central Coast stops: current preferred concept has ONE HSR station in the Central Coast region

### Evidence

The current Stage 1A/1B preferred concept has four HSR stations:

1. Broadmeadow / Newcastle
2. Lake Macquarie
3. Central Coast
4. Sydney Central

The complete Stage 1 concept then adds Parramatta and WSI.

Prime Ministerial and media material now refers specifically to **Gosford** when quoting the 30-minute Central Coast–Sydney journey. Secondary reporting of the released business case identifies **Morisset** for Lake Macquarie and **Gosford** for the Central Coast station. This is consistent with the public regional labels, but VECA should still preserve the distinction between an official regional station label and a precisely approved site until the primary station-locality material is extracted.

### What HSRA did not do

The published evaluated option is **not** two Central Coast HSR stations such as Gosford + Tuggerah/Wyong. It carries one Central Coast HSR stop, plus a separate Lake Macquarie stop to the north.

### Why this matters

The Central Coast is spatially elongated. A single Gosford-oriented station maximises some combinations of existing population access, interchange and urban renewal, but may under-serve northern Central Coast growth around Tuggerah/Wyong. Conversely, adding a second HSR stop imposes running-time and infrastructure penalties.

The correct VECA question is therefore not “why only one?” in isolation. It is:

> What marginal patronage, accessibility, housing and network benefits did the second Central Coast station generate, and what running-time/capital-cost penalty caused it to be rejected?

We do not yet have that marginal comparison from a primary HSRA table.

---

## 4. Evidence of earlier Central Coast station logic

The 2013 Phase 2 HSR study is useful as a baseline because it documented a very explicit Central Coast station screen. It tested **Kariong, Ourimbah and Tuggerah**.

The 2013 study reported approximate 30-minute-drive accessibility to the then Central Coast population of:

- Ourimbah: **85%**
- Kariong: **82%**
- Tuggerah: **69%**

It preferred Ourimbah because of its central regional location, motorway access and potential conventional-rail connectivity.

HSRA's 2024 business-case process explicitly says it built on the 2013 and 2019 studies but re-ran station-locality analysis using 26 station locations. Therefore the change from the 2013 Ourimbah preference to the current Gosford-oriented Central Coast concept is one of the most valuable decisions to reverse engineer.

Likely explanatory variables to test include:

- direct interchange with existing rail and bus networks;
- current and forecast population catchment;
- jobs and destination accessibility;
- housing/land-use uplift and developable land;
- road access and parking;
- flooding/environmental constraints;
- alignment/tunnelling cost;
- HSR running time;
- value capture / precinct-development potential.

Only the first-level categories are confirmed by published IA material; the relative contribution of each factor to the Gosford decision remains to be extracted.

---

## 5. The demand model is more sophisticated than a simple 'cars removed from M1' calculation

### Evidence

Infrastructure Australia states that HSRA's transport demand modelling incorporates post-COVID behaviour, including increased working from home, through Transport for NSW future-base settings for 2041 and 2061.

IA identifies the model as using Transport for NSW's **PTPM** framework/context. Current TfNSW modelling guidance describes PTPM as a public-transport project model with observed base demand and future growth, operating at travel-zone level across the Greater Sydney Metropolitan Area and representing car, train, bus, ferry and light rail.

Veitch Lister Consulting confirms it performed the demand modelling for the EY-led Economics, Funding and Financing, and Demand Modelling work package, and developed both the Newcastle–Sydney modelling and a new east-coast model.

VLC was re-appointed in July 2026 as Demand Forecasting Adviser for the Development Phase, indicating that the demand model is actively being refined rather than frozen.

### Implication

Mode shift should not be interpreted as:

`HSR passengers = cars removed from M1 + passengers removed from existing Newcastle train`

The model is likely calculating travel-zone origin/destination demand, mode choice, generalised travel cost and induced/redistributed trips across a network with feeder access and transfers.

However, the public IA evaluation exposes only some aggregate outcomes, not the full equations or elasticity assumptions.

---

## 6. Published mode-shift result is surprisingly modest

Infrastructure Australia notes that Stage 1 produces only about **5% switching from cars**. IA specifically flags this as a challenge to the project's national-HSR objectives.

IA also says travel-time savings constitute only around **6% of monetised benefits**, unusually low for a transport project with such a large claimed reduction in journey time.

The dominant monetised benefit is instead **land-use change: 58% of total benefits**.

### VECA interpretation

This is a major clue about HSRA's evaluation philosophy. The project is not primarily being justified as a congestion-relief railway. It is being evaluated as a **city-shaping / land-use / housing intervention with transport benefits**.

Therefore a critique based only on 'how many cars leave the M1?' would miss the logic of the business case. Conversely, because the business case relies so heavily on land-use change, station-location and housing assumptions deserve at least as much scrutiny as train-running-time assumptions.

---

## 7. Current travel assumptions exposed by IA

Published IA figures include:

- existing Newcastle–Sydney rail: about **2h40**;
- equivalent drive: about **30 minutes faster** than rail;
- proposed Newcastle–Sydney Central: around **1 hour**;
- Newcastle–Parramatta: around **1h15**, from about **2h37**;
- Newcastle–WSI: around **1h30**, from about **3h26**;
- forecast project-related journeys discussed by IA: approximately **22.7 million trips per annum in 2061**.

These values need to be reconciled to the detailed business-case demand tables before being used as model inputs.

---

## 8. The current option-selection criteria we can prove

From Infrastructure Australia's description of the 18-alignment screen, the following factors are explicitly confirmed:

| Decision factor | Evidence status | Likely role |
|---|---|---|
| Catchment and accessibility | Explicit | station/location demand and access |
| Demand | Explicit | patronage / mode-choice potential |
| Land use | Explicit | housing and development uplift |
| Strategic technical analysis | Explicit | feasibility/constraints |
| Preliminary rail operations | Explicit | journey time, service pattern, capacity |
| Strategic costings | Explicit | capital/delivery cost |
| Other qualitative factors | Explicit but unspecified | objectives/stakeholder/environment/etc. |
| Rapid economic appraisal | Explicit in final MCA | benefits versus cost |

IA also says the 26 station locations were scored against **Network and Project objectives**, but the complete objective hierarchy, weights and individual station scores are not exposed in IA's 11-page report.

---

## 9. A very revealing result from the final MCA

The selected full Newcastle–WSI option scored only **one percentage point above** the Newcastle–Sydney-Central-only alternative once costs were considered. IA describes the preferred option as producing 55% greater benefits than the second-ranked Central-only option, but its higher costs left the overall MCA result only marginally ahead.

This implies that the Western Sydney extension is not an overwhelming optimisation result. It is a close strategic choice affected by how benefits, future network extension, land use and cost are weighted.

VECA should therefore seek the actual MCA matrix and sensitivity tests before regarding the topology as uniquely optimal.

---

## 10. Reverse-engineering plan

The next research pass should reconstruct the decision system in five layers.

### A. Station-locality matrix

For all 26 station candidates, recover:

- candidate name/location;
- anchor vs optional status;
- catchment population/jobs;
- existing transport connections;
- feeder assumptions;
- housing/development capacity;
- environmental/flood/terrain constraints;
- HSR alignment cost/time consequences;
- qualitative scores;
- shortlist/rejection reason.

### B. Alignment matrix

For all 18 alignment scenarios and six shortlisted options, recover:

- station sequence;
- route length;
- tunnel/viaduct/surface proportions;
- end-to-end and intermediate running times;
- train operating pattern;
- construction cost;
- demand;
- land-use uplift;
- technical/environmental constraints;
- score/rejection reason.

### C. MCA reconstruction

Recover:

- criteria and subcriteria;
- weights;
- normalisation/scoring rules;
- quantitative vs qualitative components;
- rapid-economic-appraisal inputs;
- Option 1 / Option 3 score differences;
- sensitivity tests;
- who approved criteria and weights.

### D. Demand / mode-choice model

Recover:

- base-year OD matrices;
- 2041 and 2061 travel-zone forecasts;
- HSR fares;
- access/egress time and cost;
- transfer penalties;
- wait-time assumptions/frequency;
- in-vehicle time weighting;
- car operating/toll/parking costs;
- existing-rail service assumptions;
- mode-choice parameters / elasticities;
- induced demand;
- land-use feedback;
- work-from-home assumptions;
- road congestion feedback;
- trip-purpose segmentation;
- source of the ~5% car-switch result.

### E. VECA independent replication

Once inputs are available, create a transparent independent model that can answer counterfactuals such as:

- Central vs Martin Place vs Parramatta vs WSI as Sydney anchors;
- Gosford vs Ourimbah vs Tuggerah and one versus two Central Coast stops;
- Morisset/Lake Macquarie station alternatives;
- all-stops versus express service patterns;
- different first/last-mile assumptions including autonomous/shared vehicles;
- current settlement forecasts versus alternative VECA 2075 settlement distributions.

The purpose is not to manufacture a different answer, but to determine which assumptions actually drive HSRA's answer.

---

## 11. Key source provenance

Primary/independent sources used for this reconstruction:

- Infrastructure Australia, *High Speed Rail — Newcastle to Sydney, Stage 3 Evaluation Report*, 23 July 2025.
- HSRA Newcastle to Sydney project page.
- HSRA Industry Update / April 2026 briefing material.
- Transport for NSW current Central Station information and transport modelling guidance.
- Australian Government/HSRA business-case release material.

Supporting/contractor evidence:

- Veitch Lister Consulting, Newcastle–Sydney HSR Business Case demand-modelling project page.
- Veitch Lister Consulting, July 2026 Demand Forecasting Adviser appointment.

Historical comparison only:

- 2013 High Speed Rail Study Phase 2, including Central Coast station assessment. Historical conclusions must not be represented as current HSRA decisions.

## Assurance / limitations

This file is a curated research synthesis, not an exhaustive import. It does not claim all 26 station candidates, all 18 alignment options or full MCA scores are known yet. The exact business-case appendices and detailed demand-model outputs remain unresolved high-priority evidence gaps. Statements identified as VECA interpretation are not source facts.