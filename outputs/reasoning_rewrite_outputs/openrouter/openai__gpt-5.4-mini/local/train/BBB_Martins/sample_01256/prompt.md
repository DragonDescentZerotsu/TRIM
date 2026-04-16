You are rewriting rough neighbor-based molecule-comparison notes from Explainable Boosting Machine (EBM) into high-quality reasoning SFT data for molecule local analog-comparison task BBB_Martins where option (A) means does not cross the BBB and option (B) means crosses the BBB.

Input 1. Task playbook
# BBB_Martins threshold playbook for literature-grounded BBB crossing reasoning

## topological polar surface area
- Common threshold(s) or range(s): TPSA/PSA is commonly kept **< ~90 Å²** for BBB/CNS penetration, with many sources emphasizing **~60–70 Å²** as a practical target region; in CNS MPO-style desirability ranges, **40 < TPSA ≤ 90 Å²** is “desirable” and **TPSA > 120 Å²** is “undesirable.”  
- Usually associated with: **Lower TPSA → more likely Class B (BBB+)**; **higher TPSA → more likely Class A (BBB−)**.  
- Brief note: PSA/TPSA is repeatedly highlighted as a dominant driver of passive membrane transit; transporter effects (e.g., efflux) can still override “good” PSA/TPSA.  
- Source: citeturn32view0turn36view0turn24view0turn29view0turn22view0

## ring count
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: context-dependent (can reduce flexibility, but can also increase size/lipophilicity depending on scaffold).  
- Brief note: CNS/BBB heuristics more often specify **flexibility (rotatable bonds)** and **polarity (PSA/TPSA, HBD/HBA)** than total ring count; ring count is discussed more as a contributor to conformational range/volume than as a standalone cutoff.  
- Source: citeturn32view0turn29view0

## saturated ring count
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: weak, indirect association; higher saturation can align with improved developability and different 3D shape, but BBB impact is typically mediated through TPSA/logP/logD and ionization.  
- Brief note: Saturation (and related 3D character metrics like Fsp³) is widely used as a general medicinal chemistry heuristic rather than a BBB-specific cutoff.  
- Source: citeturn35view0turn32view0

## saturated heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: context-dependent; can **increase HBA/TPSA** (hurting Class B) while also offering **tunable basicity/ionization** (which can help or hurt depending on pKa and neutral fraction).  
- Brief note: BBB-directed guidance tends to anchor on **net polarity and ionization** rather than the count of saturated heterocycles per se.  
- Source: citeturn32view0turn24view2

## saturated carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: context-dependent; saturated carbocycles can reduce H-bonding liability versus heterocycles and can lower rotatable bonds (sometimes favoring Class B if size stays controlled).  
- Brief note: Use as a **shape/rigidity proxy** only; BBB literature rarely states a standalone saturated-carbocycle cutoff.  
- Source: citeturn32view0turn29view0

## rotatable-bond count
- Common threshold(s) or range(s): Common CNS-oriented guidance places rotatable bonds **~≤5** as typical for many centrally acting drugs; other commonly quoted practical filters use **<8** rotatable bonds (and broader oral-bioavailability context notes **>10** rotatable bonds as unfavorable).  
- Usually associated with: **Lower rotatable-bond count → more likely Class B** (less conformational mobility, often better permeability); **higher counts → more likely Class A**.  
- Brief note: BBB discussions frame this as “molecular flexibility”; it is widely treated as a practical screening/triage knob.  
- Source: citeturn32view0turn29view0turn18view0

## heteroatom count
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: **Higher heteroatom counts (especially H-bonding heteroatoms) → more likely Class A** via increased polarity/hydrogen bonding; **lower counts → more likely Class B**.  
- Brief note: In BBB/CNS heuristics, “heteroatom burden” is most often expressed as **N+O count**, **HBA/HBD**, or **PSA/TPSA**, rather than total heteroatoms including sulfur/halogens.  
- Source: citeturn32view0turn27search4turn29view0

## hydrogen-bond donor count
- Common threshold(s) or range(s): Frequently quoted CNS guidelines include **HBD < 3**; CNS MPO desirability uses an even tighter “desirable” anchor at **HBD ≤ 0.5** with **HBD > 3.5** undesirable (reflecting a strong penalty for multiple donors).  
- Usually associated with: **Lower HBD → more likely Class B**; **higher HBD → more likely Class A**.  
- Brief note: Donors are repeatedly treated as high-impact because they raise desolvation cost and correlate with both reduced passive permeability and higher efflux interaction risk in many workflows.  
- Source: citeturn29view0turn24view0turn32view0

