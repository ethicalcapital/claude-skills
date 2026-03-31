---
name: writing-exclusions
description: Use when writing reason_detail narratives for exclusions.active_exclusions records, or when composing exclusion prose for the website at /exclusions/{ticker}/. Triggers on "write exclusion entry", "write reason_detail", "draft exclusion narrative", or any request to document why a company is excluded.
---

# Writing Exclusion Entries

`reason_detail` is the public-facing prose in `exclusions.active_exclusions`. It renders on ethicic.com/exclusions/{ticker}/ and is the authoritative explanation of why a company is excluded. One record per `sub_category_code` — a company with three exclusion reasons gets three separate narratives.

## The Voice

Third-person factual narrative. You are writing a regulatory finding, not an opinion piece. The facts carry the judgment — you don't need adjectives to make the case. If the evidence is damning, just state the evidence.

## Structure

1-3 paragraphs of plain prose. No markdown headers, no bullet points, no tables, no "Excluded under X.X (policy name)" formulae. Just sentences.

**Paragraph 1**: What the company does that triggers this specific exclusion code. Name the business activity, its scale, and its centrality to the company. Revenue percentages, customer counts, asset values.

**Paragraph 2** (if needed): The specific conduct, incident, or pattern. Dates, dollar amounts, regulatory bodies, case numbers, settlement terms. Named sources (ViolationTracker, InfluenceMap, BHRRC, SEC, DOJ).

**Paragraph 3** (if needed): Context that sharpens or complicates the picture — transition plans that are real vs. performative, mitigating facts that matter, or the absence of commitments that should exist.

## What Good Looks Like

**CenterPoint Energy — political_influence:**
> CenterPoint sits on the board of the American Gas Association, which opposes building electrification policy. The company is a member of ALEC and Consumer Energy Alliance. It supported Texas SB 1261, which blocks municipal greenhouse gas regulation, and Indiana PL 180, which blocks fossil gas bans.
>
> In 2021, a CenterPoint lobbyist ghostwrote third-party comments submitted to Minnesota regulators supporting gas appliance rebates. The company acknowledged providing "guidance and sample letters." InfluenceMap assesses CenterPoint as taking "mostly negative positions on the energy transition" and "strategically advocating for fossil gas infrastructure."

**NiSource — natural_gas:**
> On September 13, 2018, over-pressurization of Columbia Gas of Massachusetts pipelines caused approximately 80 homes in Lawrence, Andover, and North Andover to explode or catch fire simultaneously. One person was killed and at least 25 were injured. The Massachusetts Attorney General reached a $56 million settlement. Residents and businesses received $143 million. Municipalities received $83 million. NiSource subsequently sold its Massachusetts gas operations to Eversource for $1.1 billion.
>
> The incident was the worst natural gas utility disaster in modern U.S. history. NiSource continues to operate Columbia Gas in six other states, distributing natural gas to 3.5 million customers with no announced phase-out plan.

**Seaboard Corporation — animal_exploitation:**
> Seaboard Corporation is a major vertically integrated pork producer, operating large-scale hog confinement facilities and processing plants primarily through its Seaboard Foods subsidiary. In 2003, workers at a Seaboard Farms facility in Oklahoma were charged with felony animal cruelty after a PETA undercover investigation documented systemic abuse of pigs. Seaboard Foods processes approximately 20,000 hogs per day at its Guymon, Oklahoma plant, making it one of the largest pork processing operations in the United States.

## Rules

1. **One record = one sub_category_code.** Don't cover multiple exclusion reasons in a single entry. CenterPoint has separate entries for `community_harm`, `fossil_fuels_midstream`, and `political_influence` — each tells its own story. Before writing, check the taxonomy description for the code you're writing — it tells you exactly what belongs here vs. next door. Read the descriptions for adjacent codes too.

2. **Route off-code evidence to review_note.** If you find evidence that doesn't fit the current `sub_category_code` but is real and material, don't drop it — write it into the record's `review_note` field with a date stamp, source attribution, and a note about which code it might belong under. Example: `[2026-03-16: AFSC documents 53 BOP contracts ($9M, 2008-2021). Does not fit military_contracting — may warrant separate record under private_prisons.]` This preserves the evidence for CIO triage without contaminating the narrative.

