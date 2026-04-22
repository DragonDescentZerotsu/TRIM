# 项目背景与目标说明

## Env Instructions

If you are on `node002` or `node001`, default to the `vllm` conda environment when you need RDKit or the local project dependencies. conda is at: /data1/tianang/anaconda3/condabin/conda

## Current Progress Snapshot

截至目前，**纯 ML 主线（global / pairwise local / hybrid）已经完成**，当前进度如下：

- 已在 `TRIM` 下建立新的项目骨架与脚本入口。
- 已把 clean split data、RDKit/pKa feature、FG feature、similarity cache 接到 `TRIM` 本地路径下，目前大文件先采用 soft link 方式迁移。
- 现在**默认使用最简单的 core pKa + no-fr version**，即：
  - `configs/features/fg_top_level_plus_rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts.json`
  - `configs/features/rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts.json`
  - `data/features/rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts/tdc_no_conflict_labels_salt_removed_unique_smiles_rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts.csv`
  - 对应脚本：`scripts/build_rdkit_pka_core_pka_no_fr_counts.py`
  - 该版本保留全部非 `rdkit__fr_*` 的 RDKit descriptor，但只保留 7 个核心 pKa 字段：
    - `pka__fraction_neutral`
    - `pka__logd_estimate`
    - `pka__num_acidic_sites`
    - `pka__num_basic_sites`
    - `pka__num_ionizable_sites`
    - `pka__most_acidic_pka`
    - `pka__most_basic_pka`
  - `global` 训练现在**默认保留含 NaN 的列**；只有 train 中整列全 NaN 的 feature 才会被丢掉
    - 脚本入口：`scripts/train_global_ebm.py`
    - 显式回到旧行为时使用：`--drop-nan-columns`
- 已跑通 global-only EBM 训练/保存/重放评估流程。
- 已用 `n_jobs=16` 跑完当前 16 个二分类任务的 global EBM，并拿到 valid set `macro_f1` 结果。
- 已完成 `BBB_Martins` 的一轮 pairwise/local valid 实验：`top_k=4`、`strict_cross_scaffold_pairs=False`、`n_jobs=64`，并拿到 pair-level 与 molecule-level 的 local-only / hybrid 指标。
- 已完成 16 个任务的 `FG + RDKit/pKa` 版本 local-only / hybrid valid 汇总评估，并生成总表：
  - `outputs/metrics/local_hybrid_batch_valid_summary_all16_fg_plus_rdkit.csv`
  - `outputs/metrics/local_hybrid_batch_valid_summary_all16_fg_plus_rdkit.json`
- 已完成 16 个任务的 `FG + RDKit/pKa` 版本 local-only / hybrid test 汇总评估，并生成总表：
  - `outputs/metrics/local_hybrid_batch_test_summary_all16_fg_plus_rdkit.csv`
  - `outputs/metrics/local_hybrid_batch_test_summary_all16_fg_plus_rdkit.json`
- 当前最重要的实验结论：
  - valid 上 16 任务平均 `macro_f1`：`global=0.6631`、`local=0.6876`、`hybrid=0.7019`
  - test 上 16 任务平均 `macro_f1`：`global=0.6564`、`local=0.6917`、`hybrid=0.6784`
  - 目前 test 上整体最强的是 `local-only`，不是 `hybrid`
  - `hybrid` 虽然在 test 上仍普遍不差于 global，但没有维持 valid 上那种平均最优的优势
- 已完成 16 个任务的 `FG + RDKit/pKa without rdkit__fr_*` 版本 global/local/hybrid 复现实验，并生成总表：
  - `outputs/metrics/local_hybrid_batch_valid_summary_all16_fg_plus_rdkit_no_fr_counts.csv`
  - `outputs/metrics/local_hybrid_batch_valid_summary_all16_fg_plus_rdkit_no_fr_counts.json`
  - `outputs/metrics/local_hybrid_batch_test_summary_all16_fg_plus_rdkit_no_fr_counts.csv`
  - `outputs/metrics/local_hybrid_batch_test_summary_all16_fg_plus_rdkit_no_fr_counts.json`
- 已完成 16 个任务的 `FG + RDKit/core-pKa without rdkit__fr_*` 版本 global/local/hybrid 复现实验，并生成总表：
  - `outputs/metrics/local_hybrid_batch_valid_summary_all16_fg_plus_rdkit_core_pka_no_fr_counts.csv`
  - `outputs/metrics/local_hybrid_batch_valid_summary_all16_fg_plus_rdkit_core_pka_no_fr_counts.json`
  - `outputs/metrics/local_hybrid_batch_test_summary_all16_fg_plus_rdkit_core_pka_no_fr_counts.csv`
  - `outputs/metrics/local_hybrid_batch_test_summary_all16_fg_plus_rdkit_core_pka_no_fr_counts.json`
- 对 `core-pKa + no-fr` 的补充结论：
  - 这版把总特征从 `95` 压到 `36`，其中 pKa 从 `66` 压到 `7`
  - 在旧的 `drop-any-NaN-columns` global 设定下：
    - valid 上 16 任务平均 `macro_f1`：`global=0.6500`、`local=0.6974`、`hybrid=0.7050`
    - test 上 16 任务平均 `macro_f1`：`global=0.6645`、`local=0.6857`、`hybrid=0.6811`
  - 在当前默认的 `keep-NaN-columns` global 设定下：
    - valid 上 16 任务平均 `macro_f1`：`global=0.6506`
    - test 上 16 任务平均 `macro_f1`：`global=0.6674`
    - 汇总文件：
      - `outputs/metrics/global_only_batch_valid_summary_all16_fg_plus_rdkit_core_pka_no_fr_keep_nan.json`
      - `outputs/metrics/global_only_batch_test_summary_all16_fg_plus_rdkit_core_pka_no_fr_keep_nan.json`
    - 对应默认 global bundle 根目录：
      - `outputs/models/global_ebm/all_tasks_njobs16_parallel_core_pka_no_fr_keep_nan`
  - 相比 `no-fr` 基线：
    - valid 上 `hybrid` 略升，`local` 略升
    - test 上 `hybrid` 略升，`global` 略升，但 `local-only` 有所下降
  - 尽管 `local-only` teacher 质量略掉，但考虑到 feature 数量和后续 agent/tool-calling 的上下文成本，这一版仍作为**默认版本**
- `core-pKa + no-fr` 之外，还额外试过一个 `core-pKa + 4 summary` 的中间版本：
  - `configs/features/fg_top_level_plus_rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_plus4_no_fr_counts.json`
  - 该版本保留 11 个 pKa 字段，但最终**不作为默认**
- `no-fr` 的基础结论（full pKa retained）：
  - valid 上 16 任务平均 `macro_f1`：`global=0.6637`、`local=0.6877`、`hybrid=0.7035`
  - test 上 16 任务平均 `macro_f1`：`global=0.6610`、`local=0.6993`、`hybrid=0.6784`
  - 去掉 `rdkit__fr_*` 后，平均性能**没有下降**；`global` 略升，`local` 在 test 上提升更明显，`hybrid` 基本持平
  - 该版本仍可作为对照基线，但**不再是默认版本**
- 已新增 EBM 可视化函数：
  - `src/trim/evaluation/ebm_visualization.py`
  - `scripts/visualize_ebm_trends.py`
- 这些函数当前用途是：
  - 从 global EBM bundle 导出 top single-molecule feature contribution 曲线
  - 从 pairwise EBM bundle 导出 top `(base, delta)` interaction heatmap
  - 同时生成对应的 summary CSV
- 已对 pairwise/local 路径做过一轮性能重构，后续不要忘记这些优化点已经存在：
  - `src/trim/training/pair_training.py` 现在会先整批加载 query/train feature table，再用向量化 `build_pair_matrix(...)` 一次性生成 pair feature，不再逐 pair 重复 `load(...)`
  - `src/trim/evaluation/pair_eval.py` 现在也是批量构造正/负 pair matrix 后统一打分，不再逐 query 反复拼 DataFrame
  - `src/trim/models/retrieval.py` 现在会缓存每个 `(task, split, query)` 的已合并候选邻居列表，避免重复 parse Morgan / Feature-Morgan similarity
  - `src/trim/features/pair_features.py` 提供了 `coerce_numeric_feature_frame(...)`、`build_pair_column_names(...)`、`build_pair_matrix(...)` 这几个向量化 helper
  - pairwise 训练与评估当前已经带 `tqdm` 进度条，主要在训练集构造、评估 query 遍历，以及多 task 脚本外层循环里
- 已新增批量实验脚本，后续不要忘：
  - `scripts/run_local_hybrid_batch_valid.py`
    - 用已有或新训练的 pairwise bundle 批量跑多任务 valid
    - 支持 task 级并行，并自动汇总 `global/local/hybrid` 指标与 `lambda`
    - 现在默认指向 `FG + RDKit/core-pKa no-fr` 配置与对应输出目录
  - `scripts/run_local_hybrid_batch_test.py`
    - 复用已有 pairwise bundle，批量跑多任务 test
    - 支持为特定任务覆盖 pair bundle 根目录，例如 `BBB_Martins`
    - 现在默认指向 `FG + RDKit/core-pKa no-fr` 配置与对应输出目录
- 已进入 reasoning / tool-calling 阶段，并完成第一批基础设施：
  - 已实现 per-sample `global_decision_evidence`、`global_middle_draft`
  - 已实现 per-neighbor `local_per_neighbor_decision_evidence`、`local_per_neighbor_middle_draft`
  - 已实现 `local_summary_middle_draft`
  - 已完成 16 个任务的 middle draft 结构回归检查，并导出 sample-0 preview 文件
  - 已完成 local pair-EBM per-neighbor feature-term 截断依据实验，结论用于决定每个 neighbor 的 `local_per_neighbor_middle_draft` 写多少条 feature evidence：
    - 新增分析脚本：`scripts/analyze_local_pair_term_coverage.py`
      - 读取已有 pairwise EBM bundle 与训练/验证时保存的 `pos/neg_{split}_pair_predictions.csv`
      - 对 `model.eval_terms(pair_matrix)` 的 feature-term contribution 按 `abs(contribution)` 排序
      - 统计 top-k feature terms 覆盖 `sum(abs(contribution))` 的比例；不把 EBM intercept 算作 feature evidence
    - 已跑完 16 任务 full train / valid 统计：
      - train 输出：`outputs/metrics/local_pair_term_coverage_core_pka_no_fr_counts_train/`
      - valid 输出：`outputs/metrics/local_pair_term_coverage_core_pka_no_fr_counts_valid/`
      - 每个目录下主要文件：
        - `pair_term_coverage_summary.csv`
        - `pair_term_coverage_rows.csv`
        - `top_feature_frequency.csv`
        - `summary.json`
    - 关键结果：
      - train 共 `119040` 个 neighbor-pair，valid 共 `16912` 个 neighbor-pair
      - top-6 feature terms 只覆盖 median absolute contribution mass 约 `45%`
      - top-8 约 `52%`，top-10 约 `58%`，top-15 约 `68%`，top-20 约 `74-75%`
      - 若真要覆盖约 `75%` 的 contribution mass，中位数需要约 `21` 个 feature terms，文本会过长
    - 后续默认决策：
      - 每个 neighbor 的 feature evidence 默认使用 `top_term_k_per_neighbor=8`
      - 这不是“覆盖绝大多数 score”的设定，而是 reasoning 文本长度与 evidence 覆盖之间的折中
      - 注意：已有 `outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts` 中旧导出仍可能是 top-6；改默认后需要重跑 evidence / rewrite 相关产物才能反映 top-8
  - 已经**抛弃 task-specific union 压缩步骤**；原因是当前默认 `core-pKa + no-fr` dense feature 池只有 `36` 个，而大多数任务的 local manifest 已几乎覆盖全部 36 个 dense features，继续做 union 裁剪收益很小
  - 相关脚本包括：
    - `scripts/build_agent_tool_manifests.py`
      - 生成简化版 task manifest，只记录 bundle 路径、label semantics、neighbor/top-k 配置，以及固定的 dense feature 列表
    - `scripts/export_agent_tool_previews.py`
      - 导出 `get_mol_properties_and_fg(SMILES)` 与 `compare_similar_mols(SMILES)` 的真实 preview JSON
  - 相关实现包括：
    - `src/trim/reasoning/evidence/global_evidence.py`
    - `src/trim/reasoning/evidence/local_evidence.py`
    - `src/trim/reasoning/agent_tools/manifests.py`
    - `src/trim/reasoning/agent_tools/tools.py`
  - 已完成 reasoning rewrite phase-1 基础设施：
    - 在 rewrite 前先做 sample-level merge/filter；只有 `global_prediction_correct == true` 或 `local_prediction_correct == true` 的样本才会进入后续 rewrite，`both_wrong` 会在任何 LLM 改写前被筛掉
    - 已新增 rewrite helper 模块：
      - `src/trim/reasoning/rewrite/playbooks.py`
      - `src/trim/reasoning/rewrite/candidates.py`
      - `src/trim/reasoning/rewrite/rendering.py`
    - 已新增 rewrite/build/render 脚本：
      - `scripts/filter_rewrite_samples.py`
        - 对齐 global/local reasoning evidence
        - 仅依据 `global_prediction_correct OR local_prediction_correct` 做 pre-rewrite 过滤
        - 当前已跑通 16 个任务的 `train` split，并输出到 `outputs/reasoning_rewrite_filters/train/<task>/`
        - 根 summary 在 `outputs/reasoning_rewrite_filters/summary.json`
      - `scripts/build_rewrite_candidates.py`
        - 合并 global/local reasoning evidence
        - 默认加载 task playbook；no-playbook ablation 可用 `--allow-missing-playbook` 跳过缺失 playbook 并写入空 playbook 文本
        - 过滤 `both_wrong`
        - 产出 `global_rewrite` / `local_rewrite` / `hybrid_rewrite` 三类最小输入 candidate JSON
      - `scripts/render_rewrite_prompts.py`
        - 从单条 candidate JSON 渲染 filled prompt
        - 支持 `global|local|hybrid` 三种 mode
      - `scripts/render_rewrite_prompts_batch.py`
        - 从 `outputs/reasoning_rewrite_filters/<split>/<task>/kept_records.json` 出发，批量重建 candidates 并渲染 filled prompts
        - 当前 `global/local` 可以直接批量 fill
        - `hybrid` 需要先存在对应的 polished rewrite 输出后才能批量 fill
        - 默认输出根目录是 `outputs/rewrite_prompts/<mode>/<split>/<task>/sample_xxxxx.md`
      - `scripts/run_reasoning_rewrites.py`
        - 从已经 `both_wrong` 过滤过的目录出发，自动构建 candidates、渲染 prompts、调用 LLM、解析 JSON、并保存 rewrite 输出
        - 当前支持两种 backend：
          - `openrouter`：默认走 `https://openrouter.ai/api/v1/chat/completions`
          - `vllm`：默认走本地 OpenAI-compatible 接口 `http://127.0.0.1:8000/v1/chat/completions`
        - 当前支持 `global|local|hybrid|all` 四种运行模式；`all` 会顺序执行 global、local、hybrid
        - `OPENROUTER_API_KEY` 现在默认优先从 repo 根目录 `.env` 读取；若 `.env` 未提供，再回退到 shell 环境变量；显式 `--api-key` 仍然最高优先级
        - 默认数据来源是 `outputs/reasoning_rewrite_filters/<split>/<task>/kept_records.json`
        - 默认 candidate cache 根目录是 `outputs/reasoning_rewrite_candidates/from_filters`
        - 默认 rewrite 输出根目录是 `outputs/reasoning_rewrite_outputs/<provider>/<model_slug>/<mode>/<split>/<task>/`
        - no-playbook ablation 需要显式指定 `--template-root prompt_templates/reasoning_sft_wo_playbook`，建议输出到 `outputs/reasoning_rewrite_outputs_wo_playbook`
        - 已支持 `--allow-missing-playbook`，用于不依赖 `playbooks/<task>.md` 的 rewrite 对照实验
        - 当前正式输出布局已改为 **每个 sample 一个子目录**：
          - `.../<mode>/<split>/<task>/sample_00000/result.json`
          - `.../<mode>/<split>/<task>/sample_00000/prompt.md`
          - `.../<mode>/<split>/<task>/sample_00000/response.txt`
        - `mode=all` 现在已经实跑验证过：会先生成 polished `single-molecule`、再生成 polished `neighbor-comparison`、最后把这两段真正喂给 final integration template 生成 `hybrid`
      - `scripts/fix_local_prompt_neighbor_typo.py`
        - 扫描 local prompt/template artifacts，把误写的 `Nrighbor` 统一替换为 `Neighbor`
        - 当前主要用于修正 `prompt_templates/reasoning_sft` 与已生成的 `outputs/rewrite_prompts` / `outputs/reasoning_rewrite_examples` / `outputs/reasoning_rewrite_outputs`
    - `scripts/extract_reasoning_evidence_all_tasks.py`
        - 从 task manifest index 批量导出 16 个任务的 global/local reasoning evidence
        - 默认按清晰的 `task/split/sample_xxxxx.json` 结构分别写到：
          - `outputs/reasoning_evidence/global/all_tasks_core_pka_no_fr_keep_nan`
          - `outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts`
        - 并在两个根目录下各自写出 `summary.json`
    - 已新增 reasoning rewrite prompt templates：
      - `prompt_templates/reasoning_sft/rewrite_global_reasoning.md`
      - `prompt_templates/reasoning_sft/rewrite_local_reasoning.md`
      - `prompt_templates/reasoning_sft/rewrite_hybrid_reasoning.md`
    - 已新增 no-playbook rewrite ablation templates：
      - `prompt_templates/reasoning_sft_wo_playbook/rewrite_global_reasoning.md`
      - `prompt_templates/reasoning_sft_wo_playbook/rewrite_local_reasoning.md`
      - `prompt_templates/reasoning_sft_wo_playbook/rewrite_hybrid_reasoning.md`
      - 这套模板不注入 `TASK_PLAYBOOK`；`global/local` 允许 LLM 用常见化学/ADMET知识解释已给出的 feature 值，但不能新增证据或改写原 draft 的标签方向
    - 当前 rewrite template 约定：
      - `global_rewrite` 只输入 task playbook 和 `global_middle_draft`
        - 现在 template 的自然语言表述已经去掉 `global` 这种系统内部术语，改成更自然的 `single-molecule analysis notes`
      - `local_rewrite` 输入 task playbook、6 个 neighbor similarity、6 个 `local_per_neighbor_middle_draft`，以及 `local_prediction`
        - 现在 template 的自然语言表述已经去掉 `local` 这种系统内部术语，改成更自然的 `neighbor-based molecule comparison` / `per-neighbor comparison notes`
      - `hybrid_rewrite` 输入已合理化的单分子分析、已合理化的多分子比较分析、以及最终标签语义
        - 现在 template 的自然语言表述已经去掉 `global/local/hybrid reasoning` 这种系统内部术语，改成：
          - `single-molecule analysis`
          - `multi-molecule comparison analysis`
          - `final integration-layer reasoning`
        - `hybrid` template 现在明确强调：这里只写**最后的融合层**，不要重写完整 end-to-end reasoning
      - `local_rewrite` 的当前强化约束是：最终文本必须显式覆盖 `Neighbor 1` 到 `Neighbor 6`，不能漏、不能合并、不能数错 neighbor，而且每个 neighbor 只能使用它自己 draft 中已经给出的证据
      - `local_rewrite` 现在还显式要求：
        - descriptor 的解释必须是 **baseline-aware / range-aware / neighbor-specific**
        - 不能把同一 descriptor 在不同 neighbors 上的方向硬压成全局单调规律
      - `global/local/hybrid` 三类 rewrite 现在都显式禁止在最终文本里出现元话语，例如：
        - `draft`
        - `playbook`
        - `prompt`
        - `input`
        - `instruction`
        - `contribution`
        - `pair score`
      - no-playbook 模板额外强调不要输出分类器内部打分或概率，例如 `predictive score`、`overall score`、`net score`、`confidence`
    - 当前 rewrite 输出 JSON schema 也已统一简化：
      - `global` / `local` / `hybrid` 三类最终文本字段现在都统一使用 `parsed_output.reasoning`
      - 不再继续扩展或依赖 `global_reasoning` / `local_reasoning` / `hybrid_reasoning` 这套旧字段命名
      - `hybrid` 的 quality check 也已改成更自然的命名：
        - `consistent_with_single_molecule_analysis`
        - `consistent_with_multi_molecule_comparison`
        - `final_label_matches_target`
        - `does_not_explicitly_reference_ground_truth`
    - 当前 rewrite pipeline 已新增通用 post-check 机制：
      - 位置：`src/trim/reasoning/rewrite/pipeline.py`
      - 入口：`collect_reasoning_post_checks(...)`
      - 当前对 `global` / `local` / `hybrid` 三种 mode 复用同一套逻辑
      - 主要用于自动检查最终 `reasoning` 里是否还残留元话语
      - 每条 rewrite output 的 `result.json` 里都会保存：
        - `post_checks.reasoning_key`
        - `post_checks.meta_reference_free`
        - `post_checks.meta_terms_found`
        - `post_checks.meta_patterns_found`
      - hard-fail patterns 已加严，会拦截 `model treats/flags/scores`、`note treats/flags`、`comparison treats/scores`、`contribution deems/scores`、`predictive/overall/net score` 等元话语
      - `validate_saved_rewrite_output(...)` 现在会用当前规则重新计算 post-check；旧输出不会因为保存了旧版 `post_checks` 就被误判为可复用
    - 当前 JSON 解析器也做过一轮稳健性增强：
      - 位置：`src/trim/reasoning/rewrite/llm.py`
      - `extract_json_from_response_text(...)` 现在对“模型返回近似 JSON、但字符串内部混入未转义换行/控制字符”的情况有 fallback 修复
      - 已通过测试覆盖，避免后续批量 rewrite 时因为格式小瑕疵直接整条失败
    - 16 个 task 的 repo 内 playbook 已补齐，统一放在 `playbooks/<task>.md`
    - 已新增 playbook research prompt 基础设施：
      - `prompt_templates/playbooks/deepresearch_threshold_playbook_prompt_template.md`
        - 用于为单个 task 生成“36 个默认 RDKit/pKa properties 的文献阈值/范围 + 官能团定性 notes”的 DeepResearch prompt
      - `src/trim/playbook_prompt.py`
        - 统一负责加载默认 36 个 properties、渲染单任务 prompt、以及按 manifest index 批量渲染
      - `scripts/render_playbook_research_prompt.py`
        - 渲染单个 task 的 filled prompt
      - `scripts/render_playbook_research_prompts_batch.py`
        - 从默认 `core_pka_no_fr_counts` manifest index 批量渲染当前 16 个任务
      - 默认输出目录：
        - `outputs/playbook_research_prompts/<task>/deepresearch_threshold_playbook_prompt_filled.md`
        - 根 summary：`outputs/playbook_research_prompts/render_summary.json`
    - 当前 local prompt renderer 已兼容逐邻居展开的最小输入格式，会为 `rewrite_local_reasoning.md` 正确填入：
      - `TASK_DESCRIPTION`
      - `POSITIVE_LABEL_SEMANTICS`
      - `NEGATIVE_LABEL_SEMANTICS`
      - `NEIGHBOR_1..6_SIMILARITIES`
      - `NEIGHBOR_1..6_LOCAL_MIDDLE_DRAFT`
    - `outputs/reasoning_evidence` 下旧的 smoke / preview / check 目录已经清理；当前正式的 full reasoning evidence 输出以这两套目录为准：
      - `outputs/reasoning_evidence/global/all_tasks_core_pka_no_fr_keep_nan`
      - `outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts`
    - 当前正式导出已经覆盖 16 个任务的 `train/valid/test` 三个 split，并按简洁的 `task/split/sample_xxxxx.json` 结构保存，同时在 global/local 两个根目录下各自写出 `summary.json`
    - 当前还另外保存了一套 `BBB_Martins train sample_00000` 的 rewrite demo：
      - candidate: `outputs/reasoning_rewrite_candidates/train_demo/BBB_Martins/sample_00000/sample_00000.json`
      - filled prompts + rewritten outputs: `outputs/reasoning_rewrite_examples/BBB_Martins/train/sample_00000/`
    - 当前还保存了一套从 `both_wrong` 过滤结果直接 batch render 出来的 prompt 示例：
      - `outputs/rewrite_prompts/global/train/BBB_Martins/sample_00000.md`
      - `outputs/rewrite_prompts/local/train/BBB_Martins/sample_00000.md`
      - 当前 `hybrid` 也已经可以用真实的 polished `single-molecule` + polished `neighbor-comparison` reasoning 做 end-to-end 实跑，并输出到：
        - `outputs/reasoning_rewrite_outputs/openrouter/openai__gpt-5.4-mini/hybrid/train/BBB_Martins/sample_00000/result.json`
    - 已新增 task-level user prompt 资产，供后续 agent `messages` 数据直接复用：
      - `src/trim/reasoning/task_user_prompts.py`
        - 统一加载/渲染每个 task 的标准 user message template
      - `scripts/build_task_user_cot_prompts.py`
        - 从旧项目 `TDC_{train,valid,test}_prompts_label_scaffold/*.jsonl` 反推出稳定模板并写入 repo
      - 当前正式 prompt 资产目录：
        - `data/prompts/tdc_cot_user_messages/<task>.json`
        - 根 manifest：`data/prompts/tdc_cot_user_messages/manifest.json`
    - 已新增 agent reasoning SFT messages builder：
      - `src/trim/reasoning/agent_sft.py`
        - 把 task user prompt、tool text 返回、以及 polished `global/local/hybrid` reasoning 组装成最终 OpenAI-style `messages`
        - 第一段 tool-call 过渡语现在是 task-aware 的 `build_global_tool_bridge(task)`，会先写 `We need to predict {brief_task_semantics} for the given SMILES...`，再调用 `get_mol_properties_and_fg`
          - 16 个任务的简短语义统一维护在 `src/trim/reasoning/semantics/task_semantics.py` 的 `BRIEF_TASK_SEMANTICS_BY_TASK`
        - 当前 transcript 结构是：
          - `user`
          - `assistant(tool_call=get_mol_properties_and_fg)`
          - `tool(get_mol_properties_and_fg result)`
          - `assistant(global reasoning + tool_call=compare_similar_mols)`
          - `tool(compare_similar_mols result)`
          - `assistant(local reasoning + hybrid reasoning + final Answer)`
        - 当前 agent SFT builder **不再遍历全 split 全部 sample**，而是只消费 `global/local/hybrid` 三类 rewrite 输出都真实存在的 sample index 交集；因此 `both_wrong` 被过滤掉、或某类 rewrite 尚未成功的 sample，不会再让后续 SFT 构建报错
        - 现在已支持 sample 级**多进程**组装、按 `sample_index` 稳定排序写出、以及边生成边 append JSONL
        - 现在已支持断点续跑：若某个 task 的 JSONL 已存在且前缀有效，会自动跳过已完成样本并从后续 sample 继续写；只有显式 `--overwrite` 才会整 task 重建
        - 当前 task 外层和 sample 内层都带 `tqdm` 进度条
      - `scripts/build_agent_reasoning_sft_messages.py`
        - 按 task 批量导出最终 agent SFT `messages` 数据
        - 已支持 `--sft-mode full|global_only|local_only`
          - `full` 保持原来的 `global -> local -> hybrid` transcript
          - `global_only` 只保留 `global_prediction_correct == true` 且已有 global rewrite 的样本，只调用 `get_mol_properties_and_fg`
          - `local_only` 只保留 `local_prediction_correct == true` 且已有 local rewrite 的样本，只调用 `compare_similar_mols`
        - 已支持 `--max-concurrency`，当前表示每个 task 内用于组装 sample 的 worker 进程数
        - 已支持 `--overwrite`；默认行为是不覆盖已有 JSONL，而是自动续跑
        - 若修改了过渡语、prompt 拼接或输出格式，重建已有 SFT JSONL 时必须显式加 `--overwrite`
      - `scripts/render_agent_message_html.py`
        - 把 agent reasoning SFT JSONL 中的一条 trace 渲染成可读 HTML，便于检查 `messages`、`thinking`、tool call、tool result 和最终 `Answer`
        - 支持 `--sample-index` 指定要可视化的 `sample_index`；不指定时默认渲染 JSONL 里的第一条非空记录
        - 适用于 `full`、`global_only`、`local_only` 三种 SFT trace
        - 示例输出目录：`outputs/visualizations/agent_reasoning_messages/`
      - `scripts/export_agent_reasoning_sft_hf_public.py`
        - 把 agent reasoning SFT JSONL 导出成 Hugging Face 可直接发布的目录布局，默认会从 records 中移除本地 `source_paths`
        - 已支持 `--sft-mode full|global_only|local_only`
        - `global_only` / `local_only` 会分别导出到独立 dataset root，例如：
          - `data/sft/agent_reasoning_messages/hf_public/openrouter/openai__gpt-5.4-mini-global-only`
          - `data/sft/agent_reasoning_messages/hf_public/openrouter/openai__gpt-5.4-mini-local-only`
      - 正式输出目录：
        - `data/sft/agent_reasoning_messages/<provider>/<model_slug>/<split>/<task>.jsonl`
        - 同目录 manifest：`data/sft/agent_reasoning_messages/<provider>/<model_slug>/<split>/manifest.json`
        - ablation 输出会多一层 mode，例如：
          - `data/sft/agent_reasoning_messages/<provider>/<model_slug>/global_only/<split>/<task>.jsonl`
          - `data/sft/agent_reasoning_messages/<provider>/<model_slug>/local_only/<split>/<task>.jsonl`
      - preview 输出目录：
        - `data/sft/agent_reasoning_messages/previews/<provider>/<model_slug>/<split>/<task>/sample_xxxxx.json`
      - 当前已保存一条真实 preview：
        - `data/sft/agent_reasoning_messages/previews/openrouter/openai__gpt-5.4-mini/train/BBB_Martins/sample_00000.json`
    - `scripts/run_reasoning_rewrites.py` / `src/trim/reasoning/rewrite/pipeline.py` 最近又补过一轮可用性增强，后续批量跑时不要忘：
      - 已支持 `max_concurrency`，按 sample 级并发请求 API；单 sample 内仍保持 `global -> local -> hybrid` 顺序
      - 已支持 `max_retries` 与 `retry_delay_s`
      - `--max-samples` 现在会严格使用本次 candidate manifest 里的 `sample_files`，不会被旧 candidate cache 中更多 sample 文件绕过
      - 现在不仅 API/解析异常会重试，`post_checks.meta_reference_free == false` 这类 post-check 不合格也会被当成失败并触发重试
      - 单条 sample 多次失败后不会中断整 task；失败会记录进对应 task 的 rewrite `manifest.json`
      - 当前每个 task 都会显示 `tqdm` 进度条
  - agent tool 侧的当前约定：
    - tool 现在直接返回固定的全部 dense features，即 `36` 个 `core-pKa + no-fr` properties，而不再按任务做 union 白名单裁剪
    - `fg_top_level` 不进 dense properties；global 只返回非 0 functional groups，local 只返回 neighbor/query 的 FG differences
    - `rdkit__fr_*` 也不再进入默认 dense properties；后续若需要，和 FG 一样按稀疏方式单独返回，而不是放进大表
    - manifest 仍然保留，但现在主要只是任务配置文件，不再承担 union 压缩的职责
    - 对于 `most_acidic_pka` / `most_basic_pka` 这类因“没有酸性/碱性位点”而缺失的值，tool/evidence JSON 里不再直接输出 `NaN`
      - 现在统一导出为 `null` + 更自然的文本语义，例如 `no acidic site` / `no basic site`
      - local comparison 中若一侧无定义值，`delta_value` 也会导出为 `null`，并附带自然语言说明，而不是 `NaN`
    - 当前对外给 LLM / agent 真正调用的返回值已经改成**纯文本字符串**，而不是结构化 dict
      - `get_mol_properties_and_fg(smiles)`：
        - 输入只有 `smiles`
        - 输出是 plain text
        - 主体是 36 个 dense properties，每行 `display_name: value`
        - 最后补一段 `functional groups:`，只列非 0 FG 及其计数
        - 对 `strongest acidic pKa` / `strongest basic pKa`，若缺失则输出 `not applicable (no acidic/basic site)`
      - `compare_similar_mols(smiles)`：
        - 输入只有 `smiles`
        - 但这个 `smiles` 必须属于当前 task；tool 会利用 task 上下文去当前 task 的 train split 检索 neighbors
        - 输出是 plain text
        - 开头先给一句 `query / neighbor / delta` 的定义
        - 然后给 `positive neighbors:` 和 `negative neighbors:`
        - 默认是 3 个正类邻居 + 3 个负类邻居，总编号连续为 `Neighbor 1..6`
        - 现在支持 `neighbors_per_label=1|2|3`，用于控制每个 label 返回几个 neighbor；OpenAI schema 里仍然只有 `smiles`，neighbor 数由外层 runtime / script 参数传入
        - 每个 neighbor 下会列 36 个 dense properties，格式是：
          - `display_name: neighbor=... | query=... | delta=...`
        - 最后补 `functional group differences:`
    - 当前仍保留内部 payload builder 供调试与 preview 导出：
      - `src/trim/reasoning/agent_tools/tools.py`
      - `get_mol_properties_and_fg_payload(smiles)`
      - `compare_similar_mols_payload(smiles)`
      - 但正常给 agent 用时，优先使用文本返回版本，不要再让 agent 直接吃内部 payload dict
    - 当前 tool payload cache 也已经正式接上：
      - 默认根目录：`outputs/reasoning_agent_tools/tool_cache`
      - 路径粒度是：
        - `get_mol_properties_and_fg`：`<feature_set_name>/<task>/<cache_namespace>/get_mol_properties_and_fg/<sha1(smiles)>.json`
        - `compare_similar_mols`：`<feature_set_name>/<task>/<cache_namespace>/compare_similar_mols/neighbors_per_label_<1|2|3>/<sha1(smiles)>.json`
      - 其中：
        - `compare_similar_mols` 是**按 task 隔离缓存**，不会跨任务复用
        - 缓存 key 是 `task + smiles + neighbors_per_label`，**不是**按 `train/valid/test` 单独分目录
        - 老的默认 3-neighbor cache 可能没有 `neighbors_per_label_3` 子目录；当前读取逻辑会把它只当作 `neighbors_per_label=3` 的兼容 cache，不会误用于 1/2-neighbor 设置
        - tool lookup 允许外部传入 raw SMILES；若原串不在当前 task 的 processed index/cache 中，runner 会用 RDKit `LargestFragmentChooser(preferOrganic=True)` + canonical isomeric SMILES 回退到当前 processed/cached SMILES
        - 同一 SMILES 若同时出现在多个 split，当前 query metadata 解析优先级是 `valid > test > train`
      - 文件名与中间目录看起来像“乱码”是正常的：
        - 当前 `cache_namespace` 使用 `portable_v3` 逻辑签名，目标是跨机器复用；它主要依赖 task / feature set / manifest / bundle 稳定元数据和 project-relative 路径，不再让 pickle 文件字节 hash 直接决定 namespace
        - 新 cache namespace 根目录会写 `cache_signature.json`，里面保留 bundle / similarity cache 的 size 与 sha256 诊断信息；这些诊断字段用于排查，不作为跨机器复用的主 key
        - 旧 `portable_v2` cache 仍作为兼容 fallback 读取，因此已有 `f55...` / `657...` 这类旧目录不需要手动迁移
        - 最终文件名是 `sha1(smiles)`，避免原始 SMILES 太长或包含不适合做文件名的字符
      - 每个缓存 JSON 内部仍然保留原始 `smiles` 字段，便于排查
    - OpenAI function-calling / Responses API 侧的 schema 与 runtime helper 已单独整理：
      - schema 定义：
        - `src/trim/reasoning/agent_tools/openai_schemas.py`
        - 入口：
          - `build_openai_agent_tool_schemas(task=...)`
          - `OPENAI_AGENT_TOOL_SCHEMAS`
      - 当前推荐的 task-aware runtime helper：
        - `src/trim/reasoning/agent_tools/openai_runtime.py`
        - 入口：
          - `build_openai_tool_runtime(...)`
          - `OpenAIAgentToolRuntime`
      - 兼容入口仍保留：
        - `build_task_bound_openai_tool_bundle(task=...)`
        - `OpenAITaskAgentToolBundle`
      - 当前推荐 helper 的用途是把两件事绑在一起：
        - `runtime.tools`：直接喂给 OpenAI agent 的 tool JSON；schema 里仍然只有 `smiles`
        - `runtime.call_tool(..., task=...)` / `runtime.call_openai_function_call(..., task=...)`：由外层代码手动传入 `task` 后执行 tool call
      - `runtime` 会在进程内按 `task` 缓存 `TaskReasoningAgentTools` runner，所以同一个 task 不会每次调用都重新初始化
      - runner 内部仍默认优先读取已有的 tool payload cache；只有 cache miss 时才会现场计算并回写
    - 最简使用示例：
      - `scripts/example_openai_agent_tools.py`
      - 用法是：
        - 先 `build_openai_tool_runtime()`
        - 把 `runtime.tools` 传给 OpenAI
        - 收到 function call 后，用 `runtime.call_tool(..., task=...)` 或 `runtime.call_openai_function_call(..., task=...)` 执行
      - 该脚本现在还额外支持：
        - `--task`
        - `--smiles`
        - `--skip-schema`
        - `--tool-cache-root`
        - `--neighbors-per-label 1|2|3`
      - 当前 `example` 末尾会自动打印两类 tool 的 cache timing demo，用于快速确认“首次生成缓存”和“第二次直接读缓存”的耗时差
    - 一个最小代码片段如下：
      - ```python
        from trim.reasoning.agent_tools import build_openai_tool_runtime

        runtime = build_openai_tool_runtime()
        tools = runtime.tools

        # 直接执行某个 tool
        text_result = runtime.call_tool(
            "get_mol_properties_and_fg",
            {"smiles": "CC(C)(C)OC(=O)CCCc1ccc(N(CCCl)CCCl)cc1"},
            task="BBB_Martins",
        )

        # 或执行 OpenAI 风格的 function call payload
        tool_call = {
            "type": "function_call",
            "function": {
                "name": "compare_similar_mols",
                "arguments": "{\"smiles\": \"CC(C)(C)OC(=O)CCCc1ccc(N(CCCl)CCCl)cc1\"}",
            },
        }
        local_text = runtime.call_openai_function_call(tool_call, task="BBB_Martins")
        ```
    - 已新增批量预热脚本与 helper，供后续正式跑 agent / SFT 前先把 tool cache 热起来：
      - `src/trim/reasoning/agent_tools/prewarm.py`
        - 入口：
          - `prewarm_agent_tool_cache(...)`
          - `prewarm_agent_tool_cache_for_task(...)`
        - 主要职责：
          - 按 task 扫描 `train/valid/test`
          - 在 task 内对重复 SMILES 去重
          - 复用与 agent SFT builder 类似的 `ProcessPoolExecutor` worker 模式并行预热两个 tool
          - 默认跳过已有缓存；显式 `force_refresh=True` 时重算
      - `scripts/prewarm_agent_tool_cache.py`
        - 用于一条命令预热所有 task 的所有唯一 SMILES
        - 支持 `--neighbors-per-label`，可重复指定要预热的 neighbor 数；默认预热当前默认值
        - 常用命令：
          - `/data1/tianang/anaconda3/envs/vllm/bin/python scripts/prewarm_agent_tool_cache.py --max-concurrency 16`
        - 默认 summary 输出：
          - `outputs/reasoning_agent_tools/tool_cache_prewarm/<feature_set_name>/manifest.json`
    - 对外推荐的最简集成方式仍然是：
      - 直接调用 `build_openai_tool_runtime(...)`
      - 若外部项目要复用，优先把 TRIM 当依赖或 submodule，而不是单独拷走 `tools.py`
      - 因为 runtime 同时依赖：
        - task manifests
        - processed splits
        - similarity cache
        - global / pos / neg model bundles
