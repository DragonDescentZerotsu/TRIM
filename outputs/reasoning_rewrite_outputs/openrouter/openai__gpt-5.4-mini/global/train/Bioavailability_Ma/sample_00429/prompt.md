You are rewriting rough single-molecule analysis notes from Explainable Boosting Machine (EBM) into high-quality reasoning SFT data for task Bioavailability_Ma where option (A) means has oral bioavailability < 20% and option (B) means has oral bioavailability ≥ 20%.

Input 1. Task playbook
# Bioavailability ≥20% Playbook for Bioavailability_Ma

The Bioavailability_Ma task is a binary label on oral bioavailability, where **(A)** indicates oral bioavailability **< 20%** and **(B)** indicates oral bioavailability **≥ 20%**. The **≥20% cutoff** aligns with a commonly used “acceptable oral bioavailability” threshold used in classic oral bioavailability analyses (notably in rat data), and similar property heuristics are often reused as practical anchors even when the underlying dataset is human-focused. citeturn46search0turn12search2turn14view2

Most **practical cutoffs in medicinal chemistry are stated for oral absorption / permeability / developability** (close proxies for oral bioavailability, since bioavailability also includes first-pass metabolism and transporter effects). That means many properties below have **robust “rule-of-thumb” thresholds** (e.g., MW, TPSA, HBD/HBA, rotatable bonds, lipophilicity), while others are **mostly ML features without stable community cutoffs**. citeturn14view0turn16view2turn18view0turn53view0turn49view2

## Ionization and charge state anchors

\## neutral fraction: estimated fraction of the molecule that is neutral at the configured pH  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: **higher oral bioavailability** when there is a **non-negligible neutral population** at intestinal/physiologic pH (supports passive permeability); extremely low neutral fraction often implies **lower passive absorption** (with notable exceptions via transporters or ion-pairing)  
- Brief note: Many practical rules treat **ionization indirectly** via logD (pH-dependent) or combined metrics that explicitly include neutral fraction. citeturn26view0  
- Source: pH-dependent logD and explicit neutral-fraction use in oral drug-likeness metrics. citeturn26view0  

\## strongest acidic pKa: pKa of the strongest acidic site  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: **lower oral bioavailability** when the strongest acidic site drives the compound to be **predominantly anionic at intestinal/physiologic pH** (passive permeability risk); potential **higher bioavailability** when acidity is balanced so the compound retains some neutral fraction at relevant pH  
- Brief note: Practical interpretation nearly always applies **Henderson–Hasselbalch** logic (ionization governed by pH vs pKa), but published “single-number pKa cutoffs” for oral bioavailability are not stable across chemotypes. citeturn23search0turn25search11turn26view0  
- Source: pH–pKa governs ionization (50% ionized at pH = pKa); oral drug rules emphasize property balance rather than a single pKa cutoff. citeturn25search11turn49view2turn26view0  

\## strongest basic pKa: pKa of the strongest basic site  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: **lower oral bioavailability** when very high basicity implies **predominantly cationic** species at intestinal/physiologic pH (passive permeability risk), though ionized bases can still be orally successful depending on solubility and transporter effects  
- Brief note: Medicinal chemistry practice typically manages base strength via **logD@pH** and polarity/size constraints rather than a universal “pKa must be <X” rule for oral bioavailability. citeturn26view0turn53view0  
- Source: oral bioavailability is multi-factorial; widely used heuristics focus on lipophilicity, PSA, MW, HBD/HBA, rotatable bonds rather than a universal basic pKa cutoff. citeturn14view0turn53view0turn49view2  

\## number of acidic sites: number of acidic ionizable sites in the molecule  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: **lower oral bioavailability** when multiple acidic sites increase the probability of **multi-anionic character** at intestinal pH (permeability risk); can also increase solubility (sometimes offsetting permeability)  
- Brief note: Community rules typically constrain **net polarity** (TPSA, HBD/HBA) and **lipophilicity at pH** rather than the raw count of acidic sites. citeturn14view0turn16view2turn18view0  
- Source: common oral bioavailability heuristics and absorption models center on lipophilicity/polarity/flexibility rather than explicit acidic-site counts. citeturn14view0turn16view2turn18view0  

