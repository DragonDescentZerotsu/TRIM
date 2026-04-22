# local-only Agent SFT 与 SFT+RL 退化问题分析报告

日期：2026-04-22

## 结论摘要

这次核查后，我认为 RL 后 valid F1 持续下降并不奇怪，主要原因不是“RL 没有利用到 SFT 未见过的数据”，而是当前 SFT 蒸馏目标、trace 行为和 RL 奖励之间还没有形成稳定的 evidence-first 学习闭环。根据 `Paper.md`，TRIM 的核心目标本来就是把 EBM 的结构化 hidden contribution 合理化改写成可监督的分子推理数据，让 LLM 学会基于工具返回的 raw values 做化学类比推理；所以“target reasoning 来自 EBM contribution”本身不是错误。真正的问题是：当前数据和 RL reward 尚未充分约束模型把这种 teacher direction 内化成可检查、证据优先的推理过程。

最关键的发现有五点：

1. local-only SFT 数据确实只来自 `local_prediction_correct == true` 且已有 local rewrite 的样本。代码入口在 `src/trim/reasoning/agent_sft.py`，`local_only` 模式使用 `local_prediction_correct` 过滤，再与已保存的 local rewrite sample index 取交集。
2. 16 个 train task 总样本数是 14,880，其中 local teacher 预测正确 13,814，最终 local-only SFT 写出 13,716 条。也就是说，SFT 没见过的 local-wrong train 样本只有 1,066 条，占 7.2%。这部分“新数据”比例不大，不足以保证 RL 一定提升。
3. SFT 目标 reasoning 确实来自 pairwise EBM 的 hidden contribution 合理化改写，这符合 TRIM 设计；但当前 trace 显示，模型学到的往往还不是“先核对 raw tool values，再形成判断”，而是“尽早确定方向，再把 raw values 组织成支持该方向的解释”。这说明 contribution-to-reasoning 蒸馏目前还存在质量缺口。
4. RL trace 里已经出现 reward 正向强化非 grounded 行为：`step20_groups.json` 有 7 条 tool error rollout，其中 4 条仍 reward=1；`step85_groups.json` 有 24 条 tool error rollout，其中 18 条 reward=1。只要最终答案碰巧对，tool 调用失败、SMILES 复制错误、无 neighbor evidence 的 fallback reasoning 都会被奖励。
5. 用户观察到的“第一个 neighbor 开头就 lock in 方向”不是 RL 才出现的。SFT target 中这个模式已经很常见。按一个保守 heuristic 统计，local-only train SFT 中约 57.2% 的样本在 `Neighbor 1` 前两句内就出现了 `supports / leans / consistent with / option` 这类局部结论性表达。

因此当前更像是：

SFT 阶段已经把 EBM teacher 的方向性信号转成了自然语言，但其中一部分样本呈现出“看完 tool 后快速选择一个方向并为它组织证据”的风格；RL 阶段只有 answer-level binary reward，没有足够的 process reward 或 grounding penalty，于是会继续强化能拿到答案奖励的捷径，包括早锁定、少用证据、tool error 后凭先验猜测。

## local-only SFT 过滤标准核查

相关代码：

- `scripts/build_agent_reasoning_sft_messages.py`
- `src/trim/reasoning/agent_sft.py`

`list_rewritten_sample_indices_for_sft_mode(...)` 对 `local_only` 的逻辑是：

- `rewrite_mode = "local"`
- `correct_field = "local_prediction_correct"`
- 从 `outputs/reasoning_rewrite_filters/<split>/<task>/kept_records.json` 读记录
- 取 `local_prediction_correct == true` 的 `sample_index`
- 再和已经存在的 local rewrite 输出取交集

这确认了 local-only SFT 不是所有 kept records，也不是 `global OR local correct`，而是 local teacher correct。

train split 汇总如下：

| 项 | 数量 |
|---|---:|
| train total | 14,880 |
| local teacher correct | 13,814 |
| local-only SFT records | 13,716 |
| local-correct 但缺 rewrite / 未进入 SFT | 98 |
| local teacher wrong | 1,066 |
| both wrong | 843 |
| global-only correct, local wrong | 223 |

