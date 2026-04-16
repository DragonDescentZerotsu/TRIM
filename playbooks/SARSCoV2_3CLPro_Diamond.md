# SARS-CoV-2 3CL protease Diamond molecular-property playbook

The TDC task is sourced from a large XChem crystallographic fragment screen against SARS-CoV-2 main protease performed at entity["organization","Diamond Light Source","Didcot, England, UK"], so fragment-screening rules are the best direct anchors. Where the Diamond literature does not use a descriptor explicitly, the closest proxy is neighboring SARS-CoV-2 3CLpro hit-finding or standard medicinal-chemistry filters such as rule-of-three, Veber, Egan, Lipinski, and Muegge. citeturn12search17turn15view0turn23view4turn25search1turn38search3turn26search2turn30search2turn28search0

## neutral fraction: estimated fraction of the molecule that is neutral at the configured pH
- Common threshold(s) or range(s): proxy only. By Henderson–Hasselbalch, a site is ~50% neutral at pH = pKa; ~90/10 at about 1 pH unit away; ~99/1 at about 2 units away. For 3CLpro-relevant medicinal chemistry, the most practical anchor is therefore whether the nearest acidic/basic pKa lies within about 1–2 units of the configured pH. citeturn33search5turn33search3turn35search17
- Usually associated with: higher neutral fraction is generally more consistent with fragment-like binders and soaking-compatible chemistry; overwhelmingly charged species are less typical starting points in Diamond-like fragment collections. citeturn23view4turn15view0
- Brief note: no Diamond paper uses neutral fraction directly; use it as a pKa-derived proxy, especially if the configured pH is near physiological pH. citeturn12search17turn35search1
- Source: Reijenga et al. on pKa/Henderson–Hasselbalch; Gaohua et al. on pH–pKa crosstalk; Diamond/TDC task description. citeturn33search5turn35search17turn12search17

## estimated logD: estimated logD at the configured pH
- Common threshold(s) or range(s): primary fragment anchor is cLogD (pH 7.4) between about −3 and 3; classic fragment rule-of-three also uses cLogP/cLogD ≤3. A broader oral-ADME proxy is the “golden triangle” logD window of roughly −2 to 5 when interpreted against MW. citeturn23view4turn23view2turn31search0
- Usually associated with: low-to-moderate logD is more consistent with Diamond-like fragment binders; very high logD is more often associated with grease, aggregation risk, and later-stage oral-lead tradeoffs rather than initial crystal-fragment positives. citeturn23view4turn39search7
- Brief note: if the configured pH is not 7.4, use the same logic but shift interpretation with the molecule’s pKa values. citeturn32search3turn31search2
- Source: Bon et al. fragment-library design review; Johnson et al. golden triangle; broader acid/base-property review. citeturn23view4turn31search0turn32search3

## strongest acidic pKa: pKa of the strongest acidic site
- Common threshold(s) or range(s): proxy at pH ~7.4: acids with pKa <4 are >99% charged; acids with pKa 6–8 are in mixed ionization equilibrium; acids well above physiological pH are increasingly neutral. citeturn35search1turn35search17
- Usually associated with: very strongly acidic groups are less typical of fragment-like 3CLpro binders; weaker acids or neutralizable acidic motifs fit the fragment-screening regime better. citeturn23view4turn15view0
- Brief note: this is a proxy from general medicinal chemistry, not a Diamond-specific cutoff. The task literature more often filters size/lipophilicity than acid pKa directly. citeturn12search17turn23view4
- Source: Manallack on pKa distributions; Gaohua et al.; fragment-library review. citeturn35search1turn35search17turn23view4

## strongest basic pKa: pKa of the strongest basic site
- Common threshold(s) or range(s): proxy at pH ~7.4: bases with pKa >10 are >99% protonated; bases with pKa 6–8 are mixed; bases below about pKa 4 are mostly unprotonated/neutral. citeturn35search1turn35search17
- Usually associated with: weakly basic heteroaromatics are common in 3CLpro binders, because S1 frequently uses pyridine- or isoxazole-like nitrogens; very strongly basic amines can push compounds out of the fragment-like ionization space. citeturn18view0turn19view0turn35search1
- Brief note: task-relevant positive chemistry often uses a basic heteroatom as an H-bond acceptor, not a highly protonated aliphatic amine. citeturn18view0turn17view4
- Source: Manallack on drug pKa distributions; Douangamath et al. fragment-binding modes. citeturn35search1turn18view0turn19view0

