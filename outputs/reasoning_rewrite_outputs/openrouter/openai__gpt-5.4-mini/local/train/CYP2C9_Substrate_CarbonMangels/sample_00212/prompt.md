You are rewriting rough neighbor-based molecule-comparison notes from Explainable Boosting Machine (EBM) into high-quality reasoning SFT data for molecule local analog-comparison task CYP2C9_Substrate_CarbonMangels where option (A) means is not a substrate to the enzyme CYP2C9 and option (B) means is a substrate to the enzyme CYP2C9.

Input 1. Task playbook
# CYP2C9_Substrate_CarbonMangels Practical Guide to Molecular Property Assessment

## neutral fraction
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: **B (substrate)** is more commonly observed when a compound exists to some extent as an **anion/negatively charged species** under physiological conditions; **A (non-substrate)** is more common in the "fully neutral + low-affinity" chemical space, but this is not absolute
- Brief note: This task comes from the PyTDC binary classification dataset for "whether a compound is a CYP2C9 substrate." Mechanistic and structural studies emphasize that CYP2C9 shows selectivity for ligands that are **negatively charged or can form anions at physiological pH** (related to electrostatic/salt-bridge interactions with Arg108 in the active site), but it can also metabolize **neutral and highly hydrophobic** compounds, so "neutral fraction" is difficult to summarize with a single threshold. 
- Source: Miners & Birkett (many CYP2C9 substrates are weak acids; pKa range), Dickmann et al. (many substrates are negatively charged at physiological pH; Arg108 is linked to selectivity for anionic substrates), Zhou et al. review (neutral highly hydrophobic compounds can also be metabolized), PyTDC dataset description. 

## estimated logD
- Common threshold(s) or range(s): common **nearby-domain anchors (ADMET/permeability/global properties)**: Egan/permeability filters often use **0 ≤ logD ≤ 3** (together with MW ≤ 500); the "Golden Triangle" often uses **−2 ≤ logD ≤ 5** (together with 200 ≤ MW ≤ 500) as a broader reference for developable chemical space (both are proxies). 
- Usually associated with: **B** tends toward a moderate logD that allows entry into a hydrophobic active pocket (though higher values are also possible); **A** may be more common in the very low-logD region (highly hydrophilic, difficult to enter a hydrophobic pocket), though this depends on the dataset and chemical space
- Brief note: For **CYP2C9 substrate/non-substrate** classification itself, public reviews emphasize an **acidic anion anchor + hydrophobic/aromatic interactions** rather than providing a unified logD threshold; therefore, the numeric values above are better used as neighborhood rules for **chemical space and developability/permeability**. 
- Source: Kralj et al. summary of common filter thresholds (including Egan and logD conditions), ADMETlab/"Golden Triangle" threshold summaries; Zhou et al. review on the ability to metabolize neutral highly hydrophobic substrates. 

## strongest acidic pKa
- Common threshold(s) or range(s): **known drug substrates of CYP2C9 are often weak acids**, with reported acidic pKa values/distributions ranging from **3.8–8.1** (one of the anchors most closely tied to the "substrate chemistry" of this task). Some broad heuristic summaries describe CYP2C9 substrates as "tending to be acidic (for example, pKa ≤ 5)," but this is likely narrower in coverage and should be regarded as a coarse proxy. 
- Usually associated with: **B** is more common when there is an acidic site that can generate a substantial anionic fraction at physiological pH (favoring electrostatic/salt-bridge interaction with Arg108); **A** is more common when no acid site capable of forming an anion is present (though neutral highly hydrophobic exceptions exist)
- Brief note: Structural and mutagenesis studies support the idea that an **anionic group ↔ Arg108** interaction is an important source of CYP2C9 selectivity; thus, in this task, "strongest acidic pKa" is often closer to mechanism than pure hydrophobicity. 
- Source: Miners & Birkett (weakly acidic substrates and pKa range), Dickmann et al. (negatively charged substrates and Arg108 selectivity), Tai et al. (crystallographic support for anionic group–Arg108 charge pairing), ScienceDirect topic page as a coarse heuristic proxy. 

