You are doing literature-grounded deep research to build a task-specific molecular-property playbook.

Task:
TDC task SARSCoV2_Vitro_Touret, where option (A) means does not inhibit SARS-CoV-2 replication and option (B) means inhibits SARS-CoV-2 replication

Goal:
Build a practical playbook for the task above, covering as many of the scientifically meaningful molecular properties used in this task as possible.

Important context:
- Your job is to find literature-supported threshold anchors, cutoffs, ranges, or commonly used interpretive rules for the provided molecular properties, specifically in the context of this task or the closest scientifically relevant neighboring tasks.
- We care about practical thresholds that chemists, ADMET researchers, or medicinal chemistry literature actually use, not only descriptor definitions.
- The property list below already uses human-readable names. Use those names directly in the playbook.
- In addition to numeric properties, if there are especially important functional groups that are repeatedly associated with the task outcome, record them in a separate qualitative section. Functional groups usually do not need thresholds or numeric ranges.

Molecular properties to cover:
- neutral fraction: estimated fraction of the molecule that is neutral at the configured pH
- estimated logD: estimated logD at the configured pH
- strongest acidic pKa: pKa of the strongest acidic site
- strongest basic pKa: pKa of the strongest basic site
- number of acidic sites: number of acidic ionizable sites in the molecule
- number of basic sites: number of basic ionizable sites in the molecule
- number of ionizable sites: total number of acidic and basic ionizable sites
- exact molecular weight: exact isotopic molecular weight
- fraction of sp3 carbons: fraction of carbon atoms that are sp3 hybridized
- heavy-atom count: number of non-hydrogen atoms
- heavy-atom molecular weight: molecular weight contributed by heavy atoms
- Labute surface area: Labute approximate surface area
- maximum absolute partial charge: largest absolute atomic partial charge
- maximum partial charge: most positive atomic partial charge
- minimum absolute partial charge: smallest absolute atomic partial charge
- minimum partial charge: most negative atomic partial charge
- estimated logP: RDKit-estimated octanol/water partition coefficient (logP)
- molecular weight: molecular weight
- NH/OH group count: number of NH or OH groups
- nitrogen/oxygen atom count: number of nitrogen and oxygen atoms
- aliphatic carbocycle count: number of aliphatic carbocyclic rings
- aliphatic heterocycle count: number of aliphatic heterocyclic rings
- aliphatic ring count: number of aliphatic rings
- aromatic carbocycle count: number of aromatic carbocyclic rings
- aromatic heterocycle count: number of aromatic heterocyclic rings
- aromatic ring count: number of aromatic rings
- hydrogen-bond acceptor count: number of hydrogen-bond acceptors
- hydrogen-bond donor count: number of hydrogen-bond donors
- heteroatom count: number of heteroatoms, such as N, O, or S
- rotatable-bond count: number of rotatable bonds
- saturated carbocycle count: number of saturated carbocyclic rings
- saturated heterocycle count: number of saturated heterocyclic rings
- saturated ring count: number of saturated rings
- ring count: total number of rings
- topological polar surface area: topological polar surface area of the molecule
- QED drug-likeness: quantitative estimate of drug-likeness

Requirements:
1. Prioritize task-specific literature. If unavailable, use the closest neighboring domain and explicitly label it as a proxy.
2. For each molecular property, try to find the most commonly used literature threshold(s), cutoff(s), or heuristic range(s).
3. Keep the answer concise. We want a practical playbook, not a long review.
4. If the literature is conflicting, briefly note the main alternatives instead of forcing a single threshold.
5. If no reliable threshold exists, say so explicitly and give only a short qualitative note.
6. Do not invent thresholds.
7. Use primary sources or strong reviews whenever possible.
8. For the functional-group section, include only groups with fairly clear task relevance. Do not try to list every possible group.

Output format:
Produce a short playbook with one section per molecular property, using exactly this schema:

## {property_name}
- Common threshold(s) or range(s):
- Usually associated with:
- Brief note:
- Source:

If no reliable threshold exists, use:
- Common threshold(s) or range(s): no stable literature threshold found
- Usually associated with:
- Brief note:
- Source:

After the property sections, add one more section using exactly this schema:

## Functional-group notes

For each clearly task-relevant functional group, add:
- Group name:
- Usually associated with:
- Brief note:
- Source:

If no clearly task-relevant functional group pattern is supported, write:
- Group name: no stable task-specific functional-group pattern found
- Usually associated with:
- Brief note:
- Source:
