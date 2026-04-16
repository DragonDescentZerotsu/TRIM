You are rewriting rough single-molecule analysis notes from Explainable Boosting Machine (EBM) into high-quality reasoning SFT data for task CYP3A4_Substrate_CarbonMangels where option (A) means is not a substrate to the enzyme CYP3A4 and option (B) means is a substrate to the enzyme CYP3A4.

Input 1. Task playbook
# CYP3A4_Substrate_CarbonMangels Quick Reference Manual for Molecular Property Thresholds

## neutral fraction
- Common threshold(s) or range(s): Using physiological pH ≈ 7.4 as the reference, |pH − pKa| = 1 usually corresponds to about a 90:10 ionized/neutral ratio, while |pH − pKa| = 2 usually corresponds to about 99:1. This provides interpretable anchor points for converting "neutral fraction."
- Usually associated with: As a proxy for adjacent tasks such as permeability- and exposure-driven metabolic accessibility, a higher neutral fraction generally favors passive permeability, whereas pronounced multicharge or strong ionization (very low neutral fraction) is often associated with poorer permeability and therefore tends to bias the compound toward non-substrate behavior along the "can it reach and be metabolized" pathway.
- Brief note: The label in CYP3A4_Substrate_CarbonMangels is whether a compound is a CYP3A4 substrate (i.e., metabolized by CYP3A4). Neutral fraction is usually not a direct decision rule by itself, but indirectly affects substrate assignment through its effects on logD, permeability, and cellular or microsomal exposure, so it is best treated as a proxy variable.
- Source: Approximate ionization ratio anchors from the Henderson-Hasselbalch relationship, together with review and practice frameworks discussing how ionization at pH 7.4 affects permeability and clearance trends.

## estimated logD
- Common threshold(s) or range(s): The "Golden Triangle" framework, used as a proxy for oral absorption × clearance, gives an empirical MW-logD7.4 region: at MW = 200, the baseline is about logD = 2-5; at MW ≈ 450, the apex is about logD = 1-2; around the center, logD ≈ 1.5 and MW ≈ 350 are described as a more balanced region.
- Usually associated with: In this proxy framework, excessively low logD7.4 (more polar compounds) is more likely to be permeability-limited, while excessively high logD7.4 (more hydrophobic compounds) is more likely to be associated with clearance or metabolism-related liabilities, such as increased in vitro clearance or other developability risks.
- Brief note: This is an empirical window for optimizing clearance and absorption, not a hard threshold for whether a compound is a CYP3A4 substrate. However, because substrate assignment is strongly related to whether a molecule can effectively reach the enzyme and react with it in vitro or in vivo, logD7.4 is frequently used as a serious engineering proxy.
- Source: The original Golden Triangle paper and its interpretation of empirical MW-logD7.4 boundaries.

## strongest acidic pKa
- Common threshold(s) or range(s): Using pH = 7.4 as the reference, if the strongest acidic pKa ≤ 5.4 (pH − pKa ≥ 2), the acidic site is usually about ≥99% deprotonated and thus more negatively charged; if pKa ≈ 6.4 (difference of 1), the ratio is about 91%/9% ionized/neutral.
- Usually associated with: Stronger acids (lower pKa) are more likely to exist as anions under physiological conditions and are often associated with lower passive permeability. In the substrate-accessibility proxy chain, this may bias the compound toward non-substrate behavior, although there are exceptions such as intramolecular hydrogen bonding or zwitterionic "molecular chameleon" behavior that can reduce the polarity penalty.
- Brief note: pKa is not a universal hard threshold for CYP3A4 substrate assignment. A more practical approach is to map pKa to neutral fraction and charge state, then interpret it jointly with logD, TPSA, and related properties.
- Source: Henderson-Hasselbalch ionization anchors and general ADMET reviews on how acid-base properties affect descriptors such as logD.

