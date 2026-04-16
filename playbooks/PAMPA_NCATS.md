# PAMPA_NCATS Molecular Property Practical Playbook

This task corresponds to PAMPA_NCATS in the Therapeutics Data Commons benchmark dataset platform. The public description indicates that it is the NCATS pH 7.4 PAMPA passive transmembrane permeability binary classification task. A common public formulation is: logPeff ≤ 2.0 is labeled low/moderate permeability, > 2.5 is labeled high permeability, and borderline samples between 2.0 and 2.5 are often removed. In the adjacent public NCATS pH 5 PAMPA panel, 0–10, 10–100, and >100 ×10^-6 cm/s are divided into low, medium, and high, respectively.

Because PAMPA mainly reads out **passive transmembrane diffusion**, and does not include active transport or paracellular pathways, the most robust priority order is usually: **ionization state** (neutral fraction / pKa / ionizable sites) → **lipophilicity** (logD / logP) → **polarity and hydrogen bonding** (TPSA / HBA / HBD / NH/OH) → **size** (MW).

## neutral fraction
- Common threshold(s) or range(s): In practice, **>10% neutral species** and **<1% neutral species** can be used as useful interpretation anchors; the former is much more likely to give **B**, while the latter is commonly seen in **A**.
- Usually associated with: A higher neutral fraction tends to favor **B**; an extremely low neutral fraction tends to favor **A**.
- Brief note: This is not a hard NCATS threshold, but an interpretation rule based on Henderson–Hasselbalch. It is especially important for PAMPA because this system is driven mainly by permeation of the neutral species.
- Source: Task-specific mechanism: PAMPA mainly reads out the neutral species; interpretation rule: acid–base equilibrium / Henderson–Hasselbalch.

## estimated logD
- Common threshold(s) or range(s): **logD7.4 around 1–3** is the most common “sweet spot” proxy; the center of the Golden Triangle is approximately **logD7.4 ≈ 1.5, MW ≈ 350**.
- Usually associated with: Around **1–3** tends to favor **B**; clearly lower values often favor **A**; very high logD is not necessarily better.
- Brief note: Task-adjacent data and industry experience both view logD as critical, but very high logD can cause membrane retention / recovery issues, so it must be interpreted together with MW, TPSA, and pKa.
- Source: Proxy rules: logD sweet spot and the Golden Triangle; task-adjacent observations: tradeoff between high logD and PAMPA recovery.

## strongest acidic pKa
- Common threshold(s) or range(s): At **pH 7.4**, a monoprotic acid with **pKa ≤ 5.4** has roughly only **≤1% neutral species** left; at **pKa ≤ 6.4**, the neutral fraction is still usually **≤10%**.
- Usually associated with: Lower acidic pKa tends to favor **A**; higher acidic pKa or the absence of acidic sites tends to favor **B**.
- Brief note: These are Henderson–Hasselbalch-derived explanatory thresholds, not direct NCATS training cutoffs. For weak acids, the persistent anionic state usually suppresses PAMPA.
- Source: PAMPA mainly reflects neutral-species permeation; persistent weak-acid anions reduce intestinal passive permeability.

## strongest basic pKa
- Common threshold(s) or range(s): At **pH 7.4**, a monoprotic base with **pKa ≥ 9.4** has roughly only **≤1% neutral species** left; at **pKa ≥ 8.4**, the neutral fraction is usually already **≤10%**.
- Usually associated with: Very high basic pKa tends to favor **A**; milder or near-neutral bases tend to favor **B**.
- Brief note: This is also a Henderson–Hasselbalch-derived explanatory threshold. In PAMPA, the fact that a strong base is “almost always protonated” is usually more unfavorable than in cell-based systems.
- Source: PAMPA mainly involves neutral-species transmembrane diffusion; acid–base equilibrium determines the neutral/ionic ratio.

## number of acidic sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More acidic sites, especially in polyacidic molecules, usually favor **A**.
- Brief note: For PAMPA, each additional acidic site adds another layer of risk for anionic/zwitterionic speciation; in practice, polyacids are often avoided first.
- Source: Task mechanism: PAMPA is driven mainly by neutral-species permeation; weak-acid anions are unfavorable for passive permeability.

## number of basic sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Polybasic molecules usually favor **A**; **0–1 protonatable basic sites** are more likely to yield **B**.
- Brief note: Multiple basic centers markedly increase the probability of protonation at pH 7.4, especially when the strongest basic pKa is high.
- Source: Task mechanism: PAMPA mainly reflects neutral-species permeation; in modern drugs, “one or no ionizable site” is very common.

## number of ionizable sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: **0–1 ionizable sites** tend to favor **B**; more sites tend to favor **A**.
- Brief note: In modern small-molecule drugs, more than 60% have one or no ionizable sites; the more sites there are, the more complex the microspecies distribution becomes, and the harder it is to maintain a meaningful neutral fraction.
- Source: Proxy: statistics on drug acid–base profiles; task mechanism: PAMPA mainly depends on the neutral species.

## exact molecular weight
- Common threshold(s) or range(s): **<500 Da** is the most commonly used classical upper limit; a more practical working zone is often **about 200–500 Da**, with the Golden Triangle centered around **350 Da**.
- Usually associated with: Lower MW tends to favor **B**; **>500 Da** tends to favor **A**.
- Brief note: However, NCATS-adjacent data indicate that both classes are abundant in the 300–500 Da range, so MW should be interpreted together with logD and TPSA.
- Source: Classical Rule of Five; Golden Triangle; neighboring NCATS pH 5 data distribution.

## fraction of sp3 carbons
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: No stable direction; higher saturation sometimes only weakly favors **B** in general drug-likeness.
- Brief note: fsp3 belongs more to the “drug-likeness / clinical success rate” dimension and is not a common hard threshold in PAMPA.
- Source: Proxy: fsp3 literature focuses more on general drug-likeness than on passive PAMPA cutoffs.

## heavy-atom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Very high heavy-atom count often tends toward **A**, but there is no independent general cutoff.
- Brief note: Passive permeability literature usually uses MW, TPSA, HBA/HBD, and logD directly rather than heavy-atom count for decision-making.
- Source: NCATS feature importance and ADMET rule literature emphasize MW / polarity / lipophilicity more strongly.

## heavy-atom molecular weight
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Higher values generally tend toward **A**, but there is no independent stable threshold.
- Brief note: In practice, one usually falls back to standard MW rather than using heavy-atom molecular weight.
- Source: Classical rules use ordinary MW; modern ADMET practice does as well.

## Labute surface area
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Larger surface area by itself does not define a stable A/B cutoff.
- Brief note: PAMPA / passive permeability literature more commonly uses **TPSA** or charge-weighted VSA descriptors rather than raw Labute surface area.
- Source: NCATS models place more emphasis on TPSA and charge-related VSA descriptors.

## maximum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Stronger local charge extrema usually tend toward **A**.
- Brief note: NCATS does indicate that “charge-related surface area” is important, but the literature does not provide unified hard thresholds for atomic partial charge.
- Source: NCATS feature importance analysis.

## maximum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Higher positive charge extrema usually tend toward **A**.
- Brief note: This value is of limited use by itself and must be interpreted together with pKa and neutral fraction; otherwise misclassification is easy.
- Source: NCATS charge descriptors; PAMPA is driven mainly by neutral-species permeation.

## minimum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: No stable direction.
- Brief note: This RDKit descriptor is rarely a common interpretation axis in medicinal chemistry or PAMPA literature.
- Source: NCATS feature-importance results do not provide a transferable cutoff for this descriptor.

## minimum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More negative extrema usually tend toward **A**.
- Brief note: In practice, it is more reliable to track **acidic functional groups + acidic pKa + TPSA** than the minimum atomic partial charge itself.
- Source: NCATS charge descriptors; weak-acid anions reduce passive permeability.

## estimated logP
- Common threshold(s) or range(s): **1–3** is often regarded as a range more favorable for balancing oral exposure and passive diffusion; **>5** is the classical Rule of Five warning threshold.
- Usually associated with: Moderate logP tends to favor **B**; very low values often favor **A**; very high values often introduce a “permeability / solubility / recovery tradeoff.”
- Brief note: In NCATS-adjacent data, both high- and low-permeability compounds are often found in the **logP 2–6** range, indicating that logP alone is insufficient.
- Source: Proxy: logP 1–3 and Rule of Five; task-adjacent observations: NCATS pH 5 distributions and feature importance.

