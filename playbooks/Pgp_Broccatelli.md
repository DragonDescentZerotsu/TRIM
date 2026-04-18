# Practical Handbook of Molecular Properties for Pgp_Broccatelli

The following is organized according to the TDC semantics for Pgp_Broccatelli: A = not a P-gp inhibitor, B = a P-gp inhibitor. Priority is given to the original task literature or the closest neighboring literature on P-gp inhibition. Whenever "proxy" is indicated, it means no stable cutoff was available in direct inhibition literature, so the closest rules from P-gp ligand behavior, efflux evasion, or general developability were used instead.

## neutral fraction
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more commonly seen in amphiphilic molecules that are partially protonatable, rather than fully neutral or permanently cationic molecules)
- Brief note: P-gp modulators/inhibitors are repeatedly described as having protonatable tertiary amines or cationic character at physiological pH; however, permanent positive charge (such as quaternary ammonium) often weakens activity, so there is no transferable numeric threshold for neutral fraction.
- Source: nearest-neighbor SAR/QSAR reviews and binding-site studies on P-gp inhibitors.

## estimated logD
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (higher lipophilicity at physiological pH is usually more favorable); very low logD is more often associated with A
- Brief note: The most stable signal in the neighboring literature is actually "retaining sufficient lipophilicity at physiological pH," but most original thresholds are reported as logP/logKow rather than a unified logD cutoff.
- Source: nearest-neighbor SAR of P-gp modulators; interpretation of logD mainly comes from physiological-pH lipophilicity proxies.

## strongest acidic pKa
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (proxy: stronger acids that are readily deprotonated at pH 7.4 are more often associated with non-inhibition or weaker interaction)
- Brief note: Nearby studies on P-gp efflux evasion repeatedly show that introducing a carboxylic acid often helps evade P-gp; this supports the idea that pronounced acidity and easy acquisition of negative charge are generally unfavorable for a small-molecule inhibitor phenotype, but the literature does not provide a universal acidic pKa cutoff.
- Source: proxy from P-gp efflux-evasion literature and empirical inhibitor rule sets involving acidic groups.

## strongest basic pKa
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (if at least one site can be protonated near physiological pH)
- Brief note: The more common rule in this task is the presence of a protonatable tertiary amine or cationic center, rather than any fixed strongest basic pKa value; in other words, the literature gives qualitative rules rather than a hard cutoff.
- Source: nearest-neighbor structural rules for P-gp modulators; the importance of basic centers comes from multiple SAR/QSAR summaries.

## number of acidic sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more common when there are 0 acidic sites); A (more common when clear acidic sites are present, proxy)
- Brief note: The literature supports the presence or absence of a carboxylic acid/anionic site more strongly than any universal counting rule for the number of acidic sites; therefore, "no acidic sites" can only be used as a soft anchor.
- Source: proxy from P-gp efflux-evasion studies plus decision-tree rules that disfavor carboxylic acids.

## number of basic sites
- Common threshold(s) or range(s): at least 1 protonatable basic center is the most common anchor, but there is no stable "optimal count"
- Usually associated with: B
- Brief note: Classic P-gp inhibitor series often contain one tertiary amine or dialkyl amine; some series favor two amines, with one protonated at physiological pH, so "at least one" is more stable than specifying an exact count.
- Source: nearest-neighbor SAR/QSAR reviews on P-gp inhibitors.

## number of ionizable sites
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more like the case of one dominant basic site without permanent charge)
- Brief note: The main discriminating signal in the literature comes from ionization type—protonatable tertiary amines, permanent quaternary ammonium, carboxylates—rather than the total number of ionizable sites.
- Source: nearest-neighbor SAR rules for P-gp ligands/inhibitors.

## exact molecular weight
- Common threshold(s) or range(s): the most common practical nearest-neighbor anchor is about 250–500 Da; older binding studies reported "optimal binding" mostly in the range 391–490 Da; MW < 250 usually does not resemble a typical P-gp ligand
- Usually associated with: B (medium to somewhat high MW); A (molecules that are too small)
- Brief note: The 391–490 Da range comes from older binding-study proxies and should not be treated as a hard inhibitor cutoff; however, "larger and more hydrophobic molecules" is a relatively stable direction in the P-gp inhibition literature.
- Source: nearest-neighbor QSAR for P-gp inhibitors plus older proxy studies on P-gp binding.

## fraction of sp3 carbons
- Common threshold(s) or range(s): no stable literature threshold found; a common general developability proxy is Fraction Csp3 ≥ 0.25
- Usually associated with: no stable A/B direction
- Brief note: This threshold comes from general drug-likeness, not P-gp inhibition specifically; classic P-gp inhibitors are often aromatic and relatively planar, so this is better used as a developability reference than as a classification rule.
- Source: proxy from the SwissADME bioavailability radar plus P-gp inhibitor reviews.