## strongest basic pKa
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: **B** does not require "high basicity"; most classic substrates are weak acids, but CYP2C9 can also catalyze some **basic drugs** (such as substrates undergoing certain N-demethylation reactions)
- Brief note: "Strongest basic pKa" alone is difficult to use as a monotonic discriminator of substrate status; its role is more often reflected through the **neutral fraction/charge distribution** and whether the molecule can **enter the hydrophobic pocket and adopt the correct binding pose**. 
- Source: Daly review (most substrates are weak acids, but basic substrates and reaction-type differences also exist), Zhou review (substrate diversity). 

## number of acidic sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: **B** is more common when at least one acidic site can generate an anion (the "weak-acid substrate" narrative); multiple acidic sites are not required
- Brief note: The key mechanistic anchor for CYP2C9 is that **one anionic/negatively charged group can pair with Arg108**; therefore, the "number of acidic sites" is a coarser descriptor than "whether there is at least one suitable acidic site and what its pKa is." 
- Source: Miners & Birkett (weakly acidic substrates are common), Tai et al. (anionic group–Arg108), Dickmann et al. (negatively charged substrates and Arg108). 

## number of basic sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable one-way association; **B** can include a small number of basic substrates, but the overall narrative still favors "weakly acidic substrates are the majority"
- Brief note: "Number of basic sites" more often influences total charge/neutral fraction and logD (in a pH-dependent manner), rather than defining a unified threshold for CYP2C9 substrate status. 
- Source: Daly review, Zhou review. 

## number of ionizable sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable one-way association; in this task it behaves more like a coarse feature for "ionization complexity/polymorphism"
- Brief note: CYP2C9 substrate status is more often linked to **whether there is a group that is anionic at physiological pH + hydrophobic/aromatic binding**, whereas the total number of ionizable sites itself lacks a standard threshold. 
- Source: Tai et al. (acidic/charge-pairing mechanism), Zhou review (substrate diversity). 

## exact molecular weight
- Common threshold(s) or range(s): commonly used (proxy) thresholds: Lipinski RO5 **MW < 500**; GSK/"4/400"-type empirical region **MW < 400** (more oriented toward better developability/lower ADMET risk); Ghose filter common range **180–480**; "Golden Triangle" commonly **200–500** (combined with logD conditions). 
- Usually associated with: both **B** and **A** may fall within these ranges; extremely small or extremely large values tend to first affect **entry/binding/transportability** rather than CYP2C9 specificity
- Brief note: For CYP2C9 substrate status, the literature emphasizes **charge and key interactions** more strongly, but MW is still a basic constraint that determines whether a molecule can **enter the CYP active cavity and form an effective binding pose** (so using general thresholds as chemical-space gatekeepers is more realistic). 
- Source: admetSAR summary of RO5/GSK/Pfizer/Golden Triangle rules; Gleeson ("more ideal region" of MW<400 & cLogP<4); common summaries of Lipinski/Ghose; Kralj summary of common filters. 

## fraction of sp3 carbons
- Common threshold(s) or range(s): as an anchor for "complexity/3D character" (proxy), some studies use **0.3** and **0.6** as segmentation thresholds in Fsp3-based categorization (not CYP2C9-specific substrate thresholds). 
- Usually associated with: classic CYP2C9 substrates (such as NSAIDs) often contain aromatic rings and relatively low Fsp3, but this is only a family resemblance, not a hard rule
- Brief note: CYP2C9 binding often involves aromatic/hydrophobic interactions and an anionic anchor; therefore, Fsp3 is better viewed as a proxy for **shape/planarity** rather than an independent determinant. 
- Source: Lovering (definition of Fsp3 and the "escape from flatland" concept), Spacial Score-related work (examples of Fsp3 segmentation thresholds), Nair et al. (examples of aromatic π–π interactions and Arg108 anionic interactions). 

## heavy-atom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: general developability filters related to molecular size sometimes use anchors such as "total atom count 20–70" (Ghose, including hydrogens); heavy-atom count depends on definition and is difficult to transfer directly
- Brief note: In the CYP2C9 substrate task, heavy-atom count is more of a proxy for **size/volume/surface area**; the literature less often gives clearly transferable thresholds using heavy-atom count. 
- Source: summaries of Lipinski extensions/Ghose filter, Kralj summary of common medicinal-chemistry filters. 

## heavy-atom molecular weight
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: highly collinear with MW; therefore the general MW threshold space is usually reused as a proxy
- Brief note: This descriptor is often used in machine-learning models to capture the "non-hydrogen atomic mass contribution"; there is little tradition of independent hand-crafted thresholds for CYP2C9 substrate status. 
- Source: common medicinal-chemistry filters (MW/logP/TPSA, etc.) as neighborhood proxies. 

## Labute surface area
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: related to molecular size/shape; indirectly affects entry into the CYP active cavity and surface complementarity upon binding
- Brief note: In both literature and practice, descriptors such as **MW, (t)PSA, logP/logD, flexibility (rotatable bonds)** are more commonly used than "absolute surface-area thresholds"; for CYP2C9, the emphasis is on the anionic anchor and aromatic/hydrophobic interactions. 
- Source: Tai et al. (anion–Arg108 mechanism), Veber (PSA/rotatable-bond thresholds as substitutes for "shape/polarity"), Kralj (filter summary). 

## maximum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: **B** is more common when a stable anion/strong negative center is present (such as a carboxylate oxygen) that can form charge pairing with Arg108 of CYP2C9, though the specific "charge value" is highly dependent on the charge model
- Brief note: "Maximum absolute partial charge" is a method-dependent QSAR electronic descriptor; CYP2C9-related literature more often uses qualitative mechanistic language such as "whether the compound is anionic" or "whether it has a group capable of charge pairing." 
- Source: Tai et al. (anionic group–Arg108), Dickmann et al. (negatively charged substrates and Arg108 selectivity). 

## maximum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable one-way association; more often reflects the presence or absence of a strong positive center (such as a protonated amine) at a given pH
- Brief note: The substrate-preference narrative for CYP2C9 focuses much more on **anionic pairing** than on **strong cationic pairing** (the latter is more typical of the classic mechanistic framework for CYP2D6). 
- Source: Tai et al. (acidic/anionic preference mechanism of 2C9), broad isoform distinction summaries (coarse-grained summary that 2C9 tends to prefer acidic compounds while 2D6 tends to prefer basic compounds). 

## minimum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: mostly a proxy for whether the charge distribution is polarized; it does not directly correspond to a transferable hand-crafted threshold
- Brief note: For CYP2C9, the key is whether there is a site that can form an anion and interact with Arg108, rather than the "minimum absolute charge" itself. 
- Source: mechanistic evidence from Dickmann et al. and Tai et al. regarding Arg108/anionic substrates. 

## minimum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: **B** is more common when a strong negative center is present (such as carboxylate O), but the specific negative value depends on the charge calculation method
- Brief note: In practice, a more transferable approach is to use **"whether there is an acidic functional group capable of anion formation + its pKa"** instead of a "partial-charge threshold." 
- Source: Miners & Birkett (weakly acidic substrates), Tai et al. (anion–Arg108), Dickmann et al. (selectivity for negatively charged substrates). 

## estimated logP
- Common threshold(s) or range(s): general (proxy) thresholds: Lipinski RO5 **logP ≤ 5**; Ghose common range **−0.4 ≤ logP ≤ 5.6**; GSK/"4/400" empirical region **logP ≤ 4**; Pfizer "3/75" often uses **logP > 3** as one of the conditions for in vivo toxicity-risk screening (together with TPSA < 75). 
- Usually associated with: **B** often requires some degree of hydrophobicity to enter the CYP active cavity, but CYP2C9 also includes classic substrates that are **acidic and relatively polar**; **A** may be more common in extremely low-logP, highly hydrophilic space
- Brief note: The CYP2C9 literature notes that **neutral highly hydrophobic substrates can also be metabolized**, indicating that logP should not be misused as a single-threshold discriminator; it is more reliable when interpreted jointly with **acidic/anionic sites (pKa)**. 
- Source: admetSAR rule summary (RO5/GSK/Pfizer), Lipinski extension/Ghose interval summaries; Zhou and Tai/Dickmann on substrate diversity and evidence for the anionic mechanism. 

