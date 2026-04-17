# Molecular-property playbook for SARSCoV2_Vitro_Touret

This playbook is tuned to the Touret live-virus VeroE6 cytopathic-effect screen behind the entity["organization","Therapeutics Data Commons","benchmark platform"] task. In the original assay, compounds were tested at 10 µM and hits were called at inhibition index ≥1 relative to arbidol, but the authors also state that the hit thresholds were arbitrary. In the closest neighboring literature, the clearest task-specific physicochemical signal is enrichment of weakly basic, lipophilic cationic amphiphilic drugs in Vero/endosomal-entry systems; neighboring studies also show strong cell-type specificity and a substantial phospholipidosis confound. For most descriptors, the most usable anchors therefore come from lysosomotropism/CAD literature and standard medicinal-chemistry filters rather than from a Touret-specific cutoff alone. citeturn1view0turn19view0turn1view2turn17search26turn22view0

## neutral fraction
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: (B) only indirectly, when the molecule behaves as a weak base rather than a permanently neutral or strongly acidic scaffold
- Brief note: Task-neighboring papers discuss basic pKa and lipophilicity, not neutral-fraction cutoffs; the recurring Vero-hit pattern is a weak base that still retains enough neutral form to cross membranes.
- Source: Villoutreix et al., 2021; Kazmi et al., 2013; Dittmar et al., 2021. citeturn22view0turn6search24turn1view2

## estimated logD
- Common threshold(s) or range(s): proxy permeability rule, 0 to 3
- Usually associated with: better follow-up likelihood when not too low and not extreme; not by itself a clean (B) rule
- Brief note: This comes from a permeability filter rather than Touret itself. In task-neighboring SARS-CoV-2 CPE work, the stronger direct signal is moderate-to-high lipophilicity/CAD behavior, so use logD together with strongest basic pKa.
- Source: Kralj et al., 2022; Villoutreix et al., 2021; Tummino et al., 2021. citeturn16view0turn22view0turn17search26

## strongest acidic pKa
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: The task-neighboring SARS-CoV-2 repurposing literature is dominated by weak-base/CAD discussions, not by acidic-ionization rules. Strong acidity is generally outside the main Vero-hit motif, but no stable acidic-pKa cutoff is used.
- Source: Touret et al., 2020; Villoutreix et al., 2021. citeturn19view0turn22view0

## strongest basic pKa
- Common threshold(s) or range(s): broad lysosomotropic rule, >6; stricter CAD rules often use >6.5 to 7.4
- Usually associated with: (B) enrichment in Touret-like Vero/endosomal-entry assays
- Brief note: This is the clearest task-neighboring anchor. High basicity plus lipophilicity repeatedly marks Vero-active CAD-like compounds, but the same pattern is also linked to cell-type specificity and phospholipidosis.
- Source: Kazmi et al., 2013; Villoutreix et al., 2021; Varalda et al., 2020; Dittmar et al., 2021; Tummino et al., 2021. citeturn6search24turn22view0turn3view2turn1view2turn17search26

## number of acidic sites
- Common threshold(s) or range(s): proxy rule, 0 to 1; compounds with >1 carboxylic acid are dismissed in the Muegge filter
- Usually associated with: (A) or weaker follow-up potential when multiple acidic sites are present
- Brief note: This is a developability proxy, not a Touret-specific assay rule. Task-neighboring Vero positives are not typically multi-acidic chemotypes.
- Source: Kralj et al., 2022; Villoutreix et al., 2021. citeturn16view0turn22view0

## number of basic sites
- Common threshold(s) or range(s): proxy rule, at least 1 basic site is common; no stable upper cutoff found
- Usually associated with: (B) enrichment when at least one basic ionizable center is present
- Brief note: The recurring CAD motif is a hydrophobic/aromatic scaffold plus one or more ionizable amines.
- Source: Villoutreix et al., 2021; Morin-Dewaele et al., 2022. citeturn22view0turn20view0

