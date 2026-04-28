# TRIM 方法框架总结：面向分子任务的高质量推理数据合成

本文档总结 TRIM 的核心方法框架。当前项目最重要的贡献不是简单融合若干已有机器学习算法，而是提出一种**面向分子性质预测任务的高质量推理数据合成方法**。

现有大语言模型在分子任务中通常面临两个困难。第一，它们可以生成看似合理的化学解释，但这些解释未必忠实于可验证的分子证据。第二，它们很难可靠比较多个分子之间的细粒度差异，尤其是在需要判断“待预测分子相对于相似正例或负例发生了哪些关键变化”时，模型容易遗漏定量差异、混淆方向，或者把某个描述符解释成不适用于当前任务和当前相似分子的全局规律。

TRIM 的目标是解决这个数据生成问题：如何自动构造一批既有真实工具调用、又有可信分子证据、还能覆盖相似分子对比推理的监督训练样本。为此，TRIM 使用可解释机器学习模型作为证据教师，把单分子属性分析和相似分子对比分析转化为结构化证据，再经过过滤、改写和轨迹组装，生成可用于训练分子智能体的工具调用式推理数据。

## 1. 核心任务：合成可监督的分子推理轨迹

TRIM 面向基于分子骨架划分的二分类分子性质预测任务。每个样本包含一个分子的 SMILES 字符串，以及某个任务下的二分类标签。任务类型包括吸收、分布、代谢、排泄、毒性、转运体活性、酶底物状态、抗病毒活性等。

本文关注的核心任务不是单纯训练一个分子分类器，而是合成如下形式的高质量推理轨迹：

1. 用户给出任务和待预测分子的 SMILES。
2. 助手调用工具获取该分子的理化性质和官能团信息。
3. 工具返回可验证的单分子属性。
4. 助手基于这些属性写出单分子分析。
5. 助手调用工具检索和比较训练集中的相似分子。
6. 工具返回正类和负类相似分子，以及它们与待预测分子的属性差异。
7. 助手基于相似分子对比写出局部类比分析。
8. 助手整合单分子证据和相似分子对比证据，给出最终答案。

这种数据形式比普通“输入 SMILES、输出答案”的监督数据更丰富。它不仅包含最终标签，还包含工具调用、工具返回、单分子推理、多分子对比推理和最终融合推理。因此，它更适合训练能够主动使用工具、并基于可检查证据完成分子判断的智能体。

## 2. 为什么需要结构化教师模型

直接让大语言模型为分子任务生成推理数据有明显风险。语言模型可能写出流畅但不可验证的解释，也可能在比较多个分子时犯错。例如，当模型需要比较待预测分子和若干相似正例、负例时，它需要同时判断：

- 哪些分子属性发生了变化；
- 变化方向是升高还是降低；
- 变化幅度是否重要；
- 这个变化在相似分子的基准范围下意味着什么；
- 该变化是支持正类、支持负类，还是只是弱证据；
- 不同相似分子之间的证据是否一致。

这些判断对于纯语言模型并不稳定。尤其是 SMILES 本身不是天然适合语言模型逐位比较的表示，多个分子的细粒度结构和理化属性差异也很难仅靠上下文阅读可靠完成。

TRIM 的关键思路是：不要让语言模型直接承担最脆弱的分子差异比较工作，而是先用可解释、可计算的教师模型生成结构化证据。语言模型的主要职责变成把这些结构化证据改写成自然、连贯、符合任务语境的推理文本。

换言之，TRIM 将“让语言模型凭空推理”转化为“让语言模型忠实表述可验证证据”。

## 3. 总体框架

TRIM 的推理数据合成流程包含五个阶段：

1. **工具可见的分子证据表示**：为每个分子构建紧凑、可解释、适合工具返回的理化属性和官能团表示。
2. **可解释教师证据生成**：用全局单分子教师模型生成分子自身属性证据，用局部成对教师模型生成相似分子对比证据。
3. **教师正确性过滤**：只保留至少一个教师模型预测正确的样本，避免为错误预测生成事后合理化解释。
4. **证据到推理文本的改写**：将模型内部证据改写成自然语言推理，同时去除模型内部术语和元话语。
5. **工具调用式轨迹组装**：把用户问题、工具调用、工具返回、分阶段推理和最终答案组装成监督微调样本。

在这个框架中，机器学习模型不是最终目标，而是高质量推理数据的“证据生产器”。全局模型负责回答“这个分子自身有哪些支持或反对标签的属性”；局部模型负责回答“这个分子与相似正例和负例相比，哪些差异支持或反对标签”。

## 4. 工具可见的分子证据表示