## number of acidic sites: number of acidic ionizable sites in the molecule
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view4turn10search17
- Usually associated with: Diamond-like binders are more often neutral to mildly ionizable overall; highly polyanionic chemotypes are uncommon in fragment collections. citeturn23view4turn35search1
- Brief note: 3CLpro and FBDD papers generally gate on MW, logD, HBA/HBD, rings, and TPSA rather than acidic-site count itself. citeturn23view4turn25search1
- Source: Bon et al. fragment-library review; Kralj review of molecular filters; Manallack pKa review. citeturn23view4turn10search17turn35search1

## number of basic sites: number of basic ionizable sites in the molecule
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view4turn10search17
- Usually associated with: one weakly basic heteroatom can be beneficial; strongly polybasic cationic scaffolds are not a standard fragment-screening preference. citeturn18view0turn23view4turn35search1
- Brief note: the task literature points to one well-placed heteroaromatic basic site more often than multiple protonatable amines. citeturn18view0turn19view0
- Source: Douangamath et al.; fragment-library review; pKa distribution review. citeturn18view0turn19view0turn23view4turn35search1

## number of ionizable sites: total number of acidic and basic ionizable sites
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view4turn10search17
- Usually associated with: fewer ionizable centers are generally more fragment-like; multiple ionizable centers chiefly matter through their effects on logD, solubility, and TPSA. citeturn23view4turn32search3
- Brief note: for this task, pKa pattern plus logD is more actionable than counting total ionizable sites. citeturn32search3turn23view4
- Source: Bon et al.; Manallack/Prankerd acid–base review; molecular-filters review. citeturn23view4turn32search3turn10search17

## exact molecular weight: exact isotopic molecular weight
- Common threshold(s) or range(s): direct task anchor is fragment-scale <300 Da; the accepted fragment definition is usually ≤300 Da and often ≤20 heavy atoms. A neighboring non-fragment 3CLpro screen used 300 < MW < 450; classic oral upper guide is MW ≤500. citeturn15view0turn23view2turn25search1turn38search3
- Usually associated with: Diamond-task binders are most plausibly enriched in the ≤300 Da fragment regime; 300–450 Da is more typical of larger non-peptidic 3CLpro screening matter; >500 is more often advanced peptidomimetic territory. citeturn12search17turn15view0turn25search1turn38search3
- Brief note: exact MW and nominal MW behave the same for triage here; the key distinction is fragment-like versus expanded inhibitor-like matter. citeturn12search17turn23view4
- Source: Diamond/TDC task description; Douangamath et al.; Bon et al.; Yamamoto et al.; Lipinski et al. citeturn12search17turn15view0turn23view2turn25search1turn38search3

## fraction of sp3 carbons: fraction of carbon atoms that are sp3 hybridized
- Common threshold(s) or range(s): the clearest 3CLpro task-neighboring screen used Fsp3 = 0.1–0.45. Outside SARS-CoV-2, fragment reviews support “some” 3D character but do not impose a universal hard cutoff. citeturn25search1turn24view1turn24view0
- Usually associated with: very low Fsp3 often tracks flat aromatic chemistry; moderate Fsp3 is more consistent with tractable fragment matter. citeturn24view1turn25search1
- Brief note: use 0.1–0.45 as a useful neighboring-task proxy, not as a strict Diamond-specific rule. citeturn25search1turn12search17
- Source: Yamamoto et al. 3CLpro screen; Bon et al. fragment-library review. citeturn25search1turn24view1

