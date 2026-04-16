You are rewriting rough single-molecule analysis notes from Explainable Boosting Machine (EBM) into high-quality reasoning SFT data for task CYP2D6_Substrate_CarbonMangels where option (A) means is not a substrate to the enzyme CYP2D6 and option (B) means is a substrate to the enzyme CYP2D6.

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

Input 2. Single-molecule analysis notes
First, pyrazolidine is present (1). The global EBM contribution here is -0.8356, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Next, lactam is count 2. The global EBM contribution here is -0.338, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Then, minimum partial charge is value -0.2717. The global EBM contribution here is -0.2274, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. After that, strongest acidic pKa is value 4.627. The global EBM contribution here is -0.2074, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Finally, fraction of sp3 carbons is value 0.1304. The global EBM contribution here is -0.1306, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Step 6, benzene is count 3. The global EBM contribution here is 0.1184, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Step 7, maximum absolute partial charge is value 0.2717. The global EBM contribution here is -0.1112, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Step 8, sulfanylidene is present (1). The global EBM contribution here is -0.0883, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Step 9, number of basic sites is absent (0). The global EBM contribution here is -0.0846, which pushes toward option (A): is not a substrate to the enzyme CYP2D6. Step 10, aromatic carbocycle count is value 3. The global EBM contribution here is 0.0569, which pushes toward option (B): is a substrate to the enzyme CYP2D6. Taken together, these global descriptor-level signals make the model predict option (A): is not a substrate to the enzyme CYP2D6 with score 0.9392.

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
