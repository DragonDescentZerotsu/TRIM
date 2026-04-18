# Quick Reference Manual for Molecular Property Thresholds in the hERG Blockade Task (TDC Binary Classification)

## neutral fraction
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more common when a “high neutral fraction” is combined with relatively high lipophilicity and/or protonatable basic centers); A (more common when the molecule is predominantly “anionic/zwitterionic” at physiological pH)
- Brief note: Multiple data-mining studies and reviews on hERG risk consistently emphasize that ionization class modulates the effect of lipophilicity on hERG, with the overall trend typically being: basic > zwitterionic > neutral > acidic (acidic compounds are generally less likely to show strong hERG activity). Therefore, neutral fraction usually needs to be interpreted together with strongest basic pKa and logP/logD, and a stable standalone threshold is rarely given.

## estimated logD
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more common at higher logD, especially for basic/protonatable compounds); A (more common at lower logD)
- Brief note: As a distribution coefficient under a specified pH condition, logD is more physiologically relevant than logP. In one industry data analysis that discussed both hERG (using dofetilide-binding inhibition as a surrogate endpoint) and property distributions, marketed CNS drugs had a ClogD (pH 7.4) 10th–90th percentile range of about −0.5 to 3.8, with a median around 1.7. This was used to describe a feasible “drug-like space,” not as a hard threshold specific to hERG.

## strongest acidic pKa
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (more common when a significantly deprotonated acidic center exists at physiological pH and the overall ionization type is acidic); B (more common in chemical space that is clearly basic/neutral and relatively lipophilic)
- Brief note: Large-scale property analyses for hERG usually treat ionization type (acidic/basic/zwitterionic/neutral) as a higher-level stratification variable: acidic compounds as a class tend to have lower nonspecific hERG risk. Therefore, the value of strongest acidic pKa usually lies in whether it pushes the molecule toward an acidic or zwitterionic ionization type, rather than in a project-transferable single cutoff.

## strongest basic pKa
- Common threshold(s) or range(s): pKa > 8.4 (one commonly used binning threshold in combinations associated with higher hERG risk); pKa ≤ 7.4 (used explicitly as an anchor for “lower basicity” in drug sets); there are also counterexamples suggesting that even pKa < 6 may still contribute to hERG risk
- Usually associated with: B (higher pKa, especially when combined with high logP); A (more common when pKa is reduced, or when the molecule shifts toward an acidic/zwitterionic ionization type)
- Brief note: One method using inhibition at the dofetilide binding site (% inhibition) as a surrogate readout for hERG defined %inh < 15 as low risk, 15–50 as medium risk, and >50 as high risk. Using pKa = 8.4 (the median) and ClogP = 3 for binning, it showed that the “high ClogP + high pKa” group was significantly enriched in high-risk compounds (>50% inhibition). On the other hand, physicochemical profiling based on public hERG databases has also pointed out that even weak bases (pKa < 6) may still make a substantial contribution to hERG inhibition potential. This means that simply lowering pKa to a “moderately low” level does not always guarantee safety; lipophilicity and aromaticity usually need to be optimized together.

## number of acidic sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (more common when there are more acidic sites and the molecule is more likely to form an anionic/zwitterionic type); B (more common when there are fewer acidic sites but the molecule also has basicity and lipophilicity)
- Brief note: Public hERG data profiling suggests that ionization type modulates the effect of logP on hERG, and acidic categories overall are less likely to show strong hERG risk at the same lipophilicity. Therefore, “number of acidic sites” is more suitable as a structural lever that shifts ionization type, rather than as a standalone thresholded variable.

## number of basic sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more common when protonatable basic centers are present and lipophilicity/aromaticity is also relatively high); A (more common when stable protonatable basic centers are absent or the overall ionization state is more acidic/zwitterionic)
- Brief note: Multiple summaries emphasize that positively charged/protonatable atoms can engage in cation–π interactions with aromatic residues in the hERG channel, which is one of the classic risk mechanisms. Therefore, in practice, whether such protonatable basic sites exist—and how many—is often more important than the exact count itself: increasing the number of basic sites generally increases the probability of forming cations at physiological pH, thereby increasing the tendency toward B.

