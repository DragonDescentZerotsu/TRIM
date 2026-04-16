You are rewriting rough neighbor-based molecule-comparison notes from Explainable Boosting Machine (EBM) into high-quality reasoning SFT data for molecule local analog-comparison task CYP2D6_Substrate_CarbonMangels where option (A) means is not a substrate to the enzyme CYP2D6 and option (B) means is a substrate to the enzyme CYP2D6.

Input 1. Task playbook
# CYP2D6 substrate molecular-property playbook for the TDC task CYP2D6_Substrate_CarbonMangels

This playbook is grounded in (i) the entity["organization","Therapeutics Data Commons","drug discovery datasets"] task context (a curated, multi-source binary substrate label) citeturn14search2turn14search11 and (ii) the closest task-adjacent, substrate-oriented literature that reports **empirical molecular-property distributions** and **operational substrate cutoffs** for CYP2D6 (notably a curated CYP2D6 kinetics database + decision-tree analysis). citeturn33view0turn20view1  
Because “substrate vs non-substrate” labels vary across sources and assays, many properties **do not have stable, universally adopted numeric cutoffs**; where this happens, the entry says so explicitly and provides only validated qualitative guidance. citeturn10view0turn33view0

## neutral fraction
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: **Lower neutral fraction at physiological pH** (i.e., more cationic character) is *often* associated with CYP2D6 substrate-like chemistry because many substrates contain a **protonated basic nitrogen** at physiological pH. citeturn22search30turn13search24turn27search1
- Brief note: A practical anchor from acid–base fundamentals is that **pH = pKa implies ~50% protonated/deprotonated** for a site; “mostly protonated” vs “mostly neutral” behavior is driven by how far pH is from pKa. (This is a mechanism-relevant proxy because CYP2D6 recognition is often discussed in terms of a protonated/basic center.) citeturn27search1turn22search30
- Source: citeturn22search30turn13search24turn27search1

## estimated logD
- Common threshold(s) or range(s): In a curated CYP2D6 kinetics small-molecule database, **LogD7.4** summary statistics were: **25th–75th percentile ~0.34–2.36**, median **~1.54**, observed range **~−1.76 to 6.38**. citeturn20view1turn20view2
- Usually associated with: **Higher lipophilicity at pH 7.4 (higher LogD7.4)** was associated with stronger substrate-like behavior in that kinetics dataset (LogD7.4 was one of the few single properties significantly correlated with normalized Km). citeturn20view1turn20view2
- Brief note: Treat LogD7.4 as a **task-adjacent anchor** because TDC Carbon-Mangels labels come from multiple literature sources, but LogD7.4 repeatedly emerges as a practical discriminator in substrate-related analyses. citeturn14search2turn20view1
- Source: citeturn20view1turn20view2turn14search2

## strongest acidic pKa
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: **Strongly acidic / predominantly anionic** molecules are *less often described as “typical” CYP2D6 substrates* than lipophilic bases (CYP2D6 is commonly described as favoring substrates with a basic center). citeturn22search30turn13search24
- Brief note: Acidic pKa mainly matters here via **ionization state at physiological pH** (shaping charge + logD), rather than as an independently thresholded CYP2D6 substrate rule. citeturn22search30turn27search1
- Source: citeturn22search30turn13search24turn27search1

## strongest basic pKa
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: **Presence of a basic center that can be protonated at physiological pH** is repeatedly noted as a common CYP2D6 substrate feature; practically, this implies a **basic pKa high enough to yield substantial protonation near pH ~7.4**. citeturn22search30turn13search24turn27search1
- Brief note: In a CYP2D6 kinetics property-analysis workflow, a “highest computed pKa” descriptor was explicitly included among computed properties because prior reports connect pKa/basicity to CYP2D6 substrate recognition—yet the same work emphasizes that **simple, single-property rules may not generalize across scaffolds**. citeturn33view0turn10view0
- Source: citeturn22search30turn13search24turn33view0turn10view0

