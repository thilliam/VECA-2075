# Session Summary — WSI, HSR and Airport Accessibility

## 1. Session identity and scope

This session was a focused transport-research and analytical-framing discussion around **Western Sydney International Airport (WSI)** and how its existence changes interpretation of the 2013 Australian High Speed Rail study.

The session did **not** design or authorise a VECA HSR route. It explored how a major new transport/economic node that did not exist as an operating airport in the 2013 study changes the questions VECA should later ask about HSR, airport access and Sydney metropolitan geography.

Main areas touched:
- 2013 HSR study assumptions and station/corridor criteria;
- WSI / Bradfield as a new national transport node;
- Sydney Airport (SYD) versus WSI accessibility by road and public transport;
- future accessibility/isochrone analysis using LGA/SA1/population data;
- possible HSR interchange concepts at or near WSI/Bradfield;
- regional-centre access to international aviation without entering central Sydney.

Approximate project timing: 9–10 September 2026, after the first major transport/population map layers and HSR evidence lineage had already been established.

Work type: research, inference, analytical-method design and future map/backlog framing. No code, dataset or map layer was implemented in this session.

## 2. What I actually did

### Research / interpretation performed

Reviewed the implications of WSI for the assumptions embedded in the 2013 HSR study, holding other 2013 conditions conceptually constant.

The discussion identified that WSI changes more than airport count. It potentially changes:
- station catchments;
- metropolitan travel markets;
- airport interchange value;
- Western Sydney's network centrality;
- development/value-capture opportunities;
- the geometry and cost logic of penetrating Sydney CBD;
- regional-centre access to international aviation.

### Airport-accessibility analytical concept

Proposed a future VECA analysis comparing **door-to-airport travel time to WSI versus Sydney Airport (SYD)** across Greater Sydney and surrounding regions.

The suggested analytical unit was finer than LGA — preferably SA1, population grid or another fine population surface — with results then aggregated to LGA for reporting.

For each origin point `p`, the basic analytical object proposed was:

`delta_t = time_to_SYD - time_to_WSI`

Interpretation:
- positive value: WSI is faster;
- zero: equal-time boundary;
- negative value: SYD is faster.

Separate surfaces should be produced for:
- road travel;
- public transport;
- potentially later multimodal/door-to-door travel.

The resulting `delta_t = 0` contour would create an intuitive **WSI-versus-SYD airport catchment boundary**, while the full raster/surface would show the magnitude of the accessibility advantage rather than only the dividing line.

### Mapping/product framing

Proposed that accessibility/isochrones become a reusable VECA analytical layer rather than an airport-specific one.

The same engine could later evaluate:
- airports;
- HSR stations;
- major hospitals;
- universities;
- CBD/employment centres;
- ports/intermodal terminals;
- other regional anchors.

This would shift the map from showing only **where infrastructure exists** to showing **what that infrastructure enables in travel-time terms**.

### WSI / Bradfield HSR-station concept

Explored whether physical/planning space exists near WSI for an HSR station and concluded that this is sufficiently plausible to justify future formal investigation.

Three conceptual station/interchange zones were identified:
1. **Airport terminal** — best direct interchange, but potentially expensive and geometrically restrictive;
2. **Airport edge / business precinct** — potentially easier HSR geometry with a short Metro transfer;
3. **Bradfield** — particularly interesting as a possible multi-network interchange because it combines undeveloped/planned land, Metro access and future southward network connections.

No preferred station location was selected.

### Regional-centre / airport-network framing

Highlighted a different travel-market question from the traditional HSR framing.

Instead of evaluating only:

`regional centre -> Sydney CBD`

VECA should later also evaluate:

`regional centre -> international aviation network`

A WSI/Bradfield HSR interchange could potentially allow places such as Newcastle, the Central Coast, Canberra and later other regional centres to access an international airport **without entering central Sydney or relying on Sydney road congestion**.

This is a potentially important network-value effect not captured well by a simple city-pair HSR versus air comparison.

## 3. Important discoveries and reasoning outcomes

### Evidence

- The current repository already records that historical HSR studies were strongly CBD-demand oriented and that their station conclusions reflect the land-use/employment assumptions of their time.
- The current HSR evidence notes already record that current HSRA planning is more polycentric and includes Western Sydney International Airport as a potential national-network node.
- The current roadmap recognises Western Sydney Airport / Aerotropolis / Bradfield as evidence that coordinated public infrastructure and planning can deliberately create new economic gravity.
- Current VECA mapping already contains population, LGA, road and rail foundations sufficient to support a future accessibility-analysis layer once routing/travel-time capability is added.