## strongest basic pKa
- Common threshold(s) or range(s): Using pH = 7.4 as the reference, if the strongest basic pKa ≥ 9.4 (pKa − pH ≥ 2), the basic site is usually about ≥99% protonated and thus more positively charged; if pKa ≈ 8.4 (difference of 1), the ratio is about 91%/9% ionized/neutral when considered as the conjugate acid.
- Usually associated with: Stronger bases (higher pKa) are more likely to carry positive charge under physiological conditions and are often associated with lower passive permeability. In the proxy sense of whether the molecule can sufficiently enter the cellular or membrane environment and contact CYP3A4, this may bias it toward non-substrate behavior or require higher hydrophobicity (logD) for compensation.
- Brief note: A strong base is not necessarily a non-substrate. Many CYP3A4 substrates contain amines and are still metabolized. A more robust approximation is to use the chain "charge state -> logD/permeability -> exposure/metabolism."
- Source: Henderson-Hasselbalch ionization anchors and empirical summaries linking ionization state to permeability and clearance trends.

## number of acidic sites
- Common threshold(s) or range(s): No stable literature threshold found. Common medicinal chemistry filters usually do not impose a hard threshold on the number of acidic sites, but instead capture related effects through HBD/HBA, TPSA, logD/logP, and similar descriptors.
- Usually associated with: More acidic sites make formation of multianionic species at physiological pH more likely, decreasing neutral fraction and logD while increasing TPSA. In accessibility-based proxy terms, this tends to bias the compound toward non-substrate behavior.
- Brief note: If task data come from in vitro microsomal or cellular systems, multianionic compounds may also introduce confounding from transport, binding, or permeability effects in the observed metabolism or substrate behavior. Therefore, the number of acidic sites is not recommended as a single-factor rule.
- Source: Henderson-Hasselbalch relationships between pKa and ionization, plus classical ADME filter frameworks that do not include hard thresholds for acidic site count.

## number of basic sites
- Common threshold(s) or range(s): No stable literature threshold found. In practice, this is more often reflected indirectly through charge state or neutral fraction, logD7.4, TPSA, HBD/HBA, and related properties.
- Usually associated with: More basic sites increase the likelihood of multiprotonation and multiple positive charges, which often reduce passive permeability. In the proxy sense of whether the compound can sufficiently contact CYP3A4, this tends to bias it toward non-substrate behavior or require higher hydrophobicity to compensate.
- Brief note: Polyamine compounds can still be CYP3A4 substrates, but site count alone is difficult to interpret because the same number of basic sites can correspond to very different pKa values, conformations, and intramolecular hydrogen-bonding behavior.
- Source: Henderson-Hasselbalch and empirical frameworks relating ionization to permeability and clearance.

## number of ionizable sites
- Common threshold(s) or range(s): No stable literature threshold found. Common drug-likeness and oral developability rules do not usually use the total number of ionizable sites as a hard threshold.
- Usually associated with: More ionizable sites increase the probability of multicharged or zwitterionic states, which can limit passive permeability. As a proxy, this shifts compounds toward non-substrate behavior or implies a need for higher hydrophobicity or special intramolecular hydrogen-bonding strategies.
- Brief note: In some chemical spaces, such as beyond-Rule-of-5 compounds, macrocycles, and molecules with strong intramolecular hydrogen bonding, there are many exceptions in which compounds with many ionizable sites are still permeable. Thus this feature is better interpreted jointly with logD7.4, TPSA, rotatable bonds, and related descriptors.
- Source: Golden Triangle discussions of ionization and permeability, and general medicinal chemistry filters that rely on integrated properties rather than site count alone.

## exact molecular weight
- Common threshold(s) or range(s): Common oral drug-likeness anchors include MW < 500 under Lipinski Rule of Five; MW < 400 with logP < 4 under GSK 4/400; MW 150-500 in the SwissADME bioavailability radar size window; MW 200-600 in the Muegge/Bayer filter; and the Golden Triangle observation that above MW ≈ 450 it becomes harder to achieve both low clearance and high permeability simultaneously.
- Usually associated with: In the proxy sense of CYP3A4 substrate accessibility, very low MW may indicate insufficient hydrophobic surface area to enter the relevant membrane environment or binding pocket, whereas very high MW more often brings permeability limitations or broader ADMET liabilities. This is not a direct substrate rule.
- Brief note: Exact molecular weight and molecular weight are usually numerically very similar, differing mainly by isotopic versus average mass, so the same empirical windows can generally be used for interpretation.
- Source: Lipinski Rule of Five, GSK 4/400, SwissADME bioavailability radar, Muegge filter, and the Golden Triangle framework.

