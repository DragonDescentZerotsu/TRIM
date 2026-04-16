You are rewriting rough neighbor-based molecule-comparison notes from Explainable Boosting Machine (EBM) into high-quality reasoning SFT data for molecule local analog-comparison task AMES where option (A) means is not mutagenic and option (B) means is mutagenic.

Input 1. Task playbook
# AMES mutagenicity molecular-property playbook

## neutral fraction: estimated fraction of the molecule that is neutral at the configured pH
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; *proxy*—lower neutral fraction (more ionized) can reduce passive membrane permeation and may contribute to “A” outcomes via lower bacterial bioavailability/exposure rather than true absence of DNA reactivity
- Brief note: For bacterial assays, limitations can arise from “differences in bioavailability,” so ionization-dependent exposure effects are plausible but not governed by a standard cutoff for neutral fraction citeturn44view0.
- Source: citeturn44view0turn39view0turn41view0

## estimated logD: estimated logD at the configured pH
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; *proxy*—extreme lipophilicity can impair effective exposure (e.g., precipitation/low soluble dose), potentially biasing toward “A” in Ames readouts
- Brief note: In OECD TG 471, dose selection is constrained by cytotoxicity and solubility; the recommended maximum test concentration for **soluble, non-cytotoxic** substances is 5 mg/plate or 5 μL/plate, making solubility/exposure a practical limiter for very hydrophobic substances citeturn9view0.
- Source: citeturn9view0turn44view0

## strongest acidic pKa: pKa of the strongest acidic site
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; *proxy*—very low (strong) acids increase anionic fraction at neutral pH, often reducing passive permeation, which can reduce effective bacterial exposure
- Brief note: The Ames test can miss some mutagens due to “differences in bioavailability,” but no standardized pKa cutoff is used to interpret mutagenicity risk in OECD TG 471 (the endpoint is driven by DNA-reactive chemistry and metabolism) citeturn44view0.
- Source: citeturn44view0turn39view0

## strongest basic pKa: pKa of the strongest basic site
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; *proxy*—presence of an ionizable nitrogen (often a primary amine; typically protonated near physiological pH) is associated with improved Gram-negative accumulation, which could increase effective exposure and thus reveal “B” outcomes if a DNA-reactive motif is present
- Brief note: Gram-negative accumulation guidelines (“eNTRy rules”) emphasize a **non-sterically encumbered ionizable nitrogen (particularly a primary amine)** plus rigidity/low 3D character; these are permeability/accumulation heuristics rather than mutagenicity mechanisms citeturn39view0turn21view0.
- Source: citeturn39view0turn21view0

## number of acidic sites: number of acidic ionizable sites in the molecule
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; *proxy*—more acidic sites often increase polarity/ionization and can reduce passive diffusion, potentially biasing toward “A” from lower exposure
- Brief note: OECD TG 471 explicitly notes that the test can miss mutagens for reasons including “differences in bioavailability,” but does not provide numeric rules mapping ionizable-site counts to outcomes citeturn44view0.
- Source: citeturn44view0turn9view0

## number of basic sites: number of basic ionizable sites in the molecule
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; *proxy*—having at least one non-sterically encumbered ionizable nitrogen (esp. primary amine) is associated with improved Gram-negative accumulation (can increase effective exposure)
- Brief note: eNTRy-style guidance is framed around **presence/absence** of an ionizable nitrogen rather than a “number of basic sites” cutoff; it is meant for Gram-negative accumulation, not direct DNA reactivity citeturn39view0turn21view0.
- Source: citeturn39view0turn21view0

## number of ionizable sites: total number of acidic and basic ionizable sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; *proxy*—more ionizable sites tends to increase polarity/charge states across pH, which can reduce passive permeability and effective exposure
- Brief note: Because some Ames false negatives/shortcomings are attributable to bioavailability differences, permeability-linked descriptors can matter operationally, but no stable “ionizable sites” cutoff is used for Ames interpretation citeturn44view0turn41view0.
- Source: citeturn44view0turn44view0turn41view0