## heavy-atom count: number of non-hydrogen atoms
- Common threshold(s) or range(s): fragment definition is generally ≤20 heavy atoms; a practical fragment filter is 8–20; a neighboring 3CLpro small-molecule screen used 20–30. citeturn22view0turn23view4turn25search1
- Usually associated with: ≤20 is more consistent with Diamond fragment positives; 20–30 is more typical of later hit-expansion or non-fragment 3CLpro screening. citeturn12search17turn23view4turn25search1
- Brief note: this is one of the most directly relevant size descriptors for the Diamond task. citeturn12search17turn22view0
- Source: Bon et al.; Kirsch et al.; Yamamoto et al. citeturn22view0turn23view4turn25search1

## heavy-atom molecular weight: molecular weight contributed by heavy atoms
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view4turn10search17
- Usually associated with: it tracks overall size much like MW and heavy-atom count; fragment-like binders still usually occupy the ≤300 Da / ≤20 heavy-atom region. citeturn15view0turn23view4
- Brief note: medicinal-chemistry papers almost always threshold MW or heavy-atom count, not heavy-atom-only MW. citeturn23view4turn10search17
- Source: Douangamath et al.; Bon et al.; molecular-filters review. citeturn15view0turn23view4turn10search17

## Labute surface area: Labute approximate surface area
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view4turn10search17
- Usually associated with: overall compactness helps, but no standalone SARS-CoV-2 3CLpro cutoff is used in practice. citeturn23view4turn15view0
- Brief note: task-relevant literature uses TPSA and global size descriptors instead. citeturn23view2turn23view4
- Source: fragment-library design review; molecular-filters review. citeturn23view4turn10search17

## maximum absolute partial charge: largest absolute atomic partial charge
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view4turn10search17
- Usually associated with: well-placed polarized atoms are important, especially carbonyl oxygens and heteroaromatic nitrogens, but descriptor-level charge maxima are not thresholded for 3CLpro. citeturn18view0turn19view0
- Brief note: SARS-CoV-2 3CLpro papers discuss specific H-bond motifs and warheads rather than abstract partial-charge cutoffs. citeturn18view0turn19view0
- Source: Douangamath et al.; fragment-library and molecular-filter reviews. citeturn18view0turn19view0turn23view4turn10search17

## maximum partial charge: most positive atomic partial charge
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view4turn10search17
- Usually associated with: positively polarized donor sites can help if correctly placed, but no 3CLpro- or FBDD-standard maximum-positive-charge cutoff is used. citeturn41search2turn18view0
- Brief note: placement and functional-group identity matter much more than the scalar descriptor. citeturn41search2turn19view0
- Source: Giordanetto et al. fragment-hit interaction analysis; Douangamath et al.; filter reviews. citeturn41search2turn19view0turn23view4turn10search17

## minimum absolute partial charge: smallest absolute atomic partial charge
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view4turn10search17
- Usually associated with: no standalone direction beyond the overall fragment-like preference for compact, moderately polar molecules. citeturn23view4turn15view0
- Brief note: this descriptor is not a common medicinal-chemistry triage handle for 3CLpro binding. citeturn10search17turn23view4
- Source: fragment-library review; molecular-filters review. citeturn23view4turn10search17

## minimum partial charge: most negative atomic partial charge
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view4turn10search17
- Usually associated with: strongly negative atoms are often carbonyl or acidic oxygens; 3CLpro commonly rewards carbonyl oxygens in amide, urea, lactam, or chloroacetyl motifs, but no descriptor-level cutoff is standard. citeturn18view0turn19view0
- Brief note: this is best interpreted structurally, not numerically. citeturn18view0turn19view0
- Source: Douangamath et al.; fragment-library and filter reviews. citeturn18view0turn19view0turn23view4turn10search17

## estimated logP: RDKit-estimated octanol/water partition coefficient (logP)
- Common threshold(s) or range(s): fragment rule-of-three uses logP ≤3; Lipinski uses logP ≤5; Egan’s oral-absorption proxy uses logP/AlogP ≤5.88 with PSA guidance. citeturn23view2turn38search3turn30search2
- Usually associated with: low-to-moderate logP is more consistent with fragment soaking and hit quality; very high logP is more often tied to solubility and developability liabilities. citeturn23view4turn39search7
- Brief note: for this task, logP mainly helps separate fragment-like binders from overly greasy matter; use logD if ionization is important. citeturn23view4turn32search3
- Source: Bon et al.; Lipinski et al.; Egan et al. citeturn23view2turn38search3turn30search2