## fraction of sp3 carbons
- Common threshold(s) or range(s): The SwissADME bioavailability radar gives Fraction Csp3 ≥ 0.25 as a lower bound for saturation in oral developability screening. Another empirical anchor, Fsp3 ≥ 0.42, has been used as a threshold for a more desirable or more three-dimensional profile associated with clinical success.
- Usually associated with: A higher sp3 fraction usually implies greater three-dimensionality and lower aromatic burden, which tends to be favorable across multiple developability metrics. As a proxy, this may reduce risks associated with highly aromatic and highly hydrophobic compounds, including CYP inhibition or nonspecific binding, and therefore may lower the probability of showing strong CYP3A4 interaction. This is not a hard substrate versus non-substrate rule.
- Brief note: Fraction of sp3 carbons is usually a secondary feature for whether a compound is a CYP3A4 substrate. Its main influence is indirect, via aromatic ring count, logP/logD, solubility, and permeability, which together shape overall metabolic exposure and interaction risk.
- Source: SwissADME bioavailability radar and empirical Fsp3 anchors from medicinal chemistry literature.

## heavy-atom count
- Common threshold(s) or range(s): No stable literature threshold found. Heavy-atom count is more often used as a proxy for size or volume than as an independent hard threshold.
- Usually associated with: As a size proxy, increased heavy-atom count often correlates with higher MW and greater surface area. In the Golden Triangle context, the authors note that in cases involving high-atomic-weight elements such as halogens, heavy-atom count, surface area, or volume may represent true size better than MW.
- Brief note: If both MW and heavy-atom count are included in feature engineering, a common strategy is to treat heavy-atom count as a composition-correction signal for MW, for example by identifying halogen-rich molecules in which MW is high but geometric size does not increase proportionally.
- Source: Golden Triangle discussion of heavy-atom count, surface area, and volume as potentially better size descriptors.

## heavy-atom molecular weight
- Common threshold(s) or range(s): No stable literature threshold found. Most common windows are defined for total MW, not separately for MW contributed only by heavy atoms.
- Usually associated with: Heavy-atom molecular weight is strongly correlated with total MW and can serve as an alternative size proxy. In compounds enriched in halogens, sulfur, or other high-atomic-weight elements, it may help identify molecules whose MW is high without proportional change in geometric size.
- Brief note: Unless there is additional evidence that heavy-atom molecular weight has an independent threshold specifically for CYP3A4 substrate behavior, it is best used only as a supplementary feature to MW.
- Source: Rule-of-Five, SwissADME, and Muegge use total MW windows, whereas the Golden Triangle discusses alternative size proxies.

## Labute surface area
- Common threshold(s) or range(s): No stable literature threshold found. Common rules rarely define a hard threshold specifically for Labute approximate surface area.
- Usually associated with: As a surface area or size proxy, increased ASA usually indicates a larger hydrophobic contact area. In settings where MW may overestimate size, total surface area, volume, or heavy-atom count may provide a closer representation of true size.
- Brief note: Labute surface area is commonly used as a general geometric feature in machine-learning ADMET models, but it rarely appears by itself in public medicinal chemistry hard-threshold rules, so it is usually more appropriate as a continuous model feature than as a manually chosen cutoff.
- Source: Common QED and Rule-of-Five style frameworks do not include hard ASA thresholds, while the Golden Triangle discusses surface area as a size proxy.

## maximum absolute partial charge
- Common threshold(s) or range(s): No stable literature threshold found. Mainstream drug-likeness and developability rules more commonly use MW, logP/logD, TPSA, HBD/HBA, rotatable bonds, aromatic rings, and similar descriptors, rather than hard cutoffs on extrema of partial charges.
- Usually associated with: Extreme local charges (large |q| values) often co-vary with strongly polar functional groups and with higher HBD, HBA, and TPSA, indirectly affecting permeability, binding, and metabolic accessibility. However, there is no stable, transferable rule mapping |q| thresholds to substrate versus non-substrate behavior.
- Brief note: Partial charges depend strongly on the charge model and on the assumed conformation and protonation state, so comparability across datasets is poor. This is one reason they are less often used as hard thresholds in the literature.
- Source: QED component descriptors and common filter systems showing that mainstream threshold frameworks do not rely on extrema of partial charge.