## exact molecular weight: exact isotopic molecular weight
- Common threshold(s) or range(s): **Rule-of-Five** flags impaired absorption/permeation when MW > 500 (*proxy*); **Ghose** “drug-like” MW range 160–480 (*proxy*) citeturn56view0turn16view0
- Usually associated with: no consistent direction for Ames mechanistically; *proxy*—very high MW can reduce bacterial uptake/solubility and bias toward “A” outcomes via reduced exposure
- Brief note: Tester strains are engineered to improve sensitivity (including enhanced uptake for larger/hydrophobic molecules via strain features such as rfa “deep rough” mutations), so MW effects are not reliably monotonic in Ames outcomes citeturn41view0.
- Source: citeturn56view0turn16view0turn41view0turn44view0

## fraction of sp3 carbons: fraction of carbon atoms that are sp3 hybridized
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: weak *proxy* tendencies only—lower fraction sp3 (more “flat,” aromatic) can co-occur with known Ames toxicophores (e.g., polycyclic aromatic systems), which are associated with “B”
- Brief note: A concrete mutagenicity-linked anchor exists for **polycyclic aromatic systems** (see aromatic ring notes), but fraction sp3 itself is not used with a standard mutagenicity cutoff citeturn32view0turn33view2.
- Source: citeturn32view0turn33view2turn31view0

## heavy-atom count: number of non-hydrogen atoms
- Common threshold(s) or range(s): no stable Ames-specific threshold found; *proxy* “lead-like” definitions in medicinal chemistry/virtual screening commonly constrain heavy atom count to roughly the **~20–25** range (context: lead-like space, not mutagenicity) citeturn57search8turn57search12
- Usually associated with: no consistent direction for mutagenicity; *proxy*—very high heavy-atom count (large molecules) can reduce diffusion/uptake and bias toward “A” via exposure limits
- Brief note: OECD TG 471 notes bioavailability differences as a reason some mutagens are not detected; size descriptors may therefore have operational relevance without being causal for DNA reactivity citeturn44view0.
- Source: citeturn57search8turn57search12turn44view0turn41view0

## heavy-atom molecular weight: molecular weight contributed by heavy atoms
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; *proxy*—tracks size similarly to molecular weight / heavy-atom count (may affect exposure)
- Brief note: Practical exposure limitations in Ames (solubility/cytotoxicity; limit concentrations) are documented, but “heavy-atom molecular weight” is not a standard interpretive axis in mutagenicity practice citeturn9view0turn44view0.
- Source: citeturn9view0turn44view0turn41view0

## Labute surface area: Labute approximate surface area
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; mostly a size/shape correlate
- Brief note: Permeability/accumulation studies in Gram-negatives discuss shape/size constraints (e.g., porin passage, efflux) but do not establish a standard Labute surface area cutoff for bacterial mutagenicity prediction citeturn39view0turn46view0.
- Source: citeturn39view0turn46view0

## maximum absolute partial charge: largest absolute atomic partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; *proxy*—more extreme partial charges can correlate with strong electrostatics/polarity, affecting uptake/efflux rather than intrinsic DNA reactivity
- Brief note: In Gram-negative accumulation/efflux work, electrostatics and **partial positive charges** have been identified as useful parameters for assessing efflux efficiency (species/context dependent), but without a universal numeric cutoff citeturn46view0.
- Source: citeturn46view0turn39view0

## maximum partial charge: most positive atomic partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; *proxy*—higher positive charge character may influence porin interactions and/or efflux
- Brief note: For E. coli, “partial positive charges” are discussed as useful parameters for assessing efflux efficiency, but the literature does not standardize a threshold on an RDKit-style max-partial-charge feature citeturn46view0.
- Source: citeturn46view0turn39view0

## minimum absolute partial charge: smallest absolute atomic partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; interpret as a model feature without a standard experimental cutoff
- Brief note: Charge distributions can matter for permeability/efflux, but there is no common mutagenicity rule anchored on “minimum absolute partial charge” citeturn46view0turn44view0.
- Source: citeturn46view0turn44view0