\## number of basic sites: number of basic ionizable sites in the molecule  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: **lower oral bioavailability** when multiple basic sites increase **polycationic** character (passive permeability risk) and may increase efflux liability; can increase aqueous solubility  
- Brief note: Practical guidance tends to appear as **logD@pH windows** and polarity constraints, which implicitly penalize highly ionized multi-basic molecules. citeturn26view0turn53view0  
- Source: lipophilicity-at-pH and property balance frameworks used for oral candidates. citeturn26view0turn53view0  

\## number of ionizable sites: total number of acidic and basic ionizable sites  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: **lower oral bioavailability** as ionizable-site count increases (greater chance of high polarity / multiple charge states), unless compensated by scaffold/lipophilicity and/or transporter-mediated uptake  
- Brief note: In practice, this is treated as a **driver variable** that manifests through TPSA/HBD/HBA/logD rather than a directly thresholded property. citeturn14view0turn16view2turn26view0  
- Source: dominant oral rules emphasize TPSA, HBD/HBA, MW, logP/logD, rotatable bonds. citeturn14view0turn16view2turn18view0turn53view0  

## Lipophilicity and partitioning anchors

\## estimated logD: estimated logD at the configured pH  
- Common threshold(s) or range(s):  
  - **logD (physiological pH) ≈ 1–3** often cited as an “optimal” region for oral drug-like space citeturn1search0turn26view0  
  - **logD at pH 6.5 in −2 to 3** reported (retrospectively) as associated with increased bioavailability in one analysis citeturn26view0  
  - **Golden Triangle (MW, logD7.4)**: an “optimal region” bounded approximately by **elogD ~ −2 to 5** with **MW ~200–500** (as a joint rule for permeability + metabolic stability) citeturn53view0  
- Usually associated with: **lower oral bioavailability** at very low logD (insufficient membrane affinity) or very high logD (solubility and/or clearance liabilities); **higher oral bioavailability** in the middle “sweet spot” (context-dependent) citeturn26view0turn53view0  
- Brief note: The literature is **not fully consistent** because the best logD depends on **MW, ionization, and whether failure mode is solubility vs permeability vs first-pass**. Weight-dependent logD lower limits for high permeability have been proposed (higher MW needing higher logD). citeturn26view0turn53view0  
- Source: lipophilicity windows and Golden Triangle depiction; weight-dependent logD discussion. citeturn1search0turn26view0turn53view0  

\## estimated logP: RDKit-estimated octanol/water partition coefficient (logP)  
- Common threshold(s) or range(s):  
  - **Rule of Five**: poor absorption/permeation more likely when **logP > 5** citeturn18view0  
  - **Ghose filter (drug-likeness)**: qualifying range **logP −0.4 to 5.6** citeturn2search2  
- Usually associated with: **lower oral bioavailability** when logP is very high (solubility/clearance liabilities) or very low (insufficient membrane partitioning), though bioavailability outcomes are strongly context- and formulation-dependent citeturn18view0turn26view0  
- Brief note: logP is **intrinsic** lipophilicity (neutral form), while permeability for ionizable drugs is often better reflected by **logD at relevant pH**. citeturn26view0  
- Source: Ro5 and Ghose property ranges; emphasis on logD for ionizable drugs. citeturn18view0turn2search2turn26view0  

## Size, flexibility, and scaffold complexity anchors

\## exact molecular weight: exact isotopic molecular weight  
- Common threshold(s) or range(s):  
  - **Rule of Five**: poor absorption/permeation more likely when **MW > 500** citeturn18view0  
  - **Ghose filter**: **MW 160–480** as a drug-likeness qualifying range citeturn2search2  
  - **Golden Triangle (joint rule)** depicts an “optimal” region with **MW roughly 200–500** (paired with logD7.4) citeturn53view0  