这也说明：如果 RL 确实在所有 train data 上跑，那么相对 SFT，真正新增的是 local-wrong 的 1,066 条，占 7.2%。这部分是 hardest slice，但数量不大，而且没有 teacher reasoning 的 warm start。

## SFT 数据本身的观察结果

### 1. EBM hidden contribution 蒸馏是方法目标，但当前数据没有稳定形成 evidence-first 风格

local rewrite candidate 里有这样的输入：

- 每个 neighbor 的 `top_pair_terms`
- 每个 term 的 `contribution`
- `supports_option`
- `pair_prediction`
- `local_prediction`

例如 `outputs/reasoning_rewrite_candidates/from_filters/train/AMES/sample_00150.json` 中，source note 明确写：

- `heteroatom count ... contribution -0.8877 ... pushes toward option (A)`
- `maximum absolute partial charge ... contribution -0.5966 ... pushes toward option (A)`
- `heavy-atom count ... contribution 1.0374 ... pushes toward option (B)`

根据 `Paper.md`，这正是 TRIM 的方法设计：不要让 LLM 直接从 SMILES 或 raw values 凭空判断，而是先由可解释教师模型完成最脆弱的差异比较，再把这些结构化证据改写成自然语言。也就是说，SFT target 使用 EBM contribution 是合理的，目标是让 LLM 通过监督学习掌握“在某个任务、某个邻居 baseline、某个 delta 范围下，这个 raw value pattern 为什么支持某个标签”。

当前真正值得警惕的是蒸馏是否成功，而不是 contribution 是否应该存在。现有数据表现出一个质量缺口：

- SFT target 解释里的“为什么这个 feature 支持 A/B”来自 hidden EBM contribution，这是 teacher signal。
- 模型实际 rollout 时只能看到 raw values，需要把 teacher signal 学成可迁移的 baseline-aware 化学解释。
- 但这些方向很多是 pairwise EBM 的局部、非单调、baseline-dependent 效应，不是简单全局规则，因此如果 rewrite 文本没有足够清楚地把 baseline、delta、邻居标签和任务语境连接起来，模型就容易学成“答案方向优先”的语言模板。

这正好解释了你看到的 grounding 问题：不是“使用 hidden contribution 这件事错了”，而是当前一部分 SFT target 还没有把 hidden contribution 稳定转化为“可由 raw tool values 支撑的、先证据后结论”的推理范式。换句话说，TRIM 的方向是对的，但当前 local-only SFT 数据里仍有一部分样本更像 teacher-label rationalization，而不是足够强的 evidence-to-label demonstration。

### 2. rewrite 模板显式给 final label，且要求每个 neighbor 解释如何帮助/伤害当前 label

`prompt_templates/reasoning_sft/rewrite_local_reasoning.md` 中有几条会强化 post-hoc rationalization：

- 输入 3 直接给 `Final prediction label`
- hard requirement 10：每个 neighbor paragraph 都要解释这个 comparison 为什么 helps or hurts current label decision
- hard requirement 23：最终预测必须匹配 provided label
- hard requirement 26：保持 original draft direction

这些要求对“把正确 teacher evidence 改写成标签一致的 reasoning”是合理的，也符合 `Paper.md` 中“教师正确性过滤 + 证据到推理文本改写”的目标。但从当前 rollout 看，它们也会带来一个副作用：如果模板没有同时强制 evidence-first 结构，模型容易学到“先对齐 provided label，再选择支持该 label 的证据表达”。这不是方法目标的问题，而是当前 rewrite 约束还需要进一步把“合理化改写”压到更忠实的证据表达上。

### 3. SFT target 中已经存在早期定向和局部自相矛盾

统计结果：

- local-only train SFT：13,716 条
- tool result 成功率：100%
- answer label 总体接近平衡：A=6,913，B=6,803
- 但 task 内部高度不平衡，例如 `ClinTox` A=943/B=45，`SARSCoV2_Vitro_Touret` A=969/B=13，`PAMPA_NCATS` A=151/B=1194
- `Neighbor 1` 前两句出现局部结论性表达的比例约 57.2%

一个具体质量问题例子：

`outputs/reasoning_rewrite_outputs/openrouter/openai__gpt-5.4-mini/local/train/AMES/sample_00150/result.json` 里有一句：