## maximum partial charge
- Common threshold(s) or range(s): No stable literature threshold found, similar to maximum absolute partial charge.
- Usually associated with: A larger maximum positive partial charge usually arises from charge concentration at a strong basic center under a particular protonation state, and as a proxy it aligns with greater ionization. However, there is no portable hard threshold.
- Brief note: If an interpretable anchor is needed, a more robust alternative is to use strongest basic pKa or neutral fraction to quantify protonation directly at a specified pH.
- Source: QED and common medicinal chemistry threshold systems do not use extrema of partial charge, whereas Henderson-Hasselbalch ionization relationships are more stable.

## minimum absolute partial charge
- Common threshold(s) or range(s): No stable literature threshold found. Partial-charge descriptors generally lack cross-model-consistent hard thresholds.
- Usually associated with: This value mostly reflects the numerically least polar atom and does not have a widely accepted interpretation boundary for substrate versus non-substrate behavior.
- Brief note: If a model depends on this feature, interpretation is better focused on more literature-supported descriptors that co-vary more strongly with it, such as TPSA, HBD/HBA, and logD/logP.
- Source: QED and mainstream filters select interpretable hard thresholds from other descriptor families rather than from partial-charge extrema.

## minimum partial charge
- Common threshold(s) or range(s): No stable literature threshold found.
- Usually associated with: A more negative minimum partial charge usually corresponds to strong electronegative functional groups such as sulfonyl or carboxylate-related motifs under a particular ionization or conformation, and as a proxy it tends to track with higher polarity and higher TPSA. However, there is no hard threshold.
- Brief note: For engineering-style thresholds, it is more practical to use descriptors with mature threshold systems such as TPSA, HBA/HBD, and logD7.4.
- Source: QED and classical filters such as Rule of Five, Veber, Egan, and Muegge provide interpretable threshold sets that do not rely on extrema of partial charge.

## estimated logP
- Common threshold(s) or range(s): Typical drug-likeness windows include logP ≤ 5 under Rule of Five; logP ≤ 4 under GSK 4/400; -0.4 ≤ logP ≤ 5.6 under Ghose; -2 ≤ logP ≤ 5 under Muegge; and the Pfizer 3/75 rule highlights a relative risk region in a toxicity context where logP > 3 and TPSA < 75.
- Usually associated with: For CYP3A4-related endpoints, reviews note that substrate kinetics and metabolic behavior are often linked to hydrophobicity measured by logP or logD7.4. As a proxy, a low logP, reflecting strong hydrophilicity, often makes it harder for a compound to achieve substantial exposure in membrane or enzyme environments.
- Brief note: logP is the intrinsic hydrophobicity of the neutral form. For ionizable molecules under physiological conditions, logD7.4 is usually a better descriptor of effective hydrophobicity.
- Source: Rule of Five, GSK 4/400, Ghose, Muegge, Pfizer 3/75, and reviews on hydrophobicity in relation to CYP3A4 kinetics.

## molecular weight
- Common threshold(s) or range(s): MW < 500 under Rule of Five; MW < 400 under GSK 4/400; MW 150-500 in the SwissADME radar; MW 200-600 in Muegge; and the Golden Triangle notes that above MW ≈ 450 it becomes harder to remain in the high-probability region for both low clearance and high permeability.
- Usually associated with: In the proxy sense of substrate accessibility, moderate MW, roughly in the few-hundred-dalton range, is more commonly seen in chemical space that is orally accessible, permeable, and able to contact hepatic or intestinal CYP3A4. Very high or very low MW often comes with systematic risks involving permeability, solubility, or clearance.
- Brief note: If a more engineering-oriented anchor is needed for CYP3A4 substrate interpretation, MW is often most informative when examined together with logD7.4 in the Golden Triangle framework.
- Source: Rule of Five, GSK 4/400, SwissADME radar, Muegge, and the Golden Triangle.

## NH/OH group count
- Common threshold(s) or range(s): As an approximate count of hydrogen-bond donor sites, Rule of Five gives HBD ≤ 5, and Muegge also gives HBD ≤ 5.
- Usually associated with: Higher NH/OH counts usually increase polarity and TPSA while reducing permeability. In the proxy sense of whether a molecule can sufficiently contact CYP3A4, an excessive donor count tends to bias toward non-substrate behavior unless compensated by greater hydrophobicity or intramolecular hydrogen bonding.
- Brief note: NH/OH group count is not always exactly equivalent to the formal HBD counting rule because different software may define certain donors differently, but in practice it is often a same-direction signal.
- Source: Lipinski Rule of Five and the Muegge filter definitions for hydrogen-bond donor thresholds.

