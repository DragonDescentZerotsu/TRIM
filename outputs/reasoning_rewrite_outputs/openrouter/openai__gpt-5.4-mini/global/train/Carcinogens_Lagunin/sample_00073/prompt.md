You are rewriting rough single-molecule analysis notes from Explainable Boosting Machine (EBM) into high-quality reasoning SFT data for task Carcinogens_Lagunin where option (A) means is not a carcinogen and option (B) means is a carcinogen.

Input 1. Task playbook
# Carcinogens_Lagunin Molecular Property Threshold Quick Reference Manual

This manual is intended for the single-task **Carcinogens_Lagunin** dataset from Therapeutics Data Commons (using your label definition: A = non-carcinogen, B = carcinogen). This dataset is provided under TDC’s “Carcinogens” task and is based on work by Alexey Lagunin and colleagues on rodent carcinogenicity prediction. The external test set description includes samples from the ISS carcinogen database and the Prestwick chemical library.

Important note: for the endpoint of **rodent carcinogenicity**, **structural alerts and metabolically generated reactive intermediates** are often more decisive than any single physicochemical property. Therefore, many physicochemical descriptors, especially charge distribution and surface-area-related features, **do not have stable hard thresholds** in the literature. In such cases, this manual prioritizes: (i) empirical thresholds that are strongly associated with **systemic exposure and developability** and are repeatedly used in medicinal chemistry and ADMET practice, as “neighboring-task proxies”; and (ii) **functional-group/substructure alerts** that are more directly relevant to carcinogenicity, listed at the end.

## neutral fraction
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A higher neutral fraction (more neutral species at physiological pH) usually implies greater passive membrane permeability potential and a stronger tendency for tissue distribution. In a risk-assessment context, greater “opportunity for exposure” is an intuitive consideration, but it is not a carcinogenicity-specific causal factor.
- Brief note: In PBPK/ADMET practice, whether ionization is “relevant in vivo” is often judged **site by site**. A common empirical rule is that **any basic center with pKa ≤ 4.4** or **any acidic center with pKa > 10.4** tends to remain neutral at physiological pH and may contribute little to in vivo ionization. Therefore, neutral fraction is usually interpreted together with the **strongest acidic/basic pKa and the number of ionizable sites**.
- Source: Ezuruike et al., 2022 (tutorial on PBPK compound files, including pKa/site relevance and empirical cutoffs)

## estimated logD
- Common threshold(s) or range(s):
  - **Golden Triangle (neighboring-task proxy: permeability / clearance / oral absorption)**: On the MW–logD7.4 plot, the region more favorable for simultaneously achieving permeability and low clearance forms a triangle. The paper explicitly notes that compounds in the **logD 1.0–2.0** range are more likely to be both “permeable and metabolically stable.” It also describes the triangle boundaries textually; for example, the baseline extends roughly from **MW = 200 with logD ≈ 2–5**, and the apex is around **MW ≈ 450 with logD ≈ 1–2**, with the center near **logD ≈ 1.5 and MW ≈ 350**.
  - **PFI (neighboring-task proxy: developability / solubility risk)**: PFI = Chrom logD7.4 + #Ar; **PFI < 6** is commonly used as a more desirable quality target. Some practical guidance also notes that permeability may peak around **PFI = 6–8**, implying that lower is not always better and that trade-offs exist.
- Usually associated with: Excessively high logD7.4 is often associated with higher lipophilicity, protein binding, and risks involving metabolic enzymes and ion channels, all of which add to the “developability burden.” Very low logD is often associated with insufficient passive permeability. These are neighboring-task empirical patterns, not carcinogenicity-specific causes.
- Brief note: This task is “carcinogenic vs. non-carcinogenic,” so logD thresholds are used more as proxies for **exposure and developability**. If a model implicitly learns that “higher exposure makes long-term bioassay positives more likely,” logD may be indirectly relevant, but it should not be treated as a substitute for structural carcinogenic mechanisms.
- Source: Johnson et al., 2009 (Golden Triangle); RSC Med. Chem. 2021 (PFI < 6); Wiley chapter sample table (PFI < 6 and note that permeability may peak at PFI = 6–8)