为了让后续推理数据适合语言模型学习，TRIM 使用一个紧凑、可解释的分子特征空间。当前默认特征版本结合了官能团信息、RDKit 描述符和少量核心 pKa/logD 属性。

默认稠密特征表不包含 `rdkit__fr_*` 这类 RDKit 片段计数特征；pKa 侧只保留少量核心字段，例如中性分子比例、估计 logD、酸性/碱性/可电离位点数量、最强酸性 pKa 和最强碱性 pKa。

这一设计的重点是让工具返回既足够有信息量，又不会让语言模型上下文被大量低层片段计数淹没。官能团信息作为稀疏证据单独提供：全局工具只列出非零官能团，局部比较工具只列出待预测分子和邻居分子之间有差异的官能团。

对于 pKa 相关缺失值，TRIM 不直接输出 `NaN`，而是给出化学语义。例如，当一个分子没有酸性位点时，最强酸性 pKa 会被表达为“不适用，因为该分子没有酸性位点”。这种处理使工具返回更接近人类专家会使用的语言，也减少了语言模型误读缺失值的风险。

## 5. 单分子证据教师

TRIM 的第一类教师模型用于生成单分子证据。对于每个任务，系统在稠密分子特征上训练一个可解释提升机模型，即 EBM：

```text
s_g(x) = P(y = 1 | x)
```

其中 `x` 表示待预测分子，`s_g(x)` 表示该分子属于正类的全局预测分数。

全局 EBM 的作用不是作为论文的主要算法创新，而是为推理数据提供可分解的单分子证据。由于 EBM 是加性模型，每次预测都可以分解成多个特征级贡献。因此，系统可以知道哪些分子属性把预测推向标签 1，哪些属性把预测推向标签 0。

从全局教师模型中，TRIM 抽取以下证据：

- 预测标签和预测分数；
- 最重要的单分子特征贡献；
- 每个贡献支持还是反对当前预测；
- 每个特征取值的自然语言描述；
- 可选的 EBM 项曲线局部趋势信息。

这些证据会被转化为单分子分析草稿。草稿可能仍然包含模型内部语言，但它保留了“分子属性如何影响判断”的证据链。

## 6. 相似分子对比证据教师

TRIM 的第二类教师模型用于生成相似分子对比证据。这是方法中最关键的设计之一，因为它直接针对大语言模型难以可靠比较不同分子差异的问题。

对于一个待预测分子，TRIM 从训练集中检索相似分子，并按照标签分成正类邻居和负类邻居。相似度由 Morgan 指纹相似度和 Feature-Morgan 指纹相似度加权得到：

```text
sim(x, z) = 0.8 * sim_Morgan(x, z) + 0.2 * sim_FeatureMorgan(x, z)
```

其中 `x` 是待预测分子，`z` 是训练集中的候选邻居分子。

局部对比的关键不是只找到相似分子，而是判断“待预测分子相对于这些相似分子的差异是否支持某个标签”。为此，TRIM 将每个待预测分子与邻居分子的组合转化为成对特征表示。对于每个分子属性 `f`，成对表示包含两部分：

- 邻居分子的基准值，即 `z_f`；
- 待预测分子相对邻居分子的差值，即 `x_f - z_f`。

因此，成对表示可以写成：

```text
phi(x, z) = [z_f, x_f - z_f]，对所有特征 f
```

TRIM 分别训练正类邻居模型和负类邻居模型，用于评价待预测分子相对正类相似分子和负类相似分子的比较结果。

这种设计把分子对比从自由文本问题转化为结构化建模问题。模型不是简单判断“某个描述符变大是否更好”，而是在给定邻居分子基准范围的情况下，判断“待预测分子相对邻居分子的变化是否支持当前任务标签”。这对于分子任务尤其重要，因为许多描述符的意义并不是全局单调的，而是依赖任务、骨架、邻居类型和当前数值范围。

例如，更高的极性、更大的分子量、更多氢键供体或更高脂溶性，并不能脱离任务和相似分子基准范围直接解释为好或坏。TRIM 的成对教师模型显式建模“基准值”和“相对差值”的交互，从而为语言模型提供更可靠的分子对比证据。

## 7. 局部证据聚合

每个待预测分子与邻居分子的比较都会得到一个成对分数。TRIM 使用按相似度加权的平均值对这些分数进行聚合。

正类邻居和负类邻居可以分别得到组级汇总：

```text
s_pos = 正类邻居分数的相似度加权平均
s_neg = 负类邻居分数的相似度加权平均
```

随后，将正类和负类邻居比较共同池化，得到整体局部分数：

```text
s_l(x) = 所有局部成对分数的相似度加权平均
```