## nitrogen/oxygen atom count
- Common threshold(s) or range(s): No stable literature threshold found. Mainstream threshold systems more often define windows directly on HBA/HBD and TPSA, while N/O atom count is usually only a compositional approximation of those quantities.
- Usually associated with: Increasing N/O atom count usually increases HBA count and TPSA, thereby lowering passive permeability. In the proxy chain for substrate assignment, this may bias the compound toward non-substrate behavior.
- Brief note: If interpretable thresholds are needed, it is generally better to use descriptors with mature threshold systems such as hydrogen-bond acceptor count and topological polar surface area.
- Source: Major threshold systems such as Rule of Five, Veber, Egan, and QED focus primarily on HBA, HBD, and TPSA.

## aliphatic carbocycle count
- Common threshold(s) or range(s): No stable literature threshold found. Common filters focus more on macro-level properties such as total ring count, aromatic ring count, rotatable bonds, and polarity.
- Usually associated with: As a structural component, the number of aliphatic carbocycles may indirectly influence logD/logP and permeability by altering three-dimensionality and hydrophobicity, but there is no generalizable threshold linking aliphatic carbocycle count to CYP3A4 substrate behavior.
- Brief note: If this feature appears important in model interpretation, a common reason is that it correlates with or complements descriptors such as aromatic ring count, Fsp3, or PFI (logD7.4 + aromatic ring count), which describe structural complexity and hydrophobicity more directly.
- Source: Muegge sets windows on total ring count rather than ring subtypes, while SwissADME and QED favor integrated property descriptions.

## aliphatic heterocycle count
- Common threshold(s) or range(s): No stable literature threshold found.
- Usually associated with: Aliphatic heterocycles often introduce heteroatoms, influencing HBA and TPSA, but they may also increase three-dimensionality and Fsp3. Their effect on substrate assignment is therefore usually indirect through these integrated properties.
- Brief note: For ionizable heterocycles such as piperidine or morpholine, interpretation should be done together with pKa and with neutral fraction or logD7.4.
- Source: SwissADME radar windows for saturation and polarity, Rule of Five, Veber, and Egan for HBA/HBD/TPSA thresholds, and Henderson-Hasselbalch for ionization anchors.

## aliphatic ring count
- Common threshold(s) or range(s): No stable literature threshold found. Common thresholds are more often placed on total ring count rather than specifically on aliphatic ring count.
- Usually associated with: Increasing aliphatic ring count may increase saturation and three-dimensionality, helping offset excessive aromaticity; as a proxy, this can reduce PFI and solubility pressure, but there is no direct threshold.
- Brief note: In practice, interpretable indicators such as PFI (logD7.4 + aromatic ring count) or fraction sp3 are used more often to guide the balance between aliphatic and aromatic ring content.
- Source: Muegge upper limits on total rings, SwissADME lower bounds on Fsp3, and medicinal chemistry use of PFI as a composite proxy.

## aromatic carbocycle count
- Common threshold(s) or range(s): No stable literature threshold found. More commonly, empirical windows are defined for total aromatic ring count or for composite indicators that combine aromatic ring count with logD.
- Usually associated with: More aromatic carbocycles usually increase planarity and hydrophobicity, potentially increasing logP/logD and PFI, thereby worsening multiple developability endpoints, including CYP interaction risk. However, this is not a hard substrate versus non-substrate split.
- Brief note: If an operational threshold is needed, it is often better to use PFI (logD7.4 + aromatic ring count) or combination rules involving logP/logD and TPSA.
- Source: PFI discussions in medicinal chemistry literature and QED, which includes aromaticity-related terms in a continuous score.

## aromatic heterocycle count
- Common threshold(s) or range(s): No stable literature threshold found.
- Usually associated with: Aromatic heterocycles are similar to aromatic carbocycles, but often introduce N/O/S atoms, increasing HBA and TPSA while tending to reduce logP. Their net effect depends on substitution pattern and ionization, so no universal threshold exists.
- Brief note: In CYP3A4 substrate tasks, this feature is more likely to function as a structural class signal, with its downstream effects ultimately reflected by continuous descriptors such as logD7.4, TPSA, and HBA/HBD.
- Source: Rule of Five, Veber, and Egan polarity and hydrogen-bond thresholds, Henderson-Hasselbalch ionization anchors, and PFI as a composite aromaticity-related indicator.

