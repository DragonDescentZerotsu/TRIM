You are rewriting one rough neighbor-based molecule-comparison note into high-quality reasoning SFT data for {{TASK_DESCRIPTION}}.

Input 1. Task playbook
{{TASK_PLAYBOOK}}

Input 2. Label semantics
"""
Option (A): {{NEGATIVE_LABEL_SEMANTICS}}
Option (B): {{POSITIVE_LABEL_SEMANTICS}}
"""

Input 3. Single-neighbor comparison
"""
Neighbor: {{NEIGHBOR_INDEX}}
Neighbor label: {{NEIGHBOR_LABEL_SEMANTICS}}
Similarity to query: {{NEIGHBOR_SIMILARITY}}
Comparison note: {{NEIGHBOR_MIDDLE_DRAFT}}
"""

Input 4. Required neighbor-level output parsed from the comparison note
"""
Neighbor-level prediction: {{NEIGHBOR_PREDICTION_SEMANTICS}}
Evidence strength: {{NEIGHBOR_EVIDENCE_STRENGTH}}
"""

Hard requirements:
1. Use only the task playbook, the supplied label semantics, this neighbor's similarity, this neighbor's label, this neighbor's comparison note, and the required neighbor-level output parsed from that note.
2. Rewrite exactly one neighbor: `Neighbor {{NEIGHBOR_INDEX}}`. Do not mention, invent, compare, summarize, or rely on any other neighbor.
3. The final `reasoning` must explicitly mention `Neighbor {{NEIGHBOR_INDEX}}`.
4. The final `reasoning` must be evidence-first: start with the raw neighbor/query/delta observations and their chemical interpretation, then give the neighbor-level prediction direction near the end.
5. Do not start the reasoning with the predicted option, the predicted label, "supports option", "leans toward option", "points to option", "consistent with option", or any equivalent early conclusion.
6. Only describe evidence that appears in this neighbor's supplied comparison note. Do not introduce any new descriptor, property, trend, neighbor, experimental fact, or molecular evidence.
7. Do not skip any feature that appears in this neighbor's supplied comparison note. Every source-note feature must still be covered somewhere in the rewrite.
8. You do not need to give the same level of detail to every feature. Major features can be expanded with fuller raw-value discussion, while secondary features may be covered more briefly as long as they are not omitted.
9. Use enough concrete `neighbor`, `query`, and `delta` values to anchor the reasoning, but do not turn the paragraph into a rigid value-by-value inventory.
10. Preserve the `neighbor` and `query` roles exactly. If the comparison note says the neighbor lacks a feature and the query has it, the rewrite must not say that the query lacks it or that the neighbor has it. If a query-minus-neighbor delta is positive, the query value must be higher or more present than the neighbor value; if it is negative, the query value must be lower or less present.
11. You may rewrite naturally, and you may use qualitative trend words such as "higher", "lower", "increased", "decreased", "favorable", or "unfavorable", but when a feature is important to the argument, keep its original concrete `neighbor`, `query`, and `delta` values alongside the interpretation rather than replacing them with vague wording.
12. The reasoning must explain why this comparison overall supports its neighbor-level prediction direction while preserving the evidence strength/confidence stated in the comparison note. For example, low-strength or mixed evidence must stay cautious and should not be rewritten as strong or high-confidence evidence. Raw values should support the explanation, not crowd it out.
13. If the supplied comparison note uses explicit non-numeric value semantics such as `not applicable`, `no acidic site`, `no basic site`, or `delta not defined`, preserve those concrete value semantics rather than dropping them when they matter to the argument.
14. Do not infer whole-molecule properties that were not explicitly stated in the supplied neighbor note. Stay close to the source content.
15. Treat this neighbor comparison as context-dependent analog evidence, not as a universal rule about the descriptor.
16. When you explain a descriptor, anchor the explanation to this neighbor's starting value or range and the specific query-minus-neighbor change described in the comparison note.
17. Do not rewrite a descriptor as if "higher is always better" or "lower is always worse" unless that exact monotonic rule is explicitly supported by this neighbor's supplied comparison note or the playbook.
18. Use the playbook only to explain why a value region or direction can matter chemically. The playbook must never override the directional effect already stated in the neighbor note.
19. If the playbook describes a descriptor in terms of ranges, windows, thresholds, or non-monotonic behavior, preserve that range-based interpretation in the rewrite. Do not flatten a range-based rule into a simple monotonic claim.
20. If a descriptor effect depends on baseline context, make that dependence clear, but you do not need to force repetitive phrases such as "in this comparison" or "at this baseline" into every sentence.
21. When relevant, connect this neighbor's raw value to the playbook's described value region or interval before explaining why the observed delta helps or hurts in this specific analog comparison.
22. Keep the final reasoning faithful to the supplied comparison note's neighbor-level direction and evidence strength.
23. The `neighbor_prediction` object must exactly match the required neighbor-level prediction. Do not choose the opposite option even if some individual feature observations point that way.
24. The `evidence_strength` field must exactly match the required evidence strength. Do not strengthen or weaken it.
25. In mixed or low-strength cases, do not say that evidence for the opposite option "outweighs", "dominates", or "is closer to" the opposite option and then conclude with the required option. Instead, describe the evidence as mixed and explain that the net neighbor-level direction is weak/slight/cautious support for the required option.
26. Do not invent new similarities, new molecular evidence, new experimental facts, or a final six-neighbor prediction.
27. Do not mention model internals, pairwise EBM, aggregation code, prompt instructions, or hidden reasoning process.
28. Keep the final reasoning faithful to the original comparison-note direction while making the prose more natural, coherent, and scientist-like.
29. The final `reasoning` must read like direct scientific reasoning, not commentary about source materials. **Do not** say "draft", "note", "playbook", "prompt", "input", "instruction", "contribution", "pair score", "supplied comparison", "source comparison", or similar metadata words in the final text.
30. Do not write phrases such as "in this draft", "in this note", "the playbook says", "the prompt provides", "this contribution pushes toward", "the supplied comparison treats", "source comparison", "this feature is treated as", "treats this as", "was judged to favor", "is judged against", "was read as", "was interpreted as", "was associated with", or "in this comparison". Translate those ideas into direct chemistry reasoning instead.
31. Do not mention EBM numeric model scores, prediction probabilities, predictive scores, overall scores, net scores, or any other classification-score values. Molecular descriptor values such as a supplied QED score may still be used when they appear in the supplied neighbor note.
32. Do not use mechanical numbered markers such as "Step 6", "Step 7", or "Step 8" in the final `reasoning`. Ordinary prose transitions are allowed when they read naturally, but do not copy a rigid source-note sequence.
33. Do not include bullet points in the final `reasoning`.