## number of ionizable sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (when “protonatable basicity dominates and lipophilicity is high”); A (when “acidic/zwitterionic character is enhanced”)
- Brief note: In many dataset-level analyses, hERG risk reflects the combined result of nonspecific hydrophobic/aromatic interactions and charge-related interactions. The total number of ionizable sites itself is not a stable threshold, but it can indirectly affect risk by changing ionization type, neutral fraction, and logD.

## exact molecular weight
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more common with larger size, especially when accompanied by higher lipophilicity/aromaticity); A (more common with smaller, more polar molecules)
- Brief note: For hERG itself, public and industrial analyses more often treat molecular size/volume as a continuous variable—modeled together with logP, PSA, aromaticity, and flexibility—rather than giving a transferable exact-MW cutoff. Therefore, exact molecular weight is usually used only as a size proxy in integrated judgment.

## fraction of sp3 carbons
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (higher sp3 fraction, often implying lower aromatic burden); B (lower sp3 fraction and stronger aromaticity)
- Brief note: In large corporate compound collections, the number of aromatic rings tends to increase together with hERG inhibition (at least over the 0–3 aromatic ring range). Therefore, “raising the sp3 fraction” (reducing planar aromatic burden) is commonly treated in project practice as a structural direction for lowering hERG risk. However, the literature rarely gives a cross-project universal threshold for “fraction of sp3 carbons” itself.

## heavy-atom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more common when heavy-atom count is higher and accompanied by stronger hydrophobic/aromatic features); A (more common when heavy-atom count is lower and polarity is higher)
- Brief note: Interpretable models from public hERG data usually treat molecular size/topological complexity as one of the key continuous factors, but they rarely provide a single hard threshold in terms of heavy-atom count. More commonly, it is interpreted together with logP, PSA, aromaticity, flexibility, and related descriptors.

## heavy-atom molecular weight
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (when larger and more hydrophobic/aromatic); A (when smaller and more polar)
- Brief note: Similar to heavy-atom count, heavy-atom molecular weight mainly enters hERG risk discussions as a proxy for size/polarizability, but there is no stable, transferable single threshold.

## Labute surface area
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (larger surface area, especially if accompanied by hydrophobic/aromatic surface); A (smaller surface area or a higher fraction of polar surface)
- Brief note: Practical physicochemical heuristics for hERG more often use operational design knobs such as logP/logD, pKa, TPSA, and aromatic ring count. Labute surface area appears more often as a QSAR descriptor in public practice than as a fixed cutoff used to guide design.

## maximum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more common when protonatable centers create pronounced positive charge distribution); A (more common when stable positive centers are absent or the overall ionization pattern is more acidic/zwitterionic)
- Brief note: Multiple mechanistic summaries link hERG blockade to positively charged centers—often protonated amines—through cation–π interactions with aromatic channel residues. Therefore, maximum absolute partial charge is better treated as an indicator of whether a strong charge center exists, rather than as a thresholded variable.

## maximum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (when the maximum positive partial charge is pronounced, usually corresponding to a protonatable basic center); A (when the maximum positive partial charge is weaker or the scaffold lacks a stably cationic center)
- Brief note: In the classic “aromatic + cation” description of hERG blockade, the positive charge center is key. However, different molecular charge calculation methods vary substantially and are sensitive to solvent and conformation, so the literature rarely gives a universal cutoff for maximum partial charge.

## minimum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable directional association with A or B (it more often reflects computational details and atom-type distribution)
- Brief note: “Minimum absolute partial charge” is usually close to 0 and often reflects the proportion of neutral/weakly polar atoms in the molecule. For hERG risk, it lacks a widely accepted actionable threshold and generally has limited interpretive value.

