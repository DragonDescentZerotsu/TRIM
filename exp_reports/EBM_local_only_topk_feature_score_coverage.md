我做了一个全量统计，结论很直接：**top-6 不能作为“覆盖绝大多数 local EBM score”的依据**。它只能说是“每个 neighbor 最显著的 6 个 feature terms”。

统计口径：对 local pair-EBM 的 `model.eval_terms(pair_matrix)`，按每个 feature-term 的 `abs(contribution)` 排序，计算 top-k 覆盖 `sum(abs(contribution))` 的比例。这个口径和当前 middle draft 的 top contribution 逻辑一致，不包括 EBM intercept。

我新增了可复跑脚本：

[scripts/analyze_local_pair_term_coverage.py](scripts/analyze_local_pair_term_coverage.py)

并跑了：

- train 全量：119,040 个 neighbor-pair
- valid 全量：16,912 个 neighbor-pair

结果文件在：

- `outputs/metrics/local_pair_term_coverage_core_pka_no_fr_counts_train/`
- `outputs/metrics/local_pair_term_coverage_core_pka_no_fr_counts_valid/`

核心结果：

| top-k | train median coverage | valid median coverage |
|---:|---:|---:|
| 6 | 45.0% | 45.1% |
| 8 | 52.0% | 52.2% |
| 10 | 57.5% | 57.7% |
| 12 | 62.1% | 62.3% |
| 15 | 67.6% | 67.8% |
| 20 | 74.4% | 74.6% |

达到目标覆盖率需要的 feature 数：

| coverage target | train median k | valid median k | train p75 k | valid p75 k |
|---:|---:|---:|---:|---:|
| 75% | 21 | 21 | 25 | 25 |
| 80% | 27 | 26 | 32 | 31 |
| 85% | 35 | 34 | 41 | 41 |
| 90% | 49 | 48 | 57 | 57 |

按 label 看没有明显差异。train 上：

- label 0: top-6 median 45.3%
- label 1: top-6 median 44.8%

positive-neighbor model 和 negative-neighbor model 也差不多：

- positive-neighbor model: top-6 median 45.7%
- negative-neighbor model: top-6 median 44.4%

所以我的建议是：

1. **不要把 top-6 描述成覆盖绝大多数 score。** 这个说法不成立。
2. 如果目标是“过半 contribution mass”，`top-8` 或 `top-10` 才有经验依据；我会选 **top-10**，因为 median coverage 稳定在 57-58%。
3. 如果目标真的是“绝大多数”，比如 75%，那固定 `top-20` 才勉强接近，但每个 sample 有 6 个 neighbors，会变成最多 120 条 feature evidence，太长。
4. 对当前 reasoning 数据构建，我更建议把 per-neighbor middle draft 改成 **top-8 或 top-10 的 salient evidence budget**，而不是 threshold coverage budget。若要更严谨，可以在 metadata 里保存 `coverage_top_k`，但文本里只写前 8/10 个。

我倾向的折中方案：**把 `top_term_k_per_neighbor` 从 6 提到 10**。它不会覆盖“绝大多数”，但比 6 有明显统计依据：从约 45% 提到约 58%，同时长度还没失控。