## number of ionizable sites
- Common threshold(s) or range(s): proxy rule, at least 1 total ionizable site, with the informative part usually being a basic site
- Usually associated with: (B) enrichment when the total includes a basic amine
- Brief note: Total ionizable-site count is less informative than whether the molecule contains a weakly basic center that supports lysosomotropism.
- Source: Villoutreix et al., 2021; Kazmi et al., 2013. citeturn22view0turn6search24

## exact molecular weight
- Common threshold(s) or range(s): 180 to 480 (Ghose); ≤500 (Lipinski); 200 to 600 appears in alternate drug-like filters
- Usually associated with: better follow-up/developability in the 180 to 500 band; not by itself a clean (B) rule
- Brief note: Practical cutoffs for exact MW are the same as for conventional molecular weight. Touret-like hits include exceptions such as macrolides, so this is a warning flag, not a veto.
- Source: Kralj et al., 2022; Touret et al., 2020. citeturn16view0turn18view0

## fraction of sp3 carbons
- Common threshold(s) or range(s): ≥0.42 is a common favorable cutoff; approved small molecules average around 0.47
- Usually associated with: better developability and usually better solubility; not uniquely a (B) rule
- Brief note: Useful as a tie-breaker to avoid overly flat aromatic chemotypes after a hit is already interesting.
- Source: Lovering et al., 2009; Kombo et al., 2013; Buskes et al., 2020. citeturn10search4turn11search2turn11search19

## heavy-atom count
- Common threshold(s) or range(s): 20 to 50
- Usually associated with: better follow-up/developability when inside the usual drug-like band; not a direct (B) rule
- Brief note: This comes from the REOS property filter and is best used as a size proxy alongside MW.
- Source: Kralj et al., 2022. citeturn16view0

## heavy-atom molecular weight
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: Standard medicinal-chemistry filters use total MW or heavy-atom count instead; heavy-atom molecular weight is not a standard interpretation axis for SARS-CoV-2 CPE triage.
- Source: Kralj et al., 2022; Daina et al., 2017. citeturn16view0turn14view0

## Labute surface area
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: In practical medicinal chemistry, TPSA is the standard polarity cutoff, not Labute surface area.
- Source: Kralj et al., 2022; Daina et al., 2017. citeturn16view0turn14view0

## maximum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: This descriptor is not part of the standard SARS-CoV-2 repurposing heuristics or mainstream drug-like filters summarized in the literature.
- Source: Kralj et al., 2022; Daina et al., 2017. citeturn16view0turn14view0

## maximum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: Partial-charge extrema are not standard medicinal-chemistry triage axes for Touret-like CPE data.
- Source: Kralj et al., 2022; Daina et al., 2017. citeturn16view0turn14view0

## minimum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: The literature uses lipophilicity, ionization, H-bonding, polarity, and flexibility far more often than this descriptor.
- Source: Kralj et al., 2022; Daina et al., 2017. citeturn16view0turn14view0

## minimum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: No stable medicinal-chemistry interpretation rule was found for this descriptor in SARS-CoV-2 CPE screening or standard drug-like filters.
- Source: Kralj et al., 2022; Daina et al., 2017. citeturn16view0turn14view0

## estimated logP
- Common threshold(s) or range(s): task-neighboring CAD rules usually start at >2 to 3, with >3 the stricter CAD cutoff; classic drug-like upper bounds are ≤5 and, in Ghose, −0.4 to 5.6
- Usually associated with: (B) enrichment in Touret-like Vero assays when moderate/high, but also with PLD-linked or cell-type-specific positives when paired with high basicity
- Brief note: This is probably the second clearest task-neighboring anchor after strongest basic pKa. Use it together with basicity, not alone.
- Source: Villoutreix et al., 2021; Kazmi et al., 2013; Varalda et al., 2020; Kralj et al., 2022; Tummino et al., 2021. citeturn22view0turn6search24turn3view2turn16view0turn17search26