## molecular weight: molecular weight
- Common threshold(s) or range(s): same practical anchors as exact molecular weight: <300 Da for direct fragment relevance; 300–450 Da as a neighboring 3CLpro small-molecule screen proxy; ≤500 Da as the classic oral-drug ceiling. citeturn15view0turn25search1turn38search3
- Usually associated with: positives in this Diamond task are most plausibly enriched in the fragment regime rather than the heavier optimized-inhibitor regime. citeturn12search17turn15view0
- Brief note: MW is a central gatekeeping property for this dataset because its source experiment was a fragment screen. citeturn12search17turn15view0
- Source: Diamond/TDC task description; Douangamath et al.; Yamamoto et al.; Lipinski et al. citeturn12search17turn15view0turn25search1turn38search3

## NH/OH group count: number of NH or OH groups
- Common threshold(s) or range(s): proxy from donor-count rules: fragment filters usually keep this at ≤3; a neighboring 3CLpro screen required at least 1 H-bond donor in its larger screening set. citeturn23view2turn23view4turn25search1
- Usually associated with: 1–3 NH/OH groups is typical of binder-like, tractable matter; zero can still bind if acceptor geometry is good, but the larger 3CLpro screen intentionally kept at least one donor. citeturn25search1turn18view0
- Brief note: this is a proxy because NH/OH count is close to, but not identical with, H-bond donor count. citeturn23view4turn25search1
- Source: Bon et al.; Yamamoto et al.; Douangamath et al. citeturn23view4turn25search1turn18view0

## nitrogen/oxygen atom count: number of nitrogen and oxygen atoms
- Common threshold(s) or range(s): no stable literature threshold found. A general fragment-hit analysis found that many fragment hits devote roughly 20–30% of heavy atoms to N/O atoms capable of H-bonding, but this is not a 3CLpro-specific count rule. citeturn41search0turn41search2
- Usually associated with: binders usually need at least a small N/O cluster because S1 and oxyanion-hole recognition often involve one heteroaromatic N plus one carbonyl O. citeturn18view0turn19view0
- Brief note: literature optimizes the role of these atoms, not their raw count. citeturn18view0turn41search2
- Source: Giordanetto et al.; Douangamath et al. citeturn41search0turn41search2turn18view0turn19view0

## aliphatic carbocycle count: number of aliphatic carbocyclic rings
- Common threshold(s) or range(s): no stable literature threshold found. citeturn25search1turn23view4
- Usually associated with: hydrophobic ring matter can help fill S2, but 3CLpro screening papers threshold total aliphatic rings rather than carbocycle-only counts. citeturn17view1turn25search1
- Brief note: use aliphatic ring count as the better operational proxy. citeturn25search1
- Source: Yamamoto et al.; Douangamath et al.; fragment-library review. citeturn25search1turn17view1turn23view4

## aliphatic heterocycle count: number of aliphatic heterocyclic rings
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view4turn10search17
- Usually associated with: piperidine, piperazine, and lactam-containing rings recur in covalent or optimized 3CLpro chemotypes, but no consistent count cutoff is used. citeturn19view0turn36search4turn36search16
- Brief note: this descriptor is more informative qualitatively than quantitatively. citeturn19view0turn36search16
- Source: Douangamath et al.; nirmatrelvir/3CLpro optimization papers; molecular-filter review. citeturn19view0turn36search4turn36search16turn10search17

## aliphatic ring count: number of aliphatic rings
- Common threshold(s) or range(s): neighboring 3CLpro small-molecule screen used 1–2 aliphatic rings. citeturn25search1
- Usually associated with: one or two aliphatic rings often support S2/S3 filling while keeping total ring count manageable. citeturn25search1turn19view0
- Brief note: this is a neighboring-task proxy, not a direct Diamond fragment requirement. citeturn12search17turn25search1
- Source: Yamamoto et al.; Douangamath et al. citeturn25search1turn19view0

