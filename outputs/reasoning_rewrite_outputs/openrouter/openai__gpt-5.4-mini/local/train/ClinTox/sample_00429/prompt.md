You are rewriting rough neighbor-based molecule-comparison notes from Explainable Boosting Machine (EBM) into high-quality reasoning SFT data for molecule local analog-comparison task ClinTox where option (A) means is not toxic and option (B) means is toxic.

Input 1. Task playbook
# ClinTox molecular-property playbook

ClinTox (as used in common benchmarks and mirrored in multiple ML datasets) is a **clinical-toxicity–relevant classification** built from a qualitative comparison of drugs **approved by the** entity["organization","U.S. Food and Drug Administration","federal agency, us"] and drugs that **failed / were terminated in clinical trials for toxicity-related reasons**. citeturn19view0 In this playbook, “A” corresponds to **not toxic** and “B” corresponds to **toxic**, with the important caveat that most molecular-property cutoffs come from **drug-likeness / ADMET / safety-risk proxy literature**, not from ClinTox-specific mechanistic rules. citeturn19view0turn36view0turn30view0

## Ionization and charge

\## neutral fraction
- Common threshold(s) or range(s): **no stable literature threshold found** (neutral fraction is typically interpreted indirectly via pKa + pH and its impact on logD/permeability/ion trapping). citeturn11search22turn31view0turn30view0  
- Usually associated with: **Lower neutral fraction for lipophilic bases** can align with lysosomal trapping/“cationic amphiphilic” behavior (often a safety red flag); **higher neutral fraction** can align with higher passive permeability and sometimes broader tissue exposure. citeturn11search22turn5search17turn30view0  
- Brief note: For ClinTox-adjacent practice, neutral fraction is mainly actionable when it reflects **basicity + lipophilicity** combinations known to increase certain liabilities (e.g., phospholipidosis, hERG risk via high logD for basic compounds). citeturn11search22turn31view0turn30view0  
- Source: Lysosomal trapping and CAD-style heuristics in medicinal chemistry/toxicology practice. citeturn11search22turn5search17turn31view0  

\## strongest acidic pKa
- Common threshold(s) or range(s): **no stable literature threshold found** for ClinTox-like toxicity classification.  
- Usually associated with: **Lower acidic pKa (stronger acids)** → more anionic fraction at physiological pH, often reduced passive permeability and lower intracellular accumulation (context-dependent). citeturn49view0turn44view0  
- Brief note: In practice, acidic pKa is mainly used to anticipate **ionization state and logD7.4**, which then ties into absorption and exposure (an indirect contributor to clinical safety outcomes). citeturn44view0turn30view0  
- Source: ADME absorption/permeability framing and property filters emphasizing lipophilicity/PSA rather than acidic pKa cutoffs. citeturn48view0turn44view0turn30view0  

\## strongest basic pKa
- Common threshold(s) or range(s): **pKa > ~6 with logP > ~1** is commonly cited as enabling lysosomal accumulation (ion trapping); **pKa > 7.4 with logP > 3** is widely used to define cationic amphiphilic drugs (CADs) in multiple analyses. citeturn11search22turn5search17  
- Usually associated with: **B (toxic) risk proxy increases** for **lipophilic bases** (lysosomotropism/CAD-like profiles), a known pattern behind phospholipidosis and other nonspecific cellular liabilities. citeturn11search22turn5search17turn30view0  
- Brief note: Basicity alone is not determinative; the *combination* with lipophilicity (logP/logD) is the practical “anchor” used in safety triage. citeturn11search22turn31view0turn30view0  
- Source: Lysosomal trapping and CAD definitions used in systems/toxicology analyses. citeturn11search22turn5search17  

\## number of acidic sites
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: More acidic sites often increases the chance of being **multiply charged** across pH ranges, generally reducing passive permeability (context-dependent). citeturn44view0turn49view0  
- Brief note: In clinical-toxicity proxy work, “ionizable-site counts” matter chiefly through downstream effects on **logD, PSA, and permeability**, not as standalone toxicity thresholds. citeturn30view0turn44view0  
- Source: Property-filter literature emphasizes permeability/PSA/lipophilicity over explicit ionizable-site-count cutoffs. citeturn49view0turn21view0turn30view0  

\## number of basic sites
- Common threshold(s) or range(s): **no stable literature threshold found** (counts are usually interpreted through net basicity/lysosomotropism rather than a fixed cutoff).  
- Usually associated with: Multiple basic centers can increase **cationic character** and, when paired with lipophilicity, can push toward lysosomal trapping/CAD-like risk. citeturn11search22turn5search17  
- Brief note: Practical screening focuses more on **most basic pKa** and **logP/logD** than on basic-site count alone. citeturn31view0turn11search22  
- Source: CAD/lysosomotropism heuristics in drug safety context. citeturn11search22turn5search17  

\## number of ionizable sites
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: Higher counts → broader charge-state distribution and often **higher polarity / lower permeability**, which can affect exposure and dose needs. citeturn49view0turn44view0  
- Brief note: For ClinTox-like outcomes, this is best treated as a *supporting* variable that helps interpret logD and permeability-related rules. citeturn30view0turn31view0  
- Source: Oral absorption / permeability heuristic frameworks. citeturn49view0turn48view0turn21view0  

