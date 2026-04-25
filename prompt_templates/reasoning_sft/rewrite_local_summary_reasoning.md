You are writing only the final neighbor-based synthesis for a chemistry classification example.

Background
Six per-neighbor molecule-comparison analyses have already been written upstream. Each neighbor has its own similarity to the query, neighbor label, neighbor-level prediction, and evidence strength.
Your job here is only to combine those six neighbor-level conclusions into the final neighbor-based classification reasoning. Do not rewrite the detailed descriptor-level evidence from scratch.

Input 1. Label semantics
"""
Option (A): {{NEGATIVE_LABEL_SEMANTICS}}
Option (B): {{POSITIVE_LABEL_SEMANTICS}}
"""

Input 2. Rewritten per-neighbor comparisons
"""
Neighbor 1
Neighbor label: {{NEIGHBOR_1_LABEL_SEMANTICS}}
Similarity to query: {{NEIGHBOR_1_SIMILARITY}}
Neighbor-level prediction: {{NEIGHBOR_1_PREDICTION_SEMANTICS}}
Evidence strength: {{NEIGHBOR_1_EVIDENCE_STRENGTH}}
Reasoning: {{NEIGHBOR_1_REASONING}}

Neighbor 2
Neighbor label: {{NEIGHBOR_2_LABEL_SEMANTICS}}
Similarity to query: {{NEIGHBOR_2_SIMILARITY}}
Neighbor-level prediction: {{NEIGHBOR_2_PREDICTION_SEMANTICS}}
Evidence strength: {{NEIGHBOR_2_EVIDENCE_STRENGTH}}
Reasoning: {{NEIGHBOR_2_REASONING}}

Neighbor 3
Neighbor label: {{NEIGHBOR_3_LABEL_SEMANTICS}}
Similarity to query: {{NEIGHBOR_3_SIMILARITY}}
Neighbor-level prediction: {{NEIGHBOR_3_PREDICTION_SEMANTICS}}
Evidence strength: {{NEIGHBOR_3_EVIDENCE_STRENGTH}}
Reasoning: {{NEIGHBOR_3_REASONING}}

Neighbor 4
Neighbor label: {{NEIGHBOR_4_LABEL_SEMANTICS}}
Similarity to query: {{NEIGHBOR_4_SIMILARITY}}
Neighbor-level prediction: {{NEIGHBOR_4_PREDICTION_SEMANTICS}}
Evidence strength: {{NEIGHBOR_4_EVIDENCE_STRENGTH}}
Reasoning: {{NEIGHBOR_4_REASONING}}

Neighbor 5
Neighbor label: {{NEIGHBOR_5_LABEL_SEMANTICS}}
Similarity to query: {{NEIGHBOR_5_SIMILARITY}}
Neighbor-level prediction: {{NEIGHBOR_5_PREDICTION_SEMANTICS}}
Evidence strength: {{NEIGHBOR_5_EVIDENCE_STRENGTH}}
Reasoning: {{NEIGHBOR_5_REASONING}}

Neighbor 6
Neighbor label: {{NEIGHBOR_6_LABEL_SEMANTICS}}
Similarity to query: {{NEIGHBOR_6_SIMILARITY}}
Neighbor-level prediction: {{NEIGHBOR_6_PREDICTION_SEMANTICS}}
Evidence strength: {{NEIGHBOR_6_EVIDENCE_STRENGTH}}
Reasoning: {{NEIGHBOR_6_REASONING}}
"""

Input 3. Required final neighbor-based prediction
{{LOCAL_TEACHER_PREDICTION_SEMANTICS}}

Input 4. Neighbor-level prediction vote count
{{NEIGHBOR_PREDICTION_VOTE_COUNT}}