- Usually associated with: **lower oral bioavailability** at higher MW (more likely solubility/permeability challenges and clearance liabilities), but many oral drugs do exceed 500 Da (beyond-Ro5 space) citeturn53view0turn26view0  
- Brief note: A key caution from classic analyses is that an MW cutoff (e.g., 500) may **not cleanly separate** good vs poor oral bioavailability on its own (property balance dominates). citeturn14view0turn53view0  
- Source: Ro5 MW=500; Ghose MW range; Veber discussion of MW cutoff limitations; Golden Triangle. citeturn18view0turn2search2turn14view0turn53view0  

\## molecular weight: molecular weight  
- Common threshold(s) or range(s): same commonly used anchors as “exact molecular weight” (MW > 500 risk in Ro5; 160–480 in Ghose; Golden Triangle joint region around 200–500) citeturn18view0turn2search2turn53view0  
- Usually associated with: **higher oral bioavailability** when MW is controlled (especially in the Ro5-like space), and **lower oral bioavailability** risk rises with MW unless compensated by other properties and/or formulation/transport mechanisms citeturn26view0turn53view0  
- Brief note: Treat MW as a **global risk amplifier**, not a strict pass/fail, because first-pass and other mechanisms can dominate oral bioavailability. citeturn53view0turn49view2  
- Source: Ro5 + multi-parameter decision framing. citeturn18view0turn53view0turn49view2  

\## heavy-atom count: number of non-hydrogen atoms  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: **similar directionality as MW** (higher heavy-atom count usually implies higher size/polar surface burden and higher oral bioavailability risk), but not used as a primary medicinal chemistry cutoff for oral bioavailability  
- Brief note: Practical filters are typically expressed directly in **MW/logP/logD/TPSA/HBD/HBA/rotatable bonds**, which are more interpretable and historically standardized. citeturn18view0turn14view0turn16view2turn53view0  
- Source: canonical oral bioavailability heuristics do not threshold heavy-atom count explicitly. citeturn18view0turn14view0turn16view2turn53view0  

\## heavy-atom molecular weight: molecular weight contributed by heavy atoms  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: broadly tracks MW (higher values often raise oral bioavailability risk), but not a standard decision cutoff in medicinal chemistry  
- Brief note: Use as a **size proxy** when MW is not otherwise available; community thresholds are typically stated on total MW. citeturn18view0turn53view0  
- Source: standard oral drug heuristics use MW rather than heavy-atom MW. citeturn18view0turn53view0  

\## fraction of sp3 carbons: fraction of carbon atoms that are sp3 hybridized  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: **higher oral developability / progression probability** (and often better solubility) when fraction sp3 is higher, as a proxy for increased 3D character; association is not a strict oral bioavailability cutoff citeturn35view0turn31view0  
- Brief note: Reported dataset-level trend: average Fsp3 ~**0.36** for discovery compounds increasing toward ~**0.47** for approved drugs (an empirical “directional anchor,” not a pass/fail rule). citeturn35view0turn31view0  
- Source: literature summaries tying Fsp3 to development success and solubility. citeturn35view0turn31view0  

\## rotatable-bond count: number of rotatable bonds  
- Common threshold(s) or range(s):  
  - **≤ 10 rotatable bonds** is the classic “good oral bioavailability probability” rule-of-thumb in Veber-style analysis citeturn14view0turn53view0  
  - Veber analysis also showed practical stratification bins: **≤7**, **8–10**, **>10** (used when examining %F ≥ 20% groups) citeturn14view2  