## number of acidic sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More acidic sites can increase **polarity/ionization complexity**, potentially reducing the “typical lipophilic base” profile often associated with CYP2D6 substrates. citeturn22search30turn20view1
- Brief note: The most consistently stated CYP2D6 substrate “motif” is **basic** rather than **acidic** ionization; acidic-site counting is therefore a secondary, indirect cue. citeturn22search30turn13search24
- Source: citeturn22search30turn13search24turn20view1

## number of basic sites
- Common threshold(s) or range(s): qualitative anchor: **≥1 basic (protonatable) nitrogen** is repeatedly described as common among “typical” CYP2D6 substrates (though atypical cases exist). citeturn22search30turn13search24
- Usually associated with: **Substrate (B)** when at least one basic site is present and protonated at physiological pH; **non-substrate (A)** is more likely when no basic site is present (not a guarantee). citeturn22search30turn13search24
- Brief note: Several substrate-recognition descriptions emphasize a **positively charged nitrogen** at a characteristic distance from the oxidation site (structure-based rather than purely property-based). citeturn13search24turn22search30
- Source: citeturn22search30turn13search24

## number of ionizable sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Higher ionizable-site count can increase **charge-state heterogeneity**, shifting logD/PSA and potentially affecting CYP2D6 interaction indirectly. citeturn22search30turn20view1
- Brief note: The CYP2D6 substrate literature most consistently emphasizes **a basic center** rather than “many ionizable sites”; treat this as a complexity/ionization proxy. citeturn22search30turn13search24
- Source: citeturn22search30turn20view1turn13search24

## exact molecular weight
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Indirectly, “drug-like” MW ranges (often discussed around **≤500 Da** in general ADMET filtering) are a common proxy context for many small-molecule tasks. citeturn22search12turn33view0
- Brief note: A CYP2D6 kinetics property-analysis pipeline explicitly computed **molecular weight** as a candidate descriptor, but that work highlighted only a subset of properties as individually significant correlates (and emphasized multi-property interactions). citeturn33view0turn20view1turn10view0
- Source: citeturn33view0turn20view1turn22search12

## fraction of sp3 carbons
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: unclear direction for CYP2D6 substrate status in threshold form; any effect is likely **scaffold/shape-mediated** rather than a direct rule. citeturn10view0turn22search30
- Brief note: Substrate-recognition discussions for CYP2D6 focus more on **basic center + aromatic/lipophilic features** than on global Fsp3 cutoffs. citeturn22search30turn10view0
- Source: citeturn22search30turn10view0

## heavy-atom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Indirect proxy for size; larger/heavier molecules may trend more lipophilic and ring-rich, which can align with substrate-enriched regions in some CYP2D6 substrate analyses. citeturn20view1turn9view3
- Brief note: Use alongside molecular weight/ring count rather than as a standalone CYP2D6 rule. citeturn33view0turn9view3
- Source: citeturn20view1turn33view0turn9view3

## heavy-atom molecular weight
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Indirect size proxy; same caveats as molecular weight. citeturn33view0turn20view1
- Brief note: No CYP2D6-specific “heavy-atom MW” cutoffs are commonly used in the substrate literature; use only as a supporting feature. citeturn10view0turn22search30
- Source: citeturn33view0turn22search30turn10view0

## Labute surface area
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Indirectly tracks size/shape; CYP2D6 substrate analyses more commonly report PSA (polar surface area), molar volume, and ring count than Labute surface area thresholds. citeturn33view0turn20view1
- Brief note: If used, interpret as a **size/shape adjunct**, not a primary CYP2D6 substrate determinant. citeturn10view0turn22search30
- Source: citeturn33view0turn20view1turn22search30

## maximum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Molecules capable of presenting a **strongly positive center** (often a protonated nitrogen) are frequently discussed as CYP2D6-substrate-like; partial-charge extrema are only a computational proxy for that motif. citeturn13search24turn22search30
- Brief note: CYP2D6 literature typically states the requirement in **chemical terms** (protonated basic nitrogen) rather than numeric partial-charge cutoffs. citeturn13search24turn22search30
- Source: citeturn13search24turn22search30