### Inference

- If the 2013 HSR study were rerun with WSI inserted but other assumptions held constant, WSI/Western Sydney would likely score materially better as a station/network node than it could in 2013.
- WSI potentially changes the HSR question from `how do we reach Sydney Central?` to a broader network-topology question: `which Sydney nodes should the through network serve, and which should be branches/interchanges?`
- Metropolitan HSR access cost may make a Western Sydney/WSI node disproportionately important because the repository's existing evidence shows the Newcastle–Sydney metropolitan approach was exceptionally expensive per kilometre compared with long rural/intercity sections.
- An airport-accessibility surface is more informative than an LGA-level binary comparison because motorway/rail topology creates irregular catchments that do not follow administrative boundaries.
- Accessibility should be treated as a population-weighted network property, not merely straight-line distance.

### Hypothesis / idea

- A future through-HSR topology might plausibly use WSI/Bradfield as a major node with Sydney CBD served as a branch or separate metropolitan connection rather than forcing all north–south services through Central. This is strictly a hypothesis for later Stage-8 transport work, not a current route recommendation.
- Bradfield may prove more attractive than the terminal itself for a national HSR interchange because of land, geometry and network-integration considerations.
- WSI may substantially expand the effective international-airport catchment of regional NSW/ACT if fast rail can connect regional centres directly to the airport precinct.
- The `WSI vs SYD equal-time boundary` could become a useful early demonstration of VECA's map evolving from evidence display into network analysis.

### Methodological lesson

- Future transport evaluation should use **door-to-door accessibility and network effects**, not just intercity station-to-station times.
- VECA should distinguish an infrastructure node's local demand from its **interchange/network value**.
- A new transport node can alter the relevance of historical feasibility-study conclusions even when the underlying engineering evidence remains valuable.
- Historical HSR findings should therefore be decomposed into durable evidence (cost, geology, tunnelling, demand behaviour) versus assumptions tied to the settlement/airport geography of the study year.

## 4. Current repository status of my work

### `present_current`

The following underlying ideas are already represented in current `main`:
- historical HSR evidence reuse rather than route advocacy;
- strong historical CBD-demand orientation;
- need to test Western Sydney / WSI rather than assume Central;
- current HSRA recognition of WSI as a network node;
- Western Sydney / Bradfield as a Capital Gravity example;
- population/LGA/road/rail spatial foundations.

### `present_but_evolved`

- HSR evidence exists mainly in legacy `research/transport/hsr_evidence_findings.md` and related study-evidence material while canonical domain-first transport organisation is being developed.
- Map capabilities are materially more advanced than the assumptions under which the original HSR evidence was collected; POC-003 population/LGA/transport layers now make finer accessibility analysis practical.

### `missing_from_main`

The following chat outcomes were not found as explicit canonical artefacts on current `main` during this summary pass:
- a defined **WSI-versus-SYD accessibility/isochrone study**;
- the `delta_t = time_to_SYD - time_to_WSI` analytical layer concept;
- a backlog item to population-weight and aggregate the airport accessibility result by LGA;
- explicit comparison of WSI HSR station zones: terminal vs airport edge/business precinct vs Bradfield;
- explicit regional-centre-to-international-airport accessibility framing;
- a formal `WSI–Bradfield national transport hub candidate` analytical object.

These appear to be chat-only ideas rather than previously implemented/removed work.

### `uncertain`

- Detailed land/corridor safeguarding around WSI/Bradfield was not inspected deeply enough during this summary task to classify an actual HSR alignment or station footprint as physically available.
- The exact future rail connections south/west of Bradfield and their preservation status should be checked against current NSW/Commonwealth planning sources before any station geometry is treated as feasible.

## 5. Incomplete work / backlog I left behind

### Required follow-up

- Build a formal WSI-versus-SYD accessibility study specification.
- Select a routing engine/data source for road and public-transport travel times.
- Calculate travel-time surfaces at SA1/population-grid resolution rather than only LGA centroids.
- Aggregate results to LGA and population-weighted catchments.
- Produce separate road and public-transport surfaces after the St Marys–WSI Metro opens.
- Map the equal-time contour and travel-time advantage bands.
- Verify WSI/Bradfield planning/cadastral/airport-safeguarding constraints before treating any HSR station zone as feasible.

