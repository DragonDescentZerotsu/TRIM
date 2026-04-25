# local-only per-neighbor rewrite 改造计划

日期：2026-04-22

## 当前进度

- `[done]` 阶段 0.1：默认 local per-neighbor evidence 从 top-6 改为 top-8。
- `[done]` 阶段 0.2：修正 `pair_score` 的 class-1 probability 语义，并把对应字段保留为诊断 metadata；最终 middle draft 不再把 `pair_score` 概率写进自然语言结论。
- `[done]` 已跑 `BBB_Martins train sample_00000/sample_00001` 两个 top-8 local evidence smoke examples，确认每个 neighbor 展开到 `Step 8`。
- `[done]` 已确认 `exp_reports/EBM_local_only_topk_feature_score_coverage.md` 的 coverage 不包含 EBM intercept / prior，只衡量 top-k feature terms 对 `sum(abs(feature contributions))` 的覆盖率。
- `[decision]` reasoning confidence 不使用 `abs(pair_score - 0.5)`；当前实现保留 teacher posterior confidence 作为诊断 metadata，SFT-facing strength 使用保守的 `teacher_aligned_evidence_strength`。
- `[done]` 阶段 0.3：feature-only confidence metadata 和 middle draft evidence-strength 文案已落到 local evidence JSON。
- `[done]` 阶段 1：16 task × train/valid/test 的 top-8 + feature-strength local evidence 已全量重跑。
- `[done]` 阶段 2：per-neighbor rewrite candidate 结构已实现，旧 monolithic `local_rewrite_input` 暂时保留以兼容现有 pipeline。
- `[done]` 阶段 2.1：train split 16 task 的新版 rewrite candidates 已生成到 `outputs/reasoning_rewrite_candidates/from_filters/train/<task>/`，总计 `14036` 条 manifest-tracked candidates。
- `[done]` 阶段 3：per-neighbor rewrite prompt 和 schema；`rewrite_local_neighbor_reasoning.md` 已新增，`local_neighbor` renderer/example runner 已接通，并用 `gpt-5.4-mini` 生成了 5 个 task 的完整 6-neighbor rewrite 示例。当前 30/30 条通过结构化和文本质量检查。
- `[done]` 阶段 5.1：summary rewrite template 已新增为 `prompt_templates/reasoning_sft/rewrite_local_summary_reasoning.md`；默认不输入 playbook，不输入 legacy `local_summary_middle_draft`，只聚合 6 个 per-neighbor rewrite outputs、similarity、neighbor prediction/strength 和 final local teacher prediction。
- `[done]` 阶段 5.2：summary template fill-in / example runner 已接通为 `local_summary` mode；已用 `gpt-5.4-mini` 基于 no-step evidence 重写 5 个 task 的 summary examples，并通过统一 checker。当前检查结果：5/5 passed，`issue_count=0`。输出根目录：`outputs/reasoning_rewrite_outputs_neighbor_level_no_step/openrouter/openai__gpt-5.4-mini/local_summary/train/`。
- `[done]` 阶段 5.3：summary prompt / checker 已新增 exact neighbor-level vote count 约束。Summary 输入会显式给出 6 个 per-neighbor prediction 的 option (A)/(B) 计数；最终 reasoning 必须自然写出相同计数，checker 会拦截把 5 个写成 4 个这类聚合错误。
- `[done]` 阶段 6.1：agent SFT builder 已新增 `local_neighbor_only` 模式；该模式从 6 个 `local_neighbor` rewrite outputs 和 1 个 `local_summary` rewrite output 组装 local-only transcript。已用 no-step 5 个 task smoke build 出 JSONL，结构检查 `issue_count=0`。
- `[done]` evidence wording cleanup：global/local middle draft 不再使用固定 `First/Next/Then/After that/Finally` 和 `Step N` 连接词，改为自然的 feature-level connector。16 task × train/valid/test 的 global/local evidence 已全量重跑；全量 `sample_*.json` 扫描确认旧连接词无命中。

## 背景

当前 local-only agent SFT 数据使用 monolithic local rewrite：一次性把 6 个 neighbors 的 similarity、middle draft 和最终 `local_prediction` 拼进同一个 rewrite prompt，由 LLM 生成完整 `Neighbor 1..6 + summary` reasoning。