## aromatic ring count
- Common threshold(s) or range(s): No stable literature threshold found. A more common strategy is to use aromatic ring count as part of composite metrics such as PFI or SFI rather than as an isolated hard threshold.
- Usually associated with: Increasing aromatic ring count usually co-varies with higher hydrophobicity, lower solubility, and higher risk of nonspecific binding, polypharmacology, or CYP interaction. As a proxy, it also shifts the compound's location in chemical space relevant to substrate versus non-substrate behavior.
- Brief note: If an engineering-style anchor must be given, one can use PFI, defined as PFI = logD7.4 + number of aromatic rings, with PFI < 6 as an empirical target for better developability.
- Source: Medicinal chemistry teaching materials on PFI and Golden Triangle discussions of how logD and MW jointly shape the balance between accessibility and clearance.

## hydrogen-bond acceptor count
- Common threshold(s) or range(s): Rule of Five gives HBA ≤ 10, and Muegge also gives HBA ≤ 10.
- Usually associated with: Increasing HBA count usually raises polarity and TPSA while reducing permeability. As a proxy, this can reduce the probability that a molecule reaches and is metabolized by CYP3A4. However, HBA sites may also contribute to binding interactions with the enzyme, so the relationship is not strictly monotonic.
- Brief note: In interpretation, HBA is often strongly correlated with TPSA. If both are in the feature set, threshold-based explanations are often clearer when framed in terms of TPSA.
- Source: Lipinski Rule of Five, Muegge, and frameworks that discuss polarity jointly with permeability and clearance.

## hydrogen-bond donor count
- Common threshold(s) or range(s): Rule of Five gives HBD ≤ 5, and Muegge also gives HBD ≤ 5.
- Usually associated with: Increasing HBD count usually raises polarity substantially and reduces passive permeability. As a substrate-accessibility proxy, a very high donor count often places compounds in non-substrate-like chemical space, although intramolecular hydrogen bonding can sometimes reduce effective polarity and create exceptions.
- Brief note: HBD substantially overlaps with NH/OH group count. If both are present, it is best to align the counting definitions and avoid redundant interpretation.
- Source: Lipinski Rule of Five, Muegge, and Golden Triangle discussions of exceptions caused by intramolecular hydrogen bonding or ionization.

## heteroatom count
- Common threshold(s) or range(s): The Muegge filter includes heteroatoms > 1 as one of its minimum functionality requirements. Most other rules reflect related effects indirectly through HBA/HBD and TPSA.
- Usually associated with: More heteroatoms generally increase polarity and the capacity for hydrogen bonding or dipolar interactions. As a proxy, very high polarity may reduce permeability, but a moderate heteroatom count may also support substrate interaction and positioning in the CYP active site, so the effect is not monotonic.
- Brief note: Different heteroatoms such as N, O, S, and halogens contribute differently, so for thresholding it is usually better to move to descriptors such as TPSA or logD7.4.
- Source: Muegge, together with the core descriptor sets of Rule of Five, Egan, Veber, and QED.

## rotatable-bond count
- Common threshold(s) or range(s): Veber gives rotatable bonds ≤ 10, and the Muegge filter gives rotatable bonds ≤ 15.
- Usually associated with: More rotatable bonds usually imply greater flexibility and higher conformational entropy cost, and are often associated with poorer oral bioavailability and permeability. As a proxy, this may reduce the probability of reaching effective exposure and undergoing metabolism in CYP3A4 systems.
- Brief note: In the Golden Triangle discussion, molecular weight is treated as a proxy for many descriptors, including rotatable bonds, meaning that MW and RB often co-vary. Therefore, RB is usually interpreted most robustly together with MW and logD.
- Source: Veber and Muegge.

## saturated carbocycle count
- Common threshold(s) or range(s): No stable literature threshold found. Most rules only set an upper bound on total ring count or capture ring-related effects implicitly through integrated scores.
- Usually associated with: Saturated carbocycles generally increase sp3 fraction and three-dimensionality and may reduce aromatic burden as a proxy, but there is no threshold directly linked to CYP3A4 substrate behavior.
- Brief note: If an operational rule is desired to manage saturation trends, fraction of sp3 carbons, using empirical anchors such as ≥0.25 or ≥0.42, is generally more transferable than counting saturated carbocycles directly.
- Source: SwissADME Fsp3 window and empirical literature anchors for Fsp3 ≥ 0.42.