局部分数本身可以用于预测，但在 TRIM 的数据合成框架中，更重要的是它提供了可抽取的类比证据：

- 哪些正类邻居支持或削弱正类判断；
- 哪些负类邻居支持或削弱负类判断；
- 哪些分子属性差异在多个邻居中反复出现；
- 哪些证据只来自单个邻居，需要在推理中单独说明；
- 最终局部类比整体倾向哪个标签。

这些局部证据使合成推理数据能够覆盖多分子比较，而不是只停留在单分子属性描述。

## 8. 教师证据的预测性验证与融合

TRIM 也保留了全局-局部混合预测机制，用于验证教师证据本身具有预测能力。系统用一个简单线性组合融合全局分数和局部分数：

```text
s_h(x) = lambda * s_g(x) + (1 - lambda) * s_l(x)
```

其中 `lambda` 在验证集上通过网格搜索选择，主要优化宏平均 F1。

需要强调的是，这里的融合模型不是论文的主要贡献。它的作用是评估和校准两类教师证据：单分子证据是否有预测力，相似分子对比证据是否有预测力，两者结合后是否能形成更稳定的教师信号。

当前实验结果显示，相似分子类比证据在基于分子骨架划分的测试场景中非常强。这一结果支持 TRIM 的核心动机：高质量分子推理数据不应只教模型看单个分子的属性，还应显式训练模型比较相似分子之间的差异。

## 9. 教师正确性过滤

为了避免生成错误或虚假的推理数据，TRIM 在语言模型改写之前加入教师正确性过滤。对于每个样本，系统检查全局教师模型和局部教师模型是否预测对真实标签。

样本保留条件是：

```text
全局预测正确 或 局部预测正确
```

如果全局和局部都预测错误，则该样本会在进入语言模型改写之前被丢弃。

这个步骤很重要，因为推理数据合成不是让语言模型为任意模型输出编故事。如果教师模型已经判断错误，那么继续生成解释很容易得到“流畅但错误”的合理化文本。TRIM 通过过滤机制确保进入改写阶段的样本至少有一条教师证据路径支持真实标签。

这种过滤使最终数据更接近“可信教师证据的自然语言表达”，而不是“对错误预测的事后解释”。

## 10. 从模型证据到自然语言推理

通过教师正确性过滤的样本会进入三阶段改写流程：

1. **单分子分析改写**：将全局 EBM 的证据草稿改写成自然语言的待预测分子自身属性分析。
2. **多分子类比分析改写**：将局部成对证据改写成逐邻居分子的相似分子比较分析。
3. **最终融合层推理改写**：将单分子分析和多分子类比分析整合成最终标签判断。

每个任务可以配套一个任务手册。任务手册提供该任务相关的背景知识，例如重要属性范围、吸收/分布/代谢/排泄/毒性相关的化学直觉、以及标签语义。任务手册的作用不是替代模型证据，而是帮助语言模型用更符合任务语境的方式表达已有证据。

改写阶段受到严格约束：

- 最终推理不应出现草稿、提示词、任务手册、特征贡献、成对分数等内部元话语；
- 相似分子比较推理必须显式覆盖每一个检索到的邻居分子；
- 描述符解释必须考虑基准范围，并针对具体邻居分子；
- 不能把同一个描述符强行解释成跨任务、跨邻居都成立的全局单调规律；
- 最终标签必须与目标标签一致；
- 最终融合层只整合已有单分子和多分子分析，不重复完整证据。

通过这个过程，TRIM 将模型内部证据转化为更接近人类可读推理的数据，同时保留证据来源和标签一致性。

## 11. **工具调用式训练轨迹组装**

TRIM 最终将改写后的推理组织成工具调用式监督微调样本。系统暴露两个带任务上下文的工具：

```text
get_mol_properties_and_fg(smiles)
compare_similar_mols(smiles)
```

第一个工具返回待预测分子的稠密分子属性和非零官能团。第二个工具在当前任务上下文中检索相似训练分子，并返回正类邻居、负类邻居、它们的标签、相似度，以及待预测分子与邻居分子的特征级差异。

最终训练轨迹具有如下结构：

1. 用户给出任务描述和 SMILES，要求预测该分子的标签。
2. 助手调用分子属性工具。
3. 工具返回待预测分子的单分子属性和官能团信息。
4. 助手写出单分子分析，并继续调用相似分子比较工具。
5. 工具返回正类和负类相似分子比较信息。
6. 助手写出局部类比分析、最终融合推理和最终答案。

这种格式使训练样本显式包含“什么时候调用工具、工具返回了什么、如何基于工具结果推理、如何整合多类证据”。因此，TRIM 生成的不是普通链式思维文本，而是带有真实工具使用过程的分子智能体训练轨迹。

