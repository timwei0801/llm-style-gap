# CLAUDE.md — Agent 操作手冊

> 這是這個 repo 的 Claude Code 操作手冊。Claude Code 在每次 session 開始時會自動讀取本檔。
> **所有 agent 都必須先讀完本檔再開始任何任務。**

---

## 📌 專案核心(必讀)

**專案名稱**:LLM 回答風格之 GAP 圖譜分析
**性質**:**一次性學期專題**,4 週後交報告即結束
**負責人(PM)**:Timwei (魏祺紘)
**目標**:用 GAP (Generalized Association Plots) seriation 分析 13 個 LLM 的回答風格,找出風格群落

### 這是研究專案,不是 production 系統

**重複念三次**:不要過度工程化。

具體禁止行為:
- ❌ 不要設計 abstract base class、不要做 plugin architecture
- ❌ 不要寫「為了未來擴展」的功能
- ❌ 不要為了 type safety 加無謂的 Pydantic / dataclass 層
- ❌ 不要設置 CI/CD、code coverage、自動部署
- ❌ 不要寫單元測試,除非該函式邏輯複雜到值得
- ❌ 不要重構 PM 沒要求重構的東西

具體鼓勵行為:
- ✅ 直接、簡單、可讀的腳本
- ✅ 能 work 就 commit,後面有問題再修
- ✅ 寫死的常數比通用配置好
- ✅ 一個檔案做一件事

---

## 👥 Agent 角色與分工

本 repo 採 **PM + Tech Lead + 5 專業 Agent** 架構。

| Agent | 職責 | system prompt 位置 |
|-------|------|-------------------|
| 🎯 Tech Lead | 拆任務、分派、整合產出、回報 PM | `.agents/tech-lead.md` |
| 📝 Prompt Designer | 100 題 prompt 設計與迭代 | `.agents/prompt-designer.md` |
| 🌐 API Runner | 跑閉源 API + Groq | `.agents/api-runner.md` |
| 🖥 GPU Runner | 跑學校 GPU 上的本地模型 | `.agents/gpu-runner.md` |
| 📊 Feature Extractor | 從回答抽取 3 層特徵 | `.agents/feature-extractor.md` |
| 🎨 GAP Analyst | GAP seriation + 視覺化 + 故事 | `.agents/gap-analyst.md` |

**每個 agent 開始任務前,必須讀自己的 system prompt + 本 CLAUDE.md。**

---

## 🔒 PM 介入規則(很重要)

PM (Timwei) 的時間有限,**不要每件小事都 ping 他**。判斷標準:

### ✅ Agent 可自行決定(直接做)
- 程式碼風格、變數命名、檔案結構
- 修 bug、加 logging、加錯誤處理
- 補充註解、改進 README
- 重跑失敗的 API 呼叫
- 處理明顯的 typo 或格式問題

### ⚠️ 開 PR 等 PM review(不要直接 merge 到 main)
- 任何 prompt 內容改動
- 特徵定義新增、刪除、修改
- 模型陣容調整
- 採樣參數變更 (temperature、max_tokens 等)
- GAP 分析設定
- 報告/視覺化內容

### 🚨 必須先問 PM 才能動(在 issue 留言詢問)
- 砍掉任何已採集的資料
- 改 schema(會影響所有 agent)
- 採用新工具/新框架
- 變更研究方法論
- 任何「我覺得這樣可能更好」的提案,不要直接做

---

## 📂 Repo 結構規範