- 当前状态判断：
  - **纯 ML 主线任务已经完成**
  - **以后默认 feature 版本是 core-pKa no-fr counts**
  - 后续若继续推进，重点应转到 **reasoning 重写 / agent tool calling**，或做更细的补充分析（例如 AD / similarity 分桶），而不是继续补基础的 pure ML pipeline

## 1. 项目背景

我们当前做的是 **TDC 上分子分类任务（尤其是类似 BBB 这样的 ADMET 分类任务）** 的纯 ML 系统与后续 reasoning 系统的基础设施建设。

目前已经完成并验证过一部分工作：

- **global 单分子 EBM** 已经实现并测试过。
- 旧代码目录在：`/data1/tianang/Projects/Intern-S1/train/tree`
- 这个旧目录原本是为了图方便放在一个更大的项目下面，但现在由于接下来要增加很多新内容（pairwise EBM、邻居检索、聚合评估、后续 reasoning 重写等），**需要单独新开一个整洁的新项目目录** 来重新组织代码。

本阶段的工作重点还不是 reasoning 文本生成，而是先把整个 **纯 ML 系统** 做扎实，并明确验证：

1. **global 单分子 EBM** 的表现（已有代码，可迁移复用）
2. **两个 pairwise EBM（正类邻居 / 负类邻居）** 的表现
3. **pairwise local 模块单独作为 molecule-level classifier 的表现**
4. **global EBM + pairwise local 模块融合后的整体 pure ML performance**

只有当以上纯 ML 系统效果不错、机制稳定、评估清楚之后，我们才推进到下一阶段：  
**把 ML 模型重写成 reasoning process / reasoning text。**

---

## 2. 为什么要做这个项目

我们的最终目标不是只要一个会分类的模型，而是要构建一个：

- 有较强分类性能
- 结构清晰
- 可解释
- 便于后续改写为 reasoning process 的系统

### 当前动机

我们之前已经有一个全局的单分子 EBM。它的优势是：

- 输入是单分子 descriptor / feature
- 可解释性强
- 可以直接看 feature contribution
- 容易作为后续 reasoning 的“全局先验锚点”

但我们观察到：
- KNN / 邻居类方法在一些 TDC 分类任务上效果也很好
- 这说明“局部案例证据 / analog evidence”是有价值的

问题在于：
- KNN 本身不像 tree/EBM 那样天然给出可重写的 reasoning draft
- 所以我们不能直接把 KNN 变成 reasoning teacher
- 正确做法是：**把“邻居比较”也转成一个可解释的 pairwise 模型**

于是形成了现在的系统设计：

- **global 单分子 EBM**：给全局先验
- **两个 pairwise EBM**：学习“query 相对正类邻居 / 负类邻居的局部变化方向”
- **邻居检索 + 聚合模块**：把多个邻居的局部判断合成为 molecule-level local score
- **融合模块**：把 global score 和 local score 融合成最终纯 ML 预测

---

## 3. 当前阶段的核心任务范围

### 当前阶段要做的
1. 从旧目录迁移 / 参考实现已有的 **global 单分子 EBM**
2. 新建独立项目目录，整理代码结构
3. 实现 **两个分开的 pairwise EBM**
4. 实现 **neighbor retrieval / pair construction / molecule-level aggregation**
5. 实现 **pair-level 与 molecule-level 的评估协议**
6. 实现 **global + local 融合后的评估**
7. 产出完整实验结果与可复现实验脚本

### 当前阶段不要做的
1. 不要实现 LLM reasoning 文本生成
2. 不要实现基于 EBM 曲线的文本压缩器
3. 不要做 chain-of-thought 数据生成
4. 不要过早优化 prompts / reasoning templates

---

## 4. 数据与划分约束（非常重要）

### Scaffold split 是核心前提
当前任务使用的是 **scaffold split**，这会直接影响 pairwise 设计和评估逻辑。