Hard requirements:
1. Use only the supplied label semantics, the six rewritten per-neighbor comparisons, their similarities, their neighbor labels, their neighbor-level predictions, their evidence strengths, and the required final neighbor-based prediction.
2. Do not use global analysis, ground-truth label, local score, pair score, probability, contribution, raw feature terms, or hidden teacher signal.
3. The final `reasoning` must explicitly mention all six neighbors by name: `Neighbor 1`, `Neighbor 2`, `Neighbor 3`, `Neighbor 4`, `Neighbor 5`, and `Neighbor 6`.
4. Do not silently drop, merge away, renumber, or miscount neighbors. There are exactly 6 neighbors.
5. Preserve every neighbor-level prediction exactly. Do not convert a neighbor-level option (A) conclusion into option (B), or option (B) into option (A).
6. When grouping evidence by direction, use the **neighbor-level prediction**, not the neighbor label. A neighbor labeled option (A) but predicted as option (B) is support for option (B), not a counterpoint to option (B). A neighbor labeled option (B) but predicted as option (A) is support for option (A), not a counterpoint to option (A).
7. The neighbor label is only context about the reference molecule. Do not turn the neighbor label itself into a vote unless the neighbor-level prediction points the same way.
8. Preserve every neighbor-level evidence strength exactly. Low-strength evidence must stay weak/cautious, medium-strength evidence must stay moderate, and high-strength evidence may be described as strong.
9. Use similarity and evidence strength when explaining the synthesis. A high-similarity high-strength neighbor should carry more weight than a low-similarity low-strength neighbor, but all six neighbors must still be accounted for.
10. Explicitly handle agreement and conflict across the six neighbors. Do not force all neighbors to sound like they point in the same direction if they do not.
11. State the exact neighbor-level prediction vote count once in natural prose, using the two option letters and the exact counts from Input 4. For example, "At the neighbor level, option (A) has 1 neighbor and option (B) has 5 neighbors." Use the actual counts for this example.
12. The final `local_prediction` object must exactly match the required final neighbor-based prediction.
13. Do not add new descriptor-level evidence, new raw values, new chemical facts, new task thresholds, new neighbors, or new experimental facts.
14. Do not re-explain every descriptor. You may briefly refer to the major already-written neighbor-level themes when needed, but the summary should focus on aggregation, weighting, and conflict resolution.
15. Do not let a low-strength neighbor sound decisive. Use cautious language such as "weak", "slight", "mixed", or "limited" when summarizing low-strength evidence.
16. Do not describe the final prediction as a probability, score, or confidence value.
17. Do not mention model internals, pairwise EBM, aggregation code, teacher labels, hidden reasoning process, datasets, training, or reward.
18. The final `reasoning` must read like direct scientific reasoning, not commentary about source materials. **Do not** say "draft", "note", "playbook", "prompt", "input", "instruction", "contribution", "pair score", "source comparison", "supplied comparison", "neighbor-comparison level", or similar metadata words in the final text.
19. Do not write phrases such as "the supplied comparison says", "the source says", "the neighbor note says", "was treated as", "was judged as", "was interpreted as", "classified by its own comparison", or "the required prediction is". Translate those ideas into direct neighbor-based scientific reasoning instead.
20. Do not include bullet points in the final `reasoning`.

Preferred style:
- Concise but explicit
- Synthesis-heavy rather than descriptor-detail-heavy
- Neighbor-aware and conflict-aware
- Clear about similarity and evidence-strength weighting
- Shorter than the six upstream neighbor analyses combined
- A good structure is:
  First group the neighbors by direction and strength.
  Then discuss how similarity changes the weighting.
  Then explain how conflicting or low-strength neighbors affect the final judgment.
  End with the required final neighbor-based prediction.

Return JSON with exactly this schema:
```json
{
  "reasoning": "...",
  "local_prediction": {
    "option": "A or B",
    "text": "...",
    "label": 0 or 1
  },
  "quality_check": {
    "uses_all_six_neighbors": true or false,
    "uses_similarity_and_evidence_strength": true or false,
    "handles_conflicting_neighbors": true or false,
    "uses_neighbor_level_predictions_as_votes": true or false,
    "does_not_add_new_descriptor_evidence": true or false,
    "preserves_neighbor_predictions": true or false,
    "preserves_neighbor_strengths": true or false,
    "final_prediction_matches_required_label": true or false,
    "no_meta_references": true or false
  }
}
```
