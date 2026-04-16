# HIA_Hou molecular-property playbook

The original Hou-style HIA classification literature commonly splits compounds into low vs high intestinal absorption at fraction absorbed (FA) of 30%; this playbook treats option A as the low-absorption side and option B as the absorbed side. The most transferable numeric anchors are TPSA, hydrogen-bonding burden, molecular weight, lipophilicity, flexibility, and persistent charge; many other descriptors are model-useful but do not have stable standalone medicinal-chemistry cutoffs. citeturn46search0turn24search7turn26view0

## neutral fraction
- Common threshold(s) or range(s): no stable literature threshold found. citeturn40search0turn40search1turn40search20
- Usually associated with: higher neutral fraction at the configured intestinal pH usually leans toward option B; very low neutral fraction usually leans toward option A in passive-absorption settings. citeturn40search14turn40search20
- Brief note: HIA literature usually handles this through pKa, pH, and logD rather than a standalone neutral-fraction cutoff; compounds with pKa values in the 6–8 region are especially pH-sensitive across the small intestine. citeturn40search1turn40search3
- Source: acid/base and oral-absorption reviews. citeturn40search0turn40search1turn40search20

## estimated logD
- Common threshold(s) or range(s): proxy only; mid-range logD is preferred, with common medicinal-chemistry anchors around logD ≈ -2 to 5, and many teams using logD in place of logP in Ro5-style filtering. citeturn38search0turn8search2turn41search7
- Usually associated with: mid-range values lean toward option B; very low values can signal poor membrane partitioning and very high values can signal solubility/formulation liabilities that hurt absorption, both leaning toward option A. citeturn8search2turn41search7
- Brief note: this is a proxy from permeability/clearance/oral-absorption design, not a stable Hou-specific cutoff. citeturn38search0turn8search2
- Source: logD-focused oral drug-design and permeability literature. citeturn38search0turn8search2turn41search7

## strongest acidic pKa
- Common threshold(s) or range(s): no stable literature threshold found. citeturn40search0turn40search1turn16search3
- Usually associated with: acids that stay strongly ionized at intestinal pH usually lean toward option A unless active transport or other factors rescue absorption. citeturn40search14turn40search20
- Brief note: the literature treats acidic pKa mainly as an input to neutral fraction, logD, and pH-dependent solubility rather than as a universal HIA cutoff. citeturn40search0turn16search3
- Source: acid/base-property reviews and GI pH absorption reviews. citeturn40search0turn40search20

## strongest basic pKa
- Common threshold(s) or range(s): no stable literature threshold found. citeturn40search0turn40search1turn16search3
- Usually associated with: very strongly basic sites that remain protonated through the intestine usually lean toward option A; moderated basicity more often supports option B. citeturn40search14turn32view1turn33view0
- Brief note: persistent cationic character is more actionable than any single basic-pKa cutoff; task-specific HIA work repeatedly flags positively charged nitrogen as unfavorable. citeturn32view1turn33view0turn30search0
- Source: acid/base reviews and later HIA classification analyses. citeturn40search1turn32view1turn33view0

## number of acidic sites
- Common threshold(s) or range(s): no stable literature threshold found. citeturn16search3turn40search0
- Usually associated with: more acidic sites usually lean toward option A because they increase charge burden and depress neutral fraction. citeturn40search14turn45search1
- Brief note: neighboring absorption literature usually interprets this descriptor indirectly through ionization state, TPSA, and logD rather than site count alone. citeturn40search0turn16search3
- Source: acid/base-property reviews and charged-motif absorption studies. citeturn16search3turn45search1

## number of basic sites
- Common threshold(s) or range(s): no stable literature threshold found. citeturn26view0turn32view1
- Usually associated with: more basic sites usually lean toward option A when they create persistent cationic character; a single attenuated basic center can still fit option B. citeturn32view1turn33view0turn25search15
- Brief note: task-specific HIA models identify basic atoms as important, but the clearest qualitative warning is the presence of positively charged nitrogen. citeturn25search15turn32view1turn33view0
- Source: task-specific HIA classification literature. citeturn26view0turn32view1turn33view0

## number of ionizable sites
- Common threshold(s) or range(s): no stable literature threshold found. citeturn40search0turn16search3
- Usually associated with: more ionizable sites usually lean toward option A in passive-absorption settings because they reduce neutral fraction and increase polarity. citeturn40search14turn40search20
- Brief note: interpret jointly with neutral fraction, pKa, charge state, and logD; raw site count alone is a weak rule. citeturn40search0turn40search1
- Source: oral absorption and acid/base literature. citeturn40search0turn40search20

## exact molecular weight
- Common threshold(s) or range(s): broad oral-absorption proxy ≤500 Da; stricter favorable-ADMET proxy <400 Da. citeturn25search2turn39search0
- Usually associated with: lower values lean toward option B; higher values lean toward option A. citeturn25search2turn39search0
- Brief note: exact MW and conventional MW are used almost interchangeably for this purpose in medicinal-chemistry heuristics. citeturn25search2turn39search0
- Source: Ro5-style and 4/400 oral-ADMET guidance. citeturn25search2turn39search0

## fraction of sp3 carbons
- Common threshold(s) or range(s): no stable HIA threshold found; a general oral-drug-likeness saturation filter often uses Fraction Csp3 ≥0.25. citeturn42search2turn42search16
- Usually associated with: higher values can support option B indirectly through better solubility/developability, but it is not a reliable standalone HIA discriminator. citeturn42search2turn42search16
- Brief note: one permeability study found no statistically significant association between flatness expressed as Fraction Csp3 and permeability. citeturn42search16
- Source: general oral-drug-likeness and permeability studies. citeturn42search2turn42search16

## heavy-atom count
- Common threshold(s) or range(s): no stable literature threshold found. citeturn35search4turn35search9
- Usually associated with: not reliable as a standalone discriminator; larger values mainly matter insofar as they track higher MW and complexity, which can lean toward option A. citeturn25search2turn39search0
- Brief note: the closest classic proxy is a total-atom guideline of 20–70 from general drug-likeness work, but that is not a heavy-atom HIA cutoff. citeturn35search4turn35search9
- Source: general drug-likeness filters and oral-ADMET rules. citeturn35search4turn25search2

## heavy-atom molecular weight
- Common threshold(s) or range(s): no stable literature threshold found. citeturn25search2turn39search0
- Usually associated with: not reliable as a standalone discriminator; higher values usually track higher total MW and so lean toward option A. citeturn25search2turn39search0
- Brief note: medicinal-chemistry practice uses total MW thresholds, not separate heavy-atom-MW thresholds, for HIA screening. citeturn25search2turn39search0
- Source: oral-ADMET rule literature. citeturn25search2turn39search0

## Labute surface area
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view3turn32view1
- Usually associated with: not reliable as a standalone discriminator; polarity-encoded surface measures are usually more informative than total surface area for option A/B. citeturn23view3turn32view1
- Brief note: HIA models use geometric and charge-weighted surface descriptors, but practical medicinal-chemistry cutoffs are standardized for TPSA rather than total surface area. citeturn23view3turn32view1turn24search7
- Source: early HIA QSPR work and later HIA classification model interpretation. citeturn23view3turn32view1

## maximum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found. citeturn32view1turn33view0
- Usually associated with: larger charge extremes usually lean toward option A, but not with a transferable raw cutoff. citeturn32view1turn33view0
- Brief note: Hou-adjacent CART models split on charge-surface descriptors rather than raw max-absolute-charge values. citeturn32view1turn33view0
- Source: task-specific HIA model-interpretation work. citeturn32view1turn33view0

## maximum partial charge
- Common threshold(s) or range(s): no stable literature threshold found. citeturn32view1turn33view0
- Usually associated with: stronger localized positive charge usually leans toward option A when it reflects persistent cationic character. citeturn32view1turn33view0
- Brief note: the practical HIA warning is usually “positively charged nitrogen present,” not a transferable maximum-partial-charge number. citeturn32view1turn33view0turn30search0
- Source: task-specific HIA classification studies. citeturn32view1turn33view0

## minimum absolute partial charge
- Common threshold(s) or range(s): no stable literature threshold found. citeturn32view1turn33view0
- Usually associated with: not reliable as a standalone discriminator for option A/B. citeturn32view1turn33view0
- Brief note: HIA literature emphasizes overall charge separation and surface polarity, not this raw descriptor by itself. citeturn32view1turn33view0
- Source: task-specific HIA model-interpretation work. citeturn32view1turn33view0

## minimum partial charge
- Common threshold(s) or range(s): no stable literature threshold found. citeturn32view1turn33view0
- Usually associated with: more extreme negative charge usually leans toward option A when it increases hydrogen-bonding and ionization burden. citeturn32view1turn33view0
- Brief note: there is no stable standalone cutoff; interpret through ionization state, TPSA, and hydrogen-bond capacity instead. citeturn24search7turn37search3turn32view1
- Source: task-specific charge-descriptor work plus standard oral-absorption rules. citeturn32view1turn33view0turn24search7

## estimated logP
- Common threshold(s) or range(s): broad oral-absorption screen ≤5; many medicinal-chemistry sources prefer roughly 1–3 for balancing permeability and solubility; a stricter favorable-ADMET proxy is <4. citeturn25search2turn36search13turn39search0
- Usually associated with: mid-range values lean toward option B; very low or very high values lean toward option A. citeturn36search13turn39search0
- Brief note: if the molecule is ionizable, logD is usually more relevant than logP for this task. citeturn38search0turn41search7
- Source: oral-absorption and lipophilicity design literature. citeturn25search2turn36search13turn39search0

## molecular weight
- Common threshold(s) or range(s): broad oral-absorption proxy ≤500 Da; stricter favorable-ADMET proxy <400 Da. citeturn25search2turn39search0
- Usually associated with: lower values lean toward option B; higher values lean toward option A. citeturn25search2turn39search0
- Brief note: this is one of the most durable neighboring-task heuristics for HIA. citeturn25search2turn39search0
- Source: Ro5-style and 4/400 oral-ADMET guidance. citeturn25search2turn39search0

## NH/OH group count
- Common threshold(s) or range(s): proxy ≤5 NH/OH groups. citeturn38search8turn25search2
- Usually associated with: lower counts lean toward option B; higher counts lean toward option A. citeturn38search8turn37search3
- Brief note: this is the practical medicinal-chemistry proxy for hydrogen-bond donor burden. citeturn38search8turn37search3
- Source: standard oral-drug property rules. citeturn38search8turn25search2

## nitrogen/oxygen atom count
- Common threshold(s) or range(s): proxy N + O ≤10. citeturn38search8turn25search15
- Usually associated with: lower counts lean toward option B; higher counts lean toward option A. citeturn38search8turn25search15
- Brief note: this is a rough proxy because not every nitrogen or oxygen is an acceptor, but it tracks the same hydrogen-bonding/polarity burden used in oral-absorption rules. citeturn38search8turn37search3
- Source: standard property rules and HIA classification interpretation. citeturn38search8turn25search15

## aliphatic carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found. citeturn44search6
- Usually associated with: not reliable as a standalone discriminator; this ring class is generally less detrimental than aromatic rings. citeturn44search6
- Brief note: neighboring developability literature discusses ring type qualitatively, not as a stable HIA cutoff. citeturn44search6
- Source: ring-type developability and bioavailability literature. citeturn44search6

## aliphatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found. citeturn44search6
- Usually associated with: often more compatible with option B than aromatic ring accumulation, but not by a transferable cutoff. citeturn44search6
- Brief note: heteroaliphatic rings are discussed as comparatively benign or beneficial in developability literature, not thresholded for HIA. citeturn44search6
- Source: ring-type developability and bioavailability literature. citeturn44search6

## aliphatic ring count
- Common threshold(s) or range(s): no stable literature threshold found. citeturn44search6
- Usually associated with: not reliable as a standalone discriminator; weaker than aromatic ring burden. citeturn44search6
- Brief note: use aromatic ring count, TPSA, and flexibility rules first. citeturn44search6turn37search3
- Source: ring-type and oral-bioavailability proxy literature. citeturn44search6turn37search3

## aromatic carbocycle count
- Common threshold(s) or range(s): no stable standalone cutoff; the closest proxy is keeping total aromatic rings at ≤3. citeturn44search1turn44search6
- Usually associated with: higher values usually lean toward option A. citeturn44search6
- Brief note: carboaromatic rings are the most detrimental ring class in developability analyses. citeturn44search6
- Source: aromatic-ring-count developability and bioavailability literature. citeturn44search1turn44search6

## aromatic heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found. citeturn44search6
- Usually associated with: higher counts can still hurt developability and absorption risk, but usually less severely than carboaromatics. citeturn44search6
- Brief note: no standalone medicinal-chemistry HIA cutoff is consistently used. citeturn44search6
- Source: ring-type developability and bioavailability literature. citeturn44search6

## aromatic ring count
- Common threshold(s) or range(s): proxy keep total aromatic rings ≤3; >3 correlates with poorer compound developability and worse human bioavailability parameters. citeturn44search1turn44search6
- Usually associated with: ≤3 leans toward option B; >3 raises option A risk. citeturn44search1turn44search3
- Brief note: this is a proxy from oral developability/bioavailability rather than a Hou-specific HIA cutoff, but it is practical. citeturn44search1turn44search3
- Source: aromatic-ring-count and oral-drug analyses. citeturn44search1turn44search3turn44search6

## hydrogen-bond acceptor count
- Common threshold(s) or range(s): ≤10 acceptors; combined donor + acceptor burden ≤12 is a common oral-bioavailability proxy. citeturn25search2turn37search3
- Usually associated with: lower counts lean toward option B; higher counts lean toward option A. citeturn25search15turn37search3
- Brief note: donor/acceptor burden is repeatedly identified as important in HIA modeling. citeturn25search15turn37search3
- Source: standard oral property rules and HIA classification literature. citeturn25search2turn25search15turn37search3

## hydrogen-bond donor count
- Common threshold(s) or range(s): ≤5 donors; combined donor + acceptor burden ≤12 is a common oral-bioavailability proxy. citeturn25search2turn37search3
- Usually associated with: lower counts lean toward option B; higher counts lean toward option A. citeturn25search15turn37search3
- Brief note: this is one of the strongest simple neighboring-task heuristics for HIA. citeturn37search3turn25search15
- Source: standard oral property rules and HIA classification literature. citeturn25search2turn25search15turn37search3

## heteroatom count
- Common threshold(s) or range(s): no stable literature threshold found. citeturn43search3turn37search12
- Usually associated with: higher counts usually lean toward option A only when they raise H-bonding, ionization, or TPSA. citeturn37search12turn24search7
- Brief note: raw heteroatom count is less useful than HBA, HBD, TPSA, and charge state; broad drug-like rules only give coarse bounds, not HIA cutoffs. citeturn43search3turn37search3
- Source: oral-drug property and drug-likeness literature. citeturn43search3turn37search3turn37search12

## rotatable-bond count
- Common threshold(s) or range(s): ≤10 rotatable bonds. citeturn37search3
- Usually associated with: lower flexibility leans toward option B; >10 leans toward option A risk. citeturn37search3
- Brief note: this is one of the most practical neighboring-task oral-absorption rules. citeturn37search3
- Source: oral-bioavailability rule literature. citeturn37search3

## saturated carbocycle count
- Common threshold(s) or range(s): no stable literature threshold found. citeturn44search6turn42search2
- Usually associated with: not reliable as a standalone discriminator; saturation can help relative to aromaticity, but not by a stable count cutoff. citeturn44search6turn42search2
- Brief note: interpret this via aromatic ring burden and Fraction Csp3 instead. citeturn44search6turn42search2
- Source: ring-type and saturation literature. citeturn44search6turn42search2