这个流程符合 TRIM 的总体目标：把 pairwise local EBM 的 hidden contribution 合理化改写成可监督 reasoning，让 LLM 学会基于工具返回的 raw neighbor/query/delta values 做 baseline-aware 化学类比推理。但现在的 trace 暴露了几个问题：

- 模型容易在 `Neighbor 1` 开头一两句就先 lock in prediction direction。
- 逐项证据有时不是 evidence-first，而是先有方向、后找证据。
- monolithic rewrite 让 LLM 在同一个 prompt 里同时看到 6 个 neighbor 和最终 label，容易形成整体标签驱动的事后合理化。
- RL 目前主要是 final answer reward，tool error 或非 grounded fallback 只要答案对也可能被奖励。

本计划把 local rewrite 改成两层结构：

1. per-neighbor rewrite：每个 neighbor 单独重写，先列 raw evidence，再给该 neighbor 自己的 pairwise teacher direction 和 feature-evidence strength。
2. summary rewrite：只读取 6 个 per-neighbor reasoning / prediction / feature-evidence strength，再聚合为 local summary 和最终 local prediction。

## 阶段 0：先修 evidence 生成基础

目标：先把后续所有 evidence 重新导出的默认行为改到 top-8，并修正 pair score / confidence 的语义，避免把 prior-heavy teacher probability 写成化学证据强度。

### 0.1 top feature 数量从 6 改为 8

状态：`[done]`

依据：`exp_reports/EBM_local_only_topk_feature_score_coverage.md`

- top-6 median coverage 约 45%。
- top-8 median coverage 约 52%。
- top-10 median coverage 约 57-58%，但每个样本 6 个 neighbors 时长度继续增加。
- 当前折中先采用 top-8，符合 `AGENTS.md` 当前记录。

需要修改：

- `src/trim/reasoning/evidence/local_evidence.py`
  - `extract_local_evidence_for_split(..., top_term_k=8)`
- `src/trim/reasoning/agent_tools/manifests.py`
  - `DEFAULT_LOCAL_TOP_TERM_K = 8`
- `scripts/extract_local_evidence.py`
  - `--top-term-k` default 改成 8
- `scripts/build_agent_tool_manifests.py`
  - `--local-top-term-k` default 改成 8
- 当前默认 core-pKa no-fr task manifests
  - `outputs/reasoning_agent_tools/manifests/fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts/*.json`
  - 将 `local_tool.top_term_k_per_neighbor` 从 6 改成 8，确保 `scripts/extract_reasoning_evidence_all_tasks.py` 直接按默认 manifest 重跑时使用 top-8。

验收：

- `rg "top_term_k_per_neighbor\": 6" outputs/reasoning_agent_tools/manifests/fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts` 不应再命中。
- 新导出的 local evidence 中每个 neighbor 的 `top_pair_terms` 最多为 8。

### 0.2 修正 pair score 文案

状态：`[done]`

当前 `pair_score` 来自：

```python
pair_scores = model.predict_proba(pair_matrix)[:, 1]
```

所以它始终是 label 1 / option B 的预测概率，不是“当前 pair_prediction 的概率”。因此旧文案：

```text
pushes toward option (A) ... with pair score 0.0205
```

容易误导，因为 0.0205 是 class-1 probability；真正支持 A 的概率应是 `1 - 0.0205 = 0.9795`。

最终实现：

- JSON 中保留 `pair_score_class1_probability = pair_score`。
- JSON 中保留 `pair_prediction_probability = pair_score` 或 `1 - pair_score`，用于诊断 teacher posterior。
- 自然语言 middle draft 不再展示 `pair_score` / `pair_prediction_probability`，因为这会把 task prior / EBM intercept 混入 SFT-facing chemical reasoning。
- per-neighbor 结论的可见强度由阶段 0.3 的 `feature_evidence_strength` / `teacher_aligned_evidence_strength` 控制。

验收：

- 新 middle draft 不使用 `with pair score ...` 或 `with probability <number>` 作为结论表达。
- `pair_score` 字段本身仍保留在 JSON 中，供后续计算、筛选和调试。

### 0.3 修正 confidence 语义

状态：`[done]`

我们不把 task prior / EBM intercept 写进 SFT target。原因是 runtime tool 不显式提供 prior，而且把 prior-heavy `pair_score` 写成高置信化学证据会教 LLM 合理化 prior。