## molecular weight
- Common threshold(s) or range(s): 180 to 480 (Ghose); ≤500 (Lipinski); 200 to 600 in alternate drug-like filters
- Usually associated with: better follow-up/developability in the usual oral-drug band; not a direct (B) signal
- Brief note: Same practical interpretation as exact molecular weight. Larger approved-drug exceptions exist in Touret-like repurposing sets.
- Source: Kralj et al., 2022; Touret et al., 2020. citeturn16view0turn18view0

## NH/OH group count
- Common threshold(s) or range(s): proxy rule, 0 to 5
- Usually associated with: better permeability/follow-up when not excessive
- Brief note: This is a surrogate for H-bond-donor burden, not a perfect replacement. Many CAD-like Vero hits sit toward the low-donor end.
- Source: Kralj et al., 2022; Villoutreix et al., 2021. citeturn16view0turn22view0

## nitrogen/oxygen atom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: Nearby library filters sometimes require at least one nitrogen and one oxygen, but that is a library-enrichment rule, not a stable SARS-CoV-2 antiviral rule.
- Source: Kralj et al., 2022. citeturn16view0

## aliphatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: Saturation is more reliably interpreted through Fsp3 than through a specific aliphatic carbocycle count.
- Source: Lovering et al., 2009; Wei et al., 2020. citeturn10search4turn11search0

## aliphatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: Heterocycles are common in drugs, but no reproducible count cutoff is used for Touret-like SARS-CoV-2 assays.
- Source: Ertl et al., 2025; Kralj et al., 2022. citeturn10search3turn16view0

## aliphatic ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: Ring presence matters broadly, but no accepted aliphatic-ring-count rule is used for this task family.
- Source: Kralj et al., 2022; Lovering et al., 2009. citeturn16view0turn10search4

## aromatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: The literature usually thresholds total aromatic ring count, not aromatic carbocycle count specifically.
- Source: Ritchie et al., 2009; Kralj et al., 2022. citeturn10search9turn16view0

## aromatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: Heteroaromatic rings are common and not themselves red flags, but no stable numeric cutoff is used; the broader liability is excessive total aromaticity.
- Source: Ritchie et al., 2011; Kralj et al., 2022. citeturn10search2turn16view0

## aromatic ring count
- Common threshold(s) or range(s): ≤3 preferred; >3 correlates with poorer developability
- Usually associated with: better follow-up potential when ≤3; use high counts as a liability flag rather than an (A)/(B) classifier
- Brief note: Many Vero-active CAD chemotypes still live around 2 to 3 aromatic/tricyclic systems, so this is best used as a “too many rings” warning.
- Source: Ritchie et al., 2009; Ritchie et al., 2011; Kralj et al., 2022. citeturn10search9turn10search2turn16view0

## hydrogen-bond acceptor count
- Common threshold(s) or range(s): ≤10
- Usually associated with: better follow-up/developability when compliant; not a direct (B) rule
- Brief note: Excess acceptor count often tracks higher polarity and weaker passive cell entry in whole-cell assays.
- Source: Kralj et al., 2022. citeturn16view0

## hydrogen-bond donor count
- Common threshold(s) or range(s): ≤5
- Usually associated with: better follow-up/developability when compliant; many CAD-like Vero hits are lower
- Brief note: Lower donor burden usually helps passive membrane crossing in cell-based antiviral assays.
- Source: Kralj et al., 2022. citeturn16view0

## heteroatom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: The closest general rule is qualitative: compounds lacking both nitrogen and oxygen are usually disfavored, but no accepted heteroatom-count cutoff exists.
- Source: Kralj et al., 2022. citeturn16view0

## rotatable-bond count
- Common threshold(s) or range(s): ≤10 (Veber); ≤8 is a stricter REOS-style bound
- Usually associated with: better follow-up/developability when not overly flexible
- Brief note: Useful as a secondary filter after a compound already looks promising; it is not a primary Touret-specific discriminator.
- Source: Kralj et al., 2022. citeturn16view0