## aromatic carbocycle count: number of aromatic carbocyclic rings
- Common threshold(s) or range(s): no stable literature threshold found. citeturn25search1turn23view4
- Usually associated with: one aromatic carbocycle often helps S2 packing, but the explicit neighboring-task filter is on total aromatic rings rather than carbocycles alone. citeturn17view1turn25search1
- Brief note: use aromatic ring count as the stronger descriptor. citeturn25search1
- Source: Douangamath et al.; Yamamoto et al.; fragment-library review. citeturn17view1turn25search1turn23view4

## aromatic heterocycle count: number of aromatic heterocyclic rings
- Common threshold(s) or range(s): neighboring 3CLpro small-molecule screen required at least 1 aromatic heterocycle. citeturn25search1
- Usually associated with: positive because S1 often recognizes a pyridine-like or isoxazole-like heteroaromatic nitrogen through His163. citeturn18view0turn19view0
- Brief note: this is one of the clearest ring-class rules that carries directly into 3CLpro chemistry. citeturn25search1turn18view0
- Source: Yamamoto et al.; Douangamath et al. citeturn25search1turn18view0turn19view0

## aromatic ring count: number of aromatic rings
- Common threshold(s) or range(s): neighboring 3CLpro small-molecule screen used 2–3 aromatic rings; total ring count still capped at 4. citeturn25search1
- Usually associated with: 2–3 aromatic rings is common in larger non-peptidic 3CLpro hits; for fragment positives, one well-placed aromatic ring can already be sufficient, especially in S2. citeturn17view1turn15view0
- Brief note: for the Diamond task, this is a useful proxy but should be interpreted alongside fragment size. citeturn12search17turn25search1
- Source: Yamamoto et al.; Douangamath et al. citeturn25search1turn17view1turn15view0

## hydrogen-bond acceptor count: number of hydrogen-bond acceptors
- Common threshold(s) or range(s): fragment Ro3 uses HBA ≤3; a practical fragment filter uses HBA ≤4; neighboring 3CLpro screen used HBA 2–7; Lipinski upper guide is HBA ≤10. citeturn23view2turn23view4turn25search1turn38search3
- Usually associated with: binders usually need a few acceptors because 3CLpro frequently exploits one heteroaromatic acceptor plus one or more carbonyl oxygens; very high HBA counts move molecules toward peptidomimetic space. citeturn18view0turn19view0turn38search3
- Brief note: this is one of the most practical task-relevant properties. citeturn18view0turn25search1
- Source: Bon et al.; Yamamoto et al.; Lipinski et al.; Douangamath et al. citeturn23view4turn25search1turn38search3turn18view0turn19view0

## hydrogen-bond donor count: number of hydrogen-bond donors
- Common threshold(s) or range(s): fragment Ro3 uses HBD ≤3; neighboring 3CLpro screen required HBD ≥1 in its larger screening set; Lipinski upper guide is HBD ≤5. citeturn23view2turn25search1turn38search3
- Usually associated with: one donor is often helpful in larger 3CLpro hits, but fragment positives can still be donor-light if acceptor geometry and hydrophobic fit are strong. citeturn25search1turn18view0turn17view1
- Brief note: donor placement matters more than donor count alone. citeturn18view0turn41search2
- Source: Bon et al.; Yamamoto et al.; Lipinski et al.; Giordanetto et al. citeturn23view2turn25search1turn38search3turn41search2

## heteroatom count: number of heteroatoms, such as N, O, or S
- Common threshold(s) or range(s): no stable literature threshold found. citeturn23view4turn10search17
- Usually associated with: multiple heteroatoms are typically needed because His163/Glu166/oxyanion-hole contacts dominate many 3CLpro complexes, but raw heteroatom count alone is less informative than HBA/HBD and ring class. citeturn18view0turn19view0
- Brief note: treat this as a secondary descriptor behind HBA, HBD, TPSA, and aromatic heterocycle count. citeturn23view4turn25search1
- Source: Douangamath et al.; Bon et al.; molecular-filters review. citeturn18view0turn19view0turn23view4turn10search17