## minimum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (more common when stable anionic centers exist and the overall molecule is acidic/zwitterionic and more polar); B (more common when obvious negative charge centers are absent and the molecule is more hydrophobic/basic overall)
- Brief note: Consistent with the general observation that acidic classes have lower overall risk, stronger negative charge centers in a molecule often imply higher polarity and lower membrane partitioning, thereby reducing nonspecific hERG risk. However, minimum partial charge depends strongly on the charge model used and lacks a stable cutoff.

## estimated logP
- Common threshold(s) or range(s): ClogP ≤ 3 (a common “lower-risk” bin); ClogP > 3 (a common “higher-risk” bin); the “3/75” rule of thumb: ClogP > 3 and TPSA < 75 Å² corresponds to a higher-risk region
- Usually associated with: B (>3 is more common); A (≤3 is more common)
- Brief note: In analyses using dofetilide-binding inhibition as a surrogate hERG endpoint, ClogP = 3 serves as a boundary: among compounds with ClogP ≤ 3, more than 70% fall into the “low-risk” group (%inh < 15); among compounds with ClogP > 3, more than 70% fall into the “medium/high-risk” group (%inh ≥ 15, including the >50% high-risk group). This is consistent with the medicinal chemistry intuition that greater hydrophobicity favors nonspecific ion-channel binding.

## molecular weight
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more common when MW is higher and accompanied by greater lipophilicity/aromaticity); A (more common when MW is lower and polarity is higher)
- Brief note: In one internal data analysis discussing both CNS physicochemical space and a hERG surrogate endpoint, marketed CNS drugs had a median MW of about 305.3 Da, while the candidate set had a median around 360.4 Da, with higher MW often accompanied by higher lipophilicity. However, this is not a hERG-specific cutoff. A more transferable approach is to interpret MW jointly with logP, pKa, TPSA, and aromaticity.

## NH/OH group count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (more common when more NH/OH groups increase polarity and reduce logP/logD); B (more common when there are fewer NH/OH groups and the molecule is more hydrophobic)
- Brief note: NH/OH count approximately corresponds to hydrogen-bond donor count (HBD). In “property–safety” analyses, increasing polarity (for example by increasing TPSA) is often used to reduce nonspecific risk. However, stable thresholds for NH/OH group count itself are uncommon in the hERG literature; it is more often treated as a design knob that works together with TPSA and logP.

## nitrogen/oxygen atom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (when increased N/O count mainly manifests as increased polarity and higher TPSA); B (when nitrogen introduces protonatable amines and forms cationic centers)
- Brief note: The number of N/O atoms can either increase polarity (reducing nonspecific hydrophobic binding) or introduce protonatable centers (increasing cation–π risk). Therefore, N/O count alone lacks a stable threshold and usually needs to be interpreted together with strongest basic pKa, TPSA, logP, and aromatic ring count.

## aliphatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (more common when saturated/non-aromatic rings replace part of the aromatic ring burden without markedly increasing logP); B (if they increase hydrophobic bulk and raise logP, risk may increase instead)
- Brief note: For hERG, the literature focuses more on thresholds for aromatic ring count, logP, pKa, and TPSA than on aliphatic carbocycle count. The effect of aliphatic carbocycles depends more on whether they drive logP upward.

## aliphatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (more common when used to increase polarity or reduce aromatic burden without markedly increasing pKa); B (when strong basic heterocyclic amines are introduced and increase the cationic fraction)
- Brief note: Aliphatic heterocycles can increase polarity by introducing heteroatoms, which may help reduce nonspecific risk, but they can also increase basicity through amine-containing heterocycles, which may worsen hERG risk. Therefore, practice usually focuses on whether strongest basic pKa is increased and whether logP is lowered or TPSA is raised, rather than on a standalone count threshold.

## aliphatic ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (more common when aliphatic rings replace aromatic rings and also increase polarity and/or reduce lipophilicity); B (when aliphatic rings mainly increase hydrophobic bulk)
- Brief note: This descriptor itself lacks a stable threshold and is usually interpreted through whether it reduces aromatic ring count (which is related to hERG risk) and whether it drives logP upward.

## aromatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more common when aromatic carbocycle count is higher)
- Brief note: In enterprise-scale data mining, increasing numbers of aromatic rings (including aromatic heterocycles) are associated with increasing hERG inhibitory activity, at least fairly consistently over the 0–3 ring range. However, few publications provide separate hard thresholds for “aromatic carbocycles” versus “aromatic heterocycles”; most instead constrain total aromatic ring count.

## aromatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more common when aromatic heterocycle count is higher and protonatable amines are also present); A (risk may decrease when aromatic heterocycles are used mainly to increase polarity without introducing high pKa)
- Brief note: Aromatic heterocycles have a dual effect: they contribute aromaticity while also introducing heteroatoms and polarity. Therefore, their risk direction depends on whether they create the “aromatic + cationic center” combination. A stable standalone count threshold is lacking.

## aromatic ring count
- Common threshold(s) or range(s): >3 aromatic rings (including heteroaromatic rings) is often used as a rule-of-thumb boundary for “poorer developability/higher risk”; within the 0–3 aromatic ring range, the upward trend in mean hERG inhibition as aromatic ring count increases is more clearly observed
- Usually associated with: B (more common when aromatic ring count is higher); A (more common when aromatic ring count is lower)
- Brief note: In large-scale compound-set statistics from a major pharmaceutical company, hERG inhibition increased with aromatic ring count in the low-ring-count region, and the analysis proposed the mnemonic rule that “more than 3 aromatic rings” is associated with poorer developability and a higher risk of development failure. That same analysis also noted that π-stacking and hydrophobic interactions between aromatic rings and aromatic residues inside the channel are structural contributors to hERG inhibition.

## hydrogen-bond acceptor count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (when increased HBA mainly raises TPSA and lowers logP); B (when increased HBA does not improve polarity or when it combines with aromatic/basic features to form stronger binding patterns)
- Brief note: HBA often affects hERG risk indirectly through its effects on TPSA, conformation, and solvation. Public thresholds are concentrated more on a few “engineering anchors” such as TPSA = 75, logP = 3, and pKa, rather than on HBA count itself.

## hydrogen-bond donor count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (more HBDs often increase polarity and reduce logP/logD); B (fewer HBDs and greater hydrophobicity)
- Brief note: In integrated property analyses that also consider surrogate hERG readouts, HBD tends to appear together with TPSA and permeability/partition properties. For example, in empirical CNS drug-space distributions, the median HBD count is around 1, and optimizing HBD to ≤2 has been proposed as a way to improve the probability of entering the target space. However, this is a developability/permeability anchor rather than a hERG-specific threshold.

## heteroatom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (when added heteroatoms mainly raise TPSA and lower logP); B (when heteroatoms introduce strongly basic centers or fail to reduce hydrophobicity)
- Brief note: Heteroatom count can either increase polarity (favorable) or create protonatable centers (unfavorable). Because no stable threshold exists, it is generally better interpreted through the three more common anchors: TPSA, logP, and pKa.

## rotatable-bond count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more common with higher flexibility/adaptability); A (more common with lower flexibility, provided hydrophobicity is not significantly increased)
- Brief note: Physicochemical models based on public hERG datasets have treated molecular size and flexibility as important tested variables, suggesting that flexibility contributes statistically to hERG risk. However, the best cutoff is not stable across different series or ionization classes, so no universal threshold is available.

## saturated carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (more common when used to reduce aromatic ring count without pushing logP upward); B (when it mainly increases hydrophobic bulk)
- Brief note: The effect of this count on hERG depends strongly on whether aromaticity is reduced and whether logP is lowered at the same time. Threshold-based evidence is insufficient.

## saturated heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (when used to introduce polarity without markedly increasing pKa); B (when the saturated heterocycle is a strongly basic amine and raises the cationic fraction)
- Brief note: Saturated heterocycles are a common design tactic for reducing aromaticity and improving properties, but whether they reduce hERG risk depends on their net effect on pKa, logP, and TPSA; no stable threshold has been established.

