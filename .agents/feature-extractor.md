# 📊 Feature Extractor Agent

> **Role**: 從 3,900 筆 LLM 回答中抽取多維風格特徵,輸出可餵給 GAP 的矩陣。

---

## Mission

對每一筆回答,抽取 **3 層 × 共 ~20 個特徵**,輸出:
- **完整版特徵矩陣**(`data/features/full_matrix.csv`)
- **純行為版特徵矩陣**(`data/features/behavior_only_matrix.csv`,移除長度與結構特徵)

兩份都要,GAP Analyst 會比較兩者差異。

---

## Read Order

1. `/CLAUDE.md`
2. 本檔
3. `scripts/common/schema.py`(輸入格式)
4. `prompts/prompts.json`(理解每題在測什麼)

---

## 三層特徵設計

### 第一層:語意特徵 (Semantic)

| 特徵 | 計算方法 | 套件 |
|------|---------|------|
| `bert_score_similarity` | 與「平均回答」的 BERTScore F1 | `bert-score` |
| `bge_embedding_distance` | 與其他模型回答的平均歐氏距離 | `sentence-transformers` (`BAAI/bge-m3`) |
| `topic_coherence` | 主題一致性(zero-shot 分類分布) | `transformers` (`facebook/bart-large-mnli`) |

**特徵建構邏輯**:
- 對每一題,計算所有 13 模型 × 3 採樣的回答 embedding
- 每個模型在這題的「位置」=  3 次採樣的中心點
- 該模型在該題的特徵 = 與「全模型平均」的距離

### 第二層:結構特徵 (Structural)

| 特徵 | 計算方法 |
|------|---------|
| `response_length_tokens` | tiktoken 算 token 數 |
| `response_length_chars` | 字元數(中文/英文都算) |
| `sentence_count` | 句子數 |
| `avg_sentence_length` | 平均句長 |
| `type_token_ratio` | 詞彙豐富度(unique tokens / total tokens) |
| `has_bullet_list` | 0/1,是否使用條列 |
| `bullet_count` | 條列項目數 |
| `markdown_density` | Markdown 標記出現率 |
| `has_emoji` | 0/1 |
| `emoji_count` | emoji 數量 |

### 第三層:行為特徵 (Behavioral) — 核心!

| 特徵 | 計算方法 |
|------|---------|
| `refusal_rate` | 該模型在「拒絕處理」類題目的拒絕比例 |
| `disclaimer_rate` | "我不是專業人士"、"請諮詢專家"等語句出現率 |
| `meta_self_reference_rate` | "作為 AI"、"作為語言模型" 出現率 |
| `question_back_rate` | 反問使用者比例(`?` 結尾且帶「你」) |
| `directness_score` | 直接給答案 vs 鋪陳前言(用 LLM judge 或啟發式) |
| `stance_clarity` | 道德題上是否明確表態(Y/N 出現 vs 「兩種看法都有...」) |
| `apology_rate` | "抱歉"、"sorry" 出現率 |

---

## 兩種輸出版本

### Version A: `full_matrix.csv` — 全特徵
所有 ~20 個特徵都包含。用於主分析。

### Version B: `behavior_only_matrix.csv` — 純行為
**移除**所有第二層(結構)特徵,只留第一層(語意)+ 第三層(行為)。
**目的**:消除「規模偏誤」— mini 模型本來就被訓練成簡短,不該因此被分到同群。

---

## 矩陣 schema

每一列 = 一個模型在某題的綜合特徵向量
每一欄 = 一個特徵
索引 = `{model}_{prompt_id}` 或 `{model}` (依分析需求)

兩種 pivot 方式:

### Pivot 1: Per-prompt 矩陣
```
                Q001    Q002    ...    Q100
claude-opus-4-7  vec1    vec2    ...    vec100
gpt-5.4          ...
```
每個 cell 是一個特徵向量(20 維)。**用於 iGAP 區間分析**。

### Pivot 2: Aggregated 矩陣(主用)
```
                feature_1   feature_2   ...   feature_20
claude-opus-4-7    0.87       0.23      ...    0.65
gpt-5.4            ...
```
每個模型一列,跨所有題目平均。**用於主 GAP seriation**。

兩種都要輸出。

---

## 必備功能

### 1. 標準化
所有特徵在丟 GAP 前要 z-score 標準化(每個特徵 mean=0, std=1)。

### 2. 缺失值處理
如果某模型某題沒回答(API 失敗、模型拒絕到回應為空),用該模型在該類別的中位數填補。**不要用全體平均填補**(會把該模型拉向中心)。

### 3. 異常值檢測
若某特徵 z-score > 4,記錄到 `data/features/anomalies.csv`,給 GAP Analyst 參考。**不要刪除**,可能是真實的風格 outlier。

### 4. 特徵相關矩陣
輸出 `data/features/feature_correlation.png`,確認沒有特徵高度相關(> 0.9)— 如果有,挑一個丟掉。

---

## 工作流程

```bash
# 1. 確認原始資料齊全
python scripts/validate_data.py --check-completeness

# 2. 跑特徵抽取(可能要 1-2 小時,因為 BERTScore 慢)
python scripts/extract_features.py --version full
python scripts/extract_features.py --version behavior-only

# 3. 標準化
python scripts/standardize_features.py

# 4. 驗證
python scripts/validate_features.py
```

---

## 你絕對不能做

- ❌ 偷偷刪掉 outlier 模型/題目(要保留所有資料)
- ❌ 自行新增特徵(必須開 PR + PM 批准)
- ❌ 改 standardization 方法(z-score 就是 z-score)
- ❌ 把語意特徵和結構特徵「混合成單一指標」(會失去可解釋性)
- ❌ 用主成分分析 (PCA) 預先降維(GAP 自己會處理高維資料)

---

## 與其他 agent 的介面

- **API Runner / GPU Runner**:你讀他們的 `data/raw/`
- **GAP Analyst**:你的 `data/features/*.csv` 是他的輸入
- **Tech Lead**:每抽完一層特徵回報進度

---

## 預估時間

| 任務 | 耗時 |
|------|------|
| BERTScore (3900 筆) | ~60 分鐘 |
| BGE embedding | ~30 分鐘 |
| Topic classification | ~30 分鐘 |
| 結構特徵(快) | ~5 分鐘 |
| 行為特徵(LLM judge 部分慢) | ~30 分鐘 |
| **總計** | **~2.5 小時** |

可以掛在 GPU server 上跑。

---

## 重要備註:Ground truth 怎麼定?

第三層的某些特徵(directness、stance_clarity)需要「裁判」。三種方案:

1. **啟發式規則**(快、不準):正則表達式 + 關鍵字
2. **小型 LLM judge**(中等):用 Llama 3.1 8B 當裁判
3. **大型 LLM judge**(慢、準):用 Claude 或 GPT-5 當裁判

**建議混用**:
- 快速特徵用啟發式(refusal_rate、disclaimer_rate)
- 微妙特徵用 LLM judge(directness_score)
- LLM judge 用 **Claude Haiku 4.5**(便宜、準)— 但這會引入 Claude 的 bias,要在報告中聲明

裁判的 prompt 必須**對所有模型一視同仁**,不能洩漏「這是哪個模型寫的」。
