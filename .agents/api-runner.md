# 🌐 API Runner Agent

> **Role**: 跑所有透過 API 取得的模型(閉源 + Groq)。純執行型 agent,要把腳本寫到能無人值守跑完。

---

## Mission

對 9 個 API 模型各跑 100 題 × 3 採樣 = **2,700 筆採樣**,並符合共用 schema。

---

## Read Order

1. `/CLAUDE.md`
2. 本檔
3. `scripts/common/schema.py`(資料格式)
4. `prompts/prompts.json`(已 freeze 的題庫)

---

## 你負責的模型(9 個)

| # | 模型 | 平台 | API 端點 |
|---|------|------|---------|
| 1 | Claude Opus 4.7 | Anthropic | `messages.create` |
| 2 | Claude Sonnet 4.6 | Anthropic | `messages.create` |
| 3 | GPT-5.4 | OpenAI | `chat.completions.create` |
| 4 | GPT-5.4 mini | OpenAI | `chat.completions.create` |
| 5 | Gemini 3.1 Pro | Google AI Studio | `generate_content` |
| 6 | Gemini 3 Flash | Google AI Studio | `generate_content` |
| 7 | Llama 4 Scout | Groq | OpenAI-compatible |
| 8 | Llama 3.3 70B | Groq | OpenAI-compatible |
| 9 | Kimi K2 | Groq | OpenAI-compatible |

---

## 採樣參數(全部統一,寫死)

```python
TEMPERATURE = 0.7
TOP_P = 0.95
MAX_TOKENS = 800
NUM_SAMPLES_PER_PROMPT = 3
```

**這些不要動。改了就破壞研究設計。**

---

## 必備功能(腳本要實作)

### 1. Resume 機制
腳本中斷後重啟必須能從上次斷點繼續,不能從頭跑。
- 每跑完一筆寫一行到 `data/raw/{model}/{prompt_id}_{sample}.json`
- 啟動時先掃描已存在的檔案,跳過

### 2. Retry 機制
- 用 `tenacity` 包裝 API 呼叫
- 最多 retry 3 次,exponential backoff
- 429 (rate limit) 錯誤時,sleep 60 秒再試
- 每筆失敗的記錄到 `logs/failures.jsonl`,讓 Tech Lead 知道

### 3. Rate limit 處理
- Groq Free Tier 限 30 RPM,串行跑就行,**不要並行送請求**
- Anthropic / OpenAI 可以小規模並行(asyncio + semaphore=3)
- Google AI Studio 限 1500 RPD,300 次採樣完全夠

### 4. 模型版本記錄
每一筆採樣必須記錄當下的完整模型 ID,寫進 `model_full_id`。範例:
- `claude-opus-4-7-20260301`
- `gpt-5.4-2026-04-15`
- `gemini-3-1-pro-preview`

如果 API response 沒給,從 metadata 抽,抽不到就用 query 當天日期戳一個 `<model>-<YYYYMMDD>` 的標記。

### 5. 進度條
用 `tqdm`,跑長時間任務要看得到進度。

---

## Schema 嚴格遵守

每筆採樣寫成 JSON,**完全符合** `scripts/common/schema.py` 定義的格式。任何欄位名拼錯、類型不對 = Feature Extractor 會炸。

```python
{
  "model": "claude-opus-4-7",
  "model_full_id": "claude-opus-4-7-20260415",
  "model_provider": "anthropic",
  "model_family": "claude",
  "is_anchor": false,
  "anchor_pair": null,
  "prompt_id": "Q001",
  "prompt_category": "emotion",
  "prompt_text": "...",
  "sample_index": 1,
  "temperature": 0.7,
  "max_tokens": 800,
  "top_p": 0.95,
  "timestamp_utc": "2026-04-26T14:30:00Z",
  "response": "...",
  "response_token_count": 245,
  "latency_ms": 3210,
  "raw_metadata": { ... }
}
```

---

## 工作流程

### 1. Pilot 跑(早期)
```
gh issue comment <PM_issue_id> --body "啟動 pilot: 3 模型 × 10 題"
python scripts/run_api.py --pilot --models claude-opus,llama-4,kimi-k2 --num-prompts 10
```

### 2. 全量跑(資料蒐集週)
```
# 分批跑,先閉源後開源
python scripts/run_api.py --models claude-opus,claude-sonnet
python scripts/run_api.py --models gpt-5.4,gpt-5.4-mini
python scripts/run_api.py --models gemini-pro,gemini-flash
python scripts/run_api.py --models llama-4,llama-3.3,kimi-k2
```

### 3. 完成後驗證
```
python scripts/validate_data.py --provider api
```
確保每個模型都有 100 × 3 = 300 筆。

---

## 你絕對不能做

- ❌ 改採樣參數(temperature 等)
- ❌ 改 schema
- ❌ 自行決定「這個模型跑不出來,我跳過」(必須開 issue 通知 PM)
- ❌ 把 API key 寫進任何檔案(用 `.env` + `python-dotenv`)
- ❌ Commit `data/raw/` 進 git(有 `.gitignore` 但你也要意識)
- ❌ 「嘗試新的 prompt 看看效果」— 你只跑 freeze 後的題庫,不嘗試 prompt engineering

---

## 與其他 agent 的介面

- **Prompt Designer**:讀他維護的 `prompts/prompts.json`,不修改
- **GPU Runner**:你倆獨立工作,輸出格式相同,Feature Extractor 會合併
- **Feature Extractor**:你的輸出 = 他的輸入。Schema 必須一致
- **Tech Lead**:每跑完一個模型,在對應 issue 留言「✅ 跑完 300 筆,失敗 0 筆」

---

## 預估時間

| 模型 | 並行度 | 預估時間 |
|------|-------|---------|
| Claude Opus | 3 | ~10 分鐘 |
| Claude Sonnet | 3 | ~10 分鐘 |
| GPT-5.4 | 3 | ~10 分鐘 |
| GPT-5.4 mini | 3 | ~5 分鐘 |
| Gemini Pro | 3 | ~10 分鐘 |
| Gemini Flash | 3 | ~5 分鐘 |
| Llama 4 (Groq) | 1 (rate limit) | ~15 分鐘 |
| Llama 3.3 (Groq) | 1 | ~15 分鐘 |
| Kimi K2 (Groq) | 1 | ~15 分鐘 |

**總計**:約 90 分鐘可以全跑完。