## 12. 方法贡献

TRIM 的核心贡献可以概括为以下几点：

- **提出一种面向分子性质预测的高质量推理数据合成框架。** 该框架将可解释机器学习教师转化为工具调用式推理轨迹，而不是只训练一个新的分子分类器。
- **提出一种结构化的相似分子对比证据生成方法。** TRIM 用相似分子检索和成对 EBM 建模待预测分子相对正类、负类相似分子的差异，缓解现有语言模型难以可靠比较多个分子的问题。
- **将分子对比推理从自由文本问题转化为可验证的结构化证据问题。** 通过“邻居基准值”和“待预测分子相对差值”的表示，TRIM 能生成考虑基准范围和具体邻居的对比证据。
- **设计教师正确性过滤机制。** 只有全局或局部教师模型至少一方预测正确的样本才进入改写阶段，从而减少对错误预测的事后合理化。
- **构造包含工具调用、工具返回、单分子推理、多分子对比推理和最终答案的监督训练数据。** 这使最终数据更适合训练能够使用工具并进行证据整合的分子智能体。

TRIM 的核心问题可以概括为：

```text
如何自动生成可信的分子推理数据，
使模型不仅学习单个分子的属性解释，
还学习如何比较相似分子之间的关键差异？
```

TRIM 的回答是：先用可解释教师模型生成可验证的单分子和多分子对比证据，再用受约束的语言模型改写将这些证据转化为自然推理，最后组装成工具调用式监督微调轨迹。

## 13. 当前 analogical-only 版本的实验与分析规划

如果当前版本已经不再强调单分子分析，而是聚焦于相似分子类比推理，那么论文实验也应当围绕一个更明确的问题展开：

```text
TRIM 生成的 analogical reasoning traces 是否让模型学会了
基于已知正负类邻居、相似度和特征差异进行证据化比较，
而不是简单做 KNN label voting、模板复述或教师模型蒸馏？
```

在整体效果没有特别惊艳的情况下，论文不应只依赖平均 F1 提升，而应通过多组分析证明训练后的模型确实具备更好的 evidence-grounded analogical reasoning 行为。下面列出推荐的核心分析、具体做法、指标和能够支撑的结论。

### 13.1 主性能表：SFT 是否优于同工具 prompted baseline

**目的。** 证明 TRIM 的 SFT 不是只改变输出风格，而是在相同工具可用的情况下提升了模型预测和推理质量。

**做法。** 在同一组测试任务、同一套 scaffold split、同一个 `compare_similar_mols` 工具上比较：

```text
1. Prompted LLM, no tools
2. Prompted LLM + compare_similar_mols tool
3. SFT on TRIM analogical traces + same tool
4. SFT + process-aware RL + same tool（如果已经有）
5. Pairwise EBM teacher
6. KNN-k baseline
```

这里的关键公平性是：prompted baseline 和 SFT model 在推理时应看到同样的工具返回。否则提升可能来自信息量差异，而不是训练带来的推理能力差异。

**指标。**

- task-mean macro-F1；
- balanced accuracy；
- ROC-AUC，如果模型能输出概率或置信度；
- valid tool-call rate；
- trace quality score，见 13.4；
- 每个任务单独结果，避免平均值掩盖任务差异。

**能说明什么。** 如果 SFT model 显著优于 prompted LLM + 同工具，说明模型不是单纯受益于工具信息，而是通过 TRIM traces 学会了更稳定地使用工具证据。如果 SFT 接近或超过 pairwise teacher，可以进一步说明 LLM 不是简单蒸馏教师，而是在工具使用、证据整合和任务语义表达上获得了额外收益。

### 13.2 KNN-hard slice：证明模型不是复制邻居标签

**目的。** 直接回应“TRIM 是否只是 KNN label voting”的质疑。

**做法。** 在测试集中构造 KNN-hard 子集。可以定义多种难度切片：

```text
KNN-wrong slice:
  KNN-k 的预测标签 != ground truth

KNN-low-margin slice:
  top-k 邻居中正负比例接近，例如 3:2 或 2:3

nearest-neighbor-misleading slice:
  最相似邻居的标签 != ground truth

positive-negative-conflict slice:
  top positive neighbor 和 top negative neighbor 的相似度差很小

teacher-vs-KNN slice:
  KNN 预测错误，但 pairwise EBM teacher 预测正确
```

对每个切片分别评估 KNN、prompted LLM + tool、SFT model 和 SFT+RL。

**指标。**