因此 confidence 需要拆成两个概念：

- `pair_score` / `pair_prediction`：保留完整 teacher output，用来定义 pairwise teacher direction。
- `feature_evidence_strength`：feature-only evidence 本身强不强，只作为 metadata。

计算方式：

```text
feature_logit = sum(all finite pair-term contributions)
feature_probability = sigmoid(feature_logit)
feature_margin = abs(feature_probability - 0.5)
low:    feature_margin <= 0.1
medium: 0.1 < feature_margin <= 0.3
high:   feature_margin > 0.3
```

新增 JSON 字段：

```json
{
  "feature_logit": 0.1447,
  "feature_probability": 0.5361,
  "feature_prediction": 1,
  "feature_prediction_semantics": {"option": "B", "text": "...", "label": 1},
  "feature_confidence_margin": 0.0361,
  "feature_evidence_strength": "low",
  "teacher_feature_agreement": true,
  "teacher_aligned_evidence_strength": "low",
  "displayed_feature_logit": -0.6931,
  "displayed_feature_probability": 0.3333,
  "displayed_feature_prediction": 0,
  "displayed_teacher_agreement": false,
  "displayed_abs_contribution_coverage": 0.4317
}
```

其中：

- `feature_*` 表示 all finite EBM feature terms 去掉 intercept 后的 feature-only evidence strength，只作为 metadata。
- `displayed_*` 表示当前 top-8 导出证据本身的诊断统计，只用于内部检查；自然语言不提 `displayed` 或 `top-ranked`。
- `teacher_aligned_evidence_strength` 是 SFT-facing per-neighbor strength。若 feature direction 或 displayed top-8 direction 与 teacher direction 不一致，则保守降为 `low`。

middle draft 结论不再写 teacher posterior probability，也不写 runtime tool 不会提供的内部结构，例如把 top-8 叫作“模型列出的最强证据”，或把 hidden full-term aggregate 写进自然语言。

最终 middle draft 使用更通用、runtime-compatible 的 evidence-strength 语义。例如：

```text
Taken together, relative to a neighbor labeled option (A): does not cross the BBB, these feature comparisons are mixed. This neighbor should be treated as low-strength evidence for option (B): crosses the BBB.
```

验收：

- `pair_score` 仍保留，但不再作为 SFT target 中的 confidence。
- per-neighbor middle draft 的 SFT-facing strength 来自 `teacher_aligned_evidence_strength`。
- `displayed_*` / full-term diagnostic fields 只保留在 JSON metadata，不在自然语言 reasoning 里提到 `listed strongest feature signals`、`full set of pairwise feature terms` 这类 runtime tool 不提供的内部结构。
- 对 prior-heavy 样本，例如 BBB_Martins negative-neighbor `pair_score=0.9212` 但 `feature_probability≈0.536`，输出应是 low-strength evidence，而不是 high-confidence support。

### 0.4 修正 middle draft feature 连接词

状态：`[done]`

旧实现使用固定 transition list：

```text
First, ...
Next, ...
Then, ...
After that, ...
Finally, ...
Step 6, ...
Step 7, ...
Step 8, ...
```

问题：

- top-8 local evidence 中第 5 个 feature 远不是真正的 final evidence，却已经写成 `Finally`。
- 第 6-8 个 feature 退化成 `Step N`，像程序化 checklist，不像自然 reasoning。
- 这些词会污染后续 rewrite input，让 SFT target 更容易学到机械 step 风格。

当前修复：

- `src/trim/reasoning/evidence/global_evidence.py`
  - 新增 `_build_ranked_evidence_detail_clause(...)`
  - global middle draft 使用自然 connector。
- `src/trim/reasoning/evidence/local_evidence.py`
  - local per-neighbor middle draft 复用同一 helper。
- 不再出现：
  - `First,`
  - `Next,`
  - `Then,`
  - `After that,`
  - `Finally,`
  - `Step N`

smoke 验收：

- local smoke:
  - `outputs/reasoning_evidence/local_smoke_no_step/BBB_Martins/train/sample_00000.json`
- global smoke:
  - `outputs/reasoning_evidence/global_smoke_no_step/BBB_Martins/train/sample_00000.json`
- check:

```bash
rg 'First,|Next,|Then,|After that,|Finally,|Step [0-9]' \
  outputs/reasoning_evidence/local_smoke_no_step/BBB_Martins/train/sample_00000.json \
  outputs/reasoning_evidence/global_smoke_no_step/BBB_Martins/train/sample_00000.json
```

结果：无命中。

## 阶段 1：重跑 top-8 local evidence

状态：`[done]`

由用户确认阶段 0 代码后执行。阶段 0.1/0.2/0.3 均已完成，现在可以进入阶段 1。

推荐命令：

```bash
/data1/tianang/anaconda3/condabin/conda run -n vllm python scripts/extract_reasoning_evidence_all_tasks.py \
  --evidence-mode local \
  --split train \
  --split valid \
  --split test \
  --prompt-root data/prompts/tdc_cot_user_messages
```

注意：

- 这会覆盖默认 local evidence output root：
  - `outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts`
- 已为 `scripts/extract_reasoning_evidence_all_tasks.py` 增加 `--evidence-mode global|local|both`，默认保持 `both`。本阶段实际使用 `--evidence-mode local`，没有重写 global evidence。
- 重跑后要检查：
  - 每个 task/split 的 manifest 中 `top_term_k == 8`。
  - 随机抽样确认 `top_pair_terms` 长度最多 8。
  - `local_prediction` 与原 top-6 evidence 应该不变，因为 top-k 只影响导出的解释 terms，不影响 pair score / local score。

验收结果：

- root summary：`evidence_mode=local`，`rows=48`，`tasks=16`，`splits=train/valid/test`。
- sample files：`21254`。
- split manifests：`48`。
- 全量 JSON 扫描：
  - `max_top_pair_terms=8`
  - `missing_or_issues=0`
  - `neighbor_count_issues=0`
  - no banned runtime-invisible phrases: `listed strongest` / `full set of pairwise` / `full pairwise` / `with probability <number>`
- strength distribution over all neighbor middle drafts：
  - `feature_evidence_strength`: high `76166` / medium `35835` / low `15523`
  - `teacher_confidence`: high `97872` / medium `21267` / low `8385`

## 阶段 2：per-neighbor rewrite candidate 结构

状态：`[done]`

目标：从当前 local rewrite candidate 中拆出 6 个独立 neighbor candidates。

每个 per-neighbor candidate 保存的信息：

- task metadata：
  - `task`
  - `split`
  - `sample_index`
  - label semantics
  - task playbook
- query metadata：
  - `smiles`
  - `gt_label` 仅作为 metadata 保存，不进入 per-neighbor prompt
- neighbor metadata：
  - `neighbor_index`：1..6，按现有正类 1..3、负类 4..6 编号
  - `neighbor_role`
  - `neighbor_label`
  - `neighbor_similarity`
  - `neighbor_smiles`
- pair teacher fields：
  - `pair_score`
  - `pair_prediction`
  - `pair_prediction_semantics`
  - `teacher_confidence` 仅作为诊断 metadata，不进入自然语言 confidence
  - `feature_evidence_strength`
  - `teacher_aligned_evidence_strength`
  - `teacher_feature_agreement`
- evidence / rewrite source：
  - `middle_draft`：来自 `reasoning_evidence` 的单个 neighbor `local_per_neighbor_middle_draft`。这是 per-neighbor rewrite 的主输入。
  - `tool_visible_observations`：每个 term 的 neighbor/query/delta/value text，不含 contribution / pair score / model 等内部术语。当前只作为 verifier / debug 辅助，不替代 middle draft 主输入。
  - `hidden_teacher_signals`：contribution、rank、supports label 等 teacher signal，只作为内部 metadata；不直接进入 prompt，也不应进入最终自然语言。
  - `middle_draft_reference`：仅保留为 legacy alias，后续 prompt renderer 应直接读取 `middle_draft`。

明确不输入：

- 整体 `local_prediction`
- 其他 neighbor 的 evidence
- final local label
- summary-level conclusion

实现位置：

- `src/trim/reasoning/rewrite/candidates.py`
  - 新增 `local_per_neighbor_rewrite_input`
  - 每条 sample candidate 中包含 `neighbors[0..5]`
  - 每个 neighbor 具有连续 `neighbor_index=1..6`
  - 旧 `local_rewrite_input` 仍保留，避免现有 monolithic local rewrite pipeline 立即断裂。

验收：

- `python -m py_compile src/trim/reasoning/rewrite/candidates.py scripts/build_rewrite_candidates.py`
- BBB_Martins train `sample_00000` smoke：`num_neighbors=6`，每个 neighbor 的 observation/signal 数量匹配，`tool_visible_observations` 不含 `contribution` / `pair score` / `model` / `listed strongest` / `full set of pairwise`。
- BBB_Martins train `sample_00000..00004` multi-sample smoke：`files=5`，`issues=0`。

## 阶段 3：per-neighbor rewrite prompt 和 schema

目标：每个 neighbor 单独生成 evidence-first reasoning。

Prompt 输入：

- `TASK_PLAYBOOK`
- `TASK_DESCRIPTION`
- label semantics
- `neighbor_index`
- `neighbor_similarity`
- `neighbor_label_semantics`
- 单个 neighbor 的 `middle_draft`

不输入：

- 其他 5 个 neighbors
- 整体 `local_prediction`
- `local_summary_middle_draft`
- `pair_score` / teacher posterior probability
- `hidden_teacher_signals`
- `contribution` 结构化列表

说明：

- 这里沿用现有 rewrite pipeline 的主输入思想：LLM rewrite 的对象是 `reasoning_evidence` 里的 middle draft。
- 与旧版不同的是，旧版一次把 6 个 `local_per_neighbor_middle_draft` 全塞给 LLM；新版每次只给一个 neighbor 的 middle draft。
- `tool_visible_observations` 可以在保存的 candidate 中保留，用于自动检查 numeric grounding / feature coverage，但不是 per-neighbor rewrite prompt 的主输入。

强制顺序：

1. `observations`：只允许陈述 raw tool-visible facts。
2. `interpretation`：基于 baseline / delta / task context 解释方向。
3. `neighbor_prediction`：最后才给 pairwise teacher direction。
4. `evidence_strength`：最后输出 `teacher_aligned_evidence_strength`，不输出 teacher posterior confidence。

禁止：

- 在 observations 前或第一两句中出现预测倾向。
- 使用 `supports option A/B`、`leans toward option A/B`、`consistent with final label` 这类过早定向短语。
- 提到 `contribution`、`pair score`、`model`、`draft`、`prompt` 等内部术语。
- 引用没有出现在该 neighbor candidate 中的 feature/value。

建议输出 schema：

```json
{
  "neighbor_index": 1,
  "observations": [
    {
      "feature": "...",
      "neighbor_value": "...",
      "query_value": "...",
      "delta": "...",
      "observation": "..."
    }
  ],
  "reasoning": "...",
  "neighbor_prediction": {
    "option": "A",
    "text": "...",
    "label": 0
  },
  "evidence_strength": "low|medium|high",
  "quality_check": {
    "evidence_before_prediction": true,
    "all_claims_grounded_in_this_neighbor": true,
    "prediction_matches_pair_teacher": true,
    "evidence_strength_matches_teacher_aligned_rule": true,
    "no_meta_references": true
  }
}
```

## 阶段 4：pair confidence 规则

状态：`[superseded by 0.3]`

原计划使用完整 teacher probability：

```text
margin = abs(pair_score - 0.5)
low confidence:    margin <= 0.1
medium confidence: 0.1 < margin <= 0.3
high confidence:   margin > 0.3
```

现在该方案不再用于 reasoning confidence，因为 `pair_score` 混合了 feature evidence 和 EBM intercept / task prior。保留这些字段仅作诊断 metadata：

- `pair_score_class1_probability`
- `pair_prediction_probability`
- `teacher_confidence_margin`
- `teacher_confidence`

reasoning target 使用阶段 0.3 的 conservative teacher-aligned evidence strength：

- `feature_confidence_margin`
- `feature_evidence_strength`
- `teacher_aligned_evidence_strength`

后续可做 ablation：

- teacher probability margin。
- teacher-aligned strength + neighbor similarity。
- teacher-aligned strength + top-term direction agreement。
- calibrated per-task confidence threshold。

## 阶段 5：summary rewrite

输入：