## maximum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Higher maximum positive charge can proxy for a **cationic center**, potentially aligning with typical CYP2D6 substrate descriptions. citeturn13search24turn22search30
- Brief note: Prefer direct ionization descriptors (pKa, neutral fraction, logD7.4) over raw partial-charge extrema when interpreting CYP2D6 substrate likelihood. citeturn20view1turn33view0
- Source: citeturn13search24turn22search30turn33view0

## minimum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: unclear; not commonly thresholded for CYP2D6 substrate status. citeturn10view0turn22search30
- Brief note: If informative at all, it is likely through correlation with heteroatom content/polarity rather than a CYP2D6-specific rule. citeturn20view1turn33view0
- Source: citeturn20view1turn33view0turn22search30

## minimum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: unclear; not commonly presented as a CYP2D6-substrate cutoff. citeturn22search30turn10view0
- Brief note: Interpret together with PSA/HBA/HBD if at all; no standard numeric thresholds were identified. citeturn20view1turn33view0
- Source: citeturn20view1turn33view0turn22search30

## estimated logP
- Common threshold(s) or range(s): In a curated CYP2D6 kinetics small-molecule database, LogP summary statistics were: **25th–75th percentile ~1.85–3.97**, median **~2.94**, observed range **~−1.67 to 8.32**. citeturn20view1turn20view2
- Usually associated with: **Higher LogP** was associated with CYP2D6 substrate status in that analysis; mean LogP was higher for substrates than for nonsubstrates (operationally defined by Km cutoffs in that work). citeturn20view1turn12view0
- Brief note: This is one of the stronger **task-adjacent quantitative anchors** available, but the same work emphasizes that single-property rules can fail across scaffolds. citeturn10view0turn20view1
- Source: citeturn20view1turn12view0turn10view0

## molecular weight
- Common threshold(s) or range(s): Proxy (general drug-likeness): **MW ≤ 500 Da** is widely used in Rule-of-Five-style filtering; not a CYP2D6-specific substrate cutoff. citeturn22search12turn33view0
- Usually associated with: Indirect; MW contributes to size/shape and can correlate with lipophilicity and ring count, which can appear in CYP2D6 substrate models. citeturn9view3turn33view0
- Brief note: A CYP2D6 kinetics property-analysis workflow computed MW but reported only certain properties (LogP, LogD7.4, PSA, MV) as individually significant correlates with normalized Km. citeturn33view0turn20view1
- Source: citeturn22search12turn33view0turn20view1turn9view3

## NH/OH group count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More NH/OH groups often increases H-bonding and PSA, which (in at least one CYP2D6 kinetics analysis) trended **higher in nonsubstrates** via higher PSA. citeturn20view1turn33view0
- Brief note: CYP2D6 substrate literature usually emphasizes **a protonatable/basic nitrogen plus lipophilic/aromatic features**, not a direct NH/OH count cutoff. citeturn22search30turn10view0
- Source: citeturn20view1turn33view0turn22search30

## nitrogen/oxygen atom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Higher N/O count often increases polarity/PSA; lower PSA was associated with substrate status in a CYP2D6 kinetics dataset, making high N/O (and thus high PSA) a potential **non-substrate** correlate in some contexts. citeturn20view1turn22search30
- Brief note: N-count is also tied to **basic-site presence**, a qualitative CYP2D6 substrate motif. citeturn22search30turn13search24
- Source: citeturn20view1turn22search30turn13search24

## aliphatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Unclear as a standalone; may contribute to lipophilicity/shape.
- Brief note: CYP2D6 substrate-recognition discussions emphasize **aromatic/lipophilic moieties** more than explicit aliphatic carbocycle counts. citeturn22search30turn9view3
- Source: citeturn22search30turn9view3

## aliphatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Can increase polarity and/or introduce a basic center depending on heteroatoms; direction depends on whether the heterocycle is protonatable.
- Brief note: Treat as qualitative: protonatable N-heterocycles can support the “basic center” motif; non-basic heterocycles may mainly affect PSA/logD. citeturn22search30turn13search24turn20view1
- Source: citeturn22search30turn13search24turn20view1