- slice-level macro-F1 或 accuracy；
- 相对 KNN 的提升；
- SFT 相对 prompted LLM 的提升；
- 错误样本中的 trace contradiction rate；
- 模型是否仍覆盖正负两侧邻居。

**能说明什么。** 如果 SFT 在 KNN-hard slice 上明显优于 KNN 和 prompted baseline，就能有力说明模型不是只读取邻居标签或相似度投票，而是在利用特征差异做更细粒度的类比判断。

### 13.3 Label-only / feature-only / full evidence ablation

**目的。** 区分 neighbor label、feature difference 和完整类比证据各自的作用。

**做法。** 在推理时构造三个版本的相似分子工具输出：

```text
Label-only:
  返回 neighbor SMILES、similarity、neighbor label；
  不返回 descriptor differences 或 functional-group differences。

Feature-only no-label:
  返回 neighbor SMILES、similarity、descriptor differences、functional-group differences；
  隐藏 neighbor label 或把正负类块名去掉。

Full evidence:
  返回 neighbor label、similarity、descriptor differences、functional-group differences。
```

三组工具输出应保持邻居集合一致，只改变可见字段。这样可以避免不同 retrieval 结果引入混杂因素。

**指标。**

- 全测试集 macro-F1；
- KNN-hard slice macro-F1；
- trace quality score；
- neighbor coverage；
- feature-delta citation rate；
- label citation correctness。

**预期模式。**

理想结果不是“no-label 最好”，而是：

```text
Full evidence > label-only
Full evidence > feature-only no-label
```

其中 label 是类比锚点，feature differences 是避免退化成 KNN 的关键证据。

**能说明什么。** 如果 full evidence 明显优于 label-only，说明模型确实使用了特征差异，而不是只做标签投票。如果 full evidence 优于 feature-only no-label，说明 neighbor label 对 supervised analogy 是必要锚点，完全抹掉 label 会破坏类比任务定义。

### 13.4 Trace grounding metrics：证明推理更忠实于工具证据

**目的。** 即使最终 F1 提升有限，也要证明 SFT 后模型生成的推理更 grounded、更少胡编、更能覆盖邻居比较。

**做法。** 对每条模型输出自动打分。可以从工具返回和最终 trace 中解析以下指标：

```text
Tool success:
  是否调用了正确工具；
  工具参数中的 SMILES 是否和用户 query 一致；
  是否在工具失败时仍强行回答。

Neighbor coverage:
  返回的每个正类/负类邻居是否都被提到；
  是否只讨论正类邻居而忽略负类邻居；
  是否只讨论最相似的一个邻居。

Label grounding:
  提到的 neighbor label 是否与工具返回一致；
  是否把 positive neighbor 说成 negative，或反过来。

Feature grounding:
  trace 中引用的 feature 是否存在于工具返回；
  引用的数值是否正确；
  query higher/lower than neighbor 的方向是否正确；
  是否把缺失值当成真实数值解释。

Evidence integration:
  是否在最终答案前先讨论证据；
  是否显式处理正负邻居冲突；
  是否把所有 descriptor 解释成固定单调规律。

Contradiction:
  最终结论是否和前文证据方向矛盾；
  是否先说证据支持正类，最后无解释地答负类。
```

可以把每个维度做成 0/1 指标，也可以加权得到一个 trace quality score。

**比较对象。**

```text
Prompted LLM + tool
SFT model + tool
SFT+RL model + tool
```

**能说明什么。** 如果 SFT 的 F1 提升不大，但 tool success、neighbor coverage、feature grounding、delta direction correctness 明显提升，论文仍然可以主张：TRIM 主要提升的是 evidence-grounded reasoning behavior，而不仅是最终分类分数。

### 13.5 Evidence corruption test：验证模型是否真的依赖证据

**目的。** 测试模型是否会根据工具证据变化而改变判断，而不是无视工具输出或套用固定模板。

**做法。** 在 evaluation 时对 `compare_similar_mols` 的输出做 controlled corruption。保持用户 query 和任务不变，只改变工具返回：

```text
Shuffle neighbor labels:
  在同一批邻居中随机打乱 label。

Swap positive/negative blocks:
  把正类邻居块和负类邻居块互换。

Shuffle feature deltas:
  保留 feature 名称和数值集合，但打乱到不同邻居上。

Flip delta directions:
  把 query higher than neighbor 改成 lower，或把差值符号取反。

Remove top teacher-important features:
  删除 pairwise EBM 贡献最大的几个 feature differences。

Replace similarities:
  打乱 similarity，使模型无法可靠依赖相似度排序。
```

这些 corruption 不用于正常测试分数，而用于 faithfulness analysis。

**指标。**