> The query has a slightly higher QED drug-likeness value (0.5148 vs 0.5973 is actually lower in the query...)

这句话内部先说 higher，括号里又承认 actually lower。它来自 rewrite 阶段的语言化错误。类似错误会被 SFT 当成 gold target。

## trace 统计和现象

### 1. SFT valid trace

路径：`outputs/traces/sft_traces_compare_only/step_325`

这里的 `summary.json` 显示每个 task 只保存 sampled trace，不是完整 valid 全量 trace：

- total valid results: 约 2,019
- sampled traces: 50
- sampled reward mean: 0.78
- tool error rate: 0
- answer counts: A=22, B=28

这些 trace 可以看行为形态，但不能直接当完整 valid F1 的充分证据。

SFT valid 的错误样本中已经能看到明显的早锁定和“descriptor 方向被任意解释”的模式。例如 AMES 错例会在 `Neighbor 1` 第一段就写：

- “several features line up with a mutagenic direction”
- “that structural difference is associated with a strong shift toward mutagenicity”
- “higher QED ... associated with a shift toward mutagenicity”

这些说法未必是凭空产生的，因为它们可能来自 SFT 阶段学到的 EBM contribution direction；但从 runtime 可检查性角度看，模型经常没有先说明 raw value、baseline 和 delta 为什么共同支持这个方向，而是直接把 direction 写成结论。这是当前数据最需要改的表现形式。

### 2. RL trace 文件更像 train rollout group，不是 valid trace

路径：`outputs/traces/traces_compare_only_SFT_RL`

需要注意：`step*_groups.json` 里的字段显示 `datasource` 全部是 `*_train`，例如：

- **`AMES_train`**
- `ClinTox_train`
- `hERG_train`
- `SARSCoV2_Vitro_Touret_train`

所以这些文件更像 RL 训练时的 sampled rollout groups，而不是 valid set evaluation trace。它们可以用来诊断 RL 过程在强化什么行为，但不能直接说明 valid F1 的完整变化。

### 3. RL 中 tool error 可以拿正 reward

这是最严重的 RL-specific 问题。

`step20_groups.json`：

- tool error rollout: 7
- reward=1: 4
- reward=0: 3
- tool error 平均 reward: 0.571
- 主要来自 `hERG_train`

`step85_groups.json`：

- tool error rollout: 24
- reward=1: 18
- reward=0: 6
- tool error 平均 reward: 0.75
- 来自 `ClinTox_train`

这些 error 的典型原因是模型 tool call 时没有精确复制 prompt SMILES。例如 prompt 是：

`CCCCCCC[N+](CC)(CC)CCCCc1ccc(Cl)cc1`

模型调用成：

`CCCCCC[N+](CC)(CC)CCCCc1ccc(Cl)cc1`

少了一个碳，tool 返回：

`SMILES ... is not part of task ... compare_similar_mols requires a known task molecule`

但如果最后答案碰巧对，这条 rollout 仍然拿正 reward。到 `step85`，一个 ClinTox group 里 24/24 tool calls 都失败，但 18/24 答案正确，因此全都给了正向学习信号。

这会直接鼓励模型学会：

1. tool 失败也没关系；
2. 没有 neighbor evidence 时可以凭 task prior / label prior / 结构先验猜；
3. 只要 final answer 对，reasoning 是否 grounded 不重要。

### 4. `needle` group 显示的是模式坍缩，不是逐步修正

selected `group_trace_step*_needle.json` 的典型形态是 24 个 rollout 里 23 个给同一个错误答案，只有 1 个对：

| file | label | answer distribution | reward mean |
|---|---:|---:|---:|
| `group_trace_step0_needle.json` | A | B=23, A=1 | 0.0417 |
| `group_trace_step24_needle.json` | A | B=23, A=1 | 0.0417 |
| `group_trace_step60_needle.json` | B | A=23, B=1 | 0.0417 |
| `group_trace_step80_needle.json` | B | A=23, B=1 | 0.0417 |
| `group_trace_step84_needle.json` | A | B=23, A=1 | 0.0417 |