## saturated heterocycle count
- Common threshold(s) or range(s): no stable literature threshold found. citeturn44search6
- Usually associated with: often more compatible with option B than aromatic ring accumulation, but not with a transferable cutoff. citeturn44search6
- Brief note: no stable HIA threshold is used in medicinal chemistry for this descriptor alone. citeturn44search6
- Source: ring-type developability and bioavailability literature. citeturn44search6

## saturated ring count
- Common threshold(s) or range(s): no stable literature threshold found. citeturn44search6turn42search2
- Usually associated with: not reliable as a standalone discriminator for option A/B. citeturn44search6
- Brief note: use aromatic ring count, flexibility, and polarity rules first. citeturn44search1turn37search3
- Source: ring-type and oral-absorption proxy literature. citeturn44search6turn37search3

## ring count
- Common threshold(s) or range(s): proxy total rings <7. citeturn43search3turn43search1
- Usually associated with: moderate ring counts lean toward option B; very ring-dense molecules raise option A risk. citeturn43search3
- Brief note: this is a general oral-drug-likeness proxy, not a validated Hou-specific HIA threshold. citeturn43search3
- Source: general drug-likeness filter literature. citeturn43search3turn43search1

## topological polar surface area
- Common threshold(s) or range(s): human HIA anchors: ≤60 Å² often accompanies >90% absorption, while ≥140 Å² robustly flags poor absorption (<10%); common oral-bioavailability proxies are ≤140 Å² and the stricter TPSA/logP filter of ≤131.6 Å² with logP ≤5.88. citeturn24search7turn37search3turn7search16
- Usually associated with: lower TPSA leans toward option B; high TPSA leans toward option A. citeturn24search7turn37search3
- Brief note: this is one of the strongest and most transferable HIA descriptors in the literature. citeturn24search7turn37search3turn7search16
- Source: human HIA datasets and oral-bioavailability filters. citeturn24search7turn37search3turn7search16

## QED drug-likeness
- Common threshold(s) or range(s): no stable task-specific HIA threshold found; in general drug-likeness usage, QED >0.67 is often treated as “attractive/drug-like.” citeturn34search0turn34search20
- Usually associated with: higher QED often leans toward option B only because QED embeds favorable MW, logP, HBA, HBD, TPSA, rotatable-bond, and aromatic-ring ranges. citeturn34search0turn34search20
- Brief note: QED is a composite score, so it is useful as a summary flag but not as a mechanistic HIA threshold. citeturn34search0turn34search14
- Source: QED development and later drug-likeness usage literature. citeturn34search0turn34search20turn34search14

## Functional-group notes

- Group name: quaternary ammonium or other permanently charged ammonium motifs.
- Usually associated with: option A. citeturn30search0turn32view1turn33view0
- Brief note: task-specific HIA work flags positively charged nitrogen as a major poor-absorption signal, and gut-restricted drug-design literature deliberately uses positive charge to suppress intestinal uptake. citeturn30search0turn32view1turn12search5
- Source: task-specific HIA classification analysis and gut-restricted design literature. citeturn30search0turn32view1turn12search5

- Group name: zwitterionic motifs.
- Usually associated with: usually option A unless the charge separation is weak or conformationally shielded. citeturn13search0turn13search15
- Brief note: recent reviews note that oral zwitterionic drugs with large charge separation tend to have only low-to-moderate permeability. citeturn13search0turn13search15
- Source: zwitterion-focused oral-drug literature. citeturn13search0turn13search15

- Group name: strongly acidic polyacid motifs such as phosphonates, bisphosphonates, phosphates, or sulfonic-acid-rich motifs.
- Usually associated with: option A. citeturn45search1turn12search6
- Brief note: highly charged acidic motifs are repeatedly used to produce low passive permeability and gut restriction; classic bisphosphonate-like tetraacids are a clear example of very low oral absorption driven by high charge. citeturn45search1turn12search6
- Source: charged-acid motif studies and gut-restricted drug-design reviews. citeturn45search1turn12search6