\## maximum absolute partial charge
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: Larger absolute partial charges often correlate with **stronger polarity / H-bonding / ionic character**, which is typically handled via TPSA/HBD/HBA/logD rather than charge cutoffs. citeturn44view0turn49view0  
- Brief note: Partial-charge extrema are widely used as continuous ML/QSAR features, but practical medicinal-chemistry toxicity rules rarely specify hard cutoffs for them. citeturn19view0turn36view0  
- Source: General ADME/tox filtering emphasizes interpretable aggregates (TPSA, HBD/HBA, logP/logD). citeturn49view0turn44view0  

\## maximum partial charge
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: More positive maxima can occur in strongly basic/ionized motifs; practical risk rules are typically expressed via **pKa + logD/logP**, not charge maxima. citeturn11search22turn31view0  
- Brief note: Consider as supportive to ionization interpretation, not as an anchored cutoff.  
- Source: CAD/lysosomotropism and hERG-lipophilicity discussions focus on pKa/logD. citeturn11search22turn31view0turn5search17  

\## minimum absolute partial charge
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: Typically not used directly; interpret through overall polarity and H-bonding descriptors instead. citeturn44view0turn49view0  
- Brief note: Rarely appears as a human-interpretable threshold in safety triage.  
- Source: Property-filter literature focuses on PSA/logP/logD/HBD/HBA. citeturn49view0turn44view0  

\## minimum partial charge
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: More negative minima can reflect strong acceptors/acidic atoms; practical thresholds are expressed via **HBA/TPSA** and permeability models. citeturn44view0turn49view0  
- Brief note: Use mainly as a model feature, not a human cutoff.  
- Source: Oral absorption/property-filter frameworks. citeturn44view0turn48view0  

## Lipophilicity and distribution

\## estimated logD
- Common threshold(s) or range(s): **logD7.4 ~ 2 ± 1** is cited as a practical “center” for satisfying ADMET balance; **hERG risk anchors** have been estimated at ~**logD 3.3 (neutral)** for ~30% risk and as low as ~**logD 1.4 (basic)** for similar risk. citeturn30view0turn31view0  
- Usually associated with: **A (not toxic) proxy** when logD7.4 sits in a moderate zone (often ~1–3); **B (toxic) proxy** when markedly high for neutral compounds, or even moderate-high for basic compounds (hERG/accumulation concerns). citeturn31view0turn30view0  
- Brief note: logD is often more relevant than logP for ionizable molecules at physiological pH and is frequently used in early safety/permeability balancing. citeturn31view0turn49view0  
- Source: ADMET optimization guidance and hERG–lipophilicity risk quantification. citeturn30view0turn31view0  

\## estimated logP
- Common threshold(s) or range(s): **Rule-of-five anchor**: logP (cLogP) **> 5** is associated with poorer absorption/permeability likelihood; **toxicity-risk proxy**: **cLogP > 3** combined with **PSA < 75 Å²** was reported to give markedly higher odds of adverse findings in preclinical tox; **DILI proxy**: logP **≥ 3** is part of the commonly cited “Rule-of-2” when paired with high daily dose (external factor). citeturn20view0turn30view0turn26search4turn26search12  
- Usually associated with: **B (toxic) proxy** at higher lipophilicity (promiscuity, accumulation, clearance issues), especially when polarity is also low. citeturn30view0turn36view0turn26search12  
- Brief note: logP is a neutral-species property; for ionizable drugs, many screening stacks prefer logD7.4 for practical risk conversations. citeturn31view0turn49view0  
- Source: Rule-of-five (absorption proxy), Pfizer-origin safety-property analyses summarized in an open review, and DILI rule-of-two follow-on analysis. citeturn20view0turn30view0turn26search12turn26search4  

## Molecular size and surface area

\## exact molecular weight
- Common threshold(s) or range(s): **Rule-of-five anchor**: MW **> 500** suggests higher probability of poor absorption/permeability; **Ghose-style drug-like range** often quoted as **160–480** (library-design proxy). citeturn20view0turn49view0  
- Usually associated with: **B (toxic) proxy** at very high MW via developability/PK stress (solubility/permeability), which can indirectly increase clinical safety risk (dose/exposure complexities). citeturn49view0turn36view0  
- Brief note: ClinTox is about clinical toxicity outcomes; MW thresholds here are best treated as **attrition-risk proxies**, not toxicity mechanisms. citeturn19view0turn36view0  
- Source: Rule-of-five and classic drug-like filters. citeturn20view0turn49view0  

\## molecular weight
- Common threshold(s) or range(s): MW **≤ 500** (rule-of-five) remains the most widely used general anchor; Ghose-style **160–480** is a common “drug-like library” range. citeturn20view0turn49view0  
- Usually associated with: **A (not toxic) proxy** when MW stays in traditional oral-drug space (all else equal); **B (toxic) proxy** when large size combines with high lipophilicity/low polarity (exposure and off-target/liability risk). citeturn30view0turn20view0  
- Brief note: MW interacts strongly with other descriptors (logD/logP, TPSA, rotatable bonds), so single-number cutoffs should be used as coarse triage only. citeturn21view0turn30view0turn44view0  
- Source: Rule-of-five and absorption/permeability modeling literature. citeturn20view0turn21view0turn49view0  