## saturated heterocycle count
- Common threshold(s) or range(s): No stable literature threshold found.
- Usually associated with: Saturated heterocycles can simultaneously increase sp3 fraction and increase polarity or HBA count. Their net effect depends on logD7.4, TPSA, and pKa or neutral fraction, so there is no single universal threshold.
- Brief note: In CYP3A4 substrate tasks, saturated heterocycle count is better treated as a structural class feature supported by continuous descriptors rather than as a threshold variable.
- Source: SwissADME windows for Fsp3, MW, and TPSA; Egan and Veber on TPSA thresholds; Henderson-Hasselbalch on ionization.

## saturated ring count
- Common threshold(s) or range(s): No stable literature threshold found. More common rules set an upper limit on total ring count, such as number of rings ≤ 7 in Muegge, or use integrated scoring systems.
- Usually associated with: A higher proportion of saturated rings usually corresponds to higher sp3 fraction and lower aromatic burden. This is generally favorable in developability proxy terms, but there is no direct hard boundary distinguishing substrates from non-substrates.
- Brief note: Management of the balance between saturated and aromatic rings is usually better handled through fraction sp3 carbons and PFI (logD7.4 + aromatic ring count).
- Source: Muegge total ring limits, SwissADME lower Fsp3 bounds, and empirical PFI rules.

## ring count
- Common threshold(s) or range(s): The Muegge filter gives number of rings ≤ 7.
- Usually associated with: Increasing total ring count usually raises rigidity and, depending on ring type, hydrophobicity or aromaticity, and may be associated with poorer solubility or permeability. For substrate assignment it is mainly a chemical-space positioning signal.
- Brief note: If ring count is high but oral exposure is still required, this often pushes the design space toward beyond-Rule-of-5 compounds, macrocycles, or molecular-chameleon strategies. In such spaces, single thresholds become less reliable and should be interpreted together with logD7.4, rotatable bonds, HBD/HBA, and related descriptors.
- Source: Muegge and the Golden Triangle multi-parameter balance concept.

## topological polar surface area
- Common threshold(s) or range(s): Veber gives TPSA ≤ 140 Å²; Egan gives TPSA ≤ 131.6 Å²; SwissADME radar gives TPSA 20-130 Å²; and Pfizer 3/75 uses TPSA < 75 Å² together with logP > 3 in a risk context.
- Usually associated with: Excessively high TPSA usually reduces passive permeability and absorption. As a proxy for whether a compound can sufficiently contact CYP3A4 and present as a metabolizable substrate, values outside these empirical windows tend to bias toward non-substrate behavior or greater dependence on transport or special strategies.
- Brief note: In many filters, TPSA separates oral accessibility better than MW alone. However, for CYP3A4 substrate tasks it should still be interpreted jointly with logD7.4 and pKa or neutral fraction.
- Source: Veber, Egan, SwissADME radar, Pfizer 3/75, and related reviews.

## QED drug-likeness
- Common threshold(s) or range(s): QED ranges from 0 to 1. In datasets concerning chemical beauty and drug-likeness, the authors reported mean QED ≈ 0.67 for the "attractive" set with standard deviation ≈ 0.16, about 0.49 for the "unattractive" set, and about 0.34 for the "too complex" set. A top-10% ChEMBL anchor of QED ≈ 0.796 has also been used as a reference line for high QED.
- Usually associated with: Higher QED, indicating closer agreement with common oral-drug property distributions, usually means closer overall balance relative to empirical windows such as Rule of Five, Veber, and Egan. As a proxy, such compounds are more likely to fall into chemical space that is permeable, exposed, and assessable in metabolic systems, and therefore are more often seen among metabolizable compounds in CYP3A4 substrate tasks, though not inevitably.
- Brief note: QED is a composite score that is most useful for ranking and relative comparison. For interpretable reasoning about why a compound does or does not resemble a substrate, it is better to unpack its component descriptors, such as MW, logP, PSA, HBD/HBA, aromatic rings, and rotatable bonds, and compare each against its corresponding threshold.
- Source: The original QED paper by Bickerton and colleagues, including its reported mean and percentile anchors and component descriptors.