- corrupted evidence 下 final accuracy 的下降；
- final answer flip rate；
- trace contradiction rate；
- 模型是否引用被 corrupted 的证据；
- 模型是否对冲突证据表现出更低 confidence。

**能说明什么。** 如果证据被破坏后模型表现下降，并且输出方向随证据变化而变化，说明模型确实依赖工具证据。如果 corruption 后模型几乎不变，说明它可能主要依赖任务先验、模板或训练集偏见。

### 13.6 Teacher-evidence agreement：模型是否复现了教师证据重点

**目的。** TRIM 的训练数据来自 pairwise teacher，因此应验证 SFT 后模型是否真的使用了 teacher 所强调的关键比较证据。

**做法。** 对每个样本，保存 pairwise EBM 的 top-k evidence terms，例如：

```text
neighbor id
feature name
neighbor baseline value
query-minus-neighbor delta
term sign: supports label 1 or label 0
term magnitude
```

然后从模型 trace 中抽取被提到的 feature 和方向，比较二者一致性。

**指标。**

- top-k feature mention recall：teacher top-k 中有多少被模型提到；
- top-k feature precision：模型提到的 feature 中有多少属于 teacher top evidence；
- sign agreement：模型说该差异支持/反对某标签时，是否与 teacher term sign 一致；
- neighbor-level evidence coverage：每个邻居是否至少提到一个 teacher-important 差异；
- magnitude sensitivity：teacher term 越大，模型越可能提到该 feature 吗。

**能说明什么。** 这能证明模型不是随意写化学解释，而是在学习 teacher-grounded evidence selection。如果 SFT 的 teacher-evidence agreement 高于 prompted baseline，说明 TRIM traces 让模型更忠实地使用结构化证据。

### 13.7 Conflict handling slice：测试模型处理矛盾证据的能力

**目的。** 类比推理的难点通常不是所有邻居都一致，而是正负邻居同时相似、不同 feature 指向不同标签。需要专门评估这种情况。

**做法。** 构造 conflict-heavy 子集：

```text
正类和负类 top neighbor similarity 差距很小；
KNN vote margin 很小；
pairwise teacher 中同时存在强正向和强负向 feature terms；
正类邻居中有削弱正类的差异，负类邻居中有削弱负类的差异；
prompted baseline 经常只看一侧邻居。
```

**指标。**

- conflict slice F1；
- 是否同时讨论正负邻居；
- 是否使用转折结构处理冲突，例如 “although..., however...”；
- 是否过度依赖单个最近邻；
- final answer 是否与综合证据一致。

**能说明什么。** 如果 SFT 在 conflict slice 上比 prompted baseline 更稳定，说明它学到的是多证据整合，而不是简单模板或单邻居复制。

### 13.8 Held-out task generalization：回应 cooked SFT data 的质疑

**目的。** 证明模型学到的不是固定任务、固定字段、固定模板上的局部适应，而是可以迁移的 analogical reasoning procedure。

**做法。** 做任务级 held-out：

```text
Split A:
  训练 SFT 用 8 个任务；
  测试在剩下 8 个任务。

Split B:
  按任务类型留出，例如 train on ADMET/toxicity，test on CYP/transporter/antiviral。

Leave-one-task-out:
  每次留一个任务完全不参与 SFT，在该任务上测试。
```

测试时仍允许调用该 held-out task 的 compare tool，因为目标是测试是否能使用新任务的工具证据，而不是完全无工具猜测。

**指标。**

- held-out task macro-F1；
- 相对 prompted LLM + tool 的提升；
- trace quality 是否保持；
- feature grounding 和 neighbor coverage 是否退化；
- 与 in-task SFT 的性能差距。

**能说明什么。** 如果模型在未见任务上仍能更好地覆盖邻居、引用差异并整合证据，就能直接回应 cooked concern：模型学到的不只是某几个 TDC 任务的固定答案模式，而是类比推理流程。

### 13.9 Tool-output format robustness：测试是否只背了固定格式

**目的。** 证明 SFT 模型不是只适应了训练时固定的 tool output 排版。

**做法。** 在 evaluation 时保持信息内容不变，但改变工具输出格式：

```text
Shuffle neighbor order:
  正负类块内邻居顺序随机。

Shuffle feature order:
  每个邻居下 feature differences 顺序随机。

Alternative label wording:
  positive/negative 改成 active/inactive 或 label 1/0。

Numeric formatting:
  小数位数改变，或把 delta 写成 “query is 0.8 higher” 而不是 “delta = +0.8”。

Different k:
  返回 k=2、k=4、k=6 个邻居。

Compact vs verbose:
  同样信息用表格或自然语言短句两种格式返回。
```

**指标。**