## molecular weight
- Common threshold(s) or range(s): same as "exact molecular weight": RO5 **<500**; more conservative development-oriented regions commonly use **<400**; Ghose **180–480**; Golden Triangle **200–500** (all are proxies). 
- Usually associated with: both **B** and **A** are possible; extreme MW values more often first affect pharmacokinetics/exposure and the ability to enter the active cavity
- Brief note: In this task, MW is mainly a chemical-space constraint variable; what is closer to CYP2C9 mechanism is usually **whether the compound is a weak acid/can form an anion + aromatic/hydrophobic interactions**. 
- Source: admetSAR (RO5/GSK/Golden Triangle), Gleeson (4/400), Miners/Tai (weak acids and Arg108 mechanism), Nair et al. (examples of aromatic/π–π and Arg108 interactions). 

## NH/OH group count
- Common threshold(s) or range(s): common proxy: in RO5, hydrogen-bond donors (roughly equivalent to NH/OH count) **HBD ≤ 5**; more lead-like filters sometimes use lower thresholds (for example, HBD ≤ 5 or smaller), but there is no single standard. 
- Usually associated with: no stable one-way association; increasing NH/OH usually raises polarity, lowers permeability, and affects logD
- Brief note: For CYP2C9 substrate status, NH/OH is more likely to influence entry into the hydrophobic pocket indirectly by changing overall polarity and ionization state; there is no unified NH/OH threshold directly tied to substrate status. 
- Source: admetSAR summary of RO5 thresholds; Kralj summary of filter thresholds; Zhou review on substrate diversity. 

## nitrogen/oxygen atom count
- Common threshold(s) or range(s): common proxy: RO5 **HBA ≤ 10** is often approximated as an upper bound where the "N/O atom count (or its effective count) is not too high"; different implementations generally use HBA (more reasonable) rather than simple N+O count. 
- Usually associated with: increasing N/O usually raises polarity and HBA, which may weaken hydrophobic binding; however, for **weakly acidic substrates**, a small number of key O atoms (such as in a carboxylate) are mechanistically important
- Brief note: It is generally better to rely on **hydrogen-bond acceptor count** and **topological polar surface area** to represent "polarity/acceptor capability," rather than treating N/O atom count as a transferable threshold. 
- Source: admetSAR (RO5), Veber (PSA threshold), Kralj (common threshold organization for HBA/HBD/PSA in filters), Tai (mechanistic role of anionic groups). 

## aliphatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable one-way association; more reflective of **ring-system scaffold type/3D character**, and may influence CYP2C9 indirectly through shape and hydrophobic contact
- Brief note: Filters and reviews more often use **total ring count / aromatic ring count / rotatable bonds / PSA** as coarser constraints. 
- Source: Kralj (thresholds for ring/aromatic ring in common filters), Ritchie (too many aromatic rings and developability risk). 

## aliphatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable one-way association; may exert indirect effects by introducing acceptors/donors or changing pKa/logD
- Brief note: The CYP2C9 **weak-acid/anionic anchor** is closer to the mechanistic core; aliphatic heterocycles are more often a **structural-domain** feature. 
- Source: Miners (weakly acidic substrates are common), Tai (anion–Arg108 mechanism). 

## aliphatic ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable one-way association; covaries with total ring count, Fsp3, and logP/logD
- Brief note: If a "ring-count" anchor is needed, practice often cites total-ring thresholds from lead-like/filter rules (for example, rings ≤4 or ≤6), but these are developability proxies, not CYP2C9-specific rules. 
- Source: Kralj summary of common filters (including examples of ring thresholds). 

## aromatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: classic CYP2C9 substrate classes (such as NSAIDs) often contain aromatic carbocycles involved in hydrophobic/π interactions, but this does not mean "more is always better"
- Brief note: From a **developability** perspective, too many aromatic rings (especially >3) are associated with risk; by contrast, CYP2C9 mechanistic literature emphasizes **aromatic/hydrophobic interactions + an anionic anchor** rather than a simple aromatic-ring-count threshold. 
- Source: Ritchie (>3 aromatic rings and developability risk), Nair et al. (examples of aromatic π–π and Arg108 anionic interactions), Tai (anionic mechanism). 

## aromatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable one-way association; aromatic heterocycles may contribute both π interactions and HBA, and may also serve as part of bioisosteres for acidic groups, though this requires structure-specific judgment
- Brief note: The key mechanistic anchor for CYP2C9 still lies closer to the **anionizable site** rather than simply **whether an aromatic heterocycle is present**. 
- Source: Miners (weakly acidic substrates are common), Tai (anion–Arg108), Zhou (substrate diversity). 

## aromatic ring count
- Common threshold(s) or range(s): general developability anchor: **>3 aromatic rings** is associated with **poorer developability/higher attrition risk**, and is a commonly cited empirical threshold (a proxy, not CYP2C9-specific). 
- Usually associated with: **B** often contains 1–3 aromatic rings, consistent with hydrophobic/π interactions; **A** is not guaranteed by fewer or more aromatic rings, though >3 often brings other ADMET risks
- Brief note: For CYP2C9, **whether there is a suitable anionic anchor (acidic site and pKa)** is usually closer to mechanism than **the number of aromatic rings**; aromatic-ring count is better used as a tool for developability/chemical-space screening. 
- Source: Ritchie (aromatic-ring threshold and developability), Dickmann/Tai (mechanistic evidence for anion–Arg108), Ward et al. summary view that ">3 aromatic rings is undesirable." 

## hydrogen-bond acceptor count
- Common threshold(s) or range(s): common proxy: RO5 **HBA ≤ 10**; some lead-like rules use tighter HBA ceilings (for example, ≤8), depending on the rule set. 
- Usually associated with: increasing HBA generally increases polarity and TPSA; there is no monotonic threshold for CYP2C9 substrate status, but key acceptors (such as carboxylate oxygens) are important in the **anionic anchor** mechanism
- Brief note: In practice, it is advisable to interpret HBA together with **TPSA/logD/pKa**; stable literature support is lacking for using HBA threshold alone to judge CYP2C9 substrate status. 
- Source: admetSAR (RO5), Kralj (common filters and HBA thresholds), Tai/Miners (weakly acidic substrates and anionic mechanism). 

## hydrogen-bond donor count
- Common threshold(s) or range(s): common proxy: RO5 **HBD ≤ 5**; some lead-like rules tighten this further (such as ≤3 or ≤4), but there is no single standard. 
- Usually associated with: increasing HBD generally raises polarity and lowers permeability; there is no unified single threshold for CYP2C9 substrate status
- Brief note: Classic CYP2C9 substrates (such as NSAIDs) can bind strongly even when HBD is not high; therefore, HBD is better treated as a general developability/permeability proxy. 
- Source: admetSAR (RO5), Kralj (filter summary), Zhou (substrate diversity). 

## heteroatom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: covaries with polarity/TPSA/HBA/HBD; there is no unified threshold for CYP2C9 substrate status
- Brief note: More transferable thresholds usually lie in combined rules involving **TPSA, HBA/HBD, logP/logD, MW**, rather than total heteroatom count. 
- Source: the filter-threshold frameworks of Veber and Kralj. 

## rotatable-bond count
- Common threshold(s) or range(s): classic oral-bioavailability proxy: Veber rule **rotatable bonds ≤ 10**. 
- Usually associated with: excessively high flexibility often lowers permeability and increases entropic penalty; it is not a CYP2C9-specific threshold, but it does affect **whether an effective binding conformation can be formed**
- Brief note: Like other CYP enzymes, CYP2C9 requires the substrate to adopt an appropriate conformation near the heme; thus, rotatable bonds is a neighborhood feature for **accessibility of a bindable conformation**, but it does not replace the **acidic/anionic anchor** mechanism. 
- Source: Veber (≤10 threshold), Tai (2C9 mechanism emphasizing anion–Arg108). 

## saturated carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable one-way association; more often influences 3D character and hydrophobic bulk
- Brief note: If ring-related thresholds are needed, general developability thresholds for total ring count or aromatic ring count are usually used instead. 
- Source: Kralj (filter summary), Ritchie (aromatic-ring threshold). 