- Usually associated with: **higher oral bioavailability** with fewer rotatable bonds (less flexibility; typically better permeability and sometimes better solubility), and **lower oral bioavailability** as flexibility increases citeturn14view0turn14view2  
- Brief note: This is among the more task-proximal heuristics because it was developed in the context of oral bioavailability datasets and is widely used as an early triage rule. citeturn14view0turn53view0  
- Source: Veber-style oral bioavailability analysis and secondary summary. citeturn14view0turn14view2turn53view0  

\## ring count: total number of rings  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: highly context-dependent; ring count impacts rigidity, lipophilicity, and polarity distribution, so directionality depends on whether rings are aromatic vs saturated and on substituents  
- Brief note: In oral bioavailability practice, ring-count guidance is **most stable for aromatic rings** (see aromatic ring count), not total rings. citeturn33search27turn33search1  
- Source: aromatic ring count, rather than total ring count, has published developability cutoffs and oral-drug distributions. citeturn33search27turn33search1  

\## aromatic ring count: number of aromatic rings  
- Common threshold(s) or range(s):  
  - **> 3 aromatic rings** correlates with poorer developability and increased attrition risk (often used as a practical “liability” threshold) citeturn33search1turn35view0  
  - In a recent analysis of FDA oral drugs (2000–2022): mean aromatic ring count ~**2**, median **3**, “drop-off above 3,” with ~90th percentile at **4** (distributional anchor) citeturn33search27  
- Usually associated with: **lower oral bioavailability / developability** risk increases with higher aromatic ring count (e.g., solubility decreases even within fixed lipophilicity ranges in reported analyses), while fewer aromatics often improves compound quality citeturn33search1turn33search4turn33search27  
- Brief note: This is closer to an “oral developability” heuristic than a pure absorption rule, but it is repeatedly used in oral-candidate triage because aromaticity affects solubility, binding, and off-target liabilities that can impact exposure. citeturn33search4turn35view0turn33search27  
- Source: aromatic ring liability threshold + oral-drug property distributions. citeturn33search1turn33search27turn35view0  

\## aromatic carbocycle count: number of aromatic carbocyclic rings  
- Common threshold(s) or range(s): **no stable literature threshold found** (stable cutoffs are usually stated for **total aromatic ring count**, not the carbocycle subset) citeturn33search1turn33search27  
- Usually associated with: higher carbocyclic aromatic content often increases lipophilicity and can worsen solubility, potentially decreasing oral bioavailability if solubility/permeability become limiting  
- Brief note: Use the **aromatic ring count >3** heuristic as the closest stable proxy. citeturn33search1turn33search27  
- Source: aromatic ring count heuristics used in oral candidate context. citeturn33search1turn33search27  

\## aromatic heterocycle count: number of aromatic heterocyclic rings  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: context-dependent; aromatic heterocycles can reduce lipophilicity vs carboaromatics and add polarity/HBA sites, so the net effect depends on overall H-bonding and TPSA  
- Brief note: Published thresholds are more stable for **total aromatic ring count** than for this subset. citeturn33search1turn33search27  
- Source: aromatic ring count heuristics and distributions for oral drugs. citeturn33search1turn33search27  

\## aliphatic ring count: number of aliphatic rings  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: mixed effects—aliphatic rings increase 3D shape/rigidity (sometimes helpful), but also add size and hydrophobic surface (sometimes harmful)  
- Brief note: Consider aliphatic rings mainly through their effects on **Fsp3, MW, logP/logD, TPSA, rotatable bonds**. citeturn35view0turn14view0turn53view0  
- Source: developability rules emphasize overall property balance and aromatic liability rather than aliphatic-ring cutoffs. citeturn14view0turn35view0turn53view0  

\## aliphatic carbocycle count: number of aliphatic carbocyclic rings  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: context-dependent; can raise hydrophobicity while increasing rigidity/3D character  
- Brief note: No widely used oral bioavailability cutoff exists for this ring subtype; treat as a contributor to logP/logD and Fsp3. citeturn35view0turn18view0  
- Source: oral heuristics prioritize lipophilicity/polarity/flexibility endpoints rather than ring-subtype counts. citeturn18view0turn14view0turn35view0  