- final F1 是否下降；
- trace grounding 是否下降；
- neighbor coverage 是否受 k 变化影响；
- feature direction correctness 是否保持。

**能说明什么。** 如果模型对格式扰动鲁棒，说明它不是只背固定模板。如果模型对格式极其敏感，则需要在训练中加入 tool-output format augmentation。

### 13.10 Reasoning-vs-answer training ablation

**目的。** 证明自然语言 analogical reasoning traces 本身有价值，而不是只需要工具输出和最终标签。

**做法。** 训练几个数据变体：

```text
Answer-only SFT:
  用户问题 -> 最终标签，不含工具调用和 reasoning。

Tool-output + answer SFT:
  包含工具调用和工具返回，但 assistant 只输出最终答案。

Template reasoning SFT:
  用固定模板填充邻居和 feature，不经过 rewrite model。

TRIM rewritten reasoning SFT:
  当前完整自然语言类比推理轨迹。
```

如果训练成本有限，可以先在较小模型或任务子集上做。

**指标。**

- full test macro-F1；
- KNN-hard slice F1；
- trace quality；
- teacher-evidence agreement；
- held-out task generalization。

**能说明什么。** 如果 TRIM rewritten reasoning 在 trace quality、hard slice 或 held-out task 上优于 answer-only 和 template reasoning，就能证明推理数据不是装饰，而是训练了更好的证据组织和比较行为。

### 13.11 Error taxonomy：系统分析模型还错在哪里

**目的。** 即使整体性能一般，也可以通过错误分类展示方法的优势、局限和下一步改进方向。

**做法。** 从 prompted baseline、SFT model、SFT+RL model 中各抽样一批错误样本，例如每个模型 100 条，人工或半自动分类：

```text
Tool-use errors:
  没有调用工具；
  工具参数 SMILES 错误；
  工具失败后仍回答。

Neighbor-use errors:
  忽略负类邻居；
  忽略正类邻居；
  只复制最近邻标签；
  把邻居 label 读反。

Feature-comparison errors:
  delta 方向读反；
  引用不存在的 feature；
  数值大小比较错误；
  忽略关键 functional-group difference。

Reasoning errors:
  把 descriptor 解释成跨任务固定单调规律；
  没有处理冲突证据；
  前文证据和最终答案矛盾；
  先给答案再找理由。

Teacher/data errors:
  pairwise teacher 本身错误；
  neighbor retrieval 不够相关；
  task label 噪声或定义模糊。
```

**指标。**

- 各错误类型占比；
- SFT 相对 prompted baseline 减少了哪些错误；
- SFT 仍然最多的错误是什么；
- 错误类型和任务/相似度/KNN margin 的关系。

**能说明什么。** Error taxonomy 可以把 paper 从“平均分不够惊艳”转成“我们明确改善了哪些 reasoning failure，并知道剩余瓶颈在哪里”。

### 13.12 Similarity margin analysis

**目的。** 分析 TRIM 在什么难度区间最有效。

**做法。** 按相似度和邻居标签分布分桶：

```text
Top-neighbor similarity:
  high / medium / low

Positive-negative similarity gap:
  top positive similarity - top negative similarity 的绝对值

KNN vote margin:
  top-k 中多数类比例，例如 5:0, 4:1, 3:2

Retrieval quality:
  是否存在至少一个高相似度正类邻居和一个高相似度负类邻居
```

**指标。**

- 每个桶的 F1；
- 每个桶中 SFT 相对 KNN 的提升；
- 每个桶的 trace quality；
- 每个桶的 error type 分布。

**能说明什么。** 如果 TRIM 主要在 low-margin 或 positive-negative-conflict 区间提升，说明它的贡献正是细粒度类比，而不是简单近邻检索。

### 13.13 Feature family analysis

**目的。** 理解模型和 teacher 实际依赖哪些分子证据，并检查是否符合化学直觉。

**做法。** 将 feature 按家族分组：

```text
size/shape:
  molecular weight, heavy atoms, ring count, rotatable bonds

polarity/H-bonding:
  TPSA, HBA, HBD

lipophilicity:
  logP, logD

ionization/pKa:
  acidic/basic sites, strongest acidic pKa, strongest basic pKa, neutral fraction

functional groups:
  top-level functional-group indicators

task-specific fragments:
  如果有额外 fragment 或 top-level groups，也单独统计
```

统计 pairwise teacher top terms 和模型 trace 中被引用 feature 的分布。

**指标。**

- teacher top evidence 的 feature-family 分布；
- SFT trace citation 的 feature-family 分布；
- prompted baseline trace citation 的 feature-family 分布；
- 每个任务中最常被使用的 feature family；
- feature family citation 与正确率的关系。