## rotatable-bond count: number of rotatable bonds
- Common threshold(s) or range(s): Ro3/fragment rule usually uses ≤3; a practical fragment filter uses ≤4; neighboring 3CLpro screen used 2–6; Veber’s oral-bioavailability proxy uses ≤10. citeturn23view2turn23view4turn25search1turn26search2turn39search2
- Usually associated with: lower flexibility is more consistent with fragment binders and good developability; too many rotors cost conformational efficiency and bioavailability. citeturn23view4turn26search2
- Brief note: for this task, low-rotor fragments are the primary anchor; the 2–6 window is mainly for larger 3CLpro screening matter. citeturn12search17turn25search1
- Source: Bon et al.; Yamamoto et al.; Veber et al. citeturn23view4turn25search1turn26search2turn39search2

## saturated carbocycle count: number of saturated carbocyclic rings
- Common threshold(s) or range(s): no stable literature threshold found. citeturn24view1turn10search17
- Usually associated with: some saturation can help 3D character, but explicit filters usually use Fsp3 or total aliphatic/saturated ring content instead. citeturn24view1turn25search1
- Brief note: use Fsp3 and ring count as better proxies. citeturn24view1turn23view4
- Source: Bon et al.; Yamamoto et al.; molecular-filters review. citeturn24view1turn25search1turn10search17

## saturated heterocycle count: number of saturated heterocyclic rings
- Common threshold(s) or range(s): no stable literature threshold found. citeturn10search17turn23view4
- Usually associated with: lactams, piperidines, and piperazines recur in 3CLpro chemotypes, but no stable standalone count rule is used. citeturn19view0turn36search4turn36search16
- Brief note: this descriptor is better handled qualitatively in the functional-group section. citeturn19view0turn36search16
- Source: Douangamath et al.; nirmatrelvir-related optimization papers; filter reviews. citeturn19view0turn36search4turn36search16turn10search17

## saturated ring count: number of saturated rings
- Common threshold(s) or range(s): no stable literature threshold found. citeturn24view1turn10search17
- Usually associated with: some saturation is desirable for 3D character, but there is no stable 3CLpro-specific count cutoff. citeturn24view1turn25search1
- Brief note: combine with Fsp3 and total ring count rather than using this descriptor alone. citeturn24view1turn23view4
- Source: Bon et al.; Yamamoto et al.; molecular-filters review. citeturn24view1turn25search1turn10search17

## ring count: total number of rings
- Common threshold(s) or range(s): a practical fragment filter uses ring count ≤4; the neighboring 3CLpro screen likewise capped total aromatic + aliphatic rings at ≤4. citeturn23view4turn25search1
- Usually associated with: ≤4 rings is common to both fragment collections and larger non-peptidic 3CLpro screening matter. citeturn23view4turn25search1
- Brief note: this is a strong operational descriptor because it captures both compactness and tractability. citeturn23view4
- Source: Bon et al.; Yamamoto et al. citeturn23view4turn25search1

## topological polar surface area: topological polar surface area of the molecule
- Common threshold(s) or range(s): fragment rule-of-three often uses TPSA/PSA ≤60; a practical fragment filter uses PSA ≤110; Veber’s oral proxy is PSA ≤140 or H-bond count ≤12; Egan’s absorption proxy uses PSA ≤131.6. citeturn23view2turn23view4turn26search2turn39search2turn30search2
- Usually associated with: Diamond-like positives usually sit in low-to-moderate PSA space; very high PSA is more often associated with advanced peptidomimetic inhibitors and poorer passive permeability. citeturn15view0turn36search16turn26search2
- Brief note: for this task, start with fragment-oriented PSA anchors, then use Veber/Egan as downstream developability proxies. citeturn12search17turn23view4turn30search2
- Source: Bon et al.; Veber et al.; Egan et al.; Douangamath et al. citeturn23view4turn26search2turn39search2turn30search2turn15view0

## QED drug-likeness: quantitative estimate of drug-likeness
- Common threshold(s) or range(s): QED >0.67 is the classic “attractive” anchor; around 0.49 is the mean of unattractive compounds; around 0.34 marks “too complex” in the original QED paper. citeturn37search0turn37search6
- Usually associated with: higher QED generally aligns with fragment/nonpeptidic tractability; lower QED flags over-complex or property-imbalanced chemistry. citeturn37search0turn37search22
- Brief note: QED is useful as a summary score, but it is not 3CLpro-specific and can underrate legitimate covalent peptidomimetics. citeturn37search0turn36search16
- Source: Bickerton et al. QED paper; follow-on QED interpretation sources. citeturn37search0turn37search6turn37search22