## heavy-atom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (only as an indirect signal of a larger molecule)
- Brief note: P-gp inhibition literature discusses MW, overall size, lipophilicity, and aromatic/basic pharmacophores, and rarely provides a transferable threshold for heavy-atom count.
- Source: nearest-neighbor P-gp inhibitor reviews; general drug-likeness atom-count rules are only weak proxies here.

## heavy-atom molecular weight
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: same direction as molecular weight, but with weaker evidence
- Brief note: The literature reports whole-molecule MW rather than heavy-atom molecular weight; if interpretation is required, one can usually only borrow the approximate MW logic of 250–500 Da.
- Source: nearest-neighbor SAR/QSAR for P-gp inhibitors; this descriptor itself lacks an independent threshold.

## Labute surface area
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable A/B direction
- Brief note: Some QSAR summaries suggest that surface area is negatively correlated with P-gp ATPase activity, but this is a dataset-specific conclusion and has not produced a transferable cutoff for Labute surface area.
- Source: nearest-neighbor summaries of P-gp ATPase/QSAR studies.

## maximum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: either A or B; what matters more is whether a protonatable cationic center is present
- Brief note: P-gp literature almost never uses extrema of partial charge as a universal threshold; qualitative descriptions such as "cationic center + HBA/HBD + aromatic/hydrophobic center" are much more common.
- Source: nearest-neighbor pharmacophore/QSAR literature on P-gp inhibitors.

## maximum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (if it reflects a protonatable tertiary amine); otherwise no stable direction
- Brief note: What is repeatedly used in the literature is the presence of a tertiary amine or positive center, not any particular numerical value of maximum partial charge.
- Source: nearest-neighbor SAR/QSAR reviews on P-gp inhibitors.

## minimum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable A/B direction
- Brief note: For negative character, P-gp literature more often uses whether a carboxylate or acidic group is present, rather than algorithm-dependent extrema such as minimum absolute partial charge.
- Source: nearest-neighbor literature on P-gp inhibitors and efflux evasion.

## minimum partial charge
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: A (if a more negative value comes from a deprotonatable acidic group, proxy); otherwise no stable direction
- Brief note: The more generalizable rule remains that carboxylic acids and anions are often unfavorable for the phenotype of small-molecule P-gp inhibitors, rather than any specific minimum partial charge cutoff.
- Source: proxy from P-gp efflux-evasion literature and empirical observations on acidic groups.

## estimated logP
- Common threshold(s) or range(s): the most reproducible anchor is logP ≥ 2.92; older binding literature gives an "optimal binding" range of logKow 3.6–4.5; another broader, more model-derived alternative anchor is logP > 1.56
- Usually associated with: B
- Brief note: This is one of the most reliable descriptors for the task; Broccatelli and subsequent multiclass studies both regard lipophilicity as a core separating variable between inhibitors and non-inhibitors.
- Source: nearest-neighbor SAR/QSAR for P-gp inhibitors plus early proxy studies on binding.

## molecular weight
- Common threshold(s) or range(s): about 250–500 Da is the most practical nearest-neighbor working range; 391–490 Da can serve as an older proxy for "optimal binding"; MW < 250 usually does not resemble a typical P-gp ligand
- Usually associated with: B (medium to somewhat high MW); A (molecules that are too small)
- Brief note: MW helps distinguish inhibitors from non-inhibitors, but it is not sufficient on its own; it is usually interpreted together with logP, aromaticity, and protonatable centers.
- Source: nearest-neighbor QSAR for P-gp inhibitors plus older proxy studies on binding.

## NH/OH group count
- Common threshold(s) or range(s): the most common inhibitor pharmacophore retains only 0–1 hydrogen-bond donor
- Usually associated with: B (more common at 0–1); many NH/OH groups are more likely to bias toward A or weaker interaction
- Brief note: The HBD direction is not completely consistent across the literature; a safer practical rule is not to accumulate too many NH/OH groups, especially since donor-rich fragments such as primary/secondary amides often weaken interaction.
- Source: nearest-neighbor pharmacophore/QSAR literature plus nearby studies on taxane–P-gp interactions.

## nitrogen/oxygen atom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (more often when the count is moderate and manifests as one basic nitrogen plus limited polar burden)
- Brief note: The literature does not use raw N/O atom count directly; it is usually decomposed into HBA, HBD, protonatable nitrogen, TPSA, and lipophilicity for interpretation.
- Source: nearest-neighbor pharmacophore/QSAR literature on P-gp inhibitors.

## aliphatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable A/B direction
- Brief note: P-gp inhibition literature emphasizes aromatic hydrophobic regions and nitrogen-containing rings, rather than the sheer number of aliphatic carbocycles.
- Source: nearest-neighbor SAR reviews on P-gp inhibitors.

## aliphatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found; however, one saturated nitrogen-containing heterocycle is a high-frequency motif
- Usually associated with: B
- Brief note: Many classic inhibitors place a protonatable positive center on rings such as piperazine or piperidine; this is a frequent structural clue, but not a universal counting rule.
- Source: nearest-neighbor SAR reviews on P-gp inhibitors.

## aliphatic ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (when rings are present, especially together with aromatic and basic centers); however, the direction is unstable
- Brief note: Some older series suggested that at least one six-membered ring is common, but this is not a transferable total cutoff for aliphatic ring count.
- Source: nearest-neighbor SAR and older proxy studies.

## aromatic carbocycle count
- Common threshold(s) or range(s): no stable universal threshold; however, 1–3 aromatic hydrophobic domains are the most common, and older SAR often favored 2–3 phenyl/aryl rings
- Usually associated with: B
- Brief note: The effect of aromatic ring count is strongly modulated by spatial arrangement; how those aromatic domains are separated or offset matters more than the raw number of rings.
- Source: nearest-neighbor pharmacophore and SAR reviews.

## aromatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (weak association)
- Brief note: Aromatic heterocycles are common in many modern P-gp inhibitor scaffolds, but the literature does not provide a universal cutoff for the number of aromatic heterocycles; their role is better captured as part of the combination of aromatic hydrophobic domains with HBA/basic centers.
- Source: nearest-neighbor reviews on heterocycles in P-gp inhibitors and older SAR.

## aromatic ring count
- Common threshold(s) or range(s): the most common inhibitor pharmacophore includes 1–2 aromatic/hydrophobic centers; however, older SAR repeatedly reported that 2–3 phenyl/aryl rings are more characteristic of strong modulators/inhibitors
- Usually associated with: B
- Brief note: This is a property with some tension but still practical value: a few high-quality pharmacophores suggest 1–2 rings, whereas series SAR often treats 2–3 rings as a marker of strong activity; in practice, 1–3 is a reasonable working range.
- Source: nearest-neighbor pharmacophore/SAR literature on P-gp inhibitors.

## hydrogen-bond acceptor count
- Common threshold(s) or range(s): inhibitor pharmacophores most often give 1–3 HBA
- Usually associated with: B (limited HBA); too many HBA are more likely to behave in a substrate-like manner
- Brief note: This is another property with directional tension: pharmacophore models often retain 1–3 HBA, but reviews also note that HBA are particularly important for substrate recognition and ATPase activation, so more HBA do not necessarily make a molecule more inhibitor-like.
- Source: nearest-neighbor pharmacophore/QSAR literature on P-gp inhibitors and reviews on hydrogen-bonding.

## hydrogen-bond donor count
- Common threshold(s) or range(s): inhibitor pharmacophores most commonly have 0–1 HBD
- Usually associated with: B (limited HBD); many or strong HBD are often unfavorable
- Brief note: The literature is not fully consistent, but from a practical design perspective, reducing donor burden and avoiding multiple NH/OH groups is a safer working rule; primary/secondary amides often weaken P-gp interaction.
- Source: nearest-neighbor pharmacophore/QSAR literature plus nearby P-gp interaction studies.

## heteroatom count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (when the heteroatom burden is moderate and composed of one basic center plus a small number of HBA/HBD)
- Brief note: Rather than total heteroatom count, P-gp literature cares more about whether those heteroatoms are HBA, HBD, or protonatable basic centers.
- Source: nearest-neighbor pharmacophore/QSAR literature on P-gp inhibitors.

## rotatable-bond count
- Common threshold(s) or range(s): no stable literature threshold found; if only general developability proxies are used, the common Veber rule is rotatable bonds ≤ 10
- Usually associated with: no stable A/B direction
- Brief note: For P-gp inhibitors, the more frequently cited rule is a sufficiently long 18-atom chain/spacer rather than a rotatable-bond cutoff; therefore, ≤ 10 can only serve as a non-task-specific developability proxy.
- Source: nearest-neighbor structural rules for P-gp modulators plus general oral drug-likeness proxies.

## saturated carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: no stable A/B direction
- Brief note: Saturated carbocycles themselves are not the focus of the literature; more important is whether a saturated nitrogen-containing heterocycle is present and protonatable.
- Source: nearest-neighbor SAR reviews on P-gp inhibitors.