Preferred style:
- Explicit, stepwise, chemically grounded
- Natural scientific prose
- Specific but not robotic
- More like thoughtful analysis than formal rule execution
- Baseline-aware and context-aware rather than globally monotonic
- Prefer interval-aware explanations when the playbook gives range-dependent guidance
- Cover all source-note features, but let secondary ones be handled more briefly than the major ones
- Let the prose flow naturally instead of forcing the same sentence template for every feature
- A good structure is:
  Discuss the raw neighbor/query/delta observations for `Neighbor {{NEIGHBOR_INDEX}}`.
  Interpret the larger feature changes in the task context.
  Conclude with the neighbor-level prediction direction and evidence strength.

Return JSON with exactly this schema:
```json
{
  "neighbor_index": {{NEIGHBOR_INDEX_JSON}},
  "reasoning": "...",
  "neighbor_prediction": {
    "option": "A or B",
    "text": "...",
    "label": 0 or 1
  },
  "evidence_strength": "low|medium|high",
  "quality_check": {
    "evidence_before_prediction": true or false,
    "covers_all_source_features": true or false,
    "prediction_matches_source_note": true or false,
    "evidence_strength_matches_source_note": true or false,
    "all_claims_grounded_in_this_neighbor": true or false,
    "no_meta_references": true or false
  }
}
```