```
llm-style-gap/
├── CLAUDE.md                    # 本檔(必讀)
├── README.md                    # 對外說明
├── .gitignore                   # 已含 secrets 防護
├── .env.example                 # API key 模板(.env 不進 git)
│
├── .agents/                     # 各 agent 的 system prompt
│   ├── tech-lead.md
│   ├── prompt-designer.md
│   ├── api-runner.md
│   ├── gpu-runner.md
│   ├── feature-extractor.md
│   └── gap-analyst.md
│
├── .github/
│   ├── ISSUE_TEMPLATE/          # Issue 模板
│   └── pull_request_template.md
│
├── prompts/                     # Prompt Designer 維護
│   ├── prompts.json             # 主題庫(100 題)
│   ├── pilot/                   # Pilot test 結果
│   └── README.md
│
├── scripts/                     # 各 agent 的執行腳本
│   ├── run_api.py               # API Runner
│   ├── run_local.py             # GPU Runner (Ollama)
│   ├── extract_features.py      # Feature Extractor
│   ├── gap_analysis.py          # GAP Analyst
│   └── common/
│       ├── schema.py            # 資料 schema(所有 agent 共用)
│       └── utils.py
│
├── data/                        # 資料(部分 commit、部分 .gitignore)
│   ├── samples/                 # 每模型 5 筆樣本(會 commit)
│   ├── raw/                     # 完整原始回答(.gitignore,放 server)
│   ├── features/                # 特徵矩陣(會 commit,壓縮版)
│   └── README.md
│
├── analysis/                    # GAP 分析輸出
│   ├── results/                 # GAP 距離矩陣、序列順序
│   ├── figures/                 # 視覺化圖(SVG/PNG)
│   └── notebooks/               # Jupyter notebook 探索
│
├── docs/                        # 報告與文件
│   ├── proposal.docx            # 提案書
│   ├── final_report.docx        # 最終報告
│   └── slides.pptx              # 投影片
│
└── logs/                        # 執行 log(.gitignore)
```

**重要規則**:
- 不要在 root 寫腳本,放 `scripts/`
- 不要在 root 放資料,放 `data/`
- 不要動 `docs/proposal.docx`(那是給教授看的版本)

---

## 🔐 安全規範(Public Repo!)

本 repo 為 **Public**,以下絕對不可進 git:

### 🚫 永遠不可 commit
- API key(任何形式:`sk-xxx`、`AIza-xxx`、Groq key 等)
- `.env` 檔
- 個人帳號資訊、token
- 學校 server IP、SSH key、密碼
- 朋友/同學的個資

### ✅ 安全做法
- API key 放 `.env`(已在 `.gitignore`)
- 用 `python-dotenv` 讀取
- 任何要 commit 的檔案,先用 `grep -ri "sk-\|AIza\|gsk_" .` 自查
- 如果不小心 commit 了 secret,**立刻**:
  1. 在 issue 標 `🚨 secret-leaked`
  2. ping PM
  3. 不要嘗試 force push 蓋掉(GitHub 仍會留快取)
  4. 立刻去對應平台 revoke 該 key

---

## 📐 共用 Schema(所有 agent 必須遵守)

任何採樣結果必須符合以下 schema(`scripts/common/schema.py`):

```python
{
  "model": "claude-opus-4-7",          # 模型 ID(短名)
  "model_full_id": "claude-opus-4-7",   # 完整版本標識
  "model_provider": "anthropic",        # anthropic / openai / google / groq / ollama
  "model_family": "claude",             # claude / gpt / gemini / llama / kimi / deepseek / qwen / glm / gemma
  "is_anchor": false,                   # 是否為錨點模型
  "anchor_pair": null,                  # 若為錨點,標 A/B/C
  
  "prompt_id": "Q001",                  # Q001 ~ Q100
  "prompt_category": "emotion",         # emotion / moral / uncertainty / creative / refusal
  "prompt_text": "我剛失戀,12 字內安慰我",
  
  "sample_index": 1,                    # 1, 2, 3 (3 次採樣)
  "temperature": 0.7,                   # 採樣參數(統一)
  "max_tokens": 800,
  "top_p": 0.95,
  
  "timestamp_utc": "2026-04-26T14:30:00Z",
  "response": "...",                    # 模型回答(原文)
  "response_token_count": 245,          # 回答 token 數
  "latency_ms": 3210,                   # 回答耗時
  
  "raw_metadata": {                     # 各家 API 的原始 metadata,供溯源
    ...
  }
}
```