\## heavy-atom count
- Common threshold(s) or range(s): **no stable literature threshold found** specific to “heavy atoms”; the closest widely cited proxy is the **Ghose ‘number of atoms’ range 20–70** (often used in library filtering). citeturn49view0  
- Usually associated with: Higher atom counts roughly track with higher MW/size; interpret via those established cutoffs rather than a separate heavy-atom rule. citeturn20view0turn49view0  
- Brief note: Many filters are expressed as MW rather than heavy-atom count because MW is more standard in medicinal chemistry decision-making. citeturn20view0turn21view0  
- Source: Ghose-style atom-count ranges summarized in classic absorption/drug-like filter discussions. citeturn49view0turn48view0  

\## heavy-atom molecular weight
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: Tracks overall MW; interpret using MW-based anchors (e.g., 500 rule-of-five) unless you have a specific modeling reason to separate heavy-atom contribution. citeturn20view0turn21view0  
- Brief note: Heavy-atom MW is uncommon as a standalone medicinal-chemistry heuristic for safety triage.  
- Source: Widely used practical filters emphasize MW, logP/logD, TPSA, HBD/HBA. citeturn20view0turn44view0turn31view0  

\## Labute surface area
- Common threshold(s) or range(s): **no stable literature threshold found** (as a named “Labute surface area” cutoff in safety/attrition practice).  
- Usually associated with: Broadly correlates with size and permeability; interpret using PSA/TPSA and MW/logD anchors instead. citeturn44view0turn21view0  
- Brief note: Surface-area concepts are most often operationalized via **PSA/TPSA** thresholds (e.g., 60/90/140 Å² anchors) rather than Labute SA. citeturn44view0turn48view0  
- Source: PSA/TPSA-based empirical cutoffs dominate practical design rules. citeturn44view0turn21view0turn48view0  

## Polarity and hydrogen bonding

\## topological polar surface area
- Common threshold(s) or range(s): Commonly used anchors include **TPSA/PSA ≤ 140 Å²** (oral permeability/bioavailability proxy), **PSA ≤ 60 Å²** for very high absorption in one classic analysis, and **~90 Å²** as an often-cited upper boundary for brain penetration; the Egan ellipse gave an upper PSA limit of **131.6 Å²** (95% ellipse) with an interacting lipophilicity boundary. citeturn44view0turn48view0turn21view0  
- Usually associated with: **A (not toxic) proxy** when PSA/TPSA is not extreme (supporting reasonable ADME); **B (toxic) proxy** indirectly when very high PSA/TPSA drives poor permeability/absorption that can stress dose/exposure margins. citeturn44view0turn36view0  
- Brief note: For ClinTox-style endpoints, TPSA is best treated as an **exposure/PK proxy** rather than a toxicity mechanism. citeturn19view0turn44view0  
- Source: Palm/Veber-style PSA cutoffs and Egan multivariate absorption model. citeturn44view0turn21view0turn48view0  

\## hydrogen-bond acceptor count
- Common threshold(s) or range(s): **HBA > 10** is the classic rule-of-five “risk” side; Veber-style heuristics also use total H-bonding capacity as a permeability proxy. citeturn20view0turn21view0  
- Usually associated with: **A (not toxic) proxy** when HBA stays in traditional oral-drug space; **B (toxic) proxy** indirectly when very high HBA contributes to high PSA and reduced permeability/absorption. citeturn21view0turn44view0  
- Brief note: Use alongside TPSA and logD; HBA is rarely used alone for toxicity calls. citeturn44view0turn31view0  
- Source: Rule-of-five and oral bioavailability analysis. citeturn20view0turn21view0  

\## hydrogen-bond donor count
- Common threshold(s) or range(s): **HBD > 5** is the rule-of-five “risk” boundary; Veber-style filters emphasize H-bonding burden via PSA or HBD+HBA totals. citeturn20view0turn21view0turn44view0  
- Usually associated with: **A (not toxic) proxy** when donor count is moderate; **B (toxic) proxy** indirectly when high HBD contributes to high polarity and poor permeability. citeturn21view0turn44view0  
- Brief note: High HBD can sometimes reduce nonspecific permeability-driven liabilities—but can also force higher doses if absorption suffers; context matters. citeturn44view0turn36view0  
- Source: Rule-of-five and Veber oral bioavailability criteria. citeturn20view0turn21view0  

\## NH/OH group count
- Common threshold(s) or range(s): Practically treated as a close proxy for HBD; **> 5 NH/OH donors** aligns with the rule-of-five “risk” side. citeturn20view0  
- Usually associated with: Same interpretation as HBD in most drug-likeness/tox triage stacks. citeturn20view0turn21view0  
- Brief note: Count-based heuristics ignore intramolecular H-bonding and conformation; PSA/logD often remains more predictive for permeability. citeturn30view0turn44view0  
- Source: Rule-of-five donor definition. citeturn20view0  

