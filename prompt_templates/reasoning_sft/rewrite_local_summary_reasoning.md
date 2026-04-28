You are writing only the final neighbor-based synthesis for a chemistry classification example.

Background
Selected per-neighbor molecule-comparison analyses have already been written upstream. Each selected neighbor has its own similarity to the query, neighbor label, neighbor-level prediction, and evidence strength.
Your job here is only to combine those selected neighbor-level conclusions into the final neighbor-based classification reasoning. Do not rewrite the detailed descriptor-level evidence from scratch.

Input 1. Label semantics
"""
Option (A): {{NEGATIVE_LABEL_SEMANTICS}}
Option (B): {{POSITIVE_LABEL_SEMANTICS}}
"""

Input 2. Rewritten per-neighbor comparisons
"""
{{SELECTED_NEIGHBOR_COMPARISONS}}
"""

Input 3. Required final neighbor-based prediction
{{LOCAL_TEACHER_PREDICTION_SEMANTICS}}

Input 4. Neighbor-level prediction vote count among the selected neighbors
{{NEIGHBOR_PREDICTION_VOTE_COUNT}}

Hard requirements:
1. Use only the supplied label semantics, the selected rewritten per-neighbor comparisons, their similarities, their neighbor labels, their neighbor-level predictions, their evidence strengths, and the required final neighbor-based prediction.
2. Do not use global analysis, ground-truth label, local score, pair score, probability, contribution, raw feature terms, or hidden teacher signal.
3. The final `reasoning` must explicitly mention every selected neighbor by name: {{SELECTED_NEIGHBOR_NAMES}}.
4. Do not silently drop, merge away, renumber, or miscount neighbors. There are exactly {{SELECTED_NEIGHBOR_COUNT}} selected neighbors.
5. Preserve every neighbor-level prediction exactly. Do not convert a neighbor-level option (A) conclusion into option (B), or option (B) into option (A).
6. When grouping evidence by direction, use the **neighbor-level prediction**, not the neighbor label. A neighbor labeled option (A) but predicted as option (B) is support for option (B), not a counterpoint to option (B). A neighbor labeled option (B) but predicted as option (A) is support for option (A), not a counterpoint to option (A).
7. The neighbor label is only context about the reference molecule. Do not turn the neighbor label itself into a vote unless the neighbor-level prediction points the same way.
8. Preserve every neighbor-level evidence strength exactly. Low-strength evidence must stay weak/cautious, medium-strength evidence must stay moderate, and high-strength evidence may be described as strong.
9. Use similarity and evidence strength when explaining the synthesis. A high-similarity high-strength neighbor should carry more weight than a low-similarity low-strength neighbor, but all selected neighbors must still be accounted for.
10. Explicitly handle agreement and conflict across the selected neighbors. Do not force all neighbors to sound like they point in the same direction if they do not.
11. State the exact selected-neighbor prediction vote count once in natural prose, using both option letters and numeric digits from Input 4. Include one sentence in this form with the actual counts: "Among the selected neighbors, option (A) has 0 neighbors and option (B) has 4 neighbors." Do not replace the numeric counts with words such as "none", "all", or "unanimously".
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
- Shorter than the selected upstream neighbor analyses combined
- A good structure is:
  First group the selected neighbors by direction and strength.
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
    "uses_all_selected_neighbors": true or false,
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