## saturated heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable one-way association; may exert indirect effects through pKa/logD/acceptor distribution
- Brief note: The more stable mechanistic handle for CYP2C9 is **charge pairing between a weakly acidic/anionic group and Arg108**. 
- Source: Arg108 mechanistic evidence from Tai and Dickmann. 

## saturated ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable one-way association; covaries with Fsp3, logP, and shape
- Brief note: Transferable thresholds usually come from lead-like/library-design rules such as **total ring count ≤4/≤6** (proxies), rather than CYP2C9-substrate-specific thresholds. 
- Source: Kralj (filter summary, including examples of ring thresholds). 

## ring count
- Common threshold(s) or range(s): common proxies (library design/lead-like): Oprea lead-like rules often use **number of rings ≤ 4**; looser ring-count thresholds (such as ≤6) also appear in other filters, depending on the rule set. 
- Usually associated with: both **B** and **A** are possible; higher ring counts often bring changes in solubility, viscosity, metabolism, and interaction risk, but this is not CYP2C9-specific
- Brief note: CYP2C9 substrates are closer to the mechanism of **an anionic anchor + aromatic/hydrophobic interactions**; ring count is more suitable as a proxy for **scaffold complexity/rigidity**. 
- Source: Kralj (threshold summary for Oprea lead-like and other filters), Tai (anionic mechanism), Nair (examples of aromatic/π–π and Arg108 interactions). 

## topological polar surface area
- Common threshold(s) or range(s): classic proxy: Veber rule **TPSA ≤ 140 Å²**; Pfizer "3/75" commonly uses **TPSA < 75 Å²** as one of the conditions (together with logP > 3) when assessing in vivo toxicity risk. 
- Usually associated with: excessively high TPSA often lowers permeability and may reduce the chance of entering a hydrophobic active pocket; however, **weakly acidic anionic** CYP2C9 substrates may themselves still have some TPSA
- Brief note: TPSA is one of the most commonly used and transferable thresholds for **polarity/exposed surface area**, but it describes overall PK developability and permeability rather than CYP2C9-specific substrate status; in this task it is best interpreted together with **pKa/neutral fraction/logD**. 
- Source: Veber (TPSA≤140 and rotatable bonds≤10), admetSAR (summary of the Pfizer 3/75 rule), Miners/Tai (weakly acidic CYP2C9 substrates and anionic mechanism). 

## QED drug-likeness
- Common threshold(s) or range(s): QED ranges from **0–1** (closer to 1 means more "drug-like"); the literature more often uses it for **ranking/relative comparison** rather than as a uniform hard threshold. 
- Usually associated with: both **B** and **A** are possible; QED is more of an **overall drug-likeness/developability composite metric** than a CYP2C9-substrate-specific property
- Brief note: QED combines multiple basic properties (MW, logP, TPSA, HBD/HBA, aromatic rings, rotatable bonds, structural alerts, etc.), so in this task it often serves as a proxy for **chemical-space quality**; however, it cannot replace the CYP2C9 mechanistic anchor of **weak acid/anionic group–Arg108**. 
- Source: Bickerton et al. proposed QED and its 0–1 range; RDKit QED documentation describing its components; Miners/Tai on the task-relevant background of the CYP2C9 anionic mechanism. 

## Functional-group notes
- Group name: Carboxylic acid / carboxylate
- Usually associated with: **B (substrate)** is more common, especially in classic CYP2C9 substrate families such as NSAIDs; the anionic form enhances recognition by forming charge pairing/salt-bridge interactions with Arg108 in the active site
- Brief note: Multiple mechanistic studies indicate that CYP2C9 substrates are often weak acids; Arg108 plays a selective role in the binding and metabolism of anionic substrates, making this one of the most transferable **functional-group-level** rules. 
- Source: Miners & Birkett (weakly acidic substrates are common; pKa range), Dickmann et al. (negatively charged substrates and Arg108 selectivity), Tai et al. (anionic group–Arg108 charge pairing/crystallographic basis). 