\## nitrogen/oxygen atom count
- Common threshold(s) or range(s): **no stable literature threshold found** as “N+O count”; the closest commonly used anchor is **HBA ≤ 10** in rule-of-five, often operationalized from heteroatoms (especially N and O). citeturn20view0  
- Usually associated with: Higher N/O count usually increases HBA/TPSA and lowers permeability; interpret via those established thresholds rather than raw N/O count. citeturn44view0turn21view0  
- Brief note: Use N/O count as a quick sanity check when HBA/TPSA are not directly available.  
- Source: Rule-of-five acceptor framing and PSA/TPSA cutoffs. citeturn20view0turn44view0  

\## heteroatom count
- Common threshold(s) or range(s): **no stable literature threshold found** (as a standalone heteroatom-count cutoff for clinical toxicity).  
- Usually associated with: Higher heteroatom counts often increase polarity/H-bonding and may reduce permeability; interpret via TPSA/HBA/HBD instead. citeturn44view0turn49view0  
- Brief note: Some library filters use atom-count style ranges (e.g., 20–70 total atoms), but this is broader than heteroatom counts. citeturn49view0  
- Source: Drug-like filter families rely on MW/logP/TPSA/HBD/HBA more than heteroatom count alone. citeturn49view0turn20view0turn21view0  

## Rings, aromaticity, and flexibility

\## fraction of sp3 carbons
- Common threshold(s) or range(s): **no stable literature threshold found** (published guidance is primarily directional: “increase saturation / 3D character”). citeturn41search6  
- Usually associated with: Higher Fsp3 (more saturation/3D) is reported to correlate with improved progression/success in retrospective analyses; as a proxy, this can align with reduced promiscuity-driven liabilities. citeturn41search6turn36view0  
- Brief note: Use as a *design direction* rather than a hard filter for ClinTox. citeturn41search6turn19view0  
- Source: “Escape from flatland” concept and clinical-success correlations. citeturn41search6  

\## rotatable-bond count
- Common threshold(s) or range(s): **≤ 10 rotatable bonds** is a widely used oral bioavailability proxy criterion; CNS-focused summaries often cite **~5 or fewer** as typical for many CNS drugs. citeturn21view0turn5search18  
- Usually associated with: **A (not toxic) proxy** when flexibility is moderate (supports predictable ADME); **B (toxic) proxy** indirectly when high flexibility accompanies high MW/polarity and worsens permeability or metabolic risk. citeturn21view0turn30view0turn36view0  
- Brief note: RotB is best used with TPSA (Veber-style) and MW/logD balancing frameworks. citeturn21view0turn44view0turn30view0  
- Source: Veber oral bioavailability criteria and CNS property summaries. citeturn21view0turn5search18  

\## aliphatic carbocycle count
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: Generally less problematic than adding additional aromatic rings; effects are context-dependent and mediated by lipophilicity/shape. citeturn12search1turn12search16  
- Brief note: Ring-type–specific guidance is more qualitative than numeric; aromatic ring count has the clearest hard-ish anchor. citeturn12search16turn12search1  
- Source: Ring-type developability discussions. citeturn12search1  

\## aliphatic heterocycle count
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: Often treated as potentially beneficial vs adding carboaromatic rings (context-dependent). citeturn12search1  
- Brief note: Practical cutoffs usually focus on *total aromatic rings* rather than aliphatic heterocycle counts. citeturn12search16  
- Source: Ring-type developability analyses. citeturn12search1  

\## aliphatic ring count
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: Interpret mainly via its influence on lipophilicity and 3D shape; no widely used numeric cutoff. citeturn12search1turn30view0  
- Brief note: Use with MW/logD and aromatic-ring-count guidance rather than alone. citeturn12search16turn30view0  
- Source: Developability ring-type discussions and lipophilicity-risk context. citeturn12search1turn30view0  

\## aromatic carbocycle count
- Common threshold(s) or range(s): **no stable standalone threshold found**; practical guidance is usually expressed in terms of **total aromatic ring count**. citeturn12search16  
- Usually associated with: More carboaromatic rings are described as particularly detrimental for developability vs other ring types in comparative analyses. citeturn12search1  
- Brief note: If you need a practical rule, use total aromatic ring count (see “aromatic ring count”). citeturn12search16  
- Source: Ring-count developability analysis. citeturn12search1turn12search16  

\## aromatic heterocycle count
- Common threshold(s) or range(s): **no stable standalone threshold found**; consider within total aromatic ring count. citeturn12search16  
- Usually associated with: Heteroaromatics are generally less detrimental than carboaromatics but still trend negative as aromatic ring burden increases. citeturn12search1turn12search16  
- Brief note: Heteroaromatics can raise TPSA/HBA, partially offsetting pure lipophilicity—but may introduce metabolic alerts depending on motif. citeturn44view0turn38search1  
- Source: Ring-type developability analysis and structural-alert context for heteroaromatics. citeturn12search1turn38search1  