## aliphatic ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Indirect via lipophilicity/shape; no standard CYP2D6 substrate cutoff identified.
- Brief note: In one CYP2D6 decision-tree analysis, “number of rings” (not ring type) was a consistent feature; ring subclass counts are finer-grained than typical literature rules. citeturn9view3turn33view0
- Source: citeturn9view3turn33view0

## aromatic carbocycle count
- Common threshold(s) or range(s): qualitative anchor: **≥1 aromatic ring** is repeatedly referenced as part of “typical” CYP2D6 substrate descriptions. citeturn22search30turn13search24
- Usually associated with: **Substrate (B)** when combined with a basic/protonated center; absence of aromatic carbocycles can reduce alignment with typical CYP2D6 substrate pharmacophores. citeturn22search30turn13search24
- Brief note: Literature commonly frames this as a **lipophilic/aromatic moiety at/near the oxidation site**, not a strict aromatic ring count threshold. citeturn22search30turn13search24
- Source: citeturn22search30turn13search24

## aromatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Can contribute to aromaticity and (if containing basic N) to the “basic center” motif; direction depends on protonatability and overall PSA/logD.
- Brief note: No widely used aromatic-heterocycle-count cutoff was identified for CYP2D6 substrate status; interpret via basic pKa and lipophilicity. citeturn22search30turn20view1
- Source: citeturn22search30turn20view1

## aromatic ring count
- Common threshold(s) or range(s): qualitative anchor: **≥1 aromatic ring** commonly appears in “typical CYP2D6 substrate” descriptions. citeturn22search30turn13search24
- Usually associated with: **Substrate (B)** when paired with a basic/protonated center and sufficient lipophilicity. citeturn22search30turn20view1
- Brief note: In one data-mining analysis, “number of rings” (counting rings broadly) was a robust decision-tree feature across multiple randomized models. citeturn9view3turn33view0
- Source: citeturn22search30turn13search24turn9view3turn33view0

## hydrogen-bond acceptor count
- Common threshold(s) or range(s): Proxy (general drug-likeness): **HBA ≤ 10** is a common Rule-of-Five-style cutoff; not a CYP2D6-specific substrate threshold. citeturn22search12turn33view0
- Usually associated with: Indirect; more acceptors often increases PSA. Lower PSA associated with substrate status in one CYP2D6 kinetics dataset suggests very high HBA (high PSA) may align more with **non-substrate** *in that context*. citeturn20view1turn33view0
- Brief note: A CYP2D6 kinetics analysis explicitly computed HBA but reported only LogP, LogD7.4, PSA, and MV as individually significant correlates with normalized Km. citeturn33view0turn20view1
- Source: citeturn22search12turn33view0turn20view1

## hydrogen-bond donor count
- Common threshold(s) or range(s): Proxy (general drug-likeness): **HBD ≤ 5** is a common Rule-of-Five-style cutoff; not a CYP2D6-specific substrate threshold. citeturn22search12turn33view0
- Usually associated with: Indirect; more donors often increases PSA. In one CYP2D6 dataset analysis, lower PSA aligned with substrate status. citeturn20view1turn33view0
- Brief note: HBD was computed but not highlighted as an individually significant correlate with normalized Km in that CYP2D6 kinetics analysis. citeturn33view0turn20view1
- Source: citeturn22search12turn33view0turn20view1

## heteroatom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Higher heteroatom count often increases PSA and decreases lipophilicity; lower PSA and higher lipophilicity aligned with substrate status in one CYP2D6 kinetics analysis. citeturn20view1turn22search30
- Brief note: Heteroatom count is not typically reported as a standalone CYP2D6 substrate rule; interpret via PSA/HBA/HBD/logD. citeturn33view0turn20view1
- Source: citeturn20view1turn33view0turn22search30