\## aliphatic heterocycle count: number of aliphatic heterocyclic rings  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: often increases polarity/HBA (potentially helping solubility but risking permeability if TPSA becomes high)  
- Brief note: Not commonly thresholded directly; evaluate via HBA/HBD/TPSA/logD. citeturn14view0turn18view0turn16view2  
- Source: established oral filters focus on HBA/HBD/TPSA/logD, not heterocycle counts. citeturn14view0turn18view0turn16view2  

\## saturated ring count: number of saturated rings  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: can correlate with higher Fsp3 and 3D character (sometimes favorable), but adds size/hydrophobicity  
- Brief note: The stable “ring” heuristic in oral space is aromatic ring count; saturated ring count is mainly interpreted via Fsp3 and lipophilicity. citeturn35view0turn33search27  
- Source: Fsp3/development-success summaries and aromatic ring heuristics. citeturn35view0turn33search27  

\## saturated carbocycle count: number of saturated carbocyclic rings  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: context-dependent; can enhance 3D character but increase hydrophobic burden  
- Brief note: No standard oral bioavailability cutoffs for this subtype; treat as a contributor variable (MW/logP/logD/Fsp3). citeturn35view0turn18view0  
- Source: oral rules-of-thumb are not expressed in saturated-carbocycle counts. citeturn18view0turn35view0  

\## saturated heterocycle count: number of saturated heterocyclic rings  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: can increase polarity and solubility but may increase TPSA/HBA enough to reduce permeability if not balanced  
- Brief note: Evaluate via HBA/HBD/TPSA/logD rather than a saturated-heterocycle cutoff. citeturn14view0turn16view2turn26view0  
- Source: dominant oral heuristics for polarity and permeability. citeturn14view0turn16view2turn26view0  

\## Labute surface area: Labute approximate surface area  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: larger surface area often correlates with higher MW and potentially higher polarity burden; directionality depends on whether surface area is hydrophobic vs polar  
- Brief note: Unlike TPSA, Labute ASA is not a widely published pass/fail oral bioavailability heuristic; it is more common as a **model feature**. citeturn14view0turn16view2turn49view2  
- Source: established oral heuristics use TPSA rather than total (Labute) surface area. citeturn14view0turn16view2turn49view2  

## Polarity and hydrogen-bonding anchors

\## topological polar surface area: topological polar surface area of the molecule  
- Common threshold(s) or range(s):  
  - **TPSA/PSA ≤ 140 Å²** (with rotatable bonds ≤10) associated with higher probability of “good” oral bioavailability in Veber-style analysis citeturn14view0turn53view0  
  - In the Egan PSA–AlogP98 absorption model: **PSA upper limit ~131.6 Å²** (95% ellipse) and **~148.1 Å²** (99% ellipse) citeturn16view2  
- Usually associated with: **lower oral bioavailability** as TPSA rises above these regions (permeability/absorption risk), with exceptions for actively transported compounds citeturn14view0turn16view2  
- Brief note: TPSA thresholds are among the most widely used because they map to membrane permeability constraints; choosing **131 vs 140 vs 148 Å²** reflects different modeling traditions and safety margins. citeturn14view0turn16view2  
- Source: Veber-style oral bioavailability rule; Egan absorption model ellipses. citeturn14view0turn16view2turn53view0  

\## hydrogen-bond donor count: number of hydrogen-bond donors  
- Common threshold(s) or range(s):  
  - **HBD ≤ 5** (Rule of Five) citeturn18view0turn53view0  
  - Alternative Veber-style criterion uses **HBD + HBA ≤ 12** (as a proxy for total H-bonding/polarity) citeturn14view0turn37view2  