这说明对某些 hard prompts，policy 基本锁在错误答案上。RL 的 sparse binary reward 只在极少数 lucky rollout 上给正反馈，但这些 lucky rollout 的 reasoning 未必更 grounded，可能只是采样到了反方向答案。

### 5. “早锁定”没有随着 step 单调恶化，但一直存在

按 heuristic 统计，`step*_groups.json` 的 early-conclusion rate 大概在 0.35 到 0.63 之间波动，没有看到严格单调上升。selected mixed/needle trace 也类似。

所以我不建议把退化主因表述成“RL 让早锁定越来越严重”。更准确的说法是：

- 早锁定是 SFT target 已经教出来的基础行为；
- RL 没有惩罚这个行为；
- RL 还额外奖励了 tool error fallback、答案先验和非 grounded guessing；
- 最终表现为 valid F1 下降。

## 根因判断

### 根因 1：当前蒸馏还没有稳定把 teacher direction 转成 evidence-first reasoning

local-only SFT 样本只覆盖 local teacher 对的情况。目标 reasoning 来自 EBM contribution direction 和最终标签，这符合 TRIM 的 correct-teacher distillation 设计；但当前数据里，部分 rewrite 更像“为一个正确 teacher label 写自然语言解释”，还不够像“展示如何从 neighbor raw values、baseline 和 delta 推出 label”。

这对 local-correct distribution 有用，但对 local-wrong / hard distribution 不一定有用。RL 加入全部 train 后，新增的恰恰是 local teacher 错的 hard slice；如果 SFT 没把 teacher direction 学成可迁移的 evidence-first 策略，模型在这些样本上就更容易退回到 label prior、早锁定和非 grounded guessing。

### 根因 2：tool schema 要求模型复制 SMILES，太脆弱

当前 `compare_similar_mols(smiles)` 要求模型把 prompt 里的 SMILES 原样传回。长 SMILES、带电 SMILES、立体标记都容易复制错。一旦复制错，tool 只能报错。

这不是模型真正需要解决的问题。active task 和 current query 本来在外层 runtime 里已知，tool 不应该依赖模型重打一遍 SMILES。

### 根因 3：RL reward 只看最终答案，缺少 grounding/process 约束

从 trace 看，tool error 后的正确答案被正常奖励。只要 answer-level reward 是唯一核心信号，RL 就会把任何能提升答案概率的行为都当成好行为，包括：

- tool call 失败后直接猜；
- 开头就选方向；
- 只选择支持当前方向的证据；
- 把 descriptor 解释成当前答案需要的方向；
- 在 hard samples 上依赖 task-level majority prior。

### 根因 4：hard slice 太小且奖励噪声很大

SFT 未见过的 local-wrong train 只有 1,066 条。RL 如果没有 task/label/hardness balancing，很容易被大量 SFT already-correct/easy 样本和 task prior 主导。对 needle samples，24 个 rollout 只有 1 个正 reward，这种极稀疏正样本的 reasoning 质量未必比负样本好。

## 建议修复

### P0：先修 tool 调用协议

把 `compare_similar_mols` 改成不需要模型复制 SMILES。

可选方案：

1. 当前 prompt 只允许一个 query 时，tool schema 改成无参数：`compare_similar_mols()`
2. 或者参数改成 `sample_id` / `query_id`，由环境注入，不让模型生成原始 SMILES
3. 如果必须保留 `smiles`，runtime 应该优先使用当前 prompt 的 canonical query，而不是信任模型传入的字符串

同时 RL reward 里加 hard penalty：

- tool error：直接 reward=0 或额外负分
- required tool 未调用：reward=0
- tool call SMILES 与 prompt SMILES 不一致：reward=0
- tool result 失败后仍输出 confident reasoning：额外 penalty

### P1：保留 EBM contribution 蒸馏目标，但强化 evidence-first rewrite 约束

这里不建议把 EBM contribution 从 SFT 数据生成里移除，因为这正是 TRIM 的方法核心。更合适的修改是：保留 contribution 作为 teacher signal，但让最终 reasoning 更明确地展示“raw tool value -> baseline-aware interpretation -> label evidence”的中间桥梁。

可选增强 1：在内部 rewrite 输入中保留 contribution，但最终文本必须先复述可见 raw evidence。