- 6 个 per-neighbor rewrite outputs
- 每个 neighbor 的 similarity
- 每个 neighbor 的 label
- 每个 neighbor 的 pair_prediction
- 每个 neighbor 的 teacher_aligned_evidence_strength
- 每个 neighbor 的 teacher_feature_agreement
- `local_teacher_prediction` / `local_teacher_prediction_semantics`

不再输入：

- 原始 top_pair_terms
- contribution
- monolithic local middle draft
- `local_summary_middle_draft`
- `local_score`
- `s_pos`
- `s_neg`

说明：

- `local_summary_middle_draft` 视为 legacy 产物，不进入新版 summary rewrite。
- Summary 层不再复述或继承 legacy 聚合文案，而是根据 6 个已经重写好的 neighbor-level reasoning、每个 neighbor 与 query 的 similarity、以及每个 neighbor 的 conservative confidence/strength 自己组织聚合推理。
- Summary prompt 可以看到每个 neighbor 的 `neighbor_prediction` 和 `evidence_strength`，但不看 teacher posterior probability。
- Summary prompt 还会看到由 6 个 per-neighbor outputs 计算出的 exact neighbor-level vote count，例如 `option (A): 1 neighbor(s); option (B): 5 neighbor(s)`。这个计数只来自 per-neighbor prediction，不来自 neighbor label。
- `local_teacher_prediction_semantics` 必须作为 summary rewrite 的 target label 输入，保证 summary 最终 prediction 与 local teacher prediction 一致。
- Summary rewrite 不能使用 `local_score`、`s_pos`、`s_neg` 或任何 legacy score-level 聚合数值来解释结论；它只能基于 6 个 per-neighbor reasoning、neighbor similarity、neighbor-level confidence/strength 和 target teacher label 来组织最终聚合推理。

summary 层职责：

- 不重复逐项 descriptor 分析。
- 比较 6 个 neighbor-level conclusions。
- 高 similarity 和 high teacher-aligned evidence strength 的 neighbor 权重更高。
- 显式处理正类邻居和负类邻居之间的冲突。
- 允许部分 neighbor 指向反方向。
- 最后输出 local-level prediction。
- 方向聚合必须按 `neighbor-level prediction` 分组，而不是按 neighbor 自身 label 分组；neighbor label 只能作为参考分子类别背景。
- 必须自然写出 exact vote count；例如 “option (A) has 1 neighbor and option (B) has 5 neighbors”。这是为了防止 summary 把 5:1 误写成 4:2 这类聚合错误。

当前 schema：

```json
{
  "reasoning": "...",
  "local_prediction": {
    "option": "A",
    "text": "...",
    "label": 0
  },
  "quality_check": {
    "uses_all_six_neighbors": true,
    "uses_similarity_and_evidence_strength": true,
    "handles_conflicting_neighbors": true,
    "uses_neighbor_level_predictions_as_votes": true,
    "does_not_add_new_descriptor_evidence": true,
    "preserves_neighbor_predictions": true,
    "preserves_neighbor_strengths": true,
    "final_prediction_matches_required_label": true,
    "no_meta_references": true
  }
}
```

实现与验收：

- Template：`prompt_templates/reasoning_sft/rewrite_local_summary_reasoning.md`
- Renderer：`render_rewrite_prompt(..., mode="local_summary", local_neighbor_outputs=...)`
- Runner：`scripts/run_local_summary_rewrite_examples.py`
- Checker：`scripts/check_local_summary_rewrite_examples.py`
- Batch runner：`scripts/run_local_neighbor_summary_rewrites.py`
  - sample 级并发
  - 每个 sample 内固定顺序：`neighbor_01..06 -> local_summary`
  - 支持 `--mode all|local_neighbor|local_summary`
  - 支持自动重建 candidates，或用 `--skip-candidate-build` 复用已有 candidate JSON
  - 每个 task 写出 `local_neighbor_summary/<split>/<task>/manifest.json`
- 5 task examples：
  - `BBB_Martins train sample_00000`
  - `AMES train sample_00001`
  - `ClinTox train sample_00000`
  - `hERG train sample_00000`
  - `PAMPA_NCATS train sample_00000`
- 统一检查报告：
  - `outputs/reasoning_rewrite_outputs_neighbor_level_no_step/openrouter/openai__gpt-5.4-mini/local_summary/train/five_task_summary_quality_check.json`
  - 当前 no-step 版本：`checked_rows=5`，`issue_count=0`，并检查 exact vote count。

## 阶段 6：SFT message builder 更新

状态：`[done_for_5_task_smoke]`

local-only transcript 的最终 assistant thinking 改为：

1. per-neighbor reasoning 1..6，按编号拼接。
2. local summary reasoning。
3. final answer。

保留外部 tool schema 暂时不变：

- `compare_similar_mols(smiles)` 仍返回 raw neighbor/query/delta properties。

但后续建议同步修复 tool binding：

- 避免模型复制 SMILES。
- 或 runtime 优先绑定当前 prompt query。

当前实现：

- 新增 SFT mode：`local_neighbor_only`
- 输出目录：
  - `data/sft/agent_reasoning_messages/<provider>/<model_slug>/local_neighbor_only/<split>/<task>.jsonl`
- 组装逻辑：
  - sample 必须在 rewrite filter 中 `local_prediction_correct == true`
  - sample 必须存在 6 个完整 per-neighbor rewrite：
    - `outputs/reasoning_rewrite_outputs_neighbor_level_no_step/<provider>/<model_slug>/local_neighbor/<split>/<task>/sample_xxxxx/neighbor_01..06/result.json`
  - sample 必须存在 summary rewrite：
    - `outputs/reasoning_rewrite_outputs_neighbor_level_no_step/<provider>/<model_slug>/local_summary/<split>/<task>/sample_xxxxx/result.json`
  - final assistant thinking 拼接为：
    - `Neighbor 1..6` reasoning
    - `Overall neighbor-based conclusion: ...`
- 入口命令：

```bash
/data1/tianang/anaconda3/condabin/conda run -n vllm python scripts/build_agent_reasoning_sft_messages.py \
  --sft-mode local_neighbor_only \
  --split train \
  --provider openrouter \
  --model openai/gpt-5.4-mini \
  --rewrite-output-root outputs/reasoning_rewrite_outputs_neighbor_level_no_step
```

验收 smoke：

- 已对 5 个 task 生成每 task 1 条 JSONL：
  - `BBB_Martins`
  - `AMES`
  - `ClinTox`
  - `hERG`
  - `PAMPA_NCATS`
- 输出 manifest：
  - `data/sft/agent_reasoning_messages/openrouter/openai__gpt-5.4-mini/local_neighbor_only/train/manifest.json`
- 结构检查：
  - `num_records=5`
  - 每条 messages 为 `user -> assistant(tool_call) -> tool -> assistant(final)`
  - 每条 final thinking 覆盖 `Neighbor 1..6`
  - 每条 source_paths 包含 `local_neighbor_01..06_result_json` 和 `local_summary_result_json`
  - `issue_count=0`

## 阶段 7：verifier / reward

### Rewrite verifier

每条 per-neighbor rewrite 检查：

- 是否所有 numeric values 都出现在 candidate/tool-visible evidence 中。
- 是否所有 top-8 terms 都被覆盖。
- 是否在 observations 前出现 label/prediction 倾向。
- `neighbor_prediction` 是否匹配 `pair_prediction`。
- `evidence_strength` 是否匹配 conservative teacher-aligned strength rule。
- 是否残留 meta terms。

每条 summary rewrite 检查：

- 是否覆盖 6 个 neighbor。
- 是否使用 pair_prediction / teacher_aligned_evidence_strength / teacher_feature_agreement。
- 是否没有重新编 descriptor-level evidence。
- local prediction 是否匹配 local teacher。

### RL reward

后续 RL 不应只用 final answer reward。建议拆分：

- final answer correctness
- valid tool call
- no SMILES mismatch / current query binding
- per-neighbor prediction matches pair teacher
- per-neighbor evidence strength matches conservative teacher-aligned strength
- numeric grounding
- no early prediction before evidence
- no tool-error fallback reasoning reward

## 阶段 8：小规模 ablation

先不要直接重建 16 task 全量。

建议先跑：

- `AMES`
- `BBB_Martins`
- `ClinTox`

每个 task 取：

- train 100-300 条
- valid sampled trace 50-100 条

比较旧版和新版：

- early lock-in rate
- numeric grounding error rate
- per-neighbor prediction match rate
- final local prediction match rate
- answer macro-F1
- tool error 后 reward 率

通过后再批量重建。