- Usually associated with: **higher oral bioavailability** when HBD is modest; **lower oral bioavailability** risk increases as HBD rises (higher polarity reduces passive permeability) citeturn18view0turn14view0  
- Brief note: HBD is highly actionable (remove NH/OH donors, reduce amide count, etc.) and is a core component of most oral property filters. citeturn18view0turn14view0  
- Source: Rule of Five + Veber-style total H-bonding constraint. citeturn18view0turn14view0turn37view2  

\## hydrogen-bond acceptor count: number of hydrogen-bond acceptors  
- Common threshold(s) or range(s):  
  - **HBA ≤ 10** (Rule of Five) citeturn18view0turn53view0  
  - Alternative Veber-style criterion: **HBD + HBA ≤ 12** citeturn14view0turn37view2  
- Usually associated with: **higher oral bioavailability** when HBA is controlled; very high HBA increases polarity/PSA and can reduce passive absorption citeturn18view0turn14view0  
- Brief note: HBA count is also used as a practical proxy for “too many heteroatoms,” but HBA is more standardized than raw heteroatom count. citeturn18view0turn14view0  
- Source: Rule of Five + Veber-style total H-bonding rule. citeturn18view0turn14view0turn37view2  

\## NH/OH group count: number of NH or OH groups  
- Common threshold(s) or range(s): commonly treated as a near-proxy for HBD; practical anchor **≈ HBD ≤ 5** citeturn18view0turn53view0  
- Usually associated with: **higher oral bioavailability** when NH/OH count is modest; higher counts can increase polarity and metabolic conjugation risk (context-dependent) citeturn18view0turn14view0  
- Brief note: In most oral-property heuristics, NH/OH groups matter because they drive HBD and TPSA, which are directly thresholded. citeturn18view0turn14view0turn16view2  
- Source: Rule of Five donor constraint (NH/OH as donors) and PSA-based absorption heuristics. citeturn18view0turn14view0turn16view2  

\## nitrogen/oxygen atom count: number of nitrogen and oxygen atoms  
- Common threshold(s) or range(s): **no stable standalone threshold found**  
- Usually associated with: higher N/O count generally increases polarity and can reduce passive permeability (lower oral bioavailability) unless balanced by lipophilicity/3D shape and/or transporters  
- Brief note: A **combined** rule has been proposed using **MW/NO > 50** as a cutoff to differentiate higher- vs lower-absorbed drug classes in one analysis—useful as a proxy when N/O is available. citeturn26view0  
- Source: N/O used as polarity proxy and in a combined MW/NO cutoff. citeturn26view0  

\## heteroatom count: number of heteroatoms, such as N, O, or S  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: higher heteroatom count often increases PSA/HBA and can reduce passive absorption (lower oral bioavailability risk rises), but effects are mediated by ionization and scaffold context  
- Brief note: Medicinal chemistry community tends to operationalize heteroatom burden via **HBA/HBD and TPSA thresholds**, not raw heteroatom count. citeturn18view0turn14view0turn16view2  
- Source: established oral heuristics are framed in HBA/HBD/TPSA rather than heteroatom count. citeturn18view0turn14view0turn16view2  

\## maximum absolute partial charge: largest absolute atomic partial charge  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: extreme partial charges can indicate strong polarity and potential permeability issues (lower oral bioavailability), but no community cutoff is used for oral bioavailability triage  
- Brief note: Partial-charge extrema are primarily used as **ML features**; classic oral property rules do not specify cutoffs on charge descriptors. citeturn18view0turn14view0turn16view2turn49view2  
- Source: canonical oral bioavailability heuristics (Ro5, Veber, Egan) do not include partial-charge thresholds. citeturn18view0turn14view0turn16view2turn49view2  

\## maximum partial charge: most positive atomic partial charge  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: more extreme positive charge localization can correlate with strong basic centers and higher polarity; directionality depends on ionization state and counterbalancing properties  
- Brief note: Not commonly thresholded; use pKa/logD/HBD/HBA/TPSA instead. citeturn14view0turn18view0turn16view2  
- Source: standard oral bioavailability filters do not include atomic partial-charge cutoffs. citeturn14view0turn18view0turn16view2  