## Functional-group notes
- Group name: weakly basic heteroaromatic nitrogens such as pyridine- and isoxazole-like motifs
- Usually associated with: binds SARS-CoV-2 3CL protease. citeturn18view0turn19view0
- Brief note: S1-binding fragments repeatedly use a pyridine ring or similar N-containing heterocycle to interact with His163; an isoxazole nitrogen was also highlighted in a fragment that bridged S1 and S1′. citeturn18view0turn19view0
- Source: Douangamath et al. fragment screen. citeturn18view0turn19view0

- Group name: carbonyl-bearing amide, urea, and lactam motifs
- Usually associated with: binds SARS-CoV-2 3CL protease. citeturn18view0turn19view0turn36search16
- Brief note: S1 fragments often pair the heteroaromatic nitrogen with a carbonyl in an amide or urea to engage Glu166, while covalent chloroacetyl series use the carbonyl oxygen to make two or three H-bonds to Gly143/Ser144/Cys145. Lactam glutamine surrogates remain central in optimized inhibitors. citeturn18view0turn19view0turn36search4
- Source: Douangamath et al.; recent 3CLpro inhibitor reviews and nirmatrelvir-analog optimization papers. citeturn18view0turn19view0turn36search16turn36search4

- Group name: hydrophobic aromatic S2 substituents such as phenyl, halophenyl, thiophenyl, and related aryl groups
- Usually associated with: binds SARS-CoV-2 3CL protease. citeturn17view1turn19view0
- Brief note: the S2 pocket was described as an “aromatic wheel,” with aromatic rings making hydrophobic contacts with Met49 or π-stacking with His41; halophenyl and thiophenyl motifs and fluoro/cyano vectors were specifically noted as productive ways to exploit nearby lipophilic space. citeturn17view1turn17view2turn19view0
- Source: Douangamath et al. fragment screen. citeturn17view1turn17view2turn19view0

- Group name: sulfonamide motifs
- Usually associated with: binds SARS-CoV-2 3CL protease. citeturn17view1turn19view0
- Brief note: several S3 fragments carried aromatic sulfonamides that H-bonded with Gln189, and N-chloroacetyl-N′-sulfonamido-piperazines formed one of the recurrent covalent-hit series. The caveat is that some members of that family were frequent hitters, so reactivity control matters. citeturn17view1turn18view0turn19view0
- Source: Douangamath et al. fragment screen. citeturn17view1turn18view0turn19view0

- Group name: mild electrophilic warheads such as N-chloroacetyl, nitrile, bromoalkyne, and isatin
- Usually associated with: binds SARS-CoV-2 3CL protease, especially covalent or reversible-covalent binding to Cys145. citeturn19view0turn20search3turn20search1
- Brief note: the Diamond fragment screen yielded tractable N-chloroacetyl series and unexpected bromoalkyne PepLite binders; the authors explicitly suggested reversible covalent nitriles as replacements, and a later open-form 3CLpro fragment screen identified isatin-based reversible covalent binders. citeturn19view0turn20search3turn20search1
- Source: Douangamath et al.; Huang et al. open-form 3CLpro fragment screen. citeturn19view0turn20search3turn20search1

- Group name: P1 γ-lactam glutamine mimics
- Usually associated with: binds SARS-CoV-2 3CL protease, especially in optimized inhibitors rather than initial Diamond fragments. citeturn36search16turn36search4
- Brief note: across advanced 3CLpro inhibitor chemistry, a five- or six-membered lactam repeatedly serves as the P1 glutamine surrogate; recent nirmatrelvir optimization retained high activity with six-membered P1 lactams, reinforcing this as a robust motif for true binders. citeturn36search16turn36search4
- Source: Recent main-protease inhibitor review; Ghosh et al. P1/P4 nirmatrelvir optimization. citeturn36search16turn36search4