## strongest acidic pKa
- Common threshold(s) or range(s):
  - Site-relevance empirical boundary: **acidic center pKa > 10.4** tends to remain neutral at physiological pH and may be considered “not relevant for in vivo ionization.”
- Usually associated with: The lower the strongest acidic pKa (stronger acid), the more likely the compound is to be deprotonated at physiological pH, usually corresponding to a higher anionic fraction, higher polarity, and lower passive permeability.
- Brief note: Carcinogenicity itself has no universal hard threshold for acidic pKa. The threshold here is mainly used to interpret exposure-related properties such as neutral fraction, logD, and PSA.
- Source: Ezuruike et al., 2022 (pKa site relevance and empirical cutoffs)

## strongest basic pKa
- Common threshold(s) or range(s):
  - Site-relevance empirical boundary: **basic center pKa ≤ 4.4** tends to remain neutral at physiological pH and may be considered “not relevant for in vivo ionization.”
- Usually associated with: The higher the strongest basic pKa (stronger base), the more likely the compound is to be protonated at physiological pH, usually corresponding to a higher cationic fraction, greater aqueous solubility, and lower passive permeability, though transporter interactions may also become stronger.
- Brief note: For rodent carcinogenicity labels such as Carcinogens_Lagunin, pKa is more often used as an **exposure/distribution** explanatory variable than as a direct “carcinogenic mechanism threshold.”
- Source: Ezuruike et al., 2022 (pKa site relevance and empirical cutoffs)

## number of acidic sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More acidic sites usually reduce neutral fraction, increase the anionic proportion, and raise polarity-related indicators such as PSA and hydrogen bonding potential.
- Brief note: The literature more often evaluates whether ionization is relevant on a site-by-site basis rather than defining hard cutoffs for the number of acidic sites.
- Source: Ezuruike et al., 2022 (site-by-site evaluation of ionization relevance)

## number of basic sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More basic sites usually reduce neutral fraction, increase the cationic proportion, and increase hydrogen-bonding and polarity-related properties.
- Brief note: For carcinogenicity, the number of ionizable sites alone is usually insufficient to provide a mechanistic explanation. In neighboring ADMET tasks, a more common approach is to evaluate it jointly with logD, PSA, MW, transporters, and related factors.
- Source: Ezuruike et al., 2022; Wiley chapter sample table summarizing commonly used integrated rules

## number of ionizable sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A higher total number of ionizable sites usually means more complex pH-dependent ionization and distribution, which may lead to larger changes in polarity and solubility and to more complex absorption behavior.
- Brief note: Empirically, each ionizable site is judged separately for whether its pKa is relevant in vivo, and the results are then aggregated into descriptors such as neutral fraction and logD.
- Source: Ezuruike et al., 2022

## exact molecular weight
- Common threshold(s) or range(s):
  - **Ro5 (oral accessibility proxy)**: MW > 500 indicates a higher likelihood of poor absorption/permeation.
  - **GSK 4/400 (general ADMET proxy)**: MW < 400 is used as a more favorable empirical boundary.
  - **Golden Triangle (permeability + low clearance proxy)**: In this framework, above approximately **MW ≈ 450**, the probability of being both “permeable and low clearance” drops markedly; the center of the favorable region is near MW ≈ 350.
- Usually associated with: Larger molecules are generally less able to balance solubility, passive permeability, and metabolic stability. In toxicology, they are also more likely to bring broader “developability risks.”
- Brief note: Veber’s analysis suggests that a simple **MW = 500** cutoff alone does not effectively distinguish good from poor oral bioavailability; MW is often only a proxy for properties such as flexibility and polarity.
- Source: Lipinski et al., 2001; Veber et al., 2002; Johnson et al., 2009; Wiley chapter sample table (4/400 overview)

