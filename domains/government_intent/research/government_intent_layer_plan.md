# Government Intent / Future Capital Optionality layer

## Purpose

Capture the long-term spatial assumptions, service plans, zoning intentions and capital choices already embedded in Commonwealth, Queensland, New South Wales, ACT and Victorian planning systems.

This layer does **not** treat current government plans as the correct 2075 answer. It records them as the present institutional baseline that VECA may later affirm, redirect or challenge.

## Core distinction

For each planned or implied investment, record both **government intent** and **decision flexibility**.

### Government intent classes

- `statutory_growth_plan` — statutory regional/city plan defining expected growth geography.
- `housing_or_zoning_target` — explicit dwelling target, rezoning direction or urban-footprint change.
- `service_plan` — health, education, emergency or other service-capacity plan.
- `infrastructure_pipeline` — identified future project or network need.
- `asset_renewal` — existing asset expected to require major refurbishment/replacement.
- `land_or_corridor_reservation` — government-controlled land/corridor preserving future choice.
- `strategic_precinct` — designated employment, industrial, university, health or innovation precinct.

### Decision-flexibility classes

- `fixed_inheritance` — already built / practically sunk.
- `committed_low_flex` — contracted or under construction; relocation is unrealistic.
- `planned_medium_flex` — funded/planned but material scope or location could still change.
- `renewal_high_flex` — major future replacement spend is likely but location/model is not immutable.
- `growth_triggered_high_flex` — need arises mainly because current population projections place growth in a particular location.
- `optionality_asset` — land/corridor/reservation that preserves future choice.

## Why this matters to VECA

The economically relevant question is not simply: `What would a new regional settlement cost?`

It is:

> How much future public and private capital is likely to be spent anyway, and how much of that inevitable spend could be redirected to support a superior 2075 spatial system?

A $2.5b hospital replacement, for example, is not equivalent to $2.5b of genuinely incremental cost if a replacement would be required regardless.

## First-pass source hierarchy

1. Statutory state/regional/city plans and spatial maps.
2. Independent infrastructure strategies and priority lists.
3. Departmental service and asset strategies (health, education, water, transport, energy).
4. Budget/forward-estimate project pipelines.
5. Precinct, airport, port and industrial master plans.
6. Local government plans only where they materially affect regional-scale outcomes.

## Current evidence anchors — September 2026

- Infrastructure Australia's 2026 Infrastructure Priority List identifies 68 nationally significant proposals over a 10-year horizon and separates investment-ready, 2–4 year and 5–10 year pipeline items.
- NSW's final 20-year Sydney Plan assumes population growth from about 5.3m to 6.6m by 2046, at least 800,000 more homes and 950,000 more jobs.
- NSW retains a dedicated 20-Year Health Infrastructure Strategy for future health-district/network investment planning.
- Queensland is integrating regional land-use and infrastructure planning: from 2026 statutory regional plans are paired with infrastructure plans covering transport, water, energy, digital and social/community infrastructure. ShapingSEQ 2023 assumes around 6m residents by 2046 and about 900,000 additional homes.
- Victoria's 2025–2055 30-year infrastructure strategy contains 45 recommendations and 8 future options across housing, health, education, water, transport, energy and climate.
- Victoria's Plan for Victoria requires planning schemes to provide capacity for 2.24m additional homes by 2051, including explicit regional-city targets and some diversion of growth away from Melbourne.
- ACT describes its infrastructure program as a multi-decade approach, with current major investment in health, education and transport.

## Outputs

- `data/derived/government_intent_seed.csv` — first-pass structured plan/intent register.
- `data/derived/future_capital_optionality_seed.csv` — future commitments and renewal liabilities with flexibility classification.
- `research/government_intent_findings_v1.md` — early cross-jurisdiction findings.

## Guardrails

- A government forecast is a baseline assumption, not VECA truth.
- Do not count the same project twice because it appears in multiple plans.
- Keep statutory land-use decisions distinct from advisory infrastructure proposals.
- Record publication date and horizon; old plans can remain useful evidence but must be clearly historical.
- Do not assume asset age alone implies relocation or replacement.
- A future hospital/school/network need should be represented as `renewal` or `growth-triggered` only where evidence supports that classification.