## hydrogen-bond acceptor count
- Common threshold(s) or range(s): Frequently quoted CNS guidelines include **HBA < 7**, often paired with a **total H-bonding count < 8** heuristic (donors + acceptors).  
- Usually associated with: **Lower HBA → more likely Class B**; **higher HBA → more likely Class A**.  
- Brief note: Acceptors correlate with polarity and PSA/TPSA; many BBB rules use acceptors directly or indirectly via N+O and PSA/TPSA.  
- Source: citeturn29view0turn32view0turn22view0

## aromatic ring count
- Common threshold(s) or range(s): In the BBB Score framework, aromatic ring count is explicitly step-scored with **strong penalties beyond 4** (i.e., **>4 aromatic rings scored as 0 contribution**), and the highest desirability occurs around **2 aromatic rings** (still favorable around **1–3** depending on the scoring function).  
- Usually associated with: **Very high aromatic ring counts (≥4–5) → more likely Class A** in rule-based BBB scoring; moderate aromatic ring counts can be compatible with Class B when PSA/TPSA and H-bonding stay controlled.  
- Brief note: Aromatic ring count is used as a practical proxy for “aromaticity burden” and is directly embedded in BBB screening scores (rather than being a universal standalone BBB cutoff).  
- Source: citeturn22view0turn21search1

## aromatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: often trends toward **Class A** as aromatic heterocycles commonly add HBA/TPSA; can still be **Class B-compatible** if overall HBA/HBD and TPSA remain in CNS ranges.  
- Brief note: Literature and scoring rules usually threshold **HBA/HBD/TPSA/pKa** rather than splitting aromatic rings into heteroaromatic vs carbocyclic subcounts.  
- Source: citeturn32view0turn29view0turn24view0

## aromatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: context-dependent; can support lipophilicity (helping passive diffusion) but too many aromatic carbocycles can push “aromaticity burden” into unfavorable developability space and may not rescue high TPSA/H-bonding.  
- Brief note: Consider this subcount mainly as a decomposition of “aromatic rings” used by some descriptor sets; BBB rules more commonly reference total aromatic rings.  
- Source: citeturn22view0turn32view0

## aliphatic ring count
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: context-dependent; added rings can reduce rotatable bonds (sometimes favoring Class B if MW/TPSA remain low).  
- Brief note: BBB/CNS literature discusses **rigidity/flexibility** primarily via rotatable bonds; aliphatic ring subcounts are rarely given hard cutoffs.  
- Source: citeturn32view0turn29view0

## aliphatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: context-dependent; can raise basic-site count and tune pKa (sometimes helpful), but may also raise HBA/TPSA (often harmful).  
- Brief note: For BBB, ionization state at physiological pH is emphasized more than “aliphatic heterocycle count” itself.  
- Source: citeturn32view0turn24view2turn22view0

## aliphatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: weak and indirect; may support Class B via reduced H-bonding while controlling rotatable bonds, but can also increase size/lipophilicity.  
- Brief note: Treat as a structural “shape/rigidity” proxy; no consensus BBB cutoff.  
- Source: citeturn32view0turn29view0

## nitrogen/oxygen atom count
- Common threshold(s) or range(s): A widely cited rule set uses **(N + O) ≤ 5** as indicating a high chance of brain entry; a paired rule states **if logP > (N + O)** then **logBB is positive** (i.e., higher brain than blood concentration).  
- Usually associated with: **Lower N+O → more likely Class B**; higher N+O generally pushes toward Class A via increased polarity/H-bonding capacity.  
- Brief note: This is a convenient “fast rule” style anchor; it compresses polarity into a single integer count and is often treated as a coarse screening heuristic.  
- Source: citeturn27search4turn32view0turn24view2

## NH/OH group count
- Common threshold(s) or range(s): Often operationalized via hydrogen-bonding rules: **HBD < 3** is a frequently quoted CNS threshold; some BBB-permeable profiles emphasize **very few polar hydrogens** (e.g., “<3, typically 0–1” in one guideline set).  
- Usually associated with: **Lower NH/OH (polar H) counts → more likely Class B**; higher counts → more likely Class A.  
- Brief note: NH/OH groups are a direct handle on donor burden and often track with both TPSA and desolvation penalties.  
- Source: citeturn29view0turn24view2turn32view0

## molecular weight
- Common threshold(s) or range(s): Classical BBB filters often use **MW < 450**; additional commonly cited anchors include **~400 as a cutoff** in some rulesets, and CNS MPO-style desirability marks **MW ≤ 360** as desirable and **MW > 500** as undesirable.  
- Usually associated with: **Lower MW → more likely Class B**; higher MW (especially beyond ~450–500) → more likely Class A.  
- Brief note: MW is treated as a size/transport proxy; exceptions exist (influx transporters, prodrugs, high lipophilicity), but MW remains a standard screening anchor.  
- Source: citeturn36view0turn32view0turn24view0turn29view0

## estimated logP
- Common threshold(s) or range(s): Reported optimum BBB penetration for multiple CNS-active classes has been cited around **logP ~1.5–2.7** (mean ~2.1); other CNS library rules use broader windows such as **~2–5**; CNS MPO desirability treats **ClogP ≤ 3** as desirable with **ClogP > 5** undesirable.  
- Usually associated with: **Moderate logP** (not too low, not too high) is most often associated with Class B; very low logP tends to Class A via poor permeability, while very high logP can increase liabilities (even if permeability rises).  
- Brief note: logP is repeatedly framed as entangled with size/surface area and H-bonding; interpret alongside TPSA/HBD/HBA and ionization.  
- Source: citeturn32view0turn24view0turn24view2turn29view0

## Labute surface area
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: smaller overall accessible surface area generally trends toward Class B (as a size proxy), but the effect is indirect.  
- Brief note: A commonly cited BBB-permeable guideline set includes **solvent-accessible surface area ~460–580 Å²** (with additional constraints like TPSA and polar hydrogens); this is a **proxy** anchor for “surface area”-type descriptors and should not be treated as a direct Labute-ASA equivalence.  
- Source: citeturn24view2turn32view0

## heavy-atom molecular weight
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: behaves as a **size proxy** similar to MW; larger values tend toward Class A when they reflect larger molecules (especially when TPSA/H-bonding also rise).  
- Brief note: BBB/CNS heuristics and scores almost always specify **MW** directly; “heavy-atom MW” is typically an internal descriptor choice rather than a literature-anchored cutoff.  
- Source: citeturn32view0turn24view0turn36view0

## heavy-atom count
- Common threshold(s) or range(s): In the BBB Score framework, heavy-atom count is scored with an explicit **0 contribution below 6 or above 45 heavy atoms**, and nonzero scoring in the **6–45** range (polynomial weighting).  
- Usually associated with: Extremely low or extremely high heavy-atom counts are treated as unfavorable for Class B in BBB Score-style screening; mid-range heavy-atom counts are more compatible with Class B if TPSA/ionization are aligned.  
- Brief note: This is best used as an **algorithmic anchor** (BBB Score) rather than a universal BBB cutoff; in practice it largely tracks molecular size.  
- Source: citeturn22view0turn21search1

## fraction of sp3 carbons
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: not BBB-specific; higher saturation (higher Fsp³) is often used as a developability/solubility heuristic and can indirectly help by reducing excessive aromaticity.  
- Brief note: One large-scale analysis trend reported across drug discovery phases is an increase in mean Fsp³ from **~0.36 (research compounds)** to **~0.47 (drugs)**; this is not a BBB cutoff, but provides a practical “typical range” anchor for rewriting feature-based rationales.  
- Source: citeturn35view0

## exact molecular weight
- Common threshold(s) or range(s): Same practical anchors as MW are typically used: **<450** is a common BBB filter; CNS MPO “desirable” anchor **≤360** and “undesirable” **>500**.  
- Usually associated with: **Lower exact MW → more likely Class B**; higher exact MW → more likely Class A.  
- Brief note: Exact MW vs average/isotopic MW is rarely distinguished in BBB heuristic rules; the screening logic is effectively “size constraint.”  
- Source: citeturn36view0turn24view0turn32view0

## number of ionizable sites
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: **More ionizable sites → more likely Class A** (lower neutral fraction at pH ~7.4, higher polarity); fewer ionizable sites can support Class B when PSA/logD are aligned.  
- Brief note: BBB discussions emphasize that passive membrane permeation is driven by the **neutral species fraction** in aqueous phase; strong acids/bases are often described as poor BBB penetrants, and a commonly cited pKa window for BBB penetration is **~4 to 10** (reflecting “weak” acids/bases).  
- Source: citeturn32view0turn24view2turn22view0

## number of basic sites
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: Presence of a **weakly basic center** is frequently compatible with Class B; multiple basic sites can increase polarity and reduce neutral fraction, pushing toward Class A unless compensated.  
- Brief note: Guidance is typically expressed in terms of **basic pKa limits** (e.g., CNS MPO desirability uses **pKa ≤ 8** as desirable and **>10** as undesirable; another analysis reports no CNS drugs with **basic pKa > 10.5**), rather than “count of basic sites.”  
- Source: citeturn24view0turn24view2turn32view0

## number of acidic sites
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: **Acidic groups/sites (especially strong acids) → more likely Class A** because acids are ionized at physiological pH and have low neutral fraction; neutral/weakly basic scaffolds are more compatible with Class B.  
- Brief note: CNS-focused reviews often highlight the general difficulty of carboxylic acids in BBB penetration and emphasize the criticality of the neutral species fraction; a commonly cited pKa window for BBB penetration is **~4–10** (weak acids/bases).  
- Source: citeturn32view0turn24view2

## estimated logD
- Common threshold(s) or range(s): One commonly cited BBB/CNS anchor is **0 < logD < 3** for better brain permeation (and intestinal permeability in neighboring contexts); CNS MPO desirability uses **ClogD7.4 ≤ 2** as desirable and **>4** as undesirable; other CNS library rules have used broader windows such as **~2–5**.  
- Usually associated with: **Moderate logD7.4** tends to favor Class B; very low logD suggests poor permeability (Class A), while very high logD can raise nonspecific binding and other liabilities even if permeability improves.  
- Brief note: Use logD7.4 as the “ionization-aware lipophilicity” anchor; interpret together with TPSA and the neutral fraction.  
- Source: citeturn32view0turn24view0turn24view2

## neutral fraction
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: **Higher neutral fraction at physiologic pH → more likely Class B** (supports passive diffusion); low neutral fraction → more likely Class A.  
- Brief note: BBB-oriented reviews emphasize that the neutral species in the aqueous phase is critical for membrane penetration; thus pKa/logD7.4 are often used as practical surrogates rather than a single universal “neutral fraction cutoff.”  
- Source: citeturn32view0turn24view2turn24view0

## sum basic site pKa
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: A “too-basic” profile (high basic pKa values) tends toward Class A due to high ionization at pH ~7.4; moderate basicity is more compatible with Class B.  
- Brief note: BBB/CNS rules are typically expressed using **maximum/most-basic pKa** rather than a sum; commonly used anchors include **pKa ≤ 8 (desirable)** and **pKa > 10 (undesirable)** in CNS MPO-type frameworks, and an additional report that no CNS drugs had **basic pKa > 10.5** in one comparative analysis.  
- Source: citeturn24view0turn24view2turn32view0turn22view0

## sum acidic site pKa
- Common threshold(s) or range(s): no stable literature threshold found  
- Usually associated with: More/stronger acidity tends toward Class A (greater ionization at pH ~7.4); weak-acid behavior can be compatible with Class B if neutral fraction is nontrivial.  
- Brief note: BBB/CNS guidance usually relies on per-site or limiting pKa values (not sums); one comparative analysis reports CNS drugs rarely having **acidic pKa below ~6**, and another commonly cited BBB penetration pKa window is **~4–10** (weak acids/bases).  
- Source: citeturn24view2turn32view0turn22view0

Input 2. Neighbor similarities and per-neighbor comparison notes
"""
Neighbors that crosses the BBB:
Neighbor 1: 
Similarity: 0.471
Comparison note: First, For NH/OH group count, the neighbor's NH/OH group count is value 4, while the query's NH/OH group count is value 5. The query-minus-neighbor delta is +1. This pairwise contribution is -0.7618, which pushes toward option (A): does not cross the BBB. Next, Both the neighbor and the query have azetidin-2-one (query-minus-neighbor delta +0). This pairwise contribution is -0.5998, which pushes toward option (A): does not cross the BBB. Then, Both the neighbor and the query have dialkyl thioether (query-minus-neighbor delta +0). This pairwise contribution is -0.5249, which pushes toward option (A): does not cross the BBB. After that, For topological polar surface area, the neighbor's topological polar surface area is value 220.26, while the query's topological polar surface area is value 193.63. The query-minus-neighbor delta is -26.63. This pairwise contribution is -0.4915, which pushes toward option (A): does not cross the BBB. Finally, For hydrogen-bond donor count, the neighbor's hydrogen-bond donor count is value 4, while the query's hydrogen-bond donor count is value 4. The query-minus-neighbor delta is +0. This pairwise contribution is -0.4349, which pushes toward option (A): does not cross the BBB. Step 6, The neighbor has 1 copies of carboxylic acid, while the query has 2 (query-minus-neighbor delta +1). This pairwise contribution is -0.4031, which pushes toward option (A): does not cross the BBB. Taken together, this positive-neighbor comparison pushes toward option (A): does not cross the BBB with pair score 0.0398.
Neighbor 2: 
Similarity: 0.396
Comparison note: First, Both the neighbor and the query have azetidin-2-one (query-minus-neighbor delta +0). This pairwise contribution is -0.5998, which pushes toward option (A): does not cross the BBB. Next, Both the neighbor and the query have dialkyl thioether (query-minus-neighbor delta +0). This pairwise contribution is -0.5249, which pushes toward option (A): does not cross the BBB. Then, For hydrogen-bond donor count, the neighbor's hydrogen-bond donor count is value 4, while the query's hydrogen-bond donor count is value 4. The query-minus-neighbor delta is +0. This pairwise contribution is -0.4349, which pushes toward option (A): does not cross the BBB. After that, For estimated logP, the neighbor's estimated logP is value -1.6113, while the query's estimated logP is value -0.7102. The query-minus-neighbor delta is +0.9011. This pairwise contribution is -0.4179, which pushes toward option (A): does not cross the BBB. Finally, For topological polar surface area, the neighbor's topological polar surface area is value 214.96, while the query's topological polar surface area is value 193.63. The query-minus-neighbor delta is -21.33. This pairwise contribution is -0.415, which pushes toward option (A): does not cross the BBB. Step 6, The neighbor has 1 copies of carboxylic acid, while the query has 2 (query-minus-neighbor delta +1). This pairwise contribution is -0.4031, which pushes toward option (A): does not cross the BBB. Taken together, this positive-neighbor comparison pushes toward option (A): does not cross the BBB with pair score 0.1246.
Neighbor 3: 
Similarity: 0.364
Comparison note: First, For heteroatom count, the neighbor's heteroatom count is value 13, while the query's heteroatom count is value 15. The query-minus-neighbor delta is +2. This pairwise contribution is -0.769, which pushes toward option (A): does not cross the BBB. Next, For NH/OH group count, the neighbor's NH/OH group count is value 4, while the query's NH/OH group count is value 5. The query-minus-neighbor delta is +1. This pairwise contribution is -0.7618, which pushes toward option (A): does not cross the BBB. Then, Both the neighbor and the query have azetidin-2-one (query-minus-neighbor delta +0). This pairwise contribution is -0.5998, which pushes toward option (A): does not cross the BBB. After that, For Labute surface area, the neighbor's Labute surface area is value 167.1932, while the query's Labute surface area is value 206.6453. The query-minus-neighbor delta is +39.452. This pairwise contribution is 0.585, which pushes toward option (B): crosses the BBB. Finally, For topological polar surface area, the neighbor's topological polar surface area is value 173.76, while the query's topological polar surface area is value 193.63. The query-minus-neighbor delta is +19.87. This pairwise contribution is -0.5675, which pushes toward option (A): does not cross the BBB. Step 6, Both the neighbor and the query have dialkyl thioether (query-minus-neighbor delta +0). This pairwise contribution is -0.5249, which pushes toward option (A): does not cross the BBB. Taken together, this positive-neighbor comparison pushes toward option (A): does not cross the BBB with pair score 0.0375.

Neighbors that does not cross the BBB
Neighbor 4: 
Similarity: 0.581
Comparison note: First, Both the neighbor and the query have azetidin-2-one (query-minus-neighbor delta +0). This pairwise contribution is -0.7798, which pushes toward option (A): does not cross the BBB. Next, Both the neighbor and the query have tetrazole (query-minus-neighbor delta +0). This pairwise contribution is 0.7459, which pushes toward option (B): crosses the BBB. Then, For topological polar surface area, the neighbor's topological polar surface area is value 172.46, while the query's topological polar surface area is value 193.63. The query-minus-neighbor delta is +21.17. This pairwise contribution is -0.7285, which pushes toward option (A): does not cross the BBB. After that, For QED drug-likeness, the neighbor's QED drug-likeness is value 0.2646, while the query's QED drug-likeness is value 0.2278. The query-minus-neighbor delta is -0.0367. This pairwise contribution is -0.5191, which pushes toward option (A): does not cross the BBB. Finally, For estimated logD, the neighbor's estimated logD is value -6.3195, while the query's estimated logD is value -7.3647. The query-minus-neighbor delta is -1.0452. This pairwise contribution is 0.512, which pushes toward option (B): crosses the BBB. Step 6, For hydrogen-bond donor count, the neighbor's hydrogen-bond donor count is value 3, while the query's hydrogen-bond donor count is value 4. The query-minus-neighbor delta is +1. This pairwise contribution is -0.4978, which pushes toward option (A): does not cross the BBB. Taken together, this negative-neighbor comparison pushes toward option (A): does not cross the BBB with pair score 0.0511.
Neighbor 5: 
Similarity: 0.536
Comparison note: First, Both the neighbor and the query have azetidin-2-one (query-minus-neighbor delta +0). This pairwise contribution is -0.7798, which pushes toward option (A): does not cross the BBB. Next, Both the neighbor and the query have tetrazole (query-minus-neighbor delta +0). This pairwise contribution is 0.7459, which pushes toward option (B): crosses the BBB. Then, For QED drug-likeness, the neighbor's QED drug-likeness is value 0.3057, while the query's QED drug-likeness is value 0.2278. The query-minus-neighbor delta is -0.0778. This pairwise contribution is -0.5027, which pushes toward option (A): does not cross the BBB. After that, The neighbor has thioenolether, while the query does not (query-minus-neighbor delta -1). This pairwise contribution is 0.4421, which pushes toward option (B): crosses the BBB. Finally, For estimated logD, the neighbor's estimated logD is value -4.9907, while the query's estimated logD is value -7.3647. The query-minus-neighbor delta is -2.374. This pairwise contribution is -0.4021, which pushes toward option (A): does not cross the BBB. Step 6, For neutral fraction, the neighbor's neutral fraction is absent (0), while the query's neutral fraction is absent (0). The query-minus-neighbor delta is +0. This pairwise contribution is -0.3836, which pushes toward option (A): does not cross the BBB. Taken together, this negative-neighbor comparison pushes toward option (A): does not cross the BBB with pair score 0.0664.
Neighbor 6: 
Similarity: 0.484
Comparison note: First, Both the neighbor and the query have azetidin-2-one (query-minus-neighbor delta +0). This pairwise contribution is -0.7798, which pushes toward option (A): does not cross the BBB. Next, For estimated logD, the neighbor's estimated logD is value -4.2526, while the query's estimated logD is value -7.3647. The query-minus-neighbor delta is -3.1121. This pairwise contribution is -0.4922, which pushes toward option (A): does not cross the BBB. Then, For QED drug-likeness, the neighbor's QED drug-likeness is value 0.5381, while the query's QED drug-likeness is value 0.2278. The query-minus-neighbor delta is -0.3103. This pairwise contribution is -0.4648, which pushes toward option (A): does not cross the BBB. After that, For maximum partial charge, the neighbor's maximum partial charge is value 0.3523, while the query's maximum partial charge is value 0.3522. The query-minus-neighbor delta is -0.0001. This pairwise contribution is -0.3873, which pushes toward option (A): does not cross the BBB. Finally, For neutral fraction, the neighbor's neutral fraction is absent (0), while the query's neutral fraction is absent (0). The query-minus-neighbor delta is +0. This pairwise contribution is -0.3836, which pushes toward option (A): does not cross the BBB. Step 6, For NH/OH group count, the neighbor's NH/OH group count is value 2, while the query's NH/OH group count is value 5. The query-minus-neighbor delta is +3. This pairwise contribution is -0.3469, which pushes toward option (A): does not cross the BBB. Taken together, this negative-neighbor comparison pushes toward option (A): does not cross the BBB with pair score 0.0128.
"""

Input 3. Final prediction label
option (A): does not cross the BBB

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