## minimum partial charge: most negative atomic partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; *proxy*—more negative charge character can reduce passive diffusion (anion-rich molecules), affecting exposure rather than DNA reactivity
- Brief note: OECD TG 471 notes that bioavailability differences can explain some shortcomings; electrostatics-related descriptors may influence exposure, but no numeric cutoff is standardized citeturn44view0.
- Source: citeturn44view0turn46view0

## estimated logP: RDKit-estimated octanol/water partition coefficient (logP)
- Common threshold(s) or range(s): **Rule-of-Five** flags impaired absorption/permeation when logP > 5 (*proxy*); **Ghose** range −0.4 to 5.6 (*proxy*) citeturn56view0turn16view0
- Usually associated with: no consistent direction for intrinsic mutagenicity; *proxy*—very high logP can reduce usable soluble dose / increase precipitation risk, potentially biasing toward “A” via exposure limitations
- Brief note: In OECD TG 471, solubility and cytotoxicity constrain the highest test concentration (5 mg/plate or 5 μL/plate for soluble non-cytotoxic substances), so extreme hydrophobicity can matter operationally citeturn9view0.
- Source: citeturn56view0turn16view0turn9view0turn44view0

## molecular weight: molecular weight
- Common threshold(s) or range(s): **Rule-of-Five**: MW > 500 suggests impaired absorption/permeation (*proxy*); **Ghose**: 160–480 (*proxy*) citeturn56view0turn16view0
- Usually associated with: no consistent direction; *proxy*—very large MW may reduce uptake/solubility and bias toward “A” outcomes through lower exposure
- Brief note: Ames tester strains can include features that enhance uptake of large/hydrophobic molecules (e.g., rfa mutations), which weakens any simple MW→outcome rule citeturn41view0.
- Source: citeturn56view0turn16view0turn41view0turn44view0

## NH/OH group count: number of NH or OH groups
- Common threshold(s) or range(s): no stable threshold directly on “NH/OH count”; *proxy*—Rule-of-Five flags poor absorption/permeation when **H-bond donor groups > 5** citeturn56view0
- Usually associated with: no consistent direction; *proxy*—higher HBD capacity can reduce passive permeability and bias toward “A” via lower exposure
- Brief note: NH/OH count is an imperfect stand-in for H-bond donors (not every NH is a donor, e.g., amides), so interpret cautiously and prefer explicit HBD count when available citeturn56view0.
- Source: citeturn56view0turn44view0

## nitrogen/oxygen atom count: number of nitrogen and oxygen atoms
- Common threshold(s) or range(s): no stable threshold on “N/O atom count”; *proxy*—Rule-of-Five uses **H-bond acceptors > 10** (acceptors often—but not always—N/O atoms) citeturn56view0
- Usually associated with: no consistent direction; *proxy*—higher heteroatom burden often increases polarity/ionization, potentially reducing permeability and biasing toward “A” via lower exposure
- Brief note: N/O atom count overestimates acceptor capacity when atoms are protonated/amide-like; treat as a coarse polarity proxy, not a mutagenicity rule citeturn56view0.
- Source: citeturn56view0turn44view0

## aliphatic carbocycle count: number of aliphatic carbocyclic rings
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction (by itself)
- Brief note: Ring-type counts are occasionally used in *drug-likeness* filters and permeability discussions, but Ames mutagenicity is dominated by reactive/toxicophoric substructures rather than “aliphatic carbocycles” per se citeturn44view0turn32view0.
- Source: citeturn44view0turn32view0

## aliphatic heterocycle count: number of aliphatic heterocyclic rings
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; depends on embedded reactive motifs (e.g., strained heterocycles are different—see functional group notes)
- Brief note: Strained three-member heterocycles (e.g., epoxides/aziridines) are clear mutagenicity toxicophores, but “aliphatic heterocycle count” broadly is not used with a cutoff citeturn32view0turn33view1.
- Source: citeturn32view0turn33view1