这意味着：

- train / valid / test 的 scaffold 是分开的
- test query 在 train 中通常拿不到 same-scaffold 邻居
- 所以整个 pairwise 系统必须从设计上适应 **cross-scaffold generalization**

### 设计后果
因此：

1. **不要依赖 same-scaffold 邻居**
2. **不要使用 same-scaffold bonus**
3. pairwise 邻居检索与训练样本构造，原则上应尽量偏向 **cross-scaffold pairs**
4. similarity 的角色主要是：
   - 邻居检索
   - 邻居过滤
   - 分数聚合权重
   - confidence / applicability domain 分析  
   **而不是一开始就作为 EBM 输入特征**

---

## 5. 系统总体设计

# 5.1 Global 模块（已有基础，可迁移）
这是已有的单分子 EBM 模块。

### 作用
- 输入：单个分子的 descriptor / feature
- 输出：molecule-level classification score / probability
- 用作全局先验 `S_global(x)`

### 状态
- 旧版本已经实现并测试过
- 旧代码参考目录：`/data1/tianang/Projects/Intern-S1/train/tree`

### 当前要求
- 不要求重新发明
- 允许直接参考或迁移旧目录的实现
- 迁移后要适配新项目结构与配置方式
- 在新项目中应作为一个规范模块存在，而不是散落脚本

---

# 5.2 Pairwise 模块（本阶段新增重点）
我们要训练 **两个分开的 pairwise EBM**：

1. **pair EBM for positive neighbors**
2. **pair EBM for negative neighbors**

### 为什么拆成两个模型
不要把 neighbor label 作为一个普通输入特征塞进统一模型。  
更合理的是拆成两个共享模型：

- 正类邻居模型：学习“相对一个正类邻居，query 是否仍倾向正类”
- 负类邻居模型：学习“相对一个负类邻居，query 是否已经摆脱负类特征，从而倾向正类”

这样语义更干净，可解释性更强，后续 reasoning 也更自然。

---

## 6. Pairwise EBM 的输入形式（非常关键）

### 6.1 基本形式
对于每个选中的 descriptor `i`，构造两列：

- `base_i = φ_i(n)`：neighbor 的该特征值
- `delta_i = φ_i(x) - φ_i(n)`：query 相对 neighbor 的变化量

其中：

- `x` = query molecule
- `n` = neighbor molecule

### 6.2 为什么不是只用 delta
只用 `delta` 不够，因为同样的变化发生在不同绝对区间，含义不同。

例如：
- TPSA 从 90 降到 70
- TPSA 从 40 降到 20

虽然 `delta` 都是 -20，但化学意义不一样。

所以 pairwise 模型必须看到：
- 邻居的 baseline context（`base_i`）
- query 相对它的变化（`delta_i`）

### 6.3 为什么不是直接用 `[x, n, x-n]`
`[φ(x), φ(n), φ(x)-φ(n)]` 信息虽全，但：
- 冗余较多
- 维度太长
- 可解释性不如 `base + delta`
- 不利于后续把每个特征压成局部 effect

所以目前明确采用：

- **`[φ_i(n), φ_i(x)-φ_i(n)]`**

---

## 7. Pairwise EBM 的模型结构要求

### 7.1 仅保留 interaction，不要 mains
pairwise EBM 的核心形式应该是：

`score(x, n) = b + Σ_i f_i(base_i, delta_i)`

其中：
- `f_i` 是该 feature 的二维交互函数
- **不允许 main effects**
- 不允许跨 feature 的交互

也就是说：
- 允许 `(TPSA_base, TPSA_delta)` 的 interaction
- 允许 `(logP_base, logP_delta)` 的 interaction
- ...
- **不允许** `(TPSA_base, logP_delta)` 这种跨特征交互
- **不允许** 单独 `TPSA_base` 的 main
- **不允许** 单独 `TPSA_delta` 的 main

### 7.2 使用 InterpretML EBM
可使用 InterpretML 的 EBM 来实现此结构，但需要在特征工程阶段先生成这些列，然后显式指定 interactions，只保留这些 pair-specific interactions。

### 7.3 similarity 初版不进模型
初版 pairwise EBM 中：
- **不要把 similarity 放进输入特征**
- 不要做 `sim × descriptor` 或 `sim × delta` 交互
- similarity 先只用于：
  - 邻居检索
  - 邻居过滤
  - 聚合加权
  - confidence / applicability domain 分析

如后续实验发现有必要，再考虑给每个 pairwise EBM 增加一个单独的 `g(sim)` 小项，但不是现在第一版要做的内容。

---

## 8. Pairwise 训练数据怎么构造

### 8.1 训练样本来源
pairwise EBM 的训练数据只能从 **train split** 内构造。

### 8.2 正类邻居模型的数据
对于一个 anchor `x`，如果要构造给正类邻居模型的训练 pair：
- 选择若干个 **正类 train neighbors**
- 每个 pair 的输入是 `(x, n_pos)` 的 pairwise 特征
- 每个 pair 的目标仍然是 `y_x`

### 8.3 负类邻居模型的数据
对于一个 anchor `x`，如果要构造给负类邻居模型的训练 pair：
- 选择若干个 **负类 train neighbors**
- 每个 pair 的输入是 `(x, n_neg)` 的 pairwise 特征
- 每个 pair 的目标仍然是 `y_x`

### 8.4 cross-scaffold 优先
由于我们最终评估是 scaffold split，训练 pair 时要尽量模拟 test-time 场景：

- 邻居优先从 **不同 scaffold** 的 train molecules 中找
- 避免过度依赖 same-scaffold pairs
- 最好能支持配置：
  - `strict_cross_scaffold_pairs = true/false`

默认推荐：**优先使用 cross-scaffold pairs**

### 8.5 邻居采样建议
初版推荐对每个 anchor：
- 正类邻居：top-k positive train neighbors
- 负类邻居：top-k negative train neighbors

其中 top-k 是基于某种 molecule similarity（例如 ECFP/Tanimoto）得到的局部邻域。
我在之前的项目里面已经实现过 KNN 相关的代码在：/data1/tianang/Projects/Intern-S1/train/KNN  
请你直接使用那部分代码里面使用的已经cache好的similarity data，并且把对应的cache好的数据还有生成那些数据的相关代码都移植到我们现在这个项目里面来。使得这个项目成为一个self-contain的项目。可能需要移植过来的代码在这里：/data1/tianang/Projects/Intern-S1/DataPrepare/TDC_mol_fingerprints，尤其是其中的 compute_fingerprints_and_similarities.py。

初版先做：
- `k_pos = 3`
- `k_neg = 3`

对于 top-k 的生成代码，或许可以参考：/data1/tianang/Projects/Intern-S1/DataPrepare/TDC_prepended/generate_knn_prompts.py

---

## 9. 邻居检索模块设计

需要有一个统一的邻居检索模块。

### 输入
- query molecule
- candidate pool（train split）
- class filter（positive / negative）
- scaffold restriction（是否排除 same-scaffold）
- similarity metric
- top-k

### 输出
- 一个有序邻居列表
- 每个邻居带：
  - molecule id
  - label
  - similarity
  - scaffold
  - 必要的 descriptor/feature

### 初版 similarity  
尽量移植我前面说的代码和数据，尤其是similarity都有现成的应该不用重新计算，两种similarity在：
- /data1/tianang/Projects/Intern-S1/DataPrepare/TDC_mol_fingerprints/Feature_Morgan_similarity
- /data1/tianang/Projects/Intern-S1/DataPrepare/TDC_mol_fingerprints/Morgan_similarity

怎么混合使用这两个 similarity 请参考：/data1/tianang/Projects/Intern-S1/train/KNN/eval_knn.py

---

## 10. Pairwise EBM 的输出语义

建议两个 pairwise EBM 都统一输出：

- `P(y_x = positive | pair(x, n))`
或等价的 positive-class score

这样做的好处是：
- 正类邻居模型高分 = 支持 query 为正类
- 负类邻居模型高分 = 表示 query 相对负类邻居已经脱离负类模式，因此仍支持正类

统一成 positive score 后，后续聚合更简单。

---

## 11. Molecule-level local aggregation（非常关键）

pairwise EBM 本身是对单个 pair 打分。  
但最终我们要给 query molecule 一个 molecule-level local score，所以必须做邻居聚合。

### 11.1 正类邻居聚合
对于 query `x` 的正类邻居集合 `N_pos(x)`：

`S_pos(x) = similarity weighted average over s_pos(x, n)`  

其中：
- `s_pos(x, n)` = 正类邻居模型对 pair `(x, n)` 的输出分数

### 11.2 负类邻居聚合
对于 query `x` 的负类邻居集合 `N_neg(x)`：

`S_neg(x) = similarity weighted average over s_neg(x, n)`

### 11.3 local score
最简单初版：

`S_local(x) = similarity weighted average over s_neg(x, n) and s_pos(x, n)`

---

## 12. Global + Local 融合模块

在有了：
- `S_global(x)`：global 单分子 EBM 分数
- `S_local(x)`：pairwise 模块聚合后的 local 分数

之后，构建融合分数：

`S_final(x) = λ * S_global(x) + (1 - λ) * S_local(x)`

### 要求
- `λ` 应可配置
- `λ` 的选择应在 valid set 上调
- 不要在 test 上调参

### 需要支持的三种系统
实验中至少要支持以下三种系统的完整评估：

1. **Global-only**
2. **Local-only**
3. **Global + Local hybrid**

---

## 13. 评估协议（必须严格区分两层）

# 13.1 Pair-level evaluation（辅助）
这是检查 pairwise EBM 是否是合格 teacher。

### 做法
对于 valid/test 中的每个 query：
- 只从 train split 检索邻居
- 构造 pair
- 跑 pairwise EBM
- pair 的标签仍然是 query 的标签 `y_x`

### 指标
pair-level 主要建议看：
- AUROC
- log loss
- Brier score

不建议把 pair-level F1 作为主指标，因为 pair 不是最终任务单位。

---

# 13.2 Molecule-level evaluation（主指标）
这是最终最重要的评估。

### 做法
对于 valid/test 中每个 query molecule：
1. 从 train split 检索正类邻居
2. 从 train split 检索负类邻居
3. 跑两个 pairwise EBM
4. 聚合成 `S_local(x)`
5. 若需要，再和 `S_global(x)` 融合成 `S_final(x)`
6. 对 query molecule 给出最终预测

### 主指标
与原来的 molecule classifier 一样，在 molecule level 上算：

- macro F1, 参考 /data1/tianang/Projects/Intern-S1/train/tree 里面的做法
- AUROC
- balanced accuracy
- Brier score 或 log loss

其中：
- macro F1：与已有习惯保持一致
- AUROC：看 threshold-free 判别能力
- balanced accuracy：适合不平衡数据
- Brier / log loss：看分数质量与可校准性

### 对比对象
至少需要比较：
1. global-only
2. local-only
3. hybrid

---

## 14. Valid / Test 的正确使用方式

### Train
- 训练 global EBM
- 训练两个 pairwise EBM

### Valid
- 调 λ
- 做模型选择
- 做 ablation
- 可选：做 calibration