3. **Lead with scale and specificity.** Not "the company has fossil fuel exposure" — instead "derives approximately 47% of revenue from natural gas distribution, serving over 4 million gas customers."

4. **Numbers baked into sentences, not listed.** Not "Revenue: $19B. Customers: 4M." Instead: "The company has committed $19 billion to gas infrastructure investment through 2035."

5. **Source attribution in the prose.** "InfluenceMap assesses..." "ViolationTracker documents..." "BHRRC 2025 data links..." "The SEC order (Administrative Proceeding File No. 3-14380) documented..."

6. **Let facts editorialize.** Not "the company is irresponsibly expanding fossil infrastructure." Instead: "The company has committed $19 billion to gas infrastructure through 2035 — not maintaining legacy systems, but actively expanding the network." The em-dash does the work.

7. **Name the absence.** "CenterPoint has no Science Based Targets initiative commitment. Its self-set net-zero target excludes Scope 3 emissions from sold gas, which is the dominant emission source for a gas distribution utility." Stating what doesn't exist is as important as stating what does.

8. **Acknowledge real complexity.** "The natural gas exposure is real but directionally shrinking under binding state law." "Gas distribution is a regulated utility obligation, not a strategic fossil fuel bet." Don't flatten nuance — the credibility of the exclusion depends on it.

9. **When a record should be lifted, say so.** "Six targeted searches found no evidence that Federal Realty Investment Trust leases properties to ICE... This record has been lifted." "The original fossil fuel exclusion predates this divestiture and is factually stale."

10. **Consistent tense.** Present tense for ongoing business activities ("Caterpillar operates a Government & Defense division"). Past tense for specific events ("settled in 2022 for $740 million"). Never mix tenses for the same timeframe — "holds 53 contracts between 2008 and 2021" is wrong because the contracts are historical.

## CIO Calibration Standards

These judgment calls encode how the CIO evaluates severity, materiality, and recency. Apply them when writing narratives.

**Escalating threshold (conduct codes):** One incident is alarming and merits observation. Two independent incidents are very concerning. Three or more isolated incidents with unrelated plaintiffs/sources showing the same fact pattern is dispositive of a systemic problem. This applies to: discrimination, harassment, working_conditions, anti_union, regulatory_failures, and OSHA violations. Note: OSHA penalties are often capped by statute (~$16K max per violation) — small dollar amounts do not mean small violations. It's the pattern.

**Recency and reform:** Companies can heal. A company with a terrible historical record but genuine, sustained reform should be reassessed. Ørsted went from the dirtiest energy company in Europe to the cleanest. State the historical record AND the current trajectory. Exclusions should reflect the present reality, not permanent punishment.

**Military contracting materiality:** Not every company that sells something to the military is a defense contractor. Exclusion thresholds: (1) specialized products/marketing targeting military customers, (2) military revenue >15% of total, or (3) purpose-built weapons systems. Dual-use commodity products (semiconductors, extension cords, test equipment) purchased by militaries are NOT grounds. Supporting military personnel as human beings (healthcare, insurance, worker protections) is NOT grounds. The line is between the war-industrial complex and incidental service to people who work in it.

**Emissions are peer-relative:** A retailer with an embarrassing carbon footprint relative to apparel peers may be excluded even if its absolute emissions are small. The questions: How does this company compare to its sector? Does leadership treat emissions governance as part of their job?

**Conflict zone affirmative defense:** For a company operating in a conflict zone to avoid exclusion, there must be an affirmative argument that the civilian population would be materially worse off without the company's service (e.g., the only source of heat or power). Partnering with a junta to run a mine gets no such defense.

**PFAS routing:** PFAS in pesticide formulations → `pesticides`. PFAS from non-pesticide products (Teflon, firefighting foam, food packaging) → `environmental_damage` or a future harmful products code, not `pesticides`.

## Anti-patterns