\## minimum absolute partial charge: smallest absolute atomic partial charge  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: not directly interpreted in medicinal chemistry oral bioavailability triage  
- Brief note: ML descriptor; lacks stable interpretive rule for oral bioavailability. citeturn49view2turn14view0  
- Source: absence from standard oral bioavailability rules-of-thumb. citeturn49view2turn14view0turn18view0  

\## minimum partial charge: most negative atomic partial charge  
- Common threshold(s) or range(s): **no stable literature threshold found**  
- Usually associated with: extreme negative charge localization can correlate with strong acids/anion-stabilizing motifs and elevated PSA; might reduce passive permeability  
- Brief note: Atomic-charge cutoffs are not standard; interpret via pKa/logD and PSA/H-bonding instead. citeturn26view0turn16view2turn14view0  
- Source: canonical absorption/bioavailability heuristics emphasize PSA/HBD/HBA/logD rather than atomic partial charges. citeturn26view0turn16view2turn14view0  

## Composite metrics and qualitative structural notes

\## QED drug-likeness: quantitative estimate of drug-likeness  
- Common threshold(s) or range(s): **no single stable cutoff**, but common anchors include:  
  - QED is scaled **0 to 1** (continuous ranking), not a strict pass/fail filter citeturn37view0turn37view2  
  - Reported mean QED around **0.67** for “attractive” compounds in one benchmark context citeturn37view2  
  - Reported median QED for drugs around **0.65**, with **~0.67** sometimes cited as an “attractive/promising” anchor citeturn35view0turn37view2  
- Usually associated with: **higher oral bioavailability likelihood** (as a composite proxy) when QED is higher, because QED aggregates MW, logP, HBD/HBA, TPSA, rotatable bonds, aromatic rings, and alerts (all linked to oral drug space) citeturn35view0turn37view2  
- Brief note: Use QED as a **summary score** when you want “overall drug-likeness pressure,” but do not treat it as a mechanistic determinant of oral bioavailability; interrogate the underlying components for actionable optimization. citeturn37view2turn49view2  
- Source: QED definition and benchmarking vs Ro5/Veber/Ghose; reported QED distribution anchors. citeturn37view2turn35view0  

## Functional-group notes

- Group name: **phenolic hydroxyls** (phenols, catechols, polyphenols)  
  - Usually associated with: **lower oral bioavailability** when extensive **phase II conjugation (glucuronidation/sulfation)** rapidly clears the parent (low exposure), unless protected (e.g., prodrugs, steric shielding)  
  - Brief note: Phenolic motifs are repeatedly highlighted as prone to extensive conjugation, which can translate into poor apparent bioavailability of the active parent. citeturn44search7turn44search23  
  - Source: reviews describing extensive sulfation/glucuronidation of phenolics and resulting poor bioavailability. citeturn44search7turn44search23  

- Group name: **phosphonic acids / phosphonates** (highly anionic at physiological pH)  
  - Usually associated with: **lower oral bioavailability** due to **very low membrane permeability** driven by high negative charge; oral success often requires **prodrug strategies**  
  - Brief note: This is one of the clearer “functional-group → oral BA liability” patterns because the strong anionic character is hard to balance with passive permeability. citeturn45search10turn45search17turn45search6  
  - Source: phosphonate/phosphonic acid reviews and examples noting low membrane permeability and low oral bioavailability. citeturn45search10turn45search17turn45search6  

- Group name: **guanidinium / guanidine-containing motifs** (strong bases; often largely protonated)  
  - Usually associated with: **lower oral bioavailability** via **poor passive permeability**; successful strategies often leverage **prodrugs** and/or **transporter targeting**  
  - Brief note: The need for transporter/prodrug approaches is repeatedly emphasized for highly polar guanidino analogs to improve intestinal permeability. citeturn44search2turn44search14turn44search6  
  - Source: guanidino/guanidine oral absorption limitation and transporter/prodrug strategies. citeturn44search2turn44search14turn44search6