### Optional enrichment

- Add peak/off-peak road scenarios.
- Add reliability/variance, not only mean travel time.
- Compare public transport access with and without proposed future rail extensions.
- Calculate population within 30/45/60/90 minutes of each airport.
- Extend the accessibility engine to major hospitals, universities, employment nodes and later HSR stations.

### Speculative future idea

- During Stage 8, compare Sydney HSR network topologies such as Central-through, WSI-through, Parramatta/WSI multi-node, and branch-to-CBD structures using whole-network travel demand and construction-cost evidence.

This must remain deferred under current doctrine: VECA has not yet reached transport-design stage.

## 6. Potential overlaps or conflicts with other agents

Likely overlaps:
- **Foundation/HSR research agent:** existing historical HSR study extraction and WSI evidence.
- **Map agents:** population, LGA, road/rail geometry, routing/serving architecture and future analytical layers.
- **Government Intent agent:** WSI/Aerotropolis/Bradfield planning and future-capital evidence.
- **Transport-capacity agents:** conventional rail capacity and network topology around Western Sydney.
- **Future accessibility/Regional Anchor Cluster work:** travel-time catchments are directly relevant to the paused Regional Anchor Cluster methodology.

Potential conceptual conflict:
- This session explored possible HSR topology around WSI. Current VECA doctrine explicitly says no preferred HSR alignment is authorised before settlement scenarios are established. Any WSI-through-route language must therefore remain clearly labelled as a hypothesis/test case rather than a project recommendation.

## 7. Things that should be promoted to canonical project knowledge

Recommended promotions:

1. Add **travel-time accessibility / isochrones** to the future analytical-map backlog as a reusable capability.
2. Add **WSI vs SYD airport accessibility** as a bounded first use case because population, LGA, road and rail foundations already exist.
3. Record that historical HSR station/corridor conclusions should be stress-tested against major post-study nodes such as WSI rather than reused unchanged.
4. Record **regional centre -> international airport accessibility** as a distinct network-value measure for later transport evaluation.
5. Add terminal / airport-edge / Bradfield as three HSR-interchange zones to investigate later, without selecting among them now.
6. Preserve the distinction between local station demand and national/interchange network value.

Appropriate destinations could include:
- transport findings/backlog;
- map analytical-layer roadmap;
- a later accessibility methodology document;
- Stage-8 transport architecture backlog;
- WSI/Bradfield government-intent findings.

## 8. Suggested reconciliation checks

1. Check current HSR study-evidence files for WSI/Bradfield references and avoid duplicating an existing station-catchment task.
2. Check the map POC backlog for any already-planned routing/isochrone capability.
3. Check current population derivatives to determine the best fine-grained population origin layer for accessibility modelling.
4. Check whether road-network topology in current derivatives is routing-safe or only visual/map-safe.
5. Check NSW transport planning sources for definitive St Marys–WSI Metro travel times and interchange assumptions before modelling public transport.
6. Check current Western Sydney/Aerotropolis planning datasets for land reservations, Metro stations, protected corridors and airport safeguarding around Bradfield.
7. Compare this session's airport-accessibility idea with the paused Regional Anchor Cluster travel-time-catchment task; they may share the same future routing infrastructure.
8. Ensure any later WSI HSR topology experiment is explicitly gated to Stage 8 and not interpreted as current candidate selection.

## 9. Compact handover

- WSI materially changes the context in which the 2013 HSR station/corridor conclusions should be interpreted.
- Current repo HSR evidence already recognises WSI as a possible national network node; this session extends that into accessibility and interchange analysis.
- Strongest new analytical idea: map `time_to_SYD - time_to_WSI` across population origins and derive the equal-time boundary.
- Do this below LGA resolution, then population-weight/aggregate to LGA.
- Produce road and public-transport versions; the two catchments will differ materially because network topology matters.
- Treat accessibility/isochrones as reusable VECA infrastructure, not an airport-only feature.
- Investigate terminal, airport-edge/business-precinct and Bradfield HSR station zones later; no preferred location is authorised.
- Important network-value question: can regional centres reach international aviation through WSI without entering central Sydney?
- Biggest overlap: map/routing capability and the paused Regional Anchor Cluster travel-time-catchment work.
- Next action if this became active work: specify and build the WSI-vs-SYD accessibility layer using existing population/road/rail foundations, while keeping HSR route design deferred until Stage 8.