## saturated ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (when saturated rings replace aromatic rings and lower logP and/or raise TPSA); B (when saturated rings increase hydrophobic bulk and drive logP upward)
- Brief note: This descriptor is usually a coarse feature of ring-type composition. In transferable hERG design rules, more operational heuristics are to limit aromatic ring count (>3 is a warning sign) and control logP (>3 is a warning sign).

## ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (when an increase in ring count mainly comes from more aromatic rings); A (when ring count rises while polarity also increases and aromatic burden does not)
- Brief note: Total ring count mixes aromatic, aliphatic, and heterocyclic rings together, making it less interpretable than aromatic ring count. Therefore, the literature tends to prefer directly constraining aromatic ring count.

## topological polar surface area
- Common threshold(s) or range(s): TPSA = 75 Å² (a commonly used threshold separating high vs. low polarity; together with logP = 3 it forms the “3/75” rule of thumb)
- Usually associated with: B (more common for the combination TPSA < 75 and logP > 3); A (more common when TPSA > 75)
- Brief note: The “3/75” rule comes from in vivo toleration data mining at a major pharmaceutical company: compounds were divided into four quadrants using rounded thresholds close to the medians, showing that when both risk factors—“C log P > 3” and “TPSA < 75”—are present, the ratio of adverse outcomes and/or pharmacological promiscuity rises significantly. This rule is not specific to hERG, but it is widely cited as an engineering anchor for nonspecific safety risk and ion-channel/off-target risk, and it has continued to be used in later hERG risk visualizations.

## QED drug-likeness
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable directional association with A or B (QED measures overall drug-likeness/developability, not hERG-specific risk)
- Brief note: QED was proposed as a 0–1 composite measure of “chemical beauty” or drug-likeness, based on desirability functions over multiple properties. It can be useful for general developability ranking, but it is not equivalent to “low hERG risk,” so there is no stable task-specific cutoff.

## Functional-group notes
- Group name: protonatable amines (tertiary amines, piperidine-like amines, etc., forming cationic centers)
- Usually associated with: B
- Brief note: Multiple summaries connect the “aromatic ring + protonatable amine” combination with hERG blockade. A common mechanistic description is that the amine is readily protonated at physiological pH, forming cation–π interactions with aromatic channel residues such as Tyr652, thereby strengthening binding.

- Group name: polyaromatic scaffolds (especially highly aromatic molecules with >3 aromatic/heteroaromatic rings)
- Usually associated with: B
- Brief note: Large-scale statistics from corporate compound collections show that mean hERG inhibitory activity rises as aromatic ring count increases over the 0–3 aromatic ring range, and propose the rule-of-thumb mnemonic that “>3 aromatic rings” is associated with poorer developability and a higher risk of development failure. This also supports constraining aromatic ring count as one of the most common strategies for reducing hERG risk.

- Group name: carboxylic acids / strongly acidic groups (pushing the molecule toward an acidic ionization type)
- Usually associated with: A
- Brief note: Physicochemical profiling analyses based on public hERG data indicate that the effect of lipophilicity on hERG differs by ionization class, with the overall trend being basic > zwitterionic > neutral > acidic. Therefore, introducing stable acidic groups often shifts a molecule toward a “lower hERG-risk class,” although exceptions may still occur if hydrophobicity is simultaneously increased substantially.

- Group name: zwitterions (scaffolds containing both cationic and anionic centers)
- Usually associated with: A (more often lower risk relative to neutral/basic compounds)
- Brief note: In public-data modeling summaries, zwitterions are treated as a class whose logP-related hERG risk lies between basic and neutral compounds (usually lower than basic, higher than acidic). Therefore, pushing a molecule toward a zwitterionic ionization type is often used as a directional strategy for reducing hERG risk, but it is not equivalent to automatic safety and still requires control of logP, TPSA, and pKa.