Input 2. Single-molecule analysis notes
First, strongest basic pKa is value 2.6693. The global EBM contribution here is -0.3496, which pushes toward option (A): has oral bioavailability < 20%. Next, urethane is present (1). The global EBM contribution here is -0.3245, which pushes toward option (A): has oral bioavailability < 20%. Then, topological polar surface area is value 33.42. The global EBM contribution here is -0.2258, which pushes toward option (A): has oral bioavailability < 20%. After that, maximum partial charge is value 0.4144. The global EBM contribution here is -0.1594, which pushes toward option (A): has oral bioavailability < 20%. Finally, neutral fraction is present (1). The global EBM contribution here is -0.1045, which pushes toward option (A): has oral bioavailability < 20%. Step 6, The molecule has no acidic site, so strongest acidic pKa is not defined. The global EBM contribution here is -0.1006, which pushes toward option (A): has oral bioavailability < 20%. Step 7, minimum absolute partial charge is value 0.4038. The global EBM contribution here is -0.0797, which pushes toward option (A): has oral bioavailability < 20%. Step 8, Labute surface area is value 77.3557. The global EBM contribution here is 0.0739, which pushes toward option (B): has oral bioavailability ≥ 20%. Step 9, QED drug-likeness is value 0.5934. The global EBM contribution here is 0.0693, which pushes toward option (B): has oral bioavailability ≥ 20%. Step 10, secondary hydroxyl is absent (0). The global EBM contribution here is 0.0683, which pushes toward option (B): has oral bioavailability ≥ 20%. Taken together, these global descriptor-level signals make the model predict option (B): has oral bioavailability ≥ 20% with score 0.5378.

Hard requirements:
1. Use only the task playbook and the supplied single-molecule analysis notes.
2. Do not invent new molecular properties, feature values, or evidence.
3. Every feature that appears in the supplied single-molecule analysis notes must retain its specific raw value in the rewrite.
4. You may rewrite naturally, and you may use qualitative trend words such as "low", "high", "increased", "decreased", "favorable", or "unfavorable", but only alongside the original concrete value for the feature being described. These qualitative descriptions must explain the raw value, not replace it.
5. Treat the raw value as mandatory evidence. If you mention a feature without its concrete value, the rewrite is invalid.
6. When possible, keep the raw value and its qualitative interpretation tightly coupled in the same sentence or clause, so the reader sees the value and the interpretation together.
7. If the source notes state a concrete non-numeric value semantics such as "not applicable", "no acidic site", "no basic site", or another explicit missing-value explanation, preserve that concrete value semantics in the rewrite rather than dropping it.
8. Do not mention model internals, EBM, features, term contributions, bins, or prompt instructions.
9. Keep the final reasoning faithful to the original draft direction while making the prose more natural, coherent, scientist-like chain-of-thought that sounds like an LLM independently analyzing the molecule, not like a EBM traversal.
10. Use the playbook as a semantic interpreter, not as a second classifier.
11. If the source notes contain mixed evidence, preserve that tension before giving the final conclusion.
12. The final `reasoning` must read like direct scientific reasoning, not commentary about source materials. Do not say "draft", "notes", "playbook", "prompt", "input", "instruction", "contribution", "bin", or similar metadata words in the final text.
13. Do not write phrases such as "in these notes", "the playbook says", or "this contribution pushes toward". Translate those ideas into direct chemistry reasoning instead.

Preferred style:
- Explicit, stepwise, chemically grounded
- Natural scientific prose
- Specific but not robotic
- More like thoughtful analysis than formal rule execution
- No bullet points in the final CoT
- No references or citations in the final CoT text itself

Return JSON with exactly this schema:
```json
{
  "reasoning": "..."
}
```