## rotatable-bond count
- Common threshold(s) or range(s): Proxy (oral bioavailability): **rotatable bonds ≤ 10** is a commonly used heuristic paired with PSA thresholds; some implementations use **<12**. citeturn34search8turn34search14
- Usually associated with: Indirect; CYP2D6 substrate recognition is not typically framed as a rotatable-bond cutoff, but flexibility influences shape and may interact with ring count and lipophilicity. citeturn9view3turn10view0
- Brief note: In a CYP2D6 kinetics analysis, rotatable bonds were computed but not among the few single properties reported as significantly correlated with normalized Km. citeturn33view0turn20view1
- Source: citeturn34search8turn34search14turn33view0turn20view1

## saturated carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Indirect via lipophilicity/3D shape; not commonly thresholded for CYP2D6 substrate status.
- Brief note: Where ring features matter for CYP2D6, literature more often discusses **ring count** and **aromatic/lipophilic moieties** rather than saturated-ring subclass cutoffs. citeturn9view3turn22search30
- Source: citeturn9view3turn22search30

## saturated heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Depends on whether the heterocycle contains a protonatable N (supporting the “basic center” motif) vs being neutral/polar (raising PSA). citeturn22search30turn13search24
- Brief note: No stable saturated-heterocycle-count cutoffs are commonly used in CYP2D6 substrate classification. citeturn10view0turn22search30
- Source: citeturn22search30turn13search24turn10view0

## saturated ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Indirect; interpret via overall ring count and lipophilicity.
- Brief note: Decision-tree models for CYP2D6 substrate status identified “number of rings” as a consistent feature, but did not standardize saturated vs aromatic ring thresholds in a widely adopted way. citeturn9view3turn33view0
- Source: citeturn9view3turn33view0

## ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: In a CYP2D6 kinetics decision-tree analysis, **number of rings** repeatedly appeared as a consistent feature of substrate-associated patterns (directionally: more ring content aligning with substrate-like space), but without a single universal cutoff. citeturn9view3turn33view0
- Brief note: Treat ring count as a **model-relevant** but **scaffold-dependent** feature; combine with logP/logD and PSA rather than using a hard rule. citeturn9view3turn20view1
- Source: citeturn9view3turn33view0turn20view1

## topological polar surface area
- Common threshold(s) or range(s): Task-adjacent anchor (CYP2D6 kinetics database PSA): **25th–75th percentile ~19.11–50.28 Å²**, median **~35.53 Å²**; substrates had **lower mean PSA** than nonsubstrates under Km-based operational definitions. citeturn20view1turn12view0  
  Proxy (oral bioavailability): PSA (or TPSA) **≤ 140 Å²** is a widely used general heuristic (not CYP2D6-specific). citeturn34search8turn34search14
- Usually associated with: **Lower PSA/TPSA** tends to associate with CYP2D6 substrate status in the kinetics dataset analysis (and is consistent with “lipophilic base” substrate descriptions). citeturn20view1turn22search30
- Brief note: The CYP2D6 kinetics analysis reported PSA as one of the few single properties significantly correlated with normalized Km, making PSA/TPSA among the more actionable polarity descriptors for substrate-adjacent reasoning. citeturn20view1turn33view0
- Source: citeturn20view1turn12view0turn34search8turn34search14turn22search30turn33view0

## QED drug-likeness
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Higher QED indicates stronger “overall drug-likeness” under the QED construction, but QED is **not a CYP2D6 substrate-specific** thresholding tool. citeturn22search12turn14search2
- Brief note: QED is an aggregate of multiple underlying descriptors (including MW, logP, HBA, HBD, PSA, rotatable bonds, aromatic rings, and structural alerts) and may correlate indirectly with substrate-like space through those components rather than providing an interpretable CYP2D6 cutoff. citeturn22search12turn33view0
- Source: citeturn22search12turn33view0turn14search2