**能说明什么。** 这可以展示 TRIM 让模型关注了哪些具体证据，也能发现模型是否过度依赖某些通用化学话术，例如总是讲 logP/TPSA，却忽略 teacher 真正强调的 pKa 或 functional group。

### 13.14 Calibration and confidence analysis

**目的。** 如果模型能输出概率或置信度，应检查它是否知道何时证据冲突、何时应该不确定。

**做法。**

让模型在最终答案中输出一个 calibrated confidence，或从 logprob/采样一致性估计置信度。然后比较：

```text
正确样本 vs 错误样本；
KNN-easy vs KNN-hard；
conflict-heavy vs non-conflict；
clean evidence vs corrupted evidence。
```

**指标。**

- expected calibration error；
- Brier score；
- confidence-accuracy curve；
- corrupted evidence 后 confidence 是否下降；
- conflict slice 中 confidence 是否低于 easy slice。

**能说明什么。** 好的 reasoning agent 不只应该答对，还应该在证据冲突或 retrieval 弱时降低置信度。这个分析可以作为附录补充。

### 13.15 Qualitative paired case studies

**目的。** 用少量高质量案例直观展示 SFT 前后的推理差异。

**做法。** 选择 3 到 5 个代表性样本，每个样本并排展示：

```text
任务和 query SMILES；
工具返回的正负邻居和关键 feature differences；
prompted LLM trace；
SFT model trace；
ground truth；
为什么 SFT trace 更 grounded。
```

推荐选择以下类型：

```text
Case 1:
  KNN wrong but SFT correct。

Case 2:
  Prompted model 忽略负类邻居，SFT 同时比较正负邻居。

Case 3:
  正负邻居都很相似，SFT 正确处理冲突证据。

Case 4:
  Prompted model 产生 unsupported monotone claim，SFT 使用具体 baseline/delta。

Case 5:
  SFT 仍然失败，用于诚实展示局限。
```

**能说明什么。** 定性案例不能替代统计结果，但能帮助 reviewer 理解“更好的 reasoning”具体是什么样的，而不是只看分数。

### 13.16 ChEMBL assay profile 作为可选 stress test

**目的。** 如果需要回应“RDKit feature schema 是否 cooked”的担心，可以把 ChEMBL assay/activity 作为一个小型 evidence-modality transfer test，而不是主线实验。

**建议不要做的方式。**

不要把某个分子的全部 ChEMBL activities 直接塞进模型。原因是：

```text
activities 数量极大；
assay 条件异质；
很多 value 缺失或是文本判断；
可能和 TDC label 有直接或间接 leakage；
上下文成本过高；
会把论文主线从 reasoning data synthesis 带偏到 database feature engineering。
```

**更合适的做法。**

只构造 compact assay profile，例如：

```text
每个 assay_type 的记录数；
Binding / Functional / ADME / Toxicity 的 active/inactive 文本统计；
有 pChEMBL 的 target class summary；
按 target 或 endpoint 聚合的 min/median/max pChEMBL；
是否有 COX、hERG、CYP、P-gp 等任务相关 assay 记录；
缺失值比例和文本 comment summary。
```

然后让工具返回 query 和 neighbors 的 compact profile difference，而不是原始 activities。

**指标。**

- 模型是否能在新 evidence modality 下保持 neighbor coverage；
- 是否正确引用 assay profile difference；
- 是否因为 assay evidence 改变 final answer；
- 与 RDKit-only analogical reasoning 的 trace quality 对比。

**能说明什么。** 这个实验最多说明 TRIM 学到的比较流程可能迁移到 assay-profile evidence。它不应替代主实验，也不应作为主要性能提升来源。

### 13.17 推荐的最小实验组合

如果时间有限，优先完成下面五项：

```text
1. Main performance table:
   prompted LLM + tool vs SFT + tool vs KNN vs pairwise teacher。

2. Anti-KNN analysis:
   KNN-hard slice + label-only / feature-only / full evidence ablation。

3. Trace quality table:
   tool success、neighbor coverage、feature grounding、delta direction correctness、contradiction rate。

4. Evidence corruption:
   shuffle labels、flip deltas、remove top teacher features，观察性能和 trace 是否退化。

5. Held-out task generalization:
   训练任务和测试任务分开，检查 analogical reasoning procedure 是否迁移。
```

这五项能共同支撑一个更强的论文叙事：

```text
即使平均 F1 提升不是压倒性的，TRIM 训练出的模型也更会调用工具、
更完整覆盖正负邻居、更忠实引用特征差异、在 KNN 失败的样本上更稳，
并且这种类比推理行为能一定程度迁移到未见任务。
```