## saturated carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: If you want a saturation-based preference, Fsp3 is the better-supported descriptor.
- Source: Lovering et al., 2009; Wei et al., 2020. citeturn10search4turn11search0

## saturated heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: Saturated heterocycles are common in medicinal chemistry, but no stable count cutoff is used for this task family.
- Source: Ertl et al., 2025; Wei et al., 2020. citeturn10search3turn11search0

## saturated ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent (A)/(B) direction
- Brief note: Saturation is better handled by Fsp3 than by raw saturated-ring count.
- Source: Lovering et al., 2009; Wei et al., 2020. citeturn10search4turn11search0

## ring count
- Common threshold(s) or range(s): at least 1 ring is usually required in drug-like filters; common upper proxies are ≤6 or, for lead-like space, ≤4
- Usually associated with: better follow-up when not ring-free and not ring-heavy; not a direct (B) rule
- Brief note: This is a broad library-design guide only. For liability, total aromatic ring count is usually more informative than total ring count.
- Source: Kralj et al., 2022. citeturn16view0

## topological polar surface area
- Common threshold(s) or range(s): ≤140 (Veber); ≤131.6 (Egan); ≤90 is a stricter cell-/BBB-permeation-friendly bound
- Usually associated with: better cell entry/follow-up when moderate; very high TPSA usually works against whole-cell antiviral activity
- Brief note: For this task family, TPSA is much more actionable than Labute surface area.
- Source: Kralj et al., 2022. citeturn16view0

## QED drug-likeness
- Common threshold(s) or range(s): ≥0.67 attractive; 0.49 to 0.67 middling/unattractive; <0.49 too complex/less attractive
- Usually associated with: better overall developability among follow-up candidates, not a direct (B) classifier
- Brief note: Use QED late, after filtering obvious assay-context artifacts such as CAD/PLD-heavy Vero-only hits.
- Source: Bickerton et al., 2012; later QED implementations and use notes. citeturn13search8turn13search19

## Functional-group notes

- Group name: ionizable secondary or tertiary amine on a hydrophobic/aromatic scaffold
- Usually associated with: (B) enrichment in Touret-like Vero/endosomal-entry assays
- Brief note: This is the canonical cationic amphiphilic drug motif. It recurs across psychotropics, antihistamines, antimalarials, and other repurposing hits, but it is also the core phospholipidosis-risk motif.
- Source: Villoutreix et al., 2021; Kazmi et al., 2013; Tummino et al., 2021. citeturn22view0turn6search24turn17search26

- Group name: tricyclic cationic amphiphile scaffold
- Usually associated with: (B) in Vero-E6 and related endosomal-entry models
- Brief note: In direct SARS-CoV-2 CAD testing, the most potent compounds shared a tricyclic ring skeleton, and modifying that tricycle reduced activity. This is a strong task-neighboring chemotype signal.
- Source: Morin-Dewaele et al., 2022. citeturn20view0

- Group name: phenothiazine scaffold
- Usually associated with: (B) in multiple SARS-CoV-2 in vitro repurposing studies
- Brief note: Phenothiazines are repeatedly highlighted in the psychotropic/COVID repurposing literature, with chlorpromazine serving as the prototype. Treat them as mechanistically plausible but high-risk for assay-context effects.
- Source: Villoutreix et al., 2021; Plaze et al., 2020. citeturn22view0turn23search1

- Group name: CAD-like antihistamine motif
- Usually associated with: (B) in several repurposing and follow-up studies
- Brief note: Antihistamines such as desloratadine, loratadine, hydroxyzine, diphenhydramine, and azelastine recur in the literature as antiviral or virus-entry-modulating hits, again mainly in the CAD/endosomal-entry neighborhood.
- Source: Morin-Dewaele et al., 2022; Reznikov et al., 2021. citeturn20view0turn23search7turn23search3