## molecular weight
- Common threshold(s) or range(s): **<500 Da** is the classical upper limit; a more practical working zone is often **about 200–500 Da**, with the center often drawn around **about 350 Da**.
- Usually associated with: Lower MW tends to favor **B**; **>500 Da** tends to favor **A**.
- Brief note: In task-adjacent NCATS data, both classes are very common in the **300–500 Da** range, so MW should not be treated as a standalone rule.
- Source: Classical Rule of Five; Golden Triangle; NCATS-adjacent distribution.

## NH/OH group count
- Common threshold(s) or range(s): **>5** is the classical “poor absorption or permeation” warning threshold.
- Usually associated with: Fewer NH/OH groups tend to favor **B**; **>5** clearly tends to favor **A**.
- Brief note: This is basically the HBD dimension from the Rule of Five; reducing NH/OH is also one of the most common medicinal-chemistry moves used to improve passive permeability.
- Source: Classical Rule of Five; increasing hydrogen bonding lowers passive permeability.

## nitrogen/oxygen atom count
- Common threshold(s) or range(s): **>10** is a classical risk anchor from the original Lipinski/USAN analysis.
- Usually associated with: **≤10** tends to favor **B**; **>10** tends to favor **A**.
- Brief note: This is a crude but practical proxy for “polarity / hydrogen-bond burden”; when possible, HBA/HBD and TPSA should still be prioritized.
- Source: The original Rule of Five / USAN analysis directly used the total N+O count.

## aliphatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: No stable direction.
- Brief note: There is no widely accepted independent PAMPA threshold for “aliphatic carbocycle count.”
- Source: Ring-count literature discusses developability tendencies rather than passive PAMPA cutoffs.

## aliphatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: No stable direction; these are usually more tolerated than carboaromatic-rich structures.
- Brief note: This is a general developability observation, not a task-specific threshold.
- Source: The influence of ring type on developability is more qualitative than quantitative.

## aliphatic ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: No stable direction.
- Brief note: The literature does not provide a widely accepted rule linking “total aliphatic ring count” to PAMPA class labels.
- Source: The influence of ring count appears more as a developability proxy.

## aromatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Higher values often imply **A** risk.
- Brief note: Increasing aromatic carbocycles usually harms general developability, especially carboaromatics, but this is not a PAMPA hard threshold.
- Source: Literature on aromatic ring count / ring type and developability.

## aromatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: High values may indicate **A** risk, but less strongly than aromatic carbocycles.
- Brief note: There is no widely used independent PAMPA cutoff.
- Source: Aromatic ring counts mainly serve as general developability proxies.

## aromatic ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: More aromatic rings usually imply greater **A** risk.
- Brief note: This is a known risk dimension in drug-likeness / developability literature, but not a general PAMPA threshold.
- Source: Aromatic ring count negatively affects developability.

## hydrogen-bond acceptor count
- Common threshold(s) or range(s): **≤10** is the classical upper limit; another commonly used proxy is **HBA + HBD ≤ 12**.
- Usually associated with: Lower HBA tends to favor **B**; **>10** tends to favor **A**.
- Brief note: This is one of the most commonly used proxy rules for passive absorption / oral exposure, although it is not PAMPA-specific.
- Source: Classical Rule of Five; Veber rule.

## hydrogen-bond donor count
- Common threshold(s) or range(s): **≤5** is the classical upper limit; another commonly used proxy is **HBA + HBD ≤ 12**.
- Usually associated with: Lower HBD tends to favor **B**; **>5** tends to favor **A**.
- Brief note: HBD is one of the passive-permeability factors most often deliberately reduced in medicinal chemistry.
- Source: Classical Rule of Five; Veber rule; increasing hydrogen bonding lowers passive permeability.

## heteroatom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Higher heteroatom count often tends toward **A**.
- Brief note: In practice, **N+O, HBA/HBD, and TPSA** are used more often than total heteroatom count.
- Source: Classical rules and PSA literature both prefer direct polarity / H-bond descriptors.

## rotatable-bond count
- Common threshold(s) or range(s): **≤10** is the most classical and most commonly used anchor.
- Usually associated with: Fewer rotatable bonds tend to favor **B**; **>10** tends to favor **A**.
- Brief note: This is a proxy for oral / passive absorption rather than a PAMPA-specific hard threshold, but it is extremely common in early screening.
- Source: Veber rule.