## aliphatic ring count: number of aliphatic rings
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction
- Brief note: Global ring counts appear in some drug-likeness heuristics, but Ames-specific interpretive rules are structural-alert driven rather than ring-count driven citeturn44view0turn32view0.
- Source: citeturn44view0turn32view0

## aromatic carbocycle count: number of aromatic carbocyclic rings
- Common threshold(s) or range(s): no stable threshold on this count alone; one task-relevant anchor is **polycyclic aromatic systems of ≥3 fused aromatic rings** (*toxicophore*) citeturn33view2
- Usually associated with: higher fused aromaticity is associated with “B” (mutagenic), particularly via DNA intercalation and/or metabolic activation (e.g., PAH diol-epoxides)
- Brief note: The ≥3 fused-ring anchor refers to *fused* polycyclic aromatic systems (not simply 3 separate phenyls) citeturn32view0turn33view2.
- Source: citeturn32view0turn33view2

## aromatic heterocycle count: number of aromatic heterocyclic rings
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; depends on attached/embedded toxicophores (e.g., aromatic nitro/amine on heteroaromatics)
- Brief note: Aromatic nitro and aromatic amine toxicophores are well-recognized for Ames mutagenicity and can occur on heteroaromatic rings; ring-type count alone is not a sufficient rule citeturn32view0turn33view0.
- Source: citeturn32view0turn33view0turn44view0

## aromatic ring count: number of aromatic rings
- Common threshold(s) or range(s): no stable cutoff on “aromatic ring count” in general; however, **polycyclic aromatic systems (≥3 fused aromatic rings)** are a documented mutagenicity toxicophore citeturn33view2
- Usually associated with: “B” more likely when high aromaticity reflects polycyclic planar systems (intercalation) and/or aromatic bioactivation motifs
- Brief note: This is a *structural-alert* anchor (fused rings & planarity) rather than a universal numeric threshold on aromatic rings citeturn33view2turn32view0.
- Source: citeturn33view2turn32view0turn44view0

## hydrogen-bond acceptor count: number of hydrogen-bond acceptors
- Common threshold(s) or range(s): **Rule-of-Five** flags impaired absorption/permeation when H-bond acceptors > 10 (*proxy*) citeturn56view0
- Usually associated with: no consistent direction for intrinsic mutagenicity; *proxy*—very high HBA can reduce passive permeability and bias toward “A” via exposure limits
- Brief note: HBA is part of permeability-oriented heuristics (drug-likeness/absorption), while Ames outcomes are primarily governed by reactive chemistry plus metabolic activation/bioavailability citeturn56view0turn44view0.
- Source: citeturn56view0turn44view0

## hydrogen-bond donor count: number of hydrogen-bond donors
- Common threshold(s) or range(s): **Rule-of-Five** flags impaired absorption/permeation when H-bond donors > 5 (*proxy*) citeturn56view0
- Usually associated with: no consistent direction; *proxy*—many donors increase polarity and can reduce passive diffusion, potentially biasing toward “A” via reduced exposure
- Brief note: HBD is an exposure/permeability feature rather than a chemical-reactivity feature; interpret as a confounder/modifier (exposure) rather than a mechanistic mutagenicity driver citeturn44view0.
- Source: citeturn56view0turn44view0

## heteroatom count: number of heteroatoms, such as N, O, or S
- Common threshold(s) or range(s): no stable threshold found
- Usually associated with: no consistent direction; higher heteroatom count often increases polarity/ionization (*proxy* exposure modifier)
- Brief note: While heteroatom count is widely used in descriptors, mutagenicity prediction practice emphasizes structural alerts/toxicophores (e.g., nitro, aziridine, epoxide) rather than heteroatom count alone citeturn32view0.
- Source: citeturn32view0turn44view0