| Don't write | Write instead |
|-------------|---------------|
| "Excluded under 2.3 (Addictive Products) for tobacco manufacturing." | "Philip Morris International derives approximately 70% of its $35.2 billion revenue from combustible cigarette manufacturing across 180 markets." |
| "The company has environmental concerns." | "PPL has accumulated $213.7 million in environmental penalties across 43 enforcement records documented by ViolationTracker." |
| "There are labor violations in the supply chain." | "BHRRC 2025 data links Meta to the highest number of global migrant and gig worker abuse cases among major tech companies, concentrated in content moderation workforce." |
| "Significant regulatory issues." | "The Massachusetts Attorney General reached a $56 million settlement. Residents and businesses received $143 million." |
| "Industry-leading emissions" | "LG&E and KU operate a generation fleet that is approximately 79% coal-fired, 20% natural gas, and 1% renewable — among the most carbon-intensive in the U.S. utility sector." |

## Database Fields

Each entry updates `exclusions.active_exclusions`:

```sql
UPDATE exclusions.active_exclusions SET
  reason_detail = 'Your narrative here',
  review_status = 'needs_cio_review'
WHERE id = '<uuid>';  -- always target by row ID
```

- `reason_detail`: The prose narrative (plain text, no markdown)
- `review_status`: Set to `needs_cio_review` for CIO sign-off before going live
- `evidence_url` / `evidence_urls`: Direct URL to primary source document
- `evidence_citation`: Formal citation string ("ViolationTracker Global, accessed 2026-03-10")

All INSERT statements must use `ON CONFLICT DO NOTHING` or `ON CONFLICT ... DO UPDATE`.

---

<!-- TAXONOMY_START -->
## Taxonomy Reference (auto-generated 2026-03-31)

> **3,331** active exclusion records across **2,389** companies, **55** sub-category codes.
> Queried from `exclusions.taxonomy` + `exclusions.active_exclusions`.
> **Stale if older than 12 months.** Re-run: `doppler run -- uv run scripts/refresh_exclusion_taxonomy.py`