### Test
- 使用在 valid 上选好的配置
- 仅做最终评估
- 不可再调参

---

## 15. Applicability Domain / Similarity 分析（建议实现）
由于是 scaffold split，neighbor-based local module 的可靠性会明显依赖 query 到 train chemical space 的距离。

建议增加一个分析模块，按 query 的邻域支持强弱分桶分析性能。

### 可分析的量
例如：
- 最大 similarity
- top-k similarity 平均值
- 是否超过最小相似度阈值
- 正负邻居相似度分布

### 分桶分析
将 valid/test 中 query 分成：
- high neighbor support
- medium neighbor support
- low neighbor support

然后分别报告：
- macro F1
- AUROC
- balanced accuracy

这有助于判断：
- local module 是不是只在“有足够邻域支持”时有效
- scaffold split 下它的适用域在哪里

---

## 16. 推荐的新项目目录结构

以下是建议的新项目目录结构，Codex 可以按此思路组织，但具体文件名可在不破坏清晰性的前提下微调。

    new_project_root/
    ├── AGENTS.md
    ├── README.md
    ├── pyproject.toml / requirements.txt
    ├── configs/
    │   ├── data/
    │   ├── global_ebm/
    │   ├── pair_ebm/
    │   ├── experiments/
    │   └── evaluation/
    ├── data/ (原本使用的处理好的data在/data1/tianang/Projects/Intern-S1/DataPrepare/TDC_no_conflict_labels_salt_removed，可以移植过来)
    │   ├── raw/
    │   ├── processed/
    │   └── splits/
    ├── src/
    │   ├── data/
    │   │   ├── dataset_loading.py
    │   │   ├── split_utils.py
    │   │   ├── scaffold_utils.py
    │   │   └── feature_builders.py
    │   ├── features/
    │   │   ├── molecular_descriptors.py
    │   │   ├── fingerprints.py
    │   │   └── pair_features.py
    │   ├── models/
    │   │   ├── global_ebm.py
    │   │   ├── pair_ebm.py
    │   │   ├── retrieval.py
    │   │   ├── aggregation.py
    │   │   └── fusion.py
    │   ├── training/
    │   │   ├── train_global.py
    │   │   ├── train_pair_pos.py
    │   │   ├── train_pair_neg.py
    │   │   └── train_pair_shared_utils.py
    │   ├── evaluation/
    │   │   ├── evaluate_pair_level.py
    │   │   ├── evaluate_molecule_level.py
    │   │   ├── metrics.py
    │   │   ├── calibration.py
    │   │   └── ad_analysis.py
    │   ├── pipelines/
    │   │   ├── run_global_only.py
    │   │   ├── run_local_only.py
    │   │   ├── run_hybrid.py
    │   │   └── full_experiment.py
    │   └── utils/
    │       ├── io.py
    │       ├── logging.py
    │       ├── seed.py
    │       └── config.py
    ├── scripts/
    │   ├── prepare_data.sh
    │   ├── train_global.sh
    │   ├── train_pair_models.sh
    │   ├── run_valid_eval.sh
    │   └── run_test_eval.sh
    ├── outputs/
    │   ├── models/
    │   ├── predictions/
    │   ├── metrics/
    │   ├── plots/
    │   └── logs/
    └── notebooks/
        ├── sanity_checks.ipynb
        └── result_analysis.ipynb

---

## 17. 对 Codex 的具体实现要求

### 17.1 先做最小可运行版本（MVP）
不要一开始把所有花哨功能都做进去。  
优先顺序：

1. 迁移/复用 global 单分子 EBM
2. 实现 pairwise feature builder
3. 实现两个 pairwise EBM
4. 实现 train-only neighbor retrieval
5. 实现 valid/test 上 molecule-level local evaluation
6. 实现 hybrid evaluation
7. 跑通完整实验

### 17.2 优先保证可复现
必须保证：
- 固定随机种子
- 配置可保存
- 模型、预测结果、指标都可落盘
- 同一配置可稳定复现

### 17.3 不要过度抽象
代码需要整洁，但不要一上来过度工程化。  
重点是：
- 路径清晰
- 模块职责明确
- 实验可复现
- 后续便于扩展 reasoning 模块

---

## 18. 推荐的实验顺序

### Phase 1：迁移 global EBM
目标：
- 将旧目录中的 global 单分子 EBM 整理迁移到新项目中
- 把需要用的之前已经cache好的 feature 文件都移植过来，分别在 /data1/tianang/Projects/Intern-S1/DataPrepare/mol_features_for_tree/rdkit_descriptors_and_pka_easy_to_NLP_Lv1 还有 /data1/tianang/Projects/AccFG/FG_feature_extraction/extracted_FG_features/tdc_no_conflict_labels_salt_removed_unique_smiles_top_level_fg_vectors.csv 两个地方。怎么使用也是参考 /data1/tianang/Projects/Intern-S1/train/tree 里面的代码
- 在新项目结构下复现其 valid/test 表现

状态：
- **已完成**
- 已在 `TRIM` 新项目结构下跑通 global EBM。
- 已完成当前 16 个任务、`n_jobs=16` 的 global EBM valid 评估。
- 后续这里若有工作，主要应是为 local/hybrid 流程补接口，而不是重新做 global 迁移。

### Phase 2：实现 pairwise 数据构造
目标：
- 能从 train split 构建 pairwise 训练数据
- 能控制正类邻居 / 负类邻居
- 能控制 cross-scaffold 邻居限制
- 能生成 `[base_i, delta_i]` 形式的 pair 特征

状态：
- **已完成**
- 已支持 train-only retrieval、正负邻居分开构造、same-scaffold 开关、批量 pair feature 生成。

### Phase 3：训练两个 pairwise EBM
目标：
- 训练 `pair_EBM_pos`
- 训练 `pair_EBM_neg`
- 不使用 main features
- 仅使用 `(base_i, delta_i)` 的 interaction

状态：
- **已完成**
- 已在 16 个任务上跑通 pairwise 训练，并用于后续 valid/test molecule-level evaluation。

### Phase 4：local-only molecule classifier
目标：
- 对 valid/test query 只从 train 检索邻居
- 跑两个 pairwise EBM
- 聚合得到 `S_local`
- 报 molecule-level performance

状态：
- **已完成**
- 已完成 16 个任务的 valid/test local-only molecule-level 评估与总表汇总。

### Phase 5：global + local hybrid
目标：
- 融合 `S_global` 和 `S_local`
- 在 valid 上调 λ
- 在 test 上报告最终结果
- 与 global-only / local-only 对比

状态：
- **已完成**
- 已完成 16 个任务的 valid/test hybrid 评估，并保存每个任务的 valid-selected `lambda`。

### Phase 6：分析与保障
目标：
- 做 pair-level teacher quality 分析
- 做 similarity / applicability domain 分桶分析
- 明确 local 模块是否真正带来增益

补充进度：
- 已经可以直接从现有 bundle 生成 global / pairwise 的解释性可视化。
- pairwise 可视化当前采用 **2D heatmap**，因为模型项是 `f_i(base_i, delta_i)`，不是单变量曲线。

状态：
- **核心结论已完成**
- 已经通过 16 任务 valid/test 对比明确看到了 `global-only / local-only / hybrid` 的整体增益格局。
- `similarity / AD` 分桶分析若后续需要，可以作为补充研究项，但不影响“纯 ML 主线已完成”的判断。

---

## 19. 本阶段的成功标准

只有满足以下条件，才说明本阶段完成得比较好：

### 工程层面
1. 新项目目录整洁且可独立运行
2. global EBM 已成功迁移或复现
3. 两个 pairwise EBM 可以成功训练
4. local-only pipeline 可以对 query molecule 输出预测
5. hybrid pipeline 可以输出预测并完成评估

当前状态：
- 第 1 条：**已基本完成**
- 第 2 条：**已完成**
- 第 3-5 条：**已完成**

### 实验层面
1. 能清楚报告 pair-level 与 molecule-level 两层指标
2. 能清楚比较 global-only / local-only / hybrid
3. 能说明 scaffold split 下 local 模块是否真的有帮助
4. 能说明 local 模块在哪些 similarity / AD 区间更可靠

当前状态：
- 第 1-3 条：**已完成**
- 第 4 条：**可选补充项，当前尚未系统做分桶报告，但不影响纯 ML 主线完成**

### 研究层面
1. 如果 local-only 明显太弱，要知道是检索问题、pair teacher 问题还是聚合问题
2. 如果 hybrid 提升明显，说明这条路线值得继续推进到 reasoning
3. 如果 hybrid 不提升，也要有足够的分析结论来指导下一步

---

## 20. 暂不做 reasoning，但代码设计要为后续预留接口

虽然当前阶段不实现 reasoning 文本，但请在设计时预留以下扩展空间：

### 未来会需要的能力
1. 从 global EBM 中抽每个 query 的 top feature contributions
2. 从 pairwise EBM 中抽每个 pair 的 top local effect terms
3. 从多个邻居中汇总 decisive local evidence
4. 将这些 evidence object 转成后续的 reasoning DSL / text

### 因此当前就建议：
- 模型推理函数除了输出最终 score 外，尽量也支持输出 feature-level contributions
- 评估/预测结果落盘时保留中间分数
- 以后 reasoning 模块可以直接消费这些结构化中间结果

但请注意：  
**本阶段不要真正实现 reasoning 文本生成。**

---

## 21. 给 Codex 的最终执行指令摘要

请按以下逻辑实现本项目：

1. 新建一个整洁的新项目目录，不要继续在旧大项目目录中堆叠新功能。
2. 从 `/data1/tianang/Projects/Intern-S1/train/tree` 参考或迁移已有的 global 单分子 EBM 实现。
3. 在新项目中实现两个分开的 pairwise EBM：
   - 一个对应正类邻居
   - 一个对应负类邻居
4. pairwise EBM 输入采用 `[base_i, delta_i]`：
   - `base_i = φ_i(neighbor)`
   - `delta_i = φ_i(query) - φ_i(neighbor)`
5. pairwise EBM 中：
   - 不使用任何 main features
   - 只保留 `(base_i, delta_i)` 这种同 feature 内部交互
   - 不做跨 feature 交互
6. scaffold split 是核心前提：
   - 训练 pairwise 数据时尽量使用 cross-scaffold pairs
   - valid/test 检索邻居时只能从 train split 检索
7. similarity 初版只用于：
   - 邻居检索
   - 邻居过滤
   - 可选的聚合权重 / AD 分析  
   不要先放进 pairwise EBM 本体。
8. 实现三套 molecule-level 系统并评估：
   - global-only
   - local-only
   - global + local hybrid
9. 指标至少包括：
   - macro F1
   - AUROC
   - balanced accuracy
   - Brier score 或 log loss
10. pairwise EBM 本身还要做 pair-level 辅助评估：
   - AUROC
   - log loss
   - Brier score
11. 只有纯 ML 系统效果与机制都清楚后，才推进到下一阶段 reasoning 重写。

---
## 22. 一个简明版本的研究目标总结（可放在 README 开头）