**禁止任何 agent 擅自改 schema**。如要新增欄位,必須開 issue 跟 PM 討論。

---

## 🔁 Workflow 規範

### Branch 命名
- `agent/prompt-designer-v3` — 某個 agent 的工作分支
- `feature/add-bertscore` — 新功能
- `fix/api-timeout` — 修 bug
- `data/sample-batch-1` — 資料批次

### Commit 訊息
用 conventional commits,簡短具體:
```
feat: add 5 new emotion prompts
fix: handle Gemini rate limit
data: add Claude Opus samples (Q001-Q100)
docs: update README with model list
chore: bump dependencies
```

### Pull Request
- 標題:一句話講清楚做了什麼
- 內文:用 `.github/pull_request_template.md`(已準備)
- 標 label:`prompt`、`api-runner`、`gpu-runner`、`feature`、`gap`、`docs`
- @PM(Timwei)review

### Issue
- **任務 issue**:由 PM 或 Tech Lead 開,assign 給對應 agent
- **問題 issue**:agent 卡住時開,標 `🆘 needs-PM`
- **發現 issue**:agent 跑出有趣現象時開,標 `💡 finding`

---

## ⚠️ 已知陷阱(歷史教訓)

這些是這個專案類型容易踩的雷,Tech Lead 必須記住:

1. **Prompt 設計階段不要急著跑全部模型**
   先 pilot 10 題在 3 個模型,看鑑別度有沒有出來,再擴大。

2. **API rate limit 是 per organization 不是 per key**
   Groq 限 30 RPM,並行 5 個請求就接近上限。要加 backoff。

3. **Ollama 在 Blackwell 架構有相容性問題**
   - DeepSeek 在 vLLM + Blackwell 不穩,改用 Ollama
   - Gemma 4 需要 build b8665+,不然會進入重複迴圈
   - GLM/Qwen 3.5 需要 `--reasoning-format none` 處理 `<think>` 標籤

4. **學校 server SSH 連線會掉**
   所有長時間任務必須包 `tmux` 或 `screen`。

5. **「mini」模型有規模偏誤**
   GPT-mini、Gemini-Flash 因訓練目標被導向簡短回答,直接比較會混淆「家族風格」與「規模效應」。Feature Extractor 必須輸出兩組分析(含長度 vs 不含長度)。

6. **模型版本會偷偷更新**
   每次採樣前記錄當天的 `model_full_id`,寫進每筆資料。

---

## 🎯 階段性目標

| 階段 | 週次 | 主導 agent | 完成標準 |
|------|------|----------|---------|
| 環境建置 | W1 | Tech Lead | 5 個模型能 hello world |
| Prompt 設計 | W2 | Prompt Designer | 100 題鎖定 + pilot 通過鑑別度檢驗 |
| 採樣 | W3 上 | API Runner + GPU Runner | 13 模型 × 100 題 × 3 = 3900 筆完整 |
| 特徵抽取 | W3 下 | Feature Extractor | 完整特徵矩陣 + schema 驗證通過 |
| GAP 分析 | W4 上 | GAP Analyst | 三大主視覺 + 4 則故事草稿 |
| 寫報告 | W4 下 | PM 主導 | 報告 + 投影片完成 |

---

## 📞 聯絡方式

PM (Timwei) 主要透過以下管道:
- GitHub Issue / PR comment(主要)
- @mention 在 PR 裡
- 緊急時:Issue 標 `🚨 urgent`

**Agent 之間不直接 chat**,所有溝通透過 issue/PR comment,確保有 paper trail。

---

## 🏁 結束條件

當 `docs/final_report.docx` 與 `docs/slides.pptx` 完成且 PM 確認後,本專案結束:
- 不再接受新 feature
- 不再 refactor
- 把 repo 設定 archived
- 把 README 改成 retrospective 版本

**結束 = 結束**,不要繼續折騰。