## saturated carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: No stable direction; these are generally more tolerable relative to a high aromaticity burden.
- Brief note: “More saturated” is more of a general drug-likeness trend than a PAMPA numerical threshold.
- Source: Literature on ring type and saturation.

## saturated heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: No stable direction; generally more acceptable than many aromatic rings.
- Brief note: There is no transferable task-specific cutoff.
- Source: Ring type / saturation mainly provides qualitative rather than quantitative interpretation.

## saturated ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: No stable direction.
- Brief note: The significance of saturated ring count depends strongly on the overall scaffold, TPSA, and logD.
- Source: Literature on ring type and saturation.

## ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Very high ring count often implies **A** risk, but there is no unified cutoff.
- Brief note: Some general drug-likeness filters restrict total ring count, but that is not a passive PAMPA rule.
- Source: Ring-count literature mainly discusses general developability.

## topological polar surface area
- Common threshold(s) or range(s): **≤140 Å²** is the most common lenient upper limit; **≤131.6 Å²** is the Egan filter; if stronger passive transmembrane permeation is desired, a lower value is often preferred in practice.
- Usually associated with: Lower TPSA tends to favor **B**; **>131–140 Å²** tends to favor **A**.
- Brief note: In NCATS-adjacent data, many compounds are already **<100 Å²**, and both classes are present, so TPSA is necessary but not sufficient.
- Source: Veber and Egan as proxy rules; NCATS-adjacent distributions and feature importance.

## QED drug-likeness
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: Higher QED only **indirectly** tends to favor **B**; it is not a direct PAMPA rule.
- Brief note: If used only as a general drug-likeness proxy, **>0.67** can be treated as “attractive,” **0.49–0.67** as intermediate, and **<0.34** as low; but these are not PAMPA thresholds.
- Source: The original QED paper and later interpretive thresholds.

## Functional-group notes

- Group name: carboxylic acid
- Usually associated with: **A**
- Brief note: This is one of the most typical permeability-limiting groups; at pH 7.4 it readily becomes an anion, which is usually strongly disadvantageous in PAMPA. In medicinal chemistry, esterification or acidic bioisosteres are often used to mitigate this.
- Source: Reviews of permeability-limiting groups; persistent weak-acid anions reduce passive permeability.

- Group name: phenol / polyhydroxy / donor-rich OH,NH motifs
- Usually associated with: **A**
- Brief note: These groups raise HBD/TPSA and strengthen interactions with water; multiple OH or NH groups often markedly reduce passive PAMPA permeability.
- Source: Studies of common permeability-limiting groups; increasing hydrogen bonding lowers passive permeability.

- Group name: guanidine / amidine
- Usually associated with: **A**
- Brief note: These groups are highly basic and are often strongly protonated at physiological pH; the classical problem is **high polarity and low membrane permeability**. Many successful examples rely on prodrug masking to rescue permeability.
- Source: Relevant prodrug and review literature consistently identifies low permeability of guanidino/amidine motifs as a core issue.

- Group name: quaternary ammonium / permanently charged cation
- Usually associated with: **A**
- Brief note: A permanent positive charge is inherently incompatible with passive transmembrane diffusion; classical drug-likeness literature places these structures on the difficult side for passive absorption.
- Source: Ionic molecules do not readily cross membranes by simple passive diffusion; classical oral-drug-likeness rules also treat quaternary ammonium salts as difficult or atypical cases.

- Group name: classical zwitterion motif
- Usually associated with: **A**
- Brief note: Typical “acid + base” zwitterions often perform poorly in PAMPA because the neutral nonionic fraction is too low; recent re-analyses also support that their membrane permeability is determined mainly by the **neutral fraction**, not by the zwitterion itself.
- Source: Re-analysis of zwitterion membrane permeability; reviews of acid–base properties.

- Group name: ester masking of a polar/acidic pharmacophore
- Usually associated with: **B**
- Brief note: When used as a **prodrug masking group**, it is often associated with higher passive permeability, especially for low-permeability parent compounds such as carboxylic acids or guanidino motifs.
- Source: Zanamivir / guanidino prodrug literature and prodrug reviews.