## rotatable-bond count: number of rotatable bonds
- Common threshold(s) or range(s): **Veber**: ≤10 rotatable bonds (*proxy for oral bioavailability/permeability*) citeturn12view0; **eNTRy (Gram-negative accumulation)**: ≤5 rotatable bonds (*proxy for bacterial accumulation*) citeturn39view0turn21view0
- Usually associated with: no consistent direction for intrinsic mutagenicity; *proxy*—lower RB (more rigid) can increase Gram-negative accumulation and may increase effective exposure, helping reveal “B” if DNA-reactive motifs exist
- Brief note: The eNTRy rule is explicitly about Gram-negative accumulation (uptake/efflux balance), not about genotoxic mechanism citeturn39view0.
- Source: citeturn12view0turn39view0turn21view0turn44view0

## saturated carbocycle count: number of saturated carbocyclic rings
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; may inversely correlate with aromaticity (and thus with aromatic toxicophores) in some datasets
- Brief note: Saturated rings can increase 3D character, but Ames mutagenicity remains dominated by specific toxicophores rather than saturation counts citeturn32view0turn33view2.
- Source: citeturn32view0turn33view2

## saturated heterocycle count: number of saturated heterocyclic rings
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction; depends on whether strained electrophilic heterocycles exist (see functional group notes)
- Brief note: “Three-membered heterocycles” (e.g., epoxides/aziridines) are mutagenicity toxicophores, but saturated heterocycles overall do not have a standalone cutoff citeturn33view0turn33view1.
- Source: citeturn33view0turn33view1

## saturated ring count: number of saturated rings
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no consistent direction
- Brief note: Saturation can modulate solubility/permeability and “flatness,” but no stable Ames-specific ring-saturation cutoff exists citeturn44view0turn31view0.
- Source: citeturn44view0turn31view0

## ring count: total number of rings
- Common threshold(s) or range(s): no stable Ames-specific threshold found; a commonly cited *drug-like* heuristic reports many drug-like molecules obey **1 ≤ number of rings ≤ 4** (*proxy*) citeturn16view0
- Usually associated with: no consistent direction; *proxy*—very high ring counts may reduce solubility/raise planarity, and mutagenicity risk is driven by specific toxicophores (polycyclic fused aromatics are a notable “B” anchor)
- Brief note: Distinguish “many rings” from the specific high-risk pattern **≥3 fused aromatic rings** (polycyclic planar systems) citeturn33view2.
- Source: citeturn16view0turn33view2turn44view0

## topological polar surface area: topological polar surface area of the molecule
- Common threshold(s) or range(s): **Veber**: PSA ≤ 140 Å² (*proxy*) citeturn12view0; **Egan absorption model**: PSA upper limit 131.6 Å² (95% ellipse) and 148.1 Å² (99% ellipse) (*proxy*) citeturn12view0
- Usually associated with: no consistent direction for intrinsic mutagenicity; *proxy*—higher TPSA tends to reduce passive permeability and can bias toward “A” via lower exposure
- Brief note: OECD TG 471 explicitly notes bioavailability differences as a reason some mutagens are not detected; TPSA is one practical bioavailability/permeability correlate, but not an Ames mechanism itself citeturn44view0turn12view0.
- Source: citeturn12view0turn44view0

## QED drug-likeness: quantitative estimate of drug-likeness
- Common threshold(s) or range(s): QED ranges 0–1 (definition); in the original QED study, “attractive” compounds had mean QED ≈ 0.67, and a “top 10% of ChEMBL” reference point corresponds to QED ≈ 0.796 (contextual anchors, not mutagenicity cutoffs) citeturn25view0turn25view1
- Usually associated with: no consistent direction for Ames; *proxy*—lower QED can co-occur with undesirable substructures/alerts (some of which overlap with mutagenicity toxicophores), potentially enriching for “B,” but this is not a validated Ames threshold
- Brief note: QED is a composite score built for drug-likeness (multi-property desirability), not for genotoxicity; treat as a coarse enrichment signal at best citeturn25view0turn23view0.
- Source: citeturn25view0turn25view1turn23view0turn32view0

## Functional-group notes
- Group name: aromatic nitro
- Usually associated with: mutagenic (B)
- Brief note: Identified as a well-recognized mutagenicity toxicophore; commonly appears in Ames-positive compounds citeturn32view0turn33view0.
- Source: citeturn33view0turn32view0