## fraction of sp3 carbons
- Common threshold(s) or range(s):
  - A practical anchor reported in review literature: **Fsp3 ≥ 0.42** is described as a “suitable value,” and about **84%** of marketed drugs meet this criterion. This is a neighboring-task proxy based on the traditional view that higher 3D character and saturation are associated with developability and success.
- Usually associated with: Higher Fsp3 is usually associated with greater saturation, stronger 3D shape, and more diverse conformational space. In medicinal chemistry it is often viewed as one strategy for reducing solubility and non-specific binding risks associated with excessive planarity and aromaticity.
- Brief note: There is no recognized direct threshold relationship between Fsp3 and carcinogenicity. In this task it is better used as a proxy for **developability/aromaticity**, and the signal is usually more robust when interpreted together with aromatic ring count and PFI.
- Source: Wei et al., 2020 (Fsp3 review and threshold anchor); Ritchie & Macdonald, 2009 (aromatic ring count and developability)

## heavy-atom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: An approximate indicator of “molecular size/complexity”; often used in potency metrics to normalize activity by size, for example as the denominator in ligand efficiency.
- Brief note: The original Golden Triangle discussion notes that **MW may overestimate “true size” in some cases because of heavy atoms such as halogens**, so heavy-atom count, molecular volume, and total surface area may sometimes represent size more effectively than MW. This explains why HAC is used in some projects to replace or supplement MW, though there is no unified hard threshold.
- Source: Nicolaou, 2014 (definition of heavy atoms in the context of ligand efficiency); Johnson et al., 2009 (discussion of HAC as a better size proxy)

## heavy-atom molecular weight
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A size/compositional proxy similar to MW, but more focused on the contribution of non-hydrogen atoms.
- Brief note: Like heavy-atom count, this kind of “size proxy” is more often used to explain or correct the limitations of MW, for example when heavy halogens inflate MW, rather than being used as a universal filtering threshold.
- Source: Johnson et al., 2009 (discussion that MW may overestimate size and that HAC/surface area can serve as alternatives)

## Labute surface area
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A proxy for molecular “size/exposed surface,” in the same family as volume and total surface area; it may indirectly affect solubility, membrane permeability, and protein binding.
- Brief note: In commonly used empirical medicinal chemistry rules such as Ro5, Veber, 3/75, 4/400, and PFI, the main variables are MW, logP/logD, PSA, RB, and aromatic rings. Total surface area and similar area metrics appear more often in fine-grained project-level modeling or as alternatives to MW.
- Source: Wiley chapter sample table (common rule sets); Johnson et al., 2009 (discussion of total surface area as a size surrogate)

## maximum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A proxy for strong local charge or polarization, which may relate to strong hydrogen-bonding sites or electronic effects near ionizable centers.
- Brief note: In publicly reproducible empirical filtering systems, atomic partial charges are more often used as continuous QSAR/QSPR features than as hard filtering rules. Therefore, it is better treated as an **interpretive feature** that supports pKa, PSA, and hydrogen-bond counts.
- Source: Reviews of common empirical rules, which focus mainly on MW, logP, PSA, and RB rather than hard thresholds for partial charge

## maximum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A proxy for the strongest positive charge, typically near strongly cationic centers, or for overall polarization.
- Brief note: As with “maximum absolute partial charge,” this is better treated as a model feature than as a threshold-based filter.
- Source: Wiley chapter sample table, reflecting the practical focus of common rule sets

## minimum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Information about the atom closest to electrical neutrality (the smallest absolute partial charge), which often lacks an intuitive medicinal chemistry interpretation.
- Brief note: This type of “extreme-value statistic” rarely appears in threshold-based medicinal chemistry rules. If used for model interpretation, it should usually be considered together with local structural context, such as proximity to ionizable centers or strong acceptors.
- Source: Wiley chapter sample table (common rule sets)