本项目旨在为 TDC 上的 scaffold-split 分子分类任务构建一个可解释、可扩展、便于后续重写为 reasoning process 的纯 ML 系统。系统由两部分组成：  
第一部分是已有的 global 单分子 EBM，用于提供全局 descriptor-level 先验；  
第二部分是新增的两个 pairwise EBM，用于学习 query molecule 相对正类邻居与负类邻居的局部变化方向，并通过 train-only 邻居检索与分数聚合形成 molecule-level local evidence。  
本阶段的重点是验证 global-only、local-only 以及 global+local hybrid 三套系统在 scaffold split 下的性能与稳定性，在此基础上再推进到后续的 reasoning 文本重写。

---

## 23. 下一阶段：Reasoning / CoT 重写（将纯 ML 决策过程转成高质量 SFT data）

### 23.1 当前阶段切换的背景

截至目前，**纯 ML 主线已经完成**：

- global 单分子 EBM 已完成并验证
- 两个 pairwise local EBM 已完成并验证
- local-only / hybrid 的 molecule-level 评估已经完成
- 16 个任务的 valid / test 结果已汇总
- 当前结论是：纯 ML pipeline 已经基本跑通，下一步重点不应该继续补基础 ML，而应该转入 **reasoning 重写阶段**

因此，从现在开始，项目的核心目标从：

- “继续提升或重构纯 ML 主线”

切换为：

- “把已经验证过的可解释 ML 决策过程，系统化地转写成高质量、可控、可筛选的 reasoning / CoT SFT data”

---

### 23.2 这一阶段的根本目标

本阶段的最终目标不是让 LLM 从零自己发明化学推理，而是：

1. 先利用已经训练好的 **global EBM + local pairwise EBM + aggregation / hybrid**  
   产出结构化、可信的 **evidence objects**

2. 再让 LLM 在受约束条件下，把这些 evidence objects 改写成：
   - 更易读
   - 更自然
   - 更像高质量 scientific reasoning
   - 但仍然忠于原始纯 ML 证据

3. 最终形成可用于后续 SFT / distilled reasoning data 的高质量样本集

换句话说：

**这一阶段不是“让 LLM 替我们做分类”**，而是  
**“让 LLM 把已经存在的可解释决策证据改写成 reasoning”**

---

### 23.3 为什么不能直接把 EBM 图翻译成文本

#### 23.3.1 对 global EBM 而言
某些 feature（例如 BBB 中的 TPSA）可能有很多 bins，直接把 bin 编号、bin 边界、bin contribution 原样翻成文字会非常糟糕：

- 不可读
- 不自然
- 不像人类 reasoning
- 容易产生伪精确解释
- 很多时候曲线局部近似线性，强行粗暴合并成几个大区间也未必合理

因此：

**不能把“模型内部表示”直接当成“自然语言解释表示”**

#### 23.3.2 对 pairwise EBM 而言
pairwise EBM 的单个项是：

`f_i(base_i, delta_i)`

它本质上是一个二维 interaction 面。  
也不能直接把 heatmap 的每个 cell 或每个 bin 原样翻成句子。

#### 23.3.3 正确做法
对于 reasoning，我们真正需要的不是：

- bin id
- 图上的每个离散点
- 原始 heatmap cell

而是：

- 当前样本上最重要的证据是什么
- 这些证据是在支持、谨慎还是反对
- 这些证据在 playbook / literature 语义里意味着什么
- global 与 local 是否一致
- 最后为什么保留这个标签

也就是说，本阶段真正要做的是：

**建立一层 evidence abstraction layer**  
把纯 ML 证据先抽象成结构化证据对象，再交给 LLM 改写。

---

### 23.4 本阶段的核心思想：三层模式

1. per important feature raw evidence objects
2. 完整决策过成的中间草稿 draft，基本上就是每个feature的值还有决策推动方向的hint的短句拼起来
3. 利用playbook做最终 polished reasoning

---

### 23.5 本阶段的设计原则

#### 原则 1：ML 证据优先，LLM 只负责改写
LLM 不负责重新做分类，不负责重新决定 label。  
LLM 的职责是：

- 读取中间草稿 draft
- 在 playbook 约束下组织语言
- 生成自然语言 reasoning

#### 原则 2：playbook 是语义解释器，不是第二个分类器
DeepResearch / literature / playbook 的作用不是覆盖模型，而是提供：

- 每种性质在文献中的常见语义
- 每种性质在任务中的常见作用背景
- 常见 caution / anti-pattern
- 合理的专业表述方式

不应该让 playbook 直接代替模型做决策。

#### 原则 3：global 与 local 必须分开建模、分开解释
global 与 local 本来来自不同 teacher：

- global = 单分子 EBM
- local = 两个 pairwise EBM + 邻居聚合

因此 reasoning 里也必须保留这两个来源的区分。

#### 原则 4：先结构化，再自然语言化
必须先抽 evidence objects，再做比较自然语言化的draft，再做自然语言。  
不要直接从图、分数、CSV 生文本。

#### 原则 5：不强行合理化错误样本
如果最终 global 和 local 的预测都和 GT 不一致，很难形成高质量合理化解释，则应丢弃 sample，而不是强行扭转标签到GT label。

---

### 23.6 本阶段的总体产物

本阶段要新增的核心产物是：

#### 1. Evidence extraction outputs
结构化证据对象，例如：
- `outputs/reasoning_evidence/.../*.json`

#### 2. Playbook / literature background
任务级、property 级解释背景：`playbooks/<task>.md`

#### 3. LLM rewritten reasoning outputs
单步生成的最终 reasoning，例如：
- `outputs/reasoning_text/.../*.jsonl`
- 每条含原始 evidence、中间draft、最终 reasoning、keep/drop 标记、元信息

#### 4. Dataset filtering / quality control reports
用于筛 SFT data 的质量控制结果，例如：
- 保留率
- global/local 一致性分布
- 邻居支持强度分布
- 被丢弃样本原因和数量统计

---

## 24. Reasoning 阶段的总体 pipeline

### 24.1 输入
输入不是原始 molecule，而是已经完成纯 ML 推理后的结果集合，包括：

- global EBM bundle / per-sample feature contributions
- pairwise EBM bundle / per-pair local effect contributions
- neighbor retrieval 结果和 similarity 信息
- local aggregation 结果
- hybrid / local / global 的最终预测分数
- GT label
- task metadata

### 24.2 中间步骤
#### Step A：evidence extraction
将纯 ML 结果抽取成结构化 evidence objects

#### Step B：贡献大的feature的evidence hint还有最终的prediction连起来变成中间draft
把每个重要feature的值，怎么推动最终决策变化连起来，加上最后的prediction，变成这个sample的中间draft

#### Step C：LLM rewriting
让 LLM 在 playbook 提供的指导下，将中间 draft 改写成自然语言 reasoning

#### Step D：quality control (可选，第一版实现可以先不考虑这个)
检查最终 reasoning 是否：
- 忠于 evidence
- 没有 hallucination
- 没有自相矛盾
- 语言质量足够高

### 24.3 输出
最终输出适用于 SFT 的样本，例如：

- instruction
- structured evidence
- final reasoning
- target label
- metadata
- keep/drop
- chosen teacher

---

## 25. Playbook / literature 的目的是什么

### 25.1 为什么需要 playbook
单靠 EBM contribution 很难直接说出好的人类语言。  
例如：

- TPSA 的贡献为正
- HBD 的贡献为负
- 某个 pairwise `(base, delta)` interaction 推动正类

这些都还只是“模型语言”，不是自然科学语言。

playbook 的作用是把这些信号转成：
- 极性负担
- 氢键负担
- 脂溶性平衡
- efflux 风险
- 电离倾向
- 局部结构变化的可能机制

### 25.2 playbook 的正确定位
playbook 不是“另一个规则分类器”，而是：

#### Property-level semantic prior
例如：
- 对 BBB，TPSA 一般和极性负担相关
- 高 HBD/HBA 往往增加渗透障碍
- 但单个 descriptor 从来不应该被当成绝对规则

#### Task-level writing prior
例如：
- 对 BBB 的写法更偏 permeability / polarity / lipophilicity / H-bond burden
- 对 DILI 的写法更偏 reactivity / metabolic liability / lipophilic burden / bioactivation risk

#### Language normalization prior
例如：
- 如何用更自然、更稳健的表述方式改写“feature contribution”

### 25.3 playbook 的组织形式

每个任务的 playbook 已统一放在 `playbooks/<task>.md`。

---

## 26. Evidence objects 的设计（最关键）

本阶段最重要的工程任务不是 prompt，而是 **evidence schema**。

### 26.1 顶层样本对象
每个 query molecule 最终应先被抽成一个统一 JSON 对象，建议包括：

- `sample_id`
- `task`
- `split`
- `smiles`
- `gt_label`
- `global_prediction`
- `local_prediction`
- `hybrid_prediction`
- `global_score`
- `local_score`
- `hybrid_score`
- `keep_for_reasoning`
- `drop_reason`（若丢弃）
- `global_decision_evidence`
- `global_middle_draft`
- `local_per_neighbor_decision_evidence`
- `local_per_neighbor_middle_draft`
- `local_summary_middle_draft`
- `hybrid_summary_middle_draft`

---

### 26.2 Global evidence 的结构
global 部分来自单分子 EBM。

每个 query 应抽取贡献绝对值最大的若干个特征，无论将prediction最终推向哪个方向

每个 global feature evidence 建议至少包括：

- `feature_name`
- `feature_value`
- `contribution` (推向 label (A) 还是 (B) 的方向)
- `contribution_rank`
- `local_trend`（在当前值附近往上/往下的趋势，如果可提取）
- `text_hint`

#### 举例
对于 TPSA：
- 不是去说“落在第 428 个 bin”
- 而是抽：
  - 当前值
  - 当前 contribution (保留正负号)
  - 当前附近局部趋势
  - 一个简短自然语言 text hint

### 26.3 关于“很多 bins 的 feature”如何处理
不要强行把所有 bins 合并成几个大区间再解释。  
对于像 TPSA 这样近似连续、局部近似线性的曲线，更合理的方式是：

#### 解释单位不是“bin”
而是：
- 当前点的数值
- 当前点的 contribution
- 当前点附近的局部斜率或局部变化趋势

因此，在抽 evidence 时，对 global feature 要优先提取：

1. 当前值
2. 当前 contribution
3. 当前附近的 local directional behavior

而不是直接提取“粗暴区间标签”。

---

### 26.4 Local evidence 的结构
local 部分来自两个 pairwise EBM 以及对应的 neighbors。

每个 query 当前默认有：
- 3 个 positive neighbors
- 3 个 negative neighbors

每个 neighbor 都应先单独抽取 evidence，但自然语言阶段不一定全部展开成长段。

#### 每个 neighbor evidence 应至少包括
- `neighbor_smiles`
- `neighbor_label`
- `neighbor_similarity`
- `neighbor_scaffold`
- `pair_model_type`（positive_neighbor_model / negative_neighbor_model）
- `pair_score`
- `top_pair_feature_names`
- `feature_comparisons`