- Group name: aromatic amine
- Usually associated with: mutagenic (B)
- Brief note: Well-recognized mutagenicity toxicophore; activity often depends on metabolic activation pathways (context-dependent) citeturn32view0turn33view0.
- Source: citeturn33view0turn44view0

- Group name: nitroso (including aromatic nitroso)
- Usually associated with: mutagenic (B)
- Brief note: Reported as a (general/specific) toxicophore class for mutagenicity; mechanisms involve reactive intermediates citeturn32view0turn33view1.
- Source: citeturn33view1turn32view0

- Group name: nitrosamine (N-nitroso)
- Usually associated with: mutagenic (B)
- Brief note: Requires metabolic activation; OECD TG 471 flags some classes (including certain nitrosamines) as “special cases” that may be detected more efficiently with preincubation methods citeturn44view0turn41view0turn33view1.
- Source: citeturn44view0turn41view0turn33view1

- Group name: azo-type / diazo / triazene / azide
- Usually associated with: mutagenic (B)
- Brief note: Identified among toxicophore groups; some act via cleavage to arylamines or via intrinsically reactive intermediates citeturn33view1turn32view0.
- Source: citeturn33view1turn32view0turn44view0

- Group name: epoxide
- Usually associated with: mutagenic (B)
- Brief note: Electrophilic alkylating substructure; identified as a specific toxicophore with substantial intrinsic reactivity citeturn33view1turn32view0.
- Source: citeturn33view1turn32view0

- Group name: aziridine
- Usually associated with: mutagenic (B)
- Brief note: Electrophilic alkylating three-member heterocycle; identified as a specific toxicophore with high apparent predictivity in the cited toxicophore work citeturn33view1turn32view0.
- Source: citeturn33view1turn32view0

- Group name: aliphatic halide (C, Br, I; excluding fluorine in the cited toxicophore definition)
- Usually associated with: mutagenic (B)
- Brief note: Identified as a general toxicophore class (alkylating potential depends on context/leaving group and structure) citeturn32view0turn33view0.
- Source: citeturn33view0turn32view0

- Group name: polycyclic aromatic planar systems / polycyclic aromatic systems (≥3 fused aromatic rings)
- Usually associated with: mutagenic (B)
- Brief note: Toxicophore anchored on **three or more fused aromatic rings**; mechanisms include DNA intercalation and metabolic activation to DNA-reactive diol-epoxides (PAH context) citeturn33view2turn32view0.
- Source: citeturn33view2turn32view0

- Group name: unsubstituted heteroatom-bonded heteroatom (e.g., certain N–O / N–N motifs)
- Usually associated with: mutagenic (B)
- Brief note: Identified as a general toxicophore class; may proceed via radical/reactive intermediates depending on subtype citeturn32view0turn33view1.
- Source: citeturn33view1turn32view0