- 每个 neighbor paragraph 的前半部分只能写 tool-visible facts：neighbor label、similarity、baseline value、query value、delta、FG difference。
- 之后才允许写这些 facts 在该 task / baseline 下为什么支持某个方向。
- 禁止第一句或前两句直接写 `supports option` / `leans toward option` / `consistent with option`。

可选增强 2：增加 rewrite verifier，检查 contribution 是否被忠实转写成 raw-value-grounded reasoning。

- 所有出现的数值必须能在 tool text 或 candidate 中找到。
- 每个方向性解释必须绑定至少一个具体 baseline + query + delta。
- 如果某个 descriptor 是非单调 / range-dependent，必须明确“在这个 neighbor baseline 下”的解释，不能写成全局规则。
- 自动拦截内部矛盾，例如 “higher QED (0.5148 vs 0.5973 is lower)”。

可选增强 3：给 final agent tool 增加轻量 evidence tags，而不是暴露完整 EBM internals。

- 例如只返回 `notable differences` 或 `teacher-highlighted differences`，但不直接返回 `pair score` / `contribution`。
- 这样能减少 LLM 在 36 个属性里盲目找理由，同时仍保留 TRIM “工具可见 raw value + teacher-selected salient evidence”的设定。
- 是否暴露 sign 可以作为 ablation：`raw values only` vs `teacher-highlighted terms` vs `teacher-highlighted terms + direction`。

### P2：RL reward 加 verifier，而不是只看 final answer

建议 reward 至少拆成：

- answer correctness
- valid tool call
- exact query binding / no SMILES mismatch
- all cited numeric values must appear in tool result
- no reasoning after tool error unless explicitly says evidence unavailable and abstains / uses fallback under penalty
- final synthesis must mention both positive and negative neighbor evidence
- first neighbor paragraph不能直接给最终方向

如果只用 answer reward，RL 会继续强化能碰巧答对的非 grounded rollout。

### P3：针对 hard slice 单独做 curriculum / balancing

建议把 train 样本分成三类评估和训练：

- local teacher correct
- global-only correct, local wrong
- both wrong

RL 或 DPO/GRPO 时要显式 balance 这三类，否则 7.2% hard slice 很容易被淹没。

同时对 task 和 label 做 balance，避免 `ClinTox`、`SARSCoV2_Vitro_Touret` 这种极端 label prior 影响 policy。

### P4：重新做 checkpoint eval trace

为了确认 valid F1 下降的机制，建议每个 checkpoint 保存完整 valid trace 或至少固定同一批 stratified valid subset，并记录：

- task
- label
- answer
- reward
- tool_called
- tool_error
- prompt_smiles
- called_smiles
- smiles_exact_match
- answer distribution by task
- macro-F1 by task
- local teacher correct / wrong 分组结果
- early-conclusion heuristic
- numeric grounding violation count

现在 `outputs/traces/traces_compare_only_SFT_RL/step*_groups.json` 更像 train rollout group，不能直接替代 valid eval trace。

## 最可能的解释

当前 pipeline 中，local-only SFT 已经完成了 TRIM 设计中的关键步骤：把 local EBM teacher 的方向性证据改写成 agent reasoning。问题在于，当前改写文本中一部分样本仍偏“teacher label rationalization”，没有稳定表现为“先展示 raw evidence，再做 baseline-aware 判断”。RL 本来希望通过全 train 数据补上 local teacher 错的区域，但新增 hard 数据只占 7.2%，而 reward 又只看 final answer。于是 RL 没有足够信号让模型学会更好的 evidence use，反而会强化下面这些坏策略：

- 复制错 SMILES 也继续猜；
- tool error 也能拿正 reward；
- 第一段 neighbor 就决定方向；
- 后面 reasoning 为这个方向找证据；
- 对 descriptor 方向做 context-free 或自相矛盾解释；
- 在 hard / needle prompts 上坍缩到某个答案先验。

所以 valid F1 下降的主因很可能是 RL reward 与我们真正想要的能力不对齐，而不是 EBM-contribution-to-reasoning 这个数据合成方向本身有问题。先修 tool binding 和 reward grounding，再加强 SFT rewrite 的 evidence-first/verifier 约束，优先级高于继续加 RL step。
