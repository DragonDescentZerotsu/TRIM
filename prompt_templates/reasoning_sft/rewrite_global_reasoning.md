You are rewriting rough single-molecule analysis notes from Explainable Boosting Machine (EBM) into high-quality reasoning SFT data for {{TASK_DESCRIPTION}}.

Input 1. Task playbook
{{TASK_PLAYBOOK}}

Input 2. Single-molecule analysis notes
{{GLOBAL_MIDDLE_DRAFT}}

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