\## aromatic ring count
- Common threshold(s) or range(s): **> 3 aromatic rings** is explicitly reported to correlate with poorer developability and higher attrition risk (a common medicinal-chemistry mnemonic). citeturn12search16  
- Usually associated with: **B (toxic) proxy** insofar as high aromatic ring count tracks with worse solubility, higher lipophilicity, CYP/hERG liabilities, and broader attrition. citeturn12search16turn30view0turn31view0  
- Brief note: This is one of the few “count” descriptors with a widely repeated practical anchor; treat it as a coarse screen, not a mechanistic toxicity rule. citeturn12search16turn19view0  
- Source: Aromatic ring count developability review and follow-on analyses. citeturn12search16turn12search1  

\## saturated carbocycle count
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: Often less detrimental than aromatic rings for developability; depends on how it shifts logP/logD and shape. citeturn12search1turn30view0  
- Brief note: Consider alongside fraction sp3 and aromatic ring count. citeturn41search6turn12search16  
- Source: Ring-type developability discussion. citeturn12search1  

\## saturated heterocycle count
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: Qualitatively, heteroaliphatic rings were reported as beneficial in many cases in ring-type analyses (context-dependent). citeturn12search1  
- Brief note: No hard cutoff; interpret via logD, TPSA, and aromatic ring burden. citeturn30view0turn44view0turn12search16  
- Source: Ring-type developability analysis. citeturn12search1  

\## saturated ring count
- Common threshold(s) or range(s): **no stable literature threshold found**.  
- Usually associated with: Often a proxy for “less aromatic/less flat,” which can be favorable, but no stable numeric rule is used. citeturn41search6turn12search16  
- Brief note: Use the aromatic ring count >3 anchor as the practical ring-count screen. citeturn12search16  
- Source: Flatland/aromatic-ring developability literature. citeturn41search6turn12search16  

\## ring count
- Common threshold(s) or range(s): **no stable literature threshold found** for total rings in ClinTox-like contexts; some screening heuristics exist in library filtering but are not ClinTox-specific. citeturn15view0  
- Usually associated with: Interpret ring count through **aromatic ring count**, ring fusion, and resulting lipophilicity/shape rather than a single total-ring cutoff. citeturn12search16turn12search1turn30view0  
- Brief note: If you need a rapid human rule, aromatic ring count provides a stronger signal than total ring count. citeturn12search16  
- Source: Library filtering discussions and aromatic ring count developability work. citeturn15view0turn12search16  

## Composite drug-likeness

\## QED drug-likeness
- Common threshold(s) or range(s): QED is defined on **0–1** as a **ranking** measure (not inherently a hard cutoff); in practical computational filtering workflows, cutoffs like **QED ≥ 0.6** are sometimes used as a “more drug-like” gate (task- and workflow-dependent). citeturn17search6turn17search15  
- Usually associated with: **A (not toxic) proxy** when QED is moderate-to-high (captures balanced property profiles similar to many oral drugs); **B (toxic) proxy** when very low QED reflects multiple property extremes tied to attrition risk. citeturn17search6turn36view0  
- Brief note: Because ClinTox compares approved vs toxicity-failed clinical-trial drugs, QED is best used as a **broad “compound quality” proxy**, not a toxicity mechanism. citeturn19view0turn17search6  
- Source: Original QED formulation and examples of QED cutoffs in practice. citeturn17search6turn17search15  

## Functional-group notes

- Group name: **Aryl amines / anilines / anilides**
- Usually associated with: Often treated as a **structural alert** class in idiosyncratic toxicity/reactive-metabolite discussions (risk is conditional, not absolute). citeturn8search5turn36view0  
- Brief note: Aryl amines can undergo bioactivation to reactive intermediates; presence alone is not determinative, but it is repeatedly flagged in drug-safety retrospectives. citeturn8search5turn36view0  
- Source: Structural alert / reactive metabolite perspective reviews. citeturn8search5turn36view0  

- Group name: **Nitro (especially nitroaromatics)**
- Usually associated with: Frequently categorized as a **structural alert** due to well-known toxicity concerns (context-dependent; some approved drugs contain nitro). citeturn7search2turn38search1  
- Brief note: Nitro groups are widely discussed as having toxicity liabilities and are commonly flagged during early design unless strongly justified. citeturn7search2turn38search1  
- Source: Nitro-group drug review and structural-alert literature. citeturn7search2turn38search1  

- Group name: **Thiophenes and furans (bioactivation-prone heteroaromatics)**
- Usually associated with: Treated as **structural alerts** in the context of potential metabolic bioactivation to reactive metabolites (risk depends on substitution, metabolism, dose). citeturn38search1turn36view0  
- Brief note: These motifs are often handled with “design-around” tactics or additional RM screening rather than immediate exclusion. citeturn38search1turn36view0  
- Source: Review focused on furans/thiophenes as alerts and broader structural-alert guidance. citeturn38search1turn36view0  

- Group name: **α,β-Unsaturated carbonyls (Michael acceptors)**
- Usually associated with: Potential **covalent reactivity** with biological nucleophiles; often flagged as higher hazard potential depending on reactivity and exposure. citeturn38search3turn36view0  
- Brief note: Medicinal chemistry practice distinguishes “tuned” covalent warheads from promiscuous electrophiles; nevertheless, Michael acceptors are a recurring structural-alert class. citeturn38search3turn36view0  
- Source: Michael acceptor reactivity perspective and structural-alert/toxicity reviews. citeturn38search3turn36view0  

- Group name: **Carboxylic acids with acyl glucuronide risk**
- Usually associated with: Potential idiosyncratic toxicity risk via **reactive acyl glucuronide metabolites** (not universal; risk depends on stability/reactivity and clinical context). citeturn8search3turn36view0  
- Brief note: Carboxylic acids are common and often safe, but acyl glucuronide reactivity is a well-discussed safety consideration in specific series. citeturn8search3turn36view0  
- Source: Acyl glucuronide safety review. citeturn8search3  

- Group name: **Cationic amphiphilic motif (lipophilic scaffold + basic amine, often tertiary)**
- Usually associated with: Lysosomotropism / phospholipidosis-style liabilities; commonly proxied by **pKa > ~6** plus **logP > ~1** and, in stricter CAD definitions, **logP > 3 and pKa > 7.4**. citeturn11search22turn5search17turn30view0  
- Brief note: This is a “pattern” rather than a single functional group; it becomes especially salient when logD is high for basic compounds (hERG and other nonspecific risks). citeturn31view0turn11search22  
- Source: Lysosomal trapping and CAD definitions used in published analyses. citeturn11search22turn5search17

Input 2. Neighbor similarities and per-neighbor comparison notes
"""
Neighbors that is toxic:
Neighbor 1: 
Similarity: 0.171
Comparison note: First, The neighbor does not have ammonium, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is -1.5774, which pushes toward option (A): is not toxic. Next, For nitrogen/oxygen atom count, the neighbor's nitrogen/oxygen atom count is value 4, while the query's nitrogen/oxygen atom count is value 4. The query-minus-neighbor delta is +0. This pairwise contribution is -0.4789, which pushes toward option (A): is not toxic. Then, For hydrogen-bond acceptor count, the neighbor's hydrogen-bond acceptor count is value 3, while the query's hydrogen-bond acceptor count is value 2. The query-minus-neighbor delta is -1. This pairwise contribution is -0.4554, which pushes toward option (A): is not toxic. After that, The neighbor does not have secondary hydroxyl, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is -0.279, which pushes toward option (A): is not toxic. Finally, For minimum absolute partial charge, the neighbor's minimum absolute partial charge is value 0.339, while the query's minimum absolute partial charge is value 0.1365. The query-minus-neighbor delta is -0.2025. This pairwise contribution is -0.2233, which pushes toward option (A): is not toxic. Step 6, For estimated logP, the neighbor's estimated logP is value 1.3101, while the query's estimated logP is value 0.8794. The query-minus-neighbor delta is -0.4307. This pairwise contribution is 0.2087, which pushes toward option (B): is toxic. Taken together, this positive-neighbor comparison pushes toward option (A): is not toxic with pair score 0.0002.
Neighbor 2: 
Similarity: 0.156
Comparison note: First, The neighbor does not have ammonium, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is -1.5774, which pushes toward option (A): is not toxic. Next, For hydrogen-bond acceptor count, the neighbor's hydrogen-bond acceptor count is value 3, while the query's hydrogen-bond acceptor count is value 2. The query-minus-neighbor delta is -1. This pairwise contribution is -0.4554, which pushes toward option (A): is not toxic. Then, For minimum absolute partial charge, the neighbor's minimum absolute partial charge is value 0.2669, while the query's minimum absolute partial charge is value 0.1365. The query-minus-neighbor delta is -0.1303. This pairwise contribution is -0.2797, which pushes toward option (A): is not toxic. After that, The neighbor does not have secondary hydroxyl, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is -0.279, which pushes toward option (A): is not toxic. Finally, The neighbor does not have alkyl aryl ether, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 0.198, which pushes toward option (B): is toxic. Step 6, For maximum partial charge, the neighbor's maximum partial charge is value 0.2669, while the query's maximum partial charge is value 0.1365. The query-minus-neighbor delta is -0.1303. This pairwise contribution is -0.1449, which pushes toward option (A): is not toxic. Taken together, this positive-neighbor comparison pushes toward option (A): is not toxic with pair score 0.0005.
Neighbor 3: 
Similarity: 0.154
Comparison note: First, The neighbor does not have ammonium, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is -1.5774, which pushes toward option (A): is not toxic. Next, For minimum partial charge, the neighbor's minimum partial charge is value -0.508, while the query's minimum partial charge is value -0.4899. The query-minus-neighbor delta is +0.018. This pairwise contribution is 0.9236, which pushes toward option (B): is toxic. Then, For estimated logP, the neighbor's estimated logP is value -3.1057, while the query's estimated logP is value 0.8794. The query-minus-neighbor delta is +3.9851. This pairwise contribution is 0.7717, which pushes toward option (B): is toxic. After that, The neighbor has lactam, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is -0.7097, which pushes toward option (A): is not toxic. Finally, The neighbor has semicarbazide, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is -0.3598, which pushes toward option (A): is not toxic. Step 6, For hydrogen-bond acceptor count, the neighbor's hydrogen-bond acceptor count is value 16, while the query's hydrogen-bond acceptor count is value 2. The query-minus-neighbor delta is -14. This pairwise contribution is -0.29, which pushes toward option (A): is not toxic. Taken together, this positive-neighbor comparison pushes toward option (A): is not toxic with pair score 0.0008.

Neighbors that is not toxic
Neighbor 4: 
Similarity: 0.539
Comparison note: First, Both the neighbor and the query have ammonium (query-minus-neighbor delta +0). This pairwise contribution is -1.3725, which pushes toward option (A): is not toxic. Next, For hydrogen-bond acceptor count, the neighbor's hydrogen-bond acceptor count is value 3, while the query's hydrogen-bond acceptor count is value 2. The query-minus-neighbor delta is -1. This pairwise contribution is -0.5916, which pushes toward option (A): is not toxic. Then, For strongest acidic pKa, the neighbor's strongest acidic pKa is value 13.844, while the query's strongest acidic pKa is value 13.8683. The query-minus-neighbor delta is +0.0243. This pairwise contribution is 0.3202, which pushes toward option (B): is toxic. After that, For maximum absolute partial charge, the neighbor's maximum absolute partial charge is value 0.4868, while the query's maximum absolute partial charge is value 0.4899. The query-minus-neighbor delta is +0.0032. This pairwise contribution is 0.3109, which pushes toward option (B): is toxic. Finally, For maximum partial charge, the neighbor's maximum partial charge is value 0.1611, while the query's maximum partial charge is value 0.1365. The query-minus-neighbor delta is -0.0246. This pairwise contribution is -0.1977, which pushes toward option (A): is not toxic. Step 6, For minimum absolute partial charge, the neighbor's minimum absolute partial charge is value 0.1611, while the query's minimum absolute partial charge is value 0.1365. The query-minus-neighbor delta is -0.0246. This pairwise contribution is -0.1739, which pushes toward option (A): is not toxic. Taken together, this negative-neighbor comparison pushes toward option (A): is not toxic with pair score 0.001.
Neighbor 5: 
Similarity: 0.430
Comparison note: First, Both the neighbor and the query have ammonium (query-minus-neighbor delta +0). This pairwise contribution is -1.3725, which pushes toward option (A): is not toxic. Next, For hydrogen-bond acceptor count, the neighbor's hydrogen-bond acceptor count is value 3, while the query's hydrogen-bond acceptor count is value 2. The query-minus-neighbor delta is -1. This pairwise contribution is -0.5916, which pushes toward option (A): is not toxic. Then, For strongest acidic pKa, the neighbor's strongest acidic pKa is value 13.8779, while the query's strongest acidic pKa is value 13.8683. The query-minus-neighbor delta is -0.0096. This pairwise contribution is 0.3117, which pushes toward option (B): is toxic. After that, For maximum absolute partial charge, the neighbor's maximum absolute partial charge is value 0.4907, while the query's maximum absolute partial charge is value 0.4899. The query-minus-neighbor delta is -0.0007. This pairwise contribution is 0.2411, which pushes toward option (B): is toxic. Finally, For hydrogen-bond donor count, the neighbor's hydrogen-bond donor count is value 2, while the query's hydrogen-bond donor count is value 3. The query-minus-neighbor delta is +1. This pairwise contribution is 0.148, which pushes toward option (B): is toxic. Step 6, For maximum partial charge, the neighbor's maximum partial charge is value 0.1365, while the query's maximum partial charge is value 0.1365. The query-minus-neighbor delta is +0. This pairwise contribution is -0.1313, which pushes toward option (A): is not toxic. Taken together, this negative-neighbor comparison pushes toward option (A): is not toxic with pair score 0.0013.
Neighbor 6: 
Similarity: 0.426
Comparison note: First, Both the neighbor and the query have ammonium (query-minus-neighbor delta +0). This pairwise contribution is -1.3725, which pushes toward option (A): is not toxic. Next, For minimum absolute partial charge, the neighbor's minimum absolute partial charge is value 0.3075, while the query's minimum absolute partial charge is value 0.1365. The query-minus-neighbor delta is -0.171. This pairwise contribution is -0.4876, which pushes toward option (A): is not toxic. Then, For hydrogen-bond acceptor count, the neighbor's hydrogen-bond acceptor count is value 4, while the query's hydrogen-bond acceptor count is value 2. The query-minus-neighbor delta is -2. This pairwise contribution is -0.4663, which pushes toward option (A): is not toxic. After that, For strongest acidic pKa, the neighbor's strongest acidic pKa is value 13.8358, while the query's strongest acidic pKa is value 13.8683. The query-minus-neighbor delta is +0.0325. This pairwise contribution is 0.3148, which pushes toward option (B): is toxic. Finally, For maximum absolute partial charge, the neighbor's maximum absolute partial charge is value 0.4903, while the query's maximum absolute partial charge is value 0.4899. The query-minus-neighbor delta is -0.0004. This pairwise contribution is 0.2326, which pushes toward option (B): is toxic. Step 6, For hydrogen-bond donor count, the neighbor's hydrogen-bond donor count is value 2, while the query's hydrogen-bond donor count is value 3. The query-minus-neighbor delta is +1. This pairwise contribution is 0.148, which pushes toward option (B): is toxic. Taken together, this negative-neighbor comparison pushes toward option (A): is not toxic with pair score 0.001.
"""