Input 2. Neighbor similarities and per-neighbor comparison notes
"""
Neighbors that is mutagenic:
Neighbor 1: 
Similarity: 0.553
Comparison note: First, Both the neighbor and the query have nitroso (query-minus-neighbor delta +0). This pairwise contribution is 2.1536, which pushes toward option (B): is mutagenic. Next, For QED drug-likeness, the neighbor's QED drug-likeness is value 0.3352, while the query's QED drug-likeness is value 0.2061. The query-minus-neighbor delta is -0.1291. This pairwise contribution is 1.0756, which pushes toward option (B): is mutagenic. Then, For ring count, the neighbor's ring count is value 4, while the query's ring count is value 5. The query-minus-neighbor delta is +1. This pairwise contribution is 0.884, which pushes toward option (B): is mutagenic. After that, For aromatic carbocycle count, the neighbor's aromatic carbocycle count is value 4, while the query's aromatic carbocycle count is value 5. The query-minus-neighbor delta is +1. This pairwise contribution is 0.74, which pushes toward option (B): is mutagenic. Finally, For estimated logD, the neighbor's estimated logD is value 4.9819, while the query's estimated logD is value 6.1351. The query-minus-neighbor delta is +1.1532. This pairwise contribution is -0.6619, which pushes toward option (A): is not mutagenic. Step 6, For fraction of sp3 carbons, the neighbor's fraction of sp3 carbons is value 0, while the query's fraction of sp3 carbons is value 0. The query-minus-neighbor delta is +0. This pairwise contribution is 0.4001, which pushes toward option (B): is mutagenic. Taken together, this positive-neighbor comparison pushes toward option (B): is mutagenic with pair score 0.9801.
Neighbor 2: 
Similarity: 0.519
Comparison note: First, Both the neighbor and the query have nitroso (query-minus-neighbor delta +0). This pairwise contribution is 2.1536, which pushes toward option (B): is mutagenic. Next, For ring count, the neighbor's ring count is value 4, while the query's ring count is value 5. The query-minus-neighbor delta is +1. This pairwise contribution is 0.884, which pushes toward option (B): is mutagenic. Then, For QED drug-likeness, the neighbor's QED drug-likeness is value 0.3247, while the query's QED drug-likeness is value 0.2061. The query-minus-neighbor delta is -0.1186. This pairwise contribution is 0.8151, which pushes toward option (B): is mutagenic. After that, For aromatic carbocycle count, the neighbor's aromatic carbocycle count is value 4, while the query's aromatic carbocycle count is value 5. The query-minus-neighbor delta is +1. This pairwise contribution is 0.74, which pushes toward option (B): is mutagenic. Finally, For estimated logP, the neighbor's estimated logP is value 5.5441, while the query's estimated logP is value 6.1351. The query-minus-neighbor delta is +0.591. This pairwise contribution is 0.6888, which pushes toward option (B): is mutagenic. Step 6, For Labute surface area, the neighbor's Labute surface area is value 115.1711, while the query's Labute surface area is value 125.8318. The query-minus-neighbor delta is +10.6607. This pairwise contribution is -0.4406, which pushes toward option (A): is not mutagenic. Taken together, this positive-neighbor comparison pushes toward option (B): is mutagenic with pair score 0.976.
Neighbor 3: 
Similarity: 0.507
Comparison note: First, For hydrogen-bond acceptor count, the neighbor's hydrogen-bond acceptor count is value 0, while the query's hydrogen-bond acceptor count is value 2. The query-minus-neighbor delta is +2. This pairwise contribution is 1.1381, which pushes toward option (B): is mutagenic. Next, The neighbor does not have nitroso, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 1.065, which pushes toward option (B): is mutagenic. Then, For ring count, the neighbor's ring count is value 5, while the query's ring count is value 5. The query-minus-neighbor delta is +0. This pairwise contribution is 0.9026, which pushes toward option (B): is mutagenic. After that, For maximum partial charge, the neighbor's maximum partial charge is value -0.0027, while the query's maximum partial charge is value 0.1232. The query-minus-neighbor delta is +0.1259. This pairwise contribution is 0.6613, which pushes toward option (B): is mutagenic. Finally, For QED drug-likeness, the neighbor's QED drug-likeness is value 0.2915, while the query's QED drug-likeness is value 0.2061. The query-minus-neighbor delta is -0.0854. This pairwise contribution is 0.487, which pushes toward option (B): is mutagenic. Step 6, For fraction of sp3 carbons, the neighbor's fraction of sp3 carbons is value 0, while the query's fraction of sp3 carbons is value 0. The query-minus-neighbor delta is +0. This pairwise contribution is 0.4001, which pushes toward option (B): is mutagenic. Taken together, this positive-neighbor comparison pushes toward option (B): is mutagenic with pair score 0.9742.

Neighbors that is not mutagenic
Neighbor 4: 
Similarity: 0.373
Comparison note: First, The neighbor does not have nitroso, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 1.8429, which pushes toward option (B): is mutagenic. Next, The neighbor has 3 copies of benzene, while the query has 5 (query-minus-neighbor delta +2). This pairwise contribution is 1.4552, which pushes toward option (B): is mutagenic. Then, For aromatic carbocycle count, the neighbor's aromatic carbocycle count is value 3, while the query's aromatic carbocycle count is value 5. The query-minus-neighbor delta is +2. This pairwise contribution is 1.0283, which pushes toward option (B): is mutagenic. After that, For aromatic ring count, the neighbor's aromatic ring count is value 3, while the query's aromatic ring count is value 5. The query-minus-neighbor delta is +2. This pairwise contribution is -1.0282, which pushes toward option (A): is not mutagenic. Finally, For QED drug-likeness, the neighbor's QED drug-likeness is value 0.4284, while the query's QED drug-likeness is value 0.2061. The query-minus-neighbor delta is -0.2222. This pairwise contribution is 0.8744, which pushes toward option (B): is mutagenic. Step 6, For estimated logP, the neighbor's estimated logP is value 3.5752, while the query's estimated logP is value 6.1351. The query-minus-neighbor delta is +2.5599. This pairwise contribution is -0.6643, which pushes toward option (A): is not mutagenic. Taken together, this negative-neighbor comparison pushes toward option (B): is mutagenic with pair score 0.9821.
Neighbor 5: 
Similarity: 0.370
Comparison note: First, The neighbor does not have nitroso, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 1.8429, which pushes toward option (B): is mutagenic. Next, The neighbor has 5 copies of benzene, while the query has 5 (query-minus-neighbor delta +0). This pairwise contribution is 0.9611, which pushes toward option (B): is mutagenic. Then, For ring count, the neighbor's ring count is value 5, while the query's ring count is value 5. The query-minus-neighbor delta is +0. This pairwise contribution is 0.8395, which pushes toward option (B): is mutagenic. After that, For aromatic carbocycle count, the neighbor's aromatic carbocycle count is value 5, while the query's aromatic carbocycle count is value 5. The query-minus-neighbor delta is +0. This pairwise contribution is 0.4765, which pushes toward option (B): is mutagenic. Finally, For estimated logD, the neighbor's estimated logD is value 6.2994, while the query's estimated logD is value 6.1351. The query-minus-neighbor delta is -0.1643. This pairwise contribution is -0.4745, which pushes toward option (A): is not mutagenic. Step 6, For aromatic ring count, the neighbor's aromatic ring count is value 5, while the query's aromatic ring count is value 5. The query-minus-neighbor delta is +0. This pairwise contribution is 0.4101, which pushes toward option (B): is mutagenic. Taken together, this negative-neighbor comparison pushes toward option (B): is mutagenic with pair score 0.9759.
Neighbor 6: 
Similarity: 0.357
Comparison note: First, For estimated logD, the neighbor's estimated logD is value -1.6702, while the query's estimated logD is value 6.1351. The query-minus-neighbor delta is +7.8053. This pairwise contribution is 1.8971, which pushes toward option (B): is mutagenic. Next, The neighbor does not have nitroso, while the query has it once (query-minus-neighbor delta +1). This pairwise contribution is 1.8429, which pushes toward option (B): is mutagenic. Then, The neighbor has 5 copies of benzene, while the query has 5 (query-minus-neighbor delta +0). This pairwise contribution is 0.9611, which pushes toward option (B): is mutagenic. After that, For estimated logP, the neighbor's estimated logP is value 3.0082, while the query's estimated logP is value 6.1351. The query-minus-neighbor delta is +3.1269. This pairwise contribution is -0.7724, which pushes toward option (A): is not mutagenic. Finally, For QED drug-likeness, the neighbor's QED drug-likeness is value 0.2497, while the query's QED drug-likeness is value 0.2061. The query-minus-neighbor delta is -0.0436. This pairwise contribution is 0.5926, which pushes toward option (B): is mutagenic. Step 6, For aromatic carbocycle count, the neighbor's aromatic carbocycle count is value 5, while the query's aromatic carbocycle count is value 5. The query-minus-neighbor delta is +0. This pairwise contribution is 0.4765, which pushes toward option (B): is mutagenic. Taken together, this negative-neighbor comparison pushes toward option (B): is mutagenic with pair score 0.9991.
"""

Input 3. Final prediction label
option (B): is mutagenic

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