## Functional-group notes
- Group name: Protonatable/basic nitrogen (e.g., tertiary or secondary amine; basic N in heterocycles when protonatable)
- Usually associated with: Substrate (B)
- Brief note: CYP2D6 substrates are commonly described as having a **basic center** that can be **protonated at physiological pH**, and classical CYP2D6 oxidation patterns are often described relative to a **positively charged nitrogen** and its geometry to the oxidation site. citeturn22search30turn13search24
- Source: citeturn22search30turn13search24

- Group name: Aromatic/lipophilic moiety (often an aromatic ring near the oxidation site)
- Usually associated with: Substrate (B)
- Brief note: “Typical” CYP2D6 substrates are commonly described as **lipophilic bases** with an **aromatic/lipophilic moiety**; decision-tree substrate models also highlighted ring content and lipophilicity as recurring features of substrate-associated patterns. citeturn22search30turn9view3turn20view1
- Source: citeturn22search30turn9view3turn20view1

Input 2. Neighbor similarities and per-neighbor comparison notes
"""
Neighbors that is a substrate to the enzyme CYP2D6:
Neighbor 1: 
Similarity: 0.179
Comparison note: First, For strongest basic pKa, the neighbor's strongest basic pKa is value 7.5429, while the query's strongest basic pKa is value 2.4913. The query-minus-neighbor delta is -5.0516. This pairwise contribution is -0.3163, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Next, The neighbor does not have purine, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 0.3108, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Then, The neighbor has pyrimidine, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is 0.2769, which pushes toward option (B): is a substrate to the enzyme CYP2D6. After that, For maximum absolute partial charge, the neighbor's maximum absolute partial charge is value 0.3383, while the query's maximum absolute partial charge is value 0.3934. The query-minus-neighbor delta is +0.0552. This pairwise contribution is 0.2439, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Finally, For minimum partial charge, the neighbor's minimum partial charge is value -0.3383, while the query's minimum partial charge is value -0.3934. The query-minus-neighbor delta is -0.0552. This pairwise contribution is 0.1908, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Step 6, The neighbor does not have uracil, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 0.1597, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Taken together, this positive-neighbor comparison pushes toward option (A): is not a substrate to the enzyme CYP2D6 with pair score 0.3666.
Neighbor 2: 
Similarity: 0.162
Comparison note: First, For strongest basic pKa, the neighbor's strongest basic pKa is value 7.448, while the query's strongest basic pKa is value 2.4913. The query-minus-neighbor delta is -4.9567. This pairwise contribution is -0.3216, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Next, The neighbor does not have purine, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 0.3108, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Then, The neighbor has 4H-1,2,4-triazole, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is 0.2056, which pushes toward option (B): is a substrate to the enzyme CYP2D6. After that, For topological polar surface area, the neighbor's topological polar surface area is value 46.3, while the query's topological polar surface area is value 82.05. The query-minus-neighbor delta is +35.75. This pairwise contribution is -0.1685, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Finally, The neighbor does not have uracil, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 0.1597, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Step 6, For neutral fraction, the neighbor's neutral fraction is value 0.4724, while the query's neutral fraction is present (1). The query-minus-neighbor delta is +0.5276. This pairwise contribution is -0.1238, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Taken together, this positive-neighbor comparison pushes toward option (A): is not a substrate to the enzyme CYP2D6 with pair score 0.3851.
Neighbor 3: 
Similarity: 0.161
Comparison note: First, The neighbor does not have purine, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 0.3108, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Next, For estimated logD, the neighbor's estimated logD is value 4.3907, while the query's estimated logD is value -0.0152. The query-minus-neighbor delta is -4.4059. This pairwise contribution is -0.2911, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Then, For minimum absolute partial charge, the neighbor's minimum absolute partial charge is value 0.1175, while the query's minimum absolute partial charge is value 0.332. The query-minus-neighbor delta is +0.2145. This pairwise contribution is -0.2246, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. After that, The neighbor has 3 copies of benzene, while the query has 0 (query-minus-neighbor delta -3). This pairwise contribution is -0.1914, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Finally, For topological polar surface area, the neighbor's topological polar surface area is value 43.7, while the query's topological polar surface area is value 82.05. The query-minus-neighbor delta is +38.35. This pairwise contribution is -0.1875, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Step 6, For fraction of sp3 carbons, the neighbor's fraction of sp3 carbons is value 0.4375, while the query's fraction of sp3 carbons is value 0.6154. The query-minus-neighbor delta is +0.1779. This pairwise contribution is 0.1866, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Taken together, this positive-neighbor comparison pushes toward option (A): is not a substrate to the enzyme CYP2D6 with pair score 0.2092.

Neighbors that is not a substrate to the enzyme CYP2D6
Neighbor 4: 
Similarity: 0.225
Comparison note: First, The neighbor has furan, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is -0.4321, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Next, Both the neighbor and the query have purine (query-minus-neighbor delta +0). This pairwise contribution is 0.3908, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Then, For minimum absolute partial charge, the neighbor's minimum absolute partial charge is value 0.3324, while the query's minimum absolute partial charge is value 0.332. The query-minus-neighbor delta is -0.0004. This pairwise contribution is -0.2495, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. After that, Both the neighbor and the query have uracil (query-minus-neighbor delta +0). This pairwise contribution is 0.2398, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Finally, For estimated logP, the neighbor's estimated logP is value 0.373, while the query's estimated logP is value -0.0152. The query-minus-neighbor delta is -0.3882. This pairwise contribution is -0.2119, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Step 6, For neutral fraction, the neighbor's neutral fraction is value 0.9515, while the query's neutral fraction is present (1). The query-minus-neighbor delta is +0.0485. This pairwise contribution is -0.1707, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Taken together, this negative-neighbor comparison pushes toward option (A): is not a substrate to the enzyme CYP2D6 with pair score 0.168.
Neighbor 5: 
Similarity: 0.205
Comparison note: First, The neighbor has phosphonic acid, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is -1.2385, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Next, The neighbor has adenine, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is -1.1339, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Then, The neighbor does not have uracil, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is -0.6802, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. After that, For topological polar surface area, the neighbor's topological polar surface area is value 136.38, while the query's topological polar surface area is value 82.05. The query-minus-neighbor delta is -54.33. This pairwise contribution is 0.3088, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Finally, For strongest acidic pKa, the neighbor's strongest acidic pKa is value 2.3712, while the query's strongest acidic pKa is value 13.8657. The query-minus-neighbor delta is +11.4945. This pairwise contribution is 0.2512, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Step 6, For estimated logD, the neighbor's estimated logD is value -5.0866, while the query's estimated logD is value -0.0152. The query-minus-neighbor delta is +5.0714. This pairwise contribution is -0.2242, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Taken together, this negative-neighbor comparison pushes toward option (A): is not a substrate to the enzyme CYP2D6 with pair score 0.0141.
Neighbor 6: 
Similarity: 0.188
Comparison note: First, For strongest acidic pKa, the neighbor's strongest acidic pKa is value 13.8279, while the query's strongest acidic pKa is value 13.8657. The query-minus-neighbor delta is +0.0378. This pairwise contribution is 1.1565, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Next, The neighbor does not have uracil, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is -0.6802, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Then, The neighbor has imidazole, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is -0.4973, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. After that, For minimum absolute partial charge, the neighbor's minimum absolute partial charge is value 0.3424, while the query's minimum absolute partial charge is value 0.332. The query-minus-neighbor delta is -0.0105. This pairwise contribution is -0.2468, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Finally, For fraction of sp3 carbons, the neighbor's fraction of sp3 carbons is value 0.5, while the query's fraction of sp3 carbons is value 0.6154. The query-minus-neighbor delta is +0.1154. This pairwise contribution is 0.2076, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Step 6, For estimated logP, the neighbor's estimated logP is value 0.092, while the query's estimated logP is value -0.0152. The query-minus-neighbor delta is -0.1072. This pairwise contribution is -0.2019, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Taken together, this negative-neighbor comparison pushes toward option (A): is not a substrate to the enzyme CYP2D6 with pair score 0.0608.
"""

Input 3. Final prediction label
option (A): is not a substrate to the enzyme CYP2D6

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