- Group name: Aromatic ring systems enabling π–π / hydrophobic contacts
- Usually associated with: **B (substrate)** is common, consistent with fitting into a hydrophobic active pocket and enabling π–π stacking/hydrophobic positioning with key aromatic residues
- Brief note: The literature reports that in CYP2C9 systems, aromatic interactions (for example, with residues such as Phe114) can contribute to substrate recognition and positioning; however, "the more aromatic rings the better" is not true, and from a developability perspective, **>3 aromatic rings** is often treated as a risk anchor. 
- Source: Nair et al. (examples of aromatic-ring π–π + Arg108 interactions), Melet et al. reports on aromatic-substrate recognition (abstract-level evidence), Ritchie et al. (>3 aromatic rings and developability risk). 

- Group name: Basic tertiary amines subject to N-demethylation
- Usually associated with: **B (substrate)**, as an exception/supplement to the broader pattern that weakly acidic substrates are the majority
- Brief note: Reviews note that, in addition to many weakly acidic substrates, CYP2C9 can also catalyze N-demethylation and related reactions for some basic drugs; therefore, the presence of a basic amine/high pKa does not automatically exclude substrate status, but there is no transferable single functional-group threshold. 
- Source: Daly review (weak acids dominate but reaction types for basic drugs are also included), Zhou review (substrate diversity and neutral highly hydrophobic exceptions).