### 2.1 Harm to Living Beings
*Product-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `animal_exploitation` | Animal Exploitation | 33 | Catch-all for commercial exploitation of animals not covered by a specific child code (animal_exploitation_hides, ani... |
| `animal_exploitation_entertainment` | Animal Entertainment | 20 | Use of live animals in commercial entertainment, including circuses, marine parks (SeaWorld), rodeos, bullfighting, e... |
| `animal_exploitation_hides` | Hides, Furs & Exotic Leather | 84 | Commercial production or sale of animal hides, furs, exotic leather, or skins — including fur farming, trapping, and ... |
| `animal_exploitation_meat` | Meat, Dairy & Eggs | 111 | Commercial production, processing, or significant revenue from sale of meat, poultry, seafood, dairy, or eggs — inclu... |
| `animal_testing` | Animal Testing & Research | 699 | Companies that test on animals as part of product development, regulatory compliance, or research — pharmaceuticals, ... |
| `factory_farming` | Factory Farming | 9 | Concentrated animal feeding operations (CAFOs) and industrial-scale confinement agriculture — companies whose primary... |
| `fur_exotic_skins` | Fur & Exotic Skins | 4 | Legacy code — functionally identical to animal_exploitation_hides. Retained for historical records. New records shoul... |
### 2.2 Weapons and Military Operations
*Product-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `military_contracting` | Military Contracting | 126 | Companies that sell weapons, military materiel, defense equipment, or military services where the military applicatio... |
| `weapons_promotion` | Weapons Promotion | 6 | Companies that promote civilian weapons ownership, manufacture civilian firearms or ammunition, or operate retail cha... |
### 2.3 Addictive and Exploitative Products
*Product-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `alcohol` | Alcohol Products | 13 | Companies that manufacture, distribute, or derive significant revenue from alcoholic beverages — breweries, distiller... |
| `exploitative_entertainment` | Exploitative Entertainment | 6 | Entertainment business models that exploit vulnerable populations or normalize harmful behavior — includes predatory ... |
| `gambling` | Gambling Operations | 25 | Companies that operate casinos, sportsbooks, online gambling platforms, lottery systems, or derive significant revenu... |
| `opioids` | Opioid Crisis | 10 | Companies with demonstrated lack of internal controls over opioid marketing, distribution, or prescribing incentives.... |
| `tobacco` | Tobacco Products | 17 | Companies that manufacture, distribute, or derive significant revenue from tobacco or nicotine products — cigarettes,... |
### 2.4 Fossil Fuels and Extractive Industries
*Product-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `coal` | Coal Operations | 91 | Companies that mine, process, transport, or trade thermal or metallurgical coal as a primary business activity. Inclu... |
| `extractive_industries` | Extractive Industries | 39 | Non-fuel mining and extraction — companies that extract minerals, metals, aggregates, or other non-fuel natural resou... |
| `fossil_fuel_ancillary` | Fossil Fuel Ancillary Services | 67 | Legacy code — being replaced by fossil_fuel_services. Companies that provide ancillary services, equipment, or infras... |
| `fossil_fuel_services` | Fossil Fuel Services | 67 | Oilfield services, equipment manufacturing, and contracting that primarily serve fossil fuel operators (e.g., SLB, Ha... |
| `fossil_fuels` | General Fossil Fuels | 0 | TEMPORARY CATCHALL — pending reclassification into fossil_fuels_upstream, fossil_fuels_midstream, fossil_fuels_downst... |
| `fossil_fuels_downstream` | Downstream Fossil Fuels | 30 | Refining, marketing, and retail distribution of fossil fuel products: refineries, fuel retailers, petrochemical proce... |
| `fossil_fuels_midstream` | Midstream Fossil Fuels | 63 | Transportation, storage, and processing of fossil fuels: pipelines, terminals, LNG facilities, storage operators. Ess... |
| `fossil_fuels_upstream` | Upstream Fossil Fuels | 96 | Exploration, extraction, and production of oil, gas, and other fossil fuels (E&P companies, drilling operators, produ... |
| `natural_gas` | Natural Gas | 16 | Companies primarily in natural gas distribution, storage, or retail — gas utilities, local distribution companies (LD... |
| `oil_gas` | Oil & Gas Extraction | 19 | Legacy catch-all for integrated oil and gas companies that span upstream, midstream, and downstream operations. For n... |
### 2.5 Surveillance and Incarceration Systems
*Product-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `border_enforcement` | Border Enforcement Infrastructure | 1 | Companies that provide infrastructure, technology, equipment, or services specifically to national border enforcement... |
| `surveillance_tech` | Surveillance Technology | 36 | Companies that manufacture, develop, or sell surveillance technology as a product — including hardware (cameras, sens... |
### 3.1 Forced Labor, Child Labor, and Trafficking
*Conduct-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `child_labor` | Child Labor | 5 | Use of child labor in company operations or supply chains |
| `forced_labor` | Forced Labor | 29 | Forced or bonded labor, human trafficking for labor exploitation, and modern slavery in direct operations or supply c... |
### 3.2 Worker Rights and Workplace Safety
*Conduct-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `anti_union` | Anti-Union Activity | 41 | Documented pattern of suppressing worker organizing — union-busting campaigns, retaliatory firings of organizers, man... |
| `discrimination` | Workplace Discrimination | 42 | Documented systemic discrimination in hiring, pay, promotion, or workplace conditions — racial discrimination, gender... |
| `preventable_deaths` | Preventable Deaths | 27 | Any corporate conduct, product defect, or operational failure that results in preventable human deaths — industrial d... |
| `worker_exploitation` | Worker Exploitation | 21 | Systematic wage theft, misclassification of employees as contractors, unpaid overtime, tip theft, or other schemes to... |
| `working_conditions` | Working Conditions | 36 | Dangerous or degrading workplace conditions — documented patterns of preventable injuries, deaths, or illness caused ... |
### 3.3 Conflict, Occupation, and Indigenous Rights
*Conduct-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `conflict_zones` | Conflict & War Zones | 116 | Companies operating in or materially supporting activities in active conflict zones — providing goods, services, or i... |
| `human_rights_violations` | Human Rights Violations | 3 | Documented complicity in serious human rights violations that do not fit a more specific code — extrajudicial killing... |
| `indigenous_rights` | Indigenous Rights | 12 | Human rights violations, Violations in conflict situations, Disrespecting indigenous sovereignty |
| `occupied_territories` | Occupied & Disputed Territories | 171 | Companies operating in or materially supporting activities in occupied or disputed territories in violation of intern... |
### 3.4 Environmental and Climate Misconduct
*Conduct-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `climate_policy` | Climate Intransigence | 95 | Companies that actively obstruct climate policy, misrepresent climate science, set misleading climate targets, or lob... |
| `emissions` | Emissions & Air Quality | 104 | Companies with outsized greenhouse gas emissions, criteria air pollutant violations, or systematic failure to reduce ... |
| `environmental_damage` | Environmental Damage | 349 | Documented environmental destruction — oil spills, toxic contamination, deforestation, habitat destruction, soil cont... |
| `pesticides` | Pesticides & Chemicals | 11 | Companies that manufacture, distribute, or derive significant revenue from synthetic pesticides, herbicides, or indus... |
| `waste_plastics` | Waste & Plastics | 10 | Companies whose business model generates outsized plastic pollution, packaging waste, or hazardous waste — single-use... |
| `water_resources` | Water Resources | 17 | Companies with documented abuse of water resources — excessive groundwater extraction, water source contamination, wa... |
### 3.5 Financial Crime and Market Abuse
*Conduct-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `anticompetitive` | Anticompetitive Practices | 34 | Anti-competitive practices: price-fixing, monopolistic behavior, or market manipulation |
| `corruption` | Corruption & Fraud | 61 | Documented corruption, bribery, or fraud in business operations or government dealings |
| `financial_misconduct` | Financial Misconduct | 175 | Predatory financial practices that harm consumers, investors, or beneficiaries — deceptive fee structures, insurance ... |
| `tax_avoidance` | Tax or Liability Avoidance | 8 | Corporate structure manipulation engineered to shed obligations to the public or harmed parties — tax inversions, spi... |
### 3.6 Consumer and Community Harm
*Conduct-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `community_harm` | Community Harm | 36 | Documented harm to specific communities from corporate operations — encompasses a wide range of localized impacts: to... |
| `legal_exploitation` | Legal System Exploitation | 1 | Business models whose core economic activity is exploiting legal structures, procedural chokepoints, or regulatory qu... |
| `predatory_business` | Extractive Business Models | 69 | Multi-level marketing structures, rent-seeking platforms, and business models that exploit customers, distributors, o... |
| `predatory_lending` | Extractive Lending | 12 | Companies whose core business or significant revenue line involves extending credit on exploitative terms — payday le... |
| `rent_seeking` | Rent-Seeking | 0 | Abuse of market power to extend dominance across adjacent markets or extract rents from captive counterparties. The v... |
### 3.7 Political Influence
*Conduct-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `political_influence` | Political Influence | 24 | Documented use of political donations, lobbying, or regulatory capture to shield harmful practices |
### 3.8 Information Integrity and Platform Accountability
*Product-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `data_privacy` | Data & Privacy | 28 | Companies whose business model involves deploying behavioral surveillance against their own users, customers, or subj... |
| `misinformation` | Misinformation & Disinformation | 18 | Systematic spread of false information, propaganda, or content designed to mislead or manipulate public understanding |
| `private_prisons` | For-Profit Prisons | 36 | Companies that own or operate for-profit prisons, immigration detention centers, or juvenile detention facilities, or... |
### 3.9 Regulatory and Governance Failures
*Conduct-Based Exclusions*

| Code | Name | Records | Description |
|------|------|---------|-------------|
| `multiple_violations` | Multiple Violations | 0 | Companies where documented misconduct spans multiple categories or where the formal exclusion grounds — typically gov... |
| `regulatory_failures` | Regulatory Violations | 52 | Companies with a documented pattern of regulatory violations across multiple domains — serial OSHA violations, repeat... |
<!-- TAXONOMY_END -->