## minimum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A proxy for the strongest negative charge, usually near strongly anionic centers or strong acceptors, or for polarization.
- Brief note: To use this type of metric as an “interpretable threshold,” model- or dataset-specific calibration is usually required; stable universal hard cutoffs are not available in public medicinal chemistry rules.
- Source: Wiley chapter sample table (common rule sets)

## estimated logP
- Common threshold(s) or range(s):
  - **Ro5 (oral accessibility proxy)**: logP > 5 indicates a higher likelihood of poor absorption/permeation.
  - **3/75 (toxicity-risk proxy)**: Empirically, **logP > 3 and PSA < 75 Å²** is associated with increased risk of in vivo toxicity findings; in practice, this is often phrased as maintaining **logP < 3 and PSA > 75** to reduce risk.
  - **4/400 (general ADMET proxy)**: The combination of cLogP < 4 and MW < 400 is often used as a more favorable empirical boundary for ADMET.
- Usually associated with: Higher logP often leads to lower solubility, increased non-specific binding, and greater developability risks involving CYPs and hERG, and may also increase tissue distribution during chronic exposure.
- Brief note: For Carcinogens_Lagunin, “high logP” can at most help explain the dimension of **exposure/developability risk**; it cannot replace recognition of structural carcinogenic mechanisms. Therefore, it should be used together with structural alerts.
- Source: Lipinski et al., 2001 (Ro5); Wiley chapter sample table (3/75 and 4/400); Goetz & Shalaeva, 2018 (reuse of the 3/75 concept and associated risk framing)

## molecular weight
- Common threshold(s) or range(s):
  - **Ro5**: MW > 500 is a risk signal.
  - **4/400**: MW < 400 is an empirical boundary for general ADMET.
  - **Golden Triangle**: In MW–logD7.4 space, once **MW exceeds about 450**, the probability of being both “permeable and low clearance” drops sharply; the center is around MW ≈ 350.
- Usually associated with: Increasing MW is generally associated with greater flexibility, greater polarity, and poorer passive permeability, which indirectly reduces oral exposure. It may also alter metabolic pathways and the probability of forming reactive intermediates, though without a universal direction.
- Brief note: Veber’s analysis emphasizes that MW itself is not the best hard threshold and is often only a synthetic proxy for variables such as rotatable bonds and PSA.
- Source: Lipinski et al., 2001; Veber et al., 2002; Johnson et al., 2009; Wiley chapter sample table

## NH/OH group count
- Common threshold(s) or range(s):
  - **Ro5 HBD formulation**: H-bond donors, counted as OH + NH, above 5 indicate a higher likelihood of poor absorption/permeation.
- Usually associated with: More NH/OH groups generally increase hydrogen-bond donor capacity and PSA, reduce passive permeability, and increase solvation, often in the same direction as lower logP/logD.
- Brief note: This count strongly overlaps with “hydrogen-bond donor count.” In carcinogenicity tasks, it behaves more like an **exposure/permeability proxy** than a mechanism-specific variable.
- Source: Lipinski et al., 2001 (OH + NH as HBD)

## nitrogen/oxygen atom count
- Common threshold(s) or range(s):
  - **Approximate Ro5 HBA formulation**: In that paper, H-bond acceptors are approximately described by the **number of N + O atoms**; when N + O > 10, poor absorption/permeation becomes more likely.
- Usually associated with: More N/O atoms generally increase acceptor count and PSA, increase polarity, and reduce passive permeability, while sometimes improving solubility.
- Brief note: N + O does not always equal HBA, for example in quaternary ammonium compounds or amides, but as a coarse anchor for “polarity burden” it is widely cited in the Ro5 context.
- Source: Lipinski et al., 2001 (N + O as an approximate HBA count)

## aliphatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More saturated/aliphatic carbocycles rather than aromatic rings generally make structures more 3D and may improve certain developability risks, though the outcome depends on the full combination of logD, RB, PSA, and related properties.
- Brief note: The literature more often provides thresholds for **aromatic ring count** rather than hard thresholds for aliphatic carbocycle count. In practice, “increasing saturation” is usually treated as a directional design strategy rather than a split rule.
- Source: Wei et al., 2020 (discussion of Fsp3 and 3D character); Ritchie & Macdonald, 2009 (importance of aromatic ring count for developability)

## aliphatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Aliphatic heterocycles often increase both 3D shape and heteroatom content, affecting polarity, hydrogen bonding, logD, PSA, and transporters in both directions depending on context.
- Brief note: No consistent universal threshold exists; a more robust approach is to capture its influence indirectly through PSA, logD, HBD/HBA, and RB.
- Source: Common integrated rules such as Veber and Golden Triangle, which reflect the practice of using multiparameter criteria rather than single ring-count thresholds

## aliphatic ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More aliphatic rings often reduce molecular flexibility (fewer rotatable bonds) and increase 3D shape, though they may also increase hydrophobicity depending on substitution.
- Brief note: If one wants to impose thresholds, practice more often does so on RB, logD, or PFI rather than on aliphatic ring count alone.
- Source: Veber et al., 2002 (RB threshold); RSC Med. Chem. 2021 (PFI as a quality metric)

## aromatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More aromatic carbocycles generally increase logP/logD, reduce aqueous solubility, and move in the same direction as CYP/hERG and protein-binding risk from a neighboring-task developability perspective.
- Brief note: Publicly reproducible empirical rules more commonly use thresholds like “total aromatic ring count > 3”; hard thresholds specifically separating aromatic carbocycles from aromatic heterocycles are not stable in the accessible sources used here.
- Source: Ritchie & Macdonald, 2009 (total aromatic ring count and developability); Bunally, 2019 (independent negative effect of aromatic ring count on solubility)

## aromatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More aromatic heterocycles still represent increased aromaticity, but they also introduce heteroatoms and raise PSA/HBA, so their effects on logD, solubility, and permeability may be non-monotonic.
- Brief note: In practice, it is better to start from the overall threshold anchor for **aromatic ring count** (>3 as a risk signal) together with PFI (logD7.4 + #Ar), and then distinguish carbocycle versus heterocycle contributions at the specific structural level.
- Source: Ritchie & Macdonald, 2009; RSC Med. Chem. 2021 (PFI definition and target)

## aromatic ring count
- Common threshold(s) or range(s):
  - **Key anchor (neighboring-task developability proxy)**: Literature gives the clear conclusion that **“more than three aromatic rings”** is associated with poorer developability and higher attrition risk in development.
  - **PFI quality metric**: PFI = Chrom logD7.4 + #Ar, and **PFI < 6** is used as a more desirable target. This is equivalent to limiting #Ar at a given logD or limiting logD at a given #Ar.
- Usually associated with: Higher aromatic ring count is associated with lower solubility, greater lipophilicity, increased serum albumin binding, and higher risks for certain CYP inhibition and hERG issues.
- Brief note: For rodent carcinogenicity, aromatic rings themselves are not a necessary carcinogenic mechanism. However, greater aromaticity can change metabolic activation and long-term tissue exposure patterns, and it co-occurs more often with several structural alerts such as PAHs, aromatic amines, and nitroaromatics. Therefore, in this task it is a very useful **upstream risk indicator**.
- Source: Ritchie & Macdonald, 2009 (aromatic ring threshold and trends); RSC Med. Chem. 2021 (PFI < 6); Wiley chapter sample table (PFI definition and practical note)

## hydrogen-bond acceptor count
- Common threshold(s) or range(s):
  - **Ro5**: HBA > 10 indicates a higher likelihood of poor absorption/permeation.
  - **Veber (alternative formulation)**: HBD + HBA ≤ 12 can be used as an empirical screen equivalent to PSA ≤ 140 Å².
- Usually associated with: More HBAs increase polarity and solvation and often reduce passive membrane permeability, though they may also improve solubility and affect transporter interactions.
- Brief note: In carcinogenicity tasks, the relevance is mainly indirect through **exposure/distribution** and clustering of structural classes; the true mechanism depends more on structural alerts and metabolic activation.
- Source: Lipinski et al., 2001; Veber et al., 2002

## hydrogen-bond donor count
- Common threshold(s) or range(s):
  - **Ro5**: HBD > 5 indicates a higher likelihood of poor absorption/permeation.
  - **Veber (alternative formulation)**: HBD + HBA ≤ 12, interchangeable with PSA ≤ 140 Å² as a screening criterion.
- Usually associated with: More HBDs usually lead to higher PSA and stronger hydration, reducing passive permeability and potentially altering metabolism and binding.
- Brief note: Like HBA, HBD is usually an **exposure/developability proxy** rather than a mechanistic carcinogenicity threshold.
- Source: Lipinski et al., 2001; Veber et al., 2002

## heteroatom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More heteroatoms are usually associated with higher PSA, stronger hydrogen-bonding potential, and greater polarity, but the direction differs by heteroatom type, such as N, O, S, or halogens.
- Brief note: In Ro5, HBA is often approximated by the count of N + O, but “heteroatom count” is broader and lacks a unified threshold. In practice, thresholds are applied more often to HBA/HBD and PSA.
- Source: Lipinski et al., 2001; Veber et al., 2002

## rotatable-bond count
- Common threshold(s) or range(s):
  - **Veber**: rotatable bonds ≤ 10 and PSA ≤ 140 Å², or HBD + HBA ≤ 12, are associated with a higher probability of good oral bioavailability.
  - Veber’s dataset also showed that compounds with rotatable bonds **>10** more often exhibited lower oral bioavailability, especially within its MW groupings.
- Usually associated with: More rotatable bonds (greater flexibility) usually increase conformational entropy penalties, reduce membrane permeability and oral absorption probability, and may also increase exposure of metabolic sites.
- Brief note: For carcinogenicity, RB mainly acts through an **exposure/ADMET proxy role** rather than as a direct mechanistic threshold.
- Source: Veber et al., 2002 (thresholds and trend conclusions)

## saturated carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A higher proportion of saturated carbocycles often tracks with higher Fsp3 and more 3D structure, potentially improving solubility and reducing non-specific risks caused by excessive aromaticity, depending on logD and substitution.
- Brief note: There is no unified count threshold; more robust anchors are Fsp3 and aromatic ring count.
- Source: Wei et al., 2020; Ritchie & Macdonald, 2009

## saturated heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Saturated heterocycles often increase both 3D character and polarity due to heteroatoms, leading to trade-offs in logD, PSA, permeability, and transporter effects.
- Brief note: No unified threshold exists; it is better controlled indirectly using logD (Golden Triangle), PSA (Veber), and HBD/HBA (Ro5/Veber).
- Source: Johnson et al., 2009; Veber et al., 2002; Lipinski et al., 2001

## saturated ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More saturated rings may reduce RB (greater rigidity) and increase 3D character, moving in the same direction as Fsp3.
- Brief note: “Saturated ring count” itself lacks a recognized threshold and is used more as an explanatory structural descriptor.
- Source: Wei et al., 2020; Veber et al., 2002 (RB and accessibility)

## ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Total ring count reflects structural complexity and rigidity, but the **type of ring**—aromatic vs. aliphatic, carbocycle vs. heterocycle, fused vs. isolated—is usually more important than the total count itself.
- Brief note: The literature explicitly points out that **aromatic ring count** may be more predictive than **total ring count** in developability analysis, so thresholds for total ring count are unstable in public empirical rules.
- Source: Ritchie & Macdonald, 2009 (emphasis on aromatic ring count over total ring count)

## topological polar surface area
- Common threshold(s) or range(s):
  - **Veber**: TPSA ≤ 140 Å², or equivalently HBD + HBA ≤ 12, is associated with a higher probability of good oral bioavailability.
  - **3/75 (toxicity-risk proxy)**: The rule is often phrased as maintaining **PSA > 75 and cLogP < 3** to reduce in vivo toxicity risk; equivalently, the combination of PSA < 75 and logP > 3 is less favorable.
- Usually associated with: Higher TPSA usually lowers passive permeability and brain penetration and improves aqueous solubility; very low TPSA together with high logP is associated with greater non-specific binding and toxicity risk in neighboring-task practice.
- Brief note: In rodent carcinogenicity tasks, TPSA behaves more like a **systemic exposure/distribution proxy**; actual carcinogenic discrimination still depends heavily on structural alerts and metabolic activation.
- Source: Veber et al., 2002; Wiley chapter sample table; Goetz & Shalaeva, 2018 (3/75 risk framing)

## QED drug-likeness
- Common threshold(s) or range(s):
  - QED is a continuous variable (0–1). The original study gave **distribution anchors** for sets considered “chemically attractive” and “unattractive”: the attractive set had mean QED ≈ **0.67** (s.d. ≈ 0.16), while the unattractive set had mean QED ≈ **0.49** (s.d. ≈ 0.23), and the “too complex” set had an even lower mean.
  - Some applications use **QED ≥ 0.5** as a threshold for being “more drug-like,” for example when summarizing datasets with a 0.5 cutoff.
- Usually associated with: Higher QED usually means the compound simultaneously satisfies, or comes close to satisfying, several classic oral-drug property preferences, such as MW, logP, PSA, HBD/HBA, aromatic rings, and RB. Therefore, it is more a proxy for developability and oral drug-likeness than a carcinogenicity mechanism metric.
- Brief note: For Carcinogens_Lagunin, QED is better viewed as a summary feature of overall drug-like shape. It may capture exposure-related properties, but **it cannot replace structural alerts**. For interpretation, it is better to decompose QED back into its components, such as logP/logD, PSA, aromatic ring count, and RB, to see what actually drives the model.
- Source: Bickerton et al., 2012 (QED distribution anchors); RDKit QED documentation (QED components); Scientific Reports 2022 (example use of QED ≥ 0.5)

## Functional-group notes
- Group name: Alkyl and aryl N-nitroso groups
- Usually associated with: B (carcinogen; typically associated with genotoxic pathways)
- Brief note: In the ISS carcinogenicity structural-alert list, “Alkyl and aryl N-nitroso groups” are explicit alert categories and showed relatively high positive predictive value in statistics derived from the ISSCAN dataset.
- Source: “Carcinogenicity (genotox and nongenotox) alerts by ISS” profiler

- Group name: Nitro-aromatic
- Usually associated with: B (increased carcinogenic risk, often associated with mutagenicity and metabolic reductive activation)
- Brief note: The ISS structural alerts include a “Nitro-aromatic (Genotox)” category; within the alert framework, this is a common genotoxicity-related substructure.
- Source: ISS carcinogenicity alerts profiler

- Group name: Primary aromatic amine / hydroxylamine and derived esters
- Usually associated with: B (elevated carcinogenic risk; a classic pathway involving metabolic activation and electrophilic intermediates)
- Brief note: The ISS alert list explicitly includes “Primary aromatic amine, hydroxyl amine and its derived esters” as a genotoxic carcinogenic structural alert.
- Source: ISS carcinogenicity alerts profiler; JRC report emphasizing structural alerts for identifying potentially mutagenic/carcinogenic chemical reactivity

- Group name: Epoxides and aziridines
- Usually associated with: B (strong electrophiles / alkylation-related reactivity; typically genotoxic)
- Brief note: The ISS alert list includes “Epoxides and aziridines” as genotoxic carcinogenic structural alerts; these functional groups are commonly included in alert sets for reactivity and alkylation risk.
- Source: ISS carcinogenicity alerts profiler; JRC structural alert and QSAR compilation report

- Group name: alpha,beta-unsaturated carbonyls
- Usually associated with: B (increased risk of electrophilic addition and covalent binding; typically a genotoxic alert)
- Brief note: The ISS alert list includes “alpha,beta-unsaturated carbonyls (Genotox)”; these structures are classic substructure indicators of electrophilic reactivity and covalent-binding risk.
- Source: ISS carcinogenicity alerts profiler; JRC report compiling structural alerts and mechanisms

- Group name: S or N mustard
- Usually associated with: B (strong alkylation/crosslinking; classic genotoxic pathway)
- Brief note: The ISS alert list explicitly includes “S or N mustard (Genotox)”; these are high-priority alerts for strong alkylating functionality.
- Source: ISS carcinogenicity alerts profiler

- Group name: Alkyl (C<5) or benzyl ester of sulphonic or phosphonic acid
- Usually associated with: B (increased alkylation/electrophilic reactivity risk)
- Brief note: The ISS alert list includes these small-alkyl or benzyl sulfonate/phosphonate esters as genotoxic carcinogenic structural alerts.
- Source: ISS carcinogenicity alerts profiler

- Group name: Hydrazine
- Usually associated with: B (increased carcinogenic risk, associated with metabolic activation and reactive intermediates)
- Brief note: The ISS alert list includes “Hydrazine (Genotox).”
- Source: ISS carcinogenicity alerts profiler

- Group name: Aromatic diazo / azo / azoxy
- Usually associated with: B (increased carcinogenic risk, potentially associated with reductive metabolism yielding aromatic amines and related pathways)
- Brief note: The ISS alert list includes entries such as “Aromatic diazo (Genotox)” and “Aliphatic azo and azoxy (Genotox),” indicating clear relevance within the alert framework.
- Source: ISS carcinogenicity alerts profiler

- Group name: Polycyclic Aromatic Hydrocarbons (PAHs) and Heterocyclic PAHs
- Usually associated with: B (one of the classic genotoxic carcinogen classes)
- Brief note: The ISS alert list includes both “Polycyclic Aromatic Hydrocarbons (Genotox)” and “Heterocyclic Polycyclic Aromatic Hydrocarbons (Genotox)” as alert categories.
- Source: ISS carcinogenicity alerts profiler

- Group name: Quinones
- Usually associated with: B (risk mechanisms involving redox cycling and electrophilic addition; typically a genotoxic alert)
- Brief note: The ISS alert list includes “Quinones (Genotox).”
- Source: ISS carcinogenicity alerts profiler

- Group name: Simple aldehyde
- Usually associated with: B (reactive carbonyl-related risk; a genotoxic category in the alert framework)
- Brief note: The ISS alert list includes “Simple aldehyde (Genotox).”
- Source: ISS carcinogenicity alerts profiler

Input 2. Single-molecule analysis notes
First, 2H-chromen-2-one is present (1). The global EBM contribution here is -0.7378, which pushes toward option (A): is not a carcinogen. Next, neutral fraction is value 0.9998. The global EBM contribution here is -0.1656, which pushes toward option (A): is not a carcinogen. Then, aliphatic ring count is value 0. The global EBM contribution here is 0.1355, which pushes toward option (B): is a carcinogen. After that, QED drug-likeness is value 0.7181. The global EBM contribution here is -0.1261, which pushes toward option (A): is not a carcinogen. Finally, aliphatic heterocycle count is value 0. The global EBM contribution here is 0.1207, which pushes toward option (B): is a carcinogen. Step 6, secondary amide is present (1). The global EBM contribution here is -0.1195, which pushes toward option (A): is not a carcinogen. Step 7, strongest basic pKa is value 3.698. The global EBM contribution here is 0.0935, which pushes toward option (B): is a carcinogen. Step 8, aromatic heterocycle count is value 1. The global EBM contribution here is -0.0879, which pushes toward option (A): is not a carcinogen. Step 9, saturated ring count is value 0. The global EBM contribution here is 0.0846, which pushes toward option (B): is a carcinogen. Step 10, strongest acidic pKa is value 13.0268. The global EBM contribution here is -0.0818, which pushes toward option (A): is not a carcinogen. Taken together, these global descriptor-level signals make the model predict option (A): is not a carcinogen with score 0.9235.

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