Input 3. Final prediction label
option (A): is not toxic

Hard requirements:
1. Use only the task playbook, the listed neighbor similarities, the per-neighbor comparison notes, and the provided final prediction label.
2. The final `reasoning` must explicitly mention all six neighbors by name: `Neighbor 1`, `Neighbor 2`, `Neighbor 3`, `Neighbor 4`, `Neighbor 5`, and `Neighbor 6`.
3. Do not silently drop, merge away, renumber, or miscount neighbors. There are exactly 6 neighbors: 3 positive neighbors and 3 negative neighbors.
4. Keep positive-neighbor and negative-neighbor evidence distinct in the reasoning.
5. For each neighbor, only describe evidence that appears in that neighbor's supplied comparison note. Do not introduce any new descriptor, property, trend, or comparison for that neighbor.
6. For each neighbor, do not skip any feature that appears in that neighbor's supplied comparison note. Every source-note feature must still be covered somewhere in the rewrite for that neighbor.
7. You do not need to give the same level of detail to every feature. Major features can be expanded with fuller raw-value discussion, while secondary features may be covered more briefly as long as they are not omitted.
8. Use enough concrete `neighbor`, `query`, and `delta` values to anchor the reasoning, but do not turn the paragraph into a rigid value-by-value inventory.
9. You may rewrite naturally, and you may use qualitative trend words such as "higher", "lower", "increased", "decreased", "favorable", or "unfavorable", but when a feature is important to the argument, keep its original concrete `neighbor`, `query`, and `delta` values alongside the interpretation rather than replacing them with vague wording.
10. Each neighbor paragraph must still explain why that comparison overall helps or hurts the current label decision. Raw values should support the explanation, not crowd it out.
11. Do not reduce a neighbor paragraph to value listing. Cover all source-note features, but let less important ones be mentioned more compactly so the prose remains natural.
12. If a supplied comparison note uses explicit non-numeric value semantics such as `not applicable`, `no acidic site`, `no basic site`, or `delta not defined`, preserve those concrete value semantics rather than dropping them when they matter to the argument.
13. Do not infer whole-molecule properties that were not explicitly stated in the supplied neighbor notes. Stay close to the source content.
14. Treat each neighbor comparison as context-dependent analog evidence, not as a universal rule about the descriptor.
15. When you explain a descriptor, anchor the explanation to that neighbor's starting value or range and the specific query-minus-neighbor change described in the draft.
16. If the same descriptor appears in multiple neighbors with different directional effects, preserve those neighbor-specific effects. Do not force them into one monotonic or global trend.
17. Do not rewrite a descriptor as if "higher is always better" or "lower is always worse" across all neighbors unless that exact monotonic rule is explicitly supported by the supplied comparison note for that neighbor.
18. Use the playbook only to explain why a value region or direction can matter chemically. The playbook must never override the directional effect already stated in a neighbor note.
19. If the playbook describes a descriptor in terms of ranges, windows, thresholds, or non-monotonic behavior, preserve that range-based interpretation in the rewrite. Do not flatten a range-based rule into a simple monotonic claim.
20. If a descriptor effect depends on baseline context, make that dependence clear, but you do not need to force repetitive phrases such as "in this comparison" or "at this baseline" into every sentence.
21. When relevant, connect the neighbor's raw value to the playbook's described value region or interval before explaining why the observed delta helps or hurts in that specific comparison.
22. After covering all 6 neighbors, explain how the six neighbor-level comparisons combine into one final prediction.
23. Make sure the final prediction matches the provided label.
24. Do not invent new neighbors, new similarities, new molecular evidence, or new experimental facts.
25. Do not mention model internals, pairwise EBM, aggregation code, prompt instructions, or hidden reasoning process.
26. Keep the final reasoning faithful to the original draft direction while making the prose more natural, coherent, and scientist-like.
27. The final `reasoning` must read like direct scientific reasoning, not commentary about source materials. **Do not** say "draft", "note", "playbook", "prompt", "input", "instruction", "contribution", "pair score", or similar metadata words in the final text.
28. Do not write phrases such as "in this draft", "in this note", "the playbook says", "the prompt provides", or "this contribution pushes toward". Translate those ideas into direct chemistry reasoning instead.

Preferred style:
- Explicit, stepwise, chemically grounded
- Natural scientific prose
- Specific but not robotic
- More like thoughtful analysis than formal rule execution
- No bullet points in the final CoT
- Baseline-aware and context-aware rather than globally monotonic
- Prefer interval-aware explanations when the playbook gives range-dependent guidance
- Cover all source-note features, but let secondary ones be handled more briefly than the major ones
- Let the prose flow naturally instead of forcing the same sentence template for every feature
- A good structure is:
  Start by describing `Neighbor 1` to `Neighbor 3` one by one.
  Then discuss `Neighbor 4` to `Neighbor 6` one by one.
  Then end with a short synthesis paragraph that integrates all six neighbors into the final prediction.

Return JSON with exactly this schema:
```json
{
  "reasoning": "...",
  "quality_check": {
    "covers_all_neighbors": true or false,
    "distinguishes_pos_neg_neighbors": true or false,
    "final_prediction_matches_provided_label": true or false,
    "no_neighbor_hallucination": true or false
  }
}
```