## saturated heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found; however, one saturated nitrogen-containing heterocycle is a common high-frequency clue
- Usually associated with: B
- Brief note: Many classic P-gp inhibitors use saturated nitrogen-containing heterocycles such as piperazine or piperidine to carry a positive center; however, this should still be viewed as a motif rather than a strict counting rule.
- Source: nearest-neighbor SAR literature on P-gp inhibitors.

## saturated ring count
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with: B (when appearing together with aromatic hydrophobic domains and a basic center); unstable if considered alone
- Brief note: The literature supports the idea that ring-rich or cyclic character is more informative than the exact number of saturated rings.
- Source: nearest-neighbor SAR and classification summaries on P-gp inhibitors.

## ring count
- Common threshold(s) or range(s): no stable universal threshold; at least one ring system is usually common background, and many strong modulator series tend toward 2–3 aryl rings
- Usually associated with: B
- Brief note: What really matters is the combination of ring richness, aromatic hydrophobic domains, and a protonatable center, rather than a standalone total ring-count threshold.
- Source: nearest-neighbor SAR/classification reviews on P-gp inhibitors.

## topological polar surface area
- Common threshold(s) or range(s): there is no stable TPSA cutoff in direct P-gp inhibition literature; if general permeability proxies are used, a common upper bound is TPSA ≤ 140 Å², and the more "comfortable" drug-like range in SwissADME is 20–130 Å²
- Usually associated with: no stable A/B direction; better used as a weak proxy to exclude very high-polarity molecules
- Brief note: For this task, TPSA is at most an auxiliary interpretive feature; direct P-gp inhibition studies more often use HBA/HBD, lipophilicity, and protonatable centers rather than TPSA itself. Nearby studies on P-gp efflux evasion also suggest that lowering PSA can reduce efflux.
- Source: proxy from Veber/SwissADME and nearby studies on P-gp efflux.

## QED drug-likeness
- Common threshold(s) or range(s): proxy: QED ≥ 0.67 is often considered attractive/drug-like, while QED ≤ 0.49 is often considered less desirable
- Usually associated with: no stable A/B direction
- Brief note: For this task, QED behaves more like a general drug-likeness/developability filter than a P-gp-inhibition-specific property; it is suitable for excluding extremely non-drug-like molecules, but not for separating A from B on its own.
- Source: proxy from the original QED framework and its commonly used interpretive thresholds.

## Functional-group notes

- Group name: protonable tertiary amine / dialkyl tertiary amine
- Usually associated with: B
- Brief note: This is one of the most stable P-gp inhibitor motifs; many reviews treat "at least one tertiary amine that can form a cation at physiological pH" as a shared feature of potent modulators.
- Source: nearest-neighbor SAR/QSAR reviews on P-gp inhibitors.

- Group name: quaternary ammonium / permanent cation
- Usually associated with: A
- Brief note: Permanent positive charge often weakens activity; classic SAR explicitly states that quaternary amines often abolish or markedly worsen modulating activity.
- Source: nearest-neighbor SAR on P-gp inhibitors.

- Group name: nitrogen-containing saturated heterocycles such as piperazine or piperidine
- Usually associated with: B
- Brief note: The most common role of these rings is not simply to increase ring count, but to present a protonatable positive center in an appropriate geometry; multiple SAR series regard them as favorable motifs.
- Source: nearest-neighbor SAR/QSAR on P-gp inhibitors.

- Group name: two or three aromatic/hydrophobic domains
- Usually associated with: B
- Brief note: Many strong inhibitor/modulator series depend on two or three aromatic hydrophobic domains; however, the exact effect depends on spatial offset and spacing, rather than a simple "one more ring is always better" rule.
- Source: nearest-neighbor pharmacophore/SAR literature on P-gp inhibitors.

- Group name: carboxylic acid
- Usually associated with: A (proxy)
- Brief note: In the closest neighboring studies on P-gp efflux evasion, carboxylic acid repeatedly correlates with P-gp evasion and reduced interaction, so it is usually an unfavorable signal for the phenotype of a small-molecule inhibitor.
- Source: proxy from P-gp efflux-evasion literature.

- Group name: primary/secondary amide
- Usually associated with: A (weak proxy)
- Brief note: Nearby taxane–P-gp studies suggest that primary/secondary amides often weaken interaction with P-gp, while conversion to tertiary amides can strengthen interaction. This pattern is better viewed as a clue for weaker interaction or evasion, rather than a universal inhibitor rule.
- Source: proxy from nearby studies on P-gp interaction and efflux.