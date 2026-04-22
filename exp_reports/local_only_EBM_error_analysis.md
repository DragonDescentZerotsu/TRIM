我按当前 local-only SFT 的 `train` 口径统计了：来源是 `outputs/reasoning_rewrite_filters/summary.json` 和 `outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts/<task>/train/sample_*.json`。

关键点：`dropped_records.json` 只包含 `both_wrong`，但 local-only SFT 的过滤标准是 `local_prediction_correct == true`，所以 **local EBM 没做对的样本 = `global_only_correct + both_wrong`**。

**总体结果**

16 个 task 的 train 总样本数是 **14,880**，local EBM 做错 **1,066**，占 **7.16%**。

其中：
- False positive：**534**，真实 0、local 预测 1
- False negative：**532**，真实 1、local 预测 0
- 距离 0.5 阈值很近的错样本：
  - `|local_score - 0.5| < 0.05`：**229**
  - `|local_score - 0.5| < 0.10`：**441**，占错样本 **41.4%**
- 高置信错样本：
  - `|local_score - 0.5| >= 0.25`：**235**，占错样本 **22.0%**

**每个 Task 的错误数**

| task | total | local wrong | wrong % | FP | FN | within 0.10 | conf >= 0.25 |
|---|---:|---:|---:|---:|---:|---:|---:|
| AMES | 5081 | 674 | 13.27% | 329 | 345 | 283 | 149 |
| BBB_Martins | 1369 | 52 | 3.80% | 40 | 12 | 19 | 14 |
| Bioavailability_Ma | 448 | 22 | 4.91% | 19 | 3 | 16 | 1 |
| CYP2C9_Substrate_CarbonMangels | 465 | 33 | 7.10% | 0 | 33 | 19 | 1 |
| CYP2D6_Substrate_CarbonMangels | 464 | 24 | 5.17% | 5 | 19 | 10 | 4 |
| CYP3A4_Substrate_CarbonMangels | 466 | 44 | 9.44% | 25 | 19 | 30 | 4 |
| Carcinogens_Lagunin | 194 | 2 | 1.03% | 1 | 1 | 1 | 0 |
| ClinTox | 1007 | 11 | 1.09% | 0 | 11 | 4 | 2 |
| DILI | 332 | 6 | 1.81% | 2 | 4 | 3 | 0 |
| HIA_Hou | 404 | 0 | 0.00% | 0 | 0 | 0 | 0 |
| PAMPA_NCATS | 1423 | 78 | 5.48% | 74 | 4 | 26 | 22 |
| Pgp_Broccatelli | 846 | 9 | 1.06% | 2 | 7 | 4 | 1 |
| SARSCoV2_3CLPro_Diamond | 615 | 25 | 4.07% | 2 | 23 | 2 | 12 |
| SARSCoV2_Vitro_Touret | 1032 | 46 | 4.46% | 1 | 45 | 8 | 17 |
| Skin_Reaction | 282 | 30 | 10.64% | 26 | 4 | 13 | 8 |
| hERG | 452 | 10 | 2.21% | 8 | 2 | 3 | 0 |

**错误原因诊断**

这里的“原因”是从 local EBM evidence 里做的诊断，不是化学因果结论。local score 是 3 个正类邻居 + 3 个负类邻居 pairwise EBM 分数的 similarity-weighted average；错样本主要分成几类：

1. **两组 neighbor 都把方向推错**  
   这是最大类：**683 / 1066 = 64.1%**。  
   其中：
   - `both_neighbor_groups_high_wrong_FP`：358 条，正/负 neighbor 两组平均分都偏高，导致真实 0 被判成 1
   - `both_neighbor_groups_low_wrong_FN`：325 条，正/负 neighbor 两组平均分都偏低，导致真实 1 被判成 0

2. **阈值附近的模糊错误很多**  
   **441 / 1066 = 41.4%** 的错样本离 0.5 不到 0.10。这类更像边界样本，不一定是强错误信号。

3. **任务有明显 FP/FN 偏向**
   - FP 偏多：`PAMPA_NCATS`、`Skin_Reaction`、`BBB_Martins`、`Bioavailability_Ma`、`hERG`
   - FN 偏多：`CYP2C9_Substrate_CarbonMangels`、`ClinTox`、`SARSCoV2_3CLPro_Diamond`、`SARSCoV2_Vitro_Touret`
   - `AMES` 几乎 FP/FN 对半，但它贡献了最多错样本：**674 / 1066 = 63.2%**

4. **错样本里最常见的误导性 top terms**
   统计的是错样本中 top pairwise EBM terms 里“支持最终错误预测方向”的特征。整体最常见的是：
   - `QED drug-likeness`
   - `ring count`
   - `fraction of sp3 carbons`
   - `strongest basic pKa`
   - `estimated logD`
   - `neutral fraction`
   - `topological polar surface area`
   - `nitro`
   - `alkyl chloride`

按 task 看，主要误导项大致是：
- `AMES`：QED、ring count、fraction sp3、basic pKa、neutral fraction
- `BBB_Martins`：TPSA、QED、neutral fraction、alkene
- `Bioavailability_Ma`：QED、neutral fraction、acidic pKa、enol
- `CYP2C9`：basic pKa、piperidine
- `CYP2D6`：basic pKa、TPSA、partial charge
- `CYP3A4`：logD、heavy-atom MW、neutral fraction、tertiary aliphatic amine
- `PAMPA_NCATS`：logD、neutral fraction、partial charge、TPSA
- `Pgp_Broccatelli`：logP、logD、heavy-atom MW
- `SARSCoV2_3CLPro_Diamond`：alkyl chloride、fraction sp3、QED
- `SARSCoV2_Vitro_Touret`：maximum partial charge、logP、rotatable bonds、logD
- `Skin_Reaction`：QED、minimum absolute partial charge、alkene
- `hERG`：TPSA、acidic pKa、nitrile、logP、carboxylic acid

结论上，local-only SFT 过滤会丢掉 **7.16%** 的 train samples；这些错样本不是单一原因，主要是 **neighbor pairwise scores 在相似度加权后整体推错**，其次是 **大量边界样本**，再加上一些 task-specific 的 FP/FN 偏置。