#### 每个 pair term 应包括
- `feature_name`
- `neighbor_value`
- `query_value`
- `delta_value`
- `contribution` (推向 label (A) 还是 (B) 的方向)
- `text_hint`

当前实现补充约定：
- dense comparison features 现在直接使用固定的全部 dense feature 列表，而不再按任务做 union 白名单裁剪
- `fg_top_level` 不在 dense comparison features 里；它们单独进入 `functional_group_differences`

#### 注意
这里的 `text_hint` 仍然应是短的、模板化的、证据级描述，不是最终 polished reasoning。

---

### 26.5 Local summary evidence 的结构

把原始 `weighted average` 语义化，而不是直接把数值写进 reasoning。

---

### 26.6 Final decision evidence 的结构
最终还需要一个统一的 decision evidence，建议包括：

- `teacher_selected`
- `teacher_score`
- `teacher_prediction`
- `gt_label`
- `global_local_relation`（agree / conflict / weak_agree / weak_conflict）
- `final_stance`
- `confidence`
- `why_keep_or_drop`
- `narrative_focus`（global / local / hybrid / mixed）

---

## 27. Sample keep/drop 策略

如果所有 global 和 local prediciton 都和 GT 不一致，则丢弃

---

## 28. Global / Local / Hybrid 的 reasoning 写法建议

### 28.1 Global reasoning
global 部分建议写成：

- 当前样本的全局 descriptor-level 趋势
- 哪些 feature 提供支持
- 哪些 feature 提供 caution
- 这些 evidence 对应什么样的 property-level 语义

不要写成：
- “bin 428 对应 +0.137”

应写成：
- “整体上，这个分子的极性负担没有落入明显不利区域”
- “有限的氢键负担与适度的脂溶性共同提供温和支持”
- “也存在某些 caution signal，但强度较弱”

### 28.2 Per-neighbor local reasoning
每个邻居都需要先做结构化分析，但自然语言层面不一定要全部展开成长段。

建议每个邻居先抽一个微分析对象，例如：
- 一句话 summary
- 1–2 个 top local effects
- 该邻居总体是支持、谨慎还是反证

### 28.3 Local summary reasoning
local summary 应写成：

- 多数邻居支持什么
- 主要反证来自哪里
- 邻居间是否一致
- 为什么 local 证据总体支持或反对该标签

不要直接写：
- “weighted average = 0.73”

而是写：
- “多数相似邻居给出一致支持，主要集中在较低极性负担这一模式”
- “虽然存在少量反证，但相似度更高的邻居总体仍偏向正类”

### 28.4 Hybrid reasoning
不需要在文本里显式出现 `lambda`。  
原因：
- `lambda` 是数值融合策略，不是人类语言层面的核心解释对象
- reasoning 应表达的是“全局与局部如何相互印证、或哪一侧最终占上风”

因此 hybrid 的文本重心应放在：
- global 与 local 是否一致
- 若不一致，哪边主导、为什么
- 最终结论如何形成

---

## 29. 为什么要把 6 个邻居先都抽证据，但自然语言阶段不一定都展开

当前 local 模块默认是：
- 3 个正类邻居
- 3 个负类邻居
- 共 6 个 neighbor comparisons

### 必须全部先抽结构化证据
因为：
- 最终 local summary 需要知道所有邻居的支持/反证格局
- 后续 quality control 也需要看到完整局部证据分布

### 但最终自然语言不一定 6 个都写成长段
因为：
- 太长
- 太重复
- 容易让 reasoning 变成机械复读
- 会降低 SFT data 质量

### 推荐做法
#### 在 evidence 层面
6 个邻居都保留

#### 在最终文字层面
- 可以只显式展开最重要的若干个邻居
- 其余邻居通过 local summary 统一归纳

例如：
- 明确写 2 个最强支持邻居
- 明确写 1 个最重要反证邻居
- 剩下的用“其余相似邻居大体一致”进行总结

---

## 30. LLM 单步重写阶段怎么做

### 30.1 输入
LLM 输入应包括：

- task name
- GT label
- selected teacher
- keep/drop 标记
- playbook relevant excerpts
- structured global evidence
- structured local evidence
- structured local summary
- structured final decision evidence

### 30.2 输出
LLM 单步输出建议至少包含：

- `keep`
- `teacher_used`
- `main_support`
- `main_caution`
- `final_reasoning`

也可以更丰富一点：

- `global_stance`
- `local_stance`
- `global_local_relation`
- `confidence`
- `final_reasoning`

### 30.3 对 LLM 的约束
必须在 prompt 中明确要求：

1. 不允许引入 evidence 中没有的新实验事实
2. 不允许篡改 GT label
3. 不允许改变 globle / local 的基本结论，但是可以根据实际 GT 改变 hybrid的结果确保SFT最终结论正确
4. 不允许把弱证据写成决定性铁律
5. 必须区分 global evidence 与 local evidence
6. 必须体现支持证据与 caution / counterevidence
7. 如果 evidence 冲突太高，应输出低质量或 drop，而不是硬写漂亮故事

### 30.4 不要让 LLM 做什么
不要让 LLM：
- 重新做分类
- 自己决定新的 label
- 自己补充分子机制结论
- 自己编造 feature effect

LLM 在这一阶段只做：
- 受约束的 evidence-to-reasoning rewriting

---

## 31. Reasoning 阶段的推荐目录与模块

建议在现有 TRIM 项目中新增一个 reasoning 子系统。

推荐新增结构例如：

    src/trim/reasoning/
    ├── playbooks/
    │   ├── common_properties/
    │   ├── tasks/
    │   └── loaders.py
    ├── evidence/
    │   ├── global_evidence.py
    │   ├── local_evidence.py
    │   ├── local_summary.py
    │   ├── teacher_selection.py
    │   └── schemas.py
    ├── prompts/
    │   ├── reasoning_prompt_builder.py
    │   └── prompt_templates.py
    ├── generation/
    │   ├── llm_rewrite.py
    │   ├── validators.py
    │   └── postprocess.py
    ├── filtering/
    │   ├── keep_drop_rules.py
    │   └── quality_checks.py
    └── pipelines/
        ├── extract_reasoning_evidence.py
        ├── build_reasoning_prompts.py
        ├── generate_reasoning_text.py
        └── build_sft_dataset.py

---

## 32. Reasoning 阶段的推荐开发顺序

### Phase R1：定义 evidence schema
目标：
- 定义统一 JSON schema
- 明确 global / local / final 三层 evidence 结构
- 明确 keep/drop 和 teacher selection 字段

这是整个 reasoning 阶段最关键的第一步。

### Phase R2：实现 evidence extraction
目标：
- 从现有 global EBM bundle 中抽 global evidence
- 从现有 pairwise EBM bundle + 邻居结果中抽 local evidence
- 生成 local summary
- 生成 final decision evidence

### Phase R3：实现 filtering
目标：
- 实现 keep/drop 规则
- 统计样本过滤结果

### Phase R4：实现单步 LLM rewriting
目标：
- 中间 draft -> final reasoning
- 确保输出不 hallucinate
- 先做少量样本 sanity check

### Phase R6：构建 reasoning SFT dataset
目标：
- 导出最终数据格式
- 含 instruction / input / output / metadata
- 可直接用于后续 SFT / distillation

---

## 33. 本阶段的成功标准

### 工程层面
1. 能从现有纯 ML 结果中稳定抽取 evidence objects 还有中间 draft
2. playbook 能被程序化加载并注入 prompt
3. teacher selection / filtering 能自动运行
4. 能批量生成 reasoning 文本
5. 能批量导出 reasoning SFT dataset

### 数据质量层面
1. 生成的 reasoning 忠于 evidence
2. 不出现明显 hallucination
3. global 与 local 证据边界清楚
4. 样本中支持证据 / caution 证据 / 最终结论结构清晰
5. 不把错误预测强行合理化

### 研究层面
1. 能回答“哪些纯 ML 样本值得转成 reasoning data”
2. 能回答“global / local / hybrid 哪一种更适合作为 reasoning teacher”
3. 能回答“playbook 是否真的提升了文本质量与稳定性”
4. 能回答“哪些样本类型应该被过滤掉而不是保留”

---

## 34. 这一阶段明确暂时不要做的事

1. 不要让 LLM 自由发挥重新做分类
2. 不要跳过 evidence objects 还有中间draft直接从模型图写文本
3. 不要把 literature / playbook 直接当第二个 classifier
4. 不要为了文字好看而保留明显错误或 evidence 混乱的样本
5. 不要急着做复杂的多阶段文本生成链条
6. 不要把 bin id / heatmap cell 直接暴露到最终 reasoning 文本中

---

## 35. 给 Codex 的最终执行指令摘要（Reasoning 阶段）

请按以下逻辑实现本阶段：

1. 纯 ML 主线已经完成，当前阶段的任务是 **reasoning / CoT 重写**，而不是继续补基础 ML pipeline。
2. 先实现 **evidence extraction layer**，把现有 global EBM、pairwise EBM、neighbor retrieval、aggregation / hybrid 结果转成统一的结构化 evidence objects。
3. 不要直接把 EBM 的 bins、曲线、heatmap 原样翻成自然语言；必须先做 evidence abstraction。
4. 对于 global 部分，不要粗暴依赖“大区间合并”；应优先抽取：
   - 当前值
   - 当前 contribution
   - text hint
5. 对于 local 部分：
   - 6 个邻居都要先抽结构化证据（3 个正类邻居 + 3 个负类邻居）
   - 每个邻居保留 similarity、label、top local features、stance
   - 然后做 local summary
7. 不要预设 hybrid 一定是最终 teacher。应实现动态 teacher selection：
   - 根据 GT、一致性、证据强度和可写性来选择 global / local / hybrid
8. 实现 keep/drop 规则：
   - 如果 global,local,hybrid 的最终结果都和 GT 不一致，则丢弃，如果global,local中有一个和GT一样，则根据GT来合理化解释改写最终hybrid的过程并且最终预测为GT label确保结论正确且中间过程合理
9. 最终采用两层产物：
   - Level 1：structured evidence objects
   - Level 2: global/local/hybrid的中间 draft
   - Level 3：LLM 生成global evidence/local evidence/local summary/hybrid summary 的 polished reasoning
10. 在 prompt 中严格限制 LLM：
    - 不可 hallucinate
    - 不可改 label
    - 不可发明新证据
    - 必须区分 global 与 local
11. 最终导出 reasoning SFT dataset，供后续 SFT / distillation 使用。

---

## 36. 一个简明版本的 reasoning 阶段总结（可放在 README / AGENTS 末尾）

在纯 ML 主线（global EBM、pairwise local EBM、local/hybrid aggregation）完成之后，项目正式进入 reasoning / CoT 重写阶段。本阶段的目标不是让 LLM 自主做分类，而是从现有可解释 ML 模型中抽取结构化 evidence objects，并结合 property-level 与 task-level playbook，把这些证据受约束地重写成高质量、忠于模型、可筛选的 reasoning SFT data。当前阶段的核心任务包括：evidence schema 设计、global/local 证据抽取、teacher selection、keep/drop 策略、playbook 构建、单步 LLM rewriting 以及最终 reasoning 数据集导出。
