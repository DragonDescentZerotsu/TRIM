# 项目背景与目标说明

## Env Instructions

If you are on `node002`, default to the `vllm` conda environment when you need RDKit or the local project dependencies. conda is at: /data1/tianang/anaconda3/condabin/conda

## Current Progress Snapshot

截至目前，**global 单分子 EBM 迁移阶段已经完成**，当前进度如下：

- 已在 `TRIM` 下建立新的项目骨架与脚本入口。
- 已把 clean split data、RDKit/pKa feature、FG feature、similarity cache 接到 `TRIM` 本地路径下，目前大文件先采用 soft link 方式迁移。
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
  - `scripts/run_local_hybrid_batch_test.py`
    - 复用已有 pairwise bundle，批量跑多任务 test
    - 支持为特定任务覆盖 pair bundle 根目录，例如 `BBB_Martins`
- 当前下一步重点应转到 **pairwise / local 模块**，不要重复花时间在 global EBM 迁移上，除非是为了配合 local / hybrid 接口做必要的小修改。

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

### Phase 3：训练两个 pairwise EBM
目标：
- 训练 `pair_EBM_pos`
- 训练 `pair_EBM_neg`
- 不使用 main features
- 仅使用 `(base_i, delta_i)` 的 interaction

### Phase 4：local-only molecule classifier
目标：
- 对 valid/test query 只从 train 检索邻居
- 跑两个 pairwise EBM
- 聚合得到 `S_local`
- 报 molecule-level performance

### Phase 5：global + local hybrid
目标：
- 融合 `S_global` 和 `S_local`
- 在 valid 上调 λ
- 在 test 上报告最终结果
- 与 global-only / local-only 对比

### Phase 6：分析与保障
目标：
- 做 pair-level teacher quality 分析
- 做 similarity / applicability domain 分桶分析
- 明确 local 模块是否真正带来增益

补充进度：
- 已经可以直接从现有 bundle 生成 global / pairwise 的解释性可视化。
- pairwise 可视化当前采用 **2D heatmap**，因为模型项是 `f_i(base_i, delta_i)`，不是单变量曲线。

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
- 第 3-5 条：**尚未完成，当前主攻方向应为 pairwise/local/hybrid**

### 实验层面
1. 能清楚报告 pair-level 与 molecule-level 两层指标
2. 能清楚比较 global-only / local-only / hybrid
3. 能说明 scaffold split 下 local 模块是否真的有帮助
4. 能说明 local 模块在哪些 similarity / AD 区间更可靠

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