Input 2. Neighbor similarities and per-neighbor comparison notes
"""
Neighbors that is a substrate to the enzyme CYP2C9:
Neighbor 1: 
Similarity: 0.357
Comparison note: First, The neighbor does not have pyrazine, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 0.7678, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Next, Both the neighbor and the query have sulfonamide (query-minus-neighbor delta +0). This pairwise contribution is 0.3318, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Then, Both the neighbor and the query have urea (query-minus-neighbor delta +0). This pairwise contribution is 0.2502, which pushes toward option (B): is a substrate to the enzyme CYP2C9. After that, Neither the neighbor nor the query has dialkyl ether (query-minus-neighbor delta +0). This pairwise contribution is 0.2498, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Finally, For neutral fraction, the neighbor's neutral fraction is value 0.0064, while the query's neutral fraction is value 0.0045. The query-minus-neighbor delta is -0.0019. This pairwise contribution is 0.2034, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Step 6, For Labute surface area, the neighbor's Labute surface area is value 107.6431, while the query's Labute surface area is value 181.6697. The query-minus-neighbor delta is +74.0267. This pairwise contribution is -0.1184, which pushes toward option (A): is not a substrate to the enzyme CYP2C9. Taken together, this positive-neighbor comparison pushes toward option (B): is a substrate to the enzyme CYP2C9 with pair score 0.5833.
Neighbor 2: 
Similarity: 0.344
Comparison note: First, The neighbor does not have pyrazine, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 0.7678, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Next, The neighbor has azocane, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is 0.4782, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Then, The neighbor has semicarbazide, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is 0.4777, which pushes toward option (B): is a substrate to the enzyme CYP2C9. After that, Both the neighbor and the query have sulfonamide (query-minus-neighbor delta +0). This pairwise contribution is 0.3318, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Finally, Neither the neighbor nor the query has dialkyl ether (query-minus-neighbor delta +0). This pairwise contribution is 0.2498, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Step 6, For neutral fraction, the neighbor's neutral fraction is value 0.0298, while the query's neutral fraction is value 0.0045. The query-minus-neighbor delta is -0.0253. This pairwise contribution is 0.2217, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Taken together, this positive-neighbor comparison pushes toward option (B): is a substrate to the enzyme CYP2C9 with pair score 0.837.
Neighbor 3: 
Similarity: 0.248
Comparison note: First, The neighbor does not have pyrazine, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 0.7678, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Next, The neighbor has secondary aromatic amine, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is 0.363, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Then, Both the neighbor and the query have sulfonamide (query-minus-neighbor delta +0). This pairwise contribution is 0.3318, which pushes toward option (B): is a substrate to the enzyme CYP2C9. After that, Both the neighbor and the query have urea (query-minus-neighbor delta +0). This pairwise contribution is 0.2502, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Finally, Neither the neighbor nor the query has dialkyl ether (query-minus-neighbor delta +0). This pairwise contribution is 0.2498, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Step 6, For strongest acidic pKa, the neighbor's strongest acidic pKa is value 4.0308, while the query's strongest acidic pKa is value 5.0534. The query-minus-neighbor delta is +1.0226. This pairwise contribution is 0.1184, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Taken together, this positive-neighbor comparison pushes toward option (B): is a substrate to the enzyme CYP2C9 with pair score 0.7843.

Neighbors that is not a substrate to the enzyme CYP2C9
Neighbor 4: 
Similarity: 0.259
Comparison note: First, The neighbor does not have pyrazine, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 1.2771, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Next, For number of basic sites, the neighbor's number of basic sites is absent (0), while the query's number of basic sites is value 3. The query-minus-neighbor delta is +3. This pairwise contribution is 0.729, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Then, For strongest acidic pKa, the neighbor's strongest acidic pKa is value 3.6796, while the query's strongest acidic pKa is value 5.0534. The query-minus-neighbor delta is +1.3738. This pairwise contribution is 0.5408, which pushes toward option (B): is a substrate to the enzyme CYP2C9. After that, Neither the neighbor nor the query has dialkyl ether (query-minus-neighbor delta +0). This pairwise contribution is 0.2872, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Finally, The neighbor does not have urea, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 0.281, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Step 6, For topological polar surface area, the neighbor's topological polar surface area is value 75.63, while the query's topological polar surface area is value 130.15. The query-minus-neighbor delta is +54.52. This pairwise contribution is -0.2577, which pushes toward option (A): is not a substrate to the enzyme CYP2C9. Taken together, this negative-neighbor comparison pushes toward option (B): is a substrate to the enzyme CYP2C9 with pair score 0.8107.
Neighbor 5: 
Similarity: 0.235
Comparison note: First, The neighbor does not have pyrazine, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 1.2771, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Next, For maximum partial charge, the neighbor's maximum partial charge is value 0.2546, while the query's maximum partial charge is value 0.3284. The query-minus-neighbor delta is +0.0738. This pairwise contribution is 0.3758, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Then, For strongest basic pKa, the neighbor's strongest basic pKa is value 9.1977, while the query's strongest basic pKa is value 4.3262. The query-minus-neighbor delta is -4.8715. This pairwise contribution is 0.3691, which pushes toward option (B): is a substrate to the enzyme CYP2C9. After that, For estimated logD, the neighbor's estimated logD is value -1.2488, while the query's estimated logD is value -0.2708. The query-minus-neighbor delta is +0.978. This pairwise contribution is 0.2876, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Finally, Neither the neighbor nor the query has dialkyl ether (query-minus-neighbor delta +0). This pairwise contribution is 0.2872, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Step 6, The neighbor has pyrrolidine, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is 0.2869, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Taken together, this negative-neighbor comparison pushes toward option (B): is a substrate to the enzyme CYP2C9 with pair score 0.9079.
Neighbor 6: 
Similarity: 0.232
Comparison note: First, The neighbor does not have pyrazine, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 1.2771, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Next, For fraction of sp3 carbons, the neighbor's fraction of sp3 carbons is value 0.1818, while the query's fraction of sp3 carbons is value 0.4286. The query-minus-neighbor delta is +0.2468. This pairwise contribution is 0.4538, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Then, The neighbor has isoxazole, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is 0.3819, which pushes toward option (B): is a substrate to the enzyme CYP2C9. After that, For maximum partial charge, the neighbor's maximum partial charge is value 0.2638, while the query's maximum partial charge is value 0.3284. The query-minus-neighbor delta is +0.0647. This pairwise contribution is 0.3755, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Finally, Neither the neighbor nor the query has dialkyl ether (query-minus-neighbor delta +0). This pairwise contribution is 0.2872, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Step 6, The neighbor does not have urea, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 0.281, which pushes toward option (B): is a substrate to the enzyme CYP2C9. Taken together, this negative-neighbor comparison pushes toward option (B): is a substrate to the enzyme CYP2C9 with pair score 0.8547.
"""

Input 3. Final prediction label
option (B): is a substrate to the enzyme CYP2C9

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