## Functional-group notes
- Group name: Strong acidic groups, such as sulfonic acids, phosphonic acids, and strongly acidic sulfate-type motifs
  - Usually associated with: At pH ≈ 7.4 these are almost fully deprotonated, giving very low neutral fraction, often high TPSA, and low logD, which tends to reduce passive permeability. As a substrate-accessibility proxy, they bias toward non-substrate behavior.
  - Brief note: This is an approximation at the level of accessibility and permeability. Whether the compound is a CYP3A4 substrate still depends on the experimental system and on whether transport or special conformational shielding of polarity is involved.
  - Source: Henderson-Hasselbalch ionization anchors, polarity and permeability threshold systems such as Veber and Egan, and Golden Triangle discussions.

- Group name: Zwitterionic scaffolds
  - Usually associated with: Literature ranking of permeability often places zwitterions among the least permeable classes, typically worse than neutral, acidic, or basic compounds, so in the proxy chain for contacting CYP3A4 they tend to bias toward non-substrate behavior.
  - Brief note: Exceptions still exist, especially when intramolecular hydrogen bonding or specific conformations reduce effective polarity and improve permeability and exposure.
  - Source: Golden Triangle discussion of ionization class and permeability, including explanations for exceptions and outliers.

- Group name: Polycarboxylates or polyamines, reflecting a tendency toward multiple ionizable sites and multiple charges
  - Usually associated with: A tendency toward multiple charges usually lowers passive permeability and decreases logD7.4. As a proxy, this biases compounds toward non-substrate behavior or implies a need for stronger hydrophobicity or molecular-chameleon strategies as compensation.
  - Brief note: It is not advisable to make a hard decision based only on the number of ionizable sites. At minimum, interpretation should combine pKa -> neutral fraction -> logD7.4 and compare against TPSA and rotatable-bond windows.
  - Source: Henderson-Hasselbalch, Golden Triangle, and Veber and Egan polarity thresholds.

- Group name: Halogen-enriched or halogen-based "soft spot blocking" patterns
  - Usually associated with: Halogens may improve metabolic stability and reduce clearance by blocking metabolic soft spots, thereby affecting observed metabolic behavior in CYP systems. At the same time, high-atomic-weight elements can cause MW to overstate true size, which is why heavy-atom count or surface area may be better alternative size proxies.
  - Brief note: This is closer to a rule about metabolic stability and clearance than a direct rule about substrate status. However, when substrate labels come from in vitro metabolism assays, it can indeed change whether significant metabolism is observed.
  - Source: Golden Triangle discussion of halogen-related outliers and soft-spot blocking, together with reviews of relationships among CYP3A4 kinetics, hydrophobicity, and structure.

Input 2. Single-molecule analysis notes
First, estimated logD is value -1.3032. The global EBM contribution here is -0.1099, which pushes toward option (A): is not a substrate to the enzyme CYP3A4. Next, heavy-atom molecular weight is value 134.117. The global EBM contribution here is -0.0919, which pushes toward option (A): is not a substrate to the enzyme CYP3A4. Then, molecular weight is value 149.237. The global EBM contribution here is -0.0912, which pushes toward option (A): is not a substrate to the enzyme CYP3A4. After that, exact molecular weight is value 149.1204. The global EBM contribution here is -0.0847, which pushes toward option (A): is not a substrate to the enzyme CYP3A4. Finally, Labute surface area is value 68.441. The global EBM contribution here is -0.0781, which pushes toward option (A): is not a substrate to the enzyme CYP3A4. Step 6, neutral fraction is value 0.0007. The global EBM contribution here is -0.078, which pushes toward option (A): is not a substrate to the enzyme CYP3A4. Step 7, strongest basic pKa is value 10.5399. The global EBM contribution here is -0.061, which pushes toward option (A): is not a substrate to the enzyme CYP3A4. Step 8, minimum absolute partial charge is value 0.0076. The global EBM contribution here is -0.0468, which pushes toward option (A): is not a substrate to the enzyme CYP3A4. Step 9, maximum partial charge is value 0.0076. The global EBM contribution here is -0.0405, which pushes toward option (A): is not a substrate to the enzyme CYP3A4. Step 10, heavy-atom count is value 11. The global EBM contribution here is -0.0365, which pushes toward option (A): is not a substrate to the enzyme CYP3A4. Taken together, these global descriptor-level signals make the model predict option (A): is not a substrate to the enzyme CYP3A4 with score 0